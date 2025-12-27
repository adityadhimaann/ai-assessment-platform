"""
Property-based tests for Question Service

Feature: ai-assessment-backend, Property 9: Question generation uses current session difficulty
Feature: ai-assessment-backend, Property 10: Generated questions have required fields

This module tests that question generation:
- Uses the current difficulty level from the session
- Passes the correct difficulty to the question generator
- Maintains consistency between session state and question generation
- Produces questions with all required fields populated

Validates: Requirements 3.5, 4.1, 4.3
"""

from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch

from app.services.question_service import QuestionService
from app.services.session_service import SessionService
from app.clients.openai_client import OpenAIClient
from app.models import Difficulty, Question
from config.settings import Settings


# ============================================================================
# Hypothesis Strategies
# ============================================================================

valid_topics = st.text(min_size=1, max_size=200)
valid_difficulties = st.sampled_from([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])


# ============================================================================
# Property Tests for Question Generation Difficulty Usage
# ============================================================================

@settings(max_examples=50)
@given(
    topic=valid_topics,
    initial_difficulty=valid_difficulties
)
def test_question_generation_uses_current_session_difficulty(topic, initial_difficulty):
    """
    Property: For any session, when generating the next question, the difficulty 
    level passed to the question generator should match the session's current 
    difficulty level.
    
    Feature: ai-assessment-backend, Property 9: Question generation uses current session difficulty
    Validates: Requirements 3.5, 4.1
    """
    # Create session service and a new session
    session_service = SessionService()
    session_id = session_service.create_session(topic, initial_difficulty)
    
    # Get the current difficulty from the session
    current_difficulty = session_service.get_current_difficulty(session_id)
    
    # Verify the current difficulty matches the initial difficulty
    assert current_difficulty == initial_difficulty, \
        f"Current difficulty {current_difficulty} should match initial difficulty {initial_difficulty}"
    
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method to capture the call
        mock_response = "What is a test question?"
        mock_openai_client.chat_completion = Mock(return_value=mock_response)
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate a question using the session's current difficulty
        question = question_service.generate_question(topic, current_difficulty)
        
        # Verify the question was generated
        assert isinstance(question, Question), \
            "Generated question should be a Question instance"
        
        # Verify the question has the correct difficulty
        assert question.difficulty == current_difficulty, \
            f"Question difficulty {question.difficulty} should match session difficulty {current_difficulty}"
        
        # Verify the question has the correct topic
        assert question.topic == topic, \
            f"Question topic '{question.topic}' should match session topic '{topic}'"
        
        # Verify the OpenAI client was called
        assert mock_openai_client.chat_completion.called, \
            "OpenAI client should have been called to generate the question"
        
        # Verify the prompt passed to OpenAI contains the correct difficulty
        call_args = mock_openai_client.chat_completion.call_args
        messages = call_args[1]["messages"]
        prompt = messages[1]["content"]
        
        # The prompt should contain the difficulty level
        assert current_difficulty.value in prompt, \
            f"Prompt should contain difficulty '{current_difficulty.value}', but got: {prompt}"


@settings(max_examples=50)
@given(
    topic=valid_topics,
    initial_difficulty=valid_difficulties,
    performance_sequence=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50),  # question_id
            st.integers(min_value=0, max_value=100),  # score
            st.booleans()  # is_correct
        ),
        min_size=1,
        max_size=5
    )
)
def test_question_generation_tracks_difficulty_changes(
    topic, initial_difficulty, performance_sequence
):
    """
    Property: For any session with performance history, when generating the next 
    question, the difficulty level should match the session's current difficulty 
    after adaptive adjustments.
    
    Feature: ai-assessment-backend, Property 9: Question generation uses current session difficulty
    Validates: Requirements 3.5, 4.1
    """
    # Create session service and a new session
    session_service = SessionService()
    session_id = session_service.create_session(topic, initial_difficulty)
    
    # Add performance records to potentially change difficulty
    for question_id, score, is_correct in performance_sequence:
        session_service.update_session_performance(
            session_id=session_id,
            question_id=question_id,
            score=score,
            is_correct=is_correct
        )
    
    # Get the current difficulty after adaptive adjustments
    current_difficulty = session_service.get_current_difficulty(session_id)
    
    # Verify the current difficulty is valid
    assert current_difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD], \
        f"Current difficulty should be a valid Difficulty enum value, but got {current_difficulty}"
    
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method
        mock_response = "What is another test question?"
        mock_openai_client.chat_completion = Mock(return_value=mock_response)
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate a question using the session's current difficulty
        question = question_service.generate_question(topic, current_difficulty)
        
        # Verify the question difficulty matches the session's current difficulty
        assert question.difficulty == current_difficulty, \
            f"Question difficulty {question.difficulty} should match session's current difficulty {current_difficulty}"
        
        # Verify the prompt contains the correct difficulty
        call_args = mock_openai_client.chat_completion.call_args
        messages = call_args[1]["messages"]
        prompt = messages[1]["content"]
        
        assert current_difficulty.value in prompt, \
            f"Prompt should contain difficulty '{current_difficulty.value}', but got: {prompt}"


