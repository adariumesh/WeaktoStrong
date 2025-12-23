"""
Production-ready configuration using Pydantic Settings
"""

import os
import secrets
from functools import lru_cache

from pydantic import Field, validator
from pydantic.networks import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables with validation"""

    # Environment
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")

    # Application
    app_name: str = Field("Weak-to-Strong Platform", env="APP_NAME")
    version: str = Field("1.0.0", env="VERSION")
    api_v1_str: str = Field("/api/v1", env="API_V1_STR")
    api_url: str = Field("http://localhost:8000", env="API_URL")
    data_dir: str = Field("./data", env="DATA_DIR")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_access_expire_minutes: int = Field(15, env="JWT_ACCESS_EXPIRE_MINUTES")
    jwt_refresh_expire_days: int = Field(7, env="JWT_REFRESH_EXPIRE_DAYS")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(0, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(30, env="DATABASE_POOL_TIMEOUT")

    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    redis_max_connections: int = Field(50, env="REDIS_MAX_CONNECTIONS")

    # CORS
    backend_cors_origins: list[AnyHttpUrl] = Field([], env="BACKEND_CORS_ORIGINS")

    # AI Services
    anthropic_api_key: str | None = Field(None, env="ANTHROPIC_API_KEY")
    claude_haiku_model: str = Field("claude-3-haiku-20240307", env="CLAUDE_HAIKU_MODEL")
    claude_sonnet_model: str = Field(
        "claude-3-5-sonnet-20241022", env="CLAUDE_SONNET_MODEL"
    )

    # Ollama
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field("llama3.2:8b", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(60, env="OLLAMA_TIMEOUT")

    # AI Configuration
    ai_default_timeout: int = Field(30, env="AI_DEFAULT_TIMEOUT")
    ai_max_tokens_per_request: int = Field(4000, env="AI_MAX_TOKENS_PER_REQUEST")
    ai_stream_chunk_size: int = Field(50, env="AI_STREAM_CHUNK_SIZE")

    # Anti-blind-prompting
    enable_prompt_validation: bool = Field(True, env="ENABLE_PROMPT_VALIDATION")
    min_prompt_length: int = Field(20, env="MIN_PROMPT_LENGTH")
    required_reasoning_patterns: str = Field(
        "because,approach,think,strategy,want to,trying to",
        env="REQUIRED_REASONING_PATTERNS",
    )

    # Rate Limiting
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, env="RATE_LIMIT_WINDOW")  # 1 hour

    # Token Usage Limits
    free_tier_daily_tokens: int = Field(10000, env="FREE_TIER_DAILY_TOKENS")
    pro_tier_daily_tokens: int = Field(100000, env="PRO_TIER_DAILY_TOKENS")
    team_tier_daily_tokens: int = Field(500000, env="TEAM_TIER_DAILY_TOKENS")
    enterprise_tier_daily_tokens: int = Field(
        -1, env="ENTERPRISE_TIER_DAILY_TOKENS"
    )  # Unlimited

    # Monitoring
    sentry_dsn: str | None = Field(None, env="SENTRY_DSN")
    enable_metrics: bool = Field(False, env="ENABLE_METRICS")
    metrics_port: int = Field(9090, env="METRICS_PORT")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")  # json or text

    # Docker/Sandbox Configuration
    docker_enabled: bool = Field(True, env="DOCKER_ENABLED")
    docker_timeout: int = Field(30, env="DOCKER_TIMEOUT")
    docker_memory_limit: str = Field("512m", env="DOCKER_MEMORY_LIMIT")
    docker_cpu_limit: str = Field("1", env="DOCKER_CPU_LIMIT")

    # Email Configuration (for notifications)
    smtp_host: str | None = Field(None, env="SMTP_HOST")
    smtp_port: int = Field(587, env="SMTP_PORT")
    smtp_username: str | None = Field(None, env="SMTP_USERNAME")
    smtp_password: str | None = Field(None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, env="SMTP_USE_TLS")

    # File Storage
    upload_max_size: int = Field(10 * 1024 * 1024, env="UPLOAD_MAX_SIZE")  # 10MB
    allowed_file_extensions: str = Field(
        "js,ts,jsx,tsx,py,html,css,json,md", env="ALLOWED_FILE_EXTENSIONS"
    )

    # Stripe Configuration
    stripe_publishable_key: str | None = Field(None, env="STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key: str | None = Field(None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str | None = Field(None, env="STRIPE_WEBHOOK_SECRET")
    stripe_success_url: str = Field(
        "http://localhost:3000/billing/success", env="STRIPE_SUCCESS_URL"
    )
    stripe_cancel_url: str = Field(
        "http://localhost:3000/billing/cancel", env="STRIPE_CANCEL_URL"
    )
    stripe_portal_return_url: str = Field(
        "http://localhost:3000/billing", env="STRIPE_PORTAL_RETURN_URL"
    )

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("secret_key", pre=True)
    def validate_secret_key(cls, v):
        if not v or v == "change-in-production":
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("SECRET_KEY must be set in production")
            return secrets.token_urlsafe(32)
        return v

    @validator("jwt_secret_key", pre=True)
    def validate_jwt_secret_key(cls, v):
        if not v or v == "change-in-production":
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("JWT_SECRET_KEY must be set in production")
            return secrets.token_urlsafe(32)
        return v

    @validator("database_url", pre=True)
    def validate_database_url(cls, v):
        if v.startswith("sqlite"):
            if os.getenv("ENVIRONMENT", "development") == "production":
                raise ValueError("SQLite is not supported in production")
        return v

    @property
    def reasoning_patterns(self) -> list[str]:
        """Get reasoning patterns as a list"""
        return [
            pattern.strip() for pattern in self.required_reasoning_patterns.split(",")
        ]

    @property
    def allowed_extensions(self) -> list[str]:
        """Get allowed file extensions as a list"""
        return [ext.strip() for ext in self.allowed_file_extensions.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment.lower() == "testing"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance (for backward compatibility)
settings = get_settings()
