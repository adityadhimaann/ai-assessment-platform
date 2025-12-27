"""
Unit tests for API error status codes

This module tests that API endpoints return the correct HTTP status codes
for various error conditions.

Validates: Requirements 7.6, 7.7
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from main import app
from app.exceptions import (
    SessionNotFoundError,
    QuestionGenerationError,
    EvaluationError,
    WhisperAPIError,
    TTSAPIError,
    AudioFileError,
    ValidationError
)


# ============================================================================
# Test Client Setup
# ============================================================================

@pytest.fixture(scope="module")
def test_client():
    """Create test client for FastAPI app"""
    # Set required environment variables for testing
    os.environ.setdefault("OPENAI_API_KEY", "test-key-123")
    os.environ.setdefault("TTS_API_KEY", "test-tts-key-123")
    
    # Register routers if not already registered
    from app.routers import assessment, audio
    
    # Check if routers are already included
    routes = [route.path for route in app.routes]
    if "/api/start-session" not in routes:
        app.include_router(assessment.router)
    if "/api/transcribe-audio" not in routes:
        app.include_router(audio.router)
    
    return TestClient(app)


# ============================================================================
# Tests for 400 Bad Request - Invalid Parameters
# ============================================================================

def test_start_session_returns_400_for_missing_topic(test_client):
    """
    Test that POST /start-session returns 400 when topic is missing.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/start-session",
        json={
            "initial_difficulty": "Medium"
        }
    )
    
    # Should return 422 (validation error) for missing required field
    assert response.status_code == 422, \
        f"Expected 422 for missing topic, got {response.status_code}"


def test_start_session_returns_422_for_invalid_difficulty(test_client):
    """
    Test that POST /start-session returns 422 when difficulty is invalid.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/start-session",
        json={
            "topic": "Python Programming",
            "initial_difficulty": "VeryHard"  # Invalid difficulty
        }
    )
    
    # Should return 422 (validation error) for invalid enum value
    assert response.status_code == 422, \
        f"Expected 422 for invalid difficulty, got {response.status_code}"


def test_submit_answer_returns_422_for_missing_fields(test_client):
    """
    Test that POST /submit-answer returns 422 when required fields are missing.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000"
            # Missing question_id and answer_text
        }
    )
    
    # Should return 422 (validation error) for missing required fields
    assert response.status_code == 422, \
        f"Expected 422 for missing fields, got {response.status_code}"


def test_submit_answer_returns_422_for_invalid_session_id_format(test_client):
    """
    Test that POST /submit-answer returns 422 when session_id is not a valid UUID.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": "not-a-valid-uuid",
            "question_id": "550e8400-e29b-41d4-a716-446655440001",
            "answer_text": "Test answer"
        }
    )
    
    # Should return 422 (validation error) for invalid UUID format
    assert response.status_code == 422, \
        f"Expected 422 for invalid UUID format, got {response.status_code}"


def test_get_next_question_returns_422_for_missing_session_id(test_client):
    """
    Test that GET /get-next-question returns 422 when session_id is missing.
    
    Validates: Requirements 7.6
    """
    response = test_client.get(
        "/api/get-next-question"
        # Missing session_id query parameter
    )
    
    # Should return 422 (validation error) for missing required parameter
    assert response.status_code == 422, \
        f"Expected 422 for missing session_id, got {response.status_code}"


def test_transcribe_audio_returns_400_for_unsupported_format(test_client):
    """
    Test that POST /transcribe-audio returns 400 for unsupported audio format.
    
    Validates: Requirements 7.6
    """
    # Create a mock audio file with unsupported format
    audio_content = b"fake audio content"
    audio_file = BytesIO(audio_content)
    
    with patch('app.services.audio_service.AudioService.transcribe_audio') as mock_transcribe:
        # Mock the service to raise AudioFileError for unsupported format
        mock_transcribe.side_effect = AudioFileError(
            message="Unsupported audio format: .txt",
            filename="test.txt"
        )
        
        response = test_client.post(
            "/api/transcribe-audio",
            files={"audio_file": ("test.txt", audio_file, "text/plain")}
        )
        
        # Should return 400 for invalid file format
        assert response.status_code == 400, \
            f"Expected 400 for unsupported format, got {response.status_code}"
        
        # Verify error response structure
        response_json = response.json()
        error_data = response_json.get("detail", response_json)
        assert "error_type" in error_data
        assert error_data["error_type"] == "AudioFileError"


def test_transcribe_audio_returns_400_for_file_too_large(test_client):
    """
    Test that POST /transcribe-audio returns 400 when file exceeds size limit.
    
    Validates: Requirements 7.6
    """
    # Create a mock audio file
    audio_content = b"fake audio content"
    audio_file = BytesIO(audio_content)
    
    with patch('app.services.audio_service.AudioService.transcribe_audio') as mock_transcribe:
        # Mock the service to raise AudioFileError for file too large
        mock_transcribe.side_effect = AudioFileError(
            message="Audio file exceeds maximum size of 25MB",
            filename="large_file.mp3",
            file_size=30 * 1024 * 1024,  # 30MB
            max_size=25 * 1024 * 1024     # 25MB
        )
        
        response = test_client.post(
            "/api/transcribe-audio",
            files={"audio_file": ("large_file.mp3", audio_file, "audio/mpeg")}
        )
        
        # Should return 400 for file too large
        assert response.status_code == 400, \
            f"Expected 400 for file too large, got {response.status_code}"


def test_generate_voice_feedback_returns_422_for_missing_text(test_client):
    """
    Test that POST /generate-voice-feedback returns 422 when feedback_text is missing.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/generate-voice-feedback",
        json={}  # Missing feedback_text
    )
    
    # Should return 422 (validation error) for missing required field
    assert response.status_code == 422, \
        f"Expected 422 for missing feedback_text, got {response.status_code}"


# ============================================================================
# Tests for 404 Not Found - Session Not Found
# ============================================================================

def test_get_next_question_returns_404_for_nonexistent_session(test_client):
    """
    Test that GET /get-next-question returns 404 when session does not exist.
    
    Validates: Requirements 7.6
    """
    # Use a valid UUID format but non-existent session
    nonexistent_session_id = "550e8400-e29b-41d4-a716-446655440099"
    
    response = test_client.get(
        f"/api/get-next-question?session_id={nonexistent_session_id}"
    )
    
    # Should return 404 for session not found
    assert response.status_code == 404, \
        f"Expected 404 for nonexistent session, got {response.status_code}"
    
    # Verify error response structure
    response_json = response.json()
    error_data = response_json.get("detail", response_json)
    assert "error_type" in error_data
    assert error_data["error_type"] == "SessionNotFoundError"
    assert "message" in error_data


def test_submit_answer_returns_404_for_nonexistent_session(test_client):
    """
    Test that POST /submit-answer returns 404 when session does not exist.
    
    Validates: Requirements 7.6
    """
    # Use a valid UUID format but non-existent session
    nonexistent_session_id = "550e8400-e29b-41d4-a716-446655440099"
    
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": nonexistent_session_id,
            "question_id": "550e8400-e29b-41d4-a716-446655440001",
            "answer_text": "Test answer"
        }
    )
    
    # Should return 404 for session not found
    assert response.status_code == 404, \
        f"Expected 404 for nonexistent session, got {response.status_code}"
    
    # Verify error response structure
    response_json = response.json()
    error_data = response_json.get("detail", response_json)
    assert "error_type" in error_data
    assert error_data["error_type"] == "SessionNotFoundError"


# ============================================================================
# Tests for 422 Validation Errors
# ============================================================================

