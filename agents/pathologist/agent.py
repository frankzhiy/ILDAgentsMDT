from agents.base import BaseAgent
from core.shared_state import SharedState
from agents.pathologist.prompts.analysis import ROLE_DEFINITION, ANALYSIS_INSTRUCTION
from agents.pathologist.prompts.summary import SUMMARY_INSTRUCTION
from llm.client import llm_client
import json

class PathologistAgent(BaseAgent):
    def __init__(self):
        super().__init__(role_name="Pathologist")

    def run(self, shared_state: SharedState, stream_callback: callable = None):
        """
        病理科医生逻辑
        """
        # 1. 获取上下文
        structured_info = shared_state.structured_info
        radiologist_opinion = shared_state.specialist_opinions.get("Radiologist", "暂无影像科意见")
        chat_history = shared_state.chat_history
        
        if not structured_info:
            return {"content": "暂无结构化病例信息，无法进行病理分析。", "summary": "暂无信息"}
            
        case_str = json.dumps(structured_info, ensure_ascii=False, indent=2)
        
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
        
        # 2. 构造 Prompt
        content = f"""【结构化病例信息】
{case_str}

【往期讨论历史】
{history_str}

【本轮影像科医生意见】
{radiologist_opinion}

{ANALYSIS_INSTRUCTION}"""

        messages = [
            {"role": "system", "content": ROLE_DEFINITION},
            {"role": "user", "content": content}
        ]
        
        # 3. 调用 LLM
        try:
            stream = True if stream_callback else False
            detailed_analysis = llm_client.get_completion(
                messages=messages,
                stream=stream,
                stream_callback=stream_callback,
                config=self.llm_config
            )
            
            # 4. 生成总结
            summary_messages = [
                {"role": "system", "content": ROLE_DEFINITION},
                {"role": "user", "content": f"【详细分析】\n{detailed_analysis}\n\n{SUMMARY_INSTRUCTION}"}
            ]
            summary = llm_client.get_completion(
                messages=summary_messages, 
                stream=False,
                config=self.llm_config
            )
            
            return {"content": detailed_analysis, "summary": summary}
            
        except Exception as e:
            return {"content": f"病理分析过程中发生错误: {str(e)}", "summary": "分析出错"}
