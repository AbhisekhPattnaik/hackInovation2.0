from sqlalchemy.orm import Session
from ..models.doctor import Doctor
from ..models.appointment import Appointment

# Map symptoms to doctor specializations
SYMPTOM_TO_SPECIALIZATION = {
    "fever": ["General Medicine", "Internal Medicine"],
    "headache": ["Neurology", "General Medicine"],
    "chest pain": ["Cardiology", "Internal Medicine"],
    "cough": ["Pulmonology", "General Medicine"],
    "back pain": ["Orthopedics", "General Medicine"],
    "stomach pain": ["Gastroenterology", "General Medicine"],
    "dizziness": ["Neurology", "Cardiology"],
    "fatigue": ["General Medicine", "Internal Medicine"],
    "anxiety": ["Psychiatry", "General Medicine"],
    "depression": ["Psychiatry", "General Medicine"],
    "skin rash": ["Dermatology", "General Medicine"],
    "joint pain": ["Orthopedics", "Rheumatology"],
    "difficulty breathing": ["Pulmonology", "Cardiology"],
    "diabetes": ["Endocrinology", "General Medicine"],
    "high blood pressure": ["Cardiology", "Internal Medicine"],
}

def get_specializations_for_symptoms(symptoms: list) -> list:
    """Get list of specializations that match the symptoms"""
    specializations = set()
    
    for symptom in symptoms:
        symptom_lower = symptom.lower()
        if symptom_lower in SYMPTOM_TO_SPECIALIZATION:
            specializations.update(SYMPTOM_TO_SPECIALIZATION[symptom_lower])
    
    return list(specializations) if specializations else ["General Medicine"]

def select_best_doctor(db: Session, symptoms: list = None):
    """Select best doctor based on symptoms and appointment count"""
    
    doctors = db.query(Doctor).all()
    
    if not doctors:
        return None
    
    # If symptoms provided, prioritize matching specialization
    if symptoms and len(symptoms) > 0:
        required_specializations = get_specializations_for_symptoms(symptoms)
        
        # First try to find doctor with matching specialization and least appointments
        best_doctor = None
        min_appointments = float("inf")
        
        # Check doctors with matching specialization
        for doctor in doctors:
            if doctor.specialization in required_specializations:
                count = db.query(Appointment)\
                    .filter(Appointment.doctor_id == doctor.id)\
                    .count()
                
                if count < min_appointments:
                    min_appointments = count
                    best_doctor = doctor
        
        # If found a matching doctor, return them
        if best_doctor:
            print(f"✅ Selected Dr. {best_doctor.name} ({best_doctor.specialization}) for symptoms: {symptoms}")
            return best_doctor
    
    # Fallback: select doctor with least appointments (General Medicine preference)
    best_doctor = None
    min_appointments = float("inf")
    gp_doctor = None  # General Practitioner as backup
    
    for doctor in doctors:
        count = db.query(Appointment)\
            .filter(Appointment.doctor_id == doctor.id)\
            .count()
        
        if count < min_appointments:
            min_appointments = count
            best_doctor = doctor
        
        # Keep track of GP
        if doctor.specialization == "General Medicine" and count < min_appointments:
            gp_doctor = doctor
    
    # Prefer GP if available
    selected = gp_doctor if gp_doctor else best_doctor
    
    if selected:
        print(f"✅ Selected Dr. {selected.name} ({selected.specialization}) - {min_appointments} appointments")
    
    return selected
