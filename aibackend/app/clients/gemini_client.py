"""
Google Gemini Client

This module provides a client for interacting with Google's Gemini API.
"""

import os
import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from config.settings import Settings


class GeminiClient:
    """
    Client for Google Gemini API interactions.
    
    Provides methods for:
    - Chat completions with Gemini Pro
    - JSON-formatted responses
    - Configurable generation parameters
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the Gemini client.
        
        Args:
            settings: Application settings containing API key
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 1.5 Pro for best quality
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "text",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate a chat completion using Gemini.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            response_format: 'text' or 'json'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        
        Returns:
            str: The generated response text
        """
        try:
            # Convert OpenAI-style messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            # Add JSON instruction if needed
            if response_format == "json":
                prompt += "\n\nIMPORTANT: Respond with ONLY valid JSON, no other text."
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages to a single prompt for Gemini.
        
        Args:
            messages: List of message dicts
        
        Returns:
            str: Combined prompt
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{content}\n")
            elif role == "user":
                prompt_parts.append(f"USER:\n{content}\n")
            elif role == "assistant":
                prompt_parts.append(f"ASSISTANT:\n{content}\n")
        
        return "\n".join(prompt_parts)
