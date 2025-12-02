import streamlit as st
from ui.layouts.main_layout import render_main_layout
from ui.pages.main_page import render_page
from core.shared_state import SharedState

# 初始化 Session State
if "shared_state" not in st.session_state:
    st.session_state["shared_state"] = SharedState()

def main():
    # 1. 渲染布局配置
    render_main_layout()
    
    # 2. 简单的路由逻辑 (目前只有一个主页面)
    # 如果将来有多个页面，可以用 st.sidebar.radio 切换
    
    # 3. 渲染主页面
    render_page(st.session_state["shared_state"])

if __name__ == "__main__":
    main()
