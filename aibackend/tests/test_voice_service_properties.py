"""
Property-based tests for voice service

Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response

This module tests that the voice service properly generates voice feedback from text,
returning valid audio data for all successful TTS API calls.

Validates: Requirements 6.2
"""

from io import BytesIO
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch, MagicMock
import pytest

from app.services.voice_service import VoiceService
from app.exceptions import TTSAPIError
from config.settings import Settings


# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Strategy for generating feedback text (non-empty strings)
feedback_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "P", "Z"),
        min_codepoint=32,
        max_codepoint=126
    ),
    min_size=1,
    max_size=500
).filter(lambda x: x.strip())  # Ensure non-empty after stripping

# Strategy for generating audio data (non-empty bytes)
audio_data = st.binary(min_size=100, max_size=10000)

# Strategy for TTS service type
tts_service_type = st.sampled_from(["openai", "elevenlabs"])


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_settings(tts_service: str = "openai") -> Settings:
    """
    Create test settings with mock API keys.
    
    Args:
        tts_service: TTS service to use ("openai" or "elevenlabs")
    
    Returns:
        Settings: Test settings instance
    """
    import os
    # Set required environment variables for testing
    os.environ["OPENAI_API_KEY"] = "test-openai-key-123"
    os.environ["TTS_API_KEY"] = "test-tts-key-123"
    os.environ["TTS_SERVICE"] = tts_service
    
    return Settings()


# ============================================================================
# Property Test for Voice Feedback Response
# ============================================================================

@settings(max_examples=50)
@given(
    feedback_text=feedback_text,
    audio_data=audio_data
)
def test_voice_feedback_generation_returns_valid_response_openai(feedback_text, audio_data):
    """
    Property 15: Voice feedback generation returns valid response (OpenAI TTS)
    
    For any successful OpenAI TTS generation with non-empty feedback text,
    the response should contain valid audio data (non-empty bytes).
    
    This property verifies that the voice service correctly generates audio
    from text using OpenAI TTS and returns the audio data without modification.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for OpenAI TTS
    test_settings = create_test_settings(tts_service="openai")
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Mock the OpenAI client's TTS method
    with patch.object(voice_service.openai_client.audio.speech, 'create') as mock_create:
        # Create a mock response object that has a read() method
        mock_response = Mock()
        mock_response.read.return_value = audio_data
        mock_create.return_value = mock_response
        
        # Call generate_voice_feedback
        result = voice_service.generate_voice_feedback(feedback_text)
        
        # Verify that the result is valid audio data (non-empty bytes)
        assert isinstance(result, bytes), (
            f"Voice feedback should return bytes, got {type(result)}"
        )
        assert len(result) > 0, "Voice feedback should return non-empty audio data"
        assert result == audio_data, (
            f"Voice feedback should return the audio data from TTS API.\n"
            f"Expected: {len(audio_data)} bytes\n"
            f"Got: {len(result)} bytes"
        )
        
        # Verify that the OpenAI API was called with correct parameters
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args.kwargs
        
        # Verify model parameter
        assert call_kwargs.get("model") in ["tts-1", "tts-1-hd"]
        
        # Verify voice parameter
        assert call_kwargs.get("voice") in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        # Verify input text
        assert call_kwargs.get("input") == feedback_text
        
        # Verify response format
        assert call_kwargs.get("response_format") == "mp3"


@settings(max_examples=50)
@given(
    feedback_text=feedback_text,
    audio_data=audio_data
)
def test_voice_feedback_generation_returns_valid_response_elevenlabs(feedback_text, audio_data):
    """
    Property 15: Voice feedback generation returns valid response (ElevenLabs)
    
    For any successful ElevenLabs TTS generation with non-empty feedback text,
    the response should contain valid audio data (non-empty bytes).
    
    This property verifies that the voice service correctly generates audio
    from text using ElevenLabs and returns the audio data without modification.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for ElevenLabs
    test_settings = create_test_settings(tts_service="elevenlabs")
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Mock the requests.post method for ElevenLabs API
    with patch('app.services.voice_service.requests.post') as mock_post:
        # Create a mock response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = audio_data
        mock_post.return_value = mock_response
        
        # Call generate_voice_feedback
        result = voice_service.generate_voice_feedback(feedback_text)
        
        # Verify that the result is valid audio data (non-empty bytes)
        assert isinstance(result, bytes), (
            f"Voice feedback should return bytes, got {type(result)}"
        )
        assert len(result) > 0, "Voice feedback should return non-empty audio data"
        assert result == audio_data, (
            f"Voice feedback should return the audio data from TTS API.\n"
            f"Expected: {len(audio_data)} bytes\n"
            f"Got: {len(result)} bytes"
        )
        
        # Verify that the ElevenLabs API was called
        mock_post.assert_called_once()
        
        # Verify the API endpoint
        call_args = mock_post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url')
        assert "elevenlabs.io" in url
        assert "text-to-speech" in url
        
        # Verify the request body contains the text
        json_data = call_args.kwargs.get('json')
        assert json_data is not None
        assert json_data.get('text') == feedback_text


