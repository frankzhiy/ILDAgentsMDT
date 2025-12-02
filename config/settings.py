from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    项目配置类
    """
    # OpenAI / DeepSeek 配置
    # 从 .env 文件中读取 OPENAI_API_KEY，如果没有则报错或为 None
    openai_api_key: str 
    openai_base_url: str = "https://api.deepseek.com" # 默认使用 DeepSeek
    model_name: str = "deepseek-chat" # 默认模型

    # ChatAnywhere 配置 (可选)
    chatanywhere_api_key: Optional[str] = None
    chatanywhere_base_url: str = "https://api.chatanywhere.tech/v1"
    
    # 测试模式开关
    # True: 限制 max_tokens 以节省 Token
    # False: 正常回复
    # test_mode: bool = True 
    test_mode: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore" # 忽略多余的环境变量

settings = Settings()
