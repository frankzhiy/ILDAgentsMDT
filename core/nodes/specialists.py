from typing import Dict, Callable, Optional
from core.shared_state import SharedState, AgentGraphState
from config.llm_config import create_config_from_model_name

def specialist_node_factory(agent_cls, role_name: str, ui_callback=None, stream_callback_factory: Optional[Callable] = None, log_callback=None, model_configs: Dict[str, str] = None, stop_event=None):
    """工厂函数，用于生成各专科医生的节点函数"""
    def node_func(state: AgentGraphState) -> Dict:
        # 检查是否已停止
        if stop_event and stop_event.is_set():
            return {}

        # 确定 LLM 配置
        llm_config = None
        if model_configs and role_name in model_configs:
            llm_config = create_config_from_model_name(model_configs[role_name])
            
        agent = agent_cls(llm_config=llm_config)
        
        if ui_callback:
            ui_callback(agent.role_name, "working")
            
        # 获取当前使用的模型名称
        model_name = agent.llm_config.model_name
        start_log = f"[{agent.role_name}] 开始分析... (Model: {model_name})"
        if log_callback:
            log_callback(start_log)
            
        temp_state = SharedState(**state)
        
        # 准备流式输出
        chat_stream_callback = None
        summary_stream_callback = None
        
        if stream_callback_factory:
            # 详细分析 -> 专科意见 (target="opinion")
            chat_stream_callback = stream_callback_factory(agent.role_name, model_name, target="opinion")
            # 总结 -> 专科总结 (target="specialist_summary")
            summary_stream_callback = stream_callback_factory(agent.role_name, model_name, target="specialist_summary")
            
        result = agent.run(temp_state, stream_callback=chat_stream_callback, summary_stream_callback=summary_stream_callback)
        
        # 处理返回结果
        if isinstance(result, dict):
            detailed_opinion = result.get("content", "")
            summary_opinion = result.get("summary", "")
        else:
            detailed_opinion = result
            summary_opinion = result
        
        end_log = f"[{agent.role_name}] 提交意见: {len(detailed_opinion)} chars"
        if log_callback:
            log_callback(end_log)
            
        if ui_callback:
            ui_callback(agent.role_name, "idle")
            
        return {
            "specialist_opinions": {agent.role_name: detailed_opinion},
            "specialist_summaries": {agent.role_name: summary_opinion},
            "chat_history": [], # 专科医生的详细意见不再放入 chat_history，而是只在右侧显示
            "agent_status": {agent.role_name: "idle"},
            "execution_logs": []
        }
    return node_func
