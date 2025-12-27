"""
Property-based tests for audio service validation

Feature: ai-assessment-backend, Property 11 & 12: Audio format validation

This module tests that the audio service properly validates audio file formats,
accepting supported formats and rejecting unsupported formats.

Validates: Requirements 5.1, 5.4
"""

from io import BytesIO
from hypothesis import given, strategies as st, settings
from fastapi import UploadFile
import pytest

from app.services.audio_service import AudioService
from app.exceptions import AudioFileError
from config.settings import Settings


# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Supported audio formats by Whisper API
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]

# Common unsupported audio/video/document formats
UNSUPPORTED_FORMATS = [
    "txt", "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "avi", "mov", "wmv", "flv", "mkv", "ogg", "ogv",
    "aac", "flac", "wma", "aiff", "alac",
    "zip", "rar", "tar", "gz", "7z",
    "jpg", "jpeg", "png", "gif", "bmp", "svg",
    "exe", "dll", "so", "dylib",
    "json", "xml", "csv", "html", "css", "js", "py", "java", "cpp"
]

# Strategy for generating supported format extensions
supported_formats = st.sampled_from(SUPPORTED_FORMATS)

# Strategy for generating unsupported format extensions
unsupported_formats = st.sampled_from(UNSUPPORTED_FORMATS)

# Strategy for generating valid filenames with supported extensions
def filename_with_extension(extension: str) -> str:
    """Generate a filename with the given extension"""
    # Generate a simple filename (alphanumeric with underscores/hyphens)
    base_name = st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_-"),
        min_size=1,
        max_size=50
    ).filter(lambda x: x and x.strip() and not x.startswith('.'))
    return st.builds(lambda name: f"{name}.{extension}", base_name)

# Strategy for generating file sizes (in bytes) that are valid (non-zero and under limit)
# Default max is 25MB = 26214400 bytes
valid_file_sizes = st.integers(min_value=1, max_value=26214400)


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_upload_file(filename: str, content_size: int) -> UploadFile:
    """
    Create a mock UploadFile for testing.
    
    Args:
        filename: The filename with extension
        content_size: Size of the file content in bytes
    
    Returns:
        UploadFile: A mock upload file object
    """
    # Create file content of specified size
    content = b"x" * content_size
    file_obj = BytesIO(content)
    
    # Create UploadFile instance
    upload_file = UploadFile(filename=filename, file=file_obj)
    
    return upload_file


def create_test_settings() -> Settings:
    """
    Create test settings with mock API keys.
    
    Returns:
        Settings: Test settings instance
    """
    import os
    # Set required environment variables for testing
    os.environ["OPENAI_API_KEY"] = "test-key-123"
    os.environ["TTS_API_KEY"] = "test-tts-key-123"
    
    return Settings()


# ============================================================================
# Property Test for Supported Audio Formats
# ============================================================================

@settings(max_examples=50)
@given(
    extension=supported_formats,
    file_size=valid_file_sizes
)
def test_audio_format_validation_accepts_supported_formats(extension, file_size):
    """
    Property 11: Audio format validation accepts supported formats
    
    For any audio file with a supported format extension (mp3, mp4, mpeg, mpga, 
    m4a, wav, webm) and valid file size, the validation should pass without 
    raising an exception.
    
    Feature: ai-assessment-backend, Property 11: Audio format validation accepts supported formats
    Validates: Requirements 5.1
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with the given extension
    filename = f"test_audio_file.{extension}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should not raise an exception
    try:
        audio_service._validate_audio_file(upload_file)
        # If we get here, validation passed (which is expected)
        assert True
    except Exception as e:
        # If an exception is raised, the test should fail
        pytest.fail(f"Validation failed for supported format '{extension}': {str(e)}")


@settings(max_examples=50)
@given(
    extension=supported_formats,
    file_size=valid_file_sizes
)
def test_audio_format_validation_accepts_uppercase_extensions(extension, file_size):
    """
    Property 11 (variant): Audio format validation accepts supported formats with uppercase
    
    For any audio file with a supported format extension in uppercase or mixed case,
    the validation should pass (case-insensitive validation).
    
    Feature: ai-assessment-backend, Property 11: Audio format validation accepts supported formats
    Validates: Requirements 5.1
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with uppercase extension
    filename = f"test_audio_file.{extension.upper()}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should not raise an exception
    try:
        audio_service._validate_audio_file(upload_file)
        # If we get here, validation passed (which is expected)
        assert True
    except Exception as e:
        # If an exception is raised, the test should fail
        pytest.fail(f"Validation failed for supported format '{extension.upper()}': {str(e)}")


