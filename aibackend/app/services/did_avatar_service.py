"""
D-ID Avatar Service

This module provides integration with D-ID API for realistic talking avatars with lip-sync.
"""

import os
import requests
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DIDAvatarService:
    """Service for creating talking avatars using D-ID API"""
    
    def __init__(self):
        self.base_url = "https://api.d-id.com"
        # Use D-ID's default presenter "Amy" - a professional female presenter
        # You can change this to any D-ID presenter ID
        self.lisa_presenter_id = "amy-jcwCkr1grs"
    
    def _get_headers(self):
        """Get headers with API key from environment"""
        api_key = os.getenv("DID_API_KEY")
        
        if not api_key:
            return None
            
        # D-ID API uses the key directly in Authorization header
        return {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        
    def create_talking_avatar(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: str = "neutral"
    ) -> Dict[str, Any]:
        """
        Create a talking avatar video with D-ID
        
        Args:
            text: The text for the avatar to speak
            voice_id: ElevenLabs voice ID (optional, uses default if not provided)
            emotion: Emotion for the avatar (neutral, happy, serious, friendly)
        
        Returns:
            Dict with video URL and talk ID
        """
        headers = self._get_headers()
        
        if not headers:
            logger.warning("D-ID API key not configured in environment")
            return {
                "video_url": None,
                "talk_id": None,
                "status": "disabled"
            }
        
        logger.info(f"D-ID API key configured, creating avatar...")
        
        try:
            # Use ElevenLabs voice if provided
            elevenlabs_voice = voice_id or os.getenv("ELEVENLABS_VOICE_ID")
            
            if elevenlabs_voice:
                voice_config = {
                    "type": "text",
                    "input": text,
                    "provider": {
                        "type": "elevenlabs",
                        "voice_id": elevenlabs_voice
                    }
                }
            else:
                # Use D-ID's default voice
                voice_config = {
                    "type": "text",
                    "input": text
                }
            
            # Create talk
            payload = {
                "script": voice_config,
                "presenter_id": self.lisa_presenter_id,
                "config": {
                    "stitch": True
                }
            }
            
            logger.info(f"Creating D-ID talk for text: {text[:50]}...")
            response = requests.post(
                f"{self.base_url}/talks",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 201:
                logger.error(f"D-ID API error: {response.status_code} - {response.text}")
                return {
                    "video_url": None,
                    "talk_id": None,
                    "status": "error",
                    "error": response.text
                }
            
            result = response.json()
            talk_id = result.get("id")
            
            logger.info(f"D-ID talk created with ID: {talk_id}")
            
            # Poll for completion (D-ID takes a few seconds to generate)
            video_url = self._wait_for_video(talk_id)
            
            return {
                "video_url": video_url,
                "talk_id": talk_id,
                "status": "ready" if video_url else "processing"
            }
            
        except Exception as e:
            logger.error(f"Error creating D-ID avatar: {e}")
            return {
                "video_url": None,
                "talk_id": None,
                "status": "error",
                "error": str(e)
            }
    
    def _wait_for_video(self, talk_id: str, max_wait: int = 30) -> Optional[str]:
        """
        Wait for D-ID to finish generating the video
        
        Args:
            talk_id: The talk ID from D-ID
            max_wait: Maximum seconds to wait
        
        Returns:
            Video URL or None if timeout
        """
        headers = self._get_headers()
        if not headers:
            return None
            
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/talks/{talk_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    if status == "done":
                        video_url = result.get("result_url")
                        logger.info(f"D-ID video ready: {video_url}")
                        return video_url
                    elif status == "error":
                        logger.error(f"D-ID generation failed: {result.get('error')}")
                        return None
                    
                    # Still processing, wait a bit
                    time.sleep(2)
                else:
                    logger.error(f"Error checking D-ID status: {response.status_code}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error polling D-ID status: {e}")
                return None
        
        logger.warning(f"D-ID video generation timeout for talk {talk_id}")
        return None
    
    def get_talk_status(self, talk_id: str) -> Dict[str, Any]:
        """
        Get the status of a D-ID talk
        
        Args:
            talk_id: The talk ID
        
        Returns:
            Status information
        """
        headers = self._get_headers()
        if not headers:
            return {"status": "error", "error": "API key not configured"}
            
        try:
            response = requests.get(
                f"{self.base_url}/talks/{talk_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "error": response.text
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
did_avatar_service = DIDAvatarService()
