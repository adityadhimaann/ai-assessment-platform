"""
Data Models

This module defines all Pydantic models for the AI Assessment Backend.
Models include domain entities, API request/response schemas, and validation logic.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enumerations
# ============================================================================

class Difficulty(str, Enum):
    """Question difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


# ============================================================================
# Domain Models
# ============================================================================

class PerformanceRecord(BaseModel):
    """
    Record of a single question attempt.
    
    Tracks the student's performance on a specific question including
    score, correctness, and difficulty level.
    """
    question_id: str = Field(..., description="Unique identifier for the question")
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    is_correct: bool = Field(..., description="Whether the answer was correct (score >= 80)")
    difficulty: Difficulty = Field(..., description="Difficulty level of the question")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the answer was submitted")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "550e8400-e29b-41d4-a716-446655440000",
                "score": 85,
                "is_correct": True,
                "difficulty": "Medium",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class Session(BaseModel):
    """
    Assessment session tracking student progress.
    
    Maintains session state including topic, current difficulty,
    and performance history for adaptive difficulty adjustment.
    """
    session_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique session identifier (UUID)"
    )
    topic: str = Field(..., min_length=1, description="Assessment topic")
    current_difficulty: Difficulty = Field(..., description="Current difficulty level")
    performance_history: List[PerformanceRecord] = Field(
        default_factory=list,
        description="History of question attempts"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session_id is a valid UUID format"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"session_id must be a valid UUID, got: {v}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "topic": "Artificial Intelligence",
                "current_difficulty": "Medium",
                "performance_history": [],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }


class EvaluationResult(BaseModel):
    """
    Result of answer evaluation by AI.
    
    Contains score, correctness determination, feedback text,
    and suggested difficulty for the next question.
    """
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    is_correct: bool = Field(..., description="Whether answer is correct (score >= 80)")
    feedback_text: str = Field(..., min_length=1, description="Detailed feedback on the answer")
    suggested_difficulty: Difficulty = Field(..., description="Suggested difficulty for next question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 85,
                "is_correct": True,
                "feedback_text": "Great answer! You correctly identified the key concepts...",
                "suggested_difficulty": "Hard"
            }
        }


class Question(BaseModel):
    """
    Generated question for assessment.
    
    Contains the question text, unique identifier, difficulty level,
    and associated topic.
    """
    question_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique question identifier (UUID)"
    )
    question_text: str = Field(..., min_length=1, description="The question text")
    difficulty: Difficulty = Field(..., description="Question difficulty level")
    topic: str = Field(..., min_length=1, description="Question topic")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Question creation timestamp"
    )
    
    @field_validator("question_id")
    @classmethod
    def validate_question_id(cls, v: str) -> str:
        """Validate question_id is a valid UUID format"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"question_id must be a valid UUID, got: {v}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "660e8400-e29b-41d4-a716-446655440001",
                "question_text": "What is the difference between supervised and unsupervised learning?",
                "difficulty": "Medium",
                "topic": "Machine Learning",
                "created_at": "2024-01-15T10:05:00Z"
            }
        }


# ============================================================================
# API Request Models
# ============================================================================

class StartSessionRequest(BaseModel):
    """Request to start a new assessment session"""
    topic: str = Field(..., min_length=1, max_length=200, description="Assessment topic")
    initial_difficulty: Difficulty = Field(..., description="Starting difficulty level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Artificial Intelligence",
                "initial_difficulty": "Medium"
            }
        }


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer for evaluation"""
    session_id: str = Field(..., description="Session identifier (UUID)")
    question_id: str = Field(..., description="Question identifier (UUID)")
    answer_text: str = Field(..., min_length=1, description="Student's answer text")
    
    @field_validator("session_id", "question_id")
    @classmethod
    def validate_uuid_fields(cls, v: str, info) -> str:
        """Validate UUID format for session_id and question_id"""
        try:
            UUID(v)
            return v
        except ValueError:
            raise ValueError(f"{info.field_name} must be a valid UUID, got: {v}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "question_id": "660e8400-e29b-41d4-a716-446655440001",
                "answer_text": "Supervised learning uses labeled data while unsupervised learning finds patterns in unlabeled data."
            }
        }


class TranscribeAudioRequest(BaseModel):
    """Request to transcribe audio (handled via multipart form data)"""
    # Note: Audio file is handled via FastAPI's UploadFile, not in this model
    pass


class VoiceFeedbackRequest(BaseModel):
    """Request to generate voice feedback from text"""
    feedback_text: str = Field(..., min_length=1, max_length=5000, description="Feedback text to convert to speech")
    
    class Config:
        json_schema_extra = {
            "example": {
                "feedback_text": "Great answer! You correctly identified the key concepts of supervised and unsupervised learning."
            }
        }


# ============================================================================
# API Response Models
# ============================================================================

class StartSessionResponse(BaseModel):
    """Response after starting a new session"""
    session_id: str = Field(..., description="Unique session identifier")
    status: str = Field(default="created", description="Session status")
    topic: str = Field(..., description="Assessment topic")
    initial_difficulty: Difficulty = Field(..., description="Starting difficulty level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "created",
                "topic": "Artificial Intelligence",
                "initial_difficulty": "Medium"
            }
        }


class QuestionResponse(BaseModel):
    """Response containing a generated question"""
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question text")
    difficulty: Difficulty = Field(..., description="Question difficulty level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "660e8400-e29b-41d4-a716-446655440001",
                "question_text": "What is the difference between supervised and unsupervised learning?",
                "difficulty": "Medium"
            }
        }


class SubmitAnswerResponse(BaseModel):
    """Response after submitting an answer"""
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    is_correct: bool = Field(..., description="Whether the answer was correct")
    feedback_text: str = Field(..., description="Detailed feedback")
    new_difficulty: Difficulty = Field(..., description="Difficulty for next question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": 85,
                "is_correct": True,
                "feedback_text": "Great answer! You correctly identified the key concepts...",
                "new_difficulty": "Hard"
            }
        }


class TranscribeResponse(BaseModel):
    """Response containing transcribed text from audio"""
    transcribed_text: str = Field(..., description="Transcribed text from audio")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcribed_text": "Supervised learning uses labeled data while unsupervised learning finds patterns in unlabeled data."
            }
        }


class VoiceFeedbackResponse(BaseModel):
    """Response containing voice feedback audio"""
    audio_url: Optional[str] = Field(None, description="URL to audio file (if not streaming)")
    message: str = Field(default="Audio generated successfully", description="Status message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "audio_url": "https://example.com/audio/feedback-123.mp3",
                "message": "Audio generated successfully"
            }
        }


# ============================================================================
# Error Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response format"""
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_type": "SessionNotFoundError",
                "message": "Session with ID 550e8400-e29b-41d4-a716-446655440000 not found",
                "details": {"session_id": "550e8400-e29b-41d4-a716-446655440000"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
