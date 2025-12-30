"""
Avatar API Router

Endpoints for generating realistic talking avatars with D-ID.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.did_avatar_service import did_avatar_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/avatar", tags=["avatar"])


class AvatarRequest(BaseModel):
    """Request model for creating talking avatar"""
    text: str
    emotion: Optional[str] = "neutral"


class AvatarResponse(BaseModel):
    """Response model for avatar creation"""
    video_url: Optional[str]
    talk_id: Optional[str]
    status: str
    error: Optional[str] = None


@router.post("/create", response_model=AvatarResponse)
async def create_talking_avatar(request: AvatarRequest):
    """
    Create a talking avatar video with D-ID
    
    The avatar will speak the provided text with lip-sync and facial expressions.
    
    Args:
        request: Avatar creation request with text and emotion
    
    Returns:
        Video URL and status
    """
    try:
        logger.info(f"Creating avatar for text: {request.text[:50]}...")
        
        result = did_avatar_service.create_talking_avatar(
            text=request.text,
            emotion=request.emotion
        )
        
        return AvatarResponse(**result)
        
    except Exception as e:
        logger.error(f"Error creating avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{talk_id}")
async def get_avatar_status(talk_id: str):
    """
    Get the status of an avatar generation
    
    Args:
        talk_id: The D-ID talk ID
    
    Returns:
        Status information
    """
    try:
        result = did_avatar_service.get_talk_status(talk_id)
        return result
    except Exception as e:
        logger.error(f"Error getting avatar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
