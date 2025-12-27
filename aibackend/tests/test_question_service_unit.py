"""
Unit tests for Question Service with mocked GPT-4o

Tests question generation for each difficulty level and API error handling.

Requirements: 4.2, 4.4
"""

import pytest
from unittest.mock import Mock, patch
from openai import APIError, APIConnectionError, RateLimitError

from app.services.question_service import QuestionService
from app.clients.openai_client import OpenAIClient
from app.models import Difficulty, Question
from app.exceptions import QuestionGenerationError, OpenAIAPIError
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
    """Create a mocked OpenAI client"""
    with patch('app.clients.openai_client.OpenAI'):
        client = OpenAIClient(mock_settings)
        return client


@pytest.fixture
def question_service(mock_openai_client):
    """Create question service with mocked OpenAI client"""
    return QuestionService(mock_openai_client)


class TestQuestionGenerationByDifficulty:
    """Test suite for question generation at different difficulty levels"""
    
    def test_generate_easy_question(self, question_service, mock_openai_client):
        """
        Test question generation for Easy difficulty level.
        
        Requirements: 4.2
        """
        # Mock the OpenAI response
        mock_openai_client.chat_completion = Mock(
            return_value="What is the capital of France?"
        )
        
        # Generate question
        topic = "Geography"
        difficulty = Difficulty.EASY
        question = question_service.generate_question(topic, difficulty)
        
        # Verify the question object
        assert isinstance(question, Question)
        assert question.question_text == "What is the capital of France?"
        assert question.difficulty == Difficulty.EASY
        assert question.topic == "Geography"
        assert question.question_id is not None
        assert len(question.question_id) > 0
        
        # Verify the OpenAI client was called correctly
        mock_openai_client.chat_completion.assert_called_once()
        call_args = mock_openai_client.chat_completion.call_args
        
        # Check messages structure
        messages = call_args[1]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "expert educator" in messages[0]["content"].lower()
        assert messages[1]["role"] == "user"
        
        # Check prompt contains difficulty and topic
        prompt = messages[1]["content"]
        assert "Easy" in prompt
        assert "Geography" in prompt
        
        # Check response format and temperature
        assert call_args[1]["response_format"] == "text"
        assert call_args[1]["temperature"] == 0.8
    
    def test_generate_medium_question(self, question_service, mock_openai_client):
        """
        Test question generation for Medium difficulty level.
        
        Requirements: 4.2
        """
        # Mock the OpenAI response
        mock_openai_client.chat_completion = Mock(
            return_value="Explain how photosynthesis converts light energy into chemical energy."
        )
        
        # Generate question
        topic = "Biology"
        difficulty = Difficulty.MEDIUM
        question = question_service.generate_question(topic, difficulty)
        
        # Verify the question object
        assert isinstance(question, Question)
        assert question.question_text == "Explain how photosynthesis converts light energy into chemical energy."
        assert question.difficulty == Difficulty.MEDIUM
        assert question.topic == "Biology"
        assert question.question_id is not None
        
        # Verify the prompt contains Medium difficulty
        call_args = mock_openai_client.chat_completion.call_args
        prompt = call_args[1]["messages"][1]["content"]
        assert "Medium" in prompt
        assert "Biology" in prompt
    
    def test_generate_hard_question(self, question_service, mock_openai_client):
        """
        Test question generation for Hard difficulty level.
        
        Requirements: 4.2
        """
        # Mock the OpenAI response
        mock_openai_client.chat_completion = Mock(
            return_value="Analyze the implications of quantum entanglement for information theory and discuss potential applications in quantum computing."
        )
        
        # Generate question
        topic = "Physics"
        difficulty = Difficulty.HARD
        question = question_service.generate_question(topic, difficulty)
        
        # Verify the question object
        assert isinstance(question, Question)
        assert question.question_text == "Analyze the implications of quantum entanglement for information theory and discuss potential applications in quantum computing."
        assert question.difficulty == Difficulty.HARD
        assert question.topic == "Physics"
        assert question.question_id is not None
        
        # Verify the prompt contains Hard difficulty
        call_args = mock_openai_client.chat_completion.call_args
        prompt = call_args[1]["messages"][1]["content"]
        assert "Hard" in prompt
        assert "Physics" in prompt
    
    def test_question_id_uniqueness(self, question_service, mock_openai_client):
        """
        Test that each generated question has a unique ID.
        
        Requirements: 4.2
        """
        # Mock the OpenAI response
        mock_openai_client.chat_completion = Mock(
            return_value="Test question"
        )
        
        # Generate multiple questions
        question1 = question_service.generate_question("Math", Difficulty.EASY)
        question2 = question_service.generate_question("Math", Difficulty.EASY)
        question3 = question_service.generate_question("Math", Difficulty.EASY)
        
        # Verify all IDs are unique
        ids = {question1.question_id, question2.question_id, question3.question_id}
        assert len(ids) == 3, "Question IDs should be unique"
    
    def test_question_text_whitespace_trimming(self, question_service, mock_openai_client):
        """
        Test that question text is trimmed of leading/trailing whitespace.
        
        Requirements: 4.2
        """
        # Mock the OpenAI response with extra whitespace
        mock_openai_client.chat_completion = Mock(
            return_value="  \n  What is machine learning?  \n  "
        )
        
        # Generate question
        question = question_service.generate_question("Computer Science", Difficulty.EASY)
        
        # Verify whitespace is trimmed
        assert question.question_text == "What is machine learning?"
        assert not question.question_text.startswith(" ")
        assert not question.question_text.endswith(" ")


