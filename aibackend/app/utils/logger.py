"""
Logging Configuration and Middleware

This module provides structured logging with appropriate levels and middleware
for logging HTTP requests, responses, and external API calls.

Requirements: 9.1, 9.3, 9.4, 9.5
"""

import logging
import sys
import time
import json
from typing import Callable, Dict, Any
from datetime import datetime, timezone
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import get_settings


# Context variable for request ID tracking
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    
    Each log entry includes:
    - timestamp: ISO format timestamp
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - logger: Logger name
    - message: Log message
    - request_id: Request ID if available
    - extra: Any additional fields passed to the logger
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string with structured log data
        """
        # Base log structure
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields from the record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.
    
    Sets up:
    - Root logger with specified level
    - Structured JSON formatter
    - Console handler for stdout
    - Appropriate log levels for third-party libraries
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Requirements: 9.1, 9.5
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Set structured formatter
    formatter = StructuredFormatter()
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure third-party library log levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **extra_fields: Any
) -> None:
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (logging.DEBUG, logging.INFO, etc.)
        message: Log message
        **extra_fields: Additional fields to include in the log
    
    Example:
        log_with_context(
            logger,
            logging.INFO,
            "API call completed",
            api="openai",
            duration_ms=150,
            status="success"
        )
    """
    # Create a log record with extra fields
    record = logger.makeRecord(
        logger.name,
        level,
        "(unknown file)",
        0,
        message,
        (),
        None
    )
    record.extra_fields = extra_fields
    logger.handle(record)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs:
    - Request details: method, path, query params, headers
    - Response details: status code, processing time
    - Request ID for correlation
    
    Requirements: 9.3, 9.4
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize request logging middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
        self.logger = get_logger("request")
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            HTTP response
        """
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}-{id(request)}"
        request_id_var.set(request_id)
        
        # Record start time
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Log request
        log_with_context(
            self.logger,
            logging.INFO,
            f"Request started: {method} {path}",
            request_id=request_id,
            method=method,
            path=path,
            query_params=query_params,
            client_host=request.client.host if request.client else None
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Log response
            log_with_context(
                self.logger,
                logging.INFO,
                f"Request completed: {method} {path}",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                processing_time_ms=round(processing_time_ms, 2)
            )
            
            return response
        
        except Exception as e:
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Log error
            log_with_context(
                self.logger,
                logging.ERROR,
                f"Request failed: {method} {path}",
                request_id=request_id,
                method=method,
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                processing_time_ms=round(processing_time_ms, 2)
            )
            
            # Re-raise exception
            raise


class ExternalAPILogger:
    """
    Logger for external API calls.
    
    Provides methods to log API calls to external services like OpenAI,
    Whisper, and TTS services.
    
    Requirements: 9.1
    """
    
    def __init__(self, service_name: str):
        """
        Initialize external API logger.
        
        Args:
            service_name: Name of the external service (e.g., "openai", "whisper")
        """
        self.service_name = service_name
        self.logger = get_logger(f"external_api.{service_name}")
    
    def log_api_call_start(
        self,
        operation: str,
        **params: Any
    ) -> float:
        """
        Log the start of an external API call.
        
        Args:
            operation: API operation name (e.g., "chat_completion", "transcribe")
            **params: API call parameters to log
            
        Returns:
            Start time for duration calculation
        """
        start_time = time.time()
        
        log_with_context(
            self.logger,
            logging.INFO,
            f"External API call started: {self.service_name}.{operation}",
            service=self.service_name,
            operation=operation,
            params=params
        )
        
        return start_time
    
    def log_api_call_success(
        self,
        operation: str,
        start_time: float,
        **result_info: Any
    ) -> None:
        """
        Log successful completion of an external API call.
        
        Args:
            operation: API operation name
            start_time: Start time from log_api_call_start
            **result_info: Information about the result
        """
        duration_ms = (time.time() - start_time) * 1000
        
        log_with_context(
            self.logger,
            logging.INFO,
            f"External API call succeeded: {self.service_name}.{operation}",
            service=self.service_name,
            operation=operation,
            duration_ms=round(duration_ms, 2),
            status="success",
            **result_info
        )
    
    def log_api_call_error(
        self,
        operation: str,
        start_time: float,
        error: Exception,
        **error_context: Any
    ) -> None:
        """
        Log failed external API call.
        
        Args:
            operation: API operation name
            start_time: Start time from log_api_call_start
            error: Exception that occurred
            **error_context: Additional context about the error
        
        Requirements: 9.1
        """
        duration_ms = (time.time() - start_time) * 1000
        
        log_with_context(
            self.logger,
            logging.ERROR,
            f"External API call failed: {self.service_name}.{operation}",
            service=self.service_name,
            operation=operation,
            duration_ms=round(duration_ms, 2),
            status="error",
            error=str(error),
            error_type=type(error).__name__,
            **error_context
        )


def initialize_logging() -> None:
    """
    Initialize logging configuration from settings.
    
    Should be called once at application startup.
    """
    try:
        settings = get_settings()
        configure_logging(settings.log_level)
        
        logger = get_logger("startup")
        logger.info(
            "Logging initialized",
            extra={"extra_fields": {"log_level": settings.log_level}}
        )
    except Exception as e:
        # Fallback to basic logging if settings fail
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.error(f"Failed to initialize structured logging: {e}")
