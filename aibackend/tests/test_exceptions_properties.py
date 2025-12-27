"""
Property-based tests for error response structure

Feature: ai-assessment-backend, Property 18: Error responses have required structure

This module tests that all exceptions produce error responses with:
- error_type field (string)
- message field (string)
- details field (dict, may be empty)

The to_dict() method on all exception classes should return a consistent structure.

Validates: Requirements 9.2
"""

from hypothesis import given, strategies as st, settings
import pytest
from datetime import datetime

from app.exceptions import (
    AssessmentError,
    SessionNotFoundError,
    InvalidDifficultyError,
    OpenAIAPIError,
    WhisperAPIError,
    TTSAPIError,
    ValidationError,
    AudioFileError,
    QuestionGenerationError,
    EvaluationError,
)


# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Generate random strings for error messages and context
error_messages = st.text(min_size=1, max_size=500)
session_ids = st.text(min_size=1, max_size=100)
difficulty_values = st.text(min_size=1, max_size=50)
operation_names = st.sampled_from([
    "evaluation", "question_generation", "audio_transcription",
    "voice_synthesis", "session_creation", "session_update"
])
service_names = st.sampled_from([
    "OpenAI", "Whisper", "ElevenLabs", "OpenAI TTS", "TTS"
])
field_names = st.text(min_size=1, max_size=100)
topic_names = st.text(min_size=1, max_size=200)
filenames = st.text(min_size=1, max_size=255)
file_sizes = st.integers(min_value=0, max_value=100_000_000)
question_ids = st.text(min_size=1, max_size=100)


# ============================================================================
# Helper Functions
# ============================================================================

def assert_error_response_structure(error_dict: dict):
    """
    Assert that an error response dictionary has the required structure.
    
    Required fields:
    - error_type: str (non-empty)
    - message: str (non-empty)
    - details: dict (may be empty)
    """
    assert isinstance(error_dict, dict), "Error response must be a dictionary"
    assert "error_type" in error_dict, "Error response must contain 'error_type' field"
    assert "message" in error_dict, "Error response must contain 'message' field"
    assert "details" in error_dict, "Error response must contain 'details' field"
    
    assert isinstance(error_dict["error_type"], str), "error_type must be a string"
    assert isinstance(error_dict["message"], str), "message must be a string"
    assert isinstance(error_dict["details"], dict), "details must be a dictionary"
    
    assert len(error_dict["error_type"]) > 0, "error_type must not be empty"
    assert len(error_dict["message"]) > 0, "message must not be empty"


# ============================================================================
# Property Tests for Base Exception
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages)
def test_assessment_error_has_required_structure(message):
    """
    Property: For any error message, AssessmentError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = AssessmentError(message=message)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "AssessmentError"
    assert error_dict["message"] == message


@settings(max_examples=50)
@given(message=error_messages, details=st.dictionaries(st.text(), st.text()))
def test_assessment_error_with_details_has_required_structure(message, details):
    """
    Property: For any error message and details dict, AssessmentError.to_dict()
    should preserve the details in the response.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = AssessmentError(message=message, details=details)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["details"] == details


# ============================================================================
# Property Tests for SessionNotFoundError
# ============================================================================

@settings(max_examples=50)
@given(session_id=session_ids)
def test_session_not_found_error_has_required_structure(session_id):
    """
    Property: For any session_id, SessionNotFoundError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = SessionNotFoundError(session_id=session_id)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "SessionNotFoundError"
    assert session_id in error_dict["message"]
    assert "session_id" in error_dict["details"]
    assert error_dict["details"]["session_id"] == session_id


# ============================================================================
# Property Tests for InvalidDifficultyError
# ============================================================================

@settings(max_examples=50)
@given(difficulty=difficulty_values)
def test_invalid_difficulty_error_has_required_structure(difficulty):
    """
    Property: For any difficulty value, InvalidDifficultyError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = InvalidDifficultyError(difficulty=difficulty)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "InvalidDifficultyError"
    assert difficulty in error_dict["message"]
    assert "provided_difficulty" in error_dict["details"]
    assert error_dict["details"]["provided_difficulty"] == difficulty