@settings(max_examples=50)
@given(
    feedback_text=feedback_text,
    audio_data=audio_data,
    tts_service=tts_service_type
)
def test_voice_feedback_generation_returns_non_empty_audio(feedback_text, audio_data, tts_service):
    """
    Property 15 (variant): Voice feedback generation always returns non-empty audio
    
    For any successful TTS generation (OpenAI or ElevenLabs), the response
    should always contain non-empty audio data, regardless of the TTS service used.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for the specified TTS service
    test_settings = create_test_settings(tts_service=tts_service)
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Mock the appropriate TTS API based on service type
    if tts_service == "openai":
        with patch.object(voice_service.openai_client.audio.speech, 'create') as mock_create:
            # Create a mock response object
            mock_response = Mock()
            mock_response.read.return_value = audio_data
            mock_create.return_value = mock_response
            
            # Call generate_voice_feedback
            result = voice_service.generate_voice_feedback(feedback_text)
    else:  # elevenlabs
        with patch('app.services.voice_service.requests.post') as mock_post:
            # Create a mock response object
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = audio_data
            mock_post.return_value = mock_response
            
            # Call generate_voice_feedback
            result = voice_service.generate_voice_feedback(feedback_text)
    
    # Verify that the result is non-empty audio data
    assert isinstance(result, bytes), "Voice feedback should return bytes"
    assert len(result) > 0, "Voice feedback should return non-empty audio data"
    
    # Verify that the audio data is substantial (at least 100 bytes)
    assert len(result) >= 100, (
        f"Voice feedback should return substantial audio data (at least 100 bytes), "
        f"got {len(result)} bytes"
    )


@settings(max_examples=50)
@given(
    feedback_text=feedback_text,
    audio_data=audio_data
)
def test_voice_feedback_preserves_audio_data_integrity(feedback_text, audio_data):
    """
    Property 15 (variant): Voice feedback preserves audio data integrity
    
    For any successful TTS generation, the audio data returned should be
    exactly the same as the audio data received from the TTS API, with
    no modifications or corruption.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for OpenAI TTS
    test_settings = create_test_settings(tts_service="openai")
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Mock the OpenAI client's TTS method
    with patch.object(voice_service.openai_client.audio.speech, 'create') as mock_create:
        # Create a mock response object
        mock_response = Mock()
        mock_response.read.return_value = audio_data
        mock_create.return_value = mock_response
        
        # Call generate_voice_feedback
        result = voice_service.generate_voice_feedback(feedback_text)
        
        # Verify that the audio data is preserved exactly
        assert result == audio_data, (
            "Voice feedback should preserve audio data integrity without modification"
        )
        
        # Verify byte-for-byte equality
        assert len(result) == len(audio_data), (
            f"Audio data length should be preserved. "
            f"Expected: {len(audio_data)}, Got: {len(result)}"
        )
        
        # Verify that the bytes are identical
        for i, (expected_byte, actual_byte) in enumerate(zip(audio_data, result)):
            assert expected_byte == actual_byte, (
                f"Audio data byte mismatch at position {i}. "
                f"Expected: {expected_byte}, Got: {actual_byte}"
            )


