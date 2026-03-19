from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.queue import QueueEntry, QueueMetrics, QueueOptimization
from ..models.appointment import Appointment
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..services.prediction_service import PredictionService, estimate_bottlenecks
from ..services.optimization_service import OptimizationService
from ..services.explainability_service import ExplainabilityService
from datetime import datetime, timedelta

router = APIRouter(prefix="/queue", tags=["Queue Management"])

@router.post("/entry/{appointment_id}")
def create_queue_entry(appointment_id: int, db: Session = Depends(get_db)):
    """Create queue entry when appointment is confirmed"""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    
    # Predict consultation duration
    predicted_duration = PredictionService.predict_consultation_duration(
        appointment.patient_id,
        appointment.doctor_id,
        patient.severity_score if patient else 0.5,
        db
    )
    
    # Predict no-show probability
    no_show_prob = PredictionService.predict_no_show_probability(appointment.patient_id, db)
    
    # Calculate priority
    priority = PredictionService.calculate_priority_score(appointment.patient_id, patient.severity_score if patient else 0.5, db)
    
    try:
        queue_entry = QueueEntry(
            appointment_id=appointment_id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            status="scheduled",
            scheduled_time=appointment.slot_time,
            predicted_consultation_duration=predicted_duration,
            predicted_no_show_probability=no_show_prob,
            priority_score=priority
        )
        
        db.add(queue_entry)
        db.commit()
        db.refresh(queue_entry)
        
        print(f"✅ Queue entry created: Patient {appointment.patient_id}, Doctor {appointment.doctor_id}")
        
        return {
            "id": queue_entry.id,
            "appointment_id": appointment_id,
            "patient_id": appointment.patient_id,
            "predicted_duration": predicted_duration,
            "no_show_risk": f"{no_show_prob:.0%}",
            "priority": priority,
            "ps_id": patient.ps_id if patient else "Unknown"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating queue entry: {str(e)}")

@router.get("/patient/{patient_id}")
def get_patient_queue_status(patient_id: int, db: Session = Depends(get_db)):
    """Get patient's current queue status and wait time prediction"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get active queue entry for patient
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.patient_id == patient_id,
        QueueEntry.status.in_(["scheduled", "waiting"])
    ).first()
    
    if not queue_entry:
        return {
            "status": "no_appointment",
            "message": "No active appointments"
        }
    
    # Recalculate wait time
    wait_time = PredictionService.predict_wait_time(
        queue_entry.doctor_id,
        queue_entry.queue_position or 1,
        db
    )
    
    doctor = db.query(Doctor).filter(Doctor.id == queue_entry.doctor_id).first()
    
    return {
        "ps_id": patient.ps_id,
        "status": queue_entry.status,
        "queue_position": queue_entry.queue_position,
        "scheduled_time": queue_entry.scheduled_time,
        "predicted_wait_time": f"{wait_time} minutes",
        "predicted_consultation_duration": f"{queue_entry.predicted_consultation_duration} minutes",
        "total_estimated_time": f"{wait_time + queue_entry.predicted_consultation_duration} minutes",
        "doctor": doctor.user.name if doctor else "Unknown",
        "no_show_risk": f"{queue_entry.predicted_no_show_probability:.0%}",
        "priority_level": "HIGH" if queue_entry.priority_score > 0.7 else "NORMAL"
    }

@router.get("/doctor/{doctor_id}/queue")
def get_doctor_queue(doctor_id: int, db: Session = Depends(get_db)):
    """Get real-time queue for specific doctor"""
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    queue_entries = db.query(QueueEntry).filter(
        QueueEntry.doctor_id == doctor_id,
        QueueEntry.status.in_(["scheduled", "waiting"])
    ).order_by(QueueEntry.priority_score.desc(), QueueEntry.scheduled_time).all()
    
    patients_list = []
    total_wait = 0
    
    for idx, entry in enumerate(queue_entries):
        patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
        patients_list.append({
            "queue_position": idx + 1,
            "patient_name": patient.user.name if patient and patient.user else "Unknown",
            "patient_ps_id": patient.ps_id if patient else "Unknown",
            "severity": patient.severity_score if patient else 0,
            "predicted_duration": entry.predicted_consultation_duration,
            "priority": entry.priority_score,
            "no_show_risk": f"{entry.predicted_no_show_probability:.0%}"
        })
        total_wait += entry.predicted_consultation_duration
    
    # Check for bottlenecks
    bottlenecks = estimate_bottlenecks(doctor_id, db)
    
    return {
        "doctor_name": doctor.user.name,
        "specialization": doctor.specialization,
        "queue_size": len(queue_entries),
        "total_estimated_time": f"{total_wait} minutes",
        "patients": patients_list,
        "bottlenecks": bottlenecks
    }

@router.get("/hospital/dashboard")
def get_hospital_queue_dashboard(db: Session = Depends(get_db)):
    """Get real-time hospital-wide queue dashboard"""
    
    # Get all active queue entries
    all_entries = db.query(QueueEntry).filter(
        QueueEntry.status.in_(["scheduled", "waiting"])
    ).all()
    
    # Group by doctor
    doctor_queues = {}
    total_wait = 0
    
    for entry in all_entries:
        if entry.doctor_id not in doctor_queues:
            doctor_queues[entry.doctor_id] = []
        doctor_queues[entry.doctor_id].append(entry)
        total_wait += entry.predicted_consultation_duration
    
    # Generate summary
    summary_data = []
    for doc_id, entries in doctor_queues.items():
        doctor = db.query(Doctor).filter(Doctor.id == doc_id).first()
        bottlenecks = estimate_bottlenecks(doc_id, db)
        
        summary_data.append({
            "doctor_id": doc_id,
            "doctor_name": doctor.user.name if doctor else "Unknown",
            "specialty": doctor.specialization if doctor else "Unknown",
            "queue_size": len(entries),
            "avg_wait_time": sum(e.predicted_consultation_duration for e in entries) // len(entries),
            "bottleneck_count": len(bottlenecks),
            "health": "🟢" if len(entries) < 5 else "🟡" if len(entries) < 8 else "🔴"
        })
    
    # Get system health
    system_summary = ExplainabilityService.generate_queue_dashboard_summary(all_entries, doctor_queues)
    
    return {
        "timestamp": datetime.utcnow(),
        "total_patients_waiting": len(all_entries),
        "total_estimated_wait": f"{total_wait} minutes",
        "doctor_summaries": summary_data,
        "system_health": system_summary.get("system_health"),
        "recommended_actions": system_summary.get("recommended_actions"),
        "bottlenecks_detected": system_summary.get("bottlenecks_detected")
    }

@router.post("/optimize/{queue_entry_id}")
def trigger_optimization(queue_entry_id: int, db: Session = Depends(get_db)):
    """Analyze queue entry and recommend optimization"""
    
    entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    # Get optimization recommendation
    recommendation = OptimizationService.recommend_optimization(queue_entry_id, db)
    
    # Generate human-readable explanation
    explanation = ExplainabilityService.generate_explanation(recommendation)
    
    # Get patient name
    patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
    patient_name = patient.user.name if patient and patient.user else "Patient"
    
    return {
        "queue_entry_id": queue_entry_id,
        "recommendation": recommendation.get("decision_type"),
        "confidence": f"{recommendation.get('confidence', 0):.0%}",
        "reasoning": recommendation.get("reasoning"),
        "explanation": explanation,
        "patient_notification": ExplainabilityService.format_for_patient_sms(recommendation),
        "doctor_notification": ExplainabilityService.format_for_doctor_dashboard(recommendation, patient_name),
        "can_be_applied": recommendation.get("decision_type") != "none"
    }

@router.post("/optimize/{queue_entry_id}/apply")
def apply_queue_optimization(queue_entry_id: int, db: Session = Depends(get_db)):
    """Apply the recommended optimization"""
    
    entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    # Get recommendation
    recommendation = OptimizationService.recommend_optimization(queue_entry_id, db)
    
    # Apply it
    success = OptimizationService.apply_optimization(queue_entry_id, recommendation, db)
    
    if success:
        return {
            "status": "applied",
            "recommendation": recommendation.get("decision_type"),
            "message": "Optimization applied successfully",
            "notification": ExplainabilityService.format_for_patient_sms(recommendation)
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to apply optimization")

@router.put("/entry/{queue_entry_id}/status")
def update_queue_status(queue_entry_id: int, status: str, db: Session = Depends(get_db)):
    """Update queue entry status (waiting, in_consultation, completed, no_show, etc)"""
    
    entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    valid_statuses = ["scheduled", "waiting", "in_consultation", "completed", "no_show", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")
    
    # Record timing
    if status == "waiting":
        entry.arrival_time = datetime.utcnow()
    elif status == "in_consultation":
        entry.consultation_start = datetime.utcnow()
    elif status in ["completed", "no_show"]:
        entry.consultation_end = datetime.utcnow()
        
        # Calculate actual timings
        if entry.arrival_time and entry.consultation_start:
            entry.actual_wait_time = int((entry.consultation_start - entry.arrival_time).total_seconds() / 60)
        if entry.consultation_start and entry.consultation_end:
            entry.actual_consultation_duration = int((entry.consultation_end - entry.consultation_start).total_seconds() / 60)
        
        # Update patient history if no-show
        if status == "no_show":
            patient = db.query(Patient).filter(Patient.id == entry.patient_id).first()
            if patient:
                patient.no_show_count += 1
    
    entry.status = status
    db.commit()
    
    return {
        "queue_entry_id": queue_entry_id,
        "status": status,
        "message": f"Status updated to {status}",
        "arrival_time": entry.arrival_time,
        "consultation_start": entry.consultation_start,
        "actual_wait_time": entry.actual_wait_time
    }

@router.get("/metrics/doctor/{doctor_id}")
def get_doctor_metrics(doctor_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get performance metrics for doctor (for ML training and optimization)"""
    
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get metrics from last N days
    since = datetime.utcnow() - timedelta(days=days)
    
    metrics = db.query(QueueMetrics).filter(
        QueueMetrics.doctor_id == doctor_id,
        QueueMetrics.metric_date >= since
    ).all()
    
    if not metrics:
        return {
            "doctor_name": doctor.user.name,
            "metrics_period": f"Last {days} days",
            "data_available": False,
            "message": "Insufficient data for metrics"
        }
    
    avg_wait = sum(m.avg_wait_time for m in metrics) / len(metrics)
    avg_duration = sum(m.avg_consultation_duration for m in metrics) / len(metrics)
    avg_no_show = sum(m.no_show_rate for m in metrics) / len(metrics)
    
    return {
        "doctor_name": doctor.user.name,
        "specialization": doctor.specialization,
        "metrics_period": f"Last {days} days",
        "avg_wait_time": f"{avg_wait:.0f} min",
        "avg_consultation_duration": f"{avg_duration:.0f} min",
        "no_show_rate": f"{avg_no_show:.1%}",
        "total_patients": sum(m.total_patients for m in metrics),
        "data_points": len(metrics)
    }
