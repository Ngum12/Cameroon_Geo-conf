"""
PROJECT SENTINEL - ML PREDICTION API
FastAPI service for conflict prediction models integration.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import logging
import json
from datetime import datetime

# Import our prediction model
from simplified_conflict_predictor import CameroonConflictPredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Project Sentinel - ML Prediction API",
    description="Advanced AI conflict prediction for Cameroon Defense Force",
    version="1.0.0"
)

# Global predictor instance
predictor = None

# Pydantic models for API
class PredictionRequest(BaseModel):
    region: Optional[str] = None
    days_ahead: int = 7
    include_regional_assessment: bool = False

class RegionalAssessmentRequest(BaseModel):
    include_historical_context: bool = True

class PredictionResponse(BaseModel):
    region: str
    prediction_horizon: str
    conflict_predicted: bool
    conflict_probability: float
    confidence_level: str
    risk_level: str
    key_risk_factors: List[Dict[str, Any]]
    model_used: str
    prediction_timestamp: str

class RegionalRiskResponse(BaseModel):
    regional_risks: Dict[str, Dict[str, Any]]
    system_status: Dict[str, Any]
    generation_timestamp: str

class SystemStatusResponse(BaseModel):
    status: str
    models_loaded: int
    data_events: int
    last_training: str
    prediction_horizons: List[int]

@app.on_event("startup")
async def startup_event():
    """Initialize the ML prediction system on startup."""
    global predictor
    
    logger.info("🚀 Initializing Project Sentinel ML Prediction API...")
    
    try:
        # Load the predictor
        predictor = CameroonConflictPredictor()
        
        # Load and process data
        if predictor.load_acled_data():
            features_df = predictor.engineer_features()
            
            if features_df is not None:
                # Train models
                results = predictor.train_prediction_models()
                
                if results:
                    logger.info("✅ ML Prediction API initialized successfully!")
                    logger.info(f"📊 {len(predictor.models)} models trained")
                    logger.info(f"📈 {len(predictor.processed_features)} events processed")
                else:
                    logger.error("❌ Model training failed")
                    raise Exception("Model training failed")
            else:
                logger.error("❌ Feature engineering failed")
                raise Exception("Feature engineering failed")
        else:
            logger.error("❌ Data loading failed")
            raise Exception("Data loading failed")
            
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        predictor = None

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "service": "Project Sentinel ML Prediction API",
        "status": "operational" if predictor else "failed",
        "version": "1.0.0",
        "cameroon_defense_force": "Geopolitical Conflict Prevention System"
    }

@app.get("/health", response_model=SystemStatusResponse)
async def health_check():
    """System health check endpoint."""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML Prediction system not initialized")
    
    return SystemStatusResponse(
        status="operational",
        models_loaded=len(predictor.models),
        data_events=len(predictor.processed_features) if predictor.processed_features is not None else 0,
        last_training=datetime.now().isoformat(),
        prediction_horizons=predictor.prediction_horizons
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_conflict(request: PredictionRequest):
    """Make conflict predictions for a specific region and time horizon."""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML Prediction system not initialized")
    
    logger.info(f"🎯 Prediction request: {request.region}, {request.days_ahead} days")
    
    try:
        # Make prediction
        prediction = predictor.predict_future_conflicts(
            region=request.region,
            days_ahead=request.days_ahead
        )
        
        if not prediction:
            raise HTTPException(status_code=500, detail="Prediction generation failed")
        
        # Convert to response format
        response = PredictionResponse(
            region=prediction.get('region', 'Unknown'),
            prediction_horizon=prediction.get('prediction_horizon', f'{request.days_ahead} days'),
            conflict_predicted=prediction.get('conflict_predicted', False),
            conflict_probability=prediction.get('conflict_probability', 0.0),
            confidence_level=prediction.get('confidence_level', 'Low'),
            risk_level=prediction.get('risk_level', 'Low'),
            key_risk_factors=prediction.get('key_risk_factors', []),
            model_used=prediction.get('model_used', 'Unknown'),
            prediction_timestamp=prediction.get('prediction_timestamp', datetime.now().isoformat())
        )
        
        logger.info(f"✅ Prediction complete: {response.conflict_probability:.1%} probability")
        return response
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/regional-assessment", response_model=RegionalRiskResponse)
async def get_regional_assessment(request: RegionalAssessmentRequest):
    """Get comprehensive risk assessment for all Cameroon regions."""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML Prediction system not initialized")
    
    logger.info("🗺️ Regional assessment request")
    
    try:
        # Get regional risk assessment
        regional_risks = predictor.get_regional_risk_assessment()
        
        # System status
        system_status = {
            "models_active": len(predictor.models),
            "total_events_analyzed": len(predictor.processed_features) if predictor.processed_features is not None else 0,
            "prediction_horizons": predictor.prediction_horizons,
            "regions_monitored": len(predictor.cameroon_regions)
        }
        
        response = RegionalRiskResponse(
            regional_risks=regional_risks,
            system_status=system_status,
            generation_timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Regional assessment complete: {len(regional_risks)} regions")
        return response
        
    except Exception as e:
        logger.error(f"❌ Regional assessment error: {e}")
        raise HTTPException(status_code=500, detail=f"Regional assessment failed: {str(e)}")

@app.get("/intelligence-report")
async def get_intelligence_report():
    """Generate comprehensive intelligence report."""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML Prediction system not initialized")
    
    logger.info("📊 Intelligence report request")
    
    try:
        # Generate report
        report = predictor.generate_intelligence_report()
        
        return {
            "report": report,
            "format": "text",
            "generation_timestamp": datetime.now().isoformat(),
            "system": "Project Sentinel ML Prediction API"
        }
        
    except Exception as e:
        logger.error(f"❌ Intelligence report error: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/regions")
async def get_supported_regions():
    """Get list of supported Cameroon regions."""
    if not predictor:
        return {"regions": []}
    
    # Get actual regions from data
    if predictor.processed_features is not None:
        actual_regions = predictor.processed_features['admin1'].unique().tolist()
    else:
        actual_regions = predictor.cameroon_regions
    
    return {
        "regions": actual_regions,
        "total_regions": len(actual_regions),
        "default_regions": predictor.cameroon_regions
    }

@app.get("/models")
async def get_model_info():
    """Get information about trained models."""
    if not predictor:
        raise HTTPException(status_code=503, detail="ML Prediction system not initialized")
    
    model_info = {}
    
    for model_key, model in predictor.models.items():
        model_type = type(model).__name__
        
        # Get feature importance if available
        feature_importance = None
        if model_key in predictor.feature_importance:
            # Get top 5 most important features
            importance_dict = predictor.feature_importance[model_key]
            top_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:5]
            feature_importance = dict(top_features)
        
        model_info[model_key] = {
            "model_type": model_type,
            "feature_importance": feature_importance,
            "prediction_horizon": model_key.split('_')[-1] if '_' in model_key else "unknown"
        }
    
    return {
        "models": model_info,
        "total_models": len(predictor.models),
        "prediction_horizons": predictor.prediction_horizons
    }

if __name__ == "__main__":
    # For development
    uvicorn.run(
        "prediction_api:app",
        host="127.0.0.1",
        port=8003,
        log_level="info",
        reload=False
    )