@settings(max_examples=50)
@given(
    extension=supported_formats,
    file_size=valid_file_sizes
)
def test_audio_format_validation_accepts_mixed_case_extensions(extension, file_size):
    """
    Property 11 (variant): Audio format validation accepts supported formats with mixed case
    
    For any audio file with a supported format extension in mixed case,
    the validation should pass (case-insensitive validation).
    
    Feature: ai-assessment-backend, Property 11: Audio format validation accepts supported formats
    Validates: Requirements 5.1
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with mixed case extension (capitalize first letter)
    mixed_case_ext = extension[0].upper() + extension[1:].lower() if len(extension) > 1 else extension.upper()
    filename = f"test_audio_file.{mixed_case_ext}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should not raise an exception
    try:
        audio_service._validate_audio_file(upload_file)
        # If we get here, validation passed (which is expected)
        assert True
    except Exception as e:
        # If an exception is raised, the test should fail
        pytest.fail(f"Validation failed for supported format '{mixed_case_ext}': {str(e)}")



# ============================================================================
# Property Test for Unsupported Audio Formats
# ============================================================================

@settings(max_examples=50)
@given(
    extension=unsupported_formats,
    file_size=valid_file_sizes
)
def test_audio_format_validation_rejects_unsupported_formats(extension, file_size):
    """
    Property 12: Audio format validation rejects unsupported formats
    
    For any audio file with an unsupported format extension, the validation 
    should fail and raise an AudioFileError indicating invalid format.
    
    Feature: ai-assessment-backend, Property 12: Audio format validation rejects unsupported formats
    Validates: Requirements 5.1, 5.4
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with the unsupported extension
    filename = f"test_audio_file.{extension}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should raise AudioFileError
    with pytest.raises(AudioFileError) as exc_info:
        audio_service._validate_audio_file(upload_file)
    
    # Verify the error message mentions unsupported format
    error_message = str(exc_info.value)
    assert "Unsupported audio format" in error_message or "unsupported" in error_message.lower()
    
    # Verify the error details contain the filename
    assert exc_info.value.details.get("filename") == filename


@settings(max_examples=50)
@given(
    extension=unsupported_formats,
    file_size=valid_file_sizes
)
def test_audio_format_validation_rejects_unsupported_formats_uppercase(extension, file_size):
    """
    Property 12 (variant): Audio format validation rejects unsupported formats with uppercase
    
    For any audio file with an unsupported format extension in uppercase,
    the validation should fail (case-insensitive rejection).
    
    Feature: ai-assessment-backend, Property 12: Audio format validation rejects unsupported formats
    Validates: Requirements 5.1, 5.4
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with uppercase unsupported extension
    filename = f"test_audio_file.{extension.upper()}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should raise AudioFileError
    with pytest.raises(AudioFileError) as exc_info:
        audio_service._validate_audio_file(upload_file)
    
    # Verify the error message mentions unsupported format
    error_message = str(exc_info.value)
    assert "Unsupported audio format" in error_message or "unsupported" in error_message.lower()


@settings(max_examples=50)
@given(file_size=valid_file_sizes)
def test_audio_format_validation_rejects_files_without_extension(file_size):
    """
    Property 12 (variant): Audio format validation rejects files without extension
    
    For any file without an extension, the validation should fail and raise 
    an AudioFileError.
    
    Feature: ai-assessment-backend, Property 12: Audio format validation rejects unsupported formats
    Validates: Requirements 5.1, 5.4
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename without extension
    filename = "test_audio_file_no_extension"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should raise AudioFileError
    with pytest.raises(AudioFileError) as exc_info:
        audio_service._validate_audio_file(upload_file)
    
    # Verify the error message mentions unsupported format
    error_message = str(exc_info.value)
    assert "Unsupported audio format" in error_message or "unsupported" in error_message.lower()


# ============================================================================
# Property Test for Audio File Size Validation
# ============================================================================

