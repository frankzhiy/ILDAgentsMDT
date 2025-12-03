from typing import List, Dict
import traceback
from core.shared_state import SharedState
from core.pipeline import build_mdt_graph

# --- API Generator ---

def run_mdt_generator(shared_state: SharedState, enabled_agents: List[str], model_configs: Dict[str, str] = None, stop_event=None):
    """
    Generator function for API usage. Yields events.
    """
    import queue
    from threading import Thread
    
    event_queue = queue.Queue()
    
    def ui_callback(role, status):
        event_queue.put({"type": "status", "role": role, "content": status})
        
    def log_callback(message):
        event_queue.put({"type": "log", "content": message})
        
    def stream_callback_factory(role, model, target="chat"):
        def callback(chunk):
            if stop_event and stop_event.is_set():
                raise InterruptedError("Generation stopped by user")
            event_queue.put({"type": "token", "role": role, "content": chunk, "target": target})
        return callback

    # Initialize round state logic (similar to run_mdt_round)
    current_round = shared_state.round_count
    if current_round not in shared_state.specialist_opinions_history:
        shared_state.specialist_opinions_history[current_round] = {}
    
    # 增量更新逻辑：如果是后续轮次，先加载上一轮的意见作为基准
    # 这样未被唤醒的 Agent 的意见将保持不变
    if current_round > 1 and (current_round - 1) in shared_state.specialist_opinions_history:
        shared_state.specialist_opinions = shared_state.specialist_opinions_history[current_round - 1].copy()
        # 注意：specialist_summaries 目前没有 history 字段，但通常也需要保留
        # 假设 shared_state.specialist_summaries 已经保留了上一轮的值（因为它是在 SharedState 对象中持久化的）
        # 但为了安全起见，我们不清除它。
    else:
        shared_state.specialist_opinions = {}
        shared_state.specialist_summaries = {}
    
    shared_state.moderator_summary = ""
    
    for agent in enabled_agents:
        shared_state.update_agent_status(agent, "idle")
        event_queue.put({"type": "status", "role": agent, "content": "idle"})

    app = build_mdt_graph(
        enabled_agents,
        ui_callback=ui_callback,
        stream_callback_factory=stream_callback_factory,
        log_callback=log_callback,
        model_configs=model_configs,
        stop_event=stop_event
    )
    
    if not app:
        yield {"type": "error", "content": "No agents selected"}
        return

    initial_state = shared_state.model_dump()
    
    def runner():
        try:
            for event in app.stream(initial_state):
                # event is dict {node_name: output}
                for node_name, output in event.items():
                    if output is None:
                        print(f"WARNING: Node '{node_name}' returned None!")
                        continue
                        
                    # Update SharedState
                    if "structured_info" in output:
                        shared_state.structured_info = output["structured_info"]
                    if "specialist_opinions" in output:
                        shared_state.specialist_opinions.update(output["specialist_opinions"])
                        shared_state.specialist_opinions_history[current_round].update(output["specialist_opinions"])
                    if "specialist_summaries" in output:
                        shared_state.specialist_summaries.update(output["specialist_summaries"])
                    if "moderator_summary" in output:
                        shared_state.moderator_summary = output["moderator_summary"]
                        shared_state.moderator_summary_history[current_round] = output["moderator_summary"]
                    if "conflicts" in output:
                        shared_state.conflicts = output["conflicts"]
                    if "discussion_notes" in output:
                        shared_state.discussion_notes = output["discussion_notes"]
                        print(f"DEBUG: Pipeline received discussion_notes: {output['discussion_notes'][:50]}...")
                    if "chat_history" in output:
                        for msg in output["chat_history"]:
                            shared_state.chat_history.append(msg)
                    
                    # Emit result event
                    print(f"DEBUG: Emitting node_finished for {node_name}")
                    if node_name == "Conflict Detector":
                        print(f"DEBUG: Conflict Detector output: {output}")
                    
                    event_queue.put({"type": "node_finished", "role": node_name, "data": output})
                    
                    # Reset status
                    shared_state.update_agent_status(node_name, "idle")
                    event_queue.put({"type": "status", "role": node_name, "content": "idle"})
                    
        except InterruptedError:
            # Gracefully stop
            pass
        except Exception as e:
            print("Error in pipeline execution:")
            traceback.print_exc()
            event_queue.put({"type": "error", "content": str(e)})
        finally:
            event_queue.put(None) # Sentinel

    t = Thread(target=runner)
    t.start()
    
    while True:
        item = event_queue.get()
        if item is None:
            break
        yield item
        
    t.join()
