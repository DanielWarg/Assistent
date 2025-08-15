"""
Application settings using pydantic-settings.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    env: str = Field(default="dev", description="Environment (dev, staging, prod)")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Server
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_dir: str = Field(default="./logs", description="Log directory")
    log_format: str = Field(default="jsonl", description="Log format")
    log_buffer_max: int = Field(default=1000, description="Maximum log buffer size")
    log_buffer_policy: str = Field(default="drop_oldest", description="Buffer overflow policy")
    log_retention_days: int = Field(default=7, description="Log retention in days")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="CORS allowed origins (comma-separated)"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite:///./jarvis.db",
        description="Database connection URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # LLM
    ollama_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API URL"
    )
    ollama_model: str = Field(
        default="llama3.2:3b",
        description="Default Ollama model"
    )
    
    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT/sessions"
    )
    api_keys: str = Field(
        default="dev-api-key-change-in-production",
        description="Comma-separated API keys for authentication"
    )
    api_key_header: str = Field(
        default="X-API-Key",
        description="Header name for API key authentication"
    )
    
    # Performance
    max_workers: int = Field(default=4, description="Maximum worker processes")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env.lower() == "prod"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.env.lower() == "dev"
