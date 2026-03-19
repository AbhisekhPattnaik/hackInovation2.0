from sqlalchemy import Column, Integer, String, DateTime, Text
from ..database.config import Base
from datetime import datetime

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String)  # ERROR, WARNING, INFO, ALERT
    message = Column(Text)
    source = Column(String, nullable=True)  # e.g., "AUTH", "OTP", "AI", "APPOINTMENT"
    user_id = Column(Integer, nullable=True)  # Related user if applicable
    severity = Column(String, default="INFO")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Integer, default=0)  # Boolean as integer
