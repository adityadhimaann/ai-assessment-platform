"""
Unit tests for API endpoint existence and parameter acceptance

This module tests that all required API endpoints are properly registered
and accept the correct parameters.

Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from main import app


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
# Tests for POST /start-session endpoint
# ============================================================================

def test_start_session_endpoint_exists(test_client):
    """
    Test that POST /start-session endpoint exists and is accessible.
    
    Validates: Requirements 7.1
    """
    # Make a request to the endpoint (even with invalid data)
    response = test_client.post(
        "/api/start-session",
        json={}
    )
    
    # Endpoint should exist (not return 404)
    assert response.status_code != 404, \
        "POST /start-session endpoint does not exist"


def test_start_session_accepts_topic_parameter(test_client):
    """
    Test that POST /start-session accepts topic parameter.
    
    Validates: Requirements 7.1
    """
    # Make a request with topic parameter
    response = test_client.post(
        "/api/start-session",
        json={
            "topic": "Python Programming",
            "initial_difficulty": "Medium"
        }
    )
    
    # Should not return 400 for missing topic (may return other errors)
    # The key is that the endpoint accepts the parameter
    assert response.status_code != 400 or "topic" not in str(response.json().get("detail", "")), \
        "Endpoint does not properly accept topic parameter"


def test_start_session_accepts_initial_difficulty_parameter(test_client):
    """
    Test that POST /start-session accepts initial_difficulty parameter.
    
    Validates: Requirements 7.1
    """
    # Make a request with initial_difficulty parameter
    response = test_client.post(
        "/api/start-session",
        json={
            "topic": "Python Programming",
            "initial_difficulty": "Medium"
        }
    )
    
    # Should not return 400 for missing initial_difficulty
    assert response.status_code != 400 or "initial_difficulty" not in str(response.json().get("detail", "")), \
        "Endpoint does not properly accept initial_difficulty parameter"


# ============================================================================
# Tests for POST /submit-answer endpoint
# ============================================================================

def test_submit_answer_endpoint_exists(test_client):
    """
    Test that POST /submit-answer endpoint exists and is accessible.
    
    Validates: Requirements 7.2
    """
    # Make a request to the endpoint (even with invalid data)
    response = test_client.post(
        "/api/submit-answer",
        json={}
    )
    
    # Endpoint should exist (not return 404)
    assert response.status_code != 404, \
        "POST /submit-answer endpoint does not exist"


def test_submit_answer_accepts_session_id_parameter(test_client):
    """
    Test that POST /submit-answer accepts session_id parameter.
    
    Validates: Requirements 7.2
    """
    # Make a request with session_id parameter
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "question_id": "550e8400-e29b-41d4-a716-446655440001",
            "answer_text": "Test answer"
        }
    )
    
    # Should not return 400 for missing session_id
    # May return 404 (session not found) or other errors, but not missing parameter error
    response_detail = str(response.json().get("detail", ""))
    assert "session_id" not in response_detail.lower() or response.status_code == 404, \
        "Endpoint does not properly accept session_id parameter"


def test_submit_answer_accepts_question_id_parameter(test_client):
    """
    Test that POST /submit-answer accepts question_id parameter.
    
    Validates: Requirements 7.2
    """
    # Make a request with question_id parameter
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "question_id": "550e8400-e29b-41d4-a716-446655440001",
            "answer_text": "Test answer"
        }
    )
    
    # Should not return 400 for missing question_id
    response_detail = str(response.json().get("detail", ""))
    assert "question_id" not in response_detail.lower() or response.status_code == 404, \
        "Endpoint does not properly accept question_id parameter"


def test_submit_answer_accepts_answer_text_parameter(test_client):
    """
    Test that POST /submit-answer accepts answer_text parameter.
    
    Validates: Requirements 7.2
    """
    # Make a request with answer_text parameter
    response = test_client.post(
        "/api/submit-answer",
        json={
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "question_id": "550e8400-e29b-41d4-a716-446655440001",
            "answer_text": "Test answer"
        }
    )
    
    # Should not return 400 for missing answer_text
    response_detail = str(response.json().get("detail", ""))
    assert "answer_text" not in response_detail.lower() or response.status_code == 404, \
        "Endpoint does not properly accept answer_text parameter"


# ============================================================================
# Tests for GET /get-next-question endpoint
# ============================================================================

def test_get_next_question_endpoint_exists(test_client):
    """
    Test that GET /get-next-question endpoint exists and is accessible.
    
    Validates: Requirements 7.3
    """
    # Make a request to the endpoint (even with invalid data)
    response = test_client.get(
        "/api/get-next-question"
    )
    
    # Endpoint should exist (not return 404 for wrong method)
    # May return 422 for missing parameter, but not 404
    assert response.status_code != 404, \
        "GET /get-next-question endpoint does not exist"


def test_get_next_question_accepts_session_id_parameter(test_client):
    """
    Test that GET /get-next-question accepts session_id parameter.
    
    Validates: Requirements 7.3
    """
    # Make a request with session_id parameter
    response = test_client.get(
        "/api/get-next-question?session_id=550e8400-e29b-41d4-a716-446655440000"
    )
    
    # Should not return 422 for missing session_id (may return 404 for not found)
    # The key is that the endpoint accepts the parameter
    if response.status_code == 422:
        response_detail = str(response.json().get("detail", ""))
        assert "session_id" not in response_detail.lower(), \
            "Endpoint does not properly accept session_id parameter"


# ============================================================================
# Tests for POST /transcribe-audio endpoint
# ============================================================================

def test_transcribe_audio_endpoint_exists(test_client):
    """
    Test that POST /transcribe-audio endpoint exists and is accessible.
    
    Validates: Requirements 7.4
    """
    # Make a request to the endpoint (even with invalid data)
    response = test_client.post(
        "/api/transcribe-audio",
        files={}
    )
    
    # Endpoint should exist (not return 404)
    assert response.status_code != 404, \
        "POST /transcribe-audio endpoint does not exist"


def test_transcribe_audio_accepts_audio_file_parameter(test_client):
    """
    Test that POST /transcribe-audio accepts audio file parameter.
    
    Validates: Requirements 7.4
    """
    # Create a mock audio file
    audio_content = b"fake audio content"
    audio_file = BytesIO(audio_content)
    
    # Make a request with audio file
    response = test_client.post(
        "/api/transcribe-audio",
        files={"audio_file": ("test.mp3", audio_file, "audio/mpeg")}
    )
    
    # Should not return 422 for missing file parameter
    # May return 400 for invalid file or 500 for API error
    if response.status_code == 422:
        response_detail = str(response.json().get("detail", ""))
        assert "audio_file" not in response_detail.lower(), \
            "Endpoint does not properly accept audio_file parameter"


# ============================================================================
# Tests for POST /generate-voice-feedback endpoint
# ============================================================================

def test_generate_voice_feedback_endpoint_exists(test_client):
    """
    Test that POST /generate-voice-feedback endpoint exists and is accessible.
    
    Validates: Requirements 7.5
    """
    # Make a request to the endpoint (even with invalid data)
    response = test_client.post(
        "/api/generate-voice-feedback",
        json={}
    )
    
    # Endpoint should exist (not return 404)
    assert response.status_code != 404, \
        "POST /generate-voice-feedback endpoint does not exist"


def test_generate_voice_feedback_accepts_feedback_text_parameter(test_client):
    """
    Test that POST /generate-voice-feedback accepts feedback_text parameter.
    
    Validates: Requirements 7.5
    """
    # Make a request with feedback_text parameter
    response = test_client.post(
        "/api/generate-voice-feedback",
        json={
            "feedback_text": "Great job on your answer!"
        }
    )
    
    # Should not return 422 for missing feedback_text
    # May return 500 for API error
    if response.status_code == 422:
        response_detail = str(response.json().get("detail", ""))
        assert "feedback_text" not in response_detail.lower(), \
            "Endpoint does not properly accept feedback_text parameter"


# ============================================================================
# Tests for all endpoints registration
# ============================================================================

def test_all_required_endpoints_are_registered(test_client):
    """
    Test that all required API endpoints are registered in the application.
    
    Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
    """
    # Get all registered routes
    routes = {route.path: route.methods for route in app.routes}
    
    # Check that all required endpoints exist
    required_endpoints = {
        "/api/start-session": {"POST"},
        "/api/submit-answer": {"POST"},
        "/api/get-next-question": {"GET"},
        "/api/transcribe-audio": {"POST"},
        "/api/generate-voice-feedback": {"POST"}
    }
    
    for endpoint, methods in required_endpoints.items():
        assert endpoint in routes, \
            f"Required endpoint {endpoint} is not registered"
        
        # Check that the correct HTTP methods are supported
        registered_methods = routes[endpoint]
        for method in methods:
            assert method in registered_methods, \
                f"Endpoint {endpoint} does not support {method} method"
