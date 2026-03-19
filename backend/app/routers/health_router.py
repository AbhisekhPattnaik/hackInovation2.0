from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.user import User
from ..models.patient import Patient
from ..services.severity_service import calculate_severity
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/health", tags=["Health"])

def get_current_patient(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract patient from bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if role != "patient":
            raise HTTPException(status_code=403, detail="Only patients can access health data")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        return patient
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/health-status")
def get_health_status(patient: Patient = Depends(get_current_patient)):
    """
    Get patient's health status with AI insights
    Returns severity score, priority level, and health percentage
    """
    
    # Calculate health score based on severity
    health_percentage = max(0, 100 - patient.severity_score)
    
    # Determine priority level
    if patient.severity_score >= 80:
        priority_level = "CRITICAL"
        priority_color = "red"
    elif patient.severity_score >= 60:
        priority_level = "HIGH"
        priority_color = "orange"
    elif patient.severity_score >= 30:
        priority_level = "MODERATE"
        priority_color = "yellow"
    else:
        priority_level = "LOW"
        priority_color = "green"
    
    return {
        "health_score": health_percentage,
        "health_status": patient.ai_priority or "NORMAL",
        "severity_score": patient.severity_score,
        "priority_level": priority_level,
        "priority_color": priority_color,
        "symptoms": patient.symptoms or "None reported",
        "age": patient.age,
        "predicted_consult_time": patient.predicted_duration or 15,
        "last_updated": patient.updated_at.isoformat() if patient.updated_at else None
    }


@router.get("/recommendations")
def get_health_recommendations(patient: Patient = Depends(get_current_patient)):
    """
    Get AI-generated health recommendations based on patient's condition
    Uses severity score and symptoms to generate personalized recommendations
    """
    
    recommendations = []
    
    # Parse symptoms from string
    symptoms_list = [s.strip() for s in (patient.symptoms or "").split(",") if s.strip()]
    
    # Generate recommendations based on severity and symptoms
    if patient.severity_score >= 80:
        recommendations.append({
            "id": 1,
            "time": "URGENT",
            "priority": "CRITICAL",
            "title": "Immediate Medical Attention Required",
            "description": "Your health metrics indicate a need for urgent medical evaluation. Please consult a doctor immediately.",
            "action": "Schedule Emergency",
            "icon": "🚨"
        })
    
    if "chest pain" in [s.lower() for s in symptoms_list] or "breathing difficulty" in [s.lower() for s in symptoms_list]:
        recommendations.append({
            "id": 2,
            "time": "NOW",
            "priority": "CRITICAL",
            "title": "Respiratory/Cardiac Assessment",
            "description": "Consider cardiac evaluation and respiratory function tests.",
            "action": "Consult",
            "icon": "❤️"
        })
    
    if patient.severity_score >= 60:
        recommendations.append({
            "id": 3,
            "time": "TODAY",
            "priority": "HIGH",
            "title": "Rest and Hydration",
            "description": "Ensure adequate rest and drink at least 2-3 liters of water daily.",
            "action": "Track",
            "icon": "💧"
        })
    
    if patient.severity_score >= 30:
        recommendations.append({
            "id": 4,
            "time": "THIS WEEK",
            "priority": "MEDIUM",
            "title": "Light Physical Activity",
            "description": "Engage in 20-30 minutes of light exercise when you feel better.",
            "action": "Schedule",
            "icon": "🏃"
        })
    
    # Always add preventive recommendations
    recommendations.append({
        "id": 5,
        "time": "DAILY",
        "priority": "MEDIUM",
        "title": "Maintain Healthy Diet",
        "description": "Include fruits, vegetables, and whole grains in your daily meals.",
        "action": "Track",
        "icon": "🥗"
    })
    
    recommendations.append({
        "id": 6,
        "time": "WEEKLY",
        "priority": "LOW",
        "title": "Regular Health Checkups",
        "description": "Schedule a follow-up appointment with your healthcare provider.",
        "action": "Schedule",
        "icon": "📋"
    })
    
    return recommendations


@router.post("/update-symptoms")
def update_symptoms(data: dict, patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)):
    """
    Update patient's symptoms and recalculate severity score
    Expected data: {"symptoms": "symptom1, symptom2, symptom3"}
    """
    
    if "symptoms" not in data:
        raise HTTPException(status_code=400, detail="symptoms field is required")
    
    symptoms = data["symptoms"]
    
    # Update symptoms
    patient.symptoms = symptoms
    
    # Recalculate severity score based on symptoms
    symptoms_list = [s.strip() for s in symptoms.split(",") if s.strip()]
    severity = calculate_severity(symptoms_list)
    patient.severity_score = severity
    
    # Update AI priority based on severity
    if severity >= 80:
        patient.ai_priority = "CRITICAL"
    elif severity >= 60:
        patient.ai_priority = "HIGH"
    elif severity >= 30:
        patient.ai_priority = "MODERATE"
    else:
        patient.ai_priority = "NORMAL"
    
    db.commit()
    db.refresh(patient)
    
    return {
        "message": "Symptoms updated successfully",
        "severity_score": severity,
        "ai_priority": patient.ai_priority,
        "recommendations_count": 6
    }
