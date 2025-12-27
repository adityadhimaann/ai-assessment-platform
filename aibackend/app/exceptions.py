"""
Custom Exceptions

This module defines all custom exceptions for the AI Assessment Backend.
Each exception includes appropriate error messages and context for debugging.
"""

from typing import Optional, Dict, Any


class AssessmentError(Exception):
    """
    Base exception for all assessment system errors.
    
    All custom exceptions in the system inherit from this base class,
    allowing for centralized error handling.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format for API responses.
        
        Returns:
            Dictionary with error_type, message, and details
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class SessionNotFoundError(AssessmentError):
    """
    Exception raised when a session ID does not exist.
    
    This occurs when attempting to retrieve or update a session
    that hasn't been created or has expired.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize the exception.
        
        Args:
            session_id: The session ID that was not found
        """
        super().__init__(
            message=f"Session with ID {session_id} not found",
            details={"session_id": session_id}
        )


class InvalidDifficultyError(AssessmentError):
    """
    Exception raised when an invalid difficulty level is provided.
    
    Valid difficulty levels are: Easy, Medium, Hard
    """
    
    def __init__(self, difficulty: str, valid_values: list = None):
        """
        Initialize the exception.
        
        Args:
            difficulty: The invalid difficulty value provided
            valid_values: List of valid difficulty values
        """
        valid = valid_values or ["Easy", "Medium", "Hard"]
        super().__init__(
            message=f"Invalid difficulty level: {difficulty}. Must be one of: {', '.join(valid)}",
            details={
                "provided_difficulty": difficulty,
                "valid_difficulties": valid
            }
        )


class OpenAIAPIError(AssessmentError):
    """
    Exception raised when OpenAI API calls fail.
    
    This includes GPT-4o evaluation/question generation and Whisper transcription.
    """
    
    def __init__(
        self,
        message: str,
        operation: str,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            operation: The operation that failed (e.g., "evaluation", "question_generation")
            original_error: The original exception from OpenAI SDK
        """
        details = {
            "operation": operation,
            "service": "OpenAI"
        }
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=f"OpenAI API error during {operation}: {message}",
            details=details
        )
        self.original_error = original_error


class WhisperAPIError(AssessmentError):
    """
    Exception raised when Whisper API transcription fails.
    
    This is a specialized OpenAI API error for audio transcription.
    """
    
    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            original_error: The original exception from Whisper API
        """
        details = {
            "operation": "audio_transcription",
            "service": "Whisper"
        }
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=f"Whisper API error: {message}",
            details=details
        )
        self.original_error = original_error


class TTSAPIError(AssessmentError):
    """
    Exception raised when Text-to-Speech API calls fail.
    
    This applies to both ElevenLabs and OpenAI TTS services.
    """
    
    def __init__(
        self,
        message: str,
        service: str = "TTS",
        original_error: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            service: The TTS service being used (e.g., "ElevenLabs", "OpenAI TTS")
            original_error: The original exception from TTS API
        """
        details = {
            "operation": "voice_synthesis",
            "service": service
        }
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=f"{service} API error: {message}",
            details=details
        )
        self.original_error = original_error


class ValidationError(AssessmentError):
    """
    Exception raised when input validation fails.
    
    This is used for custom validation beyond Pydantic's built-in validation.
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            field: The field that failed validation
            value: The invalid value provided
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(
            message=f"Validation error: {message}",
            details=details
        )


class AudioFileError(ValidationError):
    """
    Exception raised when audio file validation fails.
    
    This includes unsupported formats, file size limits, or corrupted files.
    """
    
    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        max_size: Optional[int] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            filename: Name of the audio file
            file_size: Size of the file in bytes
            max_size: Maximum allowed file size in bytes
        """
        details = {}
        if filename:
            details["filename"] = filename
        if file_size is not None:
            details["file_size_bytes"] = file_size
            details["file_size_mb"] = round(file_size / (1024 * 1024), 2)
        if max_size is not None:
            details["max_size_bytes"] = max_size
            details["max_size_mb"] = round(max_size / (1024 * 1024), 2)
        
        super().__init__(
            message=message,
            field="audio_file"
        )
        self.details.update(details)


class QuestionGenerationError(AssessmentError):
    """
    Exception raised when question generation fails.
    
    This can occur due to API errors or invalid responses from GPT-4o.
    """
    
    def __init__(
        self,
        message: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            topic: The topic for which question generation failed
            difficulty: The difficulty level requested
            original_error: The original exception if any
        """
        details = {}
        if topic:
            details["topic"] = topic
        if difficulty:
            details["difficulty"] = difficulty
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=f"Question generation failed: {message}",
            details=details
        )
        self.original_error = original_error


class EvaluationError(AssessmentError):
    """
    Exception raised when answer evaluation fails.
    
    This can occur due to API errors or invalid responses from GPT-4o.
    """
    
    def __init__(
        self,
        message: str,
        question_id: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            question_id: The question ID being evaluated
            original_error: The original exception if any
        """
        details = {}
        if question_id:
            details["question_id"] = question_id
        if original_error:
            details["original_error"] = str(original_error)
        
        super().__init__(
            message=f"Answer evaluation failed: {message}",
            details=details
        )
        self.original_error = original_error
