#!/usr/bin/env python3
"""
CPU-Optimized Translation Service for Project Sentinel
Cameroon Defense Force OSINT Analysis System

FastAPI service using Helsinki-NLP opus-mt-fr-en model for French→English translation.
Designed for CPU efficiency and defense operations reliability.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import MarianMTModel, MarianTokenizer
from contextlib import asynccontextmanager
import logging
import time
import asyncio
import torch
from typing import Dict, Any
from langdetect import detect, DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global model variables
tokenizer = None
model = None
model_loaded = False

class TranslationRequest(BaseModel):
    """Request model for French→English translation."""
    text: str = Field(..., min_length=1, max_length=5000, description="French text to translate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Le président Paul Biya a rencontré les forces de défense à Douala."
            }
        }

class TranslationResponse(BaseModel):
    """Response model for translation."""
    original_text: str = Field(..., description="Original French text")
    translated_text: str = Field(..., description="English translation")
    detected_language: str = Field(..., description="Detected language")
    confidence_score: float = Field(..., description="Translation confidence")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_text": "Le président Paul Biya a rencontré les forces de défense à Douala.",
                "translated_text": "President Paul Biya met with the defense forces in Douala.",
                "detected_language": "fr",
                "confidence_score": 0.92,
                "processing_time": 0.15
            }
        }

def detect_language(text: str) -> str:
    """
    Enhanced language detection for Cameroon context.
    Returns 'fr' for French, 'en' for English, defaults to 'fr'.
    """
    try:
        # Quick check for obvious French/English patterns
        french_indicators = [
            'le ', 'la ', 'les ', 'de ', 'du ', 'des ', 'et ', 'est ', 'avec ', 'pour ',
            'dans ', 'sur ', 'par ', 'président', 'ministre', 'gouvernement',
            'cameroun', 'yaoundé', 'douala', 'forces', 'défense', 'sécurité'
        ]
        
        english_indicators = [
            'the ', 'and ', 'is ', 'are ', 'with ', 'for ', 'in ', 'on ', 'at ',
            'president', 'minister', 'government', 'cameroon', 'defense', 'security'
        ]
        
        text_lower = text.lower()
        french_score = sum(1 for indicator in french_indicators if indicator in text_lower)
        english_score = sum(1 for indicator in english_indicators if indicator in text_lower)
        
        if english_score > french_score:
            return 'en'
        
        # Use langdetect as fallback
        detected = detect(text)
        return detected if detected in ['fr', 'en'] else 'fr'
        
    except Exception as e:
        logger.warning(f"Language detection failed: {e}, defaulting to French")
        return 'fr'

async def load_translation_model():
    """Load the Helsinki-NLP French→English translation model."""
    global tokenizer, model, model_loaded
    
    if model_loaded:
        return
    
    try:
        start_time = time.time()
        logger.info("🔄 Loading Helsinki-NLP opus-mt-fr-en model for CPU optimization...")
        
        model_name = "Helsinki-NLP/opus-mt-fr-en"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        
        # Set to evaluation mode for inference
        model.eval()
        
        load_time = time.time() - start_time
        model_loaded = True
        
        logger.info(f"✅ Translation model loaded successfully in {load_time:.2f} seconds")
        logger.info("🎯 Ready for French→English defense intelligence translation")
        
    except Exception as e:
        logger.error(f"❌ Failed to load translation model: {e}")
        raise HTTPException(status_code=503, detail=f"Translation model loading failed: {e}")

async def translate_french_to_english(text: str) -> Dict[str, Any]:
    """
    Translate French text to English using Helsinki-NLP model.
    Optimized for CPU performance and defense intelligence accuracy.
    """
    global tokenizer, model
    
    if not model_loaded:
        raise HTTPException(status_code=503, detail="Translation model not loaded")
    
    start_time = time.time()
    
    # Detect language first
    detected_lang = detect_language(text)
    
    # If already English, return as-is
    if detected_lang == 'en':
        return {
            "original_text": text,
            "translated_text": text,
            "detected_language": "en",
            "confidence_score": 1.0,
            "processing_time": time.time() - start_time
        }
    
    try:
        logger.info(f"🔄 Translating French text: {text[:50]}...")
        
        # Tokenize and translate
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():  # Optimize for inference
            translated = model.generate(
                **inputs,
                max_length=512,
                num_beams=3,  # Reduced for speed
                early_stopping=True,
                do_sample=False  # Deterministic for consistency
            )
        
        translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        processing_time = time.time() - start_time
        
        logger.info(f"✅ Translation complete in {processing_time:.2f}s: {translated_text[:50]}...")
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "detected_language": detected_lang,
            "confidence_score": 0.90,  # Helsinki-NLP models are reliable
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}")

# FastAPI lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Translation Service - CPU Optimized")
    await load_translation_model()
    yield
    # Shutdown
    logger.info("🛑 Translation Service shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Project Sentinel Translation Service",
    description="CPU-optimized French→English translation for Cameroon Defense Force",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Project Sentinel Translation Service",
        "version": "2.0.0",
        "model": "Helsinki-NLP/opus-mt-fr-en",
        "optimization": "CPU-optimized for defense operations",
        "capability": "French → English translation",
        "status": "operational" if model_loaded else "loading"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if model_loaded else "loading",
        "model_loaded": model_loaded,
        "timestamp": time.time(),
        "service": "translation"
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate_endpoint(request: TranslationRequest):
    """
    Translate French text to English.
    Optimized for Cameroon defense intelligence processing.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = await translate_french_to_english(request.text)
        return TranslationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Translation service error")

@app.get("/stats")
async def get_stats():
    """Get translation service statistics."""
    return {
        "model": "Helsinki-NLP/opus-mt-fr-en",
        "model_loaded": model_loaded,
        "supported_languages": "French → English",
        "optimization": "CPU-optimized",
        "max_length": 512,
        "designed_for": "Cameroon Defense Force Intelligence"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
