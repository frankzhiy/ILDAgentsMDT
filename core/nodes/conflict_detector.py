from typing import Dict, Callable, Optional
from core.shared_state import SharedState, AgentGraphState
from agents.conflict_detector.agent import ConflictDetectorAgent
from config.llm_config import create_config_from_model_name

def conflict_detector_node(state: AgentGraphState, ui_callback=None, stream_callback_factory: Optional[Callable] = None, log_callback=None, model_configs: Dict[str, str] = None, stop_event=None) -> Dict:
    """冲突检测节点函数"""
    print("DEBUG: Entering conflict_detector_node")
    if stop_event and stop_event.is_set():
        return {}

    llm_config = None
    if model_configs and "Conflict Detector" in model_configs:
        llm_config = create_config_from_model_name(model_configs["Conflict Detector"])
        
    agent = ConflictDetectorAgent(llm_config=llm_config)
    
    if ui_callback:
        ui_callback("Conflict Detector", "working")
        
    if log_callback:
        log_callback(f"[Conflict Detector] 正在检测意见冲突... (Model: {agent.llm_config.model_name})")
        
    temp_state = SharedState(**state)
    
    # 准备流式输出 (虽然通常不需要，但为了 UI 统一)
    stream_callback = None
    if stream_callback_factory:
        stream_callback = stream_callback_factory("Conflict Detector", agent.llm_config.model_name)
    
    conflicts = agent.run(temp_state, stream_callback=stream_callback)
    
    # 如果没有冲突，为了 UI 显示，添加一条说明信息
    if not conflicts:
        summaries = temp_state.specialist_summaries
        if len(summaries) < 2:
             conflicts = [{
                 "issue": "无法进行冲突检测",
                 "description": f"当前仅有 {len(summaries)} 位专家提交了总结，不足以进行对比检测 (至少需要2位)。",
                 "severity": "info"
             }]
        else:
             conflicts = [{
                 "issue": "检测完成",
                 "description": "各专家意见基本一致，未发现明显矛盾点。",
                 "severity": "success"
             }]

    if log_callback:
        if conflicts:
            log_callback(f"[Conflict Detector] 检测到 {len(conflicts)} 个冲突点。")
        else:
            log_callback(f"[Conflict Detector] 未检测到明显冲突。")
            
    if ui_callback:
        ui_callback("Conflict Detector", "done")

    print(f"DEBUG: Exiting conflict_detector_node with {len(conflicts)} conflicts")
    return {
        "conflicts": conflicts,
        "agent_status": {"Conflict Detector": "done"}
    }
