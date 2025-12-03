import json
from agents.base import BaseAgent
from core.shared_state import SharedState
from llm.client import llm_client
from agents.case_organizer.prompts.intake import ROLE_DEFINITION
from agents.case_organizer.prompts.structuring import STRUCTURING_INSTRUCTION, UPDATING_INSTRUCTION

class CaseOrganizerAgent(BaseAgent):
    def __init__(self, llm_config=None):
        super().__init__(role_name="Case Organizer", llm_config=llm_config)

    def run(self, shared_state: SharedState, stream_callback: callable = None) -> str:
        """
        病例整理逻辑：
        1. 读取 raw_case_text (最新输入)
        2. 判断是初次整理还是增量更新
        3. 调用 LLM 进行结构化提取/更新
        4. 更新 shared_state.structured_info
        """
        raw_text = shared_state.raw_case_text
        if not raw_text:
            return "未提供病例信息。"

        # 判断是否已有结构化信息
        existing_info = shared_state.structured_info
        
        if not existing_info:
            # 初次整理
            content = f"【原始病历】\n{raw_text}\n\n{STRUCTURING_INSTRUCTION}"
        else:
            # 增量更新
            existing_json = json.dumps(existing_info, ensure_ascii=False, indent=2)
            content = f"【已有结构化病例信息】\n{existing_json}\n\n【用户最新输入】\n{raw_text}\n\n{UPDATING_INSTRUCTION}"

        # 构造 Prompt
        messages = [
            {"role": "system", "content": ROLE_DEFINITION},
            {"role": "user", "content": content}
        ]

        # 调用 LLM (强制 JSON 模式)
        try:
            # 如果有回调，开启流式输出
            stream = True if stream_callback else False
            
            response = llm_client.get_completion(
                messages=messages,
                json_mode=True,
                stream=stream,
                stream_callback=stream_callback,
                config=self.llm_config
            )
            
            # 解析 JSON
            # 有些模型可能返回 Markdown 代码块，需要清洗
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(cleaned_response)
            
            if not existing_info:
                # 初次整理：直接是 structured_info
                shared_state.structured_info = parsed_data
                shared_state.new_evidence = {} # 初次没有“新”证据，或者可视作全部是新证据
            else:
                # 增量更新：包含 updated_case 和 new_evidence
                if "updated_case" in parsed_data:
                    shared_state.structured_info = parsed_data["updated_case"]
                    shared_state.new_evidence = parsed_data.get("new_evidence", {})
                else:
                    # Fallback: 如果模型没按新格式输出，假设全是 updated_case
                    shared_state.structured_info = parsed_data
                    shared_state.new_evidence = {}

            # 直接返回生成的内容 (JSON)，而不是摘要
            return response

        except json.JSONDecodeError:
            return f"病例整理失败：模型返回格式错误。\n原始返回: {response}"
        except Exception as e:
            return f"病例整理过程中发生错误: {str(e)}"
