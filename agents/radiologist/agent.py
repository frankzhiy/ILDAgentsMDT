from agents.base import BaseAgent
from core.shared_state import SharedState
from agents.radiologist.prompts.independent_analysis import ROLE_DEFINITION, ANALYSIS_INSTRUCTION
from agents.radiologist.prompts.summary_generation import SUMMARY_INSTRUCTION
from llm.client import llm_client
import json

class RadiologistAgent(BaseAgent):
    def __init__(self, llm_config=None):
        super().__init__(role_name="Radiologist", llm_config=llm_config)

    def run(self, shared_state: SharedState, stream_callback: callable = None, summary_stream_callback: callable = None):
        """
        影像科医生逻辑
        """
        # 1. 获取上下文：结构化病例 & 对话历史
        structured_info = shared_state.structured_info
        chat_history = shared_state.chat_history
        
        if not structured_info:
            return {"content": "暂无结构化病例信息，无法进行影像分析。", "summary": "暂无信息"}
            
        # 将结构化信息转换为字符串
        case_str = json.dumps(structured_info, ensure_ascii=False, indent=2)
        
        # 格式化对话历史
        history_str = ""
        if chat_history:
            history_list = []
            for msg in chat_history:
                role = msg["role"]
                content = msg["content"]
                # 只保留 User 和 Moderator 的对话，或者保留所有人的？
                # 用户需求：参考“过去轮数中所有医生的意见”。
                # 所以应该保留所有人的。
                history_list.append(f"【{role}】: {content}")
            history_str = "\n".join(history_list)
        else:
            history_str = "无往期讨论记录。"
        
        # 2. 构造 Prompt (详细分析)
        user_content = f"""【结构化病例信息】
{case_str}

【往期讨论历史】
{history_str}

{ANALYSIS_INSTRUCTION}"""

        messages = [
            {"role": "system", "content": ROLE_DEFINITION},
            {"role": "user", "content": user_content}
        ]
        
        # 3. 调用 LLM (详细分析 - 流式)
        try:
            stream = True if stream_callback else False
            detailed_analysis = llm_client.get_completion(
                messages=messages,
                stream=stream,
                stream_callback=stream_callback,
                config=self.llm_config
            )
            
            # 4. 生成总结 (流式)
            summary_messages = [
                {"role": "system", "content": ROLE_DEFINITION},
                {"role": "user", "content": f"【详细分析】\n{detailed_analysis}\n\n{SUMMARY_INSTRUCTION}"}
            ]
            
            summary_stream = True if summary_stream_callback else False
            summary = llm_client.get_completion(
                messages=summary_messages, 
                stream=summary_stream,
                stream_callback=summary_stream_callback,
                config=self.llm_config
            )
            
            return {"content": detailed_analysis, "summary": summary}
            
        except Exception as e:
            return {"content": f"影像分析过程中发生错误: {str(e)}", "summary": "分析出错"}
