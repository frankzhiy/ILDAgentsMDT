from pydantic import BaseModel
from config.settings import settings

class LLMConfig(BaseModel):
    api_key: str
    base_url: str
    model_name: str
    temperature: float = 0.7

# --- 基础配置获取 ---
# 优先使用 ChatAnywhere Key，如果没有则回退到 OpenAI Key (假设用户可能只配了一个)
CA_KEY = settings.chatanywhere_api_key or settings.openai_api_key
CA_URL = settings.chatanywhere_base_url

# DeepSeek 官方配置 (如果需要单独配置)
DS_KEY = settings.openai_api_key
DS_URL = settings.openai_base_url

# --- 模型预设 (Presets) ---

# 1. GPT-5.1 (通过 ChatAnywhere)
GPT5_CONFIG = LLMConfig(
    api_key=CA_KEY,
    base_url=CA_URL,
    model_name="gpt-5.1",
    temperature=0.7
)

# 2. DeepSeek V3 (通过 ChatAnywhere 或 官方)
DEEPSEEK_V3_CONFIG = LLMConfig(
    api_key=CA_KEY, # 假设也通过 ChatAnywhere 转发，或者改用 DS_KEY
    base_url=CA_URL,
    model_name="deepseek-v3-2-exp",
    temperature=0.7
)

# 3. Claude Haiku (通过 ChatAnywhere)
CLAUDE_HAIKU_CONFIG = LLMConfig(
    api_key=CA_KEY,
    base_url=CA_URL,
    model_name="claude-haiku-4-5-20251001",
    temperature=0.7
)

# 4. Gemini 2.5 Pro (通过 ChatAnywhere)
GEMINI_25_CONFIG = LLMConfig(
    api_key=CA_KEY,
    base_url=CA_URL,
    model_name="gemini-2.5-pro",
    temperature=0.7
)

# 5. Grok 4 (通过 ChatAnywhere)
GROK_4_CONFIG = LLMConfig(
    api_key=CA_KEY,
    base_url=CA_URL,
    model_name="grok-4",
    temperature=0.7
)

# 6. Qwen 3 (通过 ChatAnywhere)
QWEN_3_CONFIG = LLMConfig(
    api_key=CA_KEY,
    base_url=CA_URL,
    model_name="qwen3-235b-a22b",
    temperature=0.7
)

# --- Agent 绑定配置 ---
# 在这里为每个 Agent 分配具体的模型配置
# 你可以自由修改这里的映射关系

AGENT_LLM_CONFIGS = {
    # 整理员：任务相对简单，使用 DeepSeek V3
    "Case Organizer": DEEPSEEK_V3_CONFIG,
    
    # 主持人：需要极强的综合能力，使用 GPT-5.1
    "Moderator": GPT5_CONFIG,
    
    # 放射科：需要较强的推理能力，使用 Claude Haiku
    "Radiologist": CLAUDE_HAIKU_CONFIG,
    
    # 病理科：使用 Gemini 2.5 Pro
    "Pathologist": GEMINI_25_CONFIG,
    
    # 呼吸科：使用 Grok 4
    "Pulmonologist": GROK_4_CONFIG,
    
    # 风湿科：使用 Qwen 3
    "Rheumatologist": QWEN_3_CONFIG,
}

def get_config_for_agent(role_name: str) -> LLMConfig:
    """根据角色名获取 LLM 配置，默认返回 DeepSeek V3"""
    return AGENT_LLM_CONFIGS.get(role_name, DEEPSEEK_V3_CONFIG)

def create_config_from_model_name(model_name: str) -> LLMConfig:
    """根据模型名称创建配置对象"""
    # 检查是否是预设的模型名称，如果是，直接返回预设配置（可能包含特定的 Key/URL）
    presets = [GPT5_CONFIG, DEEPSEEK_V3_CONFIG, CLAUDE_HAIKU_CONFIG, GEMINI_25_CONFIG, GROK_4_CONFIG, QWEN_3_CONFIG]
    for preset in presets:
        if preset.model_name == model_name:
            return preset
            
    # 如果不是预设，则默认使用 ChatAnywhere 通道创建新配置
    return LLMConfig(
        api_key=CA_KEY,
        base_url=CA_URL,
        model_name=model_name,
        temperature=0.7
    )
