"""
Error Handling Middleware

This module provides global exception handling for the FastAPI application.
It maps custom exceptions to appropriate HTTP status codes and returns
structured error responses.
"""

from datetime import datetime
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.exceptions import (
    AssessmentError,
    SessionNotFoundError,
    InvalidDifficultyError,
    OpenAIAPIError,
    WhisperAPIError,
    TTSAPIError,
    ValidationError,
    AudioFileError,
    QuestionGenerationError,
    EvaluationError,
)
from app.models import ErrorResponse


# ============================================================================
# Exception to HTTP Status Code Mapping
# ============================================================================

EXCEPTION_STATUS_MAP = {
    # 404 Not Found
    SessionNotFoundError: status.HTTP_404_NOT_FOUND,
    
    # 400 Bad Request
    InvalidDifficultyError: status.HTTP_400_BAD_REQUEST,
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AudioFileError: status.HTTP_400_BAD_REQUEST,
    
    # 422 Unprocessable Entity (validation errors)
    RequestValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    PydanticValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    
    # 500 Internal Server Error (external API failures and other errors)
    OpenAIAPIError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    WhisperAPIError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    TTSAPIError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    QuestionGenerationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    EvaluationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    AssessmentError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


# ============================================================================
# Exception Handlers
# ============================================================================

async def assessment_error_handler(
    request: Request,
    exc: AssessmentError
) -> JSONResponse:
    """
    Handle custom AssessmentError exceptions.
    
    Maps the exception to the appropriate HTTP status code and returns
    a structured error response.
    
    Args:
        request: The FastAPI request object
        exc: The AssessmentError exception
        
    Returns:
        JSONResponse with structured error details
    """
    # Determine status code based on exception type
    status_code = EXCEPTION_STATUS_MAP.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    # Create error response
    error_response = ErrorResponse(
        error_type=exc.__class__.__name__,
        message=exc.message,
        details=exc.details,
        timestamp=datetime.utcnow()
    )
    
    # Return error in 'detail' field to match FastAPI convention
    # Use model_dump with mode='json' to ensure datetime is serialized
    return JSONResponse(
        status_code=status_code,
        content={"detail": error_response.model_dump(mode='json')}
    )


async def validation_error_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError]
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Converts Pydantic validation errors into structured error responses
    with detailed field-level validation information.
    
    Args:
        request: The FastAPI request object
        exc: The validation error exception
        
    Returns:
        JSONResponse with validation error details
    """
    # Extract validation error details
    errors = []
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
    elif isinstance(exc, PydanticValidationError):
        errors = exc.errors()
    
    # Format error details for FastAPI convention
    # FastAPI expects validation errors in a specific format
    formatted_errors = [
        {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        for error in errors
    ]
    
    # Return in FastAPI's standard validation error format
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors}
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Catches any unhandled exceptions and returns a generic 500 error
    response without exposing internal details.
    
    Args:
        request: The FastAPI request object
        exc: The exception
        
    Returns:
        JSONResponse with generic error message
    """
    # Log the exception (in production, use proper logging)
    print(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    
    # Create generic error response
    error_response = ErrorResponse(
        error_type="InternalServerError",
        message="An unexpected error occurred. Please try again later.",
        details={"exception_type": type(exc).__name__},
        timestamp=datetime.utcnow()
    )
    
    # Return error in 'detail' field to match FastAPI convention
    # Use model_dump with mode='json' to ensure datetime is serialized
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": error_response.model_dump(mode='json')}
    )


# ============================================================================
# Middleware Registration Helper
# ============================================================================

def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.
    
    This function should be called during application startup to configure
    global exception handling.
    
    Args:
        app: The FastAPI application instance
    """
    # Register custom exception handlers
    app.add_exception_handler(AssessmentError, assessment_error_handler)
    app.add_exception_handler(SessionNotFoundError, assessment_error_handler)
    app.add_exception_handler(InvalidDifficultyError, assessment_error_handler)
    app.add_exception_handler(OpenAIAPIError, assessment_error_handler)
    app.add_exception_handler(WhisperAPIError, assessment_error_handler)
    app.add_exception_handler(TTSAPIError, assessment_error_handler)
    app.add_exception_handler(ValidationError, assessment_error_handler)
    app.add_exception_handler(AudioFileError, assessment_error_handler)
    app.add_exception_handler(QuestionGenerationError, assessment_error_handler)
    app.add_exception_handler(EvaluationError, assessment_error_handler)
    
    # Register validation error handlers
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(PydanticValidationError, validation_error_handler)
    
    # Register generic exception handler for unexpected errors
    app.add_exception_handler(Exception, generic_exception_handler)
