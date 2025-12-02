from typing import Dict
import streamlit as st
from core.shared_state import SharedState, AgentGraphState
from agents.moderator.agent import ModeratorAgent

def moderator_node(state: AgentGraphState, ui_callback=None, chat_container=None, log_callback=None) -> Dict:
    agent = ModeratorAgent()
    
    if ui_callback:
        ui_callback(agent.role_name, "working")
        
    # 获取当前使用的模型名称
    model_name = agent.llm_config.model_name
    start_log = f"[{agent.role_name}] 开始总结... (Model: {model_name})"
    if log_callback:
        log_callback(start_log)
        
    temp_state = SharedState(**state)
    
    # 准备流式输出
    stream_callback = None
    placeholder = None
    accumulated_text = ""
    
    if chat_container:
        with chat_container:
            expander = st.expander(f"🗣️ {agent.role_name} ({model_name})", expanded=True)
            with expander:
                placeholder = st.empty()
                
                def _callback(chunk):
                    nonlocal accumulated_text
                    accumulated_text += chunk
                    placeholder.markdown(accumulated_text + "▌")
                
                stream_callback = _callback
    
    result = agent.run(temp_state, stream_callback=stream_callback)
    
    # 处理返回结果
    if isinstance(result, dict):
        patient_reply = result.get("content", "")
        medical_summary = result.get("summary", "")
    else:
        patient_reply = result
        medical_summary = result
    
    # 清除光标
    if placeholder:
        placeholder.markdown(accumulated_text)
    
    end_log = f"[{agent.role_name}] 完成总结。"
    if log_callback:
        log_callback(end_log)
        
    if ui_callback:
        ui_callback(agent.role_name, "idle")
    
    return {
        "moderator_summary": medical_summary,
        "chat_history": [
            {"role": agent.role_name, "content": patient_reply, "model": model_name}
        ],
        "agent_status": {agent.role_name: "idle"},
        "execution_logs": []
    }
