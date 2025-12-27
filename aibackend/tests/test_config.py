"""
Unit tests for configuration management

Tests configuration loading with valid environment variables,
missing required variables, and default values.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import os
import pytest
from pydantic import ValidationError

from config.settings import Settings, get_settings, reset_settings


class TestConfigurationLoading:
    """Test suite for configuration loading"""
    
    def setup_method(self):
        """Reset settings before each test"""
        reset_settings()
        # Clear environment variables that might interfere
        env_vars = [
            "OPENAI_API_KEY",
            "TTS_API_KEY",
            "TTS_SERVICE",
            "GPT_MODEL",
            "SERVER_HOST",
            "SERVER_PORT",
            "LOG_LEVEL",
            "MAX_AUDIO_SIZE_MB",
            "SESSION_STORE_TYPE"
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up after each test"""
        reset_settings()
    
    def test_valid_environment_variables(self):
        """
        Test configuration loads successfully with all valid environment variables.
        
        Requirements: 8.1, 8.2, 8.4, 8.5
        """
        # Set required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Set optional environment variables
        os.environ["GPT_MODEL"] = "gpt-4o-mini"
        os.environ["SERVER_PORT"] = "9000"
        os.environ["SERVER_HOST"] = "127.0.0.1"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["MAX_AUDIO_SIZE_MB"] = "50"
        os.environ["TTS_SERVICE"] = "elevenlabs"
        os.environ["SESSION_STORE_TYPE"] = "redis"
        
        # Load settings
        settings = Settings()
        
        # Verify required variables are loaded
        assert settings.openai_api_key == "test-openai-key-123"
        assert settings.tts_api_key == "test-tts-key-456"
        
        # Verify optional variables are loaded
        assert settings.gpt_model == "gpt-4o-mini"
        assert settings.server_port == 9000
        assert settings.server_host == "127.0.0.1"
        assert settings.log_level == "DEBUG"
        assert settings.max_audio_size_mb == 50
        assert settings.tts_service == "elevenlabs"
        assert settings.session_store_type == "redis"
    
    def test_missing_openai_api_key(self):
        """
        Test that missing OPENAI_API_KEY causes configuration to fail.
        
        Requirements: 8.1, 8.3
        """
        # Set only TTS_API_KEY, missing OPENAI_API_KEY
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Attempt to load settings should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        # Verify error mentions the missing field
        error_str = str(exc_info.value)
        assert "openai_api_key" in error_str.lower()
    
    def test_missing_tts_api_key(self):
        """
        Test that missing TTS_API_KEY causes configuration to fail.
        
        Requirements: 8.2, 8.3
        """
        # Set only OPENAI_API_KEY, missing TTS_API_KEY
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        
        # Attempt to load settings should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        # Verify error mentions the missing field
        error_str = str(exc_info.value)
        assert "tts_api_key" in error_str.lower()
    
    def test_missing_all_required_variables(self):
        """
        Test that missing all required variables causes configuration to fail.
        
        Requirements: 8.1, 8.2, 8.3
        """
        # Don't set any environment variables
        
        # Attempt to load settings should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        # Verify error mentions required fields
        error_str = str(exc_info.value)
        assert "openai_api_key" in error_str.lower() or "tts_api_key" in error_str.lower()
    
    def test_default_values(self):
        """
        Test that optional configuration values use correct defaults.
        
        Requirements: 8.4, 8.5
        """
        # Set only required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Load settings
        settings = Settings()
        
        # Verify default values
        assert settings.gpt_model == "gpt-4o"
        assert settings.server_port == 8000
        assert settings.server_host == "0.0.0.0"
        assert settings.log_level == "INFO"
        assert settings.max_audio_size_mb == 25
        assert settings.tts_service == "openai"
        assert settings.session_store_type == "memory"
    
    def test_empty_api_key_validation(self):
        """
        Test that empty API keys are rejected.
        
        Requirements: 8.1, 8.2, 8.3
        """
        # Set empty OPENAI_API_KEY
        os.environ["OPENAI_API_KEY"] = "   "
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Attempt to load settings should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        # Verify error mentions validation
        error_str = str(exc_info.value)
        assert "empty" in error_str.lower() or "openai_api_key" in error_str.lower()
    
    def test_get_settings_singleton(self):
        """
        Test that get_settings() returns a singleton instance.
        
        Requirements: 8.1, 8.2
        """
        # Set required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Get settings twice
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Verify they are the same instance
        assert settings1 is settings2
    
    def test_get_settings_with_missing_variables(self):
        """
        Test that get_settings() raises descriptive error when variables are missing.
        
        Requirements: 8.3
        """
        # Don't set any environment variables
        
        # Attempt to get settings should raise ValueError with descriptive message
        with pytest.raises(ValueError) as exc_info:
            get_settings()
        
        # Verify error message is descriptive
        error_str = str(exc_info.value)
        assert "failed to load configuration" in error_str.lower()
        assert "environment variables" in error_str.lower()
    
    def test_reset_settings(self):
        """
        Test that reset_settings() clears the singleton instance.
        
        Requirements: 8.1, 8.2
        """
        # Set required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Get settings
        settings1 = get_settings()
        
        # Reset settings
        reset_settings()
        
        # Get settings again
        settings2 = get_settings()
        
        # Verify they are different instances
        assert settings1 is not settings2
    
    def test_max_audio_size_bytes_property(self):
        """
        Test that max_audio_size_bytes property correctly converts MB to bytes.
        
        Requirements: 8.5
        """
        # Set required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        os.environ["MAX_AUDIO_SIZE_MB"] = "10"
        
        # Load settings
        settings = Settings()
        
        # Verify conversion
        assert settings.max_audio_size_bytes == 10 * 1024 * 1024
    
    def test_server_port_validation(self):
        """
        Test that server port is validated to be within valid range.
        
        Requirements: 8.5
        """
        # Set required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Test invalid port (too high)
        os.environ["SERVER_PORT"] = "99999"
        
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        error_str = str(exc_info.value)
        assert "server_port" in error_str.lower() or "less than or equal" in error_str.lower()
    
    def test_case_insensitive_env_vars(self):
        """
        Test that environment variables are case-insensitive.
        
        Requirements: 8.1, 8.2
        """
        # Set environment variables with different cases
        os.environ["openai_api_key"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        
        # Load settings
        settings = Settings()
        
        # Verify both are loaded correctly
        assert settings.openai_api_key == "test-openai-key-123"
        assert settings.tts_api_key == "test-tts-key-456"
    
    def test_gpt_model_validation(self):
        """
        Test that GPT model name cannot be empty.
        
        Requirements: 8.4
        """
        # Set required environment variables
        os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
        os.environ["TTS_API_KEY"] = "test-tts-key-456"
        os.environ["GPT_MODEL"] = "   "
        
        # Attempt to load settings should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        error_str = str(exc_info.value)
        assert "gpt_model" in error_str.lower() or "empty" in error_str.lower()
