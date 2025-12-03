from agents.base import BaseAgent
from core.shared_state import SharedState
from agents.moderator.prompts.analysis import ROLE_DEFINITION, ANALYSIS_INSTRUCTION, REPLY_INSTRUCTION
from agents.moderator.prompts.routing import ROUTING_ROLE_DEFINITION, ROUTING_INSTRUCTION
from llm.client import llm_client
import json

class ModeratorAgent(BaseAgent):
    def __init__(self, llm_config=None):
        super().__init__(role_name="Moderator", llm_config=llm_config)

    def plan(self, shared_state: SharedState):
        """
        路由逻辑：根据病例信息决定调用哪些专家
        """
        structured_info = shared_state.structured_info
        new_evidence = shared_state.new_evidence
        round_count = shared_state.round_count
        
        case_str = json.dumps(structured_info, ensure_ascii=False, indent=2)
        new_evidence_str = json.dumps(new_evidence, ensure_ascii=False, indent=2) if new_evidence else "无"
        
        context_str = ""
        if round_count > 1:
             context_str = f"""
【当前轮次】 第 {round_count} 轮
【本轮新证据】
{new_evidence_str}
"""
        else:
             context_str = f"""
【当前轮次】 第 {round_count} 轮 (首轮)
"""

        content = f"""【结构化病例信息】
{case_str}

{context_str}

{ROUTING_INSTRUCTION}"""

        messages = [
            {"role": "system", "content": ROUTING_ROLE_DEFINITION},
            {"role": "user", "content": content}
        ]
        
        try:
            response = llm_client.get_completion(
                messages=messages,
                stream=False,
                config=self.llm_config
            )
            
            # 清理 markdown 代码块标记 (如果 LLM 输出了 ```json ... ```)
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # 找到第一个换行符
                first_newline = cleaned_response.find("\n")
                if first_newline != -1:
                    cleaned_response = cleaned_response[first_newline+1:]
                
                # 去掉结尾的 ```
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
            
            selected_agents = json.loads(cleaned_response)
            
            # 验证输出是否为列表
            if not isinstance(selected_agents, list):
                print(f"Warning: Router output is not a list: {selected_agents}")
                return ["Pulmonologist"] # Fallback
                
            return selected_agents
            
        except Exception as e:
            print(f"Error in Moderator planning: {e}")
            return ["Pulmonologist"] # Fallback

    def run(self, shared_state: SharedState, stream_callback: callable = None, summary_stream_callback: callable = None):
        """
        主持专家逻辑：
        1. 综合各方意见，生成专业总结 (Internal Summary) - 支持流式输出 (summary_stream_callback)
        2. 基于总结，生成患者回复 (Patient Reply) - 支持流式输出 (stream_callback)
        """
        # 1. 获取上下文
        structured_info = shared_state.structured_info
        specialist_opinions = shared_state.specialist_opinions
        chat_history = shared_state.chat_history
        discussion_notes = shared_state.discussion_notes
        
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

【MDT 团队讨论纪要】
{discussion_notes}

{ANALYSIS_INSTRUCTION}"""

        summary_messages = [
            {"role": "system", "content": ROLE_DEFINITION},
            {"role": "user", "content": summary_content}
        ]
        
        try:
            # 第一步：生成专业总结
            # 如果提供了 summary_stream_callback，则开启流式
            summary_stream = True if summary_stream_callback else False
            
            medical_summary = llm_client.get_completion(
                messages=summary_messages,
                stream=summary_stream,
                stream_callback=summary_stream_callback,
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
