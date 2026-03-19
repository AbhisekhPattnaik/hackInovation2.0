from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get JWT configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "pulsesync-dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)