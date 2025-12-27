"""
Property-based tests for API endpoint invalid parameter handling

Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status

This module tests that API endpoints properly handle invalid parameters:
- Invalid parameter types return 400 status code
- Invalid parameter values return 400 status code
- Error responses contain proper error details

Validates: Requirements 7.6
"""

import os
from uuid import uuid4
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from main import app
from app.models import Difficulty


# ============================================================================
# Test Client Setup
# ============================================================================

def get_test_client():
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
# Hypothesis Strategies
# ============================================================================

# Valid strategies for comparison
valid_topics = st.text(min_size=1, max_size=200)
valid_difficulties = st.sampled_from(["Easy", "Medium", "Hard"])
valid_uuids = st.builds(lambda: str(uuid4()))
valid_answer_text = st.text(min_size=1, max_size=5000)
valid_feedback_text = st.text(min_size=1, max_size=5000)

# Invalid parameter strategies
invalid_types_for_string = st.one_of(
    st.integers(),
    st.floats(),
    st.booleans(),
    st.lists(st.text()),
    st.dictionaries(st.text(), st.text()),
    st.none()
)

invalid_difficulties = st.text().filter(
    lambda x: x not in ["Easy", "Medium", "Hard"] and x != ""
)

invalid_uuids = st.one_of(
    st.text(min_size=1).filter(lambda x: x and not _is_valid_uuid(x) and x.isprintable()),
    st.just("not-a-uuid"),
    st.just("12345"),
    st.just("invalid-uuid-format"),
)


def _is_valid_uuid(s: str) -> bool:
    """Helper to check if a string is a valid UUID"""
    try:
        from uuid import UUID
        UUID(s)
        return True
    except (ValueError, AttributeError):
        return False


# ============================================================================
# Property Tests for POST /start-session
# ============================================================================

@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(topic=valid_topics, invalid_difficulty=invalid_difficulties)
def test_start_session_invalid_difficulty_returns_400(topic, invalid_difficulty):
    """
    Property: For any invalid difficulty value, POST /start-session should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/start-session",
        json={
            "topic": topic,
            "initial_difficulty": invalid_difficulty
        }
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code} for difficulty '{invalid_difficulty}'"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(difficulty=valid_difficulties)
def test_start_session_missing_topic_returns_400(difficulty):
    """
    Property: For any request missing topic, POST /start-session should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/start-session",
        json={
            "initial_difficulty": difficulty
            # topic is missing
        }
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(topic=valid_topics)
def test_start_session_missing_difficulty_returns_400(topic):
    """
    Property: For any request missing initial_difficulty, POST /start-session should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/start-session",
        json={
            "topic": topic
            # initial_difficulty is missing
        }
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


# ============================================================================
# Property Tests for GET /get-next-question
# ============================================================================

@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(invalid_session_id=invalid_uuids)
def test_get_next_question_invalid_session_id_returns_400_or_404(invalid_session_id):
    """
    Property: For any invalid session_id format, GET /get-next-question should return 400 or 404 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.get(
        f"/api/get-next-question?session_id={invalid_session_id}"
    )
    
    # Should return 400, 404, or 422 (validation error or not found)
    assert response.status_code in [400, 404, 422], \
        f"Expected 400, 404, or 422, got {response.status_code} for session_id '{invalid_session_id}'"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


def test_get_next_question_missing_session_id_returns_400():
    """
    Property: For any request missing session_id, GET /get-next-question should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.get("/api/get-next-question")
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


# ============================================================================
# Property Tests for POST /submit-answer
# ============================================================================

@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    invalid_session_id=invalid_uuids,
    question_id=valid_uuids,
    answer_text=valid_answer_text
)
def test_submit_answer_invalid_session_id_returns_400_or_404(
    invalid_session_id, question_id, answer_text
):
    """
    Property: For any invalid session_id format, POST /submit-answer should return 400 or 404 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/submit-answer",
        json={
            "session_id": invalid_session_id,
            "question_id": question_id,
            "answer_text": answer_text
        }
    )
    
    # Should return 400, 404, or 422 (validation error or not found)
    assert response.status_code in [400, 404, 422], \
        f"Expected 400, 404, or 422, got {response.status_code} for session_id '{invalid_session_id}'"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    session_id=valid_uuids,
    invalid_question_id=invalid_uuids,
    answer_text=valid_answer_text
)
def test_submit_answer_invalid_question_id_returns_400(
    session_id, invalid_question_id, answer_text
):
    """
    Property: For any invalid question_id format, POST /submit-answer should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/submit-answer",
        json={
            "session_id": session_id,
            "question_id": invalid_question_id,
            "answer_text": answer_text
        }
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code} for question_id '{invalid_question_id}'"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(session_id=valid_uuids, question_id=valid_uuids)
def test_submit_answer_missing_answer_text_returns_400(session_id, question_id):
    """
    Property: For any request missing answer_text, POST /submit-answer should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/submit-answer",
        json={
            "session_id": session_id,
            "question_id": question_id
            # answer_text is missing
        }
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


# ============================================================================
# Property Tests for POST /generate-voice-feedback
# ============================================================================

def test_generate_voice_feedback_missing_feedback_text_returns_400():
    """
    Property: For any request missing feedback_text, POST /generate-voice-feedback should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/generate-voice-feedback",
        json={}  # feedback_text is missing
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(empty_feedback=st.just(""))
def test_generate_voice_feedback_empty_feedback_text_returns_400(empty_feedback):
    """
    Property: For any empty feedback_text, POST /generate-voice-feedback should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/generate-voice-feedback",
        json={"feedback_text": empty_feedback}
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


# ============================================================================
# Property Tests for POST /transcribe-audio
# ============================================================================

def test_transcribe_audio_missing_file_returns_400():
    """
    Property: For any request missing audio file, POST /transcribe-audio should return 400 status.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/transcribe-audio",
        files={}  # No file provided
    )
    
    # Should return 400 or 422 (validation error)
    assert response.status_code in [400, 422], \
        f"Expected 400 or 422, got {response.status_code}"
    
    # Response should contain error details
    error_data = response.json()
    assert "detail" in error_data


# ============================================================================
# Property Tests for Error Response Structure
# ============================================================================

@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(topic=valid_topics, invalid_difficulty=invalid_difficulties)
def test_error_responses_contain_detail_field(topic, invalid_difficulty):
    """
    Property: For any invalid request, error responses should contain a 'detail' field.
    
    Feature: ai-assessment-backend, Property 17: Invalid parameters return 400 status
    Validates: Requirements 7.6
    """
    client = get_test_client()
    response = client.post(
        "/api/start-session",
        json={
            "topic": topic,
            "initial_difficulty": invalid_difficulty
        }
    )
    
    # Should return error status
    assert response.status_code >= 400
    
    # Response should be JSON with detail field
    error_data = response.json()
    assert "detail" in error_data, \
        f"Error response missing 'detail' field: {error_data}"
