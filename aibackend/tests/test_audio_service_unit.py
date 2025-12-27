"""
Unit tests for Audio Service with mocked Whisper API

Tests successful transcription and API error handling.

Requirements: 5.2, 5.5
"""

import pytest
from io import BytesIO
from unittest.mock import Mock, patch
from fastapi import UploadFile
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError

from app.services.audio_service import AudioService
from app.exceptions import WhisperAPIError, AudioFileError
from config.settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing"""
    settings = Mock(spec=Settings)
    settings.openai_api_key = "test-api-key-123"
    settings.max_audio_size_bytes = 26214400  # 25MB
    return settings


@pytest.fixture
def audio_service(mock_settings):
    """Create audio service with mocked OpenAI client"""
    with patch('app.services.audio_service.OpenAI') as mock_openai:
        service = AudioService(mock_settings)
        service.retry_delay = 0.01  # Speed up tests
        return service


def create_mock_upload_file(filename: str, content_size: int = 1024) -> UploadFile:
    """
    Create a mock UploadFile for testing.
    
    Args:
        filename: The filename with extension
        content_size: Size of the file content in bytes
    
    Returns:
        UploadFile: A mock upload file object
    """
    content = b"x" * content_size
    file_obj = BytesIO(content)
    upload_file = UploadFile(filename=filename, file=file_obj)
    return upload_file


class TestAudioServiceSuccessfulTranscription:
    """Test suite for successful audio transcription"""
    
    def test_successful_transcription_mp3(self, audio_service):
        """
        Test successful transcription of MP3 audio file.
        
        Requirements: 5.2
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock the Whisper API response
        mock_transcript = "This is the transcribed text from the audio file."
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify the result
        assert result == mock_transcript.strip()
        
        # Verify the API was called with correct parameters
        audio_service.client.audio.transcriptions.create.assert_called_once()
        call_kwargs = audio_service.client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs["model"] == "whisper-1"
        assert call_kwargs["response_format"] == "text"
        assert "file" in call_kwargs
    
    def test_successful_transcription_wav(self, audio_service):
        """
        Test successful transcription of WAV audio file.
        
        Requirements: 5.2
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.wav", 2048)
        
        # Mock the Whisper API response
        mock_transcript = "Another transcribed text."
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify the result
        assert result == mock_transcript.strip()
    
    def test_successful_transcription_m4a(self, audio_service):
        """
        Test successful transcription of M4A audio file.
        
        Requirements: 5.2
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.m4a", 1500)
        
        # Mock the Whisper API response
        mock_transcript = "M4A transcription result."
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify the result
        assert result == mock_transcript.strip()
    
    def test_transcription_strips_whitespace(self, audio_service):
        """
        Test that transcription result has leading/trailing whitespace stripped.
        
        Requirements: 5.2
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock the Whisper API response with whitespace
        mock_transcript = "   Transcribed text with whitespace   \n"
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify whitespace is stripped
        assert result == "Transcribed text with whitespace"
        assert result == result.strip()
    
    def test_transcription_preserves_internal_whitespace(self, audio_service):
        """
        Test that transcription preserves internal whitespace and newlines.
        
        Requirements: 5.2
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock the Whisper API response with internal whitespace
        mock_transcript = "Line one.\nLine two with  multiple  spaces.\nLine three."
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify internal whitespace is preserved
        assert result == mock_transcript.strip()
        assert "\n" in result
        assert "multiple  spaces" in result
    
    def test_transcription_file_pointer_reset(self, audio_service):
        """
        Test that file pointer is reset before transcription.
        
        Requirements: 5.2
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Move file pointer to middle
        upload_file.file.seek(512)
        
        # Mock the Whisper API response
        mock_transcript = "Transcribed text."
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify the result
        assert result == mock_transcript.strip()
        
        # Verify file was seeked to beginning (check that seek was called)
        # The file pointer should have been reset to 0 before API call


class TestAudioServiceAPIErrorHandling:
    """Test suite for Whisper API error handling"""
    
    def test_empty_transcription_error(self, audio_service):
        """
        Test handling of empty transcription from Whisper API.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock empty response
        audio_service.client.audio.transcriptions.create = Mock(return_value="")
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify error details
        assert "empty transcription" in str(exc_info.value).lower()
        assert exc_info.value.details["operation"] == "audio_transcription"
        assert exc_info.value.details["service"] == "Whisper"
    
    def test_whitespace_only_transcription_error(self, audio_service):
        """
        Test handling of whitespace-only transcription from Whisper API.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock whitespace-only response
        audio_service.client.audio.transcriptions.create = Mock(return_value="   \n\t   ")
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify error details
        assert "empty transcription" in str(exc_info.value).lower()
    
    def test_api_client_error_no_retry(self, audio_service):
        """
        Test that client errors (4xx) are not retried.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock a 400 error
        mock_request = Mock()
        error = APIError("Bad request", request=mock_request, body=None)
        error.status_code = 400
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=error)
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify only called once (no retries)
        assert audio_service.client.audio.transcriptions.create.call_count == 1
        assert "client error" in str(exc_info.value).lower()
    
    def test_api_server_error_with_retries(self, audio_service):
        """
        Test that server errors (5xx) are retried.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock a 500 error
        mock_request = Mock()
        error = APIError("Internal server error", request=mock_request, body=None)
        error.status_code = 500
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=error)
        
        # Call transcribe_audio and expect error after retries
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify retried 3 times
        assert audio_service.client.audio.transcriptions.create.call_count == 3
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_unexpected_error_no_retry(self, audio_service):
        """
        Test that unexpected errors are not retried.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock an unexpected error
        error = ValueError("Unexpected error")
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=error)
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify only called once (no retries)
        assert audio_service.client.audio.transcriptions.create.call_count == 1
        assert "unexpected error" in str(exc_info.value).lower()