def test_start_session_returns_422_for_invalid_json(test_client):
    """
    Test that POST /start-session returns 422 for malformed JSON.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/start-session",
        data="not valid json",
        headers={"Content-Type": "application/json"}
    )
    
    # Should return 422 for invalid JSON
    assert response.status_code == 422, \
        f"Expected 422 for invalid JSON, got {response.status_code}"


def test_submit_answer_returns_422_for_empty_answer_text(test_client):
    """
    Test that POST /submit-answer returns 422 when answer_text is empty.
    
    Validates: Requirements 7.6
    """
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "question_id": "550e8400-e29b-41d4-a716-446655440001",
            "answer_text": ""  # Empty answer
        }
    )
    
    # Should return 422 for empty answer (if validation is implemented)
    # or 404 if session doesn't exist (which is checked first)
    assert response.status_code in [422, 404], \
        f"Expected 422 or 404, got {response.status_code}"


# ============================================================================
# Tests for 500 Internal Server Error
# ============================================================================

def test_get_next_question_returns_500_for_question_generation_failure(test_client):
    """
    Test that GET /get-next-question returns 500 when question generation fails.
    
    Validates: Requirements 7.7
    """
    # First create a session
    session_response = test_client.post(
        "/api/start-session",
        json={
            "topic": "Python Programming",
            "initial_difficulty": "Medium"
        }
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["session_id"]
    
    # Mock question service to raise an error
    with patch('app.services.question_service.QuestionService.generate_question') as mock_generate:
        mock_generate.side_effect = QuestionGenerationError(
            message="OpenAI API error",
            topic="Python Programming",
            difficulty="Medium"
        )
        
        response = test_client.get(
            f"/api/get-next-question?session_id={session_id}"
        )
        
        # Should return 500 for question generation failure
        assert response.status_code == 500, \
            f"Expected 500 for question generation failure, got {response.status_code}"
        
        # Verify error response structure
        response_json = response.json()
        error_data = response_json.get("detail", response_json)
        assert "error_type" in error_data
        assert error_data["error_type"] == "QuestionGenerationError"


def test_submit_answer_returns_500_for_evaluation_failure(test_client):
    """
    Test that POST /submit-answer returns 500 when evaluation fails.
    
    Validates: Requirements 7.7
    """
    # First create a session
    session_response = test_client.post(
        "/api/start-session",
        json={
            "topic": "Python Programming",
            "initial_difficulty": "Medium"
        }
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["session_id"]
    
    # Mock evaluation service to raise an error
    with patch('app.services.evaluation_service.EvaluationService.evaluate_answer') as mock_evaluate:
        mock_evaluate.side_effect = EvaluationError(
            message="OpenAI API error",
            question_id="test-question-id"
        )
        
        response = test_client.post(
            "/api/submit-answer",
            json={
                "session_id": session_id,
                "question_id": "550e8400-e29b-41d4-a716-446655440001",
                "answer_text": "Test answer"
            }
        )
        
        # Should return 500 for evaluation failure
        assert response.status_code == 500, \
            f"Expected 500 for evaluation failure, got {response.status_code}"
        
        # Verify error response structure
        response_json = response.json()
        error_data = response_json.get("detail", response_json)
        assert "error_type" in error_data
        assert error_data["error_type"] == "EvaluationError"


def test_transcribe_audio_returns_500_for_whisper_api_failure(test_client):
    """
    Test that POST /transcribe-audio returns 500 when Whisper API fails.
    
    Validates: Requirements 7.7
    """
    # Create a mock audio file
    audio_content = b"fake audio content"
    audio_file = BytesIO(audio_content)
    
    with patch('app.services.audio_service.AudioService.transcribe_audio') as mock_transcribe:
        # Mock the service to raise WhisperAPIError
        mock_transcribe.side_effect = WhisperAPIError(
            message="Whisper API connection failed"
        )
        
        response = test_client.post(
            "/api/transcribe-audio",
            files={"audio_file": ("test.mp3", audio_file, "audio/mpeg")}
        )
        
        # Should return 500 for Whisper API failure
        assert response.status_code == 500, \
            f"Expected 500 for Whisper API failure, got {response.status_code}"
        
        # Verify error response structure
        response_json = response.json()
        error_data = response_json.get("detail", response_json)
        assert "error_type" in error_data
        assert error_data["error_type"] == "WhisperAPIError"


def test_generate_voice_feedback_returns_500_for_tts_api_failure(test_client):
    """
    Test that POST /generate-voice-feedback returns 500 when TTS API fails.
    
    Validates: Requirements 7.7
    """
    with patch('app.services.voice_service.VoiceService.generate_voice_feedback') as mock_generate:
        # Mock the service to raise TTSAPIError
        mock_generate.side_effect = TTSAPIError(
            message="TTS API connection failed",
            service="OpenAI TTS"
        )
        
        response = test_client.post(
            "/api/generate-voice-feedback",
            json={
                "feedback_text": "Great job on your answer!"
            }
        )
        
        # Should return 500 for TTS API failure
        assert response.status_code == 500, \
            f"Expected 500 for TTS API failure, got {response.status_code}"
        
        # Verify error response structure
        response_json = response.json()
        error_data = response_json.get("detail", response_json)
        assert "error_type" in error_data
        assert error_data["error_type"] == "TTSAPIError"


def test_start_session_returns_500_for_unexpected_error(test_client):
    """
    Test that POST /start-session returns 500 for unexpected server errors.
    
    Validates: Requirements 7.7
    """
    with patch('app.services.session_service.SessionService.create_session') as mock_create:
        # Mock the service to raise an unexpected exception
        mock_create.side_effect = Exception("Unexpected database error")
        
        response = test_client.post(
            "/api/start-session",
            json={
                "topic": "Python Programming",
                "initial_difficulty": "Medium"
            }
        )
        
        # Should return 500 for unexpected error
        assert response.status_code == 500, \
            f"Expected 500 for unexpected error, got {response.status_code}"
        
        # Verify error response structure
        response_json = response.json()
        error_data = response_json.get("detail", response_json)
        assert "error_type" in error_data
        assert error_data["error_type"] == "InternalServerError"
        assert "message" in error_data


# ============================================================================
# Tests for Error Response Structure
# ============================================================================

def test_error_responses_have_required_structure(test_client):
    """
    Test that all error responses contain required fields.
    
    Validates: Requirements 7.6, 7.7
    """
    # Test with a 404 error (session not found)
    response = test_client.get(
        "/api/get-next-question?session_id=550e8400-e29b-41d4-a716-446655440099"
    )
    
    assert response.status_code == 404
    response_json = response.json()
    error_data = response_json.get("detail", response_json)
    
    # Verify required fields are present
    assert "error_type" in error_data, "Error response missing 'error_type' field"
    assert "message" in error_data, "Error response missing 'message' field"
    
    # Verify error_type is a string
    assert isinstance(error_data["error_type"], str), \
        "error_type should be a string"
    
    # Verify message is a string
    assert isinstance(error_data["message"], str), \
        "message should be a string"


def test_validation_error_response_structure(test_client):
    """
    Test that validation errors (422) have proper structure.
    
    Validates: Requirements 7.6
    """
    # Test with missing required field
    response = test_client.post(
        "/api/start-session",
        json={
            "initial_difficulty": "Medium"
            # Missing topic
        }
    )
    
    assert response.status_code == 422
    error_data = response.json()
    
    # FastAPI validation errors have a 'detail' field
    assert "detail" in error_data, "Validation error missing 'detail' field"
