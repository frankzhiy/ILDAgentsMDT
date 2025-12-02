import streamlit as st

def render_main_layout():
    """
    主页面布局设置
    """
    st.set_page_config(
        page_title="ILD Agents MDT",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 移除标题和横线
    # st.title("🏥 多智能体 MDT 虚拟诊室 (ILD Agents)")
    # st.markdown("---")
