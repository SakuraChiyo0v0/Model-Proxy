from app.providers.base import BaseProvider
from app.providers.openai import OpenAIProvider
from app.providers.deepseek import DeepSeekProvider
from app.providers.doubao import DoubaoProvider


class ProviderRegistry:
    _registry: dict[str, BaseProvider] = {}

    @classmethod
    def register(cls, provider: BaseProvider):
        cls._registry[provider.name] = provider

    @classmethod
    def get(cls, name: str) -> BaseProvider | None:
        return cls._registry.get(name)

    @classmethod
    def get_all(cls) -> list[BaseProvider]:
        return list(cls._registry.values())


# 启动时自动注册内置 Provider
ProviderRegistry.register(OpenAIProvider())
ProviderRegistry.register(DeepSeekProvider())
ProviderRegistry.register(DoubaoProvider())