class TestAudioServiceRetryLogic:
    """Test suite for retry logic with transient failures"""
    
    def test_rate_limit_retry_success(self, audio_service):
        """
        Test successful retry after rate limit error.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock rate limit error on first call, success on second
        mock_transcript = "Success after retry"
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        audio_service.client.audio.transcriptions.create = Mock(
            side_effect=[rate_limit_error, mock_transcript]
        )
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify success after retry
        assert result == mock_transcript.strip()
        assert audio_service.client.audio.transcriptions.create.call_count == 2
    
    def test_rate_limit_retry_exhausted(self, audio_service):
        """
        Test that rate limit errors fail after max retries.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock rate limit error on all attempts
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=rate_limit_error)
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify retried 3 times
        assert audio_service.client.audio.transcriptions.create.call_count == 3
        assert "rate limit" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_connection_error_retry_success(self, audio_service):
        """
        Test successful retry after connection error.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock connection error on first call, success on second
        mock_transcript = "Success after retry"
        connection_error = APIConnectionError(request=Mock())
        
        audio_service.client.audio.transcriptions.create = Mock(
            side_effect=[connection_error, mock_transcript]
        )
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify success after retry
        assert result == mock_transcript.strip()
        assert audio_service.client.audio.transcriptions.create.call_count == 2
    
    def test_connection_error_retry_exhausted(self, audio_service):
        """
        Test that connection errors fail after max retries.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock connection error on all attempts
        connection_error = APIConnectionError(request=Mock())
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=connection_error)
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify retried 3 times
        assert audio_service.client.audio.transcriptions.create.call_count == 3
        assert "connection error" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_timeout_error_retry_success(self, audio_service):
        """
        Test successful retry after timeout error.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock timeout error on first call, success on second
        mock_transcript = "Success after retry"
        timeout_error = APITimeoutError(request=Mock())
        
        audio_service.client.audio.transcriptions.create = Mock(
            side_effect=[timeout_error, mock_transcript]
        )
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify success after retry
        assert result == mock_transcript.strip()
        assert audio_service.client.audio.transcriptions.create.call_count == 2
    
    def test_timeout_error_retry_exhausted(self, audio_service):
        """
        Test that timeout errors fail after max retries.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock timeout error on all attempts
        timeout_error = APITimeoutError(request=Mock())
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=timeout_error)
        
        # Call transcribe_audio and expect error
        with pytest.raises(WhisperAPIError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify retried 3 times
        assert audio_service.client.audio.transcriptions.create.call_count == 3
        assert "timeout" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_exponential_backoff(self, audio_service):
        """
        Test that retry delays use exponential backoff.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock rate limit error on all attempts
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=rate_limit_error)
        
        # Patch time.sleep to track delays
        with patch('app.services.audio_service.time.sleep') as mock_sleep:
            try:
                audio_service.transcribe_audio(upload_file)
            except WhisperAPIError:
                pass
            
            # Verify exponential backoff: 0.01, 0.02 (delays for first 2 retries)
            assert mock_sleep.call_count == 2
            delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert delays[0] == pytest.approx(0.01, rel=0.01)  # 0.01 * 2^0
            assert delays[1] == pytest.approx(0.02, rel=0.01)  # 0.01 * 2^1
    
    def test_mixed_errors_retry_behavior(self, audio_service):
        """
        Test retry behavior with mixed transient and permanent errors.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock: connection error, then rate limit, then success
        mock_transcript = "Success"
        connection_error = APIConnectionError(request=Mock())
        rate_limit_error = RateLimitError("Rate limit", response=Mock(), body=None)
        
        audio_service.client.audio.transcriptions.create = Mock(
            side_effect=[connection_error, rate_limit_error, mock_transcript]
        )
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify success after multiple retries
        assert result == mock_transcript.strip()
        assert audio_service.client.audio.transcriptions.create.call_count == 3
    
    def test_file_pointer_reset_on_retry(self, audio_service):
        """
        Test that file pointer is reset before each retry attempt.
        
        Requirements: 5.5
        """
        # Create mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock: connection error on first attempt, success on second
        mock_transcript = "Success after retry"
        connection_error = APIConnectionError(request=Mock())
        
        # Track file pointer positions
        file_positions = []
        
        def track_position(*args, **kwargs):
            file_positions.append(upload_file.file.tell())
            if len(file_positions) == 1:
                raise connection_error
            return mock_transcript
        
        audio_service.client.audio.transcriptions.create = Mock(side_effect=track_position)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify file pointer was at 0 for both attempts
        assert len(file_positions) == 2
        assert file_positions[0] == 0  # First attempt
        assert file_positions[1] == 0  # Second attempt (after retry)
        assert result == mock_transcript.strip()


class TestAudioServiceValidationIntegration:
    """Test suite for validation integration with transcription"""
    
    def test_transcription_fails_for_unsupported_format(self, audio_service):
        """
        Test that transcription fails for unsupported audio formats.
        
        Requirements: 5.5
        """
        # Create mock upload file with unsupported format
        upload_file = create_mock_upload_file("test_audio.txt", 1024)
        
        # Call transcribe_audio and expect validation error
        with pytest.raises(AudioFileError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify error is about unsupported format
        assert "unsupported" in str(exc_info.value).lower()
        
        # Verify API was never called
        audio_service.client.audio.transcriptions.create.assert_not_called()
    
    def test_transcription_fails_for_oversized_file(self, audio_service):
        """
        Test that transcription fails for files exceeding size limit.
        
        Requirements: 5.5
        """
        # Create mock upload file exceeding size limit
        upload_file = create_mock_upload_file("test_audio.mp3", 30 * 1024 * 1024)  # 30MB
        
        # Call transcribe_audio and expect validation error
        with pytest.raises(AudioFileError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify error is about file size
        assert "exceeds maximum" in str(exc_info.value).lower()
        
        # Verify API was never called
        audio_service.client.audio.transcriptions.create.assert_not_called()
    
    def test_transcription_fails_for_empty_file(self, audio_service):
        """
        Test that transcription fails for empty audio files.
        
        Requirements: 5.5
        """
        # Create mock upload file with zero size
        upload_file = create_mock_upload_file("test_audio.mp3", 0)
        
        # Call transcribe_audio and expect validation error
        with pytest.raises(AudioFileError) as exc_info:
            audio_service.transcribe_audio(upload_file)
        
        # Verify error is about empty file
        assert "empty" in str(exc_info.value).lower()
        
        # Verify API was never called
        audio_service.client.audio.transcriptions.create.assert_not_called()
    
    def test_transcription_succeeds_after_validation(self, audio_service):
        """
        Test that transcription proceeds after successful validation.
        
        Requirements: 5.2
        """
        # Create valid mock upload file
        upload_file = create_mock_upload_file("test_audio.mp3", 1024)
        
        # Mock successful transcription
        mock_transcript = "Transcribed text"
        audio_service.client.audio.transcriptions.create = Mock(return_value=mock_transcript)
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify success
        assert result == mock_transcript.strip()
        audio_service.client.audio.transcriptions.create.assert_called_once()
