"""
Queue optimization service - recommends dynamic scheduling decisions
Uses predictions to optimize:
1. Slot reassignments (move patient earlier/later)
2. Doctor reassignments (match to less busy doctor)
3. Priority adjustments (bump urgent patients)
4. Emergency handling (walk-ins, urgent cases)
"""

from sqlalchemy.orm import Session
from ..models.queue import QueueEntry, QueueOptimization
from ..models.appointment import Appointment
from ..models.patient import Patient
from ..models.doctor import Doctor
from datetime import datetime, timedelta
import json

class OptimizationService:
    
    @staticmethod
    def recommend_optimization(queue_entry_id: int, db: Session) -> dict:
        """
        Analyze queue entry and recommend optimization
        Returns: {decision_type, recommended_slot, reasoning, confidence}
        """
        
        entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
        if not entry:
            return {"decision_type": "none", "reasoning": "Queue entry not found"}
        
        recommendation = {
            "decision_type": "none",
            "recommended_slot": None,
            "reasoning": "No optimization needed",
            "confidence": 0.0,
            "factors": {}
        }
        
        # 1. Check for no-show risk
        if entry.predicted_no_show_probability > 0.4:
            recommendation = OptimizationService._handle_no_show_risk(entry, db)
        
        # 2. Check for long wait time
        elif entry.predicted_wait_time > 60:
            recommendation = OptimizationService._handle_long_wait(entry, db)
        
        # 3. Check for doctor overload
        elif OptimizationService._is_doctor_overloaded(entry.doctor_id, db):
            recommendation = OptimizationService._handle_doctor_overload(entry, db)
        
        # 4. Check for patient prioritization
        elif entry.priority_score > 0.7:
            recommendation = OptimizationService._handle_high_priority(entry, db)
        
        return recommendation
    
    @staticmethod
    def _handle_no_show_risk(entry: QueueEntry, db: Session) -> dict:
        """Recommend reminder or earlier slot to reduce no-show"""
        
        factors = {
            "no_show_probability": str(entry.predicted_no_show_probability),
            "patient_history": f"{entry.patient.no_show_count} no-shows",
            "reason": "High risk of not showing up"
        }
        
        # Recommend moving to earlier slot (increases chance they attend)
        recommended_slot = entry.scheduled_time - timedelta(hours=1)
        
        return {
            "decision_type": "move_earlier",
            "recommended_slot": recommended_slot,
            "reasoning": f"Patient has {entry.predicted_no_show_probability:.0%} no-show risk. Moving earlier increases attendance probability. Send reminder SMS.",
            "confidence": min(0.95, 0.5 + entry.predicted_no_show_probability),
            "factors": factors,
            "action": "send_reminder_sms"  # Suggest action
        }
    
    @staticmethod
    def _handle_long_wait(entry: QueueEntry, db: Session) -> dict:
        """Recommend doctor reassignment or slot shift to reduce wait"""
        
        factors = {
            "predicted_wait": f"{entry.predicted_wait_time} min",
            "queue_position": entry.queue_position,
            "threshold": "60 min",
            "reason": "Excessive wait time detected"
        }
        
        # Find less busy doctor with same specialization
        current_doctor = entry.doctor
        alternative_doctor = OptimizationService._find_less_busy_doctor(
            current_doctor.specialization,
            current_doctor.id,
            db
        )
        
        if alternative_doctor:
            return {
                "decision_type": "doctor_reassign",
                "recommended_slot": entry.scheduled_time,
                "reasoning": f"Reassigning from Dr. {current_doctor.user.name} (queue: {entry.queue_position}) to Dr. {alternative_doctor.user.name} (less busy). Expected wait reduction: {entry.predicted_wait_time - 20} min",
                "confidence": 0.85,
                "factors": factors,
                "alternative_doctor_id": alternative_doctor.id
            }
        
        # Otherwise recommend time shift
        shifted_slot = entry.scheduled_time + timedelta(hours=2)
        return {
            "decision_type": "slot_shift",
            "recommended_slot": shifted_slot,
            "reasoning": f"Moving appointment 2 hours later to reduce queue. Current wait: {entry.predicted_wait_time} min → Expected: 20 min",
            "confidence": 0.75,
            "factors": factors
        }
    
    @staticmethod
    def _handle_doctor_overload(entry: QueueEntry, db: Session) -> dict:
        """Recommend reallocating patients from overloaded doctor"""
        
        factors = {
            "doctor_id": entry.doctor_id,
            "queue_length": len(db.query(QueueEntry).filter(
                QueueEntry.doctor_id == entry.doctor_id,
                QueueEntry.status == "waiting"
            ).all()),
            "threshold": "5 patients",
            "reason": "Doctor has excessive queue"
        }
        
        alternative_doctor = OptimizationService._find_less_busy_doctor(
            entry.doctor.specialization,
            entry.doctor_id,
            db
        )
        
        if alternative_doctor:
            return {
                "decision_type": "doctor_reassign",
                "recommended_slot": entry.scheduled_time,
                "reasoning": f"Dr. {entry.doctor.user.name} is overloaded. Reassigning to Dr. {alternative_doctor.user.name} for better service.",
                "confidence": 0.80,
                "factors": factors,
                "alternative_doctor_id": alternative_doctor.id
            }
        
        return {"decision_type": "none", "reasoning": "No alternative doctor available"}
    
    @staticmethod
    def _handle_high_priority(entry: QueueEntry, db: Session) -> dict:
        """Recommend priority bump for high-severity cases"""
        
        factors = {
            "priority_score": entry.priority_score,
            "severity": "High",
            "reason": "Medical urgency detected"
        }
        
        return {
            "decision_type": "priority_bump",
            "recommended_slot": entry.scheduled_time - timedelta(minutes=30),
            "reasoning": f"High priority patient (severity: {entry.priority_score:.0%}). Recommend moving 30 min earlier to ensure timely treatment.",
            "confidence": 0.90,
            "factors": factors
        }
    
    @staticmethod
    def _is_doctor_overloaded(doctor_id: int, db: Session) -> bool:
        """Check if doctor has excessive queue"""
        
        queue_count = db.query(QueueEntry).filter(
            QueueEntry.doctor_id == doctor_id,
            QueueEntry.status.in_(["waiting", "scheduled"])
        ).count()
        
        return queue_count > 5  # More than 5 patients waiting
    
    @staticmethod
    def _find_less_busy_doctor(specialization: str, exclude_doctor_id: int, db: Session):
        """Find doctor with same specialization but less busy"""
        
        alternative = db.query(Doctor).filter(
            Doctor.specialization == specialization,
            Doctor.id != exclude_doctor_id
        ).first()
        
        if alternative:
            queue_count = db.query(QueueEntry).filter(
                QueueEntry.doctor_id == alternative.id,
                QueueEntry.status.in_(["waiting", "scheduled"])
            ).count()
            
            if queue_count < 3:  # Less than 3 waiting
                print(f"✅ Found alternative doctor: {alternative.user.name} (queue: {queue_count})")
                return alternative
        
        return None
    
    @staticmethod
    def apply_optimization(queue_entry_id: int, optimization_decision: dict, db: Session) -> bool:
        """Apply recommended optimization to queue entry and appointment"""
        
        entry = db.query(QueueEntry).filter(QueueEntry.id == queue_entry_id).first()
        if not entry:
            return False
        
        try:
            # Update queue entry with optimization
            entry.optimization_recommended = optimization_decision.get("decision_type")
            entry.optimization_reason = optimization_decision.get("reasoning")
            
            # If recommending doctor reassignment
            if optimization_decision.get("decision_type") == "doctor_reassign":
                new_doctor_id = optimization_decision.get("alternative_doctor_id")
                if new_doctor_id:
                    appointment = entry.appointment
                    appointment.doctor_id = new_doctor_id
                    entry.doctor_id = new_doctor_id
            
            # If recommending slot shift
            if optimization_decision.get("recommended_slot"):
                appointment = entry.appointment
                appointment.slot_time = optimization_decision.get("recommended_slot")
                entry.scheduled_time = optimization_decision.get("recommended_slot")
            
            entry.optimization_applied = True
            
            # Record the optimization decision
            opt_record = QueueOptimization(
                queue_entry_id=queue_entry_id,
                doctor_id=entry.doctor_id,
                patient_id=entry.patient_id,
                decision_type=optimization_decision.get("decision_type"),
                original_slot=entry.scheduled_time,
                recommended_slot=optimization_decision.get("recommended_slot"),
                reasoning=optimization_decision.get("reasoning"),
                factors=json.dumps(optimization_decision.get("factors", {})),
                confidence_score=optimization_decision.get("confidence", 0.0),
                was_applied=True
            )
            
            db.add(opt_record)
            db.commit()
            
            print(f"✅ Optimization applied: {optimization_decision.get('decision_type')}")
            return True
        
        except Exception as e:
            db.rollback()
            print(f"❌ Error applying optimization: {str(e)}")
            return False
