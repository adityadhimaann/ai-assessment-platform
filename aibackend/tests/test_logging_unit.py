"""
Unit tests for logging behavior

This module tests request logging, response logging, error logging,
and log levels.

Validates: Requirements 9.1, 9.3, 9.4, 9.5
"""

import os
import pytest
import logging
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import (
    configure_logging,
    get_logger,
    log_with_context,
    RequestLoggingMiddleware,
    ExternalAPILogger,
    StructuredFormatter,
    initialize_logging
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def reset_logging():
    """Reset logging configuration before each test"""
    # Clear all handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    yield
    
    # Clean up after test
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)


@pytest.fixture
def test_app():
    """Create a test FastAPI app with logging middleware"""
    app = FastAPI()
    
    # Add logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add a test endpoint
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    @app.get("/test-error")
    async def test_error_endpoint():
        raise ValueError("Test error")
    
    return app


@pytest.fixture
def test_client(test_app):
    """Create test client"""
    return TestClient(test_app)


# ============================================================================
# Test Structured Formatter
# ============================================================================

class TestStructuredFormatter:
    """Test suite for structured JSON log formatter"""
    
    def test_format_basic_log_record(self, reset_logging):
        """Test formatting a basic log record"""
        formatter = StructuredFormatter()
        logger = logging.getLogger("test")
        
        # Create a log record
        record = logger.makeRecord(
            "test",
            logging.INFO,
            "test.py",
            10,
            "Test message",
            (),
            None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse JSON
        log_data = json.loads(formatted)
        
        # Verify structure
        assert "timestamp" in log_data
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test"
        assert log_data["message"] == "Test message"
    
    def test_format_log_with_exception(self, reset_logging):
        """Test formatting a log record with exception info"""
        formatter = StructuredFormatter()
        logger = logging.getLogger("test")
        
        # Create exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        # Create a log record with exception
        record = logger.makeRecord(
            "test",
            logging.ERROR,
            "test.py",
            10,
            "Error occurred",
            (),
            exc_info
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Parse JSON
        log_data = json.loads(formatted)
        
        # Verify exception is included
        assert "exception" in log_data
        assert "ValueError" in log_data["exception"]
        assert "Test exception" in log_data["exception"]


# ============================================================================
# Test Logging Configuration
# ============================================================================

class TestLoggingConfiguration:
    """Test suite for logging configuration"""
    
    def test_configure_logging_info_level(self, reset_logging):
        """Test configuring logging with INFO level"""
        configure_logging("INFO")
        
        root_logger = logging.getLogger()
        
        # Verify log level
        assert root_logger.level == logging.INFO
        
        # Verify handler is configured
        assert len(root_logger.handlers) > 0
        
        # Verify formatter is StructuredFormatter
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, StructuredFormatter)
    
    def test_configure_logging_debug_level(self, reset_logging):
        """Test configuring logging with DEBUG level"""
        configure_logging("DEBUG")
        
        root_logger = logging.getLogger()
        
        # Verify log level
        assert root_logger.level == logging.DEBUG
    
    def test_configure_logging_error_level(self, reset_logging):
        """Test configuring logging with ERROR level"""
        configure_logging("ERROR")
        
        root_logger = logging.getLogger()
        
        # Verify log level
        assert root_logger.level == logging.ERROR
    
    def test_get_logger_returns_logger(self, reset_logging):
        """Test get_logger returns a logger instance"""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"


# ============================================================================
# Test Request Logging Middleware
# ============================================================================

class TestRequestLoggingMiddleware:
    """Test suite for request logging middleware"""
    
    def test_request_logging_success(self, test_client, reset_logging, capsys):
        """Test that successful requests are logged with details"""
        # Configure logging to capture logs
        configure_logging("INFO")
        
        # Make request
        response = test_client.get("/test")
        
        # Verify response
        assert response.status_code == 200
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify logs contain request details
        assert "Request started" in captured.out
        assert "GET /test" in captured.out
        assert "Request completed" in captured.out
    
    def test_request_logging_with_query_params(self, test_client, reset_logging, capsys):
        """Test that query parameters are logged"""
        configure_logging("INFO")
        
        # Make request with query params
        response = test_client.get("/test?param1=value1&param2=value2")
        
        # Verify response
        assert response.status_code == 200
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify query params are in logs
        assert "param1" in captured.out
        assert "param2" in captured.out
    
    def test_response_logging_includes_status_code(self, test_client, reset_logging, capsys):
        """Test that response status code is logged"""
        configure_logging("INFO")
        
        # Make request
        response = test_client.get("/test")
        
        # Verify response
        assert response.status_code == 200
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify status code is in logs
        assert "status_code" in captured.out
        assert "200" in captured.out
    
    def test_response_logging_includes_processing_time(self, test_client, reset_logging, capsys):
        """Test that processing time is logged"""
        configure_logging("INFO")
        
        # Make request
        response = test_client.get("/test")
        
        # Verify response
        assert response.status_code == 200
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify processing time is in logs
        assert "processing_time_ms" in captured.out
    
    def test_error_logging_on_exception(self, test_client, reset_logging, capsys):
        """Test that errors are logged when exceptions occur"""
        configure_logging("INFO")
        
        # Make request that raises exception
        try:
            response = test_client.get("/test-error")
        except Exception:
            pass  # Expected to fail
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify error was logged
        assert "Request failed" in captured.out
        assert "error" in captured.out


# ============================================================================
# Test External API Logger
# ============================================================================

class TestExternalAPILogger:
    """Test suite for external API logging"""
    
    def test_log_api_call_start(self, reset_logging, capsys):
        """Test logging the start of an API call"""
        configure_logging("INFO")
        
        api_logger = ExternalAPILogger("openai")
        
        start_time = api_logger.log_api_call_start(
            "chat_completion",
            model="gpt-4o",
            messages=["test"]
        )
        
        # Verify start_time is returned
        assert isinstance(start_time, float)
        assert start_time > 0
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify log was created
        assert "External API call started" in captured.out
        assert "openai" in captured.out
    
    def test_log_api_call_success(self, reset_logging, capsys):
        """Test logging successful API call completion"""
        configure_logging("INFO")
        
        api_logger = ExternalAPILogger("openai")
        
        start_time = api_logger.log_api_call_start("chat_completion")
        api_logger.log_api_call_success(
            "chat_completion",
            start_time,
            tokens_used=100
        )
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify success log was created
        assert "External API call succeeded" in captured.out
        assert "duration_ms" in captured.out
    
    def test_log_api_call_error(self, reset_logging, capsys):
        """Test logging API call errors with timestamp and context"""
        configure_logging("INFO")
        
        api_logger = ExternalAPILogger("whisper")
        
        # Create a test exception
        test_error = ValueError("API rate limit exceeded")
        
        start_time = api_logger.log_api_call_start("transcribe")
        api_logger.log_api_call_error(
            "transcribe",
            start_time,
            test_error,
            status_code=429
        )
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify error log was created
        assert "External API call failed" in captured.out
        assert "error" in captured.out


# ============================================================================
# Test Log Levels
# ============================================================================

class TestLogLevels:
    """Test suite for verifying appropriate log levels are used"""
    
    def test_info_level_for_normal_operations(self, reset_logging, capsys):
        """Test that INFO level is used for normal operations"""
        configure_logging("INFO")
        
        logger = get_logger("test")
        
        log_with_context(
            logger,
            logging.INFO,
            "Normal operation",
            operation="test"
        )
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify INFO level log was created
        assert "INFO" in captured.out
        assert "Normal operation" in captured.out
    
    def test_error_level_for_failures(self, reset_logging, capsys):
        """Test that ERROR level is used for failures"""
        configure_logging("INFO")
        
        logger = get_logger("test")
        
        log_with_context(
            logger,
            logging.ERROR,
            "Operation failed",
            error="Test error"
        )
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify ERROR level log was created
        assert "ERROR" in captured.out
        assert "Operation failed" in captured.out
    
    def test_debug_level_for_detailed_info(self, reset_logging, capsys):
        """Test that DEBUG level can be used for detailed information"""
        configure_logging("DEBUG")
        
        logger = get_logger("test")
        
        log_with_context(
            logger,
            logging.DEBUG,
            "Detailed debug info",
            details="test"
        )
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify DEBUG level log was created
        assert "DEBUG" in captured.out
        assert "Detailed debug info" in captured.out
    
    def test_warning_level_for_warnings(self, reset_logging, capsys):
        """Test that WARNING level can be used"""
        configure_logging("INFO")
        
        logger = get_logger("test")
        
        log_with_context(
            logger,
            logging.WARNING,
            "Warning message",
            warning="test"
        )
        
        # Capture stdout
        captured = capsys.readouterr()
        
        # Verify WARNING level log was created
        assert "WARNING" in captured.out
        assert "Warning message" in captured.out


# ============================================================================
# Test Initialize Logging
# ============================================================================

class TestInitializeLogging:
    """Test suite for initialize_logging function"""
    
    @patch('app.utils.logger.get_settings')
    def test_initialize_logging_success(self, mock_get_settings, reset_logging):
        """Test successful logging initialization"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.log_level = "INFO"
        mock_get_settings.return_value = mock_settings
        
        # Initialize logging
        initialize_logging()
        
        # Verify logging was configured
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
    
    @patch('app.utils.logger.get_settings')
    def test_initialize_logging_with_debug_level(self, mock_get_settings, reset_logging):
        """Test logging initialization with DEBUG level"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.log_level = "DEBUG"
        mock_get_settings.return_value = mock_settings
        
        # Initialize logging
        initialize_logging()
        
        # Verify logging was configured
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    @patch('app.utils.logger.get_settings')
    def test_initialize_logging_fallback_on_error(self, mock_get_settings, reset_logging):
        """Test that logging falls back to basic config if settings fail"""
        # Mock settings to raise exception
        mock_get_settings.side_effect = Exception("Settings error")
        
        # Initialize logging (should not raise)
        initialize_logging()
        
        # Verify basic logging is still configured
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0
