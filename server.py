from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import uuid
import json
import asyncio
import traceback

from core.shared_state import SharedState
from core.schemas import CaseInput, AgentStatusUpdate, StreamEvent
from core.pipeline_api import run_mdt_generator

app = FastAPI(title="ILD Agents MDT API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Management
# In-memory storage for now. For production, use Redis.
active_sessions: Dict[str, SharedState] = {}

@app.post("/api/sessions", response_model=Dict[str, str])
async def create_session():
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = SharedState()
    return {"session_id": session_id}

@app.get("/api/sessions/{session_id}", response_model=Dict)
async def get_session_state(session_id: str):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return active_sessions[session_id].model_dump()

@app.post("/api/sessions/{session_id}/case")
async def submit_case(session_id: str, input_data: CaseInput):
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = active_sessions[session_id]
    state.raw_case_text = input_data.case_text
    state.round_count += 1
    state.raw_case_history.append(f"【第 {state.round_count} 轮输入】\n{input_data.case_text}")
    state.chat_history.append({"role": "user", "content": input_data.case_text})
    
    return {"status": "updated", "round": state.round_count}

@app.websocket("/ws/consultation/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.close(code=4004, reason="Session not found")
        return
        
    state = active_sessions[session_id]
    
    # Wait for start signal or configuration
    import threading
    stop_event = threading.Event()
    
    try:
        data = await websocket.receive_text()
        config = json.loads(data)
        enabled_agents = config.get("selected_agents", ["Case Organizer", "Radiologist", "Pathologist", "Pulmonologist", "Rheumatologist", "Moderator"])
        model_configs = config.get("model_configs", {})
        
        # Run the generator
        generator = run_mdt_generator(state, enabled_agents, model_configs=model_configs, stop_event=stop_event)
        
        # Helper to safely get next item without raising StopIteration into asyncio
        def safe_next(gen):
            try:
                return next(gen)
            except StopIteration:
                return None

        while True:
            try:
                # Use asyncio.to_thread to call next(generator) to avoid blocking the loop
                event = await asyncio.to_thread(safe_next, generator)
                
                if event is None:
                    break
                
                await websocket.send_json(event)
                
            except Exception as e:
                print(f"Error during streaming: {e}")
                traceback.print_exc()
                break
                
        try:
            await websocket.send_json({"type": "done"})
        except:
            pass
        
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        print(f"Session error: {e}")
        traceback.print_exc()
    finally:
        stop_event.set()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18000)
