from core.shared_state import AgentGraphState, SharedState
from agents.discussion.agent import DiscussionAgent
from core.schemas import StreamEvent
from config.llm_config import create_config_from_model_name

def discussion_node(state: AgentGraphState, ui_callback=None, stream_callback_factory=None, log_callback=None, model_configs=None, stop_event=None):
    """
    Team Discussion 节点
    """
    print("DEBUG: Entering discussion_node")
    # 检查是否有冲突，如果没有冲突，可能不需要讨论 (或者讨论只是确认一致)
    # 但为了流程完整性，我们总是运行，让 Agent 自己判断
    
    if ui_callback:
        ui_callback("Team Discussion", "working")
        
    llm_config = None
    if model_configs and "Team Discussion" in model_configs:
        llm_config = create_config_from_model_name(model_configs["Team Discussion"])
        
    agent = DiscussionAgent(llm_config=llm_config)
    
    stream_callback = None
    if stream_callback_factory:
        stream_callback = stream_callback_factory("Team Discussion", agent.llm_config.model_name)
    
    # 将 AgentGraphState (dict) 转换为 SharedState (Pydantic model)
    temp_state = SharedState(**state)
        
    result = agent.run(temp_state, stream_callback=stream_callback)
    
    if ui_callback:
        ui_callback("Team Discussion", "done")
        
    print(f"DEBUG: Exiting discussion_node with result: {str(result)[:50]}...")
    return {"discussion_notes": result}
