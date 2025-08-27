#!/usr/bin/env python3
"""
Named Entity Recognition Service for Project Sentinel
Cameroon Defense Force OSINT Analysis System

FastAPI service for extracting named entities (persons, locations, organizations)
from English text using XLM-RoBERTa model fine-tuned on CoNLL-03 dataset.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import torch
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for model and pipeline
ner_pipeline = None
model_info = {}

# Entity types mapping for better readability
ENTITY_MAPPING = {
    'PER': 'PERSON',
    'LOC': 'LOCATION', 
    'ORG': 'ORGANIZATION',
    'MISC': 'MISCELLANEOUS'
}

# Request/Response models
class NERRequest(BaseModel):
    """Request model for NER analysis endpoint."""
    text: str = Field(
        ..., 
        description="English text to analyze for named entities", 
        min_length=1, 
        max_length=5000
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "President Paul Biya of Cameroon visited Yaoundé today to meet with UN officials."
            }
        }

class EntityItem(BaseModel):
    """Model for individual entity item."""
    word: str = Field(..., description="The recognized entity text")
    entity_group: str = Field(..., description="Entity category (PERSON, LOCATION, ORGANIZATION, MISCELLANEOUS)")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    start: int = Field(..., description="Start position in original text")
    end: int = Field(..., description="End position in original text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "Paul Biya",
                "entity_group": "PERSON",
                "confidence": 0.9998,
                "start": 10,
                "end": 19
            }
        }

class NERResponse(BaseModel):
    """Response model for NER analysis endpoint."""
    entities: List[EntityItem] = Field(..., description="List of recognized named entities")
    entity_count: int = Field(..., description="Total number of entities found")
    processing_time: float = Field(..., description="Processing time in seconds")
    text_length: int = Field(..., description="Length of analyzed text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entities": [
                    {
                        "word": "Paul Biya",
                        "entity_group": "PERSON",
                        "confidence": 0.9998,
                        "start": 10,
                        "end": 19
                    },
                    {
                        "word": "Cameroon",
                        "entity_group": "LOCATION",
                        "confidence": 0.9995,
                        "start": 23,
                        "end": 31
                    }
                ],
                "entity_count": 2,
                "processing_time": 0.45,
                "text_length": 78
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    model_loaded: bool
    model_info: Dict[str, Any]
    timestamp: str

async def load_ner_model():
    """
    Load the XLM-RoBERTa NER model at startup.
    This model is fine-tuned on CoNLL-03 English dataset for NER tasks.
    """
    global ner_pipeline, model_info
    
    try:
        logger.info("Loading XLM-RoBERTa NER model...")
        start_time = time.time()
        
        # Model configuration
        model_name = "xlm-roberta-large-finetuned-conll03-english"
        
        # Check if CUDA is available
        device = 0 if torch.cuda.is_available() else -1
        device_name = "GPU" if torch.cuda.is_available() else "CPU"
        
        logger.info(f"Using device: {device_name}")
        
        # Load tokenizer and model
        logger.info("Loading tokenizer and model...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        
        # Create NER pipeline with aggregation strategy
        ner_pipeline = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            device=device,
            aggregation_strategy="max",  # Aggregate subword tokens
            stride=16,  # For handling long texts
        )
        
        load_time = time.time() - start_time
        
        # Store model information
        model_info = {
            "model_name": model_name,
            "device": device_name,
            "load_time": round(load_time, 2),
            "max_length": 512,
            "supported_entities": ["PERSON", "LOCATION", "ORGANIZATION", "MISCELLANEOUS"],
            "entity_codes": list(ENTITY_MAPPING.keys()),
            "aggregation_strategy": "max",
            "loaded_at": datetime.now().isoformat()
        }
        
        logger.info(f"NER model loaded successfully in {load_time:.2f} seconds")
        logger.info(f"Model supports entities: {model_info['supported_entities']}")
        
    except Exception as e:
        logger.error(f"Failed to load NER model: {str(e)}")
        model_info = {"error": str(e), "loaded_at": datetime.now().isoformat()}
        raise

def clean_entity_text(text: str) -> str:
    """Clean entity text by removing extra whitespace and special characters."""
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common artifacts
    cleaned = cleaned.replace('##', '')  # Remove BPE artifacts
    
    return cleaned.strip()

def merge_adjacent_entities(entities: List[Dict]) -> List[Dict]:
    """
    Merge adjacent entities of the same type that might have been split.
    This helps with entities that span multiple tokens.
    """
    if not entities:
        return entities
    
    merged = []
    current_entity = entities[0].copy()
    
    for i in range(1, len(entities)):
        next_entity = entities[i]
        
        # Check if entities are adjacent and of same type
        if (current_entity['entity_group'] == next_entity['entity_group'] and
            current_entity['end'] >= next_entity['start'] - 2):  # Allow small gap
            
            # Merge entities
            current_entity['word'] = f"{current_entity['word']} {next_entity['word']}"
            current_entity['end'] = next_entity['end']
            # Average confidence scores
            current_entity['confidence'] = (current_entity['confidence'] + next_entity['confidence']) / 2
        else:
            # Add current entity to results and start new one
            merged.append(current_entity)
            current_entity = next_entity.copy()
    
    # Add the last entity
    merged.append(current_entity)
    
    return merged

async def analyze_entities(text: str) -> Dict[str, Any]:
    """
    Analyze text for named entities using the XLM-RoBERTa model.
    
    Args:
        text: English text to analyze
        
    Returns:
        Dictionary with entity analysis results
    """
    if not ner_pipeline:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    start_time = time.time()
    
    try:
        logger.info(f"Analyzing entities in text: {text[:50]}...")
        
        # Perform NER analysis
        raw_entities = ner_pipeline(text)
        
        # Process and clean entities
        processed_entities = []
        
        for entity in raw_entities:
            # Map entity group to readable format
            entity_group = ENTITY_MAPPING.get(entity['entity_group'], entity['entity_group'])
            
            # Clean entity text
            clean_word = clean_entity_text(entity['word'])
            
            if clean_word:  # Only include non-empty entities
                processed_entity = {
                    "word": clean_word,
                    "entity_group": entity_group,
                    "confidence": round(entity['score'], 4),
                    "start": entity['start'],
                    "end": entity['end']
                }
                processed_entities.append(processed_entity)
        
        # Merge adjacent entities of same type
        final_entities = merge_adjacent_entities(processed_entities)
        
        # Sort by position in text
        final_entities.sort(key=lambda x: x['start'])
        
        processing_time = time.time() - start_time
        
        return {
            "entities": final_entities,
            "entity_count": len(final_entities),
            "processing_time": processing_time,
            "text_length": len(text)
        }
        
    except Exception as e:
        logger.error(f"NER analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"NER analysis failed: {str(e)}")

def filter_high_confidence_entities(entities: List[Dict], min_confidence: float = 0.5) -> List[Dict]:
    """Filter entities by confidence threshold."""
    return [entity for entity in entities if entity['confidence'] >= min_confidence]

def group_entities_by_type(entities: List[Dict]) -> Dict[str, List[Dict]]:
    """Group entities by their type for easier processing."""
    grouped = {}
    for entity in entities:
        entity_type = entity['entity_group']
        if entity_type not in grouped:
            grouped[entity_type] = []
        grouped[entity_type].append(entity)
    return grouped

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("Starting Project Sentinel NER Service...")
    await load_ner_model()
    yield
    # Shutdown
    logger.info("Shutting down NER Service...")

# Create FastAPI application
app = FastAPI(
    title="Project Sentinel NER Service",
    description="Named Entity Recognition service for OSINT analysis - Cameroon Defense Force",
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

@app.post("/analyze-entities", response_model=NERResponse)
async def analyze_entities_endpoint(request: NERRequest) -> NERResponse:
    """
    Analyze English text for named entities (persons, locations, organizations).
    
    Uses XLM-RoBERTa model fine-tuned on CoNLL-03 dataset to identify and classify
    named entities with confidence scores.
    """
    try:
        logger.info(f"NER analysis request: {request.text[:100]}...")
        
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Check text length
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        # Perform NER analysis
        result = await analyze_entities(request.text)
        
        return NERResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze-entities endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify service status and model availability.
    """
    model_loaded = ner_pipeline is not None
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
        "service": "Project Sentinel NER Service",
        "version": "1.0.0",
        "status": "operational",
        "authority": "Cameroon Defense Force",
        "classification": "RESTRICTED",
        "endpoints": {
            "analyze-entities": "POST /analyze-entities - Extract named entities from English text",
            "health": "GET /health - Service health check",
            "entity-types": "GET /entity-types - Supported entity types",
            "docs": "GET /docs - API documentation"
        }
    }

