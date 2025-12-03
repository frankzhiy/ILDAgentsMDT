from abc import ABC, abstractmethod
from core.shared_state import SharedState
from config.llm_config import get_config_for_agent

class BaseAgent(ABC):
    """
    Agent 基类
    """
    def __init__(self, role_name: str, llm_config=None):
        self.role_name = role_name
        self.llm_config = llm_config if llm_config else get_config_for_agent(role_name)

    @abstractmethod
    def run(self, shared_state: SharedState, stream_callback: callable = None):
        """
        执行 Agent 逻辑
        :param shared_state: 共享状态
        :param stream_callback: 流式输出回调函数
        :return: Agent 的输出结果 (str 或 dict)
        """
        pass
