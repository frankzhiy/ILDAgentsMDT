import streamlit as st

def render_agent_selector_panel():
    """
    渲染智能体选择面板
    """
    st.write("### 👥 参与会诊的专家")
    
    # 定义所有可用角色
    # 格式: (Role Key, Display Name, Default Checked)
    all_agents = [
        ("Case Organizer", "📋 病例整理员", True),
        ("Radiologist", "☢️ 影像科医生", True),
        ("Pathologist", "🔬 病理科医生", True),
        ("Pulmonologist", "🫁 呼吸科医生", True),
        ("Rheumatologist", "🦴 风湿科医生", True),
        ("Moderator", "👨‍🏫 主持专家", True)
    ]
    
    selected_agents = []
    
    # 使用 columns 让布局更紧凑
    for key, label, default in all_agents:
        if st.checkbox(label, value=default, key=f"chk_{key}"):
            selected_agents.append(key)
            
    return selected_agents