@settings(max_examples=50)
@given(
    topic=valid_topics,
    session_difficulty=valid_difficulties,
    question_difficulty=valid_difficulties
)
def test_question_difficulty_must_match_session_difficulty(
    topic, session_difficulty, question_difficulty
):
    """
    Property: For any session with a specific difficulty level, questions should 
    only be generated at that difficulty level, not at other difficulty levels.
    
    Feature: ai-assessment-backend, Property 9: Question generation uses current session difficulty
    Validates: Requirements 3.5, 4.1
    """
    # Create session service and a new session
    session_service = SessionService()
    session_id = session_service.create_session(topic, session_difficulty)
    
    # Get the current difficulty from the session
    current_difficulty = session_service.get_current_difficulty(session_id)
    
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method
        mock_response = "What is a test question?"
        mock_openai_client.chat_completion = Mock(return_value=mock_response)
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate a question using the CORRECT difficulty (from session)
        correct_question = question_service.generate_question(topic, current_difficulty)
        
        # Verify the question has the correct difficulty
        assert correct_question.difficulty == current_difficulty, \
            f"Question generated with session difficulty should have difficulty {current_difficulty}"
        
        # If we try to generate a question with a DIFFERENT difficulty than the session,
        # the question will have that different difficulty (this is allowed by the API,
        # but the property states that we should ALWAYS use the session's difficulty)
        if question_difficulty != session_difficulty:
            wrong_question = question_service.generate_question(topic, question_difficulty)
            
            # This demonstrates that the question service respects the difficulty passed to it
            assert wrong_question.difficulty == question_difficulty, \
                f"Question generated with {question_difficulty} should have that difficulty"
            
            # The key property is: when following the correct workflow, we should
            # ALWAYS pass the session's current difficulty to generate_question
            # This test verifies that the question service correctly uses whatever
            # difficulty is passed to it, which means the caller (API endpoint)
            # MUST pass the session's current difficulty
            assert correct_question.difficulty != wrong_question.difficulty, \
                "Questions generated with different difficulties should have different difficulty values"


@settings(max_examples=50)
@given(
    topic=valid_topics,
    difficulty=valid_difficulties
)
def test_question_generation_prompt_reflects_session_difficulty(topic, difficulty):
    """
    Property: For any session difficulty level, the prompt sent to the AI should 
    explicitly include that difficulty level to ensure appropriate question generation.
    
    Feature: ai-assessment-backend, Property 9: Question generation uses current session difficulty
    Validates: Requirements 3.5, 4.1
    """
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method to capture the prompt
        mock_response = "What is a test question?"
        captured_prompts = []
        
        def capture_prompt(messages, **kwargs):
            captured_prompts.append(messages[1]["content"])
            return mock_response
        
        mock_openai_client.chat_completion = Mock(side_effect=capture_prompt)
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate a question
        question = question_service.generate_question(topic, difficulty)
        
        # Verify a prompt was captured
        assert len(captured_prompts) == 1, \
            "Should have captured exactly one prompt"
        
        prompt = captured_prompts[0]
        
        # Verify the prompt contains the difficulty level
        assert difficulty.value in prompt, \
            f"Prompt should contain difficulty '{difficulty.value}', but got: {prompt}"
        
        # Verify the prompt contains the topic
        assert topic in prompt, \
            f"Prompt should contain topic '{topic}', but got: {prompt}"
        
        # Verify the question object has the correct difficulty
        assert question.difficulty == difficulty, \
            f"Question difficulty {question.difficulty} should match requested difficulty {difficulty}"
        
        # Verify the question object has the correct topic
        assert question.topic == topic, \
            f"Question topic '{question.topic}' should match requested topic '{topic}'"



# ============================================================================
# Property Tests for Question Response Structure
# ============================================================================

