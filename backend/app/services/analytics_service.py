"""
Advanced Analytics Service
Provides comprehensive analytics for doctor dashboard
- Queue analytics
- Performance metrics  
- Patient satisfaction metrics
- Efficiency trends
- AI-powered insights
"""

from sqlalchemy.orm import Session
from ..models.appointment import Appointment
from ..models.queue import QueueEntry
from ..models.patient import Patient
from ..models.doctor import Doctor
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class AnalyticsService:
    
    @staticmethod
    def get_doctor_performance_metrics(doctor_id: int, days: int = 30, db: Session = None) -> dict:
        """
        Calculate comprehensive performance metrics for a doctor
        """
        
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return {"error": "Doctor not found"}
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Get all appointments in period
        appointments = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time >= start_date
        ).all()
        
        if not appointments:
            return {
                "doctor_name": doctor.user.name,
                "period_days": days,
                "metrics": {
                    "total_appointments": 0,
                    "completed": 0,
                    "no_shows": 0,
                    "cancellations": 0
                },
                "message": "No data for this period"
            }
        
        # Count statuses
        completed = [a for a in appointments if a.status == "completed"]
        no_shows = [a for a in appointments if a.status == "no-show"]
        cancellations = [a for a in appointments if a.status == "cancelled"]
        
        # Calculate timing metrics
        consultation_times = []
        wait_times = []
        
        for appt in completed:
            if appt.start_time and appt.end_time:
                consultation_duration = (appt.end_time - appt.start_time).total_seconds() / 60
                consultation_times.append(consultation_duration)
            
            if appt.created_at and appt.start_time:
                appointment_wait = (appt.start_time - appt.created_at).total_seconds() / 60
                wait_times.append(appointment_wait)
        
        # Statistics
        avg_consultation = statistics.mean(consultation_times) if consultation_times else 0
        median_consultation = statistics.median(consultation_times) if consultation_times else 0
        
        avg_wait = statistics.mean(wait_times) if wait_times else 0
        median_wait = statistics.median(wait_times) if wait_times else 0
        
        # Calculate rates
        show_rate = len(completed) / len(appointments) if appointments else 0
        no_show_rate = len(no_shows) / len(appointments) if appointments else 0
        completion_rate = len(completed) / len(appointments) if appointments else 0
        
        # Patients per day
        daily_appointments = defaultdict(int)
        for appt in appointments:
            if appt.start_time:
                date_key = appt.start_time.date()
                daily_appointments[date_key] += 1
        
        avg_appointments_per_day = statistics.mean(daily_appointments.values()) if daily_appointments else 0
        
        # Utilization
        total_hours = len(appointments) * (avg_consultation / 60) if avg_consultation > 0 else 0
        working_days = len(set(a.start_time.date() for a in completed if a.start_time))
        available_hours = working_days * 8  # Assume 8-hour day
        utilization = (total_hours / available_hours * 100) if available_hours > 0 else 0
        
        return {
            "doctor_id": doctor_id,
            "doctor_name": doctor.user.name if doctor.user else "Unknown",
            "specialization": doctor.specialization,
            "period_days": days,
            "metrics": {
                "total_appointments": len(appointments),
                "completed": len(completed),
                "no_shows": len(no_shows),
                "cancellations": len(cancellations),
                "show_rate_percent": round(show_rate * 100, 1),
                "no_show_rate_percent": round(no_show_rate * 100, 1),
                "completion_rate_percent": round(completion_rate * 100, 1)
            },
            "timing_metrics": {
                "avg_consultation_minutes": round(avg_consultation, 1),
                "median_consultation_minutes": round(median_consultation, 1),
                "avg_wait_time_minutes": round(avg_wait, 1),
                "median_wait_time_minutes": round(median_wait, 1)
            },
            "efficiency_metrics": {
                "appointments_per_day": round(avg_appointments_per_day, 1),
                "utilization_percent": round(utilization, 1),
                "working_days": working_days,
                "total_hours_booked": round(total_hours, 1)
            },
            "quality_score": AnalyticsService._calculate_quality_score(
                show_rate, no_show_rate, utilization, avg_consultation
            )
        }
    
    @staticmethod
    def get_queue_analytics(doctor_id: int, db: Session) -> dict:
        """
        Get current queue analytics for a doctor
        """
        
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            return {"error": "Doctor not found"}
        
        # Current queue
        queue_entries = db.query(QueueEntry).filter(
            QueueEntry.doctor_id == doctor_id,
            QueueEntry.status.in_(["scheduled", "waiting"])
        ).order_by(QueueEntry.priority_score.desc(), QueueEntry.scheduled_time).all()
        
        if not queue_entries:
            return {
                "doctor_name": doctor.user.name,
                "queue_size": 0,
                "message": "Queue is empty"
            }
        
        # Calculate metrics
        total_estimated_time = sum(e.predicted_consultation_duration for e in queue_entries)
        avg_no_show_risk = statistics.mean([e.predicted_no_show_probability for e in queue_entries])
        avg_priority = statistics.mean([e.priority_score for e in queue_entries])
        
        high_priority_count = sum(1 for e in queue_entries if e.priority_score > 0.7)
        high_risk_count = sum(1 for e in queue_entries if e.predicted_no_show_probability > 0.4)
        
        # Next patient
        next_patient = queue_entries[0] if queue_entries else None
        next_patient_info = None
        if next_patient:
            patient = db.query(Patient).filter(Patient.id == next_patient.patient_id).first()
            next_patient_info = {
                "patient_id": next_patient.patient_id,
                "patient_name": patient.user.name if patient and patient.user else "Unknown",
                "ps_id": patient.ps_id if patient else "Unknown",
                "severity": patient.severity_score if patient else 0,
                "predicted_duration": next_patient.predicted_consultation_duration,
                "no_show_risk": f"{next_patient.predicted_no_show_probability:.0%}",
                "priority": next_patient.priority_score
            }
        
        return {
            "doctor_name": doctor.user.name if doctor.user else "Unknown",
            "queue_size": len(queue_entries),
            "total_estimated_time_minutes": total_estimated_time,
            "average_session_time": round(total_estimated_time / len(queue_entries), 1) if queue_entries else 0,
            "high_priority_patients": high_priority_count,
            "high_no_show_risk_patients": high_risk_count,
            "average_priority_score": round(avg_priority, 2),
            "average_no_show_risk": round(avg_no_show_risk, 2),
            "risk_level": "CRITICAL" if high_risk_count > 2 else "HIGH" if high_risk_count > 0 else "LOW",
            "next_patient": next_patient_info,
            "queue_details": [
                {
                    "position": idx + 1,
                    "patient_id": entry.patient_id,
                    "duration": entry.predicted_consultation_duration,
                    "priority": entry.priority_score,
                    "no_show_risk": f"{entry.predicted_no_show_probability:.0%}"
                } for idx, entry in enumerate(queue_entries[:10])
            ]
        }
    
    @staticmethod
    def get_efficiency_insights(doctor_id: int, db: Session) -> dict:
        """
        Generate AI-powered efficiency insights
        """
        
        try:
            metrics = AnalyticsService.get_doctor_performance_metrics(doctor_id, days=30, db=db)
            
            if "error" in metrics:
                return metrics
            
            insights = []
            recommendations = []
            
            # Analyze performance - with safe access
            util = metrics.get("efficiency_metrics", {}).get("utilization_percent", 0)
            show_rate = metrics.get("metrics", {}).get("show_rate_percent", 100)
            avg_consult = metrics.get("timing_metrics", {}).get("avg_consultation_minutes", 15)
            
            # Insights based on metrics
            if util > 90:
                insights.append({
                    "type": "warning",
                    "title": "High Utilization",
                    "message": f"You're running at {util}% capacity. Consider scheduling breaks.",
                    "priority": "HIGH"
                })
                recommendations.append("Request additional staff support")
            
            if show_rate < 80:
                insights.append({
                    "type": "alert",
                    "title": "Low Show Rate",
                    "message": f"Only {show_rate}% of patients are showing up. Consider SMS reminders.",
                    "priority": "HIGH"
                })
                recommendations.append("Enable automated reminder SMS system")
            
            if avg_consult < 10:
                insights.append({
                    "type": "info",
                    "title": "Very Efficient Sessions",
                    "message": f"You're completing consultations in just {avg_consult} min on average.",
                    "priority": "MEDIUM"
                })
            elif avg_consult > 40:
                insights.append({
                    "type": "warning",
                    "title": "Long Consultation Times",
                    "message": f"Your consultations average {avg_consult} min. Consider time management.",
                    "priority": "MEDIUM"
                })
                recommendations.append("Review complex cases to identify patterns")
            
            quality_score = metrics.get("quality_score", 0)
            if quality_score > 85:
                insights.append({
                    "type": "success",
                    "title": "Excellent Quality Score",
                    "message": f"Your quality score is {quality_score}. Keep up the great work!",
                    "priority": "LOW"
                })
            
            return {
                "doctor_id": doctor_id,
                "insights": insights,
                "recommendations": recommendations,
                "overall_health": AnalyticsService._calculate_overall_health(metrics),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # Return safe default response on error
            return {
                "doctor_id": doctor_id,
                "insights": [{"type": "info", "title": "System Status", "message": "Loading insights...", "priority": "LOW"}],
                "recommendations": [],
                "overall_health": "UNKNOWN",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    @staticmethod
    def _calculate_quality_score(show_rate: float, no_show_rate: float, utilization: float, avg_consultation: float) -> float:
        """
        Calculate overall quality score (0-100)
        """
        
        score = 0
        
        # Show rate (max 25 points)
        score += show_rate * 25
        
        # Utilization (max 25 points, optimal is 60-80%)
        if 60 <= utilization <= 80:
            score += 25
        elif utilization < 60:
            score += (utilization / 60) * 25
        else:
            score += max(0, 25 - ((utilization - 80) / 20) * 25)
        
        # Consultation time (max 25 points, optimal is 15-30 min)
        if 15 <= avg_consultation <= 30:
            score += 25
        elif avg_consultation < 15:
            score += (avg_consultation / 15) * 25
        else:
            score += max(0, 25 - ((avg_consultation - 30) / 30) * 25)
        
        # No-show rate (max 25 points, lower is better)
        score += (1 - min(no_show_rate, 1)) * 25
        
        return round(min(100, max(0, score)), 1)
    
    @staticmethod
    def _calculate_overall_health(metrics: dict) -> str:
        """
        Calculate overall health status
        """
        
        if "error" in metrics:
            return "UNKNOWN"
        
        util = metrics["efficiency_metrics"]["utilization_percent"]
        show_rate = metrics["metrics"]["show_rate_percent"]
        quality = metrics.get("quality_score", 50)
        
        if util > 95 or show_rate < 70 or quality < 60:
            return "CRITICAL"
        elif util > 85 or show_rate < 80 or quality < 75:
            return "WARNING"
        elif quality >= 85:
            return "EXCELLENT"
        else:
            return "GOOD"
