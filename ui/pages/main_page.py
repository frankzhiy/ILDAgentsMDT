import streamlit as st
from core.shared_state import SharedState
from core.pipeline import run_mdt_round

# 导入组件
from ui.components.chat_panel import render_chat_panel
from ui.components.shared_board_view import render_shared_board
from ui.components.model_config_panel import render_model_config_panel
from ui.components.agent_selector_panel import render_agent_selector_panel
from ui.components.member_status_panel import render_member_status_panel
from ui.components.execution_log_panel import render_execution_log_panel

# --- 测试病例数据 ---
TEST_CASES = {
    "自定义输入": "",
    "测试病例": """患者女性，52 岁，办公室文员，非吸烟者。自述约半年多前开始出现活动后气促，最初在快走或上楼时偶有胸闷感，近两三个月气促逐渐加重，伴少量干咳，有时夜间会咳几声，无明显痰液，也无发热或咯血。近几个月体重似乎有所下降，但患者不清楚具体变化。既往有甲状腺方面的问题，患者记不得是甲亢还是甲减，目前是否规律服药也不确定。无明确关节红肿，但偶尔提到早晨手部僵硬几分钟；近来皮肤较干。无明显皮疹。无口干眼干的明确主诉。家族史中父亲年轻时患过一种免疫类疾病，具体名称不清楚。

环境方面，家中卧室有一个使用多年的加湿器，偶尔使用；患者不记得上次清洗时间。家庭过去曾养过一只鸟，大约半年后送人。住处墙角偶有潮湿发黑情况，患者不清楚持续时间。工作环境中无长期粉尘接触。

体格检查生命体征平稳，双下肺背部在吸气末可闻到细微啰音。无杵状指。心脏及腹部查体无特殊发现。
实验室方面，血常规及生化基本正常，ESR 略高。ANA 为阳性，但检查报告上未看到滴度和型态记录。其他免疫学指标患者不记得是否做过，资料中未找到相关结果。KL-6 未见记录。

肺功能检查方面，患者以前做过一次，自述“医生说有点下降”，但未携带结果。三个月前在当地医院做过一份胸部 HRCT，报告描述为双肺散在片状影及多发网状影，部分位于胸膜下及下叶外带，可见局灶性磨玻璃影，部分区域呈线样改变，未见蜂窝状表现，气道有轻度扩张是否与牵拉相关未写明。是否存在较明显的分布特征未在报告中提及。""",
    
    "测试补充": """患者在随访中补做了肺功能、免疫学检查以及胸部 HRCT 原片复阅。肺功能显示 FVC 1.98 L，为预计值的 68%，FEV1 1.72 L（72% 预计值），FEV1/FVC 为 87%，TLC 3.45 L（70% 预计值），RV 1.10 L，弥散量 DLCO 为预计值的 47%，DLCO/VA 为 67%，总体表现为限制性通气功能并伴弥散能力下降。免疫学检查方面，ANA 报告为 1:320，细颗粒型，其余 ENA 结果中，SSA、SSB、Sm、Scl-70、Jo-1 等均为阴性，而 RNP 为弱阳性。RF 与抗 CCP 均为阴性，ESR 为 29 mm/h，其余炎症指标正常。KL-6 和 IgE 本次未检测。胸部 HRCT 由胸部影像科医师复阅后描述为双肺下叶及胸膜下区域可见中等范围的网状影，散在磨玻璃影主要位于下叶背段，可见部分线样影和小叶间隔增厚，局部可见轻度气道扩张但缺乏明确牵拉表现，未见蜂窝状结构，上叶改变不明显，亦未见胸膜增厚、胸腔积液、肺门或纵隔淋巴结肿大。整体影像无明显结节或空气陷闭表现。本次随访后，患者尚未进行其他检查。"""
}

