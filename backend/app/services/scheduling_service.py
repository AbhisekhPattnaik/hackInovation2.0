from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.appointment import Appointment

def assign_slot(db: Session, doctor_id: int, severity_score: float):

    # Base start time (now)
    start_time = datetime.utcnow()

    # Get all existing appointments for doctor
    appointments = db.query(Appointment)\
        .filter(Appointment.doctor_id == doctor_id)\
        .order_by(Appointment.slot_time)\
        .all()

    # Each slot = 15 mins
    slot_duration = timedelta(minutes=15)

    if not appointments:
        return start_time

    last_appointment = appointments[-1]
    next_slot = last_appointment.slot_time + slot_duration

    # Emergency override
    if severity_score > 80:
        return start_time  # push to immediate slot

    return next_slot