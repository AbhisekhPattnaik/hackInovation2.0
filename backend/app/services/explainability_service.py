"""
Explainability service - explains AI decisions in natural language
Converts technical ML outputs into human-readable explanations
for patients, doctors, and administrators
"""

import json
from datetime import datetime

class ExplainabilityService:
    
    @staticmethod
    def generate_explanation(optimization_decision: dict) -> str:
        """Convert technical decision into human-readable explanation"""
        
        decision_type = optimization_decision.get("decision_type", "none")
        confidence = optimization_decision.get("confidence", 0.0)
        
        if decision_type == "slot_shift":
            return ExplainabilityService._explain_slot_shift(optimization_decision, confidence)
        elif decision_type == "doctor_reassign":
            return ExplainabilityService._explain_doctor_reassign(optimization_decision, confidence)
        elif decision_type == "priority_bump":
            return ExplainabilityService._explain_priority_bump(optimization_decision, confidence)
        elif decision_type == "move_earlier":
            return ExplainabilityService._explain_move_earlier(optimization_decision, confidence)
        else:
            return "No changes recommended at this time."
    
    @staticmethod
    def _explain_slot_shift(decision: dict, confidence: float) -> str:
        """Explain why appointment time is being shifted"""
        
        factors = json.loads(decision.get("factors", "{}"))
        
        explanation = (
            f"🕐 **Appointment Time Changed**\n\n"
            f"Your appointment time has been optimized to reduce wait time.\n\n"
            f"**Why?** "
            f"Our AI analyzed the queue and found that moving your appointment "
            f"by {decision.get('recommended_slot')} would:\n"
            f"• Reduce your estimated wait time from {factors.get('predicted_wait', '?')} minutes to ~20 minutes\n"
            f"• Ensure you get adequate consultation time\n"
            f"• Better match doctor availability\n\n"
            f"**Confidence Level:** {confidence:.0%}\n"
            f"**Note:** You can request to keep your original time if preferred."
        )
        
        return explanation
    
    @staticmethod
    def _explain_doctor_reassign(decision: dict, confidence: float) -> str:
        """Explain why doctor is being reassigned"""
        
        factors = json.loads(decision.get("factors", "{}"))
        
        explanation = (
            f"👨‍⚕️ **Doctor Changed for Better Service**\n\n"
            f"We've reassigned you to a different doctor with the same specialty.\n\n"
            f"**Why?** "
            f"Our real-time queue analysis shows:\n"
            f"• Your current doctor has {factors.get('queue_length', '?')} patients waiting\n"
            f"• Alternative doctor has shorter queue\n"
            f"• Both doctors have same specialization\n"
            f"• This reduces your wait time from {factors.get('predicted_wait', '?')} to ~15 minutes\n\n"
            f"**Confidence Level:** {confidence:.0%}\n"
            f"**Note:** You maintain the same appointment quality with reduced wait."
        )
        
        return explanation
    
    @staticmethod
    def _explain_priority_bump(decision: dict, confidence: float) -> str:
        """Explain why patient is being prioritized"""
        
        explanation = (
            f"⭐ **Your Appointment is Prioritized**\n\n"
            f"Based on medical complexity, your appointment has been moved earlier.\n\n"
            f"**Why?** "
            f"Our AI identified that your case:\n"
            f"• Requires immediate attention (high severity)\n"
            f"• Benefits from timely consultation\n"
            f"• Has been waiting longer than others\n\n"
            f"**Confidence Level:** {confidence:.0%}\n"
            f"**New Time:** 30 minutes earlier\n"
            f"**Important:** This prioritization ensures you get necessary care promptly."
        )
        
        return explanation
    
    @staticmethod
    def _explain_move_earlier(decision: dict, confidence: float) -> str:
        """Explain why appointment is being moved earlier"""
        
        factors = json.loads(decision.get("factors", "{}"))
        
        explanation = (
            f"📅 **Appointment Moved Earlier**\n\n"
            f"To ensure you don't miss your appointment, we've shifted your time.\n\n"
            f"**Why?** "
            f"Our predictive model shows:\n"
            f"• {factors.get('patient_history', '?')} - you've had some scheduling challenges\n"
            f"• Moving your appointment 1 hour earlier increases likelihood of attendance\n"
            f"• Earlier slots often work better for patients with busy schedules\n\n"
            f"**What happens next:**\n"
            f"1. You'll receive SMS reminder 24 hours before\n"
            f"2. Another reminder 1 hour before appointment\n"
            f"3. Easy reschedule option if needed\n\n"
            f"**Confidence Level:** {confidence:.0%}"
        )
        
        return explanation
    
    @staticmethod
    def generate_queue_dashboard_summary(queue_data: list, doctor_data: dict) -> dict:
        """Generate data for real-time queue dashboard"""
        
        total_patients = len(queue_data)
        avg_wait = sum(q.get("predicted_wait", 0) for q in queue_data) / max(1, total_patients)
        
        # Identify bottlenecks
        bottleneck_doctors = []
        for doc_id, doc_queue in doctor_data.items():
            if len(doc_queue) > 5:
                bottleneck_doctors.append({
                    "doctor_id": doc_id,
                    "queue_size": len(doc_queue),
                    "severity": "HIGH" if len(doc_queue) > 8 else "MEDIUM",
                    "recommendation": "Consider urgent care for overflow"
                })
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_patients_in_queue": total_patients,
            "average_wait_time": f"{int(avg_wait)} min",
            "max_wait_time": f"{max((q.get('predicted_wait', 0) for q in queue_data), default=0)} min",
            "bottlenecks_detected": len(bottleneck_doctors),
            "bottleneck_doctors": bottleneck_doctors,
            "system_health": ExplainabilityService._assess_system_health(avg_wait, total_patients),
            "recommended_actions": ExplainabilityService._recommend_actions(total_patients, avg_wait, bottleneck_doctors)
        }
        
        return summary
    
    @staticmethod
    def _assess_system_health(avg_wait: float, total_patients: int) -> str:
        """Assess overall queue health"""
        
        if avg_wait < 15 and total_patients < 10:
            return "🟢 HEALTHY - Optimal flow"
        elif avg_wait < 30 and total_patients < 20:
            return "🟡 GOOD - Minor delays expected"
        elif avg_wait < 60 or total_patients < 30:
            return "🟠 MODERATE - Consider interventions"
        else:
            return "🔴 CONCERN - Immediate action needed"
    
    @staticmethod
    def _recommend_actions(total_patients: int, avg_wait: float, bottlenecks: list) -> list:
        """Recommend specific actions for queue management"""
        
        actions = []
        
        if avg_wait > 60:
            actions.append("Consider opening additional consultation rooms")
            actions.append("Activate emergency room for urgent cases")
        
        if len(bottlenecks) > 2:
            actions.append("Redistribute patients to available doctors")
            actions.append("Consider limiting walk-ins temporarily")
        
        if total_patients > 30:
            actions.append("Alert staff: Queue overflow expected in 30 min")
            actions.append("Prepare telehealth option for low-risk consultations")
        
        if not actions:
            actions.append("Continue current operations - system performing well")
        
        return actions
    
    @staticmethod
    def format_for_patient_sms(decision: dict) -> str:
        """Format decision explanation as SMS (must be short)"""
        
        decision_type = decision.get("decision_type", "none")
        
        if decision_type == "slot_shift":
            return "Your appointment time changed. New time: (check app). Wait reduced from 45→20 min. Confirm?"
        elif decision_type == "doctor_reassign":
            return "Doctor changed to Dr. Kumar due to shorter queue. Same specialty. OK?"
        elif decision_type == "move_earlier":
            return "Appointment moved 1 hr earlier (6pm→5pm). Helps ensure you don't miss it. Confirm?"
        else:
            return "Your appointment is confirmed. See you soon at scheduled time."
    
    @staticmethod
    def format_for_doctor_dashboard(decision: dict, patient_name: str) -> str:
        """Format decision for doctor view"""
        
        decision_type = decision.get("decision_type", "none")
        
        if decision_type == "doctor_reassign":
            return f"⚠️ Patient {patient_name} reassigned to you (queue optimization - {decision.get('reasoning')})"
        elif decision_type == "slot_shift":
            return f"📅 {patient_name}'s appointment rescheduled to optimize queue flow"
        elif decision_type == "priority_bump":
            return f"⭐ PRIORITY: {patient_name} moved up in queue (high severity)"
        else:
            return f"📋 Standard appointment: {patient_name}"
