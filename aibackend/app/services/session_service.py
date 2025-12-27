"""
Session Service

This module manages assessment sessions including creation, retrieval,
performance tracking, and adaptive difficulty adjustment.
"""

from datetime import datetime
from typing import Dict
from uuid import uuid4

from app.models import Session, Difficulty, PerformanceRecord
from app.exceptions import SessionNotFoundError


class SessionService:
    """
    Service for managing assessment sessions.
    
    Handles session lifecycle, performance tracking, and adaptive difficulty
    adjustment based on student performance patterns.
    """
    
    def __init__(self):
        """Initialize the session service with in-memory storage."""
        self._sessions: Dict[str, Session] = {}
    
    def create_session(self, topic: str, initial_difficulty: Difficulty) -> str:
        """
        Create a new assessment session.
        
        Args:
            topic: The assessment topic
            initial_difficulty: Starting difficulty level
        
        Returns:
            The unique session ID (UUID string)
        
        Requirements: 1.1, 1.2
        """
        session_id = str(uuid4())
        session = Session(
            session_id=session_id,
            topic=topic,
            current_difficulty=initial_difficulty,
            performance_history=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self._sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Session:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: The session identifier
        
        Returns:
            The Session object
        
        Raises:
            SessionNotFoundError: If session_id does not exist
        
        Requirements: 1.3, 1.4
        """
        if session_id not in self._sessions:
            raise SessionNotFoundError(session_id)
        return self._sessions[session_id]
    
    def update_session_performance(
        self,
        session_id: str,
        question_id: str,
        score: int,
        is_correct: bool
    ) -> None:
        """
        Update session with new performance record.
        
        Args:
            session_id: The session identifier
            question_id: The question identifier
            score: Score from 0-100
            is_correct: Whether the answer was correct
        
        Raises:
            SessionNotFoundError: If session_id does not exist
        
        Requirements: 1.5, 3.4
        """
        session = self.get_session(session_id)
        
        # Create performance record
        record = PerformanceRecord(
            question_id=question_id,
            score=score,
            is_correct=is_correct,
            difficulty=session.current_difficulty,
            timestamp=datetime.utcnow()
        )
        
        # Add to history
        session.performance_history.append(record)
        
        # Calculate and update difficulty
        new_difficulty = self.calculate_new_difficulty(session_id)
        session.current_difficulty = new_difficulty
        
        # Update timestamp
        session.updated_at = datetime.utcnow()
    
    def calculate_new_difficulty(self, session_id: str) -> Difficulty:
        """
        Calculate new difficulty based on recent performance.
        
        Adaptive logic:
        - 2 consecutive correct at Medium (score >= 80) → Hard
        - 2 consecutive incorrect at Hard (score < 80) → Medium
        - 2 consecutive incorrect at Medium (score < 80) → Easy
        
        Args:
            session_id: The session identifier
        
        Returns:
            The new difficulty level
        
        Raises:
            SessionNotFoundError: If session_id does not exist
        
        Requirements: 3.1, 3.2, 3.3, 3.4
        """
        session = self.get_session(session_id)
        
        # If less than 2 questions answered, keep current difficulty
        if len(session.performance_history) < 2:
            return session.current_difficulty
        
        # Get last 2 performance records
        last_two = session.performance_history[-2:]
        
        # Check if both are at the same difficulty level
        if last_two[0].difficulty != last_two[1].difficulty:
            return session.current_difficulty
        
        # Use the difficulty level from the records (not current_difficulty)
        # because we want to adjust based on performance AT that level
        records_diff = last_two[0].difficulty
        both_correct = all(record.is_correct for record in last_two)
        both_incorrect = all(not record.is_correct for record in last_two)
        
        # Apply adaptive rules based on the difficulty of the last 2 records
        # Rule 1: Medium → Hard (2 consecutive correct at Medium)
        if records_diff == Difficulty.MEDIUM and both_correct:
            return Difficulty.HARD
        
        # Rule 2: Hard → Medium (2 consecutive incorrect at Hard)
        if records_diff == Difficulty.HARD and both_incorrect:
            return Difficulty.MEDIUM
        
        # Rule 3: Medium → Easy (2 consecutive incorrect at Medium)
        if records_diff == Difficulty.MEDIUM and both_incorrect:
            return Difficulty.EASY
        
        # No change needed
        return session.current_difficulty
    
    def get_current_difficulty(self, session_id: str) -> Difficulty:
        """
        Get the current difficulty level for a session.
        
        Args:
            session_id: The session identifier
        
        Returns:
            The current difficulty level
        
        Raises:
            SessionNotFoundError: If session_id does not exist
        
        Requirements: 3.5
        """
        session = self.get_session(session_id)
        return session.current_difficulty
