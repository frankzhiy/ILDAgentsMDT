from agents.base import BaseAgent
from core.shared_state import SharedState
from agents.discussion.prompts import DISCUSSION_SYSTEM_PROMPT, DISCUSSION_USER_PROMPT_TEMPLATE
from llm.client import llm_client
import json

class DiscussionAgent(BaseAgent):
    def __init__(self, llm_config=None):
        super().__init__(role_name="Team Discussion", llm_config=llm_config)

    def run(self, shared_state: SharedState, stream_callback: callable = None):
        """
        执行讨论逻辑
        """
        # 准备输入数据
        case_text = shared_state.raw_case_text
        specialist_opinions = json.dumps(shared_state.specialist_opinions, ensure_ascii=False, indent=2)
        conflicts = json.dumps(shared_state.conflicts, ensure_ascii=False, indent=2)
        
        content = DISCUSSION_USER_PROMPT_TEMPLATE.format(
            case_text=case_text,
            specialist_opinions=specialist_opinions,
            conflicts=conflicts
        )

        messages = [
            {"role": "system", "content": DISCUSSION_SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ]
        
        # 调用 LLM
        response = llm_client.get_completion(
            messages=messages,
            stream=True, # 启用流式
            stream_callback=stream_callback,
            config=self.llm_config
        )
        
        return response
