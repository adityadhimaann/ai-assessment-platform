# Implementation Plan: AI Assessment Backend

## Overview

This implementation plan breaks down the AI Assessment Backend into discrete coding tasks. Each task builds on previous work, with incremental validation through tests. The implementation follows a bottom-up approach: core models → services → API endpoints → integration.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create project directory structure (app/, tests/, config/)
  - Create requirements.txt with FastAPI, OpenAI SDK, Pydantic, Hypothesis, pytest
  - Create .env.example file with required environment variables
  - Create main.py with basic FastAPI application setup
  - _Requirements: 8.1, 8.2, 8.5_

- [x] 2. Implement configuration management
  - [x] 2.1 Create config/settings.py with Pydantic Settings class
    - Define all environment variables with types and defaults
    - Implement validation for required variables
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 2.2 Write unit tests for configuration loading
    - Test with valid environment variables
    - Test with missing required variables
    - Test default values
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Implement core data models
  - [x] 3.1 Create app/models.py with Pydantic models
    - Define Difficulty enum
    - Define PerformanceRecord model
    - Define Session model
    - Define EvaluationResult model
    - Define Question model
    - Define all API request/response models
    - _Requirements: 1.1, 1.2, 2.6, 4.3, 10.1, 10.2, 10.3_
  
  - [x] 3.2 Write property test for data model validation
    - **Property 16: Comprehensive input validation**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.5, 7.6**
  
  - [x] 3.3 Write unit tests for model edge cases
    - Test UUID validation
    - Test enum validation
    - Test required field validation
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 4. Implement custom exceptions
  - [x] 4.1 Create app/exceptions.py with custom exception classes
    - Define AssessmentError base class
    - Define SessionNotFoundError
    - Define InvalidDifficultyError
    - Define OpenAIAPIError, WhisperAPIError, TTSAPIError
    - Define ValidationError
    - _Requirements: 9.2_
  
  - [x] 4.2 Write property test for error response structure
    - **Property 18: Error responses have required structure**
    - **Validates: Requirements 9.2**

- [x] 5. Implement Session Service
  - [x] 5.1 Create app/services/session_service.py
    - Implement create_session() method
    - Implement get_session() method
    - Implement update_session_performance() method
    - Implement calculate_new_difficulty() method with adaptive logic
    - Implement get_current_difficulty() method
    - Use in-memory dictionary for session storage
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.2 Write property test for session creation
    - **Property 1: Session creation produces unique identifiers**
    - **Validates: Requirements 1.1, 1.3**
  
  - [x] 5.3 Write property test for session initialization
    - **Property 2: Session initialization preserves input parameters**
    - **Validates: Requirements 1.2**
  
  - [x] 5.4 Write property test for session round-trip
    - **Property 3: Session round-trip consistency**
    - **Validates: Requirements 1.3, 1.5**
  
  - [x] 5.5 Write property test for invalid session IDs
    - **Property 4: Invalid session IDs produce errors**
    - **Validates: Requirements 1.4**
  
  - [x] 5.6 Write property test for difficulty persistence
    - **Property 8: Difficulty updates are persisted**
    - **Validates: Requirements 3.4**
  
  - [x] 5.7 Write unit tests for adaptive difficulty logic
    - Test Medium to Hard transition (2 correct at Medium)
    - Test Hard to Medium transition (2 incorrect at Hard)
    - Test Medium to Easy transition (2 incorrect at Medium)
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Checkpoint - Ensure session service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement OpenAI Client
  - [x] 7.1 Create app/clients/openai_client.py
    - Initialize OpenAI client with API key from settings
    - Implement chat_completion() method with JSON response format support
    - Implement error handling and retry logic
    - _Requirements: 2.1, 4.2, 8.1_
  
  - [x] 7.2 Write unit tests with mocked OpenAI API
    - Test successful API calls
    - Test API error handling
    - Test retry logic
    - _Requirements: 2.1, 2.5_

- [x] 8. Implement Evaluation Service
  - [x] 8.1 Create app/services/evaluation_service.py
    - Implement evaluate_answer() method
    - Implement _build_evaluation_prompt() helper
    - Implement _parse_evaluation_response() helper
    - Use OpenAI client for GPT-4o calls
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [x] 8.2 Write property test for score threshold
    - **Property 5: Score threshold determines correctness**
    - **Validates: Requirements 2.3, 2.4**
  
  - [x] 8.3 Write property test for evaluation response completeness
    - **Property 6: Evaluation responses contain all required fields**
    - **Validates: Requirements 2.6**
  
  - [x] 8.4 Write property test for response parsing
    - **Property 7: Evaluation response parsing preserves data**
    - **Validates: Requirements 2.2**
  
  - [x] 8.5 Write unit tests with mocked GPT-4o
    - Test evaluation with correct answer
    - Test evaluation with incorrect answer
    - Test API error handling
    - _Requirements: 2.1, 2.5_

