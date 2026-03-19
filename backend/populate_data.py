"""
Script to populate sample data for PulseSync
"""
from sqlalchemy.orm import Session
from app.database.config import SessionLocal, engine, Base
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.queue import QueueEntry
from app.services.password_service import hash_password
from datetime import datetime, timedelta
import traceback

# Drop all existing tables and recreate them
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create Admin User
    admin_user = User(
        name="Admin",
        email="admin@pulsesync.io",
        phone_number="+11111111111",
        role="admin",
        password=hash_password("admin123")
    )
    db.add(admin_user)
    db.commit()
    
    # Create Doctor Users
    doc1_user = User(
        name="Dr. Ahmed Khan", 
        email="ahmed@hospital.com", 
        phone_number="+1234567890",
        role="doctor",
        password=hash_password("doctor123")
    )
    doc2_user = User(
        name="Dr. Sarah Smith", 
        email="sarah@hospital.com", 
        phone_number="+1234567891",
        role="doctor",
        password=hash_password("doctor123")
    )
    doc3_user = User(
        name="Dr. Rajesh Kumar",
        email="rajesh@hospital.com",
        phone_number="+1234567892",
        role="doctor",
        password=hash_password("doctor123")
    )
    db.add_all([doc1_user, doc2_user, doc3_user])
    db.commit()
    
    # Create Patient Users
    patient1_user = User(
        name="John Doe", 
        email="john@patient.com", 
        phone_number="+1987654321",
        role="patient",
        password=hash_password("patient123")
    )
    patient2_user = User(
        name="Maria Garcia", 
        email="maria@patient.com", 
        phone_number="+1987654322",
        role="patient",
        password=hash_password("patient123")
    )
    patient3_user = User(
        name="Alex Thompson",
        email="alex@patient.com",
        phone_number="+1987654323",
        role="patient",
        password=hash_password("patient123")
    )
    db.add_all([patient1_user, patient2_user, patient3_user])
    db.commit()
    
    # Create Doctor profiles
    doctor1 = Doctor(
        user_id=doc1_user.id,
        name="Dr. Ahmed Khan",
        specialization="Cardiology",
        avg_consult_time=20,
        utilization=0.5
    )
    doctor2 = Doctor(
        user_id=doc2_user.id,
        name="Dr. Sarah Smith",
        specialization="General Medicine",
        avg_consult_time=15,
        utilization=0.3
    )
    doctor3 = Doctor(
        user_id=doc3_user.id,
        name="Dr. Rajesh Kumar",
        specialization="Orthopedics",
        avg_consult_time=18,
        utilization=0.4
    )
    db.add_all([doctor1, doctor2, doctor3])
    db.commit()
    
    # Create Patient profiles with symptoms and AI priority
    patient1 = Patient(
        user_id=patient1_user.id, 
        severity_score=20.0,  # Low severity (headache, cold)
        predicted_duration=15,
        no_show_count=0,
        late_arrival_count=0,
        age=28,
        symptoms="headache, cold",
        ai_priority="LOW"
    )
    patient2 = Patient(
        user_id=patient2_user.id, 
        severity_score=55.0,  # Moderate severity (high fever, vomiting)
        predicted_duration=30,
        no_show_count=0,
        late_arrival_count=0,
        age=42,
        symptoms="high fever, vomiting, weakness",
        ai_priority="MODERATE"
    )
    patient3 = Patient(
        user_id=patient3_user.id,
        severity_score=35.0,  # Moderate severity (chest pain)
        predicted_duration=25,
        no_show_count=0,
        late_arrival_count=0,
        age=35,
        symptoms="chest pain, breathing difficulty",
        ai_priority="HIGH"
    )
    db.add_all([patient1, patient2, patient3])
    db.commit()
    
    # Create sample appointments
    now = datetime.utcnow()
    
    appt1 = Appointment(
        doctor_id=doctor1.id,
        patient_id=patient1.id,
        slot_time=now + timedelta(hours=1),
        status="scheduled"
    )
    appt2 = Appointment(
        doctor_id=doctor1.id,
        patient_id=patient2.id,
        slot_time=now + timedelta(hours=2),
        status="scheduled"
    )
    appt3 = Appointment(
        doctor_id=doctor2.id,
        patient_id=patient1.id,
        slot_time=now + timedelta(hours=3),
        status="scheduled"
    )
    appt4 = Appointment(
        doctor_id=doctor3.id,
        patient_id=patient3.id,
        slot_time=now + timedelta(hours=1, minutes=30),
        status="scheduled"
    )
    db.add_all([appt1, appt2, appt3, appt4])
    db.commit()
    
    # Create queue entries for appointments
    for idx, (appt, patient) in enumerate([
        (appt1, patient1),
        (appt2, patient2),
        (appt3, patient1),
        (appt4, patient3)
    ]):
        queue_entry = QueueEntry(
            appointment_id=appt.id,
            patient_id=appt.patient_id,
            doctor_id=appt.doctor_id,
            status="scheduled",
            scheduled_time=appt.slot_time,
            predicted_consultation_duration=patient.predicted_duration,
            predicted_no_show_probability=0.05,
            priority_score=patient.severity_score
        )
        db.add(queue_entry)
    db.commit()
    
    print("[OK] Sample data created successfully!")
    print("\n[ADMIN LOGIN]:")
    print("  - admin@pulsesync.io / admin123")
    print("\n[DOCTOR LOGINS]:")
    print("  - ahmed@hospital.com / doctor123 (Cardiology)")
    print("  - sarah@hospital.com / doctor123 (General Medicine)")
    print("  - rajesh@hospital.com / doctor123 (Orthopedics)")
    print("\n[PATIENT LOGINS]:")
    print(f"  - john@patient.com / patient123 (PS ID: {patient1.ps_id})")
    print(f"  - maria@patient.com / patient123 (PS ID: {patient2.ps_id})")
    print(f"  - alex@patient.com / patient123 (PS ID: {patient3.ps_id})")
    print("\n[OK] Pre-scheduled appointments and queue entries created!")
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

