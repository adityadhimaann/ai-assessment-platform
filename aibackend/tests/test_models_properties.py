"""
Property-based tests for data model validation

Feature: ai-assessment-backend, Property 16: Comprehensive input validation

This module tests that API requests properly validate:
- Required fields are present
- Difficulty values are one of Easy/Medium/Hard
- Session IDs and Question IDs are valid UUID format
- Invalid inputs return 422 validation errors

Validates: Requirements 10.1, 10.2, 10.3, 10.5, 7.6
"""

from uuid import uuid4
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError
import pytest

from app.models import (
    StartSessionRequest,
    SubmitAnswerRequest,
    VoiceFeedbackRequest,
    Difficulty,
    Session,
    Question,
)


# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Valid strategies
valid_difficulties = st.sampled_from([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
valid_uuids = st.builds(lambda: str(uuid4()))
valid_topics = st.text(min_size=1, max_size=200)
valid_answer_text = st.text(min_size=1, max_size=5000)
valid_feedback_text = st.text(min_size=1, max_size=5000)

# Invalid strategies
invalid_difficulties = st.text().filter(lambda x: x not in ["Easy", "Medium", "Hard"])
invalid_uuids = st.one_of(
    st.text().filter(lambda x: x and not _is_valid_uuid(x)),
    st.just(""),
    st.just("not-a-uuid"),
    st.just("12345"),
    st.just("invalid-uuid-format"),
)
empty_strings = st.just("")


def _is_valid_uuid(s: str) -> bool:
    """Helper to check if a string is a valid UUID"""
    try:
        from uuid import UUID
        UUID(s)
        return True
    except (ValueError, AttributeError):
        return False


# ============================================================================
# Property Tests for StartSessionRequest
# ============================================================================

@settings(max_examples=50)
@given(topic=valid_topics, difficulty=valid_difficulties)
def test_start_session_request_accepts_valid_inputs(topic, difficulty):
    """
    Property: For any valid topic and difficulty, StartSessionRequest should accept the input.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1, 10.2
    """
    request = StartSessionRequest(topic=topic, initial_difficulty=difficulty)
    assert request.topic == topic
    assert request.initial_difficulty == difficulty


@settings(max_examples=50)
@given(difficulty=valid_difficulties)
def test_start_session_request_rejects_missing_topic(difficulty):
    """
    Property: For any request missing the topic field, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises((ValidationError, TypeError)):
        StartSessionRequest(initial_difficulty=difficulty)


@settings(max_examples=50)
@given(topic=valid_topics)
def test_start_session_request_rejects_missing_difficulty(topic):
    """
    Property: For any request missing the initial_difficulty field, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises((ValidationError, TypeError)):
        StartSessionRequest(topic=topic)


@settings(max_examples=50)
@given(topic=valid_topics, invalid_difficulty=invalid_difficulties)
def test_start_session_request_rejects_invalid_difficulty(topic, invalid_difficulty):
    """
    Property: For any invalid difficulty value, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.2
    """
    with pytest.raises(ValidationError):
        StartSessionRequest(topic=topic, initial_difficulty=invalid_difficulty)


@settings(max_examples=50)
@given(topic=empty_strings, difficulty=valid_difficulties)
def test_start_session_request_rejects_empty_topic(topic, difficulty):
    """
    Property: For any empty topic, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises(ValidationError):
        StartSessionRequest(topic=topic, initial_difficulty=difficulty)


# ============================================================================
# Property Tests for SubmitAnswerRequest
# ============================================================================

@settings(max_examples=50)
@given(
    session_id=valid_uuids,
    question_id=valid_uuids,
    answer_text=valid_answer_text
)
def test_submit_answer_request_accepts_valid_inputs(session_id, question_id, answer_text):
    """
    Property: For any valid session_id, question_id, and answer_text, SubmitAnswerRequest should accept the input.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1, 10.3
    """
    request = SubmitAnswerRequest(
        session_id=session_id,
        question_id=question_id,
        answer_text=answer_text
    )
    assert request.session_id == session_id
    assert request.question_id == question_id
    assert request.answer_text == answer_text


@settings(max_examples=50)
@given(
    invalid_session_id=invalid_uuids,
    question_id=valid_uuids,
    answer_text=valid_answer_text
)
def test_submit_answer_request_rejects_invalid_session_id(invalid_session_id, question_id, answer_text):
    """
    Property: For any invalid session_id format, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.3
    """
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(
            session_id=invalid_session_id,
            question_id=question_id,
            answer_text=answer_text
        )


@settings(max_examples=50)
@given(
    session_id=valid_uuids,
    invalid_question_id=invalid_uuids,
    answer_text=valid_answer_text
)
def test_submit_answer_request_rejects_invalid_question_id(session_id, invalid_question_id, answer_text):
    """
    Property: For any invalid question_id format, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.3
    """
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(
            session_id=session_id,
            question_id=invalid_question_id,
            answer_text=answer_text
        )


@settings(max_examples=50)
@given(
    session_id=valid_uuids,
    question_id=valid_uuids,
    empty_answer=empty_strings
)
def test_submit_answer_request_rejects_empty_answer(session_id, question_id, empty_answer):
    """
    Property: For any empty answer_text, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(
            session_id=session_id,
            question_id=question_id,
            answer_text=empty_answer
        )


@settings(max_examples=50)
@given(question_id=valid_uuids, answer_text=valid_answer_text)
def test_submit_answer_request_rejects_missing_session_id(question_id, answer_text):
    """
    Property: For any request missing session_id, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises((ValidationError, TypeError)):
        SubmitAnswerRequest(question_id=question_id, answer_text=answer_text)


# ============================================================================
# Property Tests for VoiceFeedbackRequest
# ============================================================================

@settings(max_examples=50)
@given(feedback_text=valid_feedback_text)
def test_voice_feedback_request_accepts_valid_inputs(feedback_text):
    """
    Property: For any valid feedback_text, VoiceFeedbackRequest should accept the input.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    request = VoiceFeedbackRequest(feedback_text=feedback_text)
    assert request.feedback_text == feedback_text


@settings(max_examples=50)
@given(empty_feedback=empty_strings)
def test_voice_feedback_request_rejects_empty_feedback(empty_feedback):
    """
    Property: For any empty feedback_text, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises(ValidationError):
        VoiceFeedbackRequest(feedback_text=empty_feedback)


def test_voice_feedback_request_rejects_missing_feedback():
    """
    Property: For any request missing feedback_text, validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1
    """
    with pytest.raises((ValidationError, TypeError)):
        VoiceFeedbackRequest()


# ============================================================================
# Property Tests for Session Model
# ============================================================================

@settings(max_examples=50)
@given(topic=valid_topics, difficulty=valid_difficulties)
def test_session_model_accepts_valid_inputs(topic, difficulty):
    """
    Property: For any valid topic and difficulty, Session model should accept the input.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1, 10.2
    """
    session = Session(topic=topic, current_difficulty=difficulty)
    assert session.topic == topic
    assert session.current_difficulty == difficulty
    assert _is_valid_uuid(session.session_id)


@settings(max_examples=50)
@given(invalid_session_id=invalid_uuids, topic=valid_topics, difficulty=valid_difficulties)
def test_session_model_rejects_invalid_session_id(invalid_session_id, topic, difficulty):
    """
    Property: For any invalid session_id format, Session validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.3
    """
    with pytest.raises(ValidationError):
        Session(session_id=invalid_session_id, topic=topic, current_difficulty=difficulty)


# ============================================================================
# Property Tests for Question Model
# ============================================================================

@settings(max_examples=50)
@given(
    question_text=valid_answer_text,
    difficulty=valid_difficulties,
    topic=valid_topics
)
def test_question_model_accepts_valid_inputs(question_text, difficulty, topic):
    """
    Property: For any valid question_text, difficulty, and topic, Question model should accept the input.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.1, 10.2
    """
    question = Question(question_text=question_text, difficulty=difficulty, topic=topic)
    assert question.question_text == question_text
    assert question.difficulty == difficulty
    assert question.topic == topic
    assert _is_valid_uuid(question.question_id)


@settings(max_examples=50)
@given(
    invalid_question_id=invalid_uuids,
    question_text=valid_answer_text,
    difficulty=valid_difficulties,
    topic=valid_topics
)
def test_question_model_rejects_invalid_question_id(invalid_question_id, question_text, difficulty, topic):
    """
    Property: For any invalid question_id format, Question validation should fail.
    
    Feature: ai-assessment-backend, Property 16: Comprehensive input validation
    Validates: Requirements 10.3
    """
    with pytest.raises(ValidationError):
        Question(
            question_id=invalid_question_id,
            question_text=question_text,
            difficulty=difficulty,
            topic=topic
        )