- [x] 9. Implement Question Service
  - [x] 9.1 Create app/services/question_service.py
    - Implement generate_question() method
    - Implement _build_question_prompt() helper
    - Use OpenAI client for GPT-4o calls
    - Generate unique question IDs
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 9.2 Write property test for question response structure
    - **Property 10: Generated questions have required fields**
    - **Validates: Requirements 4.3**
  
  - [x] 9.3 Write property test for difficulty usage
    - **Property 9: Question generation uses current session difficulty**
    - **Validates: Requirements 3.5, 4.1**
  
  - [x] 9.4 Write unit tests with mocked GPT-4o
    - Test question generation for each difficulty level
    - Test API error handling
    - _Requirements: 4.2, 4.4_

- [x] 10. Checkpoint - Ensure core services tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [-] 11. Implement Audio Service
  - [x] 11.1 Create app/services/audio_service.py
    - Implement transcribe_audio() method
    - Implement _validate_audio_file() helper
    - Use OpenAI Whisper API for transcription
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.4_
  
  - [x] 11.2 Write property test for audio format validation (supported)
    - **Property 11: Audio format validation accepts supported formats**
    - **Validates: Requirements 5.1**
  
  - [x] 11.3 Write property test for audio format validation (unsupported)
    - **Property 12: Audio format validation rejects unsupported formats**
    - **Validates: Requirements 5.1, 5.4**
  
  - [x] 11.4 Write property test for file size validation
    - **Property 13: Audio file size validation enforces limit**
    - **Validates: Requirements 10.4**
  
  - [x] 11.5 Write property test for transcription response
    - **Property 14: Transcription response returns text**
    - **Validates: Requirements 5.3**
  
  - [x] 11.6 Write unit tests with mocked Whisper API
    - Test successful transcription
    - Test API error handling
    - _Requirements: 5.2, 5.5_

- [x] 12. Implement Voice Service
  - [x] 12.1 Create app/services/voice_service.py
    - Implement generate_voice_feedback() method
    - Implement _call_tts_api() helper
    - Support ElevenLabs or OpenAI TTS based on configuration
    - _Requirements: 6.1, 6.2, 6.4, 6.5_
  
  - [x] 12.2 Write property test for voice feedback response
    - **Property 15: Voice feedback generation returns valid response**
    - **Validates: Requirements 6.2**
  
  - [x] 12.3 Write unit tests with mocked TTS API
    - Test successful audio generation
    - Test streaming support
    - Test API error handling
    - _Requirements: 6.1, 6.4, 6.5_

- [x] 13. Implement API endpoints
  - [x] 13.1 Create app/routers/assessment.py with FastAPI router
    - Implement POST /start-session endpoint
    - Implement GET /get-next-question endpoint
    - Implement POST /submit-answer endpoint
    - Wire up Session Service, Evaluation Service, Question Service
    - _Requirements: 7.1, 7.2, 7.3, 1.1, 2.1, 4.1_
  
  - [x] 13.2 Create app/routers/audio.py with FastAPI router
    - Implement POST /transcribe-audio endpoint
    - Implement POST /generate-voice-feedback endpoint
    - Wire up Audio Service and Voice Service
    - _Requirements: 7.4, 7.5, 5.1, 6.1_
  
  - [x] 13.3 Write property test for invalid parameters
    - **Property 17: Invalid parameters return 400 status**
    - **Validates: Requirements 7.6**
  
  - [x] 13.4 Write unit tests for endpoint existence
    - Test all endpoints are registered
    - Test endpoint parameter acceptance
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 13.5 Write unit tests for error status codes
    - Test 400 for invalid parameters
    - Test 404 for session not found
    - Test 422 for validation errors
    - Test 500 for server errors
    - _Requirements: 7.6, 7.7_

- [x] 14. Implement error handling middleware
  - [x] 14.1 Create app/middleware/error_handler.py
    - Implement global exception handler
    - Map exceptions to HTTP status codes
    - Return structured error responses
    - _Requirements: 9.2, 7.6, 7.7_
  
  - [x] 14.2 Write unit tests for error handling
    - Test each exception type returns correct status code
    - Test error response structure
    - _Requirements: 9.2_

- [x] 15. Implement logging
  - [x] 15.1 Create app/utils/logger.py
    - Configure structured logging with appropriate levels
    - Implement request logging middleware
    - Implement response logging middleware
    - Log external API calls and errors
    - _Requirements: 9.1, 9.3, 9.4, 9.5_
  
  - [x] 15.2 Write unit tests for logging behavior
    - Test request logging
    - Test response logging
    - Test error logging
    - Test log levels
    - _Requirements: 9.1, 9.3, 9.4, 9.5_

- [ ] 16. Wire everything together in main.py
  - [x] 16.1 Update main.py
    - Import and register routers
    - Add error handling middleware
    - Add logging middleware
    - Add CORS middleware for frontend integration
    - Configure startup validation for environment variables
    - _Requirements: 8.3, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 16.2 Write integration tests
    - Test complete flow: start session → get question → submit answer
    - Test session state persistence across requests
    - Test adaptive difficulty across multiple questions
    - _Requirements: 1.1, 2.1, 3.1, 3.2, 3.3, 4.1_

- [x] 17. Final checkpoint - Ensure all tests pass
  - Run full test suite with coverage report
  - Verify minimum 80% code coverage
  - Ensure all property tests run 100+ iterations
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests use Hypothesis library with minimum 100 iterations
- Unit tests use pytest with mocking for external APIs
- Integration tests verify end-to-end flows
- All tests should be tagged with feature name and property number where applicable