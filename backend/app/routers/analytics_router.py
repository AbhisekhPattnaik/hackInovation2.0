"""
Analytics Router - Provides comprehensive analytics endpoints
for doctor dashboard, admin panel, and system monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.doctor import Doctor
from ..models.user import User
from ..services.analytics_service import AnalyticsService
from ..services.timeseries_prediction import TimeSeriesPredictionService
from ..services.reinforcement_learning_optimizer import ReinforcementLearningOptimizer
from ..services.graph_queue_model import GraphQueueModel
from ..services.explainability_service import ExplainabilityService
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_doctor_from_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract doctor from bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if not email or role != "doctor":
            raise HTTPException(status_code=403, detail="Not a doctor account")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    return doctor

@router.get("/doctor/performance")
def get_doctor_performance(
    days: int = 30,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get comprehensive performance metrics for authenticated doctor"""
    return AnalyticsService.get_doctor_performance_metrics(doctor.id, days=days, db=db)

@router.get("/doctor/queue")
def get_doctor_queue_analytics(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get current queue analytics"""
    return AnalyticsService.get_queue_analytics(doctor.id, db=db)

@router.get("/doctor/insights")
def get_doctor_efficiency_insights(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get AI-powered efficiency insights for doctor"""
    return AnalyticsService.get_efficiency_insights(doctor.id, db=db)

@router.get("/doctor/utilization-forecast")
def get_utilization_forecast(
    days: int = 7,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get 1-week doctor utilization forecast"""
    return TimeSeriesPredictionService.predict_doctor_utilization(
        doctor.id, days_ahead=days, db=db
    )

@router.get("/doctor/delay-prediction")
def get_delay_prediction(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get prediction of doctor running behind schedule"""
    return TimeSeriesPredictionService.predict_delays(doctor.id, db=db)

@router.get("/doctor/queue-optimization")
def get_queue_optimization(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get RL-based queue optimization recommendations"""
    return ReinforcementLearningOptimizer.optimize_queue_batch(doctor.id, db=db)

@router.get("/doctor/slot-reassignments")
def get_slot_reassignments(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get real-time slot reassignment recommendations"""
    try:
        # Get all pending appointments for the doctor
        from ..models.appointment import Appointment
        from ..models.queue import QueueEntry
        
        pending_appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status.in_(["scheduled", "queued"])
        ).all()
        
        reassignments = []
        for appt in pending_appointments:
            queue_entry = db.query(QueueEntry).filter(
                QueueEntry.appointment_id == appt.id
            ).first()
            
            if queue_entry:
                # Get RL-based recommendation for this specific appointment
                recommendation = ReinforcementLearningOptimizer.recommend_slot_reassignment(queue_entry.id, db)
                
                if recommendation and recommendation.get("recommendation") != "no_change":
                    reassignments.append({
                        "appointment_id": appt.id,
                        "patient_id": appt.patient_id,
                        "current_slot": appt.slot_time.isoformat() if appt.slot_time else None,
                        "recommendation": recommendation.get("recommendation", "no_change"),
                        "confidence": recommendation.get("confidence", 0),
                        "reason": recommendation.get("reason", ""),
                        "suggested_time": recommendation.get("suggested_time", ""),
                        "priority_change": recommendation.get("priority_change", 0)
                    })
        
        return {
            "doctor_id": doctor.id,
            "total_pending": len(pending_appointments),
            "reassignments_available": len(reassignments),
            "reassignments": reassignments,
            "message": f"Found {len(reassignments)} slot optimization opportunities"
        }
    except Exception as e:
        print(f"❌ Error fetching slot reassignments: {str(e)}")
        return {
            "doctor_id": doctor.id,
            "total_pending": 0,
            "reassignments_available": 0,
            "reassignments": [],
            "message": "Unable to fetch reassignments at this time",
            "error": str(e)
        }

@router.get("/doctor/queue-graph-model")
def get_doctor_queue_graph_model(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get graph-based queue modeling for doctor's queue"""
    try:
        from ..models.appointment import Appointment
        from ..models.queue import QueueEntry
        from ..models.patient import Patient
        
        # Get all queue entries for this doctor
        queue_entries = db.query(QueueEntry).join(
            Appointment, QueueEntry.appointment_id == Appointment.id
        ).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status.in_(["scheduled", "queued"])
        ).order_by(QueueEntry.priority.desc(), QueueEntry.arrival_time.asc()).all()
        
        # Build graph model
        nodes = []
        edges = []
        
        for idx, entry in enumerate(queue_entries):
            appt = entry.appointment
            patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()
            
            node = {
                "id": f"patient_{appt.patient_id}",
                "label": f"Patient {appt.patient_id}",
                "priority": entry.priority,
                "wait_time": (entry.arrival_time.timestamp() if entry.arrival_time else 0),
                "severity": entry.priority,
                "status": appt.status
            }
            nodes.append(node)
            
            # Add edges between sequential patients
            if idx > 0:
                edges.append({
                    "source": f"patient_{queue_entries[idx-1].appointment.patient_id}",
                    "target": f"patient_{appt.patient_id}",
                    "type": "sequence",
                    "wait_time_after_prev": entry.priority
                })
        
        # Analyze queue efficiency
        total_patients = len(queue_entries)
        avg_wait_time = sum(e.priority for e in queue_entries) / max(total_patients, 1) if queue_entries else 0
        
        # Identify critical paths
        critical_patients = [
            {
                "patient_id": e.appointment.patient_id,
                "priority": e.priority,
                "estimated_time_in_queue": e.priority * 5  # Rough estimation
            }
            for e in sorted(queue_entries, key=lambda x: x.priority, reverse=True)[:3]
        ]
        
        return {
            "doctor_id": doctor.id,
            "queue_size": total_patients,
            "graph": {
                "nodes": nodes,
                "edges": edges
            },
            "metrics": {
                "average_priority": avg_wait_time,
                "queue_depth": total_patients,
                "estimated_total_wait": avg_wait_time * total_patients if total_patients > 0 else 0
            },
            "critical_path": {
                "high_priority_patients": critical_patients,
                "estimated_discharge_time": sum(e.priority for e in queue_entries[:min(3, total_patients)]) * 5 if queue_entries else 0
            },
            "bottlenecks": [
                {
                    "position": idx,
                    "patient_id": e.appointment.patient_id,
                    "reason": "High priority" if e.priority > avg_wait_time else "Complex case"
                }
                for idx, e in enumerate(queue_entries[:3])
            ]
        }
    except Exception as e:
        print(f"❌ Error fetching queue graph model: {str(e)}")
        return {
            "doctor_id": doctor.id,
            "queue_size": 0,
            "graph": {"nodes": [], "edges": []},
            "metrics": {},
            "critical_path": {},
            "bottlenecks": [],
            "error": str(e)
        }

@router.get("/system/queue-graph")
def get_queue_graph(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get graph representation of entire queue system (admin only)"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return GraphQueueModel.build_queue_graph(db=db)

@router.get("/system/bottlenecks")
def get_system_bottlenecks(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get system bottleneck analysis"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        
        if role not in ["admin", "doctor"]:
            raise HTTPException(status_code=403, detail="Access required")
        
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return GraphQueueModel.identify_bottlenecks(db=db)

@router.get("/system/patient-flow")
def get_patient_flow_analysis(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Analyze patient flow across system"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        
        if role not in ["admin", "doctor"]:
            raise HTTPException(status_code=403, detail="Access required")
        
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return GraphQueueModel.analyze_patient_flow(db=db)

@router.get("/system/resource-recommendations")
def get_resource_recommendations(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get AI recommendations for resource allocation"""
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        
        if role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return GraphQueueModel.recommend_resource_allocation(db=db)
