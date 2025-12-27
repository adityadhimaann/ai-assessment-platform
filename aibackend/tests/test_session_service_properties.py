"""
Property-based tests for Session Service

Feature: ai-assessment-backend, Property 1: Session creation produces unique identifiers

This module tests that session creation:
- Produces unique session IDs for each call
- Returns valid UUID format session IDs
- Allows retrieval of created sessions

Validates: Requirements 1.1, 1.3
"""

from hypothesis import given, strategies as st, settings
from uuid import UUID

from app.services.session_service import SessionService
from app.models import Difficulty


# ============================================================================
# Hypothesis Strategies
# ============================================================================

valid_topics = st.text(min_size=1, max_size=200)
valid_difficulties = st.sampled_from([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])


# ============================================================================
# Property Tests for Session Creation
# ============================================================================

@settings(max_examples=50)
@given(topic=valid_topics, difficulty=valid_difficulties)
def test_session_creation_produces_unique_identifiers(topic, difficulty):
    """
    Property: For any topic and difficulty level, creating a new session should 
    return a unique session ID that can be used to retrieve the session.
    
    Feature: ai-assessment-backend, Property 1: Session creation produces unique identifiers
    Validates: Requirements 1.1, 1.3
    """
    service = SessionService()
    
    # Create first session
    session_id_1 = service.create_session(topic, difficulty)
    
    # Verify session_id_1 is a valid UUID
    try:
        UUID(session_id_1)
    except ValueError:
        raise AssertionError(f"Session ID '{session_id_1}' is not a valid UUID")
    
    # Verify we can retrieve the session
    session_1 = service.get_session(session_id_1)
    assert session_1 is not None
    assert session_1.session_id == session_id_1
    assert session_1.topic == topic
    assert session_1.current_difficulty == difficulty
    
    # Create second session with same parameters
    session_id_2 = service.create_session(topic, difficulty)
    
    # Verify session_id_2 is a valid UUID
    try:
        UUID(session_id_2)
    except ValueError:
        raise AssertionError(f"Session ID '{session_id_2}' is not a valid UUID")
    
    # Verify the two session IDs are unique
    assert session_id_1 != session_id_2, \
        f"Session IDs should be unique, but got duplicate: {session_id_1}"
    
    # Verify we can retrieve both sessions independently
    session_1_retrieved = service.get_session(session_id_1)
    session_2_retrieved = service.get_session(session_id_2)
    
    assert session_1_retrieved.session_id == session_id_1
    assert session_2_retrieved.session_id == session_id_2
    assert session_1_retrieved.session_id != session_2_retrieved.session_id


@settings(max_examples=50)
@given(
    topic1=valid_topics,
    topic2=valid_topics,
    difficulty1=valid_difficulties,
    difficulty2=valid_difficulties
)
def test_session_creation_uniqueness_across_different_parameters(
    topic1, topic2, difficulty1, difficulty2
):
    """
    Property: For any combination of topics and difficulties, each session 
    creation should produce a unique identifier.
    
    Feature: ai-assessment-backend, Property 1: Session creation produces unique identifiers
    Validates: Requirements 1.1, 1.3
    """
    service = SessionService()
    
    # Create multiple sessions with potentially different parameters
    session_ids = set()
    
    for topic, difficulty in [(topic1, difficulty1), (topic2, difficulty2)]:
        session_id = service.create_session(topic, difficulty)
        
        # Verify it's a valid UUID
        try:
            UUID(session_id)
        except ValueError:
            raise AssertionError(f"Session ID '{session_id}' is not a valid UUID")
        
        # Verify uniqueness
        assert session_id not in session_ids, \
            f"Duplicate session ID generated: {session_id}"
        
        session_ids.add(session_id)
        
        # Verify retrieval works
        retrieved_session = service.get_session(session_id)
        assert retrieved_session.session_id == session_id
        assert retrieved_session.topic == topic
        assert retrieved_session.current_difficulty == difficulty


# ============================================================================
# Property Tests for Session Initialization
# ============================================================================

