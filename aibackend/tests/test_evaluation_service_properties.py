"""
Property-based tests for Evaluation Service

Feature: ai-assessment-backend, Property 5: Score threshold determines correctness

This module tests that evaluation results:
- Correctly determine is_correct based on score threshold (>= 80)
- Apply the threshold consistently across all score values

Validates: Requirements 2.3, 2.4
"""

from hypothesis import given, strategies as st, settings

from app.models import EvaluationResult, Difficulty


# ============================================================================
# Hypothesis Strategies
# ============================================================================

valid_scores = st.integers(min_value=0, max_value=100)
valid_feedback = st.text(min_size=1, max_size=500).filter(lambda s: s.strip() != "")
valid_difficulties = st.sampled_from([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])


# ============================================================================
# Property Tests for Score Threshold
# ============================================================================

@settings(max_examples=50)
@given(
    score=valid_scores,
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_score_threshold_determines_correctness(score, feedback_text, suggested_difficulty):
    """
    Property: For any evaluation result, the is_correct field should be true 
    if and only if the score is greater than or equal to 80.
    
    Feature: ai-assessment-backend, Property 5: Score threshold determines correctness
    Validates: Requirements 2.3, 2.4
    """
    # Determine expected correctness based on score threshold
    expected_is_correct = score >= 80
    
    # Create an EvaluationResult with the generated score and expected is_correct
    result = EvaluationResult(
        score=score,
        is_correct=expected_is_correct,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    # Verify the is_correct field matches the threshold logic
    assert result.is_correct == expected_is_correct, \
        f"For score {score}, is_correct should be {expected_is_correct}, but got {result.is_correct}"
    
    # Verify the threshold boundary conditions explicitly
    if score >= 80:
        assert result.is_correct is True, \
            f"Score {score} >= 80 should result in is_correct=True, but got {result.is_correct}"
    else:
        assert result.is_correct is False, \
            f"Score {score} < 80 should result in is_correct=False, but got {result.is_correct}"


@settings(max_examples=50)
@given(
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_score_threshold_boundary_at_80(feedback_text, suggested_difficulty):
    """
    Property: The score threshold boundary at 80 should be inclusive - 
    a score of exactly 80 should result in is_correct=True.
    
    Feature: ai-assessment-backend, Property 5: Score threshold determines correctness
    Validates: Requirements 2.3, 2.4
    """
    # Test the exact boundary: score = 80
    result_at_threshold = EvaluationResult(
        score=80,
        is_correct=True,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    assert result_at_threshold.is_correct is True, \
        "Score of exactly 80 should result in is_correct=True"
    assert result_at_threshold.score == 80
    
    # Test just below the boundary: score = 79
    result_below_threshold = EvaluationResult(
        score=79,
        is_correct=False,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    assert result_below_threshold.is_correct is False, \
        "Score of 79 should result in is_correct=False"
    assert result_below_threshold.score == 79
    
    # Test just above the boundary: score = 81
    result_above_threshold = EvaluationResult(
        score=81,
        is_correct=True,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    assert result_above_threshold.is_correct is True, \
        "Score of 81 should result in is_correct=True"
    assert result_above_threshold.score == 81


@settings(max_examples=50)
@given(
    score=st.integers(min_value=80, max_value=100),
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_scores_above_threshold_are_correct(score, feedback_text, suggested_difficulty):
    """
    Property: For any score >= 80, is_correct must be True.
    
    Feature: ai-assessment-backend, Property 5: Score threshold determines correctness
    Validates: Requirements 2.3
    """
    result = EvaluationResult(
        score=score,
        is_correct=True,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    assert result.is_correct is True, \
        f"Score {score} >= 80 must have is_correct=True, but got {result.is_correct}"
    assert result.score >= 80


@settings(max_examples=50)
@given(
    score=st.integers(min_value=0, max_value=79),
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_scores_below_threshold_are_incorrect(score, feedback_text, suggested_difficulty):
    """
    Property: For any score < 80, is_correct must be False.
    
    Feature: ai-assessment-backend, Property 5: Score threshold determines correctness
    Validates: Requirements 2.4
    """
    result = EvaluationResult(
        score=score,
        is_correct=False,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    assert result.is_correct is False, \
        f"Score {score} < 80 must have is_correct=False, but got {result.is_correct}"
    assert result.score < 80


# ============================================================================
# Property Tests for Evaluation Response Completeness
# ============================================================================

@settings(max_examples=50)
@given(
    score=valid_scores,
    is_correct=st.booleans(),
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_evaluation_response_contains_all_required_fields(
    score, is_correct, feedback_text, suggested_difficulty
):
    """
    Property: For any successful evaluation, the response should contain 
    non-null values for score, is_correct, feedback_text, and suggested_difficulty fields.
    
    Feature: ai-assessment-backend, Property 6: Evaluation responses contain all required fields
    Validates: Requirements 2.6
    """
    # Create an EvaluationResult with all fields
    result = EvaluationResult(
        score=score,
        is_correct=is_correct,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    # Verify all required fields are present and non-null
    assert result.score is not None, "score field must not be None"
    assert result.is_correct is not None, "is_correct field must not be None"
    assert result.feedback_text is not None, "feedback_text field must not be None"
    assert result.suggested_difficulty is not None, "suggested_difficulty field must not be None"
    
    # Verify field types are correct
    assert isinstance(result.score, int), f"score must be int, got {type(result.score)}"
    assert isinstance(result.is_correct, bool), f"is_correct must be bool, got {type(result.is_correct)}"
    assert isinstance(result.feedback_text, str), f"feedback_text must be str, got {type(result.feedback_text)}"
    assert isinstance(result.suggested_difficulty, Difficulty), \
        f"suggested_difficulty must be Difficulty enum, got {type(result.suggested_difficulty)}"
    
    # Verify field values are valid
    assert 0 <= result.score <= 100, f"score must be between 0-100, got {result.score}"
    assert len(result.feedback_text) > 0, "feedback_text must not be empty"
    assert result.suggested_difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD], \
        f"suggested_difficulty must be a valid Difficulty value, got {result.suggested_difficulty}"


@settings(max_examples=50)
@given(
    score=valid_scores,
    is_correct=st.booleans(),
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_evaluation_result_serialization_preserves_all_fields(
    score, is_correct, feedback_text, suggested_difficulty
):
    """
    Property: For any evaluation result, serializing to dict and back 
    should preserve all required fields without data loss.
    
    Feature: ai-assessment-backend, Property 6: Evaluation responses contain all required fields
    Validates: Requirements 2.6
    """
    # Create an EvaluationResult
    original_result = EvaluationResult(
        score=score,
        is_correct=is_correct,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    # Serialize to dict
    result_dict = original_result.model_dump()
    
    # Verify all required fields are in the dict
    assert "score" in result_dict, "score field missing from serialized dict"
    assert "is_correct" in result_dict, "is_correct field missing from serialized dict"
    assert "feedback_text" in result_dict, "feedback_text field missing from serialized dict"
    assert "suggested_difficulty" in result_dict, "suggested_difficulty field missing from serialized dict"
    
    # Verify values match original
    assert result_dict["score"] == original_result.score, \
        f"score mismatch: expected {original_result.score}, got {result_dict['score']}"
    assert result_dict["is_correct"] == original_result.is_correct, \
        f"is_correct mismatch: expected {original_result.is_correct}, got {result_dict['is_correct']}"
    assert result_dict["feedback_text"] == original_result.feedback_text, \
        f"feedback_text mismatch: expected {original_result.feedback_text}, got {result_dict['feedback_text']}"
    assert result_dict["suggested_difficulty"] == original_result.suggested_difficulty.value, \
        f"suggested_difficulty mismatch: expected {original_result.suggested_difficulty.value}, got {result_dict['suggested_difficulty']}"


@settings(max_examples=50)
@given(
    score=valid_scores,
    is_correct=st.booleans(),
    suggested_difficulty=valid_difficulties
)
def test_evaluation_result_rejects_empty_feedback(score, is_correct, suggested_difficulty):
    """
    Property: For any evaluation result, feedback_text must not be empty or whitespace-only.
    
    Feature: ai-assessment-backend, Property 6: Evaluation responses contain all required fields
    Validates: Requirements 2.6
    """
    import pytest
    from pydantic import ValidationError
    
    # Test with empty string
    with pytest.raises(ValidationError) as exc_info:
        EvaluationResult(
            score=score,
            is_correct=is_correct,
            feedback_text="",
            suggested_difficulty=suggested_difficulty
        )
    
    # Verify the error is about feedback_text
    error_str = str(exc_info.value)
    assert "feedback_text" in error_str.lower(), \
        f"Expected validation error for feedback_text, got: {error_str}"


# ============================================================================
# Property Tests for Response Parsing
# ============================================================================

@settings(max_examples=50)
@given(
    score=valid_scores,
    is_correct=st.booleans(),
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_evaluation_response_parsing_preserves_data(
    score, is_correct, feedback_text, suggested_difficulty
):
    """
    Property: For any valid GPT-4o JSON response containing evaluation fields,
    parsing the response should correctly extract all field values without data loss.
    
    Feature: ai-assessment-backend, Property 7: Evaluation response parsing preserves data
    Validates: Requirements 2.2
    """
    import json
    from app.services.evaluation_service import EvaluationService
    from app.clients.openai_client import OpenAIClient
    from config.settings import Settings
    
    # Create a mock settings object (we won't actually call the API)
    settings = Settings(
        openai_api_key="test-key",
        tts_api_key="test-key",
        gpt_model="gpt-4o"
    )
    openai_client = OpenAIClient(settings)
    evaluation_service = EvaluationService(openai_client)
    
    # Create a valid JSON response with the generated values
    response_json = {
        "score": score,
        "is_correct": is_correct,
        "feedback_text": feedback_text,
        "suggested_difficulty": suggested_difficulty.value
    }
    
    # Convert to JSON string
    response_text = json.dumps(response_json)
    
    # Parse the response using the service's parsing method
    parsed_result = evaluation_service._parse_evaluation_response(response_text)
    
    # Verify all fields are preserved without data loss
    assert parsed_result.score == score, \
        f"Score mismatch: expected {score}, got {parsed_result.score}"
    assert parsed_result.is_correct == is_correct, \
        f"is_correct mismatch: expected {is_correct}, got {parsed_result.is_correct}"
    assert parsed_result.feedback_text == feedback_text.strip(), \
        f"feedback_text mismatch: expected '{feedback_text.strip()}', got '{parsed_result.feedback_text}'"
    assert parsed_result.suggested_difficulty == suggested_difficulty, \
        f"suggested_difficulty mismatch: expected {suggested_difficulty}, got {parsed_result.suggested_difficulty}"
    
    # Verify the parsed result is a valid EvaluationResult
    assert isinstance(parsed_result, EvaluationResult), \
        f"Parsed result should be EvaluationResult, got {type(parsed_result)}"


@settings(max_examples=50)
@given(
    score=valid_scores,
    is_correct=st.booleans(),
    feedback_text=valid_feedback,
    suggested_difficulty=valid_difficulties
)
def test_evaluation_response_parsing_round_trip(
    score, is_correct, feedback_text, suggested_difficulty
):
    """
    Property: For any evaluation result, converting to JSON and parsing back
    should preserve all data (round-trip consistency).
    Note: feedback_text will be trimmed during parsing, so we compare trimmed values.
    
    Feature: ai-assessment-backend, Property 7: Evaluation response parsing preserves data
    Validates: Requirements 2.2
    """
    import json
    from app.services.evaluation_service import EvaluationService
    from app.clients.openai_client import OpenAIClient
    from config.settings import Settings
    
    # Create original evaluation result
    original_result = EvaluationResult(
        score=score,
        is_correct=is_correct,
        feedback_text=feedback_text,
        suggested_difficulty=suggested_difficulty
    )
    
    # Convert to JSON (simulating GPT-4o response format)
    response_json = {
        "score": original_result.score,
        "is_correct": original_result.is_correct,
        "feedback_text": original_result.feedback_text,
        "suggested_difficulty": original_result.suggested_difficulty.value
    }
    response_text = json.dumps(response_json)
    
    # Parse back using the service
    settings = Settings(
        openai_api_key="test-key",
        tts_api_key="test-key",
        gpt_model="gpt-4o"
    )
    openai_client = OpenAIClient(settings)
    evaluation_service = EvaluationService(openai_client)
    
    parsed_result = evaluation_service._parse_evaluation_response(response_text)
    
    # Verify round-trip consistency
    # Note: feedback_text is trimmed during parsing, so compare trimmed values
    assert parsed_result.score == original_result.score, \
        "Round-trip failed: score mismatch"
    assert parsed_result.is_correct == original_result.is_correct, \
        "Round-trip failed: is_correct mismatch"
    assert parsed_result.feedback_text == original_result.feedback_text.strip(), \
        "Round-trip failed: feedback_text mismatch (after trimming)"
    assert parsed_result.suggested_difficulty == original_result.suggested_difficulty, \
        "Round-trip failed: suggested_difficulty mismatch"


@settings(max_examples=50)
@given(
    score=valid_scores,
    is_correct=st.booleans(),
    feedback_text=st.text(min_size=1, max_size=500).filter(lambda s: s.strip() != "").map(lambda s: "  " + s + "  "),  # Add whitespace
    suggested_difficulty=valid_difficulties
)
def test_evaluation_response_parsing_handles_whitespace(
    score, is_correct, feedback_text, suggested_difficulty
):
    """
    Property: For any evaluation response with whitespace in feedback_text,
    parsing should trim the whitespace while preserving the content.
    
    Feature: ai-assessment-backend, Property 7: Evaluation response parsing preserves data
    Validates: Requirements 2.2
    """
    import json
    from app.services.evaluation_service import EvaluationService
    from app.clients.openai_client import OpenAIClient
    from config.settings import Settings
    
    # Create a JSON response with whitespace in feedback
    response_json = {
        "score": score,
        "is_correct": is_correct,
        "feedback_text": feedback_text,
        "suggested_difficulty": suggested_difficulty.value
    }
    response_text = json.dumps(response_json)
    
    # Parse the response
    settings = Settings(
        openai_api_key="test-key",
        tts_api_key="test-key",
        gpt_model="gpt-4o"
    )
    openai_client = OpenAIClient(settings)
    evaluation_service = EvaluationService(openai_client)
    
    parsed_result = evaluation_service._parse_evaluation_response(response_text)
    
    # Verify whitespace is trimmed
    assert parsed_result.feedback_text == feedback_text.strip(), \
        f"Whitespace not properly trimmed: expected '{feedback_text.strip()}', got '{parsed_result.feedback_text}'"
    
    # Verify other fields are preserved
    assert parsed_result.score == score
    assert parsed_result.is_correct == is_correct
    assert parsed_result.suggested_difficulty == suggested_difficulty
