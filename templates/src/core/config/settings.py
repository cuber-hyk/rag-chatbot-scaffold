"""
Application Settings

Configuration File Structure:
- config/application.yaml  → Application settings (ports, CORS, features)
- config/providers.yaml     → Provider selection and connections
- config/prompts.yaml       → System prompts
- .env                      → API keys and secrets (never commit to git)

Environment Variables Priority:
1. .env file (for API keys only)
2. YAML files (for application config)
3. Default values
"""

from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import yaml
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with clear separation of concerns"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==================== Project ====================
    project_name: str = Field(default="my-rag-chatbot")
    project_description: str = Field(default="A RAG-based chatbot")
    version: str = Field(default="0.1.0")
    environment: str = Field(default="development")

    # ==================== API Server ====================
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_version_prefix: str = Field(default="v1")

    # CORS
    cors_enabled: bool = Field(default=True)
    cors_origins: List[str] = Field(default=["http://localhost:5173"])

    # ==================== LLM Provider ====================
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4o")
    llm_temperature: float = Field(default=0.7)
    llm_max_tokens: int = Field(default=2048)

    # LLM Base URL (can be overridden for OpenAI-compatible APIs)
    # For SiliconCloud: https://api.siliconflow.cn/v1
    # For Moonshot: https://api.moonshot.cn/v1
    # For OpenAI: https://api.openai.com/v1
    llm_base_url: str = Field(default="https://api.openai.com/v1")

    # Azure-specific settings
    azure_openai_endpoint: str = Field(default="")
    azure_openai_deployment: str = Field(default="")

    # LLM API Keys (from .env ONLY)
    # For OpenAI-compatible providers (SiliconCloud, Moonshot): use OPENAI_API_KEY
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    azure_openai_api_key: str = Field(default="")

    # Embedding
    embedding_provider: str = Field(default="openai")
    embedding_model: str = Field(default="text-embedding-3-small")

    # Embedding Base URL
    embedding_base_url: str = Field(default="https://api.openai.com/v1")

    # ==================== Vector Database ====================
    vector_db_provider: str = Field(default="weaviate")
    vector_db_collection: str = Field(default="documents")

    # Vector DB URLs (from config)
    qdrant_url: str = Field(default="http://localhost:6333")
    weaviate_url: str = Field(default="http://localhost:8080")
    pinecone_cloud: str = Field(default="aws")
    pinecone_region: str = Field(default="us-east-1")

    # Vector DB API Keys (from .env ONLY)
    qdrant_api_key: str = Field(default="")
    weaviate_api_key: str = Field(default="")
    pinecone_api_key: str = Field(default="")

    # ==================== Search ====================
    search_provider: str = Field(default="duckduckgo")
    search_max_results: int = Field(default=5)
    tavily_api_key: str = Field(default="")

    # ==================== Session ====================
    session_storage: str = Field(default="redis")
    session_ttl: int = Field(default=300)
    redis_url: str = Field(default="redis://localhost:6379")

    # ==================== Documents ====================
    document_formats: List[str] = Field(
        default=["pdf", "markdown", "word", "text"]
    )
    max_file_size_mb: int = Field(default=10)
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)

    # ==================== Logging ====================
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="text")

    # ==================== Features ====================
    websocket_enabled: bool = Field(default=False)
    streaming_enabled: bool = Field(default=True)

    # ==================== Authentication ====================
    # From .env ONLY
    api_key: str = Field(default="")

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider"""
        valid = ["openai", "anthropic", "azure"]
        if v not in valid:
            raise ValueError(f"Invalid llm_provider: {v}. Must be one of {valid}")
        return v

    @field_validator("vector_db_provider")
    @classmethod
    def validate_vector_db_provider(cls, v: str) -> str:
        """Validate vector database provider"""
        valid = ["weaviate", "qdrant", "pinecone"]
        if v not in valid:
            raise ValueError(f"Invalid vector_db_provider: {v}. Must be one of {valid}")
        return v

    @field_validator("search_provider")
    @classmethod
    def validate_search_provider(cls, v: str) -> str:
        """Validate search provider"""
        valid = ["duckduckgo", "tavily"]
        if v not in valid:
            raise ValueError(f"Invalid search_provider: {v}. Must be one of {valid}")
        return v


# Fields that should ONLY come from .env (never from YAML)
_ENV_ONLY_FIELDS = {
    "openai_api_key",
    "anthropic_api_key",
    "azure_openai_api_key",
    "qdrant_api_key",
    "weaviate_api_key",
    "pinecone_api_key",
    "tavily_api_key",
    "api_key",
    "redis_url",
}


# Global instances
_settings: Optional[Settings] = None
_prompts: Dict[str, str] = {}


def _load_yaml_file(config_path: Path) -> Dict[str, Any]:
    """Load a YAML file and return as dict"""
    if not config_path.exists():
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _flatten_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten nested config dict for Settings"""
    flat = {}

    # Handle nested structures
    if "project" in config:
        flat.update({f"project_{k}": v for k, v in config["project"].items()})
    if "api" in config:
        if "cors" in config["api"]:
            flat["cors_enabled"] = config["api"]["cors"].get("enabled", True)
            flat["cors_origins"] = config["api"]["cors"].get("origins", ["http://localhost:5173"])
        flat.update({k: v for k, v in config["api"].items() if k != "cors"})
    if "session" in config:
        flat["session_storage"] = config["session"].get("storage", "redis")
        flat["session_ttl"] = config["session"].get("ttl", 300)
    if "documents" in config:
        flat["document_formats"] = config["documents"].get("formats", ["pdf", "markdown", "word", "text"])
        flat["max_file_size_mb"] = config["documents"].get("max_file_size_mb", 10)
        flat["chunk_size"] = config["documents"].get("chunk_size", 1000)
        flat["chunk_overlap"] = config["documents"].get("chunk_overlap", 200)
    if "logging" in config:
        flat["log_level"] = config["logging"].get("level", "INFO")
        flat["log_format"] = config["logging"].get("format", "text")
    if "features" in config:
        flat["websocket_enabled"] = config["features"].get("websocket", False)
        flat["streaming_enabled"] = config["features"].get("streaming", True)

    return flat