def render_page(shared_state: SharedState):
    """
    主会诊页面逻辑
    """
    
    # --- 侧边栏 ---
    with st.sidebar:
        selected_agents = render_agent_selector_panel()
        st.divider()
        # 传入 selected_agents 以支持按角色配置
        model_configs = render_model_config_panel(selected_agents)

    # --- 主区域布局 ---
    # 比例 1:6:3
    # Streamlit 无法精确控制比例，但我们可以用 container height 来模拟
    # 假设总高度 1000px (或自适应)
    
    # 1. 顶部：成员状态 (Ratio 1)
    top_container = st.container(height=120)
    with top_container:
        status_container = st.empty()
        render_member_status_panel(shared_state, selected_agents, container=status_container)
    
    # 2. 中间：医患对话 (Ratio 6)
    # 这里是主要的聊天区域
    middle_container = st.container(height=600)
    with middle_container:
        # 渲染对话历史：只显示 User 和 Moderator
        dialogue_history = [msg for msg in shared_state.chat_history if msg["role"] in ["user", "Moderator"]]
        
        if not dialogue_history:
            st.info("请在下方输入病例信息开始会诊...")
        else:
            for msg in dialogue_history:
                role = msg["role"]
                content = msg["content"]
                
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                elif role == "Moderator":
                    with st.chat_message("assistant", avatar="👨‍⚕️"):
                        st.markdown(content)

    # 3. 底部：共享信息 & 内部讨论 (Ratio 3)
    bottom_container = st.container(height=300)
    with bottom_container:
        tab_board, tab_internal, tab_logs = st.tabs(["📋 共享信息", "🧠 内部讨论", "📜 执行日志"])
        
        with tab_board:
            raw_case_placeholder, structured_info_placeholder, opinions_placeholder = render_shared_board(shared_state)
            
        with tab_internal:
            # 这里显示 Agent 的详细分析过程 (Streaming)
            # 我们需要传递这个 container 给 pipeline
            chat_container = st.container()
            # 初始渲染历史记录 (非 Moderator 的部分)
            internal_history = [msg for msg in shared_state.chat_history if msg["role"] not in ["user", "Moderator"]]
            with chat_container:
                 for msg in internal_history:
                     role = msg['role']
                     model = msg.get('model', '')
                     title = f"🗣️ {role}"
                     if model:
                         title += f" ({model})"
                     with st.expander(title, expanded=False):
                         st.markdown(msg['content'])

        with tab_logs:
            log_container = st.container(height=300)
            with log_container:
                render_execution_log_panel(shared_state.execution_logs, container=log_container)

    # --- 输入区 (底部) ---
    # 使用 columns 布局：左侧输入框，右侧选择框
    
    st.divider()
    
    # 创建一个占位符，用于动态切换“输入模式”和“运行模式”
    input_area = st.empty()

    # 定义提交处理函数 (Callback)
    def handle_submit():
        user_input = st.session_state.get("chat_input_widget", "").strip()
        if not user_input:
            return
            
        # 1. 更新状态
        shared_state.raw_case_text = user_input
        shared_state.round_count += 1
        
        # 更新原始病历历史
        shared_state.raw_case_history.append(f"【第 {shared_state.round_count} 轮输入】\n{user_input}")
        
        # 添加到对话历史
        user_msg = {"role": "user", "content": user_input}
        shared_state.chat_history.append(user_msg)
        
        # 清空输入框 (通过 session_state)
        st.session_state["chat_input_widget"] = ""
        
        # 2. 设置运行标志，交由主循环处理
        st.session_state["trigger_mdt_run"] = True

    # 默认渲染输入界面
    with input_area.container():
        input_col, select_col = st.columns([4, 1])
        
        with select_col:
            # 回调函数：当下拉菜单变化时更新 shared_state 和 text_area
            def on_case_select():
                selected = st.session_state.get("case_selector")
                if selected and selected in TEST_CASES:
                    new_text = TEST_CASES[selected]
                    # 更新 session_state 中的 input widget
                    st.session_state["chat_input_widget"] = new_text

            st.selectbox(
                "选择测试病例",
                options=list(TEST_CASES.keys()),
                key="case_selector",
                on_change=on_case_select,
                index=0,
                label_visibility="collapsed" # 隐藏 label 以节省空间
            )

        with input_col:
            # 移除 st.form，改用 Callback 模式
            col_text, col_btn = st.columns([6, 1])
            with col_text:
                st.text_input(
                    "输入", 
                    placeholder="请输入病例描述或追问...", 
                    key="chat_input_widget", 
                    label_visibility="collapsed",
                    on_change=handle_submit # 回车触发提交
                )
            with col_btn:
                st.button("发送", use_container_width=True, on_click=handle_submit) # 按钮触发提交

    # --- 处理运行逻辑 ---
    if st.session_state.get("trigger_mdt_run", False):
        # 重置标志，防止重复运行
        st.session_state["trigger_mdt_run"] = False
        
        # 运行 Pipeline
        # 使用 spinner 提示，但允许流式输出更新其他容器
        with st.spinner("MDT 专家组正在分析中..."):
            try:
                run_mdt_round(
                    shared_state, 
                    selected_agents, 
                    model_configs, 
                    status_container=status_container, 
                    chat_container=chat_container,
                    structured_info_placeholder=structured_info_placeholder,
                    opinions_placeholder=opinions_placeholder,
                    log_placeholder=log_container
                )
            except Exception as e:
                st.error(f"运行出错: {e}")
        
        # 运行完成后刷新页面，显示最终状态
        st.rerun()

