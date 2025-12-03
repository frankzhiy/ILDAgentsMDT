import openai
import json
import time
from typing import Dict, Any, Optional
from config.settings import settings
from config.llm_config import LLMConfig

class LLMClient:
    """
    大模型客户端封装类 (LLM Client Wrapper)
    
    该类旨在提供一个统一的接口来调用不同的大语言模型服务（如 OpenAI, DeepSeek, Claude 等）。
    它支持多 Provider 管理，能够根据传入的配置自动切换底层的 API Client。
    
    主要功能：
    1. 多客户端管理：根据 API Key 和 Base URL 缓存和复用 openai.OpenAI 实例。
    2. 统一调用接口：屏蔽不同模型在调用细节上的差异（目前主要基于 OpenAI 兼容接口）。
    3. 流式/非流式支持：统一封装了流式输出 (Stream) 和普通输出的处理逻辑。
    4. JSON 模式支持：便捷地开启 JSON Output Mode。
    5. 测试模式支持：在测试环境下限制 Token 消耗。
    """
    def __init__(self):
        """
        初始化 LLMClient。
        
        默认创建一个基于 settings 中配置的 OpenAI 客户端作为后备。
        初始化客户端缓存字典 `_clients`。
        """
        # 默认客户端 (兼容旧代码或未指定配置的情况)
        self.default_client = openai.OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        # 客户端缓存: {(api_key, base_url): client_instance}
        # 用于避免重复创建相同的客户端连接
        self._clients = {}

    def _get_client(self, config: LLMConfig = None) -> openai.OpenAI:
        """
        根据提供的配置获取或创建 OpenAI 客户端实例。
        
        :param config: LLMConfig 对象，包含 api_key 和 base_url。
        :return: openai.OpenAI 客户端实例。
        """
        if not config:
            return self.default_client
        
        key = (config.api_key, config.base_url)
        if key not in self._clients:
            self._clients[key] = openai.OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
        return self._clients[key]

    def get_completion(self, 
                       messages: list, 
                       model: str = None, 
                       temperature: float = 0.7,
                       json_mode: bool = False,
                       stream: bool = False,
                       stream_callback: callable = None,
                       config: LLMConfig = None) -> str:
        """
        获取模型回复的核心方法。
        
        :param messages: 对话列表，格式为 [{"role": "user", "content": "..."}]。
        :param model: (可选) 强制指定使用的模型名称。如果不传，则优先使用 config 中的 model_name，最后回退到 settings.model_name。
        :param temperature: (可选) 采样温度。如果不传，则优先使用 config 中的 temperature。
        :param json_mode: 是否强制模型输出 JSON 格式 (需要模型支持 json_object)。
        :param stream: 是否开启流式输出 (Streaming)。
        :param stream_callback: 流式输出时的回调函数，接收 chunk 字符串作为参数。
        :param config: (新增) LLMConfig 对象，指定本次调用使用的模型配置 (Key, URL, Model, Temp)。
        :return: 模型生成的完整文本内容。
        """
        # 1. 确定使用的配置参数 (Model & Temperature)
        target_model = model
        target_temp = temperature
        
        if config:
            # 如果提供了 config，优先使用 config 中的模型名（除非显式传入了 model 参数）
            target_model = model or config.model_name
            # 如果传入的 temperature 是默认值 0.7，则尝试使用 config 中的配置
            target_temp = temperature if temperature != 0.7 else config.temperature
        else:
            # 回退到全局设置
            target_model = model or settings.model_name

        # 2. 获取对应的 API Client
        client = self._get_client(config)
        
        # 3. 执行 API 调用
        try:
            response_format = {"type": "json_object"} if json_mode else None
            
            # 构造请求参数
            kwargs = {
                "model": target_model,
                "messages": messages,
                "temperature": target_temp,
                "response_format": response_format,
                "stream": stream
            }

            # --- 测试模式 (Test Mode) ---
            # 在测试模式下限制 max_tokens 以节省成本
            if settings.test_mode:
                kwargs["max_tokens"] = 256 
                print(f"[Test Mode] Max tokens limited to {kwargs['max_tokens']} for {target_model}")

            if stream:
                # 流式处理逻辑
                response_stream = client.chat.completions.create(**kwargs)
                full_content = ""
                for chunk in response_stream:
                    # 增加安全检查：确保 choices 列表不为空
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        # 检查 content 是否存在 (有些 chunk 可能只包含 finish_reason)
                        if delta.content is not None:
                            content_chunk = delta.content
                            full_content += content_chunk
                            if stream_callback:
                                stream_callback(content_chunk)
                return full_content
            else:
                # 非流式处理逻辑
                response = client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
        except InterruptedError:
            raise
        except Exception as e:
            return f"[Error] LLM 调用失败: {str(e)}"

llm_client = LLMClient()
