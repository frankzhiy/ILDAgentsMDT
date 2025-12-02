from typing import List, Dict
import streamlit as st
from langgraph.graph import StateGraph, END
from core.shared_state import SharedState, AgentGraphState
from core.nodes import case_organizer_node, specialist_node_factory, moderator_node

# 导入各 Agent (仅需专科医生，因为 Organizer 和 Moderator 封装在节点函数中)
from agents.radiologist.agent import RadiologistAgent
from agents.pathologist.agent import PathologistAgent
from agents.pulmonologist.agent import PulmonologistAgent
from agents.rheumatologist.agent import RheumatologistAgent

# --- Graph Construction ---

def build_mdt_graph(enabled_agents: List[str], ui_callback=None, chat_container=None, log_callback=None):
    """构建 LangGraph 图结构"""
    workflow = StateGraph(AgentGraphState)
    
    # 辅助函数：绑定 callback 和 container
    from functools import partial
    
    # 去重 enabled_agents，防止重复添加节点导致 ValueError
    enabled_agents = list(dict.fromkeys(enabled_agents))
    
    def bind_args(func):
        kwargs = {}
        if ui_callback:
            kwargs['ui_callback'] = ui_callback
        if chat_container:
            kwargs['chat_container'] = chat_container
        if log_callback:
            kwargs['log_callback'] = log_callback
        
        if kwargs:
            return partial(func, **kwargs)
        return func

    # 识别启用的角色
    has_organizer = "Case Organizer" in enabled_agents
    has_moderator = "Moderator" in enabled_agents
    
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
                ui_callback=ui_callback, 
                chat_container=chat_container,
                log_callback=log_callback
            )
            workflow.add_node(node_name, node_func)
            active_specialists.append(node_name)

    # 添加 Organizer 节点
    if has_organizer:
        workflow.add_node("Case Organizer", bind_args(case_organizer_node))
        
    # 添加 Moderator 节点
    if has_moderator:
        workflow.add_node("Moderator", bind_args(moderator_node))

    # --- 定义边 (Edges) ---
    
    # 1. 确定入口点
    entry_point = None
    if has_organizer:
        entry_point = "Case Organizer"
    elif active_specialists:
        entry_point = active_specialists[0]
    elif has_moderator:
        entry_point = "Moderator"
    else:
        # 没有任何 Agent 被选中，直接结束
        return None

    workflow.set_entry_point(entry_point)
    
    # 2. 连接 Organizer -> First Specialist
    if has_organizer:
        if active_specialists:
            workflow.add_edge("Case Organizer", active_specialists[0])
        elif has_moderator:
            workflow.add_edge("Case Organizer", "Moderator")
        else:
            workflow.add_edge("Case Organizer", END)
            
    # 3. 连接 Specialists 串行
    for i in range(len(active_specialists) - 1):
        workflow.add_edge(active_specialists[i], active_specialists[i+1])
        
    # 4. 连接 Last Specialist -> Moderator
    if active_specialists:
        last_spec = active_specialists[-1]
        if has_moderator:
            workflow.add_edge(last_spec, "Moderator")
        else:
            workflow.add_edge(last_spec, END)
            
    # 5. Moderator -> End
    if has_moderator:
        workflow.add_edge("Moderator", END)

    return workflow.compile()

# --- Main Entry Point ---

