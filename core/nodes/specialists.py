from typing import Dict
import streamlit as st
from core.shared_state import SharedState, AgentGraphState

def specialist_node_factory(agent_cls, ui_callback=None, chat_container=None, log_callback=None):
    """工厂函数，用于生成各专科医生的节点函数"""
    def node_func(state: AgentGraphState) -> Dict:
        agent = agent_cls()
        
        if ui_callback:
            ui_callback(agent.role_name, "working")
            
        # 获取当前使用的模型名称
        model_name = agent.llm_config.model_name
        start_log = f"[{agent.role_name}] 开始分析... (Model: {model_name})"
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
            detailed_opinion = result.get("content", "")
            summary_opinion = result.get("summary", "")
        else:
            detailed_opinion = result
            summary_opinion = result
        
        # 清除光标
        if placeholder:
            placeholder.markdown(accumulated_text)
            
        end_log = f"[{agent.role_name}] 提交意见: {len(detailed_opinion)} chars"
        if log_callback:
            log_callback(end_log)
            
        if ui_callback:
            ui_callback(agent.role_name, "idle")
            
        return {
            "specialist_opinions": {agent.role_name: summary_opinion},
            "chat_history": [{"role": agent.role_name, "content": detailed_opinion, "model": model_name}],
            "agent_status": {agent.role_name: "idle"},
            "execution_logs": []
        }
    return node_func
