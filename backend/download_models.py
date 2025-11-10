"""
Download required ML models for translation and search
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_models():
    """Download required models from Hugging Face"""
    
    try:
        logger.info("Starting model download...")
        
        # Translation models
        logger.info("Downloading translation models...")
        print("Note: Model downloads are handled lazily on first use.")
        print("Required models:")
        print("- Helsinki-NLP/opus-mt-en-vi (English to Vietnamese)")
        print("- Helsinki-NLP/opus-mt-vi-en (Vietnamese to English)")
        print("- sentence-transformers/all-MiniLM-L6-v2 (Embeddings)")
        print("\nModels will be downloaded automatically on first API call.")
        
        logger.info("Model configuration completed")
        
    except Exception as e:
        logger.error(f"Error during model download: {e}")
        raise


if __name__ == "__main__":
    download_models()
