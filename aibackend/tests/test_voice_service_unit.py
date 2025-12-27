"""
Unit tests for Voice Service with mocked TTS API

Tests successful audio generation, streaming support, and API error handling.

Requirements: 6.1, 6.4, 6.5
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError
import requests

from app.services.voice_service import VoiceService
from app.exceptions import TTSAPIError
from config.settings import Settings


@pytest.fixture
def mock_settings_openai():
    """Create mock settings for OpenAI TTS testing"""
    settings = Mock(spec=Settings)
    settings.openai_api_key = "test-openai-key-123"
    settings.tts_api_key = "test-tts-key-123"
    settings.tts_service = "openai"
    return settings


@pytest.fixture
def mock_settings_elevenlabs():
    """Create mock settings for ElevenLabs TTS testing"""
    settings = Mock(spec=Settings)
    settings.openai_api_key = "test-openai-key-123"
    settings.tts_api_key = "test-elevenlabs-key-123"
    settings.tts_service = "elevenlabs"
    return settings


@pytest.fixture
def voice_service_openai(mock_settings_openai):
    """Create voice service with mocked OpenAI client"""
    with patch('app.services.voice_service.OpenAI') as mock_openai:
        service = VoiceService(mock_settings_openai)
        service.retry_delay = 0.01  # Speed up tests
        return service


@pytest.fixture
def voice_service_elevenlabs(mock_settings_elevenlabs):
    """Create voice service for ElevenLabs"""
    service = VoiceService(mock_settings_elevenlabs)
    service.retry_delay = 0.01  # Speed up tests
    return service


class TestVoiceServiceSuccessfulGeneration:
    """Test suite for successful audio generation"""
    
    def test_successful_generation_openai_default_params(self, voice_service_openai):
        """
        Test successful audio generation with OpenAI TTS using default parameters.
        
        Requirements: 6.1
        """
        # Mock audio data
        mock_audio_data = b"fake_audio_data_mp3_content"
        
        # Mock the OpenAI TTS response
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        voice_service_openai.openai_client.audio.speech.create = Mock(return_value=mock_response)
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("This is test feedback text.")
        
        # Verify the result
        assert result == mock_audio_data
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Verify the API was called with correct parameters
        voice_service_openai.openai_client.audio.speech.create.assert_called_once()
        call_kwargs = voice_service_openai.openai_client.audio.speech.create.call_args.kwargs
        assert call_kwargs["model"] == "tts-1"
        assert call_kwargs["voice"] == "alloy"
        assert call_kwargs["input"] == "This is test feedback text."
        assert call_kwargs["response_format"] == "mp3"
    
    def test_successful_generation_openai_custom_voice(self, voice_service_openai):
        """
        Test successful audio generation with custom voice parameter.
        
        Requirements: 6.1
        """
        # Mock audio data
        mock_audio_data = b"fake_audio_data_with_custom_voice"
        
        # Mock the OpenAI TTS response
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        voice_service_openai.openai_client.audio.speech.create = Mock(return_value=mock_response)
        
        # Call generate_voice_feedback with custom voice
        result = voice_service_openai.generate_voice_feedback(
            "Test feedback",
            voice="nova"
        )
        
        # Verify the result
        assert result == mock_audio_data
        
        # Verify the API was called with custom voice
        call_kwargs = voice_service_openai.openai_client.audio.speech.create.call_args.kwargs
        assert call_kwargs["voice"] == "nova"
    
    def test_successful_generation_openai_custom_model(self, voice_service_openai):
        """
        Test successful audio generation with custom model parameter.
        
        Requirements: 6.1
        """
        # Mock audio data
        mock_audio_data = b"fake_audio_data_with_custom_model"
        
        # Mock the OpenAI TTS response
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        voice_service_openai.openai_client.audio.speech.create = Mock(return_value=mock_response)
        
        # Call generate_voice_feedback with custom model
        result = voice_service_openai.generate_voice_feedback(
            "Test feedback",
            model="tts-1-hd"
        )
        
        # Verify the result
        assert result == mock_audio_data
        
        # Verify the API was called with custom model
        call_kwargs = voice_service_openai.openai_client.audio.speech.create.call_args.kwargs
        assert call_kwargs["model"] == "tts-1-hd"
    
    def test_successful_generation_elevenlabs_default_params(self, voice_service_elevenlabs):
        """
        Test successful audio generation with ElevenLabs TTS using default parameters.
        
        Requirements: 6.1
        """
        # Mock audio data
        mock_audio_data = b"fake_elevenlabs_audio_data"
        
        # Mock the requests.post response
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = mock_audio_data
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback
            result = voice_service_elevenlabs.generate_voice_feedback("This is test feedback.")
            
            # Verify the result
            assert result == mock_audio_data
            assert isinstance(result, bytes)
            assert len(result) > 0
            
            # Verify the API was called
            mock_post.assert_called_once()
            
            # Verify the request parameters
            call_kwargs = mock_post.call_args.kwargs
            assert "elevenlabs.io" in call_kwargs.get("url", mock_post.call_args[0][0])
            assert call_kwargs["json"]["text"] == "This is test feedback."
            assert "xi-api-key" in call_kwargs["headers"]
    
    def test_successful_generation_elevenlabs_custom_voice(self, voice_service_elevenlabs):
        """
        Test successful audio generation with ElevenLabs using custom voice.
        
        Requirements: 6.1
        """
        # Mock audio data
        mock_audio_data = b"fake_elevenlabs_audio_custom_voice"
        
        # Mock the requests.post response
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = mock_audio_data
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback with custom voice
            result = voice_service_elevenlabs.generate_voice_feedback(
                "Test feedback",
                voice="custom_voice_id_123"
            )
            
            # Verify the result
            assert result == mock_audio_data
            
            # Verify the custom voice ID is in the URL
            url = mock_post.call_args.kwargs.get("url", mock_post.call_args[0][0])
            assert "custom_voice_id_123" in url


class TestVoiceServiceStreamingSupport:
    """Test suite for streaming support"""
    
    def test_openai_returns_audio_bytes_for_streaming(self, voice_service_openai):
        """
        Test that OpenAI TTS returns audio bytes that can be streamed.
        
        The audio data returned is in bytes format which can be streamed
        directly to the client for immediate playback.
        
        Requirements: 6.5
        """
        # Mock audio data
        mock_audio_data = b"streamable_audio_data_chunk"
        
        # Mock the OpenAI TTS response
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        voice_service_openai.openai_client.audio.speech.create = Mock(return_value=mock_response)
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("Streaming test")
        
        # Verify the result is bytes (streamable format)
        assert isinstance(result, bytes)
        assert result == mock_audio_data
        
        # Verify the audio can be chunked for streaming
        chunk_size = 1024
        chunks = [result[i:i+chunk_size] for i in range(0, len(result), chunk_size)]
        assert len(chunks) > 0
        assert b"".join(chunks) == mock_audio_data
    
    def test_elevenlabs_returns_audio_bytes_for_streaming(self, voice_service_elevenlabs):
        """
        Test that ElevenLabs TTS returns audio bytes that can be streamed.
        
        Requirements: 6.5
        """
        # Mock audio data
        mock_audio_data = b"elevenlabs_streamable_audio"
        
        # Mock the requests.post response
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = mock_audio_data
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback
            result = voice_service_elevenlabs.generate_voice_feedback("Streaming test")
            
            # Verify the result is bytes (streamable format)
            assert isinstance(result, bytes)
            assert result == mock_audio_data
    
    def test_audio_format_is_mp3_for_streaming(self, voice_service_openai):
        """
        Test that audio is generated in MP3 format which is suitable for streaming.
        
        Requirements: 6.5
        """
        # Mock audio data
        mock_audio_data = b"mp3_audio_data"
        
        # Mock the OpenAI TTS response
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        voice_service_openai.openai_client.audio.speech.create = Mock(return_value=mock_response)
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("MP3 format test")
        
        # Verify the API was called with MP3 format
        call_kwargs = voice_service_openai.openai_client.audio.speech.create.call_args.kwargs
        assert call_kwargs["response_format"] == "mp3"
        
        # Verify result is bytes (MP3 data)
        assert isinstance(result, bytes)


class TestVoiceServiceAPIErrorHandling:
    """Test suite for TTS API error handling"""
    
    def test_empty_feedback_text_error(self, voice_service_openai):
        """
        Test handling of empty feedback text.
        
        Requirements: 6.4
        """
        # Call generate_voice_feedback with empty text
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("")
        
        # Verify error details
        assert "empty" in str(exc_info.value).lower()
    
    def test_whitespace_only_feedback_text_error(self, voice_service_openai):
        """
        Test handling of whitespace-only feedback text.
        
        Requirements: 6.4
        """
        # Call generate_voice_feedback with whitespace-only text
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("   \n\t   ")
        
        # Verify error details
        assert "empty" in str(exc_info.value).lower()
    
    def test_openai_api_client_error_no_retry(self, voice_service_openai):
        """
        Test that OpenAI client errors (4xx) are not retried.
        
        Requirements: 6.4
        """
        # Mock a 400 error
        mock_request = Mock()
        error = APIError("Bad request", request=mock_request, body=None)
        error.status_code = 400
        
        voice_service_openai.openai_client.audio.speech.create = Mock(side_effect=error)
        
        # Call generate_voice_feedback and expect error
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify only called once (no retries)
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 1
        assert "client error" in str(exc_info.value).lower()
    
    def test_openai_api_server_error_with_retries(self, voice_service_openai):
        """
        Test that OpenAI server errors (5xx) are retried.
        
        Requirements: 6.4
        """
        # Mock a 500 error
        mock_request = Mock()
        error = APIError("Internal server error", request=mock_request, body=None)
        error.status_code = 500
        
        voice_service_openai.openai_client.audio.speech.create = Mock(side_effect=error)
        
        # Call generate_voice_feedback and expect error after retries
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify retried 3 times
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 3
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_openai_empty_audio_data_error(self, voice_service_openai):
        """
        Test handling of empty audio data from OpenAI TTS.
        
        Requirements: 6.4
        """
        # Mock empty audio response
        mock_response = Mock()
        mock_response.read.return_value = b""
        voice_service_openai.openai_client.audio.speech.create = Mock(return_value=mock_response)
        
        # Call generate_voice_feedback and expect error
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify error details
        assert "empty audio data" in str(exc_info.value).lower()
    
    def test_elevenlabs_client_error_no_retry(self, voice_service_elevenlabs):
        """
        Test that ElevenLabs client errors (4xx) are not retried.
        
        Requirements: 6.4
        """
        # Mock a 400 error
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.text = "Bad request"
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback and expect error
            with pytest.raises(TTSAPIError) as exc_info:
                voice_service_elevenlabs.generate_voice_feedback("Test feedback")
            
            # Verify only called once (no retries)
            assert mock_post.call_count == 1
            assert "client error" in str(exc_info.value).lower()
    
    def test_elevenlabs_server_error_with_retries(self, voice_service_elevenlabs):
        """
        Test that ElevenLabs server errors (5xx) are retried.
        
        Requirements: 6.4
        """
        # Mock a 500 error
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback and expect error after retries
            with pytest.raises(TTSAPIError) as exc_info:
                voice_service_elevenlabs.generate_voice_feedback("Test feedback")
            
            # Verify retried 3 times
            assert mock_post.call_count == 3
            assert "after all retries" in str(exc_info.value).lower()
    
    def test_elevenlabs_empty_audio_data_error(self, voice_service_elevenlabs):
        """
        Test handling of empty audio data from ElevenLabs.
        
        Requirements: 6.4
        """
        # Mock empty audio response
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b""
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback and expect error
            with pytest.raises(TTSAPIError) as exc_info:
                voice_service_elevenlabs.generate_voice_feedback("Test feedback")
            
            # Verify error details
            assert "empty audio data" in str(exc_info.value).lower()
    
    def test_unexpected_error_no_retry(self, voice_service_openai):
        """
        Test that unexpected errors are not retried.
        
        Requirements: 6.4
        """
        # Mock an unexpected error
        error = ValueError("Unexpected error")
        
        voice_service_openai.openai_client.audio.speech.create = Mock(side_effect=error)
        
        # Call generate_voice_feedback and expect error
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify only called once (no retries)
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 1
        assert "unexpected error" in str(exc_info.value).lower()


class TestVoiceServiceRetryLogic:
    """Test suite for retry logic with transient failures"""
    
    def test_rate_limit_retry_success_openai(self, voice_service_openai):
        """
        Test successful retry after rate limit error with OpenAI.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"success_after_retry"
        
        # Mock rate limit error on first call, success on second
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        
        voice_service_openai.openai_client.audio.speech.create = Mock(
            side_effect=[rate_limit_error, mock_response]
        )
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify success after retry
        assert result == mock_audio_data
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 2
    
    def test_rate_limit_retry_exhausted_openai(self, voice_service_openai):
        """
        Test that rate limit errors fail after max retries with OpenAI.
        
        Requirements: 6.4
        """
        # Mock rate limit error on all attempts
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        voice_service_openai.openai_client.audio.speech.create = Mock(side_effect=rate_limit_error)
        
        # Call generate_voice_feedback and expect error
        with pytest.raises(TTSAPIError) as exc_info:
            voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify retried 3 times
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 3
        assert "rate limit" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_connection_error_retry_success_openai(self, voice_service_openai):
        """
        Test successful retry after connection error with OpenAI.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"success_after_connection_retry"
        
        # Mock connection error on first call, success on second
        connection_error = APIConnectionError(request=Mock())
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        
        voice_service_openai.openai_client.audio.speech.create = Mock(
            side_effect=[connection_error, mock_response]
        )
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify success after retry
        assert result == mock_audio_data
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 2
    
    def test_timeout_error_retry_success_openai(self, voice_service_openai):
        """
        Test successful retry after timeout error with OpenAI.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"success_after_timeout_retry"
        
        # Mock timeout error on first call, success on second
        timeout_error = APITimeoutError(request=Mock())
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        
        voice_service_openai.openai_client.audio.speech.create = Mock(
            side_effect=[timeout_error, mock_response]
        )
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify success after retry
        assert result == mock_audio_data
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 2
    
    def test_rate_limit_retry_success_elevenlabs(self, voice_service_elevenlabs):
        """
        Test successful retry after rate limit error with ElevenLabs.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"elevenlabs_success_after_retry"
        
        # Mock rate limit error on first call, success on second
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_rate_limit_response = Mock()
            mock_rate_limit_response.status_code = 429
            
            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.content = mock_audio_data
            
            mock_post.side_effect = [mock_rate_limit_response, mock_success_response]
            
            # Call generate_voice_feedback
            result = voice_service_elevenlabs.generate_voice_feedback("Test feedback")
            
            # Verify success after retry
            assert result == mock_audio_data
            assert mock_post.call_count == 2
    
    def test_connection_error_retry_success_elevenlabs(self, voice_service_elevenlabs):
        """
        Test successful retry after connection error with ElevenLabs.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"elevenlabs_success_after_connection_retry"
        
        # Mock connection error on first call, success on second
        with patch('app.services.voice_service.requests.post') as mock_post:
            connection_error = requests.exceptions.ConnectionError("Connection failed")
            
            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.content = mock_audio_data
            
            mock_post.side_effect = [connection_error, mock_success_response]
            
            # Call generate_voice_feedback
            result = voice_service_elevenlabs.generate_voice_feedback("Test feedback")
            
            # Verify success after retry
            assert result == mock_audio_data
            assert mock_post.call_count == 2
    
    def test_timeout_error_retry_success_elevenlabs(self, voice_service_elevenlabs):
        """
        Test successful retry after timeout error with ElevenLabs.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"elevenlabs_success_after_timeout_retry"
        
        # Mock timeout error on first call, success on second
        with patch('app.services.voice_service.requests.post') as mock_post:
            timeout_error = requests.exceptions.Timeout("Request timeout")
            
            mock_success_response = Mock()
            mock_success_response.status_code = 200
            mock_success_response.content = mock_audio_data
            
            mock_post.side_effect = [timeout_error, mock_success_response]
            
            # Call generate_voice_feedback
            result = voice_service_elevenlabs.generate_voice_feedback("Test feedback")
            
            # Verify success after retry
            assert result == mock_audio_data
            assert mock_post.call_count == 2
    
    def test_exponential_backoff_openai(self, voice_service_openai):
        """
        Test that retry delays use exponential backoff with OpenAI.
        
        Requirements: 6.4
        """
        # Mock rate limit error on all attempts
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        voice_service_openai.openai_client.audio.speech.create = Mock(side_effect=rate_limit_error)
        
        # Patch time.sleep to track delays
        with patch('app.services.voice_service.time.sleep') as mock_sleep:
            try:
                voice_service_openai.generate_voice_feedback("Test feedback")
            except TTSAPIError:
                pass
            
            # Verify exponential backoff: 0.01, 0.02 (delays for first 2 retries)
            assert mock_sleep.call_count == 2
            delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert delays[0] == pytest.approx(0.01, rel=0.01)  # 0.01 * 2^0
            assert delays[1] == pytest.approx(0.02, rel=0.01)  # 0.01 * 2^1
    
    def test_exponential_backoff_elevenlabs(self, voice_service_elevenlabs):
        """
        Test that retry delays use exponential backoff with ElevenLabs.
        
        Requirements: 6.4
        """
        # Mock rate limit error on all attempts
        with patch('app.services.voice_service.requests.post') as mock_post:
            mock_rate_limit_response = Mock()
            mock_rate_limit_response.status_code = 429
            mock_post.return_value = mock_rate_limit_response
            
            # Patch time.sleep to track delays
            with patch('app.services.voice_service.time.sleep') as mock_sleep:
                try:
                    voice_service_elevenlabs.generate_voice_feedback("Test feedback")
                except TTSAPIError:
                    pass
                
                # Verify exponential backoff
                assert mock_sleep.call_count == 2
                delays = [call[0][0] for call in mock_sleep.call_args_list]
                assert delays[0] == pytest.approx(0.01, rel=0.01)
                assert delays[1] == pytest.approx(0.02, rel=0.01)
    
    def test_mixed_errors_retry_behavior(self, voice_service_openai):
        """
        Test retry behavior with mixed transient and permanent errors.
        
        Requirements: 6.4
        """
        # Mock audio data
        mock_audio_data = b"success_after_mixed_errors"
        
        # Mock: connection error, then rate limit, then success
        connection_error = APIConnectionError(request=Mock())
        rate_limit_error = RateLimitError("Rate limit", response=Mock(), body=None)
        mock_response = Mock()
        mock_response.read.return_value = mock_audio_data
        
        voice_service_openai.openai_client.audio.speech.create = Mock(
            side_effect=[connection_error, rate_limit_error, mock_response]
        )
        
        # Call generate_voice_feedback
        result = voice_service_openai.generate_voice_feedback("Test feedback")
        
        # Verify success after multiple retries
        assert result == mock_audio_data
        assert voice_service_openai.openai_client.audio.speech.create.call_count == 3


class TestVoiceServiceConfiguration:
    """Test suite for service configuration and initialization"""
    
    def test_unsupported_tts_service_error(self):
        """
        Test that unsupported TTS service raises error during initialization.
        
        Requirements: 6.4
        """
        # Create settings with unsupported TTS service
        settings = Mock(spec=Settings)
        settings.openai_api_key = "test-key"
        settings.tts_api_key = "test-key"
        settings.tts_service = "unsupported_service"
        
        # Attempt to create voice service and expect error
        with pytest.raises(ValueError) as exc_info:
            VoiceService(settings)
        
        # Verify error message
        assert "unsupported" in str(exc_info.value).lower()
    
    def test_openai_service_initialization(self, mock_settings_openai):
        """
        Test successful initialization with OpenAI TTS service.
        
        Requirements: 6.1
        """
        with patch('app.services.voice_service.OpenAI') as mock_openai:
            service = VoiceService(mock_settings_openai)
            
            # Verify service is initialized correctly
            assert service.tts_service == "openai"
            assert service.max_retries == 3
            assert service.retry_delay == 1.0
            
            # Verify OpenAI client was initialized
            mock_openai.assert_called_once_with(api_key="test-openai-key-123")
    
    def test_elevenlabs_service_initialization(self, mock_settings_elevenlabs):
        """
        Test successful initialization with ElevenLabs TTS service.
        
        Requirements: 6.1
        """
        service = VoiceService(mock_settings_elevenlabs)
        
        # Verify service is initialized correctly
        assert service.tts_service == "elevenlabs"
        assert service.max_retries == 3
        assert service.retry_delay == 1.0
        assert service.elevenlabs_api_key == "test-elevenlabs-key-123"
        assert "elevenlabs.io" in service.elevenlabs_base_url
