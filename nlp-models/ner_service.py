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
from typing import List, Dict, Any, Optional, Set, Tuple
import time
from datetime import datetime
import re
import networkx as nx
import json

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
    text: str = Field(..., description="The recognized entity text")
    label: str = Field(..., description="Entity category (PERSON, LOCATION, ORGANIZATION, MISCELLANEOUS)")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    start: int = Field(..., description="Start position in original text")
    end: int = Field(..., description="End position in original text")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Paul Biya",
                "label": "PERSON",
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
                        "text": "Paul Biya",
                        "label": "PERSON",
                        "confidence": 0.9998,
                        "start": 10,
                        "end": 19
                    },
                    {
                        "text": "Cameroon",
                        "label": "LOCATION",
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

class ActorRelationship(BaseModel):
    """Model for actor relationships in network analysis."""
    source: str = Field(..., description="Source actor name")
    target: str = Field(..., description="Target actor name")
    relationship_type: str = Field(..., description="Type of relationship (allied, opposes, commands, etc.)")
    strength: float = Field(..., description="Relationship strength (0.0 to 1.0)")
    context: str = Field(..., description="Context where relationship was identified")
    confidence: float = Field(..., description="Confidence in relationship detection")

class ActorProfile(BaseModel):
    """Model for individual actor profile."""
    name: str = Field(..., description="Actor name")
    actor_type: str = Field(..., description="Type (political_leader, military_commander, organization, etc.)")
    importance_score: float = Field(..., description="Actor importance score (0.0 to 1.0)")
    connections: int = Field(..., description="Number of connections in network")
    centrality: float = Field(..., description="Network centrality measure")
    key_attributes: List[str] = Field(default_factory=list, description="Key attributes/roles")

class NetworkAnalysisRequest(BaseModel):
    """Request model for network analysis endpoint."""
    texts: List[str] = Field(..., description="List of texts to analyze for actor relationships", min_items=1, max_items=50)
    
class NetworkAnalysisResponse(BaseModel):
    """Response model for network analysis endpoint."""
    actors: List[ActorProfile] = Field(..., description="Identified actors and their profiles")
    relationships: List[ActorRelationship] = Field(..., description="Identified relationships between actors")
    network_metrics: Dict[str, Any] = Field(..., description="Network-wide metrics and statistics")
    processing_time: float = Field(..., description="Processing time in seconds")

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
        if (current_entity['label'] == next_entity['label'] and
            current_entity['end'] >= next_entity['start'] - 2):  # Allow small gap
            
            # Merge entities
            current_entity['text'] = f"{current_entity['text']} {next_entity['text']}"
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
                    "text": clean_word,  # Use 'text' for consistency
                    "label": entity_group,  # Use 'label' for consistency  
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
        entity_type = entity['label']
        if entity_type not in grouped:
            grouped[entity_type] = []
        grouped[entity_type].append(entity)
    return grouped

# ACTOR NETWORK ANALYSIS FUNCTIONS

def initialize_cameroon_actor_knowledge() -> Dict[str, Dict[str, Any]]:
    """Initialize comprehensive Cameroon actor knowledge base."""
    return {
        # POLITICAL LEADERS
        "Paul Biya": {
            "type": "political_leader",
            "role": "President",
            "importance": 1.0,
            "attributes": ["head_of_state", "CPDM_leader", "executive_power"],
            "known_relationships": ["Prime Minister", "Minister of Defense", "CPDM party"]
        },
        "Joseph Dion Ngute": {
            "type": "political_leader", 
            "role": "Prime Minister",
            "importance": 0.9,
            "attributes": ["head_of_government", "cabinet_leader"],
            "known_relationships": ["Paul Biya", "cabinet ministers"]
        },
        "Maurice Kamto": {
            "type": "political_leader",
            "role": "Opposition Leader",
            "importance": 0.8,
            "attributes": ["MRC_leader", "opposition", "lawyer"],
            "known_relationships": ["MRC party", "opposition groups"]
        },
        
        # MILITARY LEADERS
        "Joseph Beti Assomo": {
            "type": "military_commander",
            "role": "Minister of Defense", 
            "importance": 0.9,
            "attributes": ["defense_minister", "military_leadership"],
            "known_relationships": ["Paul Biya", "military commanders", "BIR"]
        },
        "Jacob Kodji": {
            "type": "military_commander",
            "role": "BIR Commander",
            "importance": 0.8,
            "attributes": ["special_forces", "counter_terrorism", "rapid_intervention"],
            "known_relationships": ["Ministry of Defense", "regional commanders"]
        },
        
        # ORGANIZATIONS - GOVERNMENT
        "BIR": {
            "type": "military_organization",
            "role": "Rapid Intervention Battalion",
            "importance": 0.9,
            "attributes": ["elite_forces", "counter_terrorism", "special_operations"],
            "known_relationships": ["Ministry of Defense", "regional commands"]
        },
        "CPDM": {
            "type": "political_organization", 
            "role": "Ruling Party",
            "importance": 0.9,
            "attributes": ["ruling_party", "government", "political_power"],
            "known_relationships": ["Paul Biya", "government ministers"]
        },
        
        # ORGANIZATIONS - OPPOSITION
        "MRC": {
            "type": "political_organization",
            "role": "Opposition Party", 
            "importance": 0.7,
            "attributes": ["opposition", "political_party"],
            "known_relationships": ["Maurice Kamto", "opposition coalition"]
        },
        
        # THREAT ACTORS
        "Boko Haram": {
            "type": "terrorist_organization",
            "role": "Terrorist Group",
            "importance": 0.9,
            "attributes": ["terrorism", "insurgency", "far_north_threat"],
            "known_relationships": ["ISWAP", "regional terrorist networks"]
        },
        "ISWAP": {
            "type": "terrorist_organization", 
            "role": "Terrorist Group",
            "importance": 0.8,
            "attributes": ["terrorism", "regional_threat", "cross_border"],
            "known_relationships": ["Boko Haram", "Nigeria operations"]
        },
        
        # SEPARATIST ACTORS
        "Ambazonia Defense Forces": {
            "type": "separatist_organization",
            "role": "Armed Group",
            "importance": 0.7, 
            "attributes": ["separatist", "anglophone_crisis", "armed_resistance"],
            "known_relationships": ["restoration forces", "separatist networks"]
        }
    }

def detect_actor_relationships(entities: List[Dict], text: str) -> List[Dict[str, Any]]:
    """Detect relationships between actors based on textual context."""
    relationships = []
    actor_knowledge = initialize_cameroon_actor_knowledge()
    
    # Extract person and organization entities
    persons = [e for e in entities if e['label'] == 'PERSON']
    orgs = [e for e in entities if e['label'] == 'ORGANIZATION']
    all_actors = persons + orgs
    
    # Relationship patterns
    command_patterns = [r"commander", r"leader", r"head", r"minister", r"president", r"chief"]
    alliance_patterns = [r"allied", r"partnership", r"cooperation", r"agreement", r"treaty"]
    conflict_patterns = [r"against", r"opposes", r"conflict", r"fighting", r"war", r"battle"]
    subordinate_patterns = [r"under", r"reports to", r"commanded by", r"led by"]
    
    text_lower = text.lower()
    
    # Analyze relationships between detected actors
    for i, actor1 in enumerate(all_actors):
        for actor2 in all_actors[i+1:]:
            name1, name2 = actor1['text'], actor2['text']
            
            # Skip if actors are too far apart in text
            pos_diff = abs(actor1['start'] - actor2['start'])
            if pos_diff > 200:  # Limit to nearby entities
                continue
            
            relationship_type = "unknown"
            strength = 0.3  # Default low strength
            confidence = 0.5
            
            # Detect command relationships
            if any(re.search(pattern, text_lower) for pattern in command_patterns):
                if actor1['label'] == 'PERSON' and actor2['label'] == 'ORGANIZATION':
                    relationship_type = "commands"
                    strength = 0.8
                    confidence = 0.7
                elif actor2['label'] == 'PERSON' and actor1['label'] == 'ORGANIZATION':
                    relationship_type = "commanded_by" 
                    strength = 0.8
                    confidence = 0.7
            
            # Detect alliance relationships
            elif any(re.search(pattern, text_lower) for pattern in alliance_patterns):
                relationship_type = "allied"
                strength = 0.7
                confidence = 0.6
            
            # Detect conflict relationships
            elif any(re.search(pattern, text_lower) for pattern in conflict_patterns):
                relationship_type = "opposes"
                strength = 0.9
                confidence = 0.8
            
            # Use knowledge base to enhance relationships
            if name1 in actor_knowledge and name2 in actor_knowledge[name1]["known_relationships"]:
                strength = min(1.0, strength + 0.3)
                confidence = min(1.0, confidence + 0.2)
            
            if relationship_type != "unknown":
                relationships.append({
                    "source": name1,
                    "target": name2,
                    "relationship_type": relationship_type,
                    "strength": round(strength, 2),
                    "context": text[:200] + "..." if len(text) > 200 else text,
                    "confidence": round(confidence, 2)
                })
    
    return relationships

def build_actor_network(actors: List[Dict], relationships: List[Dict]) -> nx.Graph:
    """Build NetworkX graph from actors and relationships."""
    G = nx.Graph()
    
    # Add actor nodes with attributes
    for actor in actors:
        G.add_node(actor['name'], 
                   actor_type=actor['actor_type'],
                   importance=actor['importance_score'],
                   attributes=actor['key_attributes'])
    
    # Add relationship edges
    for rel in relationships:
        G.add_edge(rel['source'], rel['target'],
                   relationship=rel['relationship_type'],
                   strength=rel['strength'],
                   confidence=rel['confidence'])
    
    return G

def calculate_network_metrics(G: nx.Graph) -> Dict[str, Any]:
    """Calculate comprehensive network metrics."""
    if G.number_of_nodes() == 0:
        return {"total_nodes": 0, "total_edges": 0, "network_density": 0.0}
    
    # Basic metrics
    metrics = {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "network_density": nx.density(G),
        "average_clustering": nx.average_clustering(G) if G.number_of_nodes() > 0 else 0.0
    }
    
    # Centrality measures
    if G.number_of_nodes() > 1:
        centrality = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G)
        
        # Most central actors
        top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
        top_brokers = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
        
        metrics.update({
            "most_central_actors": [{"actor": actor, "centrality": round(score, 3)} 
                                   for actor, score in top_central],
            "key_brokers": [{"actor": actor, "betweenness": round(score, 3)} 
                           for actor, score in top_brokers]
        })
    
    # Connected components
    components = list(nx.connected_components(G))
    metrics["connected_components"] = len(components)
    metrics["largest_component_size"] = len(max(components, key=len)) if components else 0
    
    return metrics

