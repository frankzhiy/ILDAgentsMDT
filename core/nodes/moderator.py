from typing import Dict, Callable, Optional
from core.shared_state import SharedState, AgentGraphState
from agents.moderator.agent import ModeratorAgent
from config.llm_config import create_config_from_model_name

def moderator_node(state: AgentGraphState, ui_callback=None, stream_callback_factory: Optional[Callable] = None, log_callback=None, model_configs: Dict[str, str] = None, stop_event=None) -> Dict:
    """Moderator 节点函数"""
    if stop_event and stop_event.is_set():
        return {}

    llm_config = None
    if model_configs and "Moderator" in model_configs:
        llm_config = create_config_from_model_name(model_configs["Moderator"])
        
    agent = ModeratorAgent(llm_config=llm_config)
    
    if ui_callback:
        ui_callback("Moderator", "working")
        
    if log_callback:
        log_callback(f"[Moderator] 开始总结会诊意见... (Model: {agent.llm_config.model_name})")
        
    temp_state = SharedState(**state)
    
    # 准备流式输出
    chat_stream_callback = None
    summary_stream_callback = None
    
    if stream_callback_factory:
        chat_stream_callback = stream_callback_factory("Moderator", agent.llm_config.model_name, target="chat")
        summary_stream_callback = stream_callback_factory("Moderator", agent.llm_config.model_name, target="summary")
    
    result = agent.run(temp_state, stream_callback=chat_stream_callback, summary_stream_callback=summary_stream_callback)
    
    # 处理返回结果
    if isinstance(result, dict):
        patient_reply = result.get("content", "")
        medical_summary = result.get("summary", "")
    else:
        patient_reply = result
        medical_summary = result
    
    if log_callback:
        log_callback(f"[Moderator] 完成总结。")
        
    if ui_callback:
        ui_callback("Moderator", "done")

    return {
        "moderator_summary": medical_summary,
        "chat_history": [{"role": "Moderator", "content": patient_reply}],
        "agent_status": {"Moderator": "done"}
    }

def moderator_router_node(state: AgentGraphState, ui_callback=None, stream_callback_factory=None, log_callback=None, model_configs: Dict[str, str] = None, stop_event=None) -> Dict:
    """Moderator 路由节点函数"""
    if stop_event and stop_event.is_set():
        return {}

    llm_config = None
    if model_configs and "Moderator" in model_configs:
        llm_config = create_config_from_model_name(model_configs["Moderator"])
        
    agent = ModeratorAgent(llm_config=llm_config)
    
    if ui_callback:
        ui_callback("Moderator", "planning")
        
    if log_callback:
        log_callback(f"[Moderator] 正在规划会诊流程... (Model: {agent.llm_config.model_name})")
        
    temp_state = SharedState(**state)
    
    selected_agents = agent.plan(temp_state)
    
    if log_callback:
        log_callback(f"[Moderator] 决定邀请以下专家: {', '.join(selected_agents)}")
        
    return {"selected_agents": selected_agents}

