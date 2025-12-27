"""
Audio API Router

This module provides REST API endpoints for audio transcription and
voice feedback generation.
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import Response
from typing import Annotated

from app.models import (
    TranscribeResponse,
    VoiceFeedbackRequest,
    VoiceFeedbackResponse
)
from app.services.audio_service import AudioService
from app.services.voice_service import VoiceService
from app.exceptions import (
    WhisperAPIError,
    TTSAPIError,
    AudioFileError,
    AssessmentError
)
from config.settings import get_settings, Settings


# Create router
router = APIRouter(
    prefix="/api",
    tags=["audio"]
)


# Dependency injection for services
def get_audio_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> AudioService:
    """Get AudioService instance"""
    return AudioService(settings)


def get_voice_service(
    settings: Annotated[Settings, Depends(get_settings)]
) -> VoiceService:
    """Get VoiceService instance"""
    return VoiceService(settings)


@router.post(
    "/transcribe-audio",
    response_model=TranscribeResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio to text",
    description="Convert audio file to text using Whisper API"
)
async def transcribe_audio(
    audio_file: Annotated[UploadFile, File(description="Audio file to transcribe")],
    audio_service: Annotated[AudioService, Depends(get_audio_service)]
) -> TranscribeResponse:
    """
    Transcribe an audio file to text.
    
    Accepts an audio file in supported formats (mp3, mp4, mpeg, mpga, m4a, wav, webm),
    validates the file, and transcribes it using OpenAI Whisper API.
    
    Args:
        audio_file: The uploaded audio file
        audio_service: Injected audio service
    
    Returns:
        TranscribeResponse: Transcribed text from the audio
    
    Raises:
        HTTPException: 400 for invalid file format/size, 500 for API errors
    
    Requirements: 7.4, 5.1
    """
    try:
        # Transcribe the audio
        transcribed_text = audio_service.transcribe_audio(audio_file)
        
        # Return response
        return TranscribeResponse(
            transcribed_text=transcribed_text
        )
    
    except AudioFileError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except WhisperAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )
    except AssessmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "InternalServerError",
                "message": f"Failed to transcribe audio: {str(e)}"
            }
        )


@router.post(
    "/generate-voice-feedback",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Generate voice feedback",
    description="Convert feedback text to audio using TTS service"
)
async def generate_voice_feedback(
    request: VoiceFeedbackRequest,
    voice_service: Annotated[VoiceService, Depends(get_voice_service)]
) -> Response:
    """
    Generate voice feedback from text.
    
    Converts the provided feedback text to audio using the configured
    TTS service (OpenAI or ElevenLabs) and returns the audio data.
    
    Args:
        request: Voice feedback request with feedback_text
        voice_service: Injected voice service
    
    Returns:
        Response: Audio data as MP3 with appropriate content type
    
    Raises:
        HTTPException: 400 for invalid parameters, 500 for API errors
    
    Requirements: 7.5, 6.1
    """
    try:
        # Generate voice feedback
        audio_data = voice_service.generate_voice_feedback(
            feedback_text=request.feedback_text
        )
        
        # Return audio as response with appropriate content type
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=feedback.mp3"
            }
        )
    
    except TTSAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.to_dict()
        )
    except AssessmentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.to_dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_type": "InternalServerError",
                "message": f"Failed to generate voice feedback: {str(e)}"
            }
        )
