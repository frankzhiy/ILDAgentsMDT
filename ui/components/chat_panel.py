import streamlit as st

def render_chat_panel(chat_history):
    """
    渲染聊天框组件
    """
    st.subheader("💬 会诊对话记录")
    
    chat_container = st.container(height=400)
    
    with chat_container:
        if not chat_history:
            st.info("暂无对话记录，请开始会诊。")
        else:
            for msg in chat_history:
                role = msg.get("role", "Unknown")
                content = msg.get("content", "")
                model = msg.get("model", "")
                
                # 过滤掉 System 消息
                if role == "System":
                    continue
                
                # 构造标题
                title = f"🗣️ {role}"
                if model:
                    title += f" ({model})"
                
                # 使用折叠框展示，与流式输出保持一致
                with st.expander(title, expanded=True):
                    st.markdown(content)
    
    return chat_container
