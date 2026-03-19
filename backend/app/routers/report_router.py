from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Header
from sqlalchemy.orm import Session
from ..database.sesion import get_db
from ..models.medical_report import MedicalReport
from ..models.patient import Patient
from ..models.user import User
from ..schemas.medical_report_schema import MedicalReportResponse
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM
import base64

router = APIRouter(prefix="/reports", tags=["Medical Reports"])

def get_current_user_from_token(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Extract user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_parts = authorization.split()
        if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = token_parts[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/my-reports", response_model=list[MedicalReportResponse])
def get_my_reports(current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    """Get all medical reports for the current logged-in patient with doctor review notes"""
    
    # Verify user is a patient
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=403, detail="Only patients can view their reports")
    
    # Get all reports for this patient ordered by most recent
    reports = db.query(MedicalReport).filter(MedicalReport.patient_id == patient.id).order_by(MedicalReport.created_at.desc()).all()
    
    result = []
    for report in reports:
        uploader = db.query(User).filter(User.id == report.uploaded_by).first()
        uploader_name = uploader.name if uploader else "Unknown"
        
        reviewed_by_name = None
        if report.reviewed_by:
            reviewer = db.query(User).filter(User.id == report.reviewed_by).first()
            reviewed_by_name = reviewer.name if reviewer else "Unknown"
        
        result.append(MedicalReportResponse(
            id=report.id,
            patient_id=report.patient_id,
            file_name=report.file_name,
            file_type=report.file_type,
            diagnosis=report.diagnosis,
            created_at=report.created_at,
            uploader_name=uploader_name,
            status=str(report.status) if report.status else "pending",
            review_notes=report.review_notes,
            findings=report.findings,
            reviewed_by=reviewed_by_name,
            reviewed_at=report.reviewed_at,
            report_type=report.report_type,
            description=report.report_description
        ))
    
    return result

@router.post("/upload/{patient_id}")
async def upload_report(
    patient_id: int,
    user_id: int = Form(...),
    file: UploadFile = File(...),
    diagnosis: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload medical report for a patient"""
    
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
            diagnosis=diagnosis
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        print(f"✅ Report uploaded: {file.filename} for patient {patient_id}")
        
        return {
            "id": report.id,
            "message": "Report uploaded successfully",
            "file_name": report.file_name,
            "uploaded_by": user.name
        }
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error uploading report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading report: {str(e)}")

@router.get("/patient/{patient_id}", response_model=list[MedicalReportResponse])
def get_patient_reports(patient_id: int, db: Session = Depends(get_db)):
    """Get all reports for a patient"""
    
    reports = db.query(MedicalReport).filter(MedicalReport.patient_id == patient_id).all()
    
    result = []
    for report in reports:
        uploader = db.query(User).filter(User.id == report.uploaded_by).first()
        uploader_name = uploader.name if uploader else "Unknown"
        
        result.append(MedicalReportResponse(
            id=report.id,
            patient_id=report.patient_id,
            file_name=report.file_name,
            file_type=report.file_type,
            diagnosis=report.diagnosis,
            created_at=report.created_at,
            uploader_name=uploader_name
        ))
    
    return result

@router.get("/{report_id}/download")
def download_report(report_id: int, db: Session = Depends(get_db)):
    """Download a specific report"""
    
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Encode file data as base64 for transmission
    file_data_b64 = base64.b64encode(report.file_data).decode('utf-8')
    
    return {
        "file_name": report.file_name,
        "file_type": report.file_type,
        "file_data": file_data_b64,
        "diagnosis": report.diagnosis,
        "created_at": report.created_at
    }

@router.put("/{report_id}/diagnosis")
def update_diagnosis(report_id: int, diagnosis: str, db: Session = Depends(get_db)):
    """Update diagnosis for a report (doctor use)"""
    
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.diagnosis = diagnosis
    db.commit()
    db.refresh(report)
    
    print(f"✅ Diagnosis updated for report {report_id}")
    
    return {
        "message": "Diagnosis updated successfully",
        "report_id": report.id,
        "diagnosis": report.diagnosis
    }

@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report"""
    
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    
    print(f"✅ Report {report_id} deleted")
    
    return {"message": "Report deleted successfully"}
