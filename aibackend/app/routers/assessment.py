"""
Assessment API Router

This module provides REST API endpoints for assessment session management,
question generation, and answer evaluation.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated

from app.models import (
    StartSessionRequest,
    StartSessionResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    Difficulty
)
from pydantic import BaseModel
from typing import List


class SessionSummaryResponse(BaseModel):
    """Response model for session summary"""
    session_id: str
    topic: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    average_score: float
    final_difficulty: Difficulty
    performance_by_difficulty: dict
    score_trend: List[int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "topic": "Python Programming",
                "total_questions": 10,
                "correct_answers": 7,
                "incorrect_answers": 3,
                "average_score": 78.5,
                "final_difficulty": "Medium",
                "performance_by_difficulty": {
                    "Easy": {"correct": 3, "total": 3},
                    "Medium": {"correct": 3, "total": 5},
                    "Hard": {"correct": 1, "total": 2}
                },
                "score_trend": [85, 90, 75, 80, 70, 85, 90, 65, 75, 80]
            }
        }
from app.services.session_service import SessionService
from app.services.evaluation_service import EvaluationService
from app.services.question_service import QuestionService
from app.clients.openai_client import OpenAIClient
from app.exceptions import (
    SessionNotFoundError,
    QuestionGenerationError,
    EvaluationError,
    AssessmentError
)
from config.settings import get_settings, Settings


# Create router
router = APIRouter(
    prefix="/api",
    tags=["assessment"]
)


# Dependency injection for services
def get_session_service() -> SessionService:
    """Get SessionService instance"""
    return SessionService()


def get_evaluation_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> EvaluationService:
    """Get EvaluationService instance"""
    openai_client = OpenAIClient(settings)
    return EvaluationService(openai_client, dev_mode=settings.dev_mode)


def get_question_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> QuestionService:
    """Get QuestionService instance"""
    openai_client = OpenAIClient(settings)
    return QuestionService(openai_client, dev_mode=settings.dev_mode)


# Global session service instance (in-memory storage)
_session_service_instance = None


def get_shared_session_service() -> SessionService:
    """
    Get shared SessionService instance.
    
    Uses a singleton pattern to ensure all requests use the same
    in-memory session storage.
    """
    global _session_service_instance
    if _session_service_instance is None:
        _session_service_instance = SessionService()
    return _session_service_instance


@router.post(
    "/start-session",
    response_model=StartSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new assessment session",
    description="Create a new assessment session with specified topic and initial difficulty"
)
async def start_session(
    request: StartSessionRequest,
    session_service: Annotated[SessionService, Depends(get_shared_session_service)]
) -> StartSessionResponse:
    """
    Start a new assessment session.
    
    Creates a new session with a unique ID, initializes it with the specified
    topic and difficulty level, and returns the session details.
    
    Args:
        request: Session creation request with topic and initial_difficulty
        session_service: Injected session service
    
    Returns:
        StartSessionResponse: Session ID and status
    
    Raises:
        HTTPException: 400 for invalid parameters, 500 for server errors
    
    Requirements: 7.1, 1.1
    """
    try:
        # Create session
        session_id = session_service.create_session(
            topic=request.topic,
            initial_difficulty=request.initial_difficulty
        )
        
        # Return response
        return StartSessionResponse(
            session_id=session_id,
            status="created",
            topic=request.topic,
            initial_difficulty=request.initial_difficulty
        )
    
    except AssessmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "InternalServerError",
                "message": f"Failed to create session: {str(e)}"
            }
        )


@router.get(
    "/get-next-question",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get next question for session",
    description="Generate and return the next question based on current session difficulty"
)
async def get_next_question(
    session_id: str,
    session_service: Annotated[SessionService, Depends(get_shared_session_service)],
    question_service: Annotated[QuestionService, Depends(get_question_service)]
) -> QuestionResponse:
    """
    Get the next question for an assessment session.
    
    Retrieves the current difficulty from the session and generates an
    appropriate question using GPT-4o.
    
    Args:
        session_id: The session identifier (UUID)
        session_service: Injected session service
        question_service: Injected question service
    
    Returns:
        QuestionResponse: Generated question with ID, text, and difficulty
    
    Raises:
        HTTPException: 404 for session not found, 400 for invalid parameters,
                      500 for server errors
    
    Requirements: 7.3, 4.1, 3.5
    """
    import traceback
    
    try:
        # Get session to retrieve current difficulty
        session = session_service.get_session(session_id)
        
        # Get current difficulty
        current_difficulty = session.current_difficulty
        
        # Generate question
        question = question_service.generate_question(
            topic=session.topic,
            difficulty=current_difficulty
        )
        
        # Return response
        return QuestionResponse(
            question_id=question.question_id,
            question_text=question.question_text,
            difficulty=question.difficulty
        )
    
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except QuestionGenerationError as e:
        print(f"QuestionGenerationError: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )
    except AssessmentError as e:
        print(f"AssessmentError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "InternalServerError",
                "message": f"Failed to generate question: {str(e)}",
                "traceback": traceback.format_exc()
            }
        )


@router.post(
    "/submit-answer",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit answer for evaluation",
    description="Evaluate student answer and update session with performance data"
)
async def submit_answer(
    request: SubmitAnswerRequest,
    session_service: Annotated[SessionService, Depends(get_shared_session_service)],
    evaluation_service: Annotated[EvaluationService, Depends(get_evaluation_service)]
) -> SubmitAnswerResponse:
    """
    Submit an answer for evaluation.
    
    Evaluates the student's answer using GPT-4o, updates the session with
    performance data, and calculates the new difficulty level for the next question.
    
    Args:
        request: Answer submission with session_id, question_id, and answer_text
        session_service: Injected session service
        evaluation_service: Injected evaluation service
    
    Returns:
        SubmitAnswerResponse: Evaluation results with score, correctness,
                             feedback, and new difficulty
    
    Raises:
        HTTPException: 404 for session not found, 400 for invalid parameters,
                      500 for server errors
    
    Requirements: 7.2, 2.1
    """
    try:
        # Get session to retrieve topic and validate session exists
        session = session_service.get_session(request.session_id)
        
        # For evaluation, we need the actual question text
        # In a real implementation, we would store questions and retrieve them
        # For now, we'll use a placeholder approach
        # TODO: Implement question storage and retrieval
        question_text = f"Question {request.question_id}"
        
        # Evaluate the answer
        evaluation_result = evaluation_service.evaluate_answer(
            question=question_text,
            answer=request.answer_text,
            topic=session.topic
        )
        
        # Update session with performance
        session_service.update_session_performance(
            session_id=request.session_id,
            question_id=request.question_id,
            score=evaluation_result.score,
            is_correct=evaluation_result.is_correct
        )
        
        # Get updated session to retrieve new difficulty
        updated_session = session_service.get_session(request.session_id)
        new_difficulty = updated_session.current_difficulty
        
        # Return response
        return SubmitAnswerResponse(
            score=evaluation_result.score,
            is_correct=evaluation_result.is_correct,
            feedback_text=evaluation_result.feedback_text,
            new_difficulty=new_difficulty
        )
    
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except EvaluationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )
    except AssessmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "InternalServerError",
                "message": f"Failed to evaluate answer: {str(e)}"
            }
        )



@router.get(
    "/session-summary/{session_id}",
    response_model=SessionSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get session summary and results",
    description="Retrieve comprehensive summary of session performance including scores, difficulty progression, and statistics"
)
async def get_session_summary(
    session_id: str,
    session_service: Annotated[SessionService, Depends(get_shared_session_service)]
) -> SessionSummaryResponse:
    """
    Get comprehensive summary of an assessment session.
    
    Calculates and returns detailed statistics including:
    - Total questions answered
    - Correct/incorrect counts
    - Average score
    - Performance breakdown by difficulty level
    - Score trend over time
    
    Args:
        session_id: The session identifier (UUID)
        session_service: Injected session service
    
    Returns:
        SessionSummaryResponse: Comprehensive session statistics
    
    Raises:
        HTTPException: 404 for session not found, 500 for server errors
    """
    try:
        # Get session
        session = session_service.get_session(session_id)
        
        # Calculate statistics
        total_questions = len(session.performance_history)
        correct_answers = sum(1 for record in session.performance_history if record.is_correct)
        incorrect_answers = total_questions - correct_answers
        
        # Calculate average score
        if total_questions > 0:
            average_score = sum(record.score for record in session.performance_history) / total_questions
        else:
            average_score = 0.0
        
        # Performance by difficulty
        performance_by_difficulty = {}
        for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            records_at_diff = [r for r in session.performance_history if r.difficulty == difficulty]
            if records_at_diff:
                performance_by_difficulty[difficulty.value] = {
                    "correct": sum(1 for r in records_at_diff if r.is_correct),
                    "total": len(records_at_diff)
                }
        
        # Score trend
        score_trend = [record.score for record in session.performance_history]
        
        return SessionSummaryResponse(
            session_id=session.session_id,
            topic=session.topic,
            total_questions=total_questions,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            average_score=round(average_score, 1),
            final_difficulty=session.current_difficulty,
            performance_by_difficulty=performance_by_difficulty,
            score_trend=score_trend
        )
    
    except SessionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.to_dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "InternalServerError",
                "message": f"Failed to get session summary: {str(e)}"
            }
        )
