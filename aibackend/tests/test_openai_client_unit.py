"""
Unit tests for OpenAI Client with mocked API

Tests successful API calls, error handling, and retry logic.

Requirements: 2.1, 2.5
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError

from app.clients.openai_client import OpenAIClient
from app.exceptions import OpenAIAPIError
from config.settings import Settings


@pytest.fixture
def mock_settings():
    """Create mock settings for testing"""
    settings = Mock(spec=Settings)
    settings.openai_api_key = "test-api-key-123"
    settings.gpt_model = "gpt-4o"
    return settings


@pytest.fixture
def openai_client(mock_settings):
    """Create OpenAI client with mocked settings"""
    with patch('app.clients.openai_client.OpenAI') as mock_openai:
        client = OpenAIClient(mock_settings)
        client.retry_delay = 0.01  # Speed up tests
        return client


class TestOpenAIClientSuccessfulCalls:
    """Test suite for successful OpenAI API calls"""
    
    def test_successful_text_completion(self, openai_client):
        """
        Test successful chat completion with text response format.
        
        Requirements: 2.1
        """
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test response"
        
        openai_client.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Make the request
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"}
        ]
        result = openai_client.chat_completion(messages, response_format="text")
        
        # Verify the result
        assert result == "This is a test response"
        
        # Verify the API was called with correct parameters
        openai_client.client.chat.completions.create.assert_called_once()
        call_args = openai_client.client.chat.completions.create.call_args[1]
        assert call_args["model"] == "gpt-4o"
        assert call_args["messages"] == messages
        assert call_args["temperature"] == 0.7
        assert "response_format" not in call_args
    
    def test_successful_json_completion(self, openai_client):
        """
        Test successful chat completion with JSON response format.
        
        Requirements: 2.1
        """
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"score": 85, "feedback": "Good answer"}'
        
        openai_client.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Make the request
        messages = [
            {"role": "system", "content": "You are an evaluator"},
            {"role": "user", "content": "Evaluate this answer"}
        ]
        result = openai_client.chat_completion(messages, response_format="json")
        
        # Verify the result
        assert result == '{"score": 85, "feedback": "Good answer"}'
        
        # Verify the API was called with JSON format
        call_args = openai_client.client.chat.completions.create.call_args[1]
        assert call_args["response_format"] == {"type": "json_object"}
    
    def test_successful_completion_with_custom_temperature(self, openai_client):
        """
        Test chat completion with custom temperature parameter.
        
        Requirements: 2.1
        """
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        
        openai_client.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Make the request with custom temperature
        messages = [{"role": "user", "content": "Test"}]
        result = openai_client.chat_completion(messages, temperature=0.2)
        
        # Verify temperature was passed
        call_args = openai_client.client.chat.completions.create.call_args[1]
        assert call_args["temperature"] == 0.2
    
    def test_successful_completion_with_max_tokens(self, openai_client):
        """
        Test chat completion with max_tokens parameter.
        
        Requirements: 2.1
        """
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        
        openai_client.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Make the request with max_tokens
        messages = [{"role": "user", "content": "Test"}]
        result = openai_client.chat_completion(messages, max_tokens=100)
        
        # Verify max_tokens was passed
        call_args = openai_client.client.chat.completions.create.call_args[1]
        assert call_args["max_tokens"] == 100


class TestOpenAIClientErrorHandling:
    """Test suite for OpenAI API error handling"""
    
    def test_empty_response_error(self, openai_client):
        """
        Test handling of empty response from API.
        
        Requirements: 2.5
        """
        # Mock the API response with None content
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = None
        
        openai_client.client.chat.completions.create = Mock(return_value=mock_response)
        
        # Make the request and expect error
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify error details
        assert "empty response" in str(exc_info.value).lower()
        assert exc_info.value.details["operation"] == "chat_completion"
    
    def test_api_client_error_no_retry(self, openai_client):
        """
        Test that client errors (4xx) are not retried.
        
        Requirements: 2.5
        """
        # Mock a 400 error
        mock_request = Mock()
        error = APIError("Bad request", request=mock_request, body=None)
        # Set status_code attribute for the error handling logic
        error.status_code = 400
        
        openai_client.client.chat.completions.create = Mock(side_effect=error)
        
        # Make the request and expect error
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify only called once (no retries)
        assert openai_client.client.chat.completions.create.call_count == 1
        assert "client error" in str(exc_info.value).lower()
    
    def test_api_server_error_with_retries(self, openai_client):
        """
        Test that server errors (5xx) are retried.
        
        Requirements: 2.5
        """
        # Mock a 500 error
        mock_request = Mock()
        error = APIError("Internal server error", request=mock_request, body=None)
        # Set status_code attribute for the error handling logic
        error.status_code = 500
        
        openai_client.client.chat.completions.create = Mock(side_effect=error)
        
        # Make the request and expect error after retries
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify retried 3 times
        assert openai_client.client.chat.completions.create.call_count == 3
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_unexpected_error_no_retry(self, openai_client):
        """
        Test that unexpected errors are not retried.
        
        Requirements: 2.5
        """
        # Mock an unexpected error
        error = ValueError("Unexpected error")
        
        openai_client.client.chat.completions.create = Mock(side_effect=error)
        
        # Make the request and expect error
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify only called once (no retries)
        assert openai_client.client.chat.completions.create.call_count == 1
        assert "unexpected error" in str(exc_info.value).lower()


class TestOpenAIClientRetryLogic:
    """Test suite for retry logic with transient failures"""
    
    def test_rate_limit_retry_success(self, openai_client):
        """
        Test successful retry after rate limit error.
        
        Requirements: 2.5
        """
        # Mock rate limit error on first call, success on second
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Success after retry"
        
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        openai_client.client.chat.completions.create = Mock(
            side_effect=[rate_limit_error, mock_response]
        )
        
        # Make the request
        messages = [{"role": "user", "content": "Test"}]
        result = openai_client.chat_completion(messages)
        
        # Verify success after retry
        assert result == "Success after retry"
        assert openai_client.client.chat.completions.create.call_count == 2
    
    def test_rate_limit_retry_exhausted(self, openai_client):
        """
        Test that rate limit errors fail after max retries.
        
        Requirements: 2.5
        """
        # Mock rate limit error on all attempts
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        openai_client.client.chat.completions.create = Mock(side_effect=rate_limit_error)
        
        # Make the request and expect error
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify retried 3 times
        assert openai_client.client.chat.completions.create.call_count == 3
        assert "rate limit" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_connection_error_retry_success(self, openai_client):
        """
        Test successful retry after connection error.
        
        Requirements: 2.5
        """
        # Mock connection error on first call, success on second
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Success after retry"
        
        connection_error = APIConnectionError(request=Mock())
        
        openai_client.client.chat.completions.create = Mock(
            side_effect=[connection_error, mock_response]
        )
        
        # Make the request
        messages = [{"role": "user", "content": "Test"}]
        result = openai_client.chat_completion(messages)
        
        # Verify success after retry
        assert result == "Success after retry"
        assert openai_client.client.chat.completions.create.call_count == 2
    
    def test_connection_error_retry_exhausted(self, openai_client):
        """
        Test that connection errors fail after max retries.
        
        Requirements: 2.5
        """
        # Mock connection error on all attempts
        connection_error = APIConnectionError(request=Mock())
        
        openai_client.client.chat.completions.create = Mock(side_effect=connection_error)
        
        # Make the request and expect error
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify retried 3 times
        assert openai_client.client.chat.completions.create.call_count == 3
        assert "connection error" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_timeout_error_retry_success(self, openai_client):
        """
        Test successful retry after timeout error.
        
        Requirements: 2.5
        """
        # Mock timeout error on first call, success on second
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Success after retry"
        
        timeout_error = APITimeoutError(request=Mock())
        
        openai_client.client.chat.completions.create = Mock(
            side_effect=[timeout_error, mock_response]
        )
        
        # Make the request
        messages = [{"role": "user", "content": "Test"}]
        result = openai_client.chat_completion(messages)
        
        # Verify success after retry
        assert result == "Success after retry"
        assert openai_client.client.chat.completions.create.call_count == 2
    
    def test_timeout_error_retry_exhausted(self, openai_client):
        """
        Test that timeout errors fail after max retries.
        
        Requirements: 2.5
        """
        # Mock timeout error on all attempts
        timeout_error = APITimeoutError(request=Mock())
        
        openai_client.client.chat.completions.create = Mock(side_effect=timeout_error)
        
        # Make the request and expect error
        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(OpenAIAPIError) as exc_info:
            openai_client.chat_completion(messages)
        
        # Verify retried 3 times
        assert openai_client.client.chat.completions.create.call_count == 3
        assert "timeout" in str(exc_info.value).lower()
        assert "after all retries" in str(exc_info.value).lower()
    
    def test_exponential_backoff(self, openai_client):
        """
        Test that retry delays use exponential backoff.
        
        Requirements: 2.5
        """
        # Mock rate limit error on all attempts
        rate_limit_error = RateLimitError("Rate limit exceeded", response=Mock(), body=None)
        
        openai_client.client.chat.completions.create = Mock(side_effect=rate_limit_error)
        
        # Patch time.sleep to track delays
        with patch('app.clients.openai_client.time.sleep') as mock_sleep:
            messages = [{"role": "user", "content": "Test"}]
            
            try:
                openai_client.chat_completion(messages)
            except OpenAIAPIError:
                pass
            
            # Verify exponential backoff: 0.01, 0.02 (delays for first 2 retries)
            assert mock_sleep.call_count == 2
            delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert delays[0] == pytest.approx(0.01, rel=0.01)  # 0.01 * 2^0
            assert delays[1] == pytest.approx(0.02, rel=0.01)  # 0.01 * 2^1
    
    def test_mixed_errors_retry_behavior(self, openai_client):
        """
        Test retry behavior with mixed transient and permanent errors.
        
        Requirements: 2.5
        """
        # Mock: connection error, then rate limit, then success
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Success"
        
        connection_error = APIConnectionError(request=Mock())
        rate_limit_error = RateLimitError("Rate limit", response=Mock(), body=None)
        
        openai_client.client.chat.completions.create = Mock(
            side_effect=[connection_error, rate_limit_error, mock_response]
        )
        
        # Make the request
        messages = [{"role": "user", "content": "Test"}]
        result = openai_client.chat_completion(messages)
        
        # Verify success after multiple retries
        assert result == "Success"
        assert openai_client.client.chat.completions.create.call_count == 3
