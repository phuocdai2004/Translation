"""
Text-to-Speech Routes using Edge TTS
Provides high-quality voice synthesis for Vietnamese and English
"""

import io
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import edge_tts
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["text-to-speech"])

# Voice mappings for different languages
VOICES = {
    "vi": {
        "name": "Vietnamese Female",
        "voice": "vi-VN-HoaiMyNeural",
    },
    "vi-male": {
        "name": "Vietnamese Male",
        "voice": "vi-VN-NamMinhNeural",
    },
    "en": {
        "name": "English Female",
        "voice": "en-US-AriaNeural",
    },
    "en-male": {
        "name": "English Male",
        "voice": "en-US-GuyNeural",
    },
    "en-uk": {
        "name": "English UK",
        "voice": "en-GB-SoniaNeural",
    },
}


class TTSRequest(BaseModel):
    text: str
    language: str = "vi"  # Default: Vietnamese
    voice: str = None  # Optional: specific voice
    rate: float = 1.0  # Speed: 0.5 to 2.0
    pitch: int = 0  # Pitch: -50 to 50


@router.post("/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return audio file
    
    Args:
        text: Text to convert
        language: Language code (vi, en, etc.)
        voice: Specific voice (optional)
        rate: Speech rate (0.5 to 2.0)
        pitch: Pitch adjustment (-50 to 50)
    
    Returns:
        Audio stream (mp3)
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        # Determine voice
        voice_key = request.voice if request.voice and request.voice in VOICES else request.language
        
        if voice_key not in VOICES:
            raise HTTPException(status_code=400, detail=f"Unsupported language/voice: {voice_key}")
        
        voice_name = VOICES[voice_key]["voice"]
        
        # Validate rate and pitch
        if not (0.5 <= request.rate <= 2.0):
            raise HTTPException(status_code=400, detail="Rate must be between 0.5 and 2.0")
        
        if not (-50 <= request.pitch <= 50):
            raise HTTPException(status_code=400, detail="Pitch must be between -50 and 50")
        
        # Generate speech
        logger.info(f"TTS: Converting text to speech | Voice: {voice_name} | Rate: {request.rate}")
        
        # Format rate and pitch for edge-tts
        rate_percent = int((request.rate - 1.0) * 100)
        
        communicate = edge_tts.Communicate(
            text=request.text,
            voice=voice_name,
            rate=f"{rate_percent:+d}%" if rate_percent != 0 else "+0%",
            pitch=f"{request.pitch:+d}Hz" if request.pitch != 0 else "+0Hz",
        )
        
        # Stream to bytes
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        
        logger.info(f"✓ TTS successful | {len(request.text)} chars -> {audio_data.getbuffer().nbytes} bytes")
        
        return StreamingResponse(
            iter([audio_data.getvalue()]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Content-Length": str(len(audio_data.getvalue())),
            },
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ TTS Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available voices
    
    Returns:
        List of available voices with descriptions
    """
    return {
        "vietnamese": [
            {
                "key": "vi",
                "name": VOICES["vi"]["name"],
                "voice": VOICES["vi"]["voice"],
            },
            {
                "key": "vi-male",
                "name": VOICES["vi-male"]["name"],
                "voice": VOICES["vi-male"]["voice"],
            },
        ],
        "english": [
            {
                "key": "en",
                "name": VOICES["en"]["name"],
                "voice": VOICES["en"]["voice"],
            },
            {
                "key": "en-male",
                "name": VOICES["en-male"]["name"],
                "voice": VOICES["en-male"]["voice"],
            },
            {
                "key": "en-uk",
                "name": VOICES["en-uk"]["name"],
                "voice": VOICES["en-uk"]["voice"],
            },
        ],
    }


@router.get("/health")
async def tts_health():
    """Health check for TTS service"""
    return {
        "status": "ok",
        "service": "text-to-speech",
        "available_voices": len(VOICES),
        "languages": ["Vietnamese", "English"],
    }
