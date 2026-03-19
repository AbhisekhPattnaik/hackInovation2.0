"""
ML Models Router
Provides endpoints for disease classification and appointment no-show prediction
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
import os
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from ..database.sesion import get_db
from ..models.user import User
from ..models.patient import Patient
from ..ml.disease_classifier import DiseaseClassifier
from ..ml.appointment_noshow_predictor import AppointmentNoShowPredictor
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/ml", tags=["ML Models"])

# Load models on startup
disease_classifier = None
noshow_predictor = None

def load_models():
    """Load trained ML models from disk"""
    global disease_classifier, noshow_predictor
    
    disease_model_path = r"D:\PulseSync\backend\app\ml\models\disease_classifier.pkl"
    noshow_model_path = r"D:\PulseSync\backend\app\ml\models\noshow_predictor.pkl"
    
    try:
        if os.path.exists(disease_model_path):
            disease_classifier = DiseaseClassifier.load(disease_model_path)
        else:
            print("[WARNING] Disease classifier model not found. Train models first!")
    except Exception as e:
        print(f"[WARNING] Error loading disease classifier: {e}")
    
    try:
        if os.path.exists(noshow_model_path):
            noshow_predictor = AppointmentNoShowPredictor.load(noshow_model_path)
        else:
            print("[WARNING] No-show predictor model not found. Train models first!")
    except Exception as e:
        print(f"[WARNING] Error loading no-show predictor: {e}")

# Load models when router is imported
load_models()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract user from bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# ==================== DISEASE CLASSIFICATION ENDPOINTS ====================

class DiseasePredictionRequest(BaseModel):
    """Request body for disease prediction"""
    symptoms: List[str]
    top_k: Optional[int] = 5

class DiseasePredictionResponse(BaseModel):
    """Response for disease prediction"""
    primary_prediction: dict
    alternative_diagnoses: List[dict]
    input_symptoms: List[str]
    confidence_threshold: float

@router.post("/disease/predict")
def predict_disease(request: DiseasePredictionRequest) -> DiseasePredictionResponse:
    """
    Predict disease based on symptoms
    
    Returns top K disease predictions with confidence scores and descriptions
    """
    if not disease_classifier:
        raise HTTPException(
            status_code=503,
            detail="Disease classifier model not loaded. Train models first!"
        )
    
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="At least one symptom required")
    
    try:
        result = disease_classifier.predict(request.symptoms, top_k=request.top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/disease/symptoms")
def get_available_symptoms():
    """Get list of all available symptoms in the system"""
    if not disease_classifier:
        raise HTTPException(status_code=503, detail="Disease classifier not loaded")
    
    return {
        'symptoms': disease_classifier.symptom_list,
        'symptom_count': len(disease_classifier.symptom_list),
        'severity_weights': disease_classifier.symptom_severity
    }

@router.get("/disease/model-info")
def get_disease_model_info():
    """Get information about the disease classification model"""
    if not disease_classifier:
        raise HTTPException(status_code=503, detail="Disease classifier not loaded")
    
    return {
        'model_type': 'Gradient Boosting Classifier',
        'num_diseases': disease_classifier.model_performance['num_diseases'],
        'num_features': disease_classifier.model_performance['num_features'],
        'training_samples': disease_classifier.model_performance['training_samples'],
        'test_accuracy': disease_classifier.model_performance['test_accuracy'],
        'test_f1_score': disease_classifier.model_performance['test_f1'],
        'status': 'Production Ready'
    }

# ==================== APPOINTMENT NO-SHOW ENDPOINTS ====================

class AppointmentNoShowRequest(BaseModel):
    """Request body for no-show prediction"""
    age: int
    is_female: int
    age_group: int
    days_advance_booking: int
    has_hypertension: int
    has_diabetes: int
    has_alcoholism: int
    medical_complexity: int
    received_sms_reminder: int
    appointment_month: int
    appointment_weekday: int
    is_weekend_appt: int

class AppointmentNoShowResponse(BaseModel):
    """Response for no-show prediction"""
    no_show_probability: float
    risk_level: str
    recommendations: List[str]
    confidence: float

@router.post("/appointment/predict-noshow")
def predict_appointment_noshow(request: AppointmentNoShowRequest) -> AppointmentNoShowResponse:
    """
    Predict probability of appointment no-show
    
    Helps optimize queue management and resource allocation
    Returns risk level and personalized recommendations
    """
    if not noshow_predictor:
        raise HTTPException(
            status_code=503,
            detail="No-show predictor model not loaded. Train models first!"
        )
    
    try:
        appointment_data = request.dict()
        result = noshow_predictor.predict_no_show_probability(appointment_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/appointment/model-info")
def get_noshow_model_info():
    """Get information about the no-show prediction model"""
    if not noshow_predictor:
        raise HTTPException(status_code=503, detail="No-show predictor not loaded")
    
    return {
        'model_type': 'Gradient Boosting Classifier',
        'num_features': noshow_predictor.model_performance['num_features'],
        'training_samples': noshow_predictor.model_performance['training_samples'],
        'test_f1_score': noshow_predictor.model_performance['test_f1'],
        'test_auc_roc': noshow_predictor.model_performance['test_auc'],
        'no_show_rate_in_data': noshow_predictor.model_performance['no_show_rate'],
        'top_features': list(noshow_predictor.feature_importance.keys())[:10],
        'status': 'Production Ready'
    }

# ==================== BATCH PREDICTION ENDPOINTS ====================

class BatchDiseasePredictionRequest(BaseModel):
    """Request body for batch disease predictions"""
    predictions: List[DiseasePredictionRequest]

@router.post("/disease/predict-batch")
def predict_disease_batch(request: BatchDiseasePredictionRequest):
    """
    Predict diseases for multiple symptom sets in batch
    """
    if not disease_classifier:
        raise HTTPException(status_code=503, detail="Disease classifier not loaded")
    
    results = []
    for pred_request in request.predictions:
        try:
            result = disease_classifier.predict(pred_request.symptoms, top_k=pred_request.top_k)
            results.append({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            results.append({
                'status': 'error',
                'error': str(e)
            })
    
    return {'results': results, 'total': len(results), 'successful': sum(1 for r in results if r['status'] == 'success')}

# ==================== HEALTH CHECK ====================

@router.get("/health")
def ml_health_check():
    """Check if ML models are loaded and ready"""
    return {
        'disease_classifier_loaded': disease_classifier is not None,
        'noshow_predictor_loaded': noshow_predictor is not None,
        'models_ready': disease_classifier is not None and noshow_predictor is not None,
        'message': 'All models ready' if (disease_classifier and noshow_predictor) else 'Some models not loaded'
    }
