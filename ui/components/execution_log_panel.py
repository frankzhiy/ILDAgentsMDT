import streamlit as st
import time

def render_execution_log_panel(execution_logs, container=None):
    """
    渲染详细执行日志模块
    :param execution_logs: 日志列表
    :param container: 可选的 Streamlit 容器，如果提供则在该容器内渲染
    """
    # 如果没有提供 container，就使用当前上下文
    parent = container if container else st
    
    # 如果是直接调用（非 container 内部），可能需要 subheader
    if container is None:
        st.subheader("📜 系统执行日志")
        target_container = st.container(height=300)
    else:
        # 如果传入了 container，我们假设外部已经处理了布局，或者直接在这个 container 里写
        # 但为了保持滚动效果，我们最好在 container 里再套一个固定高度的 container
        # 或者外部传入的就是那个固定高度的 container
        target_container = container

    with target_container:
        # 清空容器内容（如果是实时更新，通常需要清空重绘）
        # 注意：st.empty() 可以清空，但 st.container() 不能直接清空。
        # 如果传入的是 st.empty()，则每次都是新的。
        # 如果传入的是 st.container()，则会追加。
        
        # 策略：我们假设外部传入的是一个 st.empty() 用于全量刷新，
        # 或者我们在这里只负责渲染内容。
        
        # 简单起见，我们只负责渲染列表。
        if not execution_logs:
            st.caption("暂无日志...")
        else:
            # 倒序显示？或者正序。通常日志是正序。
            for log in execution_logs:
                st.text(f"> {log}")
