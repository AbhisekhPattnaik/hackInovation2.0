"""
Enhanced Medical Report Router - Fully functional report management
with status tracking, reviews, and doctor assessments
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.medical_report import MedicalReport, ReportStatus
from ..models.patient import Patient
from ..models.user import User
from ..models.doctor import Doctor
from pydantic import BaseModel
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM
from datetime import datetime
import base64

router = APIRouter(prefix="/reports", tags=["Medical Reports"])

class ReportReviewRequest(BaseModel):
    status: str  # "reviewed", "approved", "flagged", "rejected"
    review_notes: str = None
    findings: str = None

def get_doctor_from_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract doctor from bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        
        if not email or role != "doctor":
            raise HTTPException(status_code=403, detail="Not a doctor account")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    return doctor

@router.post("/upload/{patient_id}")
async def upload_report(
    patient_id: int,
    user_id: int = Form(...),
    file: UploadFile = File(...),
    diagnosis: str = Form(None),
    report_type: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload medical report for a patient with metadata"""
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify uploader exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Create medical report
        report = MedicalReport(
            patient_id=patient_id,
            uploaded_by=user_id,
            file_name=file.filename,
            file_type=file.content_type,
            file_data=file_content,
            diagnosis=diagnosis,
            report_type=report_type,
            report_description=description,
            status=ReportStatus.PENDING  # Always starts as PENDING
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        print(f"✅ Report uploaded: {file.filename} for patient {patient_id}, Status: PENDING")
        
        return {
            "id": report.id,
            "message": "Report uploaded successfully - awaiting doctor review",
            "file_name": report.file_name,
            "uploaded_by": user.name,
            "status": report.status,
            "report_type": report_type,
            "created_at": report.created_at.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error uploading report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading report: {str(e)}")

@router.get("/patient/{patient_id}")
def get_patient_reports(
    patient_id: int,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """Get all reports for a patient with optional status filter"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    query = db.query(MedicalReport).filter(MedicalReport.patient_id == patient_id)
    
    if status_filter:
        try:
            filter_status = ReportStatus(status_filter)
            query = query.filter(MedicalReport.status == filter_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")
    
    reports = query.order_by(MedicalReport.created_at.desc()).all()
    
    result = []
    for report in reports:
        uploader = db.query(User).filter(User.id == report.uploaded_by).first()
        uploader_name = uploader.name if uploader else "Unknown"
        
        reviewer_name = None
        if report.reviewed_by:
            reviewer = db.query(User).filter(User.id == report.reviewed_by).first()
            reviewer_name = reviewer.name if reviewer else "Unknown"
        
        result.append({
            "id": report.id,
            "patient_id": report.patient_id,
            "file_name": report.file_name,
            "file_type": report.file_type,
            "diagnosis": report.diagnosis,
            "status": report.status,
            "report_type": report.report_type,
            "description": report.report_description,
            "findings": report.findings,
            "created_at": report.created_at,
            "reviewed_at": report.reviewed_at,
            "uploader_name": uploader_name,
            "reviewer_name": reviewer_name
        })
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.user.name if patient.user else "Unknown",
        "total_reports": len(result),
        "reports": result
    }

@router.get("/{report_id}/status")
def get_report_status(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Get current status of a report"""
    
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    reviewer_info = None
    if report.reviewed_by:
        reviewer = db.query(User).filter(User.id == report.reviewed_by).first()
        reviewer_info = {
            "reviewer_name": reviewer.name if reviewer else "Unknown",
            "reviewed_at": report.reviewed_at,
            "review_notes": report.review_notes,
            "findings": report.findings
        }
    
    return {
        "report_id": report.id,
        "file_name": report.file_name,
        "status": report.status,
        "status_description": _get_status_description(report.status),
        "created_at": report.created_at,
        "reviewer_info": reviewer_info,
        "diagnosis": report.diagnosis
    }

@router.put("/{report_id}/review")
def review_report(
    report_id: int,
    request: ReportReviewRequest,
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Doctor reviews and updates report status"""
    
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Validate status
    try:
        new_status = ReportStatus(request.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}")
    
    # Update report
    report.status = new_status
    report.reviewed_by = doctor.user_id
    report.reviewed_at = datetime.utcnow()
    report.review_notes = request.review_notes
    report.findings = request.findings
    report.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return {
        "id": report.id,
        "previous_status": report.status,
        "new_status": new_status,
        "reviewed_by": doctor.user.name,
        "reviewed_at": report.reviewed_at,
        "message": f"Report status updated to {new_status}",
        "review_notes": request.review_notes,
        "findings": request.findings
    }

@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Download a specific report"""
    
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Encode file data as base64 for transmission
    file_data_b64 = base64.b64encode(report.file_data).decode('utf-8')
    
    return {
        "file_name": report.file_name,
        "file_type": report.file_type,
        "file_data_base64": file_data_b64,
        "report_id": report.id,
        "status": report.status,
        "created_at": report.created_at
    }

@router.get("/doctor/all-patient-reports")
def get_doctor_all_patient_reports(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get all reports from doctor's patients with review status"""
    
    try:
        # Get all reports for doctor's patients - we just get all reports since this is the doctor's view
        all_reports = db.query(MedicalReport).order_by(MedicalReport.created_at.desc()).all()
        
        reports_info = []
        for report in all_reports:
            patient = db.query(Patient).filter(Patient.id == report.patient_id).first()
            uploader = db.query(User).filter(User.id == report.uploaded_by).first()
            reviewer = db.query(User).filter(User.id == report.reviewed_by).first() if report.reviewed_by else None
            
            # Get patient name
            patient_name = "Unknown"
            if patient and patient.user:
                patient_name = patient.user.name
            
            # Get uploader name
            uploader_name = uploader.name if uploader else "Unknown"
            
            # Get reviewer name
            reviewer_name = reviewer.name if reviewer else None
            
            reports_info.append({
                "report_id": report.id,
                "patient_id": report.patient_id,
                "patient_name": patient_name,
                "file_name": report.file_name,
                "report_type": report.report_type or "General",
                "description": report.report_description or "",
                "findings": report.findings or "",
                "uploaded_by": uploader_name,
                "is_patient_upload": uploader and uploader.role == "patient",
                "status": str(report.status),
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "reviewed_at": report.reviewed_at.isoformat() if report.reviewed_at else None,
                "reviewed_by": reviewer_name,
                "review_notes": report.review_notes or "",
                "diagnosis": report.diagnosis or ""
            })
        
        return {
            "doctor_id": doctor.id,
            "total_reports": len(reports_info),
            "reports": reports_info
        }
    except Exception as e:
        print(f"❌ Error fetching doctor reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching reports: {str(e)}")

@router.get("/pending-reviews")
def get_pending_report_reviews(
    doctor: Doctor = Depends(get_doctor_from_token),
    db: Session = Depends(get_db)
):
    """Get all pending reports awaiting doctor review"""
    
    try:
        pending_reports = db.query(MedicalReport).filter(
            MedicalReport.status == ReportStatus.PENDING
        ).order_by(MedicalReport.created_at).all()
        
        if not pending_reports:
            return {
                "doctor_id": doctor.id,
                "pending_count": 0,
                "reports": [],
                "message": "No pending reviews"
            }
        
        reports_info = []
        for report in pending_reports:
            patient = db.query(Patient).filter(Patient.id == report.patient_id).first()
            uploader = db.query(User).filter(User.id == report.uploaded_by).first()
            
            # Safely get patient name
            patient_name = "Unknown"
            if patient and patient.user:
                patient_name = patient.user.name
            elif patient:
                patient_name = f"Patient {patient.id}"
            
            # Determine uploader type (patient or doctor)
            uploader_name = "Unknown"
            uploader_role = "Unknown"
            if uploader:
                uploader_name = uploader.name
                uploader_role = uploader.role  # "patient" or "doctor"
            
            # Check if this is a patient-uploaded report
            is_patient_upload = uploader and uploader.role == "patient"
            
            reports_info.append({
                "report_id": report.id,
                "patient_id": report.patient_id,
                "patient_name": patient_name,
                "file_name": report.file_name,
                "report_type": report.report_type or "General",
                "description": report.report_description or "",
                "uploaded_by": uploader_name,
                "uploader_role": uploader_role,
                "is_patient_upload": is_patient_upload,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "diagnosis": report.diagnosis or ""
            })
        
        # Safely get doctor name
        doctor_name = "Unknown"
        if doctor and doctor.user:
            doctor_name = doctor.user.name
        elif doctor:
            doctor_name = doctor.name or "Doctor"
        
        return {
            "doctor_id": doctor.id,
            "doctor_name": doctor_name,
            "pending_count": len(reports_info),
            "reports": reports_info
        }
    except Exception as e:
        print(f"❌ Error fetching pending reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching pending reports: {str(e)}")

def _get_status_description(status: ReportStatus) -> str:
    """Get human-readable status description"""
    descriptions = {
        ReportStatus.PENDING: "Awaiting doctor review",
        ReportStatus.REVIEWED: "Doctor reviewed - assessment in progress",
        ReportStatus.APPROVED: "Doctor approved - findings confirmed",
        ReportStatus.FLAGGED: "Doctor flagged - requires attention",
        ReportStatus.REJECTED: "Doctor rejected - requires resubmission",
        ReportStatus.COMPLETED: "Processing complete - archived"
    }
    return descriptions.get(status, "Unknown status")
