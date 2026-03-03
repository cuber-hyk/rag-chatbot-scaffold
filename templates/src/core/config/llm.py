"""
LLM Configuration Management

Handles loading and creating LLM models based on provider configuration.
"""

from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from src.core.config.settings import get_settings


class LLMConfig:
    """LLM configuration manager"""

    def __init__(self):
        self.settings = get_settings()

    def _get_api_key(self) -> str:
        """Get API key for configured provider"""
        provider = self.settings.llm_provider
        provider_keys = {
            "openai": self.settings.openai_api_key,
            "anthropic": self.settings.anthropic_api_key,
            "azure": self.settings.azure_openai_api_key,
        }
        api_key = provider_keys.get(provider, "")
        if not api_key:
            raise ValueError(f"API key not found for provider '{provider}'. Please set the appropriate API key in .env file.")
        return api_key

    def _get_base_url(self) -> str:
        """Get base URL for configured provider"""
        provider = self.settings.llm_provider
        if provider == "openai":
            return self.settings.llm_base_url
        elif provider == "anthropic":
            return "https://api.anthropic.com"
        elif provider == "azure":
            return self.settings.azure_openai_endpoint
        return ""

    def get_chat_model(self):
        """Get configured chat model"""
        return init_chat_model(
            model=self.settings.llm_model,
            model_provider=self.settings.llm_provider,
            api_key=self._get_api_key(),
            base_url=self._get_base_url(),
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
        )

    def get_embedding_model(self) -> OpenAIEmbeddings:
        """Get configured embedding model"""
        return OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=self._get_api_key(),
            base_url=self.settings.embedding_base_url,
        )
