from sqlalchemy import Column, Integer, String, DateTime, Boolean
from ..database.config import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, nullable=True)
    password = Column(String)
    role = Column(String)  # "doctor" or "patient"
    created_at = Column(DateTime, default=datetime.utcnow)