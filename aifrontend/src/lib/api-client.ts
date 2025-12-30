/**
 * API Client for AI Assessment Backend
 * 
 * This module provides a typed client for interacting with the FastAPI backend.
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Types matching backend models
export type Difficulty = 'Easy' | 'Medium' | 'Hard';

export interface StartSessionRequest {
  topic: string;
  initial_difficulty: Difficulty;
}

export interface StartSessionResponse {
  session_id: string;
  status: string;
  topic: string;
  initial_difficulty: Difficulty;
}

export interface QuestionResponse {
  question_id: string;
  question_text: string;
  difficulty: Difficulty;
}

export interface SubmitAnswerRequest {
  session_id: string;
  question_id: string;
  answer_text: string;
}

export interface SubmitAnswerResponse {
  score: number;
  is_correct: boolean;
  feedback_text: string;
  new_difficulty: Difficulty;
}

export interface TranscribeResponse {
  transcribed_text: string;
}

export interface VoiceFeedbackRequest {
  feedback_text: string;
}

export interface SessionSummary {
  session_id: string;
  topic: string;
  total_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  average_score: number;
  final_difficulty: Difficulty;
  performance_by_difficulty: {
    [key: string]: {
      correct: number;
      total: number;
    };
  };
  score_trend: number[];
}

export interface AvatarResponse {
  video_url: string | null;
  talk_id: string | null;
  status: string;
  error?: string;
}


// Error response type
export interface ErrorResponse {
  error_type: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * API Client class for backend communication
 */
export class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Start a new assessment session
   */
  async startSession(request: StartSessionRequest): Promise<StartSessionResponse> {
    const response = await fetch(`${this.baseURL}/start-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to start session');
    }

    return response.json();
  }

  /**
   * Get the next question for a session
   */
  async getNextQuestion(sessionId: string): Promise<QuestionResponse> {
    const response = await fetch(
      `${this.baseURL}/get-next-question?session_id=${encodeURIComponent(sessionId)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to get next question');
    }

    return response.json();
  }

  /**
   * Submit an answer for evaluation
   */
  async submitAnswer(request: SubmitAnswerRequest): Promise<SubmitAnswerResponse> {
    const response = await fetch(`${this.baseURL}/submit-answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to submit answer');
    }

    return response.json();
  }

  /**
   * Transcribe audio file to text
   */
  async transcribeAudio(audioFile: File): Promise<TranscribeResponse> {
    const formData = new FormData();
    formData.append('audio_file', audioFile);

    const response = await fetch(`${this.baseURL}/transcribe-audio`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to transcribe audio');
    }

    return response.json();
  }

  /**
   * Generate voice feedback from text
   */
  async generateVoiceFeedback(request: VoiceFeedbackRequest): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/generate-voice-feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to generate voice feedback');
    }

    return response.blob();
  }

  /**
   * Get session summary and results
   */
  async getSessionSummary(sessionId: string): Promise<SessionSummary> {
    const response = await fetch(
      `${this.baseURL}/session-summary/${encodeURIComponent(sessionId)}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to get session summary');
    }

    return response.json();
  }

  /**
   * Read question aloud using Lisa's voice
   */
  async readQuestion(questionText: string): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/read-question`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ feedback_text: questionText }),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to read question');
    }

    return response.blob();
  }

  /**
   * Create a talking avatar video with D-ID
   */
  async createTalkingAvatar(text: string, emotion: string = 'neutral'): Promise<AvatarResponse> {
    const response = await fetch(`${this.baseURL}/avatar/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, emotion }),
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to create avatar');
    }

    return response.json();
  }

  /**
   * Get avatar generation status
   */
  async getAvatarStatus(talkId: string): Promise<any> {
    const response = await fetch(`${this.baseURL}/avatar/status/${encodeURIComponent(talkId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error: ErrorResponse = await response.json();
      throw new Error(error.message || 'Failed to get avatar status');
    }

    return response.json();
  }
}

// Export singleton instance
export const apiClient = new APIClient();