async def analyze_actor_networks(texts: List[str]) -> Dict[str, Any]:
    """Analyze actor networks from multiple texts."""
    if not ner_pipeline:
        raise HTTPException(status_code=503, detail="NER model not loaded")
    
    start_time = time.time()
    
    all_entities = []
    all_relationships = []
    actor_knowledge = initialize_cameroon_actor_knowledge()
    
    # Process each text
    for text in texts:
        # Extract entities
        result = await analyze_entities(text)
        entities = result["entities"]
        all_entities.extend(entities)
        
        # Detect relationships
        relationships = detect_actor_relationships(entities, text)
        all_relationships.extend(relationships)
    
    # Build actor profiles
    actor_profiles = {}
    for entity in all_entities:
        if entity['label'] in ['PERSON', 'ORGANIZATION']:
            name = entity['text']
            if name not in actor_profiles:
                # Get actor info from knowledge base or create default
                if name in actor_knowledge:
                    kb_info = actor_knowledge[name]
                    actor_profiles[name] = {
                        "name": name,
                        "actor_type": kb_info["type"],
                        "importance_score": kb_info["importance"],
                        "connections": 0,
                        "centrality": 0.0,
                        "key_attributes": kb_info["attributes"]
                    }
                else:
                    # Default profile for unknown actors
                    actor_type = "organization" if entity['label'] == 'ORGANIZATION' else "person"
                    actor_profiles[name] = {
                        "name": name,
                        "actor_type": actor_type,
                        "importance_score": 0.5,  # Default importance
                        "connections": 0,
                        "centrality": 0.0,
                        "key_attributes": []
                    }
    
    # Build network graph
    actor_list = list(actor_profiles.values())
    G = build_actor_network(actor_list, all_relationships)
    
    # Update actor profiles with network metrics
    if G.number_of_nodes() > 1:
        centrality = nx.degree_centrality(G)
        for name in actor_profiles:
            if name in centrality:
                actor_profiles[name]["centrality"] = round(centrality[name], 3)
                actor_profiles[name]["connections"] = G.degree(name)
    
    # Calculate network-wide metrics
    network_metrics = calculate_network_metrics(G)
    
    processing_time = time.time() - start_time
    
    return {
        "actors": list(actor_profiles.values()),
        "relationships": all_relationships,
        "network_metrics": network_metrics,
        "processing_time": processing_time
    }

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
    title="Project Sentinel NER & Network Analysis Service",
    description="Named Entity Recognition and Actor Network Analysis for defense intelligence - Cameroon Defense Force",
    version="2.0.0",
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
        "service": "Project Sentinel NER & Network Analysis Service",
        "version": "2.0.0",
        "status": "operational",
        "authority": "Cameroon Defense Force",
        "classification": "RESTRICTED",
        "capabilities": [
            "Named Entity Recognition (NER)",
            "Actor Network Analysis", 
            "Relationship Mapping",
            "Political Alliance Detection",
            "Military Chain Analysis",
            "Terrorist Network Mapping"
        ],
        "endpoints": {
            "analyze-entities": "POST /analyze-entities - Extract named entities from English text",
            "analyze-actor-networks": "POST /analyze-actor-networks - Build actor relationship networks",
            "actor-knowledge": "GET /actor-knowledge - Cameroon actor knowledge base",
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

@app.post("/analyze-actor-networks", response_model=NetworkAnalysisResponse)
async def analyze_actor_networks_endpoint(request: NetworkAnalysisRequest) -> NetworkAnalysisResponse:
    """
    Analyze actor relationships and build network graphs from multiple texts.
    
    Identifies political leaders, military commanders, organizations, and terrorist groups,
    then maps their relationships (commands, alliances, conflicts) for intelligence analysis.
    """
    try:
        logger.info(f"Network analysis request: {len(request.texts)} texts")
        
        # Validate input
        if not request.texts or not any(text.strip() for text in request.texts):
            raise HTTPException(status_code=400, detail="At least one non-empty text required")
        
        # Filter out empty texts
        valid_texts = [text.strip() for text in request.texts if text.strip()]
        
        # Perform network analysis
        result = await analyze_actor_networks(valid_texts)
        
        return NetworkAnalysisResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in network analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/actor-knowledge")
async def get_actor_knowledge():
    """
    Get the Cameroon actor knowledge base for reference.
    """
    try:
        knowledge = initialize_cameroon_actor_knowledge()
        
        # Structure response for easy consumption
        actors_by_type = {}
        for name, info in knowledge.items():
            actor_type = info["type"]
            if actor_type not in actors_by_type:
                actors_by_type[actor_type] = []
            
            actors_by_type[actor_type].append({
                "name": name,
                "role": info["role"],
                "importance": info["importance"],
                "attributes": info["attributes"],
                "known_relationships": info["known_relationships"]
            })
        
        return {
            "total_actors": len(knowledge),
            "actor_types": list(actors_by_type.keys()),
            "actors_by_type": actors_by_type,
            "categories": {
                "political_leaders": len([a for a in knowledge.values() if a["type"] == "political_leader"]),
                "military_commanders": len([a for a in knowledge.values() if a["type"] == "military_commander"]),
                "organizations": len([a for a in knowledge.values() if "organization" in a["type"]]),
                "threat_actors": len([a for a in knowledge.values() if "terrorist" in a["type"] or "separatist" in a["type"]])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting actor knowledge: {str(e)}")
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