@app.get("/entity-types")
async def supported_entity_types():
    """Get information about supported entity types."""
    if not ner_pipeline:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "supported_entities": model_info.get("supported_entities", []),
        "entity_descriptions": {
            "PERSON": "Names of people, including first names, last names, nicknames",
            "LOCATION": "Names of locations, including countries, cities, regions, landmarks",
            "ORGANIZATION": "Names of companies, agencies, institutions, political groups",
            "MISCELLANEOUS": "Other named entities that don't fit the above categories"
        },
        "confidence_threshold": "Entities with confidence < 0.5 may be less reliable",
        "model_info": {
            "name": model_info.get("model_name", ""),
            "aggregation_strategy": model_info.get("aggregation_strategy", ""),
            "max_input_length": model_info.get("max_length", 512)
        }
    }

@app.post("/analyze-entities/grouped")
async def analyze_entities_grouped(request: NERRequest):
    """
    Analyze entities and return them grouped by type for easier processing.
    """
    try:
        # Get regular analysis
        result = await analyze_entities(request.text)
        
        # Group entities by type
        grouped_entities = group_entities_by_type(result["entities"])
        
        # Add summary statistics
        entity_stats = {
            entity_type: len(entities) 
            for entity_type, entities in grouped_entities.items()
        }
        
        return {
            "grouped_entities": grouped_entities,
            "entity_statistics": entity_stats,
            "total_entities": result["entity_count"],
            "processing_time": result["processing_time"],
            "text_length": result["text_length"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in grouped analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/analyze-entities/high-confidence")
async def analyze_entities_high_confidence(
    request: NERRequest, 
    min_confidence: float = 0.8
):
    """
    Analyze entities and return only those above a specified confidence threshold.
    """
    try:
        # Get regular analysis
        result = await analyze_entities(request.text)
        
        # Filter high-confidence entities
        high_conf_entities = filter_high_confidence_entities(
            result["entities"], 
            min_confidence
        )
        
        return {
            "entities": high_conf_entities,
            "entity_count": len(high_conf_entities),
            "total_entities_found": result["entity_count"],
            "confidence_threshold": min_confidence,
            "processing_time": result["processing_time"],
            "text_length": result["text_length"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in high-confidence analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    
    # Run the service
    uvicorn.run(
        "ner_service:app",
        host="0.0.0.0",
        port=8002,  # Different port from translation service
        reload=False,  # Set to True for development
        log_level="info"
    )