def run_mdt_round(shared_state: SharedState, enabled_agents: List[str], model_configs: Dict, status_container=None, chat_container=None, structured_info_placeholder=None, opinions_placeholder=None, log_placeholder=None):
    """
    执行一轮 MDT 会诊流程 (LangGraph 版本)
    :param status_container: Streamlit 容器，用于实时更新 UI
    :param chat_container: Streamlit 容器，用于流式输出对话
    :param structured_info_placeholder: Streamlit 容器，用于实时更新结构化病例
    :param opinions_placeholder: Streamlit 容器，用于实时更新专科意见
    :param log_placeholder: Streamlit 容器，用于实时更新执行日志
    """
    print("Starting MDT Round (LangGraph)...")
    
    # 导入 UI 渲染函数以进行实时更新
    # 注意：这里为了避免循环导入，我们在函数内部导入
    from ui.components.member_status_panel import render_member_status_panel
    from ui.components.shared_board_view import render_specialist_opinions_content, render_structured_info_content
    
    def update_ui():
        if status_container:
            render_member_status_panel(shared_state, enabled_agents, container=status_container)
        if structured_info_placeholder:
            with structured_info_placeholder.container():
                render_structured_info_content(shared_state)
        if opinions_placeholder:
            with opinions_placeholder.container():
                render_specialist_opinions_content(shared_state)

    # 定义日志回调
    def log_callback(message):
        shared_state.execution_logs.append(message)
        if log_placeholder:
            # 直接追加到容器，而不是全量刷新
            with log_placeholder:
                st.text(f"> {message}")

    # --- 多轮对话状态更新 ---
    # 轮次和原始输入历史已经在 main_page.py 中更新了，这里直接使用
    current_round = shared_state.round_count
    
    # 初始化本轮的历史记录容器
    if current_round not in shared_state.specialist_opinions_history:
        shared_state.specialist_opinions_history[current_round] = {}

    # 【关键修复】清空本轮的临时状态，防止上一轮的旧意见干扰本轮判断
    # 历史记录已经保存在 specialist_opinions_history 中，所以这里可以安全清空
    shared_state.specialist_opinions = {}
    shared_state.moderator_summary = ""

    # 初始化状态：所有启用的 Agent 设为 "idle" (待命)
    for agent in enabled_agents:
        shared_state.update_agent_status(agent, "idle")
    update_ui()
    
    # 1. 构建图
    # 定义回调函数，用于在 Node 内部更新 UI
    def node_ui_callback(role_name, status):
        if status_container:
            shared_state.update_agent_status(role_name, status)
            render_member_status_panel(shared_state, enabled_agents, container=status_container)
            
    app = build_mdt_graph(
        enabled_agents, 
        ui_callback=node_ui_callback, 
        chat_container=chat_container,
        log_callback=log_callback
    )
    
    if not app:
        print("No agents selected.")
        return
    
    # 2. 准备初始状态
    initial_state = shared_state.model_dump()
    
    # 3. 执行图 (使用 stream 模式以获取实时状态)
    
    final_state_dict = initial_state
    
    try:
        for event in app.stream(initial_state):
            # event 是一个字典，key 是 node name，value 是该 node 的输出
            for node_name, output in event.items():
                print(f"Node {node_name} finished.")
                
                # 更新 SharedState 数据
                if "structured_info" in output:
                    shared_state.structured_info = output["structured_info"]
                if "specialist_opinions" in output:
                    shared_state.specialist_opinions.update(output["specialist_opinions"])
                    # 更新历史记录
                    shared_state.specialist_opinions_history[current_round].update(output["specialist_opinions"])
                    
                if "moderator_summary" in output:
                    shared_state.moderator_summary = output["moderator_summary"]
                    # 更新历史记录
                    shared_state.moderator_summary_history[current_round] = output["moderator_summary"]
                    
                if "chat_history" in output:
                    for msg in output["chat_history"]:
                        shared_state.chat_history.append(msg)
                # execution_logs 已经在 callback 中处理了，这里不需要再 append
                
                # 记录最终状态
                final_state_dict.update(output)
                
                # 每次迭代结束（一个节点完成），更新 UI
                # 将该节点设为 idle (表示已完成待命)
                shared_state.update_agent_status(node_name, "idle")
                update_ui()
            
    except Exception as e:
        print(f"Error in execution: {e}")
        log_callback(f"Error: {str(e)}")
    
    # 最终全部设为 idle
    for agent in enabled_agents:
        shared_state.update_agent_status(agent, "idle")
    update_ui()
    
    print("MDT Round Completed.")
