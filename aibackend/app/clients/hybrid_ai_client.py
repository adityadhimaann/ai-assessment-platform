"""
Hybrid AI Client

This module provides an intelligent hybrid approach that uses both OpenAI GPT-4 and Google Gemini,
then selects or combines the best response.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from app.clients.openai_client import OpenAIClient
from app.clients.gemini_client import GeminiClient
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)


class HybridAIClient:
    """
    Hybrid AI client that uses both GPT-4 and Gemini for better quality.
    
    Strategies:
    1. Parallel Generation: Call both models simultaneously
    2. Quality Scoring: Evaluate which response is better
    3. Ensemble: Combine insights from both models
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize hybrid AI client with both OpenAI and Gemini.
        
        Args:
            settings: Application settings
        """
        self.openai_client = OpenAIClient(settings)
        
        # Try to initialize Gemini (optional)
        try:
            self.gemini_client = GeminiClient(settings)
            self.has_gemini = True
            logger.info("✅ Hybrid AI: Both GPT-4 and Gemini available")
        except Exception as e:
            self.gemini_client = None
            self.has_gemini = False
            logger.warning(f"⚠️  Gemini not available: {e}. Using GPT-4 only.")
    
    async def generate_question_hybrid(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.9
    ) -> str:
        """
        Generate a question using both models and select the best one.
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
        
        Returns:
            str: The best question from both models
        """
        if not self.has_gemini:
            # Fallback to GPT-4 only
            return self.openai_client.chat_completion(
                messages=messages,
                response_format="text",
                temperature=temperature
            )
        
        try:
            # Call both models in parallel
            logger.info("🤖 Generating question with GPT-4 and Gemini in parallel...")
            
            gpt_task = asyncio.create_task(
                asyncio.to_thread(
                    self.openai_client.chat_completion,
                    messages=messages,
                    response_format="text",
                    temperature=temperature
                )
            )
            
            gemini_task = asyncio.create_task(
                asyncio.to_thread(
                    self.gemini_client.chat_completion,
                    messages=messages,
                    response_format="text",
                    temperature=temperature
                )
            )
            
            # Wait for both responses
            gpt_response, gemini_response = await asyncio.gather(
                gpt_task, gemini_task, return_exceptions=True
            )
            
            # Handle errors
            if isinstance(gpt_response, Exception):
                logger.error(f"GPT-4 error: {gpt_response}")
                gpt_response = None
            
            if isinstance(gemini_response, Exception):
                logger.error(f"Gemini error: {gemini_response}")
                gemini_response = None
            
            # Select best question
            best_question = self._select_best_question(gpt_response, gemini_response)
            
            return best_question
            
        except Exception as e:
            logger.error(f"Hybrid generation error: {e}")
            # Fallback to GPT-4
            return self.openai_client.chat_completion(
                messages=messages,
                response_format="text",
                temperature=temperature
            )
    
    async def evaluate_answer_hybrid(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1000
    ) -> str:
        """
        Evaluate an answer using both models and combine their insights.
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
        
        Returns:
            str: Combined evaluation JSON
        """
        if not self.has_gemini:
            # Fallback to GPT-4 only
            return self.openai_client.chat_completion(
                messages=messages,
                response_format="json",
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        try:
            logger.info("🤖 Evaluating answer with GPT-4 and Gemini in parallel...")
            
            # Call both models in parallel
            gpt_task = asyncio.create_task(
                asyncio.to_thread(
                    self.openai_client.chat_completion,
                    messages=messages,
                    response_format="json",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            )
            
            gemini_task = asyncio.create_task(
                asyncio.to_thread(
                    self.gemini_client.chat_completion,
                    messages=messages,
                    response_format="json",
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            )
            
            # Wait for both responses
            gpt_response, gemini_response = await asyncio.gather(
                gpt_task, gemini_task, return_exceptions=True
            )
            
            # Handle errors
            if isinstance(gpt_response, Exception):
                logger.error(f"GPT-4 error: {gpt_response}")
                gpt_response = None
            
            if isinstance(gemini_response, Exception):
                logger.error(f"Gemini error: {gemini_response}")
                gemini_response = None
            
            # Combine evaluations
            combined_evaluation = self._combine_evaluations(gpt_response, gemini_response)
            
            return combined_evaluation
            
        except Exception as e:
            logger.error(f"Hybrid evaluation error: {e}")
            # Fallback to GPT-4
            return self.openai_client.chat_completion(
                messages=messages,
                response_format="json",
                temperature=temperature,
                max_tokens=max_tokens
            )
    
    def _select_best_question(
        self,
        gpt_question: Optional[str],
        gemini_question: Optional[str]
    ) -> str:
        """
        Select the best question from both models.
        
        Criteria:
        1. Length: Prefer questions that are detailed but not too long
        2. Specificity: Prefer questions with specific terms/numbers
        3. Clarity: Prefer questions that are clear and well-structured
        
        Args:
            gpt_question: Question from GPT-4
            gemini_question: Question from Gemini
        
        Returns:
            str: The best question
        """
        # If only one is available, use it
        if not gpt_question:
            logger.info("✅ Selected: Gemini (GPT-4 unavailable)")
            return gemini_question or "Error: No question generated"
        
        if not gemini_question:
            logger.info("✅ Selected: GPT-4 (Gemini unavailable)")
            return gpt_question
        
        # Score both questions
        gpt_score = self._score_question(gpt_question)
        gemini_score = self._score_question(gemini_question)
        
        logger.info(f"📊 Question scores - GPT-4: {gpt_score:.2f}, Gemini: {gemini_score:.2f}")
        
        # Select the better one
        if gpt_score >= gemini_score:
            logger.info("✅ Selected: GPT-4 (higher quality score)")
            return gpt_question
        else:
            logger.info("✅ Selected: Gemini (higher quality score)")
            return gemini_question
    
    def _score_question(self, question: str) -> float:
        """
        Score a question based on quality metrics.
        
        Args:
            question: The question text
        
        Returns:
            float: Quality score (0-100)
        """
        if not question:
            return 0.0
        
        score = 50.0  # Base score
        
        # Length score (prefer 50-150 characters)
        length = len(question)
        if 50 <= length <= 150:
            score += 20
        elif 30 <= length <= 200:
            score += 10
        
        # Specificity score (has numbers, technical terms)
        if any(char.isdigit() for char in question):
            score += 10
        
        # Question word score (starts with What, How, Why, etc.)
        question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who', 'can', 'could', 'would', 'should', 'explain', 'describe', 'analyze']
        if any(question.lower().startswith(word) for word in question_words):
            score += 15
        
        # Clarity score (has proper punctuation)
        if question.endswith('?'):
            score += 5
        
        return min(score, 100.0)
    
    def _combine_evaluations(
        self,
        gpt_eval: Optional[str],
        gemini_eval: Optional[str]
    ) -> str:
        """
        Combine evaluations from both models into a superior evaluation.
        
        Strategy:
        1. Parse both JSON responses
        2. Average the scores
        3. Combine feedback (take best parts from each)
        4. Use consensus for correctness
        
        Args:
            gpt_eval: Evaluation JSON from GPT-4
            gemini_eval: Evaluation JSON from Gemini
        
        Returns:
            str: Combined evaluation JSON
        """
        # If only one is available, use it
        if not gpt_eval:
            logger.info("✅ Using: Gemini evaluation (GPT-4 unavailable)")
            return gemini_eval or '{"error": "No evaluation generated"}'
        
        if not gemini_eval:
            logger.info("✅ Using: GPT-4 evaluation (Gemini unavailable)")
            return gpt_eval
        
        try:
            # Parse both evaluations
            gpt_data = json.loads(gpt_eval)
            gemini_data = json.loads(gemini_eval)
            
            # Combine scores (weighted average: GPT-4 60%, Gemini 40%)
            gpt_score = gpt_data.get("score", 0)
            gemini_score = gemini_data.get("score", 0)
            combined_score = int(gpt_score * 0.6 + gemini_score * 0.4)
            
            # Consensus on correctness
            gpt_correct = gpt_data.get("is_correct", False)
            gemini_correct = gemini_data.get("is_correct", False)
            combined_correct = gpt_correct and gemini_correct  # Both must agree for "correct"
            
            # Combine feedback (merge insights from both)
            gpt_feedback = gpt_data.get("feedback_text", "")
            gemini_feedback = gemini_data.get("feedback_text", "")
            
            # Create comprehensive feedback
            combined_feedback = self._merge_feedback(gpt_feedback, gemini_feedback)
            
            # Use GPT-4's difficulty suggestion (more conservative)
            suggested_difficulty = gpt_data.get("suggested_difficulty", "Medium")
            
            # Create combined result
            combined_result = {
                "score": combined_score,
                "is_correct": combined_correct,
                "feedback_text": combined_feedback,
                "suggested_difficulty": suggested_difficulty
            }
            
            logger.info(f"✅ Combined evaluation - Score: {combined_score}, Correct: {combined_correct}")
            
            return json.dumps(combined_result)
            
        except Exception as e:
            logger.error(f"Error combining evaluations: {e}")
            # Fallback to GPT-4
            logger.info("⚠️  Fallback to GPT-4 evaluation")
            return gpt_eval
    
    def _merge_feedback(self, gpt_feedback: str, gemini_feedback: str) -> str:
        """
        Merge feedback from both models into comprehensive feedback.
        
        Args:
            gpt_feedback: Feedback from GPT-4
            gemini_feedback: Feedback from Gemini
        
        Returns:
            str: Merged feedback
        """
        # If one is significantly longer, prefer it
        if len(gpt_feedback) > len(gemini_feedback) * 1.5:
            return gpt_feedback
        elif len(gemini_feedback) > len(gpt_feedback) * 1.5:
            return gemini_feedback
        
        # Otherwise, combine unique insights
        # For now, prefer GPT-4's feedback as it's typically more structured
        # In future, could use NLP to extract unique points from each
        return gpt_feedback
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "text",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Synchronous wrapper for hybrid generation.
        
        Args:
            messages: Conversation messages
            response_format: 'text' or 'json'
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        
        Returns:
            str: Generated response
        """
        # Run async function in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if response_format == "json":
            return loop.run_until_complete(
                self.evaluate_answer_hybrid(messages, temperature, max_tokens)
            )
        else:
            return loop.run_until_complete(
                self.generate_question_hybrid(messages, temperature)
            )