@settings(max_examples=50)
@given(
    topic=valid_topics,
    difficulty=valid_difficulties
)
def test_generated_questions_have_required_fields(topic, difficulty):
    """
    Property: For any successfully generated question, the response should 
    contain a non-empty question_id and non-empty question_text.
    
    Feature: ai-assessment-backend, Property 10: Generated questions have required fields
    Validates: Requirements 4.3
    """
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method to return a valid question text
        mock_question_text = "What is a test question about the topic?"
        mock_openai_client.chat_completion = Mock(return_value=mock_question_text)
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate a question
        question = question_service.generate_question(topic, difficulty)
        
        # Verify the question is a Question instance
        assert isinstance(question, Question), \
            f"Generated question should be a Question instance, but got {type(question)}"
        
        # Property: question_id must be non-empty
        assert question.question_id is not None, \
            "Question ID should not be None"
        assert isinstance(question.question_id, str), \
            f"Question ID should be a string, but got {type(question.question_id)}"
        assert len(question.question_id) > 0, \
            "Question ID should be non-empty"
        
        # Property: question_text must be non-empty
        assert question.question_text is not None, \
            "Question text should not be None"
        assert isinstance(question.question_text, str), \
            f"Question text should be a string, but got {type(question.question_text)}"
        assert len(question.question_text) > 0, \
            "Question text should be non-empty"
        
        # Additional verification: question_id should be a valid UUID format
        from uuid import UUID
        try:
            UUID(question.question_id)
        except ValueError:
            raise AssertionError(
                f"Question ID should be a valid UUID format, but got: {question.question_id}"
            )
        
        # Additional verification: other required fields should also be present
        assert question.difficulty is not None, \
            "Question difficulty should not be None"
        assert question.difficulty == difficulty, \
            f"Question difficulty should match requested difficulty {difficulty}"
        
        assert question.topic is not None, \
            "Question topic should not be None"
        assert question.topic == topic, \
            f"Question topic should match requested topic '{topic}'"
        
        assert question.created_at is not None, \
            "Question created_at timestamp should not be None"


@settings(max_examples=50)
@given(
    topic=valid_topics,
    difficulty=valid_difficulties,
    question_text=st.text(min_size=1, max_size=500).filter(lambda s: len(s.strip()) > 0)
)
def test_generated_questions_preserve_response_text(topic, difficulty, question_text):
    """
    Property: For any valid question text returned by the AI, the Question 
    object should preserve that text exactly without modification.
    
    Feature: ai-assessment-backend, Property 10: Generated questions have required fields
    Validates: Requirements 4.3
    """
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method to return the specific question text
        mock_openai_client.chat_completion = Mock(return_value=question_text)
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate a question
        question = question_service.generate_question(topic, difficulty)
        
        # Property: The question text should be preserved exactly (after stripping)
        expected_text = question_text.strip()
        assert question.question_text == expected_text, \
            f"Question text should be '{expected_text}', but got '{question.question_text}'"
        
        # Property: All required fields should be present
        assert question.question_id is not None and len(question.question_id) > 0, \
            "Question ID should be non-empty"
        assert question.question_text is not None and len(question.question_text) > 0, \
            "Question text should be non-empty"


@settings(max_examples=50)
@given(
    topic=valid_topics,
    difficulty=valid_difficulties
)
def test_generated_questions_have_unique_ids(topic, difficulty):
    """
    Property: For any sequence of generated questions, each question should 
    have a unique question_id.
    
    Feature: ai-assessment-backend, Property 10: Generated questions have required fields
    Validates: Requirements 4.3
    """
    # Create a mock OpenAI client
    mock_settings = Mock(spec=Settings)
    mock_settings.openai_api_key = "test-api-key"
    mock_settings.gpt_model = "gpt-4o"
    
    with patch('app.clients.openai_client.OpenAI'):
        mock_openai_client = OpenAIClient(mock_settings)
        
        # Mock the chat_completion method
        mock_openai_client.chat_completion = Mock(return_value="What is a test question?")
        
        # Create question service
        question_service = QuestionService(mock_openai_client)
        
        # Generate multiple questions
        num_questions = 10
        questions = [
            question_service.generate_question(topic, difficulty)
            for _ in range(num_questions)
        ]
        
        # Property: All question IDs should be unique
        question_ids = [q.question_id for q in questions]
        unique_ids = set(question_ids)
        
        assert len(unique_ids) == num_questions, \
            f"Expected {num_questions} unique question IDs, but got {len(unique_ids)}"
        
        # Property: All questions should have non-empty IDs and text
        for i, question in enumerate(questions):
            assert question.question_id is not None and len(question.question_id) > 0, \
                f"Question {i} should have non-empty ID"
            assert question.question_text is not None and len(question.question_text) > 0, \
                f"Question {i} should have non-empty text"
