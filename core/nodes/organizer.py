from typing import Dict
import streamlit as st
from core.shared_state import SharedState, AgentGraphState
from agents.case_organizer.agent import CaseOrganizerAgent

def case_organizer_node(state: AgentGraphState, ui_callback=None, chat_container=None, log_callback=None) -> Dict:
    agent = CaseOrganizerAgent()
    
    # UI 更新：开始工作
    if ui_callback:
        ui_callback(agent.role_name, "working")
    
    # 获取当前使用的模型名称
    model_name = agent.llm_config.model_name
    start_log = f"[{agent.role_name}] 开始整理病例... (Model: {model_name})"
    if log_callback:
        log_callback(start_log)
        
    temp_state = SharedState(**state)
    
    # 准备流式输出
    stream_callback = None
    placeholder = None
    accumulated_text = ""
    
    if chat_container:
        # 在 chat_container 中创建一个新的 expander
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
    
    # 清除光标
    if placeholder:
        placeholder.markdown(accumulated_text)

    end_log = f"[{agent.role_name}] 完成: {result[:50]}..."
    if log_callback:
        log_callback(end_log)

    # UI 更新：完成工作
    if ui_callback:
        ui_callback(agent.role_name, "idle")
    
    return {
        "structured_info": temp_state.structured_info,
        "chat_history": [
            {"role": agent.role_name, "content": result, "model": model_name}
        ],
        "agent_status": {agent.role_name: "idle"},
        # execution_logs 已经在 log_callback 中处理了，这里返回空或者不返回
        # 但为了兼容性，还是返回，虽然可能会重复如果外部也处理
        # 我们修改 run_mdt_round 不再依赖这里的 execution_logs 来更新 UI
        "execution_logs": [] 
    }
