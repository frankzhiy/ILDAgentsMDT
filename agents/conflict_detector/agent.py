from agents.base import BaseAgent
from core.shared_state import SharedState
from agents.conflict_detector.prompts.detection import ROLE_DEFINITION, DETECTION_INSTRUCTION
from llm.client import llm_client
import json

class ConflictDetectorAgent(BaseAgent):
    def __init__(self, llm_config=None):
        super().__init__(role_name="Conflict Detector", llm_config=llm_config)

    def run(self, shared_state: SharedState, stream_callback: callable = None):
        """
        冲突检测逻辑
        """
        # 1. 获取各专科意见
        summaries = shared_state.specialist_summaries
        
        # 如果只有一个或没有专家发言，自然没有冲突
        if len(summaries) < 2:
            return []

        # 2. 构造 Prompt
        summaries_str = "\n\n".join([f"【{role}】\n{summary}" for role, summary in summaries.items()])
        
        content = f"""【各专科医生意见总结】
{summaries_str}

{DETECTION_INSTRUCTION}"""

        messages = [
            {"role": "system", "content": ROLE_DEFINITION},
            {"role": "user", "content": content}
        ]
        
        # 3. 调用 LLM
        try:
            # 冲突检测通常不需要流式展示给用户看过程，只需要结果
            # 但为了保持一致性，如果传了 stream_callback 也可以用
            stream = True if stream_callback else False
            
            response = llm_client.get_completion(
                messages=messages,
                json_mode=True, # 强制 JSON
                stream=stream,
                stream_callback=stream_callback,
                config=self.llm_config
            )
            
            # 清洗和解析
            cleaned_response = response.replace("```json", "").replace("```", "").strip()
            parsed_data = json.loads(cleaned_response)
            
            if isinstance(parsed_data, dict):
                if "conflicts" in parsed_data:
                    conflicts = parsed_data["conflicts"]
                elif "items" in parsed_data:
                    conflicts = parsed_data["items"]
                else:
                    # 尝试作为单个对象处理，或者返回空
                    print(f"Warning: Conflict Detector returned unexpected dict format: {parsed_data.keys()}")
                    conflicts = []
            elif isinstance(parsed_data, list):
                conflicts = parsed_data
            else:
                conflicts = []
            
            return conflicts
            
        except Exception as e:
            print(f"冲突检测出错: {e}")
            return []
