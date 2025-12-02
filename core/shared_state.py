from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Annotated, TypedDict
import operator

class SharedState(BaseModel):
    """
    共享状态模型，存储 MDT 会诊过程中的所有信息
    (主要用于 UI 展示和数据持久化)
    """
    # 原始输入
    raw_case_text: str = Field(default="", description="原始病历文本")
    
    # 结构化信息
    structured_info: Dict[str, str] = Field(default_factory=dict, description="结构化临床信息")
    
    # 各专科意见
    # key: 专科角色名, value: 意见文本
    specialist_opinions: Dict[str, str] = Field(default_factory=dict, description="各专科医生的分析意见")
    
    # 主持专家总结
    moderator_summary: str = Field(default="", description="主持专家的最终总结")
    
    # 对话历史 (用于 Chat Panel)
    chat_history: List[Dict[str, str]] = Field(default_factory=list, description="会诊过程中的对话记录")
    
    # 新增：Agent 状态 (用于成员状态概览)
    # key: role_name, value: status (e.g., "idle", "working", "done")
    agent_status: Dict[str, str] = Field(default_factory=dict, description="各智能体的当前状态")
    
    # 新增：详细执行日志 (用于日志模块)
    execution_logs: List[str] = Field(default_factory=list, description="详细的执行日志流")

    # --- 多轮对话支持 ---
    round_count: int = Field(default=0, description="当前对话轮数")
    raw_case_history: List[str] = Field(default_factory=list, description="每轮的原始输入历史")
    specialist_opinions_history: Dict[int, Dict[str, str]] = Field(default_factory=dict, description="历史轮次的专科意见")
    moderator_summary_history: Dict[int, str] = Field(default_factory=dict, description="历史轮次的专家总结")

    def update_opinion(self, role: str, opinion: str):
        self.specialist_opinions[role] = opinion
        self.chat_history.append({"role": role, "content": opinion})

    def set_summary(self, summary: str):
        self.moderator_summary = summary
        self.chat_history.append({"role": "Moderator", "content": f"【总结】\n{summary}"})

    def add_log(self, role: str, message: str):
        """添加对话记录"""
        self.chat_history.append({"role": role, "content": message})
        
    def add_execution_log(self, message: str):
        """添加系统执行日志"""
        self.execution_logs.append(message)
        
    def update_agent_status(self, role: str, status: str):
        self.agent_status[role] = status

# --- LangGraph 专用状态定义 ---

def merge_dicts(a: Dict, b: Dict) -> Dict:
    """合并字典的 reducer"""
    return {**a, **b}

def add_messages(left: List, right: List) -> List:
    """合并列表的 reducer"""
    return left + right

class AgentGraphState(TypedDict):
    """
    LangGraph 中流转的状态
    使用 Annotated 定义合并策略 (Reducer)
    """
    raw_case_text: str
    # 结构化信息：覆盖更新
    structured_info: Dict[str, str]
    # 专科意见：合并更新 (保留旧的，添加新的)
    specialist_opinions: Annotated[Dict[str, str], merge_dicts]
    # 总结：覆盖更新
    moderator_summary: str
    # 历史记录：追加更新
    chat_history: Annotated[List[Dict[str, str]], add_messages]
    # Agent 状态：合并更新
    agent_status: Annotated[Dict[str, str], merge_dicts]
    # 执行日志：追加更新
    execution_logs: Annotated[List[str], add_messages]
    
    # --- 多轮对话支持 ---
    round_count: int
    raw_case_history: List[str]
    specialist_opinions_history: Dict[int, Dict[str, str]]
    moderator_summary_history: Dict[int, str]