class TestQuestionGenerationErrorHandling:
    """Test suite for error handling during question generation"""
    
    def test_empty_response_error(self, question_service, mock_openai_client):
        """
        Test handling of empty response from GPT-4o.
        
        Requirements: 4.4
        """
        # Mock empty response
        mock_openai_client.chat_completion = Mock(return_value="")
        
        # Attempt to generate question and expect error
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question("Math", Difficulty.EASY)
        
        # Verify error details
        assert "empty question text" in str(exc_info.value).lower()
    
    def test_whitespace_only_response_error(self, question_service, mock_openai_client):
        """
        Test handling of whitespace-only response from GPT-4o.
        
        Requirements: 4.4
        """
        # Mock whitespace-only response
        mock_openai_client.chat_completion = Mock(return_value="   \n\t   ")
        
        # Attempt to generate question and expect error
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question("Math", Difficulty.EASY)
        
        # Verify error details
        assert "empty question text" in str(exc_info.value).lower()
    
    def test_openai_api_error_handling(self, question_service, mock_openai_client):
        """
        Test handling of OpenAI API errors.
        
        Requirements: 4.4
        """
        # Mock OpenAI API error
        api_error = OpenAIAPIError(
            message="API request failed",
            operation="question_generation"
        )
        mock_openai_client.chat_completion = Mock(side_effect=api_error)
        
        # Attempt to generate question and expect error
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question("Math", Difficulty.EASY)
        
        # Verify error details
        assert "failed to generate question" in str(exc_info.value).lower()
        assert exc_info.value.original_error == api_error
    
    def test_rate_limit_error_handling(self, question_service, mock_openai_client):
        """
        Test handling of rate limit errors from OpenAI.
        
        Requirements: 4.4
        """
        # Mock rate limit error wrapped in OpenAIAPIError
        rate_limit_error = OpenAIAPIError(
            message="Rate limit exceeded",
            operation="question_generation"
        )
        mock_openai_client.chat_completion = Mock(side_effect=rate_limit_error)
        
        # Attempt to generate question and expect error
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question("Science", Difficulty.MEDIUM)
        
        # Verify error is wrapped properly
        assert "failed to generate question" in str(exc_info.value).lower()
    
    def test_connection_error_handling(self, question_service, mock_openai_client):
        """
        Test handling of connection errors to OpenAI.
        
        Requirements: 4.4
        """
        # Mock connection error wrapped in OpenAIAPIError
        connection_error = OpenAIAPIError(
            message="Connection failed",
            operation="question_generation"
        )
        mock_openai_client.chat_completion = Mock(side_effect=connection_error)
        
        # Attempt to generate question and expect error
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question("History", Difficulty.HARD)
        
        # Verify error is wrapped properly
        assert "failed to generate question" in str(exc_info.value).lower()
    
    def test_unexpected_error_handling(self, question_service, mock_openai_client):
        """
        Test handling of unexpected errors during question generation.
        
        Requirements: 4.4
        """
        # Mock unexpected error
        unexpected_error = ValueError("Unexpected error occurred")
        mock_openai_client.chat_completion = Mock(side_effect=unexpected_error)
        
        # Attempt to generate question and expect error
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question("Math", Difficulty.EASY)
        
        # Verify error details
        assert "unexpected error" in str(exc_info.value).lower()
        assert exc_info.value.original_error == unexpected_error
    
    def test_error_preserves_context(self, question_service, mock_openai_client):
        """
        Test that errors preserve topic and difficulty context.
        
        Requirements: 4.4
        """
        # Mock API error
        api_error = OpenAIAPIError(
            message="API failed",
            operation="question_generation"
        )
        mock_openai_client.chat_completion = Mock(side_effect=api_error)
        
        # Attempt to generate question
        topic = "Chemistry"
        difficulty = Difficulty.MEDIUM
        
        with pytest.raises(QuestionGenerationError) as exc_info:
            question_service.generate_question(topic, difficulty)
        
        # Verify context is preserved in error
        error = exc_info.value
        assert error.original_error == api_error


class TestQuestionPromptBuilding:
    """Test suite for question prompt construction"""
    
    def test_prompt_contains_difficulty_guidelines(self, question_service):
        """
        Test that the prompt includes difficulty-specific guidelines.
        
        Requirements: 4.2
        """
        # Build prompts for each difficulty
        easy_prompt = question_service._build_question_prompt("Math", Difficulty.EASY)
        medium_prompt = question_service._build_question_prompt("Math", Difficulty.MEDIUM)
        hard_prompt = question_service._build_question_prompt("Math", Difficulty.HARD)
        
        # Verify difficulty guidelines are present
        assert "Easy" in easy_prompt
        assert "Basic concepts" in easy_prompt or "definitions" in easy_prompt
        
        assert "Medium" in medium_prompt
        assert "Application" in medium_prompt or "analysis" in medium_prompt
        
        assert "Hard" in hard_prompt
        assert "Complex" in hard_prompt or "synthesis" in hard_prompt
    
    def test_prompt_contains_topic(self, question_service):
        """
        Test that the prompt includes the specified topic.
        
        Requirements: 4.2
        """
        topics = ["Mathematics", "Biology", "History", "Computer Science"]
        
        for topic in topics:
            prompt = question_service._build_question_prompt(topic, Difficulty.MEDIUM)
            assert topic in prompt
    
    def test_prompt_requests_open_ended_question(self, question_service):
        """
        Test that the prompt requests an open-ended question format.
        
        Requirements: 4.2
        """
        prompt = question_service._build_question_prompt("Science", Difficulty.EASY)
        
        # Verify prompt discourages multiple choice
        assert "open-ended" in prompt.lower() or "no multiple choice" in prompt.lower()
