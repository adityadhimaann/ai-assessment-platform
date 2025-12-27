"""
Audio Service

This module provides audio transcription functionality using OpenAI Whisper API.
It validates audio files and transcribes them to text.
"""

from typing import BinaryIO, Set
from fastapi import UploadFile
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
import time

from config.settings import Settings
from app.exceptions import WhisperAPIError, AudioFileError


class AudioService:
    """
    Service for transcribing audio files using Whisper API.
    
    This service:
    - Validates audio file formats and sizes
    - Transcribes audio to text using OpenAI Whisper
    - Handles API errors with retry logic
    """
    
    # Supported audio formats by Whisper API
    SUPPORTED_FORMATS: Set[str] = {
        "mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"
    }
    
    def __init__(self, settings: Settings):
        """
        Initialize the audio service.
        
        Args:
            settings: Application settings containing API key and configuration
        """
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    def transcribe_audio(self, audio_file: UploadFile) -> str:
        """
        Transcribe an audio file to text using Whisper API.
        
        This method validates the audio file format and size, then sends it
        to the Whisper API for transcription. Includes retry logic for
        transient failures.
        
        Args:
            audio_file: The uploaded audio file to transcribe
        
        Returns:
            str: The transcribed text from the audio
        
        Raises:
            AudioFileError: If the audio file is invalid (format or size)
            WhisperAPIError: If the Whisper API call fails
        
        Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.4
        """
        # Validate the audio file
        self._validate_audio_file(audio_file)
        
        # Transcribe with retry logic
        for attempt in range(self.max_retries):
            try:
                # Reset file pointer to beginning
                audio_file.file.seek(0)
                
                # Call Whisper API
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file.file,
                    response_format="text"
                )
                
                # Validate response
                if not transcript or not transcript.strip():
                    raise WhisperAPIError(
                        message="Received empty transcription from Whisper API"
                    )
                
                return transcript.strip()
            
            except RateLimitError as e:
                # Rate limit hit - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise WhisperAPIError(
                        message="Rate limit exceeded after all retries",
                        original_error=e
                    )
            
            except APITimeoutError as e:
                # Timeout error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise WhisperAPIError(
                        message="Request timeout after all retries",
                        original_error=e
                    )
            
            except APIConnectionError as e:
                # Connection error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise WhisperAPIError(
                        message="Connection error after all retries",
                        original_error=e
                    )
            
            except APIError as e:
                # General API error - don't retry for client errors (4xx)
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    raise WhisperAPIError(
                        message=f"API client error: {str(e)}",
                        original_error=e
                    )
                
                # Retry for server errors (5xx)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise WhisperAPIError(
                        message=f"API error after all retries: {str(e)}",
                        original_error=e
                    )
            
            except Exception as e:
                # Unexpected error - don't retry
                raise WhisperAPIError(
                    message=f"Unexpected error during transcription: {str(e)}",
                    original_error=e
                )
        
        # Should never reach here, but just in case
        raise WhisperAPIError(
            message="Failed to transcribe audio after all retries"
        )
    
    def _validate_audio_file(self, audio_file: UploadFile) -> None:
        """
        Validate audio file format and size.
        
        Checks that:
        1. File has a valid extension supported by Whisper API
        2. File size does not exceed the configured maximum
        
        Args:
            audio_file: The uploaded audio file to validate
        
        Raises:
            AudioFileError: If validation fails
        
        Requirements: 5.1, 5.4, 10.4
        """
        # Validate filename exists
        if not audio_file.filename:
            raise AudioFileError(
                message="Audio file must have a filename"
            )
        
        # Extract file extension
        filename_lower = audio_file.filename.lower()
        file_extension = None
        
        if "." in filename_lower:
            file_extension = filename_lower.rsplit(".", 1)[1]
        
        # Validate file format
        if not file_extension or file_extension not in self.SUPPORTED_FORMATS:
            supported_list = ", ".join(sorted(self.SUPPORTED_FORMATS))
            raise AudioFileError(
                message=f"Unsupported audio format. Supported formats: {supported_list}",
                filename=audio_file.filename
            )
        
        # Validate file size
        # Get current position, seek to end, get size, then reset position
        current_pos = audio_file.file.tell()
        audio_file.file.seek(0, 2)  # Seek to end
        file_size = audio_file.file.tell()
        audio_file.file.seek(current_pos)  # Reset to original position
        
        max_size = self.settings.max_audio_size_bytes
        
        if file_size > max_size:
            raise AudioFileError(
                message=f"Audio file size exceeds maximum allowed size",
                filename=audio_file.filename,
                file_size=file_size,
                max_size=max_size
            )
        
        # Additional validation: check if file is empty
        if file_size == 0:
            raise AudioFileError(
                message="Audio file is empty",
                filename=audio_file.filename,
                file_size=file_size
            )


def create_audio_service(settings: Settings) -> AudioService:
    """
    Factory function to create an AudioService instance.
    
    Args:
        settings: Application settings
    
    Returns:
        AudioService: Configured audio service instance
    """
    return AudioService(settings)
