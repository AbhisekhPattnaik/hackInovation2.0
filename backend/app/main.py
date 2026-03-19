from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from .database.config import engine, Base
from . import models
from .routers.user_router import router as user_router
from .routers.appointment_router import router as appointment_router
from .routers.appointment_advanced_router import router as appointment_advanced_router
from .routers.report_router import router as report_router
from .routers.report_advanced_router import router as report_advanced_router
from .routers.queue_router import router as queue_router
from .routers.admin_router import router as admin_router
from .routers.otp_router import router as otp_router
from .routers.health_router import router as health_router
from .routers.analytics_router import router as analytics_router
from .routers.ml_router import router as ml_router
from .routers.prescription_router import router as prescription_router
from .auth_routes import router as auth_router

# Create FastAPI app
app = FastAPI(title="PulseSync AI")

# Add CORS middleware FIRST so it wraps all routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router)
app.include_router(appointment_router)
app.include_router(appointment_advanced_router)
app.include_router(report_router)
app.include_router(report_advanced_router)
app.include_router(queue_router)
app.include_router(admin_router)
app.include_router(otp_router)
app.include_router(health_router)
app.include_router(analytics_router)
app.include_router(ml_router)
app.include_router(prescription_router)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "PulseSync Backend Running ✓", "features": "Patient & Doctor Dashboards"}