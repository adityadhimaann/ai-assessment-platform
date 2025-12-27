"""
Unit tests for Session Service Adaptive Difficulty Logic

This module tests the specific adaptive difficulty transition scenarios:
- Medium to Hard transition (2 correct at Medium)
- Hard to Medium transition (2 incorrect at Hard)
- Medium to Easy transition (2 incorrect at Medium)

Validates: Requirements 3.1, 3.2, 3.3
"""

import pytest
from app.services.session_service import SessionService
from app.models import Difficulty


class TestAdaptiveDifficultyTransitions:
    """Test suite for adaptive difficulty transition logic."""
    
    def test_medium_to_hard_transition_two_correct_at_medium(self):
        """
        Test Medium to Hard transition (2 correct at Medium).
        
        Scenario:
        - Create a session at Medium difficulty
        - Submit two consecutive correct answers with scores >= 80
        - Verify difficulty increases to Hard
        
        Validates: Requirements 3.1
        """
        service = SessionService()
        
        # Create a session at Medium difficulty
        session_id = service.create_session(
            topic="Python Programming",
            initial_difficulty=Difficulty.MEDIUM
        )
        
        # Verify initial difficulty
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.MEDIUM
        
        # Submit first correct answer at Medium (score >= 80)
        service.update_session_performance(
            session_id=session_id,
            question_id="q1",
            score=85,
            is_correct=True
        )
        
        # After first correct answer, difficulty should still be Medium
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.MEDIUM, \
            "Difficulty should remain Medium after first correct answer"
        
        # Submit second correct answer at Medium (score >= 80)
        service.update_session_performance(
            session_id=session_id,
            question_id="q2",
            score=90,
            is_correct=True
        )
        
        # After two consecutive correct answers at Medium, difficulty should increase to Hard
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.HARD, \
            "Difficulty should increase to Hard after two consecutive correct answers at Medium"
        
        # Verify performance history
        assert len(session.performance_history) == 2
        assert session.performance_history[0].is_correct is True
        assert session.performance_history[0].difficulty == Difficulty.MEDIUM
        assert session.performance_history[1].is_correct is True
        assert session.performance_history[1].difficulty == Difficulty.MEDIUM
    
    def test_hard_to_medium_transition_two_incorrect_at_hard(self):
        """
        Test Hard to Medium transition (2 incorrect at Hard).
        
        Scenario:
        - Create a session at Hard difficulty
        - Submit two consecutive incorrect answers with scores < 80
        - Verify difficulty decreases to Medium
        
        Validates: Requirements 3.2
        """
        service = SessionService()
        
        # Create a session at Hard difficulty
        session_id = service.create_session(
            topic="Advanced Algorithms",
            initial_difficulty=Difficulty.HARD
        )
        
        # Verify initial difficulty
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.HARD
        
        # Submit first incorrect answer at Hard (score < 80)
        service.update_session_performance(
            session_id=session_id,
            question_id="q1",
            score=45,
            is_correct=False
        )
        
        # After first incorrect answer, difficulty should still be Hard
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.HARD, \
            "Difficulty should remain Hard after first incorrect answer"
        
        # Submit second incorrect answer at Hard (score < 80)
        service.update_session_performance(
            session_id=session_id,
            question_id="q2",
            score=60,
            is_correct=False
        )
        
        # After two consecutive incorrect answers at Hard, difficulty should decrease to Medium
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.MEDIUM, \
            "Difficulty should decrease to Medium after two consecutive incorrect answers at Hard"
        
        # Verify performance history
        assert len(session.performance_history) == 2
        assert session.performance_history[0].is_correct is False
        assert session.performance_history[0].difficulty == Difficulty.HARD
        assert session.performance_history[1].is_correct is False
        assert session.performance_history[1].difficulty == Difficulty.HARD
    
    def test_medium_to_easy_transition_two_incorrect_at_medium(self):
        """
        Test Medium to Easy transition (2 incorrect at Medium).
        
        Scenario:
        - Create a session at Medium difficulty
        - Submit two consecutive incorrect answers with scores < 80
        - Verify difficulty decreases to Easy
        
        Validates: Requirements 3.3
        """
        service = SessionService()
        
        # Create a session at Medium difficulty
        session_id = service.create_session(
            topic="Basic Mathematics",
            initial_difficulty=Difficulty.MEDIUM
        )
        
        # Verify initial difficulty
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.MEDIUM
        
        # Submit first incorrect answer at Medium (score < 80)
        service.update_session_performance(
            session_id=session_id,
            question_id="q1",
            score=50,
            is_correct=False
        )
        
        # After first incorrect answer, difficulty should still be Medium
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.MEDIUM, \
            "Difficulty should remain Medium after first incorrect answer"
        
        # Submit second incorrect answer at Medium (score < 80)
        service.update_session_performance(
            session_id=session_id,
            question_id="q2",
            score=65,
            is_correct=False
        )
        
        # After two consecutive incorrect answers at Medium, difficulty should decrease to Easy
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.EASY, \
            "Difficulty should decrease to Easy after two consecutive incorrect answers at Medium"
        
        # Verify performance history
        assert len(session.performance_history) == 2
        assert session.performance_history[0].is_correct is False
        assert session.performance_history[0].difficulty == Difficulty.MEDIUM
        assert session.performance_history[1].is_correct is False
        assert session.performance_history[1].difficulty == Difficulty.MEDIUM
    
    def test_no_transition_with_mixed_results(self):
        """
        Test that difficulty does not change with mixed correct/incorrect results.
        
        This ensures the adaptive logic only triggers on consecutive results.
        """
        service = SessionService()
        
        # Create a session at Medium difficulty
        session_id = service.create_session(
            topic="General Knowledge",
            initial_difficulty=Difficulty.MEDIUM
        )
        
        # Submit correct then incorrect
        service.update_session_performance(
            session_id=session_id,
            question_id="q1",
            score=85,
            is_correct=True
        )
        
        service.update_session_performance(
            session_id=session_id,
            question_id="q2",
            score=50,
            is_correct=False
        )
        
        # Difficulty should remain Medium (no consecutive pattern)
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.MEDIUM, \
            "Difficulty should remain Medium with mixed results"
    
    def test_no_transition_at_easy_with_incorrect_answers(self):
        """
        Test that difficulty does not decrease below Easy.
        
        Ensures the system handles the lower boundary correctly.
        """
        service = SessionService()
        
        # Create a session at Easy difficulty
        session_id = service.create_session(
            topic="Basic Concepts",
            initial_difficulty=Difficulty.EASY
        )
        
        # Submit two consecutive incorrect answers
        service.update_session_performance(
            session_id=session_id,
            question_id="q1",
            score=40,
            is_correct=False
        )
        
        service.update_session_performance(
            session_id=session_id,
            question_id="q2",
            score=35,
            is_correct=False
        )
        
        # Difficulty should remain Easy (cannot go lower)
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.EASY, \
            "Difficulty should remain Easy (cannot decrease below Easy)"
    
    def test_no_transition_at_hard_with_correct_answers(self):
        """
        Test that difficulty does not increase above Hard.
        
        Ensures the system handles the upper boundary correctly.
        """
        service = SessionService()
        
        # Create a session at Hard difficulty
        session_id = service.create_session(
            topic="Expert Topics",
            initial_difficulty=Difficulty.HARD
        )
        
        # Submit two consecutive correct answers
        service.update_session_performance(
            session_id=session_id,
            question_id="q1",
            score=95,
            is_correct=True
        )
        
        service.update_session_performance(
            session_id=session_id,
            question_id="q2",
            score=98,
            is_correct=True
        )
        
        # Difficulty should remain Hard (cannot go higher)
        session = service.get_session(session_id)
        assert session.current_difficulty == Difficulty.HARD, \
            "Difficulty should remain Hard (cannot increase above Hard)"
