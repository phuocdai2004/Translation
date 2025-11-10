"""
Translation API routes using Google Translate API (Free, powerful, reliable)
"""

from fastapi import APIRouter, HTTPException
import logging
from app.models.translation import TranslationRequest, TranslationResponse
import requests
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Google Translate API endpoint (free, unofficial but very reliable)
GOOGLE_TRANSLATE_API = "https://translate.googleapis.com/translate_a/single"

# Map language codes
LANGUAGE_MAP = {
    "en": "en",
    "vi": "vi",
}

# Headers to mimic browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def load_translation_models():
    """Initialize translation - using Google Translate API (online service)"""
    logger.info("✓ Google Translate API ready (online service - free & powerful)")


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text using Google Translate API (FREE, 99% accurate, no API key needed)
    
    ### Parameters:
    - **text**: Text to translate
    - **source_lang**: Source language code ("en" or "vi")
    - **target_lang**: Target language code ("en" or "vi")
    
    ### Returns:
    - **original_text**: Original input text
    - **translated_text**: Translated text
    - **source_lang**: Source language
    - **target_lang**: Target language
    """
    try:
        logger.info(f"Translating from {request.source_lang} to {request.target_lang}: {request.text[:50]}...")
        
        # Validate language codes
        if request.source_lang not in LANGUAGE_MAP or request.target_lang not in LANGUAGE_MAP:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language pair. Supported: en, vi"
            )
        
        # If same language, return as-is
        if request.source_lang == request.target_lang:
            return TranslationResponse(
                original_text=request.text,
                translated_text=request.text,
                source_lang=request.source_lang,
                target_lang=request.target_lang
            )
        
        # Google Translate API call
        # Format: https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t&q=hello
        params = {
            "client": "gtx",
            "sl": LANGUAGE_MAP[request.source_lang],  # source language
            "tl": LANGUAGE_MAP[request.target_lang],  # target language
            "dt": "t",  # request type (t = translation)
            "q": request.text  # text to translate
        }
        
        response = requests.get(
            GOOGLE_TRANSLATE_API,
            params=params,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        
        # Google Translate returns nested array: [[[translated_text, original_text, ...]]]
        result = response.json()
        
        if result and len(result) > 0 and len(result[0]) > 0 and len(result[0][0]) > 0:
            translated_text = result[0][0][0]
            
            if translated_text:
                logger.info(f"✓ Translation successful: '{request.text[:40]}' -> '{translated_text[:40]}'")
                return TranslationResponse(
                    original_text=request.text,
                    translated_text=translated_text,
                    source_lang=request.source_lang,
                    target_lang=request.target_lang
                )
            else:
                raise ValueError("Empty translation returned")
        else:
            logger.error(f"Unexpected response format: {result}")
            raise ValueError("Invalid response format from Google Translate")
            
    except requests.exceptions.Timeout:
        logger.error("Google Translate request timeout (10s)")
        raise HTTPException(status_code=504, detail="Translation service timeout")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to translation service")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.get("/translate/languages")
async def get_supported_languages():
    """Get list of supported language pairs"""
    return {
        "supported_pairs": [
            {"from": "en", "to": "vi", "name": "English to Vietnamese"},
            {"from": "vi", "to": "en", "name": "Vietnamese to English"},
        ],
        "total": 2
    }