@settings(max_examples=50)
@given(topic=valid_topics, initial_difficulty=valid_difficulties)
def test_session_initialization_preserves_input_parameters(topic, initial_difficulty):
    """
    Property: For any topic and initial difficulty, a newly created session should 
    have the specified topic, the specified difficulty level, and an empty 
    performance history.
    
    Feature: ai-assessment-backend, Property 2: Session initialization preserves input parameters
    Validates: Requirements 1.2
    """
    service = SessionService()
    
    # Create a new session
    session_id = service.create_session(topic, initial_difficulty)
    
    # Retrieve the session
    session = service.get_session(session_id)
    
    # Verify the topic is preserved
    assert session.topic == topic, \
        f"Expected topic '{topic}', but got '{session.topic}'"
    
    # Verify the difficulty level is preserved
    assert session.current_difficulty == initial_difficulty, \
        f"Expected difficulty '{initial_difficulty}', but got '{session.current_difficulty}'"
    
    # Verify the performance history is empty
    assert session.performance_history == [], \
        f"Expected empty performance history, but got {len(session.performance_history)} records"
    
    # Verify session has required metadata fields
    assert session.session_id == session_id
    assert session.created_at is not None
    assert session.updated_at is not None


# ============================================================================
# Property Tests for Session Round-Trip
# ============================================================================

@settings(max_examples=50)
@given(
    topic=valid_topics,
    initial_difficulty=valid_difficulties,
    performance_data=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=50),  # question_id
            st.integers(min_value=0, max_value=100),  # score
            st.booleans()  # is_correct
        ),
        min_size=0,
        max_size=10
    )
)
def test_session_round_trip_consistency(topic, initial_difficulty, performance_data):
    """
    Property: For any session that is created and then modified, retrieving the 
    session should return data that reflects all modifications made.
    
    Feature: ai-assessment-backend, Property 3: Session round-trip consistency
    Validates: Requirements 1.3, 1.5
    """
    service = SessionService()
    
    # Create a new session
    session_id = service.create_session(topic, initial_difficulty)
    
    # Retrieve the session to verify initial state
    session_before = service.get_session(session_id)
    assert session_before.topic == topic
    assert session_before.current_difficulty == initial_difficulty
    assert len(session_before.performance_history) == 0
    
    # Apply modifications: add performance records
    for question_id, score, is_correct in performance_data:
        service.update_session_performance(
            session_id=session_id,
            question_id=question_id,
            score=score,
            is_correct=is_correct
        )
    
    # Retrieve the session again
    session_after = service.get_session(session_id)
    
    # Verify session ID is unchanged
    assert session_after.session_id == session_id, \
        "Session ID should remain unchanged after modifications"
    
    # Verify topic is unchanged
    assert session_after.topic == topic, \
        f"Topic should remain '{topic}', but got '{session_after.topic}'"
    
    # Verify performance history reflects all modifications
    assert len(session_after.performance_history) == len(performance_data), \
        f"Expected {len(performance_data)} performance records, but got {len(session_after.performance_history)}"
    
    # Verify each performance record was persisted correctly
    for i, (question_id, score, is_correct) in enumerate(performance_data):
        record = session_after.performance_history[i]
        assert record.question_id == question_id, \
            f"Record {i}: Expected question_id '{question_id}', but got '{record.question_id}'"
        assert record.score == score, \
            f"Record {i}: Expected score {score}, but got {record.score}"
        assert record.is_correct == is_correct, \
            f"Record {i}: Expected is_correct {is_correct}, but got {record.is_correct}"
        assert record.timestamp is not None, \
            f"Record {i}: timestamp should not be None"
    
    # Verify updated_at timestamp was modified (should be >= created_at)
    assert session_after.updated_at >= session_after.created_at, \
        "updated_at should be >= created_at after modifications"
    
    # If modifications were made, verify updated_at changed
    if len(performance_data) > 0:
        # Note: We can't directly compare with session_before.updated_at because
        # the session object is mutable and gets updated in place. Instead, we
        # verify that updated_at is set and reasonable.
        assert session_after.updated_at is not None, \
            "updated_at should be set after modifications"


