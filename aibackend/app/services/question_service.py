"""
Question Service

This module provides question generation functionality using OpenAI GPT-4o.
It generates questions appropriate to the specified topic and difficulty level.
"""

from uuid import uuid4
from app.models import Question, Difficulty
from app.clients.openai_client import OpenAIClient
from app.exceptions import QuestionGenerationError, OpenAIAPIError
from config.settings import Settings


class QuestionService:
    """
    Service for generating assessment questions using AI.
    
    This service uses GPT-4o to:
    - Generate questions based on topic and difficulty level
    - Ensure questions are appropriate for the specified difficulty
    - Assign unique identifiers to each question
    """
    
    def __init__(self, openai_client: OpenAIClient, dev_mode: bool = False):
        """
        Initialize the question service.
        
        Args:
            openai_client: OpenAI client for making API calls
            dev_mode: Enable development mode with mock responses
        """
        self.openai_client = openai_client
        self.dev_mode = dev_mode
    
    def generate_question(
        self,
        topic: str,
        difficulty: Difficulty
    ) -> Question:
        """
        Generate a question using GPT-4o.
        
        This method sends a prompt to GPT-4o to create a question based on
        the specified topic and difficulty level, then returns a Question
        object with a unique ID.
        
        Args:
            topic: The topic/subject area for the question
            difficulty: The difficulty level (Easy, Medium, or Hard)
        
        Returns:
            Question: Generated question with unique ID, text, difficulty, and topic
        
        Raises:
            QuestionGenerationError: If question generation fails or response is invalid
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        try:
            # Generate unique question ID
            question_id = str(uuid4())
            
            # Use mock response in dev mode
            if self.dev_mode:
                question_text = self._generate_mock_question(topic, difficulty)
            else:
                # Build the question generation prompt
                prompt = self._build_question_prompt(topic, difficulty)
                
                # Call GPT-4o
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert educator creating assessment questions. "
                                  "Generate clear, well-formed questions appropriate to the "
                                  "specified difficulty level and topic."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                question_text = self.openai_client.chat_completion(
                    messages=messages,
                    response_format="text",
                    temperature=0.8  # Higher temperature for more varied questions
                )
                
                # Validate the response
                question_text = question_text.strip()
                if not question_text:
                    raise QuestionGenerationError(
                        message="Received empty question text from GPT-4o"
                    )
            
            # Create and return Question object
            question = Question(
                question_id=question_id,
                question_text=question_text,
                difficulty=difficulty,
                topic=topic
            )
            
            return question
        
        except OpenAIAPIError as e:
            raise QuestionGenerationError(
                message=f"Failed to generate question: {e.message}",
                original_error=e
            )
        except Exception as e:
            raise QuestionGenerationError(
                message=f"Unexpected error during question generation: {str(e)}",
                original_error=e
            )
    
    def _generate_mock_question(self, topic: str, difficulty: Difficulty) -> str:
        """
        Generate a mock question for development/testing.
        
        Args:
            topic: The topic/subject area
            difficulty: The difficulty level
        
        Returns:
            str: A mock question appropriate to the difficulty level
        """
        mock_questions = {
            Difficulty.EASY: [
                f"What is {topic}?",
                f"Can you define {topic} in your own words?",
                f"What are the basic concepts of {topic}?",
            ],
            Difficulty.MEDIUM: [
                f"How does {topic} work in practice?",
                f"What are the key applications of {topic}?",
                f"Explain the relationship between {topic} and related concepts.",
            ],
            Difficulty.HARD: [
                f"Analyze the implications of {topic} on modern technology.",
                f"Compare and contrast different approaches to {topic}.",
                f"Evaluate the challenges and future directions of {topic}.",
            ]
        }
        
        import random
        questions = mock_questions.get(difficulty, mock_questions[Difficulty.MEDIUM])
        return random.choice(questions)
    
    def _build_question_prompt(
        self,
        topic: str,
        difficulty: Difficulty
    ) -> str:
        """
        Build the question generation prompt for GPT-4o.
        
        The prompt instructs GPT-4o to generate a question appropriate
        to the specified topic and difficulty level.
        
        Args:
            topic: The topic/subject area
            difficulty: The difficulty level
        
        Returns:
            str: The formatted prompt for GPT-4o
        """
        prompt = f"""Generate a {difficulty.value} level question about {topic}.

Difficulty Guidelines:
- Easy: Basic concepts, definitions, recall of fundamental information. Questions should test understanding of core terminology and simple facts.
- Medium: Application of concepts, analysis of relationships, understanding of how ideas connect. Questions should require reasoning and explanation.
- Hard: Complex problem-solving, synthesis of multiple concepts, evaluation and critical thinking. Questions should challenge deep understanding and require sophisticated analysis.

Requirements:
- The question should be clear and unambiguous
- It should be appropriate for the {difficulty.value} difficulty level
- It should be directly related to {topic}
- It should be answerable in a few sentences or a short paragraph
- Do not include multiple choice options - this should be an open-ended question

Return only the question text, with no additional formatting, preamble, or explanation."""
        
        return prompt


def create_question_service(settings: Settings) -> QuestionService:
    """
    Factory function to create a QuestionService instance.
    
    Args:
        settings: Application settings
    
    Returns:
        QuestionService: Configured question service instance
    """
    openai_client = OpenAIClient(settings)
    return QuestionService(openai_client)
