"""
Unit tests for Evaluation Service with mocked GPT-4o

Tests evaluation with correct answers, incorrect answers, and API error handling.

Requirements: 2.1, 2.5
"""

import pytest
import json
from unittest.mock import Mock, patch

from app.services.evaluation_service import EvaluationService
from app.clients.openai_client import OpenAIClient
from app.models import EvaluationResult, Difficulty
from app.exceptions import EvaluationError, OpenAIAPIError
from config.settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing"""
    settings = Mock(spec=Settings)
    settings.openai_api_key = "test-api-key-123"
    settings.gpt_model = "gpt-4o"
    return settings


@pytest.fixture
def mock_openai_client(mock_settings):
    """Create a mock OpenAI client"""
    client = Mock(spec=OpenAIClient)
    client.settings = mock_settings
    return client


@pytest.fixture
def evaluation_service(mock_openai_client):
    """Create evaluation service with mocked OpenAI client"""
    return EvaluationService(mock_openai_client)


class TestEvaluationServiceCorrectAnswers:
    """Test suite for evaluating correct answers"""
    
    def test_evaluate_correct_answer_high_score(self, evaluation_service, mock_openai_client):
        """
        Test evaluation of a correct answer with high score (>= 80).
        
        Requirements: 2.1
        """
        # Mock GPT-4o response for a correct answer
        gpt_response = {
            "score": 95,
            "is_correct": True,
            "feedback_text": "Excellent answer! You demonstrated a thorough understanding of the topic.",
            "suggested_difficulty": "Hard"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="What is photosynthesis?",
            answer="Photosynthesis is the process by which plants convert light energy into chemical energy.",
            topic="Biology"
        )
        
        # Verify the result
        assert isinstance(result, EvaluationResult)
        assert result.score == 95
        assert result.is_correct is True
        assert "Excellent" in result.feedback_text
        assert result.suggested_difficulty == Difficulty.HARD
        
        # Verify OpenAI client was called correctly
        mock_openai_client.chat_completion.assert_called_once()
        call_args = mock_openai_client.chat_completion.call_args
        
        # Verify messages structure
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "expert educator" in messages[0]["content"].lower()
        assert messages[1]["role"] == "user"
        
        # Verify prompt contains question, answer, and topic
        prompt = messages[1]["content"]
        assert "photosynthesis" in prompt.lower()
        assert "Biology" in prompt
        
        # Verify JSON response format was requested
        assert call_args[1]["response_format"] == "json"
        assert call_args[1]["temperature"] == 0.3
    
    def test_evaluate_correct_answer_at_threshold(self, evaluation_service, mock_openai_client):
        """
        Test evaluation of a correct answer at the threshold (score = 80).
        
        Requirements: 2.1
        """
        # Mock GPT-4o response for answer at threshold
        gpt_response = {
            "score": 80,
            "is_correct": True,
            "feedback_text": "Good answer. You covered the main points.",
            "suggested_difficulty": "Medium"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="Explain Newton's first law",
            answer="An object at rest stays at rest unless acted upon by a force.",
            topic="Physics"
        )
        
        # Verify the result
        assert result.score == 80
        assert result.is_correct is True
        assert result.suggested_difficulty == Difficulty.MEDIUM
    
    def test_evaluate_correct_answer_suggests_hard(self, evaluation_service, mock_openai_client):
        """
        Test that high-scoring answers suggest Hard difficulty.
        
        Requirements: 2.1
        """
        # Mock GPT-4o response with score >= 90
        gpt_response = {
            "score": 92,
            "is_correct": True,
            "feedback_text": "Outstanding answer with excellent detail.",
            "suggested_difficulty": "Hard"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="Test question",
            answer="Test answer",
            topic="Test topic"
        )
        
        # Verify Hard difficulty is suggested
        assert result.score >= 90
        assert result.suggested_difficulty == Difficulty.HARD


class TestEvaluationServiceIncorrectAnswers:
    """Test suite for evaluating incorrect answers"""
    
    def test_evaluate_incorrect_answer_low_score(self, evaluation_service, mock_openai_client):
        """
        Test evaluation of an incorrect answer with low score (< 80).
        
        Requirements: 2.1
        """
        # Mock GPT-4o response for an incorrect answer
        gpt_response = {
            "score": 45,
            "is_correct": False,
            "feedback_text": "Your answer is partially correct but misses key concepts. "
                           "Review the relationship between energy and matter.",
            "suggested_difficulty": "Easy"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="What is E=mc²?",
            answer="It's about energy",
            topic="Physics"
        )
        
        # Verify the result
        assert isinstance(result, EvaluationResult)
        assert result.score == 45
        assert result.is_correct is False
        assert "partially correct" in result.feedback_text.lower()
        assert result.suggested_difficulty == Difficulty.EASY
    
    def test_evaluate_incorrect_answer_just_below_threshold(self, evaluation_service, mock_openai_client):
        """
        Test evaluation of an answer just below the threshold (score = 79).
        
        Requirements: 2.1
        """
        # Mock GPT-4o response for answer just below threshold
        gpt_response = {
            "score": 79,
            "is_correct": False,
            "feedback_text": "Close! You have the right idea but need more detail.",
            "suggested_difficulty": "Medium"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="Test question",
            answer="Test answer",
            topic="Test topic"
        )
        
        # Verify the result
        assert result.score == 79
        assert result.is_correct is False
        assert result.suggested_difficulty == Difficulty.MEDIUM
    
    def test_evaluate_incorrect_answer_zero_score(self, evaluation_service, mock_openai_client):
        """
        Test evaluation of a completely incorrect answer (score = 0).
        
        Requirements: 2.1
        """
        # Mock GPT-4o response for completely incorrect answer
        gpt_response = {
            "score": 0,
            "is_correct": False,
            "feedback_text": "This answer is incorrect. Please review the fundamental concepts.",
            "suggested_difficulty": "Easy"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="What is 2+2?",
            answer="5",
            topic="Mathematics"
        )
        
        # Verify the result
        assert result.score == 0
        assert result.is_correct is False
        assert result.suggested_difficulty == Difficulty.EASY
    
    def test_evaluate_incorrect_answer_suggests_easy(self, evaluation_service, mock_openai_client):
        """
        Test that low-scoring answers suggest Easy difficulty.
        
        Requirements: 2.1
        """
        # Mock GPT-4o response with score < 70
        gpt_response = {
            "score": 50,
            "is_correct": False,
            "feedback_text": "Needs improvement. Review the basics.",
            "suggested_difficulty": "Easy"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(gpt_response)
        
        # Evaluate an answer
        result = evaluation_service.evaluate_answer(
            question="Test question",
            answer="Test answer",
            topic="Test topic"
        )
        
        # Verify Easy difficulty is suggested
        assert result.score < 70
        assert result.suggested_difficulty == Difficulty.EASY


class TestEvaluationServiceAPIErrorHandling:
    """Test suite for API error handling"""
    
    def test_openai_api_error_propagation(self, evaluation_service, mock_openai_client):
        """
        Test that OpenAI API errors are properly caught and wrapped.
        
        Requirements: 2.5
        """
        # Mock OpenAI API error
        original_error = OpenAIAPIError(
            message="API rate limit exceeded",
            operation="chat_completion"
        )
        mock_openai_client.chat_completion.side_effect = original_error
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error details
        assert "failed to evaluate answer" in str(exc_info.value).lower()
        assert exc_info.value.details is not None
        # The original_error is stored as a string in details dict
        assert "original_error" in exc_info.value.details
        # But also as an attribute on the exception
        assert isinstance(exc_info.value.original_error, OpenAIAPIError)
    
    def test_invalid_json_response_error(self, evaluation_service, mock_openai_client):
        """
        Test handling of invalid JSON response from GPT-4o.
        
        Requirements: 2.5
        """
        # Mock invalid JSON response
        mock_openai_client.chat_completion.return_value = "This is not valid JSON"
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error details
        assert "failed to parse" in str(exc_info.value).lower() or "json" in str(exc_info.value).lower()
    
    def test_missing_required_fields_error(self, evaluation_service, mock_openai_client):
        """
        Test handling of response missing required fields.
        
        Requirements: 2.5
        """
        # Mock response missing feedback_text field
        incomplete_response = {
            "score": 85,
            "is_correct": True,
            "suggested_difficulty": "Medium"
            # Missing feedback_text
        }
        mock_openai_client.chat_completion.return_value = json.dumps(incomplete_response)
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error mentions missing fields
        assert "missing required fields" in str(exc_info.value).lower()
        assert "feedback_text" in str(exc_info.value).lower()
    
    def test_invalid_score_value_error(self, evaluation_service, mock_openai_client):
        """
        Test handling of invalid score value (out of range).
        
        Requirements: 2.5
        """
        # Mock response with invalid score
        invalid_response = {
            "score": 150,  # Invalid: > 100
            "is_correct": True,
            "feedback_text": "Good answer",
            "suggested_difficulty": "Medium"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(invalid_response)
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error mentions invalid score
        assert "invalid score" in str(exc_info.value).lower()
    
    def test_invalid_difficulty_value_error(self, evaluation_service, mock_openai_client):
        """
        Test handling of invalid difficulty value.
        
        Requirements: 2.5
        """
        # Mock response with invalid difficulty
        invalid_response = {
            "score": 85,
            "is_correct": True,
            "feedback_text": "Good answer",
            "suggested_difficulty": "VeryHard"  # Invalid difficulty
        }
        mock_openai_client.chat_completion.return_value = json.dumps(invalid_response)
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error mentions invalid difficulty
        assert "invalid suggested_difficulty" in str(exc_info.value).lower()
    
    def test_empty_feedback_text_error(self, evaluation_service, mock_openai_client):
        """
        Test handling of empty feedback text.
        
        Requirements: 2.5
        """
        # Mock response with empty feedback
        invalid_response = {
            "score": 85,
            "is_correct": True,
            "feedback_text": "",  # Empty feedback
            "suggested_difficulty": "Medium"
        }
        mock_openai_client.chat_completion.return_value = json.dumps(invalid_response)
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error mentions feedback_text
        assert "feedback_text" in str(exc_info.value).lower()
    
    def test_unexpected_exception_handling(self, evaluation_service, mock_openai_client):
        """
        Test handling of unexpected exceptions during evaluation.
        
        Requirements: 2.5
        """
        # Mock unexpected exception
        mock_openai_client.chat_completion.side_effect = ValueError("Unexpected error")
        
        # Attempt to evaluate and expect EvaluationError
        with pytest.raises(EvaluationError) as exc_info:
            evaluation_service.evaluate_answer(
                question="Test question",
                answer="Test answer",
                topic="Test topic"
            )
        
        # Verify error is wrapped in EvaluationError
        assert "unexpected error" in str(exc_info.value).lower()


class TestEvaluationServicePromptBuilding:
    """Test suite for evaluation prompt building"""
    
    def test_prompt_contains_all_required_elements(self, evaluation_service):
        """
        Test that the evaluation prompt contains all required elements.
        
        Requirements: 2.1
        """
        # Build a prompt
        prompt = evaluation_service._build_evaluation_prompt(
            question="What is the capital of France?",
            answer="Paris",
            topic="Geography"
        )
        
        # Verify prompt contains all required elements
        assert "Geography" in prompt
        assert "What is the capital of France?" in prompt
        assert "Paris" in prompt
        assert "score" in prompt.lower()
        assert "feedback" in prompt.lower()
        assert "json" in prompt.lower()
        assert "0-100" in prompt or "0 to 100" in prompt or "0 - 100" in prompt
    
    def test_prompt_includes_difficulty_guidance(self, evaluation_service):
        """
        Test that the prompt includes guidance for suggesting difficulty.
        
        Requirements: 2.1
        """
        # Build a prompt
        prompt = evaluation_service._build_evaluation_prompt(
            question="Test question",
            answer="Test answer",
            topic="Test topic"
        )
        
        # Verify prompt includes difficulty guidance
        assert "Easy" in prompt
        assert "Medium" in prompt
        assert "Hard" in prompt
        assert "suggested_difficulty" in prompt.lower() or "difficulty" in prompt.lower()


class TestEvaluationServiceResponseParsing:
    """Test suite for response parsing"""
    
    def test_parse_valid_response_all_difficulties(self, evaluation_service):
        """
        Test parsing valid responses for all difficulty levels.
        
        Requirements: 2.1
        """
        # Test Easy difficulty
        easy_response = json.dumps({
            "score": 60,
            "is_correct": False,
            "feedback_text": "Needs improvement",
            "suggested_difficulty": "Easy"
        })
        easy_result = evaluation_service._parse_evaluation_response(easy_response)
        assert easy_result.suggested_difficulty == Difficulty.EASY
        
        # Test Medium difficulty
        medium_response = json.dumps({
            "score": 75,
            "is_correct": False,
            "feedback_text": "Good effort",
            "suggested_difficulty": "Medium"
        })
        medium_result = evaluation_service._parse_evaluation_response(medium_response)
        assert medium_result.suggested_difficulty == Difficulty.MEDIUM
        
        # Test Hard difficulty
        hard_response = json.dumps({
            "score": 95,
            "is_correct": True,
            "feedback_text": "Excellent",
            "suggested_difficulty": "Hard"
        })
        hard_result = evaluation_service._parse_evaluation_response(hard_response)
        assert hard_result.suggested_difficulty == Difficulty.HARD
    
    def test_parse_response_trims_whitespace(self, evaluation_service):
        """
        Test that parsing trims whitespace from feedback text.
        
        Requirements: 2.1
        """
        # Response with whitespace in feedback
        response = json.dumps({
            "score": 85,
            "is_correct": True,
            "feedback_text": "  Good answer with whitespace  ",
            "suggested_difficulty": "Medium"
        })
        
        result = evaluation_service._parse_evaluation_response(response)
        
        # Verify whitespace is trimmed
        assert result.feedback_text == "Good answer with whitespace"
        assert not result.feedback_text.startswith(" ")
        assert not result.feedback_text.endswith(" ")