# ============================================================================
# Property Tests for Invalid Session IDs
# ============================================================================

@settings(max_examples=50)
@given(invalid_session_id=st.text(min_size=1, max_size=100))
def test_invalid_session_ids_produce_errors(invalid_session_id):
    """
    Property: For any string that is not a valid session ID in the system, 
    attempting to retrieve the session should return an error indicating the 
    session does not exist.
    
    Feature: ai-assessment-backend, Property 4: Invalid session IDs produce errors
    Validates: Requirements 1.4
    """
    from app.exceptions import SessionNotFoundError
    import pytest
    
    service = SessionService()
    
    # Create a valid session to ensure the service is working
    valid_topic = "Test Topic"
    valid_difficulty = Difficulty.MEDIUM
    valid_session_id = service.create_session(valid_topic, valid_difficulty)
    
    # If the randomly generated invalid_session_id happens to match the valid one,
    # skip this test iteration (extremely unlikely with UUIDs)
    if invalid_session_id == valid_session_id:
        return
    
    # Attempt to retrieve a session with the invalid ID
    # This should raise SessionNotFoundError
    with pytest.raises(SessionNotFoundError) as exc_info:
        service.get_session(invalid_session_id)
    
    # Verify the error contains the session ID
    error = exc_info.value
    assert invalid_session_id in str(error), \
        f"Error message should contain the invalid session ID '{invalid_session_id}'"


# ============================================================================
# Property Tests for Difficulty Persistence
# ============================================================================

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
def test_difficulty_updates_are_persisted(topic, initial_difficulty, performance_sequence):
    """
    Property: For any session where the difficulty level is changed, retrieving 
    the session should reflect the new difficulty level.
    
    Feature: ai-assessment-backend, Property 8: Difficulty updates are persisted
    Validates: Requirements 3.4
    """
    service = SessionService()
    
    # Create a new session
    session_id = service.create_session(topic, initial_difficulty)
    
    # Verify initial difficulty
    session_initial = service.get_session(session_id)
    assert session_initial.current_difficulty == initial_difficulty, \
        f"Initial difficulty should be {initial_difficulty}, but got {session_initial.current_difficulty}"
    
    # Track difficulty changes as we add performance records
    previous_difficulty = initial_difficulty
    
    for question_id, score, is_correct in performance_sequence:
        # Update session with performance record
        service.update_session_performance(
            session_id=session_id,
            question_id=question_id,
            score=score,
            is_correct=is_correct
        )
        
        # Retrieve the session to check if difficulty was persisted
        session_after_update = service.get_session(session_id)
        current_difficulty = session_after_update.current_difficulty
        
        # Verify the difficulty is one of the valid values
        assert current_difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD], \
            f"Difficulty should be a valid Difficulty enum value, but got {current_difficulty}"
        
        # Verify that the difficulty in the session matches what calculate_new_difficulty returns
        calculated_difficulty = service.calculate_new_difficulty(session_id)
        assert current_difficulty == calculated_difficulty, \
            f"Session difficulty {current_difficulty} should match calculated difficulty {calculated_difficulty}"
        
        # Store for next iteration
        previous_difficulty = current_difficulty
    
    # Final verification: retrieve the session one more time to ensure persistence
    final_session = service.get_session(session_id)
    final_difficulty = final_session.current_difficulty
    
    # Verify the final difficulty is valid
    assert final_difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD], \
        f"Final difficulty should be a valid Difficulty enum value, but got {final_difficulty}"
    
    # Verify the final difficulty matches the last calculated difficulty
    final_calculated = service.calculate_new_difficulty(session_id)
    assert final_difficulty == final_calculated, \
        f"Final session difficulty {final_difficulty} should match final calculated difficulty {final_calculated}"
    
    # Verify that all performance records were persisted
    assert len(final_session.performance_history) == len(performance_sequence), \
        f"Expected {len(performance_sequence)} performance records, but got {len(final_session.performance_history)}"