@settings(max_examples=50)
@given(
    feedback_text=feedback_text,
    audio_data=audio_data,
    voice=st.sampled_from(["alloy", "echo", "fable", "onyx", "nova", "shimmer", None]),
    model=st.sampled_from(["tts-1", "tts-1-hd", None])
)
def test_voice_feedback_accepts_optional_parameters(feedback_text, audio_data, voice, model):
    """
    Property 15 (variant): Voice feedback accepts optional voice and model parameters
    
    For any successful TTS generation with optional voice and model parameters,
    the response should contain valid audio data, and the parameters should be
    passed correctly to the TTS API.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for OpenAI TTS
    test_settings = create_test_settings(tts_service="openai")
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Mock the OpenAI client's TTS method
    with patch.object(voice_service.openai_client.audio.speech, 'create') as mock_create:
        # Create a mock response object
        mock_response = Mock()
        mock_response.read.return_value = audio_data
        mock_create.return_value = mock_response
        
        # Call generate_voice_feedback with optional parameters
        result = voice_service.generate_voice_feedback(
            feedback_text,
            voice=voice,
            model=model
        )
        
        # Verify that the result is valid audio data
        assert isinstance(result, bytes), "Voice feedback should return bytes"
        assert len(result) > 0, "Voice feedback should return non-empty audio data"
        assert result == audio_data, "Voice feedback should return the audio data from TTS API"
        
        # Verify that the OpenAI API was called with correct parameters
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args.kwargs
        
        # Verify voice parameter (should use provided value or default)
        expected_voice = voice if voice is not None else "alloy"
        assert call_kwargs.get("voice") == expected_voice
        
        # Verify model parameter (should use provided value or default)
        expected_model = model if model is not None else "tts-1"
        assert call_kwargs.get("model") == expected_model


@settings(max_examples=50)
@given(
    # Generate various types of whitespace-only or empty strings
    invalid_text=st.one_of(
        st.just(""),
        st.just("   "),
        st.just("\t"),
        st.just("\n"),
        st.just("\r\n"),
        st.just("  \t  \n  "),
        st.text(alphabet=st.sampled_from([" ", "\t", "\n", "\r"]), min_size=1, max_size=20)
    )
)
def test_voice_feedback_rejects_empty_text(invalid_text):
    """
    Property 15 (variant): Voice feedback rejects empty or whitespace-only text
    
    For any empty or whitespace-only feedback text, the voice service should
    raise a TTSAPIError indicating that the text cannot be empty.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for OpenAI TTS
    test_settings = create_test_settings(tts_service="openai")
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Attempt to generate voice feedback with empty/whitespace text
    with pytest.raises(TTSAPIError) as exc_info:
        voice_service.generate_voice_feedback(invalid_text)
    
    # Verify the error message mentions empty text
    error_message = str(exc_info.value)
    assert "empty" in error_message.lower() or "cannot be empty" in error_message.lower()


@settings(max_examples=50)
@given(
    feedback_text=feedback_text,
    # Generate various lengths of audio data to test different scenarios
    audio_size=st.integers(min_value=100, max_value=1000000)
)
def test_voice_feedback_handles_various_audio_sizes(feedback_text, audio_size):
    """
    Property 15 (variant): Voice feedback handles various audio data sizes
    
    For any successful TTS generation, the voice service should correctly
    handle and return audio data of various sizes, from small to large.
    
    Feature: ai-assessment-backend, Property 15: Voice feedback generation returns valid response
    Validates: Requirements 6.2
    """
    # Create test settings for OpenAI TTS
    test_settings = create_test_settings(tts_service="openai")
    
    # Create voice service
    voice_service = VoiceService(test_settings)
    
    # Generate audio data of the specified size
    audio_data = b"x" * audio_size
    
    # Mock the OpenAI client's TTS method
    with patch.object(voice_service.openai_client.audio.speech, 'create') as mock_create:
        # Create a mock response object
        mock_response = Mock()
        mock_response.read.return_value = audio_data
        mock_create.return_value = mock_response
        
        # Call generate_voice_feedback
        result = voice_service.generate_voice_feedback(feedback_text)
        
        # Verify that the result has the correct size
        assert len(result) == audio_size, (
            f"Voice feedback should return audio data of the correct size. "
            f"Expected: {audio_size} bytes, Got: {len(result)} bytes"
        )
        
        # Verify that the audio data is correct
        assert result == audio_data, "Voice feedback should return the correct audio data"
