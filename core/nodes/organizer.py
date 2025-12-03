from typing import Dict, Callable, Optional
from core.shared_state import SharedState, AgentGraphState
from agents.case_organizer.agent import CaseOrganizerAgent
from config.llm_config import create_config_from_model_name

def case_organizer_node(state: AgentGraphState, ui_callback=None, stream_callback_factory: Optional[Callable] = None, log_callback=None, model_configs: Dict[str, str] = None, stop_event=None) -> Dict:
    # 检查是否已停止
    if stop_event and stop_event.is_set():
        return {}

    llm_config = None
    if model_configs and "Case Organizer" in model_configs:
        llm_config = create_config_from_model_name(model_configs["Case Organizer"])
        
    agent = CaseOrganizerAgent(llm_config=llm_config)
    
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
    if stream_callback_factory:
        stream_callback = stream_callback_factory(agent.role_name, model_name)

    result = agent.run(temp_state, stream_callback=stream_callback)
    
    end_log = f"[{agent.role_name}] 完成: {result[:50]}..."
    if log_callback:
        log_callback(end_log)

    # UI 更新：完成工作
    if ui_callback:
        ui_callback(agent.role_name, "idle")
    
    return {
        "structured_info": temp_state.structured_info,
        "new_evidence": temp_state.new_evidence,
        "chat_history": [
            {"role": agent.role_name, "content": result, "model": model_name}
        ],
        "agent_status": {agent.role_name: "idle"},
        # execution_logs 已经在 log_callback 中处理了，这里返回空或者不返回
        # 但为了兼容性，还是返回，虽然可能会重复如果外部也处理
        # 我们修改 run_mdt_round 不再依赖这里的 execution_logs 来更新 UI
        "execution_logs": [] 
    }
