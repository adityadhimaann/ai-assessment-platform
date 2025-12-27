"""
Unit tests for data model edge cases

This module tests specific edge cases for model validation:
- UUID validation edge cases
- Enum validation edge cases
- Required field validation edge cases

Requirements: 10.1, 10.2, 10.3
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models import (
    Difficulty,
    PerformanceRecord,
    Session,
    EvaluationResult,
    Question,
    StartSessionRequest,
    SubmitAnswerRequest,
    VoiceFeedbackRequest,
)


# ============================================================================
# UUID Validation Tests
# ============================================================================

class TestUUIDValidation:
    """Test UUID validation for session_id and question_id fields"""
    
    def test_session_with_invalid_uuid_format(self):
        """Test that Session rejects invalid UUID format"""
        with pytest.raises(ValidationError) as exc_info:
            Session(
                session_id="not-a-valid-uuid",
                topic="Test Topic",
                current_difficulty=Difficulty.MEDIUM
            )
        assert "session_id must be a valid UUID" in str(exc_info.value)
    
    def test_session_with_empty_uuid(self):
        """Test that Session rejects empty UUID"""
        with pytest.raises(ValidationError) as exc_info:
            Session(
                session_id="",
                topic="Test Topic",
                current_difficulty=Difficulty.MEDIUM
            )
        assert "session_id must be a valid UUID" in str(exc_info.value)
    
    def test_session_with_numeric_uuid(self):
        """Test that Session rejects numeric-only UUID"""
        with pytest.raises(ValidationError) as exc_info:
            Session(
                session_id="12345",
                topic="Test Topic",
                current_difficulty=Difficulty.MEDIUM
            )
        assert "session_id must be a valid UUID" in str(exc_info.value)
    
    def test_session_with_valid_uuid(self):
        """Test that Session accepts valid UUID format"""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        session = Session(
            session_id=valid_uuid,
            topic="Test Topic",
            current_difficulty=Difficulty.MEDIUM
        )
        assert session.session_id == valid_uuid
    
    def test_question_with_invalid_uuid_format(self):
        """Test that Question rejects invalid UUID format"""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                question_id="invalid-uuid-format",
                question_text="What is AI?",
                difficulty=Difficulty.EASY,
                topic="AI"
            )
        assert "question_id must be a valid UUID" in str(exc_info.value)
    
    def test_question_with_valid_uuid(self):
        """Test that Question accepts valid UUID format"""
        valid_uuid = "660e8400-e29b-41d4-a716-446655440001"
        question = Question(
            question_id=valid_uuid,
            question_text="What is AI?",
            difficulty=Difficulty.EASY,
            topic="AI"
        )
        assert question.question_id == valid_uuid
    
    def test_submit_answer_request_with_invalid_session_id(self):
        """Test that SubmitAnswerRequest rejects invalid session_id UUID"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitAnswerRequest(
                session_id="not-valid",
                question_id="660e8400-e29b-41d4-a716-446655440001",
                answer_text="Test answer"
            )
        assert "session_id must be a valid UUID" in str(exc_info.value)
    
    def test_submit_answer_request_with_invalid_question_id(self):
        """Test that SubmitAnswerRequest rejects invalid question_id UUID"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitAnswerRequest(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                question_id="not-valid",
                answer_text="Test answer"
            )
        assert "question_id must be a valid UUID" in str(exc_info.value)
    
    def test_submit_answer_request_with_both_valid_uuids(self):
        """Test that SubmitAnswerRequest accepts both valid UUIDs"""
        request = SubmitAnswerRequest(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            question_id="660e8400-e29b-41d4-a716-446655440001",
            answer_text="Test answer"
        )
        assert request.session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.question_id == "660e8400-e29b-41d4-a716-446655440001"


# ============================================================================
# Enum Validation Tests
# ============================================================================

class TestEnumValidation:
    """Test Difficulty enum validation across models"""
    
    def test_difficulty_enum_valid_values(self):
        """Test that Difficulty enum accepts valid values"""
        assert Difficulty.EASY == "Easy"
        assert Difficulty.MEDIUM == "Medium"
        assert Difficulty.HARD == "Hard"
    
    def test_session_with_invalid_difficulty_string(self):
        """Test that Session rejects invalid difficulty string"""
        with pytest.raises(ValidationError) as exc_info:
            Session(
                topic="Test Topic",
                current_difficulty="VeryHard"  # Invalid
            )
        assert "current_difficulty" in str(exc_info.value).lower()
    
    def test_session_with_lowercase_difficulty(self):
        """Test that Session rejects lowercase difficulty"""
        with pytest.raises(ValidationError) as exc_info:
            Session(
                topic="Test Topic",
                current_difficulty="easy"  # Should be "Easy"
            )
        assert "current_difficulty" in str(exc_info.value).lower()
    
    def test_session_with_valid_difficulty_enum(self):
        """Test that Session accepts valid Difficulty enum"""
        session = Session(
            topic="Test Topic",
            current_difficulty=Difficulty.MEDIUM
        )
        assert session.current_difficulty == Difficulty.MEDIUM
    
    def test_start_session_request_with_invalid_difficulty(self):
        """Test that StartSessionRequest rejects invalid difficulty"""
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest(
                topic="Test Topic",
                initial_difficulty="Impossible"
            )
        assert "initial_difficulty" in str(exc_info.value).lower()
    
    def test_start_session_request_with_valid_difficulty(self):
        """Test that StartSessionRequest accepts valid difficulty"""
        request = StartSessionRequest(
            topic="Test Topic",
            initial_difficulty=Difficulty.HARD
        )
        assert request.initial_difficulty == Difficulty.HARD
    
    def test_performance_record_with_invalid_difficulty(self):
        """Test that PerformanceRecord rejects invalid difficulty"""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceRecord(
                question_id="660e8400-e29b-41d4-a716-446655440001",
                score=85,
                is_correct=True,
                difficulty="SuperEasy"  # Invalid
            )
        assert "difficulty" in str(exc_info.value).lower()
    
    def test_evaluation_result_with_invalid_suggested_difficulty(self):
        """Test that EvaluationResult rejects invalid suggested_difficulty"""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationResult(
                score=85,
                is_correct=True,
                feedback_text="Good job!",
                suggested_difficulty="Extreme"  # Invalid
            )
        assert "suggested_difficulty" in str(exc_info.value).lower()
    
    def test_question_with_valid_difficulty(self):
        """Test that Question accepts valid difficulty"""
        question = Question(
            question_text="What is AI?",
            difficulty=Difficulty.EASY,
            topic="AI"
        )
        assert question.difficulty == Difficulty.EASY


# ============================================================================
# Required Field Validation Tests
# ============================================================================

class TestRequiredFieldValidation:
    """Test required field validation across models"""
    
    def test_session_missing_topic(self):
        """Test that Session requires topic field"""
        with pytest.raises(ValidationError) as exc_info:
            Session(current_difficulty=Difficulty.MEDIUM)
        assert "topic" in str(exc_info.value).lower()
    
    def test_session_missing_difficulty(self):
        """Test that Session requires current_difficulty field"""
        with pytest.raises(ValidationError) as exc_info:
            Session(topic="Test Topic")
        assert "current_difficulty" in str(exc_info.value).lower()
    
    def test_session_with_empty_topic(self):
        """Test that Session rejects empty topic"""
        with pytest.raises(ValidationError) as exc_info:
            Session(
                topic="",
                current_difficulty=Difficulty.MEDIUM
            )
        assert "topic" in str(exc_info.value).lower()
    
    def test_performance_record_missing_question_id(self):
        """Test that PerformanceRecord requires question_id"""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceRecord(
                score=85,
                is_correct=True,
                difficulty=Difficulty.MEDIUM
            )
        assert "question_id" in str(exc_info.value).lower()
    
    def test_performance_record_missing_score(self):
        """Test that PerformanceRecord requires score"""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceRecord(
                question_id="660e8400-e29b-41d4-a716-446655440001",
                is_correct=True,
                difficulty=Difficulty.MEDIUM
            )
        assert "score" in str(exc_info.value).lower()
    
    def test_performance_record_missing_is_correct(self):
        """Test that PerformanceRecord requires is_correct"""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceRecord(
                question_id="660e8400-e29b-41d4-a716-446655440001",
                score=85,
                difficulty=Difficulty.MEDIUM
            )
        assert "is_correct" in str(exc_info.value).lower()
    
    def test_evaluation_result_missing_score(self):
        """Test that EvaluationResult requires score"""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationResult(
                is_correct=True,
                feedback_text="Good job!",
                suggested_difficulty=Difficulty.HARD
            )
        assert "score" in str(exc_info.value).lower()
    
    def test_evaluation_result_missing_feedback_text(self):
        """Test that EvaluationResult requires feedback_text"""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationResult(
                score=85,
                is_correct=True,
                suggested_difficulty=Difficulty.HARD
            )
        assert "feedback_text" in str(exc_info.value).lower()
    
    def test_evaluation_result_with_empty_feedback_text(self):
        """Test that EvaluationResult rejects empty feedback_text"""
        with pytest.raises(ValidationError) as exc_info:
            EvaluationResult(
                score=85,
                is_correct=True,
                feedback_text="",
                suggested_difficulty=Difficulty.HARD
            )
        assert "feedback_text" in str(exc_info.value).lower()
    
    def test_question_missing_question_text(self):
        """Test that Question requires question_text"""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                difficulty=Difficulty.EASY,
                topic="AI"
            )
        assert "question_text" in str(exc_info.value).lower()
    
    def test_question_with_empty_question_text(self):
        """Test that Question rejects empty question_text"""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                question_text="",
                difficulty=Difficulty.EASY,
                topic="AI"
            )
        assert "question_text" in str(exc_info.value).lower()
    
    def test_question_missing_topic(self):
        """Test that Question requires topic"""
        with pytest.raises(ValidationError) as exc_info:
            Question(
                question_text="What is AI?",
                difficulty=Difficulty.EASY
            )
        assert "topic" in str(exc_info.value).lower()
    
    def test_start_session_request_missing_topic(self):
        """Test that StartSessionRequest requires topic"""
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest(initial_difficulty=Difficulty.MEDIUM)
        assert "topic" in str(exc_info.value).lower()
    
    def test_start_session_request_missing_initial_difficulty(self):
        """Test that StartSessionRequest requires initial_difficulty"""
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest(topic="Test Topic")
        assert "initial_difficulty" in str(exc_info.value).lower()
    
    def test_submit_answer_request_missing_session_id(self):
        """Test that SubmitAnswerRequest requires session_id"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitAnswerRequest(
                question_id="660e8400-e29b-41d4-a716-446655440001",
                answer_text="Test answer"
            )
        assert "session_id" in str(exc_info.value).lower()
    
    def test_submit_answer_request_missing_question_id(self):
        """Test that SubmitAnswerRequest requires question_id"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitAnswerRequest(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                answer_text="Test answer"
            )
        assert "question_id" in str(exc_info.value).lower()
    
    def test_submit_answer_request_missing_answer_text(self):
        """Test that SubmitAnswerRequest requires answer_text"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitAnswerRequest(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                question_id="660e8400-e29b-41d4-a716-446655440001"
            )
        assert "answer_text" in str(exc_info.value).lower()
    
    def test_submit_answer_request_with_empty_answer_text(self):
        """Test that SubmitAnswerRequest rejects empty answer_text"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitAnswerRequest(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                question_id="660e8400-e29b-41d4-a716-446655440001",
                answer_text=""
            )
        assert "answer_text" in str(exc_info.value).lower()
    
    def test_voice_feedback_request_missing_feedback_text(self):
        """Test that VoiceFeedbackRequest requires feedback_text"""
        with pytest.raises(ValidationError) as exc_info:
            VoiceFeedbackRequest()
        assert "feedback_text" in str(exc_info.value).lower()
    
    def test_voice_feedback_request_with_empty_feedback_text(self):
        """Test that VoiceFeedbackRequest rejects empty feedback_text"""
        with pytest.raises(ValidationError) as exc_info:
            VoiceFeedbackRequest(feedback_text="")
        assert "feedback_text" in str(exc_info.value).lower()


# ============================================================================
# Additional Edge Cases
# ============================================================================

class TestAdditionalEdgeCases:
    """Test additional edge cases for model validation"""
    
    def test_performance_record_score_below_minimum(self):
        """Test that PerformanceRecord rejects score below 0"""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceRecord(
                question_id="660e8400-e29b-41d4-a716-446655440001",
                score=-1,
                is_correct=False,
                difficulty=Difficulty.EASY
            )
        assert "score" in str(exc_info.value).lower()
    
    def test_performance_record_score_above_maximum(self):
        """Test that PerformanceRecord rejects score above 100"""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceRecord(
                question_id="660e8400-e29b-41d4-a716-446655440001",
                score=101,
                is_correct=True,
                difficulty=Difficulty.HARD
            )
        assert "score" in str(exc_info.value).lower()
    
    def test_performance_record_score_at_boundaries(self):
        """Test that PerformanceRecord accepts scores at boundaries (0 and 100)"""
        # Test score = 0
        record_min = PerformanceRecord(
            question_id="660e8400-e29b-41d4-a716-446655440001",
            score=0,
            is_correct=False,
            difficulty=Difficulty.EASY
        )
        assert record_min.score == 0
        
        # Test score = 100
        record_max = PerformanceRecord(
            question_id="660e8400-e29b-41d4-a716-446655440001",
            score=100,
            is_correct=True,
            difficulty=Difficulty.HARD
        )
        assert record_max.score == 100
    
    def test_evaluation_result_score_boundaries(self):
        """Test that EvaluationResult accepts scores at boundaries"""
        # Test score = 0
        result_min = EvaluationResult(
            score=0,
            is_correct=False,
            feedback_text="Needs improvement",
            suggested_difficulty=Difficulty.EASY
        )
        assert result_min.score == 0
        
        # Test score = 100
        result_max = EvaluationResult(
            score=100,
            is_correct=True,
            feedback_text="Perfect!",
            suggested_difficulty=Difficulty.HARD
        )
        assert result_max.score == 100
    
    def test_session_auto_generates_uuid(self):
        """Test that Session auto-generates a valid UUID if not provided"""
        session = Session(
            topic="Test Topic",
            current_difficulty=Difficulty.MEDIUM
        )
        # Verify it's a valid UUID format
        from uuid import UUID
        try:
            UUID(session.session_id)
            assert True
        except ValueError:
            pytest.fail("Session did not generate a valid UUID")
    
    def test_question_auto_generates_uuid(self):
        """Test that Question auto-generates a valid UUID if not provided"""
        question = Question(
            question_text="What is AI?",
            difficulty=Difficulty.EASY,
            topic="AI"
        )
        # Verify it's a valid UUID format
        from uuid import UUID
        try:
            UUID(question.question_id)
            assert True
        except ValueError:
            pytest.fail("Question did not generate a valid UUID")
    
    def test_start_session_request_topic_max_length(self):
        """Test that StartSessionRequest enforces topic max length"""
        long_topic = "A" * 201  # Exceeds max_length=200
        with pytest.raises(ValidationError) as exc_info:
            StartSessionRequest(
                topic=long_topic,
                initial_difficulty=Difficulty.MEDIUM
            )
        assert "topic" in str(exc_info.value).lower()
    
    def test_voice_feedback_request_max_length(self):
        """Test that VoiceFeedbackRequest enforces feedback_text max length"""
        long_feedback = "A" * 5001  # Exceeds max_length=5000
        with pytest.raises(ValidationError) as exc_info:
            VoiceFeedbackRequest(feedback_text=long_feedback)
        assert "feedback_text" in str(exc_info.value).lower()
