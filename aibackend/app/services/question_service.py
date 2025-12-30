"""
Question Service

This module provides question generation functionality using Hybrid AI (GPT-4 + Gemini).
It generates questions appropriate to the specified topic and difficulty level.
"""

from uuid import uuid4
from app.models import Question, Difficulty
from app.clients.hybrid_ai_client import HybridAIClient
from app.exceptions import QuestionGenerationError, OpenAIAPIError
from config.settings import Settings


class QuestionService:
    """
    Service for generating assessment questions using Hybrid AI (GPT-4 + Gemini).
    
    This service uses both GPT-4 and Gemini to:
    - Generate questions based on topic and difficulty level
    - Select the best question from both models
    - Ensure questions are appropriate for the specified difficulty
    - Assign unique identifiers to each question
    """
    
    def __init__(self, ai_client: HybridAIClient, dev_mode: bool = False):
        """
        Initialize the question service.
        
        Args:
            ai_client: Hybrid AI client for making API calls
            dev_mode: Enable development mode with mock responses
        """
        self.ai_client = ai_client
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
                        "content": "You are an expert educator and assessment designer with deep knowledge across multiple subjects. "
                                  "Your questions are known for being clear, focused, and educational. "
                                  "You create questions that test genuine understanding and help students learn through practice. "
                                  "Generate questions that are specific, practical, and appropriate to the difficulty level."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                question_text = self.ai_client.chat_completion(
                    messages=messages,
                    response_format="text",
                    temperature=0.9  # High temperature for maximum variety and creativity
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
        
        # Difficulty-specific guidelines
        difficulty_guidelines = {
            Difficulty.EASY: """
**EASY Level Guidelines:**
- Focus on FUNDAMENTAL concepts and basic definitions
- Test recall and basic comprehension
- Questions should be answerable with 2-3 sentences
- Examples: "What is...", "Define...", "List the main components of...", "Explain the basic purpose of..."
- Avoid: Complex scenarios, multi-step reasoning, advanced terminology
- Target: Someone learning the topic for the first time
""",
            Difficulty.MEDIUM: """
**MEDIUM Level Guidelines:**
- Focus on PRACTICAL APPLICATION and understanding relationships
- Test how concepts work together and why they matter
- Questions should require 3-4 sentences with examples
- Examples: "How does... work in practice?", "Why is... important for...", "Compare... and...", "What happens when..."
- Include: Real-world scenarios, cause-and-effect, practical implications
- Target: Someone with basic knowledge who needs to apply it
""",
            Difficulty.HARD: """
**HARD Level Guidelines:**
- Focus on ADVANCED ANALYSIS, evaluation, and synthesis
- Test deep understanding, trade-offs, and complex problem-solving
- Questions should require 4-5 sentences with detailed reasoning
- Examples: "Analyze the trade-offs between...", "Design a solution for...", "Evaluate the impact of...", "How would you optimize..."
- Include: Edge cases, system design, architectural decisions, performance considerations
- Target: Someone with solid understanding who can think critically
"""
        }
        
        prompt = f"""Generate a high-quality {difficulty.value} level interview question about {topic}.

{difficulty_guidelines[difficulty]}

**Topic Context: {topic}**

**Question Quality Requirements:**
1. SPECIFICITY: Focus on ONE specific aspect of {topic}, not general overview
2. CLARITY: Make it crystal clear what you're asking - no ambiguity
3. RELEVANCE: Ensure it's practical and commonly encountered in real scenarios
4. DEPTH: Match the complexity to the difficulty level exactly
5. VARIETY: Avoid generic questions - be creative and specific
6. EDUCATIONAL: Answering should reinforce learning and understanding

**Question Structure:**
- Start with a clear question word (What, How, Why, When, etc.)
- Be specific about the context or scenario
- Keep it concise but complete (1-2 sentences max)
- Make it conversational and natural for an interview setting

**Examples of GOOD questions by difficulty:**

EASY:
- "What is the main purpose of {topic} in modern applications?"
- "Can you explain what happens when you use {topic} for the first time?"
- "What are the three key components that make up {topic}?"

MEDIUM:
- "How would you implement {topic} in a production environment with 1000 users?"
- "Why might a developer choose {topic} over alternative approaches?"
- "What are the common pitfalls when working with {topic}, and how do you avoid them?"

HARD:
- "Design a scalable architecture using {topic} that handles 1 million requests per day. What are your key considerations?"
- "Analyze the performance trade-offs between different {topic} implementations in high-concurrency scenarios."
- "How would you debug a complex issue in {topic} where standard approaches aren't working?"

**Examples of BAD questions to AVOID:**
- Too vague: "Tell me about {topic}" (not specific enough)
- Too broad: "Explain everything about {topic}" (too general)
- Too simple for level: "What is {topic}?" (for Hard difficulty)
- Too complex for level: "Design a distributed system..." (for Easy difficulty)

**IMPORTANT:**
- Generate a UNIQUE question - don't repeat common interview questions
- Match the difficulty level EXACTLY - Easy should be genuinely easy, Hard should be genuinely challenging
- Make it INTERVIEW-STYLE - conversational and natural
- Focus on ONE clear concept or scenario

Return ONLY the question text - no preamble, no explanation, no formatting marks, no quotes."""
        
        return prompt


def create_question_service(settings: Settings) -> QuestionService:
    """
    Factory function to create a QuestionService instance.
    
    Args:
        settings: Application settings
    
    Returns:
        QuestionService: Configured question service instance
    """
    ai_client = HybridAIClient(settings)
    return QuestionService(ai_client)
