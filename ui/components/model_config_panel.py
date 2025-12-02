import streamlit as st
from config.settings import settings

def render_model_config_panel(enabled_agents):
    """
    渲染模型配置面板 (支持每个 Agent 独立配置)
    :param enabled_agents: 当前选中的 Agent 列表
    """
    with st.expander("⚙️ 模型配置", expanded=False):
        st.caption(f"Global API Key: {settings.openai_api_key[:5]}***")
        
        # 默认配置
        default_model = "gpt-4"
        default_temp = 0.7
        
        configs = {}
        
        # 使用 Tabs 分别配置
        # 为了避免 Tab 太多，我们只显示 "Global" 和 "Per-Agent"
        
        config_mode = st.radio("配置模式", ["全局统一配置", "按角色单独配置"], horizontal=True)
        
        if config_mode == "全局统一配置":
            global_model = st.selectbox("统一模型", ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"], index=0, key="global_model")
            global_temp = st.slider("统一 Temperature", 0.0, 1.0, default_temp, key="global_temp")
            
            # 为所有启用的 Agent 应用此配置
            for agent in enabled_agents:
                configs[agent] = {"model_name": global_model, "temperature": global_temp}
                
        else:
            # 按角色配置
            if not enabled_agents:
                st.warning("请先选择参与会诊的专家")
            else:
                # 创建 Tabs
                tabs = st.tabs([a[:4]+".." for a in enabled_agents]) # 简写名字防止 Tab 过宽
                
                for i, agent_name in enumerate(enabled_agents):
                    with tabs[i]:
                        st.caption(f"配置 {agent_name}")
                        m = st.selectbox(f"模型 ({agent_name})", ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"], index=0, key=f"model_{agent_name}")
                        t = st.slider(f"Temp ({agent_name})", 0.0, 1.0, default_temp, key=f"temp_{agent_name}")
                        configs[agent_name] = {"model_name": m, "temperature": t}
        
        return configs
