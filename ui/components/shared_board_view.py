import streamlit as st
from core.shared_state import SharedState

def render_specialist_opinions_content(shared_state: SharedState):
    """
    渲染专科意见内容的辅助函数 (支持多轮展示)
    """
    history = shared_state.specialist_opinions_history
    
    # 如果历史为空，尝试显示当前的（兼容旧逻辑）
    if not history and not shared_state.specialist_opinions:
        st.info("暂无专科意见")
        return

    # 如果有历史记录，按轮次显示
    if history:
        sorted_rounds = sorted(history.keys())
        for r in sorted_rounds:
            st.caption(f"--- 第 {r} 轮讨论 ---")
            opinions = history[r]
            # 定义固定的显示顺序
            order = ["Radiologist", "Pathologist", "Pulmonologist", "Rheumatologist"]
            for role in order:
                if role in opinions:
                    with st.expander(f"{role} 意见", expanded=True):
                        st.write(opinions[role])
            # 显示其他可能存在的角色
            for role, opinion in opinions.items():
                if role not in order:
                    with st.expander(f"{role} 意见", expanded=True):
                        st.write(opinion)
    else:
        # 只有当前意见（第一轮刚开始可能还没写入 history）
        for role, opinion in shared_state.specialist_opinions.items():
            with st.expander(f"{role} 意见", expanded=True):
                st.write(opinion)

def render_structured_info_content(shared_state: SharedState):
    """
    渲染结构化病例内容的辅助函数
    """
    st.json(shared_state.structured_info)

def render_shared_board(shared_state: SharedState):
    """
    渲染共享信息栏视图
    返回: (raw_case_placeholder, structured_info_placeholder, opinions_placeholder)
    """
    st.subheader("📋 共享信息栏")
    
    tab1, tab2, tab3, tab4 = st.tabs(["原始病历", "结构化病例", "专科意见", "专家结论"])
    
    with tab1:
        raw_case_placeholder = st.empty()
        with raw_case_placeholder.container():
            if shared_state.raw_case_history:
                for idx, content in enumerate(shared_state.raw_case_history):
                    st.text_area(f"第 {idx+1} 轮输入", value=content, height=150, disabled=True, key=f"raw_case_{idx}")
            else:
                st.text_area("原始输入", value=shared_state.raw_case_text, height=300, disabled=True)
        
    with tab2:
        structured_info_placeholder = st.empty()
        with structured_info_placeholder.container():
            render_structured_info_content(shared_state)
        
    with tab3:
        # 创建一个空的容器，用于后续更新
        opinions_placeholder = st.empty()
        with opinions_placeholder.container():
            render_specialist_opinions_content(shared_state)
                    
    with tab4:
        # 显示历史结论
        if shared_state.moderator_summary_history:
            for r, summary in shared_state.moderator_summary_history.items():
                st.caption(f"--- 第 {r} 轮结论 ---")
                st.success(summary)
        elif shared_state.moderator_summary:
            st.success(shared_state.moderator_summary)
        else:
            st.info("等待主持专家总结...")
            
    return raw_case_placeholder, structured_info_placeholder, opinions_placeholder