def _flatten_providers_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten providers.yaml config"""
    flat = {}

    if "llm" in config:
        flat["llm_provider"] = config["llm"].get("provider", "openai")
        flat["llm_model"] = config["llm"].get("model", "gpt-4o")
        flat["llm_temperature"] = config["llm"].get("temperature", 0.7)
        flat["llm_max_tokens"] = config["llm"].get("max_tokens", 2048)

        # Base URL - can be overridden for OpenAI-compatible APIs
        flat["llm_base_url"] = config["llm"].get("base_url", "https://api.openai.com/v1")

        # Azure-specific
        flat["azure_openai_endpoint"] = config["llm"].get("azure_endpoint", "")
        flat["azure_openai_deployment"] = config["llm"].get("azure_deployment", "")

    if "embedding" in config:
        flat["embedding_provider"] = config["embedding"].get("provider", "openai")
        flat["embedding_model"] = config["embedding"].get("model", "text-embedding-3-small")
        flat["embedding_base_url"] = config["embedding"].get("base_url", "https://api.openai.com/v1")

    if "vector_db" in config:
        flat["vector_db_provider"] = config["vector_db"].get("provider", "weaviate")
        flat["vector_db_collection"] = config["vector_db"].get("collection", "documents")
        if "connections" in config["vector_db"]:
            if "qdrant" in config["vector_db"]["connections"]:
                flat["qdrant_url"] = config["vector_db"]["connections"]["qdrant"].get("url", "http://localhost:6333")
            if "weaviate" in config["vector_db"]["connections"]:
                flat["weaviate_url"] = config["vector_db"]["connections"]["weaviate"].get("url", "http://localhost:8080")
            if "pinecone" in config["vector_db"]["connections"]:
                flat["pinecone_cloud"] = config["vector_db"]["connections"]["pinecone"].get("cloud", "aws")
                flat["pinecone_region"] = config["vector_db"]["connections"]["pinecone"].get("region", "us-east-1")

    if "search" in config:
        flat["search_provider"] = config["search"].get("provider", "duckduckgo")
        flat["search_max_results"] = config["search"].get("max_results", 5)

    return flat


def get_settings() -> Settings:
    """
    Get or create settings instance

    Loading order:
    1. config/application.yaml - Application settings
    2. config/providers.yaml - Provider configuration
    3. .env - API keys and secrets
    4. Default values
    """
    global _settings
    if _settings is None:
        # Load application config
        app_config = _load_yaml_file(Path("config/application.yaml"))
        app_flat = _flatten_config(app_config)

        # Load providers config
        providers_config = _load_yaml_file(Path("config/providers.yaml"))
        providers_flat = _flatten_providers_config(providers_config)

        # Merge configs
        config_dict = {**app_flat, **providers_flat}

        # Remove API key fields to ensure they only come from .env
        for field in _ENV_ONLY_FIELDS:
            config_dict.pop(field, None)

        # Create settings - API keys loaded from .env by Pydantic
        _settings = Settings(**config_dict)

    return _settings


def get_prompts() -> Dict[str, str]:
    """Load prompts from config/prompts.yaml"""
    global _prompts
    if not _prompts:
        prompt_config = _load_yaml_file(Path("config/prompts.yaml"))
        _prompts = prompt_config.get("prompts", {})
    return _prompts


def reset_settings():
    """Reset settings (mainly for testing)"""
    global _settings, _prompts
    _settings = None
    _prompts = {}
