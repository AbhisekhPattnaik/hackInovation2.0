"""
AI Doctor Matching Engine
Matches patients with best doctors based on specialty, availability, utilization, and experience
"""

from sqlalchemy.orm import Session
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..models.appointment import Appointment
from datetime import datetime, timedelta

class AIDoctorMatcher:
    def __init__(self, db: Session):
        self.db = db
    
    def match_doctor(self, patient_id: int, symptoms: str = None) -> list:
        """
        AI matches patient with best doctors
        Returns: [best_doctor, alternative_1, alternative_2]
        """
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return []
        
        # Get all VERIFIED doctors
        doctors = self.db.query(Doctor).filter(
            Doctor.verification_status == "VERIFIED"
        ).all()
        
        if not doctors:
            return []
        
        # Score each doctor
        scores = []
        for doctor in doctors:
            score = self._calculate_doctor_score(doctor, patient, symptoms)
            scores.append({
                "doctor": doctor,
                "score": score["confidence"],
                "details": score
            })
        
        # Sort by score descending
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 3
        return [
            {
                "doctor_id": item["doctor"].id,
                "name": item["doctor"].name,
                "specialty": item["doctor"].specialization,
                "confidence": round(item["score"], 2),
                "utilization": item["doctor"].utilization,
                "rating": item["doctor"].rating,
                "explanation": item["details"]["explanation"]
            }
            for item in scores[:3]
        ]
    
    def _calculate_doctor_score(self, doctor: Doctor, patient: Patient, symptoms: str = None) -> dict:
        """
        Calculate match score based on:
        - Specialty matching (if symptoms provided)
        - Availability (fewer appointments = higher score)
        - Utilization balance
        - Experience
        - Rating
        """
        base_score = 0.5
        explanation_parts = []
        
        # 1. Specialty matching (30% weight)
        specialty_score = 0.7  # Default
        if symptoms:
            specialty_match = self._get_specialty_for_symptoms(symptoms)
            if specialty_match.lower() in doctor.specialization.lower():
                specialty_score = 0.95
                explanation_parts.append(f"Specialty match: {specialty_match}")
            else:
                specialty_score = 0.5
        base_score += specialty_score * 0.3
        
        # 2. Availability (30% weight)
        appointment_count = self.db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status.in_(["scheduled", "in_progress"])
        ).count()
        
        availability_score = max(0, 1.0 - (appointment_count * 0.1))
        explanation_parts.append(f"Availability: {int(appointment_count)} existing appointments")
        base_score += availability_score * 0.3
        
        # 3. Utilization balance (25% weight)
        # Prefer doctors with 40-60% utilization
        ideal_util = 0.5
        util_diff = abs(doctor.utilization - ideal_util)
        utilization_score = max(0, 1.0 - (util_diff * 2))
        explanation_parts.append(f"Utilization: {int(doctor.utilization * 100)}%")
        base_score += utilization_score * 0.25
        
        # 4. Experience & Rating (15% weight)
        experience_score = min(1.0, 0.5 + (doctor.years_of_experience * 0.05))
        rating_score = min(1.0, doctor.rating / 5.0)
        quality_score = (experience_score + rating_score) / 2
        explanation_parts.append(f"Experience: {doctor.years_of_experience} years, Rating: {doctor.rating}/5")
        base_score += quality_score * 0.15
        
        # Cap at 1.0
        final_score = min(1.0, base_score)
        
        return {
            "confidence": final_score,
            "explanation": " | ".join(explanation_parts)
        }
    
    def _get_specialty_for_symptoms(self, symptoms: str) -> str:
        """
        AI Maps symptoms to medical specialty
        (In production, use NLP/ML model)
        """
        symptoms_lower = symptoms.lower()
        
        specialty_map = {
            "cardiology": ["chest", "heart", "cardiac", "angina", "arrhythmia"],
            "orthopedics": ["bone", "fracture", "joint", "back", "spine", "muscle"],
            "dermatology": ["skin", "rash", "acne", "allergic", "eczema"],
            "neurology": ["headache", "migraine", "stroke", "seizure", "neurological"],
            "general medicine": ["fever", "cold", "flu", "general", "checkup"],
            "pediatrics": ["child", "baby", "infant", "kids", "pediatric"],
        }
        
        for specialty, keywords in specialty_map.items():
            if any(keyword in symptoms_lower for keyword in keywords):
                return specialty
        
        return "general medicine"