# ============================================================================
# Property Tests for OpenAIAPIError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages, operation=operation_names)
def test_openai_api_error_has_required_structure(message, operation):
    """
    Property: For any error message and operation, OpenAIAPIError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = OpenAIAPIError(message=message, operation=operation)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "OpenAIAPIError"
    assert operation in error_dict["message"]
    assert "operation" in error_dict["details"]
    assert error_dict["details"]["operation"] == operation


# ============================================================================
# Property Tests for WhisperAPIError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages)
def test_whisper_api_error_has_required_structure(message):
    """
    Property: For any error message, WhisperAPIError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = WhisperAPIError(message=message)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "WhisperAPIError"
    assert "operation" in error_dict["details"]
    assert error_dict["details"]["operation"] == "audio_transcription"


# ============================================================================
# Property Tests for TTSAPIError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages, service=service_names)
def test_tts_api_error_has_required_structure(message, service):
    """
    Property: For any error message and service name, TTSAPIError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = TTSAPIError(message=message, service=service)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "TTSAPIError"
    assert service in error_dict["message"]
    assert "service" in error_dict["details"]
    assert error_dict["details"]["service"] == service


# ============================================================================
# Property Tests for ValidationError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages, field=field_names)
def test_validation_error_has_required_structure(message, field):
    """
    Property: For any error message and field name, ValidationError.to_dict() should return
    a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = ValidationError(message=message, field=field)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "ValidationError"
    assert "field" in error_dict["details"]
    assert error_dict["details"]["field"] == field


# ============================================================================
# Property Tests for AudioFileError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages, filename=filenames, file_size=file_sizes)
def test_audio_file_error_has_required_structure(message, filename, file_size):
    """
    Property: For any error message, filename, and file size, AudioFileError.to_dict()
    should return a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = AudioFileError(message=message, filename=filename, file_size=file_size)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "AudioFileError"
    assert "filename" in error_dict["details"]
    assert error_dict["details"]["filename"] == filename


# ============================================================================
# Property Tests for QuestionGenerationError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages, topic=topic_names, difficulty=difficulty_values)
def test_question_generation_error_has_required_structure(message, topic, difficulty):
    """
    Property: For any error message, topic, and difficulty, QuestionGenerationError.to_dict()
    should return a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = QuestionGenerationError(message=message, topic=topic, difficulty=difficulty)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "QuestionGenerationError"
    assert "topic" in error_dict["details"]
    assert error_dict["details"]["topic"] == topic


# ============================================================================
# Property Tests for EvaluationError
# ============================================================================

@settings(max_examples=50)
@given(message=error_messages, question_id=question_ids)
def test_evaluation_error_has_required_structure(message, question_id):
    """
    Property: For any error message and question_id, EvaluationError.to_dict()
    should return a dictionary with error_type, message, and details fields.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    error = EvaluationError(message=message, question_id=question_id)
    error_dict = error.to_dict()
    
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == "EvaluationError"
    assert "question_id" in error_dict["details"]
    assert error_dict["details"]["question_id"] == question_id


# ============================================================================
# Property Tests for All Exception Types
# ============================================================================

@settings(max_examples=50)
@given(
    exception_type=st.sampled_from([
        SessionNotFoundError,
        InvalidDifficultyError,
        OpenAIAPIError,
        WhisperAPIError,
        TTSAPIError,
        ValidationError,
        AudioFileError,
        QuestionGenerationError,
        EvaluationError,
    ]),
    message=error_messages
)
def test_all_exceptions_inherit_to_dict_structure(exception_type, message):
    """
    Property: For any exception type in the system, calling to_dict() should return
    a dictionary with the required error response structure.
    
    Feature: ai-assessment-backend, Property 18: Error responses have required structure
    Validates: Requirements 9.2
    """
    # Create exception with minimal required parameters
    if exception_type == SessionNotFoundError:
        error = exception_type(session_id="test-session-id")
    elif exception_type == InvalidDifficultyError:
        error = exception_type(difficulty="TestDifficulty")
    elif exception_type == OpenAIAPIError:
        error = exception_type(message=message, operation="test_operation")
    elif exception_type == WhisperAPIError:
        error = exception_type(message=message)
    elif exception_type == TTSAPIError:
        error = exception_type(message=message)
    elif exception_type == ValidationError:
        error = exception_type(message=message)
    elif exception_type == AudioFileError:
        error = exception_type(message=message)
    elif exception_type == QuestionGenerationError:
        error = exception_type(message=message)
    elif exception_type == EvaluationError:
        error = exception_type(message=message)
    else:
        error = exception_type(message=message)
    
    error_dict = error.to_dict()
    assert_error_response_structure(error_dict)
    assert error_dict["error_type"] == exception_type.__name__
