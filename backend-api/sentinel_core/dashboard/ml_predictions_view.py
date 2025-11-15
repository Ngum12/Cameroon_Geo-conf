"""
Django views for ML predictions integration.
"""

import json
import requests
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ML Prediction API settings
ML_API_BASE_URL = "http://127.0.0.1:8003"
ML_API_TIMEOUT = 30  # seconds

def check_ml_api_health() -> Dict[str, Any]:
    """Check if ML Prediction API is available."""
    try:
        response = requests.get(f"{ML_API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return {"status": "available", "data": response.json()}
        else:
            return {"status": "unavailable", "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "unavailable", "error": str(e)}

@csrf_exempt
@require_http_methods(["GET", "POST"])
def predict_conflict(request):
    """
    Make conflict predictions using ML models.
    
    POST body:
    {
        "region": "Extreme-Nord" (optional),
        "days_ahead": 7,
        "include_regional_assessment": false
    }
    """
    
    if request.method == "GET":
        # Health check
        health = check_ml_api_health()
        return JsonResponse({
            "service": "ML Predictions",
            "ml_api_status": health["status"],
            "available_endpoints": ["/predict", "/regional-assessment", "/intelligence-report"]
        })
    
    try:
        # Parse request body
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = {
                "region": request.POST.get('region'),
                "days_ahead": int(request.POST.get('days_ahead', 7)),
                "include_regional_assessment": request.POST.get('include_regional_assessment') == 'true'
            }
        
        logger.info(f"🎯 ML prediction request: {data}")
        
        # Check ML API availability
        health = check_ml_api_health()
        if health["status"] != "available":
            return JsonResponse({
                "success": False,
                "error": "ML Prediction API unavailable",
                "details": health.get("error", "Unknown error"),
                "fallback_prediction": {
                    "region": data.get("region", "All regions"),
                    "conflict_probability": 0.5,
                    "confidence": "Low - API unavailable",
                    "note": "This is a fallback response. ML API is not accessible."
                }
            }, status=503)
        
        # Make prediction request
        ml_response = requests.post(
            f"{ML_API_BASE_URL}/predict",
            json=data,
            timeout=ML_API_TIMEOUT
        )
        
        if ml_response.status_code == 200:
            prediction_data = ml_response.json()
            
            return JsonResponse({
                "success": True,
                "prediction": prediction_data,
                "ml_api_status": "available",
                "processing_time": "real-time"
            })
        else:
            logger.error(f"❌ ML API error: {ml_response.status_code} - {ml_response.text}")
            return JsonResponse({
                "success": False,
                "error": "ML prediction failed",
                "http_status": ml_response.status_code,
                "details": ml_response.text[:500]
            }, status=500)
            
    except json.JSONDecodeError as e:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON in request body",
            "details": str(e)
        }, status=400)
        
    except requests.exceptions.Timeout:
        return JsonResponse({
            "success": False,
            "error": "ML API timeout",
            "details": f"Request timeout after {ML_API_TIMEOUT} seconds"
        }, status=504)
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        return JsonResponse({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }, status=500)

@csrf_exempt 
@require_http_methods(["GET"])
def regional_assessment(request):
    """Get comprehensive regional risk assessment."""
    
    try:
        logger.info("🗺️ Regional assessment request")
        
        # Check ML API availability
        health = check_ml_api_health()
        if health["status"] != "available":
            return JsonResponse({
                "success": False,
                "error": "ML Prediction API unavailable",
                "details": health.get("error", "Unknown error")
            }, status=503)
        
        # Request data
        request_data = {
            "include_historical_context": request.GET.get('include_historical_context', 'true') == 'true'
        }
        
        # Make assessment request
        ml_response = requests.post(
            f"{ML_API_BASE_URL}/regional-assessment",
            json=request_data,
            timeout=ML_API_TIMEOUT
        )
        
        if ml_response.status_code == 200:
            assessment_data = ml_response.json()
            
            return JsonResponse({
                "success": True,
                "assessment": assessment_data,
                "ml_api_status": "available"
            })
        else:
            logger.error(f"❌ Regional assessment error: {ml_response.status_code}")
            return JsonResponse({
                "success": False,
                "error": "Regional assessment failed",
                "http_status": ml_response.status_code
            }, status=500)
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            "success": False,
            "error": "ML API timeout"
        }, status=504)
        
    except Exception as e:
        logger.error(f"❌ Regional assessment error: {e}")
        return JsonResponse({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def intelligence_report(request):
    """Generate comprehensive intelligence report."""
    
    try:
        logger.info("📊 Intelligence report request")
        
        # Check ML API availability
        health = check_ml_api_health()
        if health["status"] != "available":
            return JsonResponse({
                "success": False,
                "error": "ML Prediction API unavailable",
                "details": health.get("error", "Unknown error")
            }, status=503)
        
        # Make report request
        ml_response = requests.get(
            f"{ML_API_BASE_URL}/intelligence-report",
            timeout=ML_API_TIMEOUT
        )
        
        if ml_response.status_code == 200:
            report_data = ml_response.json()
            
            return JsonResponse({
                "success": True,
                "report": report_data,
                "ml_api_status": "available"
            })
        else:
            logger.error(f"❌ Intelligence report error: {ml_response.status_code}")
            return JsonResponse({
                "success": False,
                "error": "Intelligence report generation failed",
                "http_status": ml_response.status_code
            }, status=500)
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            "success": False,
            "error": "ML API timeout"
        }, status=504)
        
    except Exception as e:
        logger.error(f"❌ Intelligence report error: {e}")
        return JsonResponse({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def ml_system_status(request):
    """Get ML system status and capabilities."""
    
    try:
        # Check health
        health = check_ml_api_health()
        
        if health["status"] == "available":
            # Get detailed status
            try:
                models_response = requests.get(f"{ML_API_BASE_URL}/models", timeout=5)
                regions_response = requests.get(f"{ML_API_BASE_URL}/regions", timeout=5)
                
                models_data = models_response.json() if models_response.status_code == 200 else {}
                regions_data = regions_response.json() if regions_response.status_code == 200 else {}
                
                return JsonResponse({
                    "success": True,
                    "ml_api_status": "available",
                    "health_data": health["data"],
                    "models": models_data,
                    "regions": regions_data,
                    "capabilities": [
                        "Conflict prediction (7, 30, 90 days)",
                        "Regional risk assessment",
                        "Intelligence report generation",
                        "Multi-region monitoring",
                        "Real-time analysis"
                    ]
                })
                
            except Exception as e:
                return JsonResponse({
                    "success": True,
                    "ml_api_status": "available",
                    "health_data": health["data"],
                    "note": "Basic health check only",
                    "error": str(e)
                })
        else:
            return JsonResponse({
                "success": False,
                "ml_api_status": "unavailable",
                "error": health.get("error", "ML API not accessible"),
                "fallback_mode": "Manual analysis required"
            })
            
    except Exception as e:
        logger.error(f"❌ ML system status error: {e}")
        return JsonResponse({
            "success": False,
            "error": "Status check failed",
            "details": str(e)
        }, status=500)

