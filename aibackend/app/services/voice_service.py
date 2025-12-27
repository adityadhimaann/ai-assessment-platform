"""
Voice Service

This module provides text-to-speech functionality using either OpenAI TTS or ElevenLabs.
It converts feedback text to audio for voice feedback generation.
"""

import time
from typing import Optional, Literal, BinaryIO
from io import BytesIO
import requests
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError

from config.settings import Settings
from app.exceptions import TTSAPIError


class VoiceService:
    """
    Service for generating voice feedback from text.
    
    This service:
    - Converts text to speech using OpenAI TTS or ElevenLabs
    - Supports streaming for immediate playback
    - Handles API errors with retry logic
    - Returns audio data or URLs based on configuration
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the voice service.
        
        Args:
            settings: Application settings containing API keys and TTS configuration
        """
        self.settings = settings
        self.tts_service = settings.tts_service
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Initialize appropriate client based on TTS service
        if self.tts_service == "openai":
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        elif self.tts_service == "elevenlabs":
            self.elevenlabs_api_key = settings.tts_api_key
            self.elevenlabs_base_url = "https://api.elevenlabs.io/v1"
        else:
            raise ValueError(f"Unsupported TTS service: {self.tts_service}")
    
    def generate_voice_feedback(
        self,
        feedback_text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None
    ) -> bytes:
        """
        Generate voice feedback from text.
        
        Converts the provided feedback text to audio using the configured
        TTS service (OpenAI or ElevenLabs). Includes retry logic for
        transient failures.
        
        Args:
            feedback_text: The text to convert to speech
            voice: Optional voice ID/name (uses settings or service defaults if not provided)
            model: Optional model name (uses settings or service defaults if not provided)
        
        Returns:
            bytes: The audio data as bytes (MP3 format)
        
        Raises:
            TTSAPIError: If the TTS API call fails
        
        Requirements: 6.1, 6.2, 6.4, 6.5
        """
        if not feedback_text or not feedback_text.strip():
            raise TTSAPIError(
                message="Feedback text cannot be empty",
                service=self.tts_service
            )
        
        # Use voice from settings if available and not overridden
        if self.tts_service == "elevenlabs" and not voice:
            voice = self.settings.elevenlabs_voice_id
        
        # Use model from settings if available and not overridden
        if self.tts_service == "elevenlabs" and not model:
            model = self.settings.elevenlabs_model_id
        
        # Call appropriate TTS API based on configuration
        if self.tts_service == "openai":
            return self._call_openai_tts(feedback_text, voice, model)
        elif self.tts_service == "elevenlabs":
            return self._call_elevenlabs_tts(feedback_text, voice, model)
        else:
            raise TTSAPIError(
                message=f"Unsupported TTS service: {self.tts_service}",
                service=self.tts_service
            )
    
    def _call_openai_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None
    ) -> bytes:
        """
        Call OpenAI TTS API to generate audio.
        
        Args:
            text: The text to convert to speech
            voice: Voice to use (default: "alloy")
            model: Model to use (default: "tts-1")
        
        Returns:
            bytes: The audio data as bytes
        
        Raises:
            TTSAPIError: If the API call fails
        """
        # Set defaults
        voice = voice or "alloy"
        model = model or "tts-1"
        
        for attempt in range(self.max_retries):
            try:
                # Call OpenAI TTS API
                response = self.openai_client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                    response_format="mp3"
                )
                
                # Read audio data from response
                audio_data = response.read()
                
                if not audio_data:
                    raise TTSAPIError(
                        message="Received empty audio data from OpenAI TTS",
                        service="OpenAI TTS"
                    )
                
                return audio_data
            
            except RateLimitError as e:
                # Rate limit hit - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise TTSAPIError(
                        message="Rate limit exceeded after all retries",
                        service="OpenAI TTS",
                        original_error=e
                    )
            
            except APITimeoutError as e:
                # Timeout error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise TTSAPIError(
                        message="Request timeout after all retries",
                        service="OpenAI TTS",
                        original_error=e
                    )
            
            except APIConnectionError as e:
                # Connection error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise TTSAPIError(
                        message="Connection error after all retries",
                        service="OpenAI TTS",
                        original_error=e
                    )
            
            except APIError as e:
                # General API error - don't retry for client errors (4xx)
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    raise TTSAPIError(
                        message=f"API client error: {str(e)}",
                        service="OpenAI TTS",
                        original_error=e
                    )
                
                # Retry for server errors (5xx)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise TTSAPIError(
                        message=f"API error after all retries: {str(e)}",
                        service="OpenAI TTS",
                        original_error=e
                    )
            
            except Exception as e:
                # Unexpected error - don't retry
                raise TTSAPIError(
                    message=f"Unexpected error during TTS generation: {str(e)}",
                    service="OpenAI TTS",
                    original_error=e
                )
        
        # Should never reach here, but just in case
        raise TTSAPIError(
            message="Failed to generate audio after all retries",
            service="OpenAI TTS"
        )
    
    def _call_elevenlabs_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        model: Optional[str] = None
    ) -> bytes:
        """
        Call ElevenLabs TTS API to generate audio.
        
        Args:
            text: The text to convert to speech
            voice: Voice ID to use (default: "21m00Tcm4TlvDq8ikWAM" - Rachel)
            model: Model ID to use (default: "eleven_monolingual_v1")
        
        Returns:
            bytes: The audio data as bytes
        
        Raises:
            TTSAPIError: If the API call fails
        """
        # Set defaults
        voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        model_id = model or "eleven_monolingual_v1"
        
        # Build API endpoint
        url = f"{self.elevenlabs_base_url}/text-to-speech/{voice_id}"
        
        # Build headers
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        # Build request body
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                # Make API request
                response = requests.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=30
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise TTSAPIError(
                            message="Rate limit exceeded after all retries",
                            service="ElevenLabs"
                        )
                
                # Check for client errors (4xx)
                if 400 <= response.status_code < 500:
                    raise TTSAPIError(
                        message=f"API client error: {response.status_code} - {response.text}",
                        service="ElevenLabs"
                    )
                
                # Check for server errors (5xx) - retry
                if 500 <= response.status_code < 600:
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    else:
                        raise TTSAPIError(
                            message=f"API server error after all retries: {response.status_code}",
                            service="ElevenLabs"
                        )
                
                # Check for success
                if response.status_code != 200:
                    raise TTSAPIError(
                        message=f"Unexpected status code: {response.status_code}",
                        service="ElevenLabs"
                    )
                
                # Get audio data
                audio_data = response.content
                
                if not audio_data:
                    raise TTSAPIError(
                        message="Received empty audio data from ElevenLabs",
                        service="ElevenLabs"
                    )
                
                return audio_data
            
            except requests.exceptions.Timeout as e:
                # Timeout error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise TTSAPIError(
                        message="Request timeout after all retries",
                        service="ElevenLabs",
                        original_error=e
                    )
            
            except requests.exceptions.ConnectionError as e:
                # Connection error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise TTSAPIError(
                        message="Connection error after all retries",
                        service="ElevenLabs",
                        original_error=e
                    )
            
            except TTSAPIError:
                # Re-raise our own exceptions
                raise
            
            except Exception as e:
                # Unexpected error - don't retry
                raise TTSAPIError(
                    message=f"Unexpected error during TTS generation: {str(e)}",
                    service="ElevenLabs",
                    original_error=e
                )
        
        # Should never reach here, but just in case
        raise TTSAPIError(
            message="Failed to generate audio after all retries",
            service="ElevenLabs"
        )


def create_voice_service(settings: Settings) -> VoiceService:
    """
    Factory function to create a VoiceService instance.
    
    Args:
        settings: Application settings
    
    Returns:
        VoiceService: Configured voice service instance
    """
    return VoiceService(settings)
