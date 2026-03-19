"""
Graph-Based Queue Modeling
Models patient flow across departments as a network
- Nodes: Doctor/Department
- Edges: Patient transfers
- Metrics: Flow rate, bottlenecks, cycle time
"""

from sqlalchemy.orm import Session
from ..models.queue import QueueEntry
from ..models.appointment import Appointment
from ..models.patient import Patient
from ..models.doctor import Doctor
from datetime import datetime, timedelta
from collections import defaultdict

class GraphQueueModel:
    
    @staticmethod
    def build_queue_graph(db: Session) -> dict:
        """
        Build a graph representation of queue system
        Returns: nodes (doctors/departments) and edges (patient flows)
        """
        
        # Get all active queue entries
        queue_entries = db.query(QueueEntry).filter(
            QueueEntry.status.in_(["scheduled", "waiting"])
        ).all()
        
        # Build doctor nodes
        doctor_ids = set(entry.doctor_id for entry in queue_entries)
        doctors = db.query(Doctor).filter(Doctor.id.in_(doctor_ids)).all()
        
        nodes = {}
        for doctor in doctors:
            specialist_appts = [e for e in queue_entries if e.doctor_id == doctor.id]
            total_wait = sum(e.predicted_consultation_duration for e in specialist_appts)
            
            nodes[doctor.id] = {
                "id": doctor.id,
                "name": doctor.user.name if doctor.user else "Unknown",
                "specialization": doctor.specialization,
                "queue_size": len(specialist_appts),
                "total_queue_time": total_wait,
                "avg_consultation_time": (total_wait / len(specialist_appts)) if specialist_appts else 0,
                "no_show_risk": sum(e.predicted_no_show_probability for e in specialist_appts) / len(specialist_appts) if specialist_appts else 0,
                "utilization": min(100, (total_wait / 420) * 100)  # 7 hours = 420 minutes
            }
        
        # Build edges (patient dependencies/transfers)
        edges = []
        patient_ids = set(entry.patient_id for entry in queue_entries)
        
        for patient_id in patient_ids:
            patient_queue_entries = [e for e in queue_entries if e.patient_id == patient_id]
            
            # If patient has multiple appointments (transfers), create edges
            if len(patient_queue_entries) > 1:
                sorted_entries = sorted(patient_queue_entries, key=lambda e: e.scheduled_time)
                for i in range(len(sorted_entries) - 1):
                    edges.append({
                        "from_doctor_id": sorted_entries[i].doctor_id,
                        "to_doctor_id": sorted_entries[i + 1].doctor_id,
                        "patient_id": patient_id,
                        "transfer_time": (sorted_entries[i + 1].scheduled_time - sorted_entries[i].scheduled_time).total_seconds() / 60
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_queue_entries": len(queue_entries),
            "total_patients": len(patient_ids),
            "total_doctors": len(doctors)
        }
    
    @staticmethod
    def identify_bottlenecks(db: Session) -> dict:
        """
        Identify bottlenecks in queue system
        Returns: departments with high wait times, doctor overload, etc.
        """
        
        graph = GraphQueueModel.build_queue_graph(db)
        
        bottlenecks = {
            "doctor_overload": [],
            "high_wait_time": [],
            "high_no_show_risk": [],
            "specialist_bottleneck": []
        }
        
        for doctor_id, node in graph["nodes"].items():
            # Doctor overload: >80% utilization
            if node["utilization"] > 80:
                bottlenecks["doctor_overload"].append({
                    "doctor_id": doctor_id,
                    "doctor_name": node["name"],
                    "utilization": node["utilization"],
                    "queue_size": node["queue_size"],
                    "severity": "CRITICAL" if node["utilization"] > 95 else "HIGH"
                })
            
            # High wait time: >60 minutes total
            if node["total_queue_time"] > 60:
                bottlenecks["high_wait_time"].append({
                    "doctor_id": doctor_id,
                    "doctor_name": node["name"],
                    "total_wait": node["total_queue_time"],
                    "avg_wait_per_patient": node["total_queue_time"] / max(1, node["queue_size"]),
                    "queue_size": node["queue_size"]
                })
            
            # High no-show risk
            if node["no_show_risk"] > 0.3:
                bottlenecks["high_no_show_risk"].append({
                    "doctor_id": doctor_id,
                    "doctor_name": node["name"],
                    "avg_no_show_risk": node["no_show_risk"],
                    "affected_patients": node["queue_size"]
                })
            
            # Specialist bottleneck (specialty-specific analysis)
            if node["queue_size"] > 5:
                bottlenecks["specialist_bottleneck"].append({
                    "doctor_id": doctor_id,
                    "specialization": node["specialization"],
                    "queue_size": node["queue_size"],
                    "recommendation": f"Consider calling additional {node['specialization']} resource"
                })
        
        return bottlenecks
    
    @staticmethod
    def analyze_patient_flow(db: Session) -> dict:
        """
        Analyze patient movement through system
        Returns: flow metrics, average cycle time, path efficiency
        """
        
        # Get all completed appointments from today
        today = datetime.now().date()
        today_appts = db.query(Appointment).filter(
            Appointment.status == "completed",
            Appointment.start_time >= datetime.combine(today, datetime.min.time())
        ).all()
        
        # Group by patient to trace paths
        patient_paths = defaultdict(list)
        for appt in today_appts:
            if appt.patient_id:
                patient_paths[appt.patient_id].append({
                    "doctor_id": appt.doctor_id,
                    "start_time": appt.start_time,
                    "end_time": appt.end_time
                })
        
        # Analyze flow
        total_cycle_time = 0
        path_count = 0
        specialist_flows = defaultdict(int)
        
        for patient_id, path in patient_paths.items():
            if len(path) > 1:
                # Multi-step path
                sorted_path = sorted(path, key=lambda x: x["start_time"])
                cycle_time = (sorted_path[-1]["end_time"] - sorted_path[0]["start_time"]).total_seconds() / 60
                total_cycle_time += cycle_time
                path_count += 1
                
                # Track specialist transitions
                for i in range(len(sorted_path) - 1):
                    flow_key = f"{sorted_path[i]['doctor_id']}->{sorted_path[i+1]['doctor_id']}"
                    specialist_flows[flow_key] += 1
        
        avg_cycle_time = (total_cycle_time / path_count) if path_count > 0 else 0
        
        return {
            "patients_processed": len(today_appts),
            "multi_step_patients": path_count,
            "average_cycle_time_minutes": avg_cycle_time,
            "total_flow_paths": path_count,
            "specialist_transitions": dict(specialist_flows),
            "efficiency_score": min(100, (30 / max(1, avg_cycle_time)) * 100)  # Ideal is 30 min
        }
    
    @staticmethod
    def recommend_resource_allocation(db: Session) -> dict:
        """
        Recommend resource allocation based on queue graph
        Returns: suggestions to optimize staffing
        """
        
        graph = GraphQueueModel.build_queue_graph(db)
        bottlenecks = GraphQueueModel.identify_bottlenecks(db)
        
        recommendations = []
        
        # Overloaded doctors - recommend assistant or transfer
        for overload in bottlenecks["doctor_overload"]:
            recommendations.append({
                "type": "add_support",
                "doctor_name": overload["doctor_name"],
                "action": f"Assign medical assistant to {overload['doctor_name']}",
                "expected_impact": "Reduce utilization to <70%",
                "priority": "HIGH" if overload["utilization"] > 95 else "MEDIUM"
            })
        
        # Specialty bottlenecks
        specialty_groups = defaultdict(list)
        for doctor_id, node in graph["nodes"].items():
            specialty_groups[node["specialization"]].append(node)
        
        for specialty, doctors in specialty_groups.items():
            total_patients = sum(d["queue_size"] for d in doctors)
            if total_patients > 15:
                recommendations.append({
                    "type": "call_specialist",
                    "specialty": specialty,
                    "total_patients_waiting": total_patients,
                    "action": f"Call additional {specialty} specialist on call",
                    "priority": "HIGH"
                })
        
        return {
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "estimated_impact": f"Could improve overall queue efficiency by 15-25%"
        }