@settings(max_examples=50)
@given(
    extension=supported_formats,
    # Generate file sizes that exceed the limit (25MB = 26214400 bytes)
    # Test with sizes from just over the limit to much larger
    file_size=st.integers(min_value=26214401, max_value=100 * 1024 * 1024)  # 25MB+1 to 100MB
)
def test_audio_file_size_validation_enforces_limit(extension, file_size):
    """
    Property 13: Audio file size validation enforces limit
    
    For any audio file larger than the configured maximum size (25MB by default),
    the validation should fail and raise an AudioFileError indicating the file
    size exceeds the limit.
    
    Feature: ai-assessment-backend, Property 13: Audio file size validation enforces limit
    Validates: Requirements 10.4
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with supported extension
    filename = f"large_audio_file.{extension}"
    
    # Create mock upload file with size exceeding the limit
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should raise AudioFileError
    with pytest.raises(AudioFileError) as exc_info:
        audio_service._validate_audio_file(upload_file)
    
    # Verify the error message mentions file size exceeding limit
    error_message = str(exc_info.value)
    assert "exceeds maximum" in error_message.lower() or "too large" in error_message.lower()
    
    # Verify the error details contain the filename
    assert exc_info.value.details.get("filename") == filename
    
    # Verify the error details contain file size information
    assert exc_info.value.details.get("file_size_bytes") == file_size
    assert exc_info.value.details.get("max_size_bytes") == test_settings.max_audio_size_bytes


@settings(max_examples=50)
@given(
    extension=supported_formats,
    # Generate file sizes at the boundary (exactly at the limit)
    # This tests the edge case where file_size == max_size
)
def test_audio_file_size_validation_accepts_files_at_limit(extension):
    """
    Property 13 (variant): Audio file size validation accepts files at the limit
    
    For any audio file with size exactly equal to the maximum allowed size,
    the validation should pass (boundary test).
    
    Feature: ai-assessment-backend, Property 13: Audio file size validation enforces limit
    Validates: Requirements 10.4
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with supported extension
    filename = f"boundary_audio_file.{extension}"
    
    # Create mock upload file with size exactly at the limit
    file_size = test_settings.max_audio_size_bytes
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Validate the audio file - should not raise an exception
    try:
        audio_service._validate_audio_file(upload_file)
        # If we get here, validation passed (which is expected)
        assert True
    except Exception as e:
        # If an exception is raised, the test should fail
        pytest.fail(f"Validation failed for file at size limit ({file_size} bytes): {str(e)}")


@settings(max_examples=50)
@given(extension=supported_formats)
def test_audio_file_size_validation_rejects_empty_files(extension):
    """
    Property 13 (variant): Audio file size validation rejects empty files
    
    For any audio file with zero size, the validation should fail and raise
    an AudioFileError indicating the file is empty.
    
    Feature: ai-assessment-backend, Property 13: Audio file size validation enforces limit
    Validates: Requirements 10.4
    """
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with supported extension
    filename = f"empty_audio_file.{extension}"
    
    # Create mock upload file with zero size
    upload_file = create_mock_upload_file(filename, 0)
    
    # Validate the audio file - should raise AudioFileError
    with pytest.raises(AudioFileError) as exc_info:
        audio_service._validate_audio_file(upload_file)
    
    # Verify the error message mentions empty file
    error_message = str(exc_info.value)
    assert "empty" in error_message.lower()
    
    # Verify the error details contain the filename
    assert exc_info.value.details.get("filename") == filename
    
    # Verify the error details contain file size of 0
    assert exc_info.value.details.get("file_size_bytes") == 0


# ============================================================================
# Property Test for Transcription Response
# ============================================================================

@settings(max_examples=50)
@given(
    extension=supported_formats,
    file_size=valid_file_sizes,
    # Generate arbitrary transcribed text that Whisper API might return
    transcribed_text=st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd", "P", "Z"),
            min_codepoint=32,
            max_codepoint=126
        ),
        min_size=1,
        max_size=500
    ).filter(lambda x: x.strip())  # Ensure non-empty after stripping
)
def test_transcription_response_returns_text(extension, file_size, transcribed_text):
    """
    Property 14: Transcription response returns text
    
    For any valid Whisper API response containing transcribed text, the 
    Audio_Processor should return the transcribed text without modification
    (after stripping whitespace).
    
    This property verifies that the audio service correctly extracts and returns
    the transcription text from the Whisper API response, preserving the content
    exactly as returned by the API.
    
    Feature: ai-assessment-backend, Property 14: Transcription response returns text
    Validates: Requirements 5.3
    """
    from unittest.mock import Mock, patch
    
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with supported extension
    filename = f"test_audio.{extension}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Mock the OpenAI client's transcription method
    # The Whisper API returns the transcribed text directly as a string
    with patch.object(audio_service.client.audio.transcriptions, 'create') as mock_create:
        # Set the mock to return the transcribed text
        mock_create.return_value = transcribed_text
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify that the result matches the transcribed text (after stripping)
        expected_text = transcribed_text.strip()
        assert result == expected_text, (
            f"Transcription result does not match expected text.\n"
            f"Expected: {repr(expected_text)}\n"
            f"Got: {repr(result)}"
        )
        
        # Verify that the OpenAI API was called with correct parameters
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args.kwargs
        
        # Verify model parameter
        assert call_kwargs.get("model") == "whisper-1"
        
        # Verify response format
        assert call_kwargs.get("response_format") == "text"
        
        # Verify file parameter exists
        assert "file" in call_kwargs


