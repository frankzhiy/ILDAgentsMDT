import streamlit as st

def render_member_status_panel(shared_state, enabled_agents, container=None):
    """
    渲染诊断室成员模块 & 成员状态概览
    :param shared_state: 共享状态对象
    :param enabled_agents: 当前启用的 Agent 列表 (用于判断离线)
    :param container: 可选的 st.container 或 st.empty，用于实时刷新
    """
    # 如果没有传入 container，就使用当前上下文
    if container is None:
        container = st.container()

    # 定义所有角色及其图标
    all_roles = [
        ("Case Organizer", "📋", "病例整理"),
        ("Radiologist", "☢️", "影像科"),
        ("Pathologist", "🔬", "病理科"),
        ("Pulmonologist", "🫁", "呼吸科"),
        ("Rheumatologist", "🦴", "风湿科"),
        ("Moderator", "👨‍🏫", "主持专家")
    ]

    agent_status = shared_state.agent_status
    
    # 统计各状态人数
    count_idle = 0
    count_working = 0
    count_offline = 0
    
    # 准备渲染数据
    render_data = []
    
    for role_key, icon, label in all_roles:
        is_enabled = role_key in enabled_agents
        
        if not is_enabled:
            status = "offline"
            count_offline += 1
        else:
            # 获取当前状态，默认为 idle (待命)
            # 注意：pipeline 运行时会更新 agent_status
            current_s = agent_status.get(role_key, "idle")
            if current_s == "working":
                status = "working"
                count_working += 1
            else:
                status = "idle"
                count_idle += 1
        
        render_data.append({
            "key": role_key,
            "icon": icon,
            "label": label,
            "status": status
        })

    with container:
        # 1. 注入 CSS 样式 (仅保留动画定义，颜色样式改为内联以确保显示)
        st.markdown("""
        <style>
        @keyframes breathing {
            0% { box-shadow: 0 0 5px rgba(33, 150, 243, 0.2); border-color: #2196f3; background-color: #e3f2fd; }
            50% { box-shadow: 0 0 20px rgba(33, 150, 243, 0.6); border-color: #1976d2; background-color: #bbdefb; }
            100% { box-shadow: 0 0 5px rgba(33, 150, 243, 0.2); border-color: #2196f3; background-color: #e3f2fd; }
        }
        
        .member-card-base {
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100px; /* 确保有高度 */
        }
        
        .status-working-anim {
            animation: breathing 2s infinite ease-in-out;
        }
        </style>
        """, unsafe_allow_html=True)

        # 2. 状态概览条 (使用内联样式)
        # 增加小标题，移除边框
        st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <h4 style="margin: 0; padding: 0; font-size: 16px; color: #333;">🩺 专家团队状态监控</h4>
        </div>
        """, unsafe_allow_html=True)

        # 3. 成员卡片网格
        cols = st.columns(len(all_roles))
        
        for idx, item in enumerate(render_data):
            status = item['status']
            
            # 定义内联样式
            # 移除 border: 2px solid; 改为无边框或仅背景
            # 用户要求“取消边框”，所以我们只用背景色和阴影
            base_style = "border-radius: 8px; padding: 8px; text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 80px;"
            
            if status == "idle":
                # 绿色背景，无边框
                style = f"{base_style} background-color: #e8f5e9; color: #2e7d32;"
                anim_class = ""
                status_desc = "待命"
            elif status == "working":
                # 蓝色背景，无边框 (动画通过 class 添加)
                style = f"{base_style} background-color: #e3f2fd; color: #0d47a1;"
                anim_class = "status-working-anim"
                status_desc = "回复中..."
            else: # offline
                # 灰色背景，无边框
                style = f"{base_style} background-color: #f5f5f5; color: #9e9e9e; opacity: 0.6;"
                anim_class = ""
                status_desc = "离线"
            
            with cols[idx]:
                st.markdown(f"""
                <div class="{anim_class}" style="{style}">
                    <div style="font-size: 24px; margin-bottom: 2px;">{item['icon']}</div>
                    <div style="font-weight: bold; font-size: 13px;">{item['label']}</div>
                    <div style="font-size: 11px; margin-top: 2px;">{status_desc}</div>
                </div>
                """, unsafe_allow_html=True)
