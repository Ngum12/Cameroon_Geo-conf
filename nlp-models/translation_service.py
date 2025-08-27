#!/usr/bin/env python3
"""
Translation Service for Project Sentinel
Cameroon Defense Force OSINT Analysis System

FastAPI service for translating text to English using Facebook's M2M100 model.
Supports automatic language detection and translation of news articles.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from transformers import pipeline, M2M100ForConditionalGeneration, M2M100Tokenizer
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import torch
from typing import Optional, Dict, Any
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for model and pipeline
translation_pipeline = None
model_info = {}

# Request/Response models
class TranslationRequest(BaseModel):
    """Request model for translation endpoint."""
    text: str = Field(..., description="Text to translate", min_length=1, max_length=10000)
    source_lang: str = Field(default="auto", description="Source language code or 'auto' for detection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Bonjour, comment allez-vous?",
                "source_lang": "auto"
            }
        }

class TranslationResponse(BaseModel):
    """Response model for translation endpoint."""
    translated_text: str = Field(..., description="Translated text in English")
    detected_language: Optional[str] = Field(None, description="Detected source language")
    confidence_score: Optional[float] = Field(None, description="Translation confidence")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "Hello, how are you?",
                "detected_language": "fr",
                "confidence_score": 0.95,
                "processing_time": 1.23
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    model_loaded: bool
    model_info: Dict[str, Any]
    timestamp: str

async def load_translation_model():
    """
    Load the Facebook M2M100 translation model at startup.
    This model supports 100 languages and can translate between any pair.
    """
    global translation_pipeline, model_info
    
    try:
        logger.info("Loading M2M100 translation model...")
        start_time = time.time()
        
        # Model configuration
        model_name = "facebook/m2m100_418M"
        
        # Check if CUDA is available
        device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if torch.cuda.is_available() else "CPU"
        
        logger.info(f"Using device: {device_name}")
        
        # Load model and tokenizer
        logger.info("Loading tokenizer and model...")
        tokenizer = M2M100Tokenizer.from_pretrained(model_name)
        model = M2M100ForConditionalGeneration.from_pretrained(model_name)
        
        # Create translation pipeline
        translation_pipeline = pipeline(
            "translation",
            model=model,
            tokenizer=tokenizer,
            device=device,
            max_length=512,
            do_sample=False,
            num_beams=5,
        )
        
        load_time = time.time() - start_time
        
        # Store model information
        model_info = {
            "model_name": model_name,
            "device": device_name,
            "load_time": round(load_time, 2),
            "max_length": 512,
            "supported_languages": [
                "en", "fr", "de", "es", "it", "pt", "ru", "zh", "ja", "ko", 
                "ar", "hi", "tr", "pl", "nl", "sv", "da", "no", "fi", "cs",
                "hu", "ro", "bg", "hr", "sk", "sl", "et", "lv", "lt", "mt",
                "ga", "cy", "eu", "ca", "gl", "ast", "oc", "br", "co", "wa",
                "lb", "is", "fo", "gd", "gv", "kw", "sco", "yi", "he", "ur",
                "fa", "ps", "sd", "gu", "pa", "ne", "si", "my", "km", "lo",
                "th", "vi", "id", "ms", "tl", "jv", "su", "mg", "ny", "sn",
                "yo", "ig", "ha", "sw", "zu", "xh", "af", "sq", "am", "hy",
                "az", "be", "bn", "bs", "eu", "ka", "kk", "ky", "mk", "mn",
                "uz", "ta", "te", "ml", "kn", "or", "as", "mr"
            ],
            "loaded_at": datetime.now().isoformat()
        }
        
        logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
        logger.info(f"Model supports {len(model_info['supported_languages'])} languages")
        
    except Exception as e:
        logger.error(f"Failed to load translation model: {str(e)}")
        model_info = {"error": str(e), "loaded_at": datetime.now().isoformat()}
        raise

def detect_language(text: str) -> str:
    """
    Detect language of input text.
    For simplicity, we'll use basic heuristics and common French/English patterns.
    In production, you might want to use langdetect or similar libraries.
    """
    text_lower = text.lower()
    
    # French indicators
    french_words = ["le", "la", "les", "de", "du", "des", "et", "à", "dans", "pour", "avec", "sur", "est", "sont", "une", "un"]
    french_count = sum(1 for word in french_words if word in text_lower)
    
    # English indicators
    english_words = ["the", "and", "to", "of", "in", "for", "with", "on", "is", "are", "a", "an", "this", "that"]
    english_count = sum(1 for word in english_words if word in text_lower)
    
    # Simple detection logic
    if french_count > english_count:
        return "fr"
    elif english_count > french_count:
        return "en"
    else:
        return "auto"  # Fallback to auto-detection

async def translate_text(text: str, source_lang: str = "auto") -> Dict[str, Any]:
    """
    Translate text to English using the M2M100 model.
    
    Args:
        text: Input text to translate
        source_lang: Source language code or 'auto' for detection
        
    Returns:
        Dictionary with translation results
    """
    if not translation_pipeline:
        raise HTTPException(status_code=503, detail="Translation model not loaded")
    
    start_time = time.time()
    
    try:
        # Detect language if auto
        detected_lang = None
        if source_lang == "auto":
            detected_lang = detect_language(text)
            if detected_lang == "en":
                # Text is already in English
                return {
                    "translated_text": text,
                    "detected_language": "en",
                    "confidence_score": 1.0,
                    "processing_time": time.time() - start_time
                }
            source_lang = detected_lang if detected_lang != "auto" else "fr"  # Default to French
        
        # Prepare source language for M2M100 format
        if source_lang == "fr":
            src_lang = "fr"
            translation_pipeline.tokenizer.src_lang = "fr"
        else:
            src_lang = source_lang
            translation_pipeline.tokenizer.src_lang = source_lang
        
        # Set target language to English
        translation_pipeline.tokenizer.tgt_lang = "en"
        
        # Perform translation
        logger.info(f"Translating from {src_lang} to en: {text[:50]}...")
        
        result = translation_pipeline(text, max_length=512, num_beams=5)
        translated_text = result[0]["translation_text"]
        
        processing_time = time.time() - start_time
        
        return {
            "translated_text": translated_text,
            "detected_language": detected_lang or source_lang,
            "confidence_score": 0.85,  # M2M100 doesn't provide confidence scores
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting Project Sentinel Translation Service...")
    await load_translation_model()
    yield
    # Shutdown
    logger.info("Shutting down Translation Service...")

# Create FastAPI application
app = FastAPI(
    title="Project Sentinel Translation Service",
    description="AI-powered translation service for OSINT analysis - Cameroon Defense Force",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest) -> TranslationResponse:
    """
    Translate text to English using Facebook's M2M100 model.
    
    Accepts text in various languages and translates to English for OSINT analysis.
    Supports automatic language detection for French/English text.
    """
    try:
        logger.info(f"Translation request: {request.text[:100]}... (lang: {request.source_lang})")
        
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Perform translation
        result = await translate_text(request.text, request.source_lang)
        
        return TranslationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in translate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status and model availability.
    """
    model_loaded = translation_pipeline is not None
    status = "healthy" if model_loaded else "unhealthy"
    
    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        model_info=model_info,
        timestamp=datetime.now().isoformat()
    )

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Project Sentinel Translation Service",
        "version": "1.0.0",
        "status": "operational",
        "authority": "Cameroon Defense Force",
        "classification": "RESTRICTED",
        "endpoints": {
            "translate": "POST /translate - Translate text to English",
            "health": "GET /health - Service health check",
            "docs": "GET /docs - API documentation"
        }
    }

@app.get("/languages")
async def supported_languages():
    """Get list of supported languages."""
    if not translation_pipeline:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "supported_languages": model_info.get("supported_languages", []),
        "total_count": len(model_info.get("supported_languages", [])),
        "primary_languages": ["fr", "en", "ar", "es", "pt", "de"],
        "note": "M2M100 model supports translation between any of these language pairs"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Run the service
    uvicorn.run(
        "translation_service:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Set to True for development
        log_level="info"
    )
