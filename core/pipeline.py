from typing import List, Dict
from langgraph.graph import StateGraph, END
from core.shared_state import SharedState, AgentGraphState
from core.nodes import case_organizer_node, specialist_node_factory, moderator_node, moderator_router_node, conflict_detector_node, discussion_node

# 导入各 Agent (仅需专科医生，因为 Organizer 和 Moderator 封装在节点函数中)
from agents.radiologist.agent import RadiologistAgent
from agents.pathologist.agent import PathologistAgent
from agents.pulmonologist.agent import PulmonologistAgent
from agents.rheumatologist.agent import RheumatologistAgent

# --- Graph Construction ---

def build_mdt_graph(enabled_agents: List[str], ui_callback=None, stream_callback_factory=None, log_callback=None, model_configs: Dict[str, str] = None, stop_event=None):
    """构建 LangGraph 图结构 (Agentic Pattern: Router-Workers)"""
    workflow = StateGraph(AgentGraphState)
    
    # 辅助函数：绑定 callback 和 container
    from functools import partial
    
    # 去重 enabled_agents
    enabled_agents = list(dict.fromkeys(enabled_agents))
    
    def bind_args(func):
        kwargs = {}
        if ui_callback:
            kwargs['ui_callback'] = ui_callback
        if stream_callback_factory:
            kwargs['stream_callback_factory'] = stream_callback_factory
        if log_callback:
            kwargs['log_callback'] = log_callback
        if model_configs:
            kwargs['model_configs'] = model_configs
        if stop_event:
            kwargs['stop_event'] = stop_event
        
        if kwargs:
            return partial(func, **kwargs)
        return func

    # 识别启用的角色
    has_organizer = "Case Organizer" in enabled_agents
    has_moderator = "Moderator" in enabled_agents
    # 默认启用冲突检测 (如果启用了 Moderator)
    has_conflict_detector = has_moderator 
    # 默认启用团队讨论 (如果启用了 Moderator)
    has_discussion = has_moderator
    
    # 专科医生映射
    agent_map = {
        "Radiologist": RadiologistAgent,
        "Pathologist": PathologistAgent,
        "Pulmonologist": PulmonologistAgent,
        "Rheumatologist": RheumatologistAgent
    }
    
    active_specialists = []
    for name in enabled_agents:
        if name in agent_map:
            node_name = name 
            # 使用 factory 生成并绑定 callback
            node_func = specialist_node_factory(
                agent_map[name], 
                role_name=node_name,
                ui_callback=ui_callback, 
                stream_callback_factory=stream_callback_factory,
                log_callback=log_callback,
                model_configs=model_configs,
                stop_event=stop_event
            )
            workflow.add_node(node_name, node_func)
            active_specialists.append(node_name)

    # 添加 Organizer 节点
    if has_organizer:
        workflow.add_node("Case Organizer", bind_args(case_organizer_node))
        
    # 添加 Moderator 节点 (Router 和 Aggregator)
    if has_moderator:
        # 1. Router: 负责规划
        workflow.add_node("Moderator_Router", bind_args(moderator_router_node))
        # 2. Aggregator: 负责总结 (沿用 "Moderator" 名称以保持 UI 兼容)
        workflow.add_node("Moderator", bind_args(moderator_node))
        
    # 添加 Conflict Detector 节点
    if has_conflict_detector:
        workflow.add_node("Conflict Detector", bind_args(conflict_detector_node))

    # 添加 Team Discussion 节点
    if has_discussion:
        workflow.add_node("Team Discussion", bind_args(discussion_node))

    # --- 定义边 (Edges) ---
    
    # 1. 确定入口点
    entry_point = None
    if has_organizer:
        entry_point = "Case Organizer"
    elif has_moderator:
        entry_point = "Moderator_Router"
    elif active_specialists:
        entry_point = active_specialists[0]
    else:
        # 没有任何 Agent 被选中，直接结束
        return None

    workflow.set_entry_point(entry_point)
    
    # 2. 连接 Organizer -> Router (或 First Specialist)
    if has_organizer:
        if has_moderator:
            workflow.add_edge("Case Organizer", "Moderator_Router")
        elif active_specialists:
            workflow.add_edge("Case Organizer", active_specialists[0])
        else:
            workflow.add_edge("Case Organizer", END)
            
    # 3. 核心路由逻辑
    if has_moderator:
        def route_specialists(state: AgentGraphState):
            selected = state.get("selected_agents", [])
            # 过滤：只调用在 UI 中启用的专家
            target_nodes = [s for s in selected if s in active_specialists]
            
            if not target_nodes:
                # 如果没有选中的专家（或都被禁用了），直接去总结
                return ["Moderator"]
            return target_nodes

        # Router -> Specialists (并行)
        workflow.add_conditional_edges(
            "Moderator_Router",
            route_specialists
        )
        
        # Specialists -> Conflict Detector (汇聚)
        for spec in active_specialists:
            workflow.add_edge(spec, "Conflict Detector")
            
        # Conflict Detector -> Team Discussion
        workflow.add_edge("Conflict Detector", "Team Discussion")
        
        # Team Discussion -> Moderator
        workflow.add_edge("Team Discussion", "Moderator")
        
        # Moderator -> END
        workflow.add_edge("Moderator", END)
        
    else:
        # 降级模式：如果没有 Moderator，则使用旧的串行逻辑
        for i in range(len(active_specialists) - 1):
            workflow.add_edge(active_specialists[i], active_specialists[i+1])
            
        if active_specialists:
            workflow.add_edge(active_specialists[-1], END)

    return workflow.compile()
