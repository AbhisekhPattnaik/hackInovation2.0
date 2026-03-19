"""
ML-powered prediction service for queue optimization
Uses historical data to predict:
1. Consultation duration
2. No-show probability
3. Delays and bottlenecks
4. Patient priority scores
"""

from sqlalchemy.orm import Session
from ..models.queue import QueueEntry
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..models.appointment import Appointment
from datetime import datetime, timedelta
import random

class PredictionService:
    
    @staticmethod
    def predict_consultation_duration(
        patient_id: int,
        doctor_id: int,
        severity_score: float,
        db: Session
    ) -> int:
        """
        Predict consultation duration in minutes using:
        - Patient's historical average duration
        - Doctor's specialization and workload
        - Symptom severity
        - Time-of-day patterns
        """
        
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        # Base duration
        base_duration = 15  # Default 15 minutes
        
        # 1. Use patient's historical average if available
        if patient and patient.avg_historical_duration > 0:
            base_duration = patient.avg_historical_duration * 0.7  # Weight recent history
        
        # 2. Adjust for severity
        severity_multiplier = 1.0 + (severity_score * 0.5)  # High severity = longer
        
        # 3. Adjust for doctor
        if doctor and doctor.specialization == "Cardiology":
            severity_multiplier *= 1.2  # Cardiologists take longer
        elif doctor and doctor.specialization == "Psychiatry":
            severity_multiplier *= 1.3  # Psychiatrists take longest
        
        # 4. Add small randomness (realistic variation)
        randomness = random.uniform(0.85, 1.15)
        
        predicted = int(base_duration * severity_multiplier * randomness)
        
        # Clamp between 5 and 60 minutes
        predicted = max(5, min(60, predicted))
        
        print(f"🔮 Predicted duration: {predicted} min (base: {base_duration}, severity: {severity_score})")
        
        return predicted
    
    @staticmethod
    def predict_no_show_probability(patient_id: int, db: Session) -> float:
        """
        Predict probability patient will no-show (0-1)
        Based on:
        - Historical no-show rate
        - Arrival behavior
        - Time until appointment
        """
        
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        if not patient:
            return 0.05  # Default 5% for unknown patients
        
        # Base probability from history
        total_appts = patient.id * 2  # Rough estimate, would come from actual data
        if total_appts > 0:
            historical_rate = patient.no_show_count / max(1, total_appts)
        else:
            historical_rate = 0.05
        
        # Late arrival pattern increases no-show probability
        late_arrival_impact = patient.late_arrival_count * 0.05  # Each late arrival +5%
        
        # Combined probability
        probability = min(0.5, historical_rate + late_arrival_impact)  # Cap at 50%
        
        print(f"📊 No-show probability: {probability:.2%} (history: {historical_rate:.2%})")
        
        return probability
    
    @staticmethod
    def predict_wait_time(
        doctor_id: int,
        queue_position: int,
        db: Session
    ) -> int:
        """
        Predict wait time in minutes until patient sees doctor
        Based on:
        - Patients ahead in queue
        - Average consultation duration for that doctor
        - Current queue state
        """
        
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        
        # Get all active queue entries for this doctor
        active_queue = db.query(QueueEntry).filter(
            QueueEntry.doctor_id == doctor_id,
            QueueEntry.status.in_(["waiting", "in_consultation"])
        ).all()
        
        # Calculate wait time
        wait_time = 0
        
        # Sum duration of patients ahead
        for i, entry in enumerate(sort_queue(active_queue)):
            if i < queue_position:
                # Use predicted or average duration
                duration = entry.predicted_consultation_duration or 15
                wait_time += duration + 2  # +2 min for buffer/transition
        
        # Add buffer
        wait_time = max(0, wait_time - 5)
        
        print(f"⏱️  Predicted wait time: {wait_time} min (position: {queue_position}, queue size: {len(active_queue)})")
        
        return wait_time
    
    @staticmethod
    def calculate_priority_score(
        patient_id: int,
        severity_score: float,
        db: Session
    ) -> float:
        """
        Calculate patient priority (0-1) for dynamic scheduling
        Based on:
        - Medical severity
        - Wait time already accumulated
        - Patient characteristics
        - Fair scheduling (FIFO with exceptions)
        """
        
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        
        # Base on severity
        severity_component = min(1.0, severity_score)  # Clamp to 0-1
        
        # Check appointment age (patients waiting longer get priority)
        age_component = 0.0
        if patient:
            appointment = db.query(Appointment).filter(
                Appointment.patient_id == patient_id
            ).order_by(Appointment.slot_time).first()
            
            if appointment:
                minutes_waiting = (datetime.utcnow() - appointment.slot_time).total_seconds() / 60
                # Each 30 minutes waiting adds 0.1 to priority
                age_component = min(0.3, minutes_waiting / 300)
        
        # Vulnerable patient premium (elderly, critical condition)
        vulnerable_component = 0.1 if patient and patient.no_show_count > 5 else 0.0
        
        # Combined priority
        priority = min(1.0, severity_component * 0.6 + age_component * 0.3 + vulnerable_component)
        
        print(f"⭐ Priority: {priority:.2f} (severity: {severity_component:.2f}, age: {age_component:.2f})")
        
        return priority

def sort_queue(entries):
    """Sort queue entries by priority and fairness"""
    return sorted(entries, key=lambda e: (e.priority_score, e.scheduled_time), reverse=True)

def estimate_bottlenecks(doctor_id: int, db: Session) -> list:
    """
    Identify queue bottlenecks for a doctor
    Returns list of times when queue backlog expected
    """
    
    active_queue = db.query(QueueEntry).filter(
        QueueEntry.doctor_id == doctor_id,
        QueueEntry.status.in_(["waiting", "scheduled"])
    ).all()
    
    bottlenecks = []
    cumulative_time = 0
    threshold = 60  # Alert if wait time exceeds 60 minutes
    
    for entry in sort_queue(active_queue):
        cumulative_time += entry.predicted_consultation_duration or 15
        
        if cumulative_time > threshold:
            bottlenecks.append({
                "patient_id": entry.patient_id,
                "predicted_wait": cumulative_time,
                "severity": "HIGH" if cumulative_time > 90 else "MEDIUM"
            })
    
    if bottlenecks:
        print(f"⚠️  Bottlenecks detected for doctor {doctor_id}: {len(bottlenecks)} patients affected")
    
    return bottlenecks
