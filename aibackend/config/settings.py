"""
Configuration Management

This module handles all application configuration using Pydantic Settings.
Environment variables are loaded from .env file or system environment.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional

# Load .env file explicitly
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All required settings must be provided via environment variables.
    Optional settings have default values.
    """
    
    # OpenAI Configuration (Required)
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for GPT-4o and Whisper API"
    )
    
    # TTS Service Configuration (Required)
    tts_api_key: str = Field(
        ...,
        description="API key for Text-to-Speech service (ElevenLabs or OpenAI)"
    )
    
    tts_service: Literal["openai", "elevenlabs"] = Field(
        default="openai",
        description="TTS service to use (openai or elevenlabs)"
    )
    
    # ElevenLabs Voice Configuration (Optional)
    elevenlabs_voice_id: Optional[str] = Field(
        default=None,
        description="ElevenLabs voice ID to use (e.g., for custom voices like 'Devi')"
    )
    
    elevenlabs_model_id: Optional[str] = Field(
        default="eleven_monolingual_v1",
        description="ElevenLabs model ID to use"
    )
    
    # Development Mode (Optional)
    dev_mode: bool = Field(
        default=False,
        description="Enable development mode with mock responses"
    )
    
    # Model Configuration (Optional with defaults)
    gpt_model: str = Field(
        default="gpt-4o",
        description="OpenAI model to use for evaluation and question generation"
    )
    
    # Server Configuration (Optional with defaults)
    server_host: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    
    server_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port number"
    )
    
    # Logging Configuration (Optional with defaults)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Audio Configuration (Optional with defaults)
    max_audio_size_mb: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Maximum audio file size in megabytes"
    )
    
    # Session Storage Configuration (Optional with defaults)
    session_store_type: Literal["memory", "redis", "database"] = Field(
        default="memory",
        description="Session storage backend type"
    )
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @field_validator("openai_api_key", "tts_api_key")
    @classmethod
    def validate_api_keys(cls, v: str, info) -> str:
        """Validate that API keys are not empty"""
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v.strip()
    
    @field_validator("gpt_model")
    @classmethod
    def validate_gpt_model(cls, v: str) -> str:
        """Validate GPT model name"""
        if not v or not v.strip():
            raise ValueError("gpt_model cannot be empty")
        return v.strip()
    
    @property
    def max_audio_size_bytes(self) -> int:
        """Convert max audio size from MB to bytes"""
        return self.max_audio_size_mb * 1024 * 1024


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Creates the settings instance on first call and validates all required
    environment variables are present.
    
    Returns:
        Settings: The application settings
        
    Raises:
        ValueError: If required environment variables are missing
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            raise ValueError(
                f"Failed to load configuration. Please ensure all required "
                f"environment variables are set. Error: {str(e)}"
            ) from e
    return _settings


def reset_settings() -> None:
    """
    Reset the global settings instance.
    
    This is primarily used for testing to reload settings with different
    environment variables.
    """
    global _settings
    _settings = None
