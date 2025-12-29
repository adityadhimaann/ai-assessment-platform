"""
Evaluation Service

This module provides answer evaluation functionality using OpenAI GPT-4o.
It evaluates student answers, provides feedback, and suggests difficulty adjustments.
"""

import json
from typing import Dict, Any
from app.models import EvaluationResult, Difficulty
from app.clients.openai_client import OpenAIClient
from app.exceptions import EvaluationError, OpenAIAPIError
from config.settings import Settings


class EvaluationService:
    """
    Service for evaluating student answers using AI.
    
    This service uses GPT-4o to:
    - Score student answers on a 0-100 scale
    - Determine correctness based on score threshold (>= 80)
    - Provide constructive feedback
    - Suggest difficulty adjustments for next questions
    """
    
    def __init__(self, openai_client: OpenAIClient, dev_mode: bool = False):
        """
        Initialize the evaluation service.
        
        Args:
            openai_client: OpenAI client for making API calls
            dev_mode: Enable development mode with mock responses
        """
        self.openai_client = openai_client
        self.dev_mode = dev_mode
        self.score_threshold = 80  # Score >= 80 is considered correct
    
    def evaluate_answer(
        self,
        question: str,
        answer: str,
        topic: str
    ) -> EvaluationResult:
        """
        Evaluate a student's answer using GPT-4o.
        
        This method sends the question and answer to GPT-4o for evaluation,
        receives a structured response with score and feedback, and parses
        it into an EvaluationResult.
        
        Args:
            question: The question text that was asked
            answer: The student's answer text
            topic: The topic/subject area of the question
        
        Returns:
            EvaluationResult: Structured evaluation with score, correctness,
                            feedback, and suggested difficulty
        
        Raises:
            EvaluationError: If evaluation fails or response is invalid
        """
        try:
            # Use mock response in dev mode
            if self.dev_mode:
                return self._generate_mock_evaluation(answer)
            
            # Build the evaluation prompt
            prompt = self._build_evaluation_prompt(question, answer, topic)
            
            # Call GPT-4o with JSON response format
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert educator and mentor who provides detailed, constructive feedback. "
                              "Your evaluations are fair, specific, and educational. You identify both strengths and areas for improvement. "
                              "Your feedback helps students understand not just what they got wrong, but how to improve and what to focus on. "
                              "You always respond with valid JSON in the exact format specified, with detailed 3-5 sentence feedback."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response_text = self.openai_client.chat_completion(
                messages=messages,
                response_format="json",
                temperature=0.3  # Lower temperature for more consistent evaluation
            )
            
            # Parse the response
            evaluation_result = self._parse_evaluation_response(response_text)
            
            return evaluation_result
        
        except OpenAIAPIError as e:
            raise EvaluationError(
                message=f"Failed to evaluate answer: {e.message}",
                original_error=e
            )
        except Exception as e:
            raise EvaluationError(
                message=f"Unexpected error during evaluation: {str(e)}",
                original_error=e
            )
    
    def _generate_mock_evaluation(self, answer: str) -> EvaluationResult:
        """
        Generate a mock evaluation for development/testing.
        
        Args:
            answer: The student's answer
        
        Returns:
            EvaluationResult: A mock evaluation result
        """
        import random
        
        # Generate a random score based on answer length (simple heuristic)
        answer_length = len(answer.strip())
        if answer_length < 20:
            score = random.randint(40, 60)
        elif answer_length < 100:
            score = random.randint(60, 85)
        else:
            score = random.randint(75, 95)
        
        is_correct = score >= self.score_threshold
        
        feedback_templates = [
            "Good effort! Your answer demonstrates understanding of the key concepts.",
            "Well done! You've covered the main points effectively.",
            "Nice work! Consider adding more detail to strengthen your response.",
            "Great answer! You've shown solid comprehension of the topic.",
        ] if is_correct else [
            "Your answer shows some understanding, but needs more detail.",
            "Consider reviewing the key concepts and try to be more specific.",
            "You're on the right track, but your answer could be more comprehensive.",
            "Good start! Try to elaborate more on the main points.",
        ]
        
        feedback = random.choice(feedback_templates)
        
        # Suggest difficulty based on score
        if score >= 85:
            suggested_difficulty = Difficulty.HARD
        elif score >= 70:
            suggested_difficulty = Difficulty.MEDIUM
        else:
            suggested_difficulty = Difficulty.EASY
        
        return EvaluationResult(
            score=score,
            is_correct=is_correct,
            feedback_text=feedback,
            suggested_difficulty=suggested_difficulty
        )
    
    def _build_evaluation_prompt(
        self,
        question: str,
        answer: str,
        topic: str
    ) -> str:
        """
        Build the evaluation prompt for GPT-4o.
        
        The prompt instructs GPT-4o to evaluate the answer and return
        a structured JSON response with score, correctness, feedback,
        and suggested difficulty.
        
        Args:
            question: The question text
            answer: The student's answer
            topic: The topic/subject area
        
        Returns:
            str: The formatted prompt for GPT-4o
        """
        prompt = f"""You are an expert educator evaluating a student's answer. Provide detailed, constructive feedback.

Topic: {topic}
Question: {question}
Student Answer: {answer}

Evaluation Criteria:
1. ACCURACY: Is the information factually correct?
2. COMPLETENESS: Does it cover all key aspects of the question?
3. CLARITY: Is the explanation clear and well-organized?
4. DEPTH: Does it show genuine understanding vs surface-level knowledge?
5. RELEVANCE: Does it directly address what was asked?

Provide:
1. A score from 0-100:
   - 90-100: Excellent - Accurate, complete, clear, shows deep understanding
   - 80-89: Good - Mostly correct with minor gaps or unclear points
   - 70-79: Satisfactory - Correct basics but missing depth or has some errors
   - 60-69: Needs improvement - Partial understanding with significant gaps
   - Below 60: Insufficient - Major misunderstandings or incomplete

2. Whether the answer is correct (score >= 80 is considered correct)

3. DETAILED, SPECIFIC feedback that includes:
   - What the student did WELL (be specific about correct points)
   - What was MISSING or INCORRECT (identify specific gaps or errors)
   - HOW TO IMPROVE (give actionable advice with examples)
   - KEY CONCEPTS to review or remember for next time
   - Make feedback 3-5 sentences, educational and encouraging

4. Suggested difficulty for next question:
   - If score >= 85: suggest "Hard" (student is ready for challenge)
   - If score >= 70: suggest "Medium" (student is progressing well)
   - If score < 70: suggest "Easy" (student needs more foundation)

Return your response as JSON with this exact structure:
{{
  "score": <integer from 0-100>,
  "is_correct": <boolean>,
  "feedback_text": "<detailed, specific, constructive feedback in 3-5 sentences>",
  "suggested_difficulty": "<Easy|Medium|Hard>"
}}

Important:
- Be SPECIFIC in feedback - mention actual concepts, not just "good job"
- Be CONSTRUCTIVE and ENCOURAGING - focus on learning, not just grading
- Give ACTIONABLE advice - tell them exactly what to add or change
- Consider PARTIAL CREDIT - reward correct elements even if incomplete
- Ensure JSON is valid and follows the exact structure above"""
        
        return prompt
    
    def _parse_evaluation_response(self, response_text: str) -> EvaluationResult:
        """
        Parse the GPT-4o evaluation response into an EvaluationResult.
        
        This method validates the JSON structure and ensures all required
        fields are present with correct types.
        
        Args:
            response_text: The JSON response from GPT-4o
        
        Returns:
            EvaluationResult: Parsed and validated evaluation result
        
        Raises:
            EvaluationError: If response is invalid or missing required fields
        """
        try:
            # Parse JSON response
            data = json.loads(response_text)
            
            # Validate required fields are present
            required_fields = ["score", "is_correct", "feedback_text", "suggested_difficulty"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                raise EvaluationError(
                    message=f"Response missing required fields: {', '.join(missing_fields)}"
                )
            
            # Extract and validate score
            score = data["score"]
            if not isinstance(score, int) or not (0 <= score <= 100):
                raise EvaluationError(
                    message=f"Invalid score value: {score}. Must be integer between 0-100"
                )
            
            # Extract and validate is_correct
            is_correct = data["is_correct"]
            if not isinstance(is_correct, bool):
                raise EvaluationError(
                    message=f"Invalid is_correct value: {is_correct}. Must be boolean"
                )
            
            # Extract and validate feedback_text
            feedback_text = data["feedback_text"]
            if not isinstance(feedback_text, str) or not feedback_text.strip():
                raise EvaluationError(
                    message="feedback_text must be a non-empty string"
                )
            
            # Extract and validate suggested_difficulty
            suggested_difficulty_str = data["suggested_difficulty"]
            try:
                suggested_difficulty = Difficulty(suggested_difficulty_str)
            except ValueError:
                raise EvaluationError(
                    message=f"Invalid suggested_difficulty: {suggested_difficulty_str}. "
                           f"Must be one of: Easy, Medium, Hard"
                )
            
            # Create and return EvaluationResult
            return EvaluationResult(
                score=score,
                is_correct=is_correct,
                feedback_text=feedback_text.strip(),
                suggested_difficulty=suggested_difficulty
            )
        
        except json.JSONDecodeError as e:
            raise EvaluationError(
                message=f"Failed to parse evaluation response as JSON: {str(e)}",
                original_error=e
            )
        except EvaluationError:
            # Re-raise EvaluationError as-is
            raise
        except Exception as e:
            raise EvaluationError(
                message=f"Unexpected error parsing evaluation response: {str(e)}",
                original_error=e
            )


def create_evaluation_service(settings: Settings) -> EvaluationService:
    """
    Factory function to create an EvaluationService instance.
    
    Args:
        settings: Application settings
    
    Returns:
        EvaluationService: Configured evaluation service instance
    """
    openai_client = OpenAIClient(settings)
    return EvaluationService(openai_client)
