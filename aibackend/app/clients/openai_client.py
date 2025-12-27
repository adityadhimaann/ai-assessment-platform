"""
OpenAI Client

This module provides a wrapper around the OpenAI SDK for GPT-4o and Whisper API calls.
It handles authentication, error handling, and retry logic.
"""

import time
from typing import List, Dict, Any, Optional, Literal
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError
from config.settings import Settings
from app.exceptions import OpenAIAPIError


class OpenAIClient:
    """
    Client for interacting with OpenAI APIs (GPT-4o and Whisper).
    
    This client handles:
    - Authentication with OpenAI API
    - Chat completion requests with JSON response format
    - Error handling and retry logic for transient failures
    - Rate limiting and timeout handling
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the OpenAI client.
        
        Args:
            settings: Application settings containing API key and model configuration
        """
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.gpt_model
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Literal["json", "text"]] = "text",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Make a chat completion request to GPT-4o.
        
        This method includes retry logic for transient failures like rate limits
        and connection errors.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            response_format: Format of the response - "json" for JSON mode, "text" for regular
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in the response (None for model default)
        
        Returns:
            The response content as a string
        
        Raises:
            OpenAIAPIError: If the API call fails after all retries
        """
        operation = "chat_completion"
        
        for attempt in range(self.max_retries):
            try:
                # Build request parameters
                request_params: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                }
                
                # Add JSON response format if requested
                if response_format == "json":
                    request_params["response_format"] = {"type": "json_object"}
                
                # Add max_tokens if specified
                if max_tokens is not None:
                    request_params["max_tokens"] = max_tokens
                
                # Make the API call
                response = self.client.chat.completions.create(**request_params)
                
                # Extract and return the content
                content = response.choices[0].message.content
                if content is None:
                    raise OpenAIAPIError(
                        message="Received empty response from OpenAI API",
                        operation=operation
                    )
                
                return content
            
            except RateLimitError as e:
                # Rate limit hit - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise OpenAIAPIError(
                        message="Rate limit exceeded after all retries",
                        operation=operation,
                        original_error=e
                    )
            
            except APITimeoutError as e:
                # Timeout error - retry (must be before APIConnectionError)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise OpenAIAPIError(
                        message="Request timeout after all retries",
                        operation=operation,
                        original_error=e
                    )
            
            except APIConnectionError as e:
                # Connection error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise OpenAIAPIError(
                        message="Connection error after all retries",
                        operation=operation,
                        original_error=e
                    )
            
            except APIError as e:
                # General API error - don't retry for client errors (4xx)
                if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                    raise OpenAIAPIError(
                        message=f"API client error: {str(e)}",
                        operation=operation,
                        original_error=e
                    )
                
                # Retry for server errors (5xx)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                else:
                    raise OpenAIAPIError(
                        message=f"API error after all retries: {str(e)}",
                        operation=operation,
                        original_error=e
                    )
            
            except Exception as e:
                # Unexpected error - don't retry
                raise OpenAIAPIError(
                    message=f"Unexpected error: {str(e)}",
                    operation=operation,
                    original_error=e
                )
        
        # Should never reach here, but just in case
        raise OpenAIAPIError(
            message="Failed to complete request after all retries",
            operation=operation
        )
