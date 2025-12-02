from agents.base import BaseAgent
from core.shared_state import SharedState
from agents.moderator.prompts.analysis import ROLE_DEFINITION, ANALYSIS_INSTRUCTION, REPLY_INSTRUCTION
from llm.client import llm_client
import json

class ModeratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role_name="Moderator")

    def run(self, shared_state: SharedState, stream_callback: callable = None):
        """
        主持专家逻辑：
        1. 综合各方意见，生成专业总结 (Internal Summary)
        2. 基于总结，生成患者回复 (Patient Reply) - 支持流式输出
        """
        # 1. 获取上下文
        structured_info = shared_state.structured_info
        specialist_opinions = shared_state.specialist_opinions
        chat_history = shared_state.chat_history
        
        case_str = json.dumps(structured_info, ensure_ascii=False, indent=2)
        opinions_str = "\n".join([f"【{role}】\n{opinion}" for role, opinion in specialist_opinions.items()])
        
        # 格式化对话历史
        history_str = ""
        if chat_history:
            history_list = []
            for msg in chat_history:
                role = msg["role"]
                content = msg["content"]
                history_list.append(f"【{role}】: {content}")
            history_str = "\n".join(history_list)
        else:
            history_str = "无往期讨论记录。"

        # 2. 生成专业总结 (非流式，用于内部记录和展示在结论栏)
        summary_content = f"""【结构化病例信息】
{case_str}

【往期讨论历史】
{history_str}

【本轮各专科意见】
{opinions_str}

{ANALYSIS_INSTRUCTION}"""

        summary_messages = [
            {"role": "system", "content": ROLE_DEFINITION},
            {"role": "user", "content": summary_content}
        ]
        
        try:
            # 第一步：生成专业总结
            medical_summary = llm_client.get_completion(
                messages=summary_messages,
                stream=False,
                config=self.llm_config
            )
            
            # 3. 生成患者回复 (流式，用于对话框)
            # 构造对话历史上下文，以便 Moderator 能够回答追问
            # 提取 chat_history 中的 User 和 Moderator 消息
            dialogue_history = []
            for msg in shared_state.chat_history:
                if msg["role"] == "user":
                    dialogue_history.append(f"基层医生: {msg['content']}")
                elif msg["role"] == "Moderator":
                    dialogue_history.append(f"MDT专家: {msg['content']}")
            
            dialogue_context = "\n".join(dialogue_history)
            
            reply_content = f"""【MDT 专业总结】
{medical_summary}

【医患对话历史】
{dialogue_context}

{REPLY_INSTRUCTION}"""

            reply_messages = [
                {"role": "system", "content": ROLE_DEFINITION},
                {"role": "user", "content": reply_content}
            ]
            
            stream = True if stream_callback else False
            patient_reply = llm_client.get_completion(
                messages=reply_messages,
                stream=stream,
                stream_callback=stream_callback,
                config=self.llm_config
            )
            
            return {"content": patient_reply, "summary": medical_summary}
            
        except Exception as e:
            return {"content": f"主持专家分析过程中发生错误: {str(e)}", "summary": "分析出错"}
