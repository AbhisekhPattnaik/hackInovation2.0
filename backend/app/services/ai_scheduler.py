"""
AI Scheduling Engine
Optimizes appointment slots, predicts wait times, detects overload, suggests reassignments
"""

from sqlalchemy.orm import Session
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.appointment import Appointment
from ..models.queue import QueueEntry
from datetime import datetime, timedelta
from typing import List, Dict

class AIScheduler:
    def __init__(self, db: Session):
        self.db = db
    
    def predict_wait_time(self, doctor_id: int) -> int:
        """
        Predict waiting time for a doctor based on:
        - Current queue length
        - Average consultation time
        - Appointments in pipeline
        """
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return 0
        
        # Get current waiting appointments
        waiting_appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "scheduled"
        ).count()
        
        # Get queue entries
        queue_entries = self.db.query(QueueEntry).filter(
            QueueEntry.doctor_id == doctor_id,
            QueueEntry.status == "scheduled"
        ).count()
        
        total_queue = waiting_appointments + queue_entries
        avg_time = doctor.avg_consult_time
        
        predicted_wait = total_queue * avg_time
        return min(predicted_wait, 120)  # Cap at 2 hours
    
    def detect_overload(self, doctor_id: int) -> Dict:
        """
        Detect if doctor is overloaded and return recommendations
        """
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return {"overloaded": False}
        
        # Count appointments for today
        today = datetime.utcnow().date()
        today_appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.slot_time >= datetime.combine(today, datetime.min.time()),
            Appointment.slot_time < datetime.combine(today, datetime.max.time()),
            Appointment.status.in_(["scheduled", "in_progress"])
        ).count()
        
        # Rough calculation: 8-hour day = 480 minutes
        minutes_available = 480
        minutes_needed = today_appointments * doctor.avg_consult_time
        
        utilization = minutes_needed / minutes_available if minutes_available > 0 else 0
        is_overloaded = utilization > 0.85
        
        return {
            "overloaded": is_overloaded,
            "utilization": min(utilization, 1.0),
            "appointments_today": today_appointments,
            "predicted_end_time": minutes_needed,
        }
    
    def suggest_reassignment(self, appointment_id: int, other_doctors: List[int] = None) -> Dict:
        """
        Analyze if appointment should be reassigned and suggest alternatives
        """
        appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            return {"suggested": False}
        
        current_doctor = self.db.query(Doctor).filter(
            Doctor.id == appointment.doctor_id
        ).first()
        
        # Check if current doctor is overloaded
        overload_status = self.detect_overload(appointment.doctor_id)
        
        if not overload_status["overloaded"]:
            return {"suggested": False, "reason": "Doctor not overloaded"}
        
        # Find alternative doctors with same specialty
        alternative_doctors = self.db.query(Doctor).filter(
            Doctor.specialization == current_doctor.specialization,
            Doctor.id != appointment.doctor_id,
            Doctor.verification_status == "VERIFIED"
        ).all()
        
        if not alternative_doctors:
            return {"suggested": False, "reason": "No alternative doctors available"}
        
        # Rank alternatives by utilization and wait time
        alternatives = []
        for alt_doctor in alternative_doctors:
            wait_time = self.predict_wait_time(alt_doctor.id)
            alternatives.append({
                "doctor_id": alt_doctor.id,
                "name": alt_doctor.name,
                "specialization": alt_doctor.specialization,
                "predicted_wait": wait_time,
                "utilization": alt_doctor.utilization,
                "rating": alt_doctor.rating
            })
        
        alternatives.sort(key=lambda x: (x["predicted_wait"], x["utilization"]))
        
        return {
            "suggested": True,
            "current_doctor_id": appointment.doctor_id,
            "current_wait_time": self.predict_wait_time(appointment.doctor_id),
            "reason": "Current doctor overloaded",
            "alternatives": alternatives[:3]  # Top 3 alternatives
        }
    
    def suggest_priority_upgrade(self, patient_id: int) -> Dict:
        """
        Suggest priority upgrades for high-severity patients
        """
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return {"upgrade_suggested": False}
        
        # If severity score is high, suggest priority upgrade
        if patient.severity_score > 0.7:
            return {
                "upgrade_suggested": True,
                "current_priority": patient.ai_priority,
                "recommended_priority": "HIGH" if patient.severity_score > 0.8 else "NORMAL",
                "reason": f"High severity score: {patient.severity_score}"
            }
        
        return {"upgrade_suggested": False}
    
    def get_slot_recommendations(self, doctor_id: int, date: datetime = None) -> List[Dict]:
        """
        Recommend optimal appointment slots for a doctor
        """
        if date is None:
            date = datetime.utcnow().date()
        
        doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return []
        
        # Get existing appointments for the day
        existing_appointments = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.slot_time >= datetime.combine(date, datetime.min.time()),
            Appointment.slot_time < datetime.combine(date, datetime.max.time())
        ).all()
        
        # Generate potential slots (every 30 minutes from 9 AM to 6 PM)
        slots = []
        current_time = datetime.combine(date, datetime.strptime("09:00", "%H:%M").time())
        end_time = datetime.combine(date, datetime.strptime("18:00", "%H:%M").time())
        
        slot_duration = timedelta(minutes=30)
        
        while current_time < end_time:
            # Check if slot is free
            conflicting = [a for a in existing_appointments 
                          if a.slot_time <= current_time < a.slot_time + timedelta(minutes=doctor.avg_consult_time)]
            
            if not conflicting:
                slots.append({
                    "time": current_time.isoformat(),
                    "available": True,
                    "predicted_wait": len([a for a in existing_appointments if a.slot_time < current_time]) * doctor.avg_consult_time
                })
            
            current_time += slot_duration
        
        return slots[:8]  # Return next 8 available slots