@settings(max_examples=50)
@given(
    extension=supported_formats,
    file_size=valid_file_sizes,
    # Generate text with leading/trailing whitespace to test stripping
    transcribed_text=st.text(
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd", "P"),
            min_codepoint=32,
            max_codepoint=126
        ),
        min_size=1,
        max_size=200
    ).filter(lambda x: x.strip()),  # Ensure non-empty after stripping
    leading_spaces=st.integers(min_value=0, max_value=10),
    trailing_spaces=st.integers(min_value=0, max_value=10)
)
def test_transcription_response_strips_whitespace(
    extension, file_size, transcribed_text, leading_spaces, trailing_spaces
):
    """
    Property 14 (variant): Transcription response strips leading/trailing whitespace
    
    For any valid Whisper API response containing transcribed text with leading
    or trailing whitespace, the Audio_Processor should return the text with
    whitespace stripped.
    
    This ensures consistent output regardless of how the Whisper API formats
    the response.
    
    Feature: ai-assessment-backend, Property 14: Transcription response returns text
    Validates: Requirements 5.3
    """
    from unittest.mock import Mock, patch
    
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with supported extension
    filename = f"test_audio.{extension}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Add leading and trailing whitespace to the transcribed text
    text_with_whitespace = (" " * leading_spaces) + transcribed_text + (" " * trailing_spaces)
    
    # Mock the OpenAI client's transcription method
    with patch.object(audio_service.client.audio.transcriptions, 'create') as mock_create:
        # Set the mock to return the text with whitespace
        mock_create.return_value = text_with_whitespace
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify that the result has whitespace stripped
        expected_text = transcribed_text.strip()
        assert result == expected_text, (
            f"Transcription result should have whitespace stripped.\n"
            f"Expected: {repr(expected_text)}\n"
            f"Got: {repr(result)}"
        )
        
        # Verify no leading or trailing whitespace in result
        assert result == result.strip(), "Result should not have leading/trailing whitespace"


@settings(max_examples=50)
@given(
    extension=supported_formats,
    file_size=valid_file_sizes,
    # Generate multi-line transcribed text
    lines=st.lists(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd", "P"),
                min_codepoint=32,
                max_codepoint=126
            ),
            min_size=1,
            max_size=100
        ).filter(lambda x: x.strip()),
        min_size=1,
        max_size=10
    )
)
def test_transcription_response_preserves_multiline_text(extension, file_size, lines):
    """
    Property 14 (variant): Transcription response preserves multi-line text
    
    For any valid Whisper API response containing multi-line transcribed text,
    the Audio_Processor should preserve the line structure while stripping
    leading/trailing whitespace from the entire text.
    
    Feature: ai-assessment-backend, Property 14: Transcription response returns text
    Validates: Requirements 5.3
    """
    from unittest.mock import Mock, patch
    
    # Create test settings
    test_settings = create_test_settings()
    
    # Create audio service
    audio_service = AudioService(test_settings)
    
    # Generate filename with supported extension
    filename = f"test_audio.{extension}"
    
    # Create mock upload file
    upload_file = create_mock_upload_file(filename, file_size)
    
    # Join lines with newlines to create multi-line text
    transcribed_text = "\n".join(lines)
    
    # Mock the OpenAI client's transcription method
    with patch.object(audio_service.client.audio.transcriptions, 'create') as mock_create:
        # Set the mock to return the multi-line text
        mock_create.return_value = transcribed_text
        
        # Call transcribe_audio
        result = audio_service.transcribe_audio(upload_file)
        
        # Verify that the result preserves the multi-line structure
        expected_text = transcribed_text.strip()
        assert result == expected_text, (
            f"Transcription result should preserve multi-line structure.\n"
            f"Expected: {repr(expected_text)}\n"
            f"Got: {repr(result)}"
        )
        
        # Verify that newlines are preserved in the result
        if "\n" in transcribed_text:
            assert "\n" in result, "Multi-line structure should be preserved"
