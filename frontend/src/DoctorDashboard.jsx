import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './DoctorDashboard.css';
import { InsightCard, NoDataPlaceholder } from './AnalyticsComponents';
import { 
  PerformanceSummaryChart, 
  UtilizationForecastChart, 
  TimingMetricsChart,
  EfficiencyMetricsChart,
  QualityScoreChart
} from './AnalyticsCharts';

const DoctorDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [doctor, setDoctor] = useState(null);
  const [todayQueue, setTodayQueue] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [insights, setInsights] = useState(null);
  const [utilizationForecast, setUtilizationForecast] = useState(null);
  const [delayPrediction, setDelayPrediction] = useState(null);
  const [queueOptimization, setQueueOptimization] = useState(null);
  const [slotReassignments, setSlotReassignments] = useState(null);
  const [queueGraphModel, setQueueGraphModel] = useState(null);
  const [pendingReports, setPendingReports] = useState(null);
  const [allPatientReports, setAllPatientReports] = useState(null);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [patientDetails, setPatientDetails] = useState(null);
  const [showPatientModal, setShowPatientModal] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [showQueueAnalyzerModal, setShowQueueAnalyzerModal] = useState(false);
  const [showPatientPredictorModal, setShowPatientPredictorModal] = useState(false);
  const [showDatasetExplorerModal, setShowDatasetExplorerModal] = useState(false);
  const [showReportActionModal, setShowReportActionModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [reportAction, setReportAction] = useState(null);
  const [reportNotes, setReportNotes] = useState('');
  const [reportFilterType, setReportFilterType] = useState('all');
  const [reportViewType, setReportViewType] = useState('pending');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const token = localStorage.getItem('token');
  const API_URL = 'http://127.0.0.1:8000';

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    fetchAllData();
    // Refresh data every 30 seconds for real-time updates
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, [token, navigate]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      console.log('Fetching all data...');
      
      // Fetch doctor info
      const doctorRes = await fetch(`${API_URL}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (doctorRes.ok) {
        const doctorData = await doctorRes.json();
        setDoctor(doctorData);
        console.log('Doctor data loaded');
      } else {
        console.warn('Failed to fetch doctor info:', doctorRes.status);
      }

      // Fetch today's queue
      const queueRes = await fetch(`${API_URL}/appointments/advanced/doctor/today-queue`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (queueRes.ok) {
        const queueData = await queueRes.json();
        setTodayQueue(queueData);
        console.log('Queue data loaded');
      } else {
        console.warn('Failed to fetch queue:', queueRes.status);
      }

      // Fetch performance metrics
      const perfRes = await fetch(`${API_URL}/analytics/doctor/performance`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (perfRes.ok) {
        const perfData = await perfRes.json();
        setPerformance(perfData);
        console.log('Performance data loaded');
      } else {
        console.warn('Failed to fetch performance:', perfRes.status);
      }

      // Fetch efficiency insights
      const insightRes = await fetch(`${API_URL}/analytics/doctor/insights`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (insightRes.ok) {
        const insightData = await insightRes.json();
        setInsights(insightData);
        console.log('Insights data loaded');
      } else {
        console.warn('Failed to fetch insights:', insightRes.status);
      }

      // Fetch utilization forecast
      const forecastRes = await fetch(`${API_URL}/analytics/doctor/utilization-forecast`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (forecastRes.ok) {
        const forecastData = await forecastRes.json();
        setUtilizationForecast(forecastData);
        console.log('Forecast data loaded');
      } else {
        console.warn('Failed to fetch forecast:', forecastRes.status);
      }

      // Fetch delay prediction
      const delayRes = await fetch(`${API_URL}/analytics/doctor/delay-prediction`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (delayRes.ok) {
        const delayData = await delayRes.json();
        setDelayPrediction(delayData);
        console.log('Delay prediction loaded');
      } else {
        console.warn('Failed to fetch delay prediction:', delayRes.status);
      }

      // Fetch queue optimization
      const optRes = await fetch(`${API_URL}/analytics/doctor/queue-optimization`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (optRes.ok) {
        const optData = await optRes.json();
        setQueueOptimization(optData);
        console.log('Queue optimization loaded');
      } else {
        console.warn('Failed to fetch queue optimization:', optRes.status);
      }

      // Fetch real-time slot reassignments
      const reassignRes = await fetch(`${API_URL}/analytics/doctor/slot-reassignments`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (reassignRes.ok) {
        const reassignData = await reassignRes.json();
        setSlotReassignments(reassignData);
        console.log('Slot reassignments loaded');
      } else {
        console.warn('Failed to fetch slot reassignments:', reassignRes.status);
      }

      // Fetch queue graph model
      const queueGraphRes = await fetch(`${API_URL}/analytics/doctor/queue-graph-model`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (queueGraphRes.ok) {
        const queueGraphData = await queueGraphRes.json();
        setQueueGraphModel(queueGraphData);
        console.log('Queue graph model loaded');
      } else {
        console.warn('Failed to fetch queue graph model:', queueGraphRes.status);
      }

      // Fetch pending reports
      const reportsRes = await fetch(`${API_URL}/reports/pending-reviews`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (reportsRes.ok) {
        const reportsData = await reportsRes.json();
        setPendingReports(reportsData);
        console.log('Reports data loaded');
      } else {
        console.warn('Failed to fetch reports:', reportsRes.status);
      }

      // Fetch all patient reports (reviewed and pending)
      const allReportsRes = await fetch(`${API_URL}/reports/doctor/all-patient-reports`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (allReportsRes.ok) {
        const allReportsData = await allReportsRes.json();
        setAllPatientReports(allReportsData);
        console.log('All patient reports loaded');
      } else {
        console.warn('Failed to fetch all patient reports:', allReportsRes.status);
      }

      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message || 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handleViewPatient = async (appointmentId) => {
    try {
      const res = await fetch(`${API_URL}/appointments/advanced/${appointmentId}/patient-details`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPatientDetails(data);
        setSelectedAppointment(appointmentId);
        setShowPatientModal(true);
      }
    } catch (err) {
      console.error('Error fetching patient details:', err);
    }
  };

  const handleCompleteAppointment = async (appointmentId, notes, diagnosis) => {
    try {
      const res = await fetch(`${API_URL}/appointments/advanced/${appointmentId}/complete`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          doctor_notes: notes,
          diagnosis: diagnosis
        })
      });

      if (res.ok) {
        alert('Appointment completed successfully');
        setShowCompleteModal(false);
        fetchAllData();
      }
    } catch (err) {
      console.error('Error completing appointment:', err);
      alert('Error completing appointment');
    }
  };

  const handleRescheduleAppointment = async (appointmentId, newTime, reason) => {
    try {
      const res = await fetch(`${API_URL}/appointments/advanced/${appointmentId}/reschedule`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          new_slot_time: newTime,
          reason: reason
        })
      });

      if (res.ok) {
        alert('Appointment rescheduled successfully');
        setShowRescheduleModal(false);
        fetchAllData();
      }
    } catch (err) {
      console.error('Error rescheduling appointment:', err);
      alert('Error rescheduling appointment');
    }
  };

  const handleReportAction = async (action) => {
    if (!selectedReport) return;

    try {
      const response = await fetch(`${API_URL}/reports/${selectedReport.report_id}/review`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status: action,
          review_notes: reportNotes,
          findings: reportNotes
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Report ${action} successfully!`);
        setShowReportActionModal(false);
        setSelectedReport(null);
        setReportNotes('');
        // Refresh reports list
        setActiveTab('reports');
        fetchAllData();
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Failed to ${action} report: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error(`Error ${action} report:`, err);
      alert(`Error ${action} report`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="doctor-dashboard">
        <div className="doctor-sidebar">
          <div className="doctor-logo">
            <span className="doctor-logo-icon">⚕️</span>
            <span className="doctor-logo-text">PulseSync</span>
          </div>
        </div>
        <div className="doctor-main">
          <div className="loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="doctor-dashboard">
      {/* Sidebar */}
      <div className="doctor-sidebar">
        <div className="doctor-logo">
          <span className="doctor-logo-icon">⚕️</span>
          <span className="doctor-logo-text">PulseSync AI</span>
        </div>

        <nav className="doctor-nav">
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Dashboard</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'queue' ? 'active' : ''}`}
            onClick={() => setActiveTab('queue')}
          >
            <span className="nav-icon">👥</span>
            <span className="nav-label">Today's Queue</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <span className="nav-icon">📈</span>
            <span className="nav-label">Analytics</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            <span className="nav-icon">📋</span>
            <span className="nav-label">Reports</span>
          </div>
          <div 
            className={`nav-item ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <span className="nav-icon">💡</span>
            <span className="nav-label">AI Insights</span>
          </div>
          <div 
            className={`nav-item logout`}
            onClick={handleLogout}
          >
            <span className="nav-icon">🚪</span>
            <span className="nav-label">Logout</span>
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="doctor-main">
        {error && <div className="error-banner">{error}</div>}

        {/* DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <div className="tab-content">
            <div className="header-section">
              <div>
                <h1 className="page-title">Welcome, Dr. {doctor?.name || 'Doctor'}</h1>
                <p className="page-subtitle">Specialization: {doctor?.specialization || 'N/A'}</p>
              </div>
            </div>

            {/* Key Metrics Grid - Enhanced */}
            <div className="metrics-grid-enhanced">
              {todayQueue && (
                <>
                  <div className="metric-card-large">
                    <div className="metric-background">👥</div>
                    <div className="metric-content-large">
                      <div className="metric-label">Patients Today</div>
                      <div className="metric-value">{todayQueue.queue_size || 0}</div>
                      <div className="metric-trend">On schedule</div>
                    </div>
                  </div>
                  <div className="metric-card-large">
                    <div className="metric-background">⏱️</div>
                    <div className="metric-content-large">
                      <div className="metric-label">Queue Time</div>
                      <div className="metric-value">{todayQueue.total_estimated_time || 0}m</div>
                      <div className="metric-trend">Average: {Math.round((todayQueue.total_estimated_time || 0) / (todayQueue.queue_size || 1))}m/patient</div>
                    </div>
                  </div>
                </>
              )}

              {performance && (
                <>
                  <div className="metric-card-large">
                    <div className="metric-background">✅</div>
                    <div className="metric-content-large">
                      <div className="metric-label">Completion Rate</div>
                      <div className="metric-value">{performance.metrics?.completion_rate_percent || 0}%</div>
                      <div className="metric-trend">This month</div>
                    </div>
                  </div>
                  <div className="metric-card-large">
                    <div className="metric-background">⭐</div>
                    <div className="metric-content-large">
                      <div className="metric-label">Quality Score</div>
                      <div className="metric-value">{performance.quality_score?.toFixed(1) || 0}/100</div>
                      <div className="metric-trend">
                        {performance.quality_score > 80 ? "Excellent performance" : performance.quality_score > 60 ? "Good performance" : "Needs improvement"}
                      </div>
                    </div>
                  </div>
                </>
              )}

              {delayPrediction && (
                <div className="metric-card-large">
                  <div className="metric-background">⚠️</div>
                  <div className="metric-content-large">
                    <div className="metric-label">Delay Risk</div>
                    <div className="metric-value">{(delayPrediction.delay_probability * 100).toFixed(0)}%</div>
                    <div className="metric-trend">{delayPrediction.delay_probability > 0.5 ? 'High risk' : 'Low risk'}</div>
                  </div>
                </div>
              )}
            </div>

            {/* Dataset Analytics Section */}
            {performance && (
              <div className="analytics-section-dashboard">
                <h2 className="section-title">📊 Dataset Analytics</h2>
                <div className="analytics-row">
                  <div className="analytics-card-dashboard">
                    <div className="analytics-header">
                      <span className="analytics-icon">📋</span>
                      <h3>Appointment Statistics</h3>
                    </div>
                    <div className="analytics-stats">
                      <div className="stat-item">
                        <span className="stat-label">Total Appointments</span>
                        <span className="stat-value">{performance.metrics?.total_appointments || 0}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Show Rate</span>
                        <span className="stat-value">{performance.metrics?.show_rate_percent || 0}%</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">No-Show Rate</span>
                        <span className="stat-value">{performance.metrics?.no_show_rate_percent || 0}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="analytics-card-dashboard">
                    <div className="analytics-header">
                      <span className="analytics-icon">⏱️</span>
                      <h3>Timing Insights</h3>
                    </div>
                    <div className="analytics-stats">
                      <div className="stat-item">
                        <span className="stat-label">Avg Consultation</span>
                        <span className="stat-value">{performance.timing_metrics?.avg_consultation_minutes || 0}m</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Avg Wait Time</span>
                        <span className="stat-value">{performance.timing_metrics?.avg_wait_time_minutes || 0}m</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Peak Hours Avg</span>
                        <span className="stat-value">9-11 AM</span>
                      </div>
                    </div>
                  </div>

                  <div className="analytics-card-dashboard">
                    <div className="analytics-header">
                      <span className="analytics-icon">⚡</span>
                      <h3>Efficiency Metrics</h3>
                    </div>
                    <div className="analytics-stats">
                      <div className="stat-item">
                        <span className="stat-label">Appts/Day</span>
                        <span className="stat-value">{performance.efficiency_metrics?.appointments_per_day || 0}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Utilization</span>
                        <span className="stat-value">{performance.efficiency_metrics?.utilization_percent || 0}%</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Working Days</span>
                        <span className="stat-value">{performance.efficiency_metrics?.working_days || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Next Patient Card - Redesigned */}
            {todayQueue?.next_patient && (
              <div className="next-patient-section">
                <h2 className="section-title">🎯 Next Patient</h2>
                <div className="next-patient-card-large">
                  <div className="patient-avatar">{todayQueue.next_patient.patient_name.charAt(0)}</div>
                  <div className="patient-details-grid">
                    <div className="patient-detail">
                      <span className="detail-label">Name</span>
                      <span className="detail-value">{todayQueue.next_patient.patient_name}</span>
                    </div>
                    <div className="patient-detail">
                      <span className="detail-label">Patient ID</span>
                      <span className="detail-value">{todayQueue.next_patient.ps_id}</span>
                    </div>
                    <div className="patient-detail">
                      <span className="detail-label">Severity</span>
                      <span className="detail-value detail-severity">{todayQueue.next_patient.severity.toFixed(1)}</span>
                    </div>
                    <div className="patient-detail">
                      <span className="detail-label">Est. Duration</span>
                      <span className="detail-value">{todayQueue.next_patient.predicted_duration} min</span>
                    </div>
                  </div>
                  <div className="patient-risk-indicator">
                    <span className="risk-label">No-Show Risk</span>
                    <span className={`risk-value risk-${todayQueue.next_patient.no_show_risk.toLowerCase()}`}>{todayQueue.next_patient.no_show_risk}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Interactive Dataset Tools */}
            <div className="dataset-actions-section">
              <h2 className="section-title">🔍 Dataset Tools</h2>
              <div className="dataset-actions-grid">
                <button className="dataset-action-btn" onClick={() => setShowQueueAnalyzerModal(true)}>
                  <span className="dataset-action-icon">📊</span>
                  <span className="dataset-action-title">Queue Analyzer</span>
                  <span className="dataset-action-desc">Analyze patient queue & optimize order</span>
                </button>
                <button className="dataset-action-btn" onClick={() => setShowPatientPredictorModal(true)}>
                  <span className="dataset-action-icon">🔮</span>
                  <span className="dataset-action-title">Patient Predictor</span>
                  <span className="dataset-action-desc">Predict patient risks & outcomes</span>
                </button>
                <button className="dataset-action-btn" onClick={() => setShowDatasetExplorerModal(true)}>
                  <span className="dataset-action-icon">🗂️</span>
                  <span className="dataset-action-title">Dataset Explorer</span>
                  <span className="dataset-action-desc">Explore dataset patterns & trends</span>
                </button>
              </div>
            </div>

            {!todayQueue && !performance && !delayPrediction && (
              <div className="loading-placeholder">
                <div className="loading-spinner"></div>
                <p>Loading dashboard data...</p>
              </div>
            )}
          </div>
        )}

        {/* QUEUE TAB */}
        {activeTab === 'queue' && (
          <div className="tab-content">
            <h1>Today's Queue</h1>
            {todayQueue ? (
              <>
                <p className="subtitle">{todayQueue.date} | {todayQueue.queue_size} patients</p>
                <div className="queue-list">
                  {todayQueue.appointments && todayQueue.appointments.map((appt, idx) => (
                    <div key={idx} className="queue-item">
                      <div className="queue-position">#{appt.position}</div>
                      <div className="queue-details">
                        <div className="patient-name">{appt.patient_name}</div>
                        <div className="patient-meta">
                          <span>ID: {appt.ps_id}</span>
                          <span>Severity: {appt.severity.toFixed(1)}</span>
                          <span>Duration: {appt.predicted_duration}m</span>
                          <span>Risk: {appt.no_show_risk}</span>
                        </div>
                      </div>
                      <button 
                        className="btn-view-patient"
                        onClick={() => handleViewPatient(appt.appointment_id)}
                      >
                        View Patient
                      </button>
                      <button 
                        className="btn-complete"
                        onClick={() => {
                          setSelectedAppointment(appt.appointment_id);
                          setShowCompleteModal(true);
                        }}
                      >
                        Complete
                      </button>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="loading">Loading queue data...</div>
            )}
          </div>
        )}

        {/* ANALYTICS TAB */}
        {activeTab === 'analytics' && (
          <div className="tab-content">
            <h1>Analytics Dashboard</h1>
            <p className="subtitle">30-Day Performance Metrics</p>

            {performance ? (
              <div className="analytics-section">
                {/* Performance Summary Chart */}
                <PerformanceSummaryChart performanceData={performance} />

                {/* Timing Metrics Chart */}
                <TimingMetricsChart performanceData={performance} />

                {/* Efficiency Metrics Chart */}
                <EfficiencyMetricsChart performanceData={performance} />

                {/* Quality Score Chart */}
                <QualityScoreChart performanceData={performance} />

                {/* 7-Day Utilization Forecast Chart */}
                {utilizationForecast && utilizationForecast.forecast && (
                  <UtilizationForecastChart forecastData={utilizationForecast} />
                )}

                {/* Smart Queue Insights */}
                <div className="analytics-section">
                  <h2>🧠 Smart Queue Insights</h2>
                  <div className="smart-queue-grid">
                    <div className="smart-queue-card">
                      <div className="queue-insight-icon">📊</div>
                      <h4>Queue Optimization</h4>
                      <p>Current queue efficiency is at <strong>{performance.efficiency_metrics?.utilization_percent || 0}%</strong>. 
                      {queueOptimization?.recommendation ? queueOptimization.recommendation : "Reorder based on urgency and availability for optimal scheduling."}</p>
                    </div>
                    <div className="smart-queue-card">
                      <div className="queue-insight-icon">⚠️</div>
                      <h4>Risk Management</h4>
                      <p>No-show Risk: <strong>{(delayPrediction?.delay_probability * 100).toFixed(0)}%</strong>. 
                      {delayPrediction?.delay_probability > 0.5 
                        ? "Monitor high-risk appointments closely and send reminders." 
                        : "Risk is low. Maintain current communication strategy."}</p>
                    </div>
                    <div className="smart-queue-card">
                      <div className="queue-insight-icon">⚡</div>
                      <h4>Time Optimization</h4>
                      <p>Average consultation: <strong>{performance.timing_metrics?.avg_consultation_minutes || 0}m</strong>. 
                      Avg wait time: <strong>{performance.timing_metrics?.avg_wait_time_minutes || 0}m</strong>. 
                      Optimize scheduling for better efficiency.</p>
                    </div>
                    <div className="smart-queue-card">
                      <div className="queue-insight-icon">📈</div>
                      <h4>Performance Trend</h4>
                      <p>Quality Score: <strong>{performance.quality_score?.toFixed(1) || 0}/100</strong>. 
                      {performance.quality_score > 80 ? "Excellent! Maintain current standards." : "Focus on improving patient satisfaction scores."}</p>
                    </div>
                  </div>
                </div>

                {/* Real-time Slot Reassignments */}
                {slotReassignments && (
                  <div className="analytics-section">
                    <h2>🔄 Real-Time Slot Reassignments</h2>
                    <div className="reassignment-info">
                      <p className="reassignment-message">{slotReassignments.message}</p>
                    </div>
                    {slotReassignments.reassignments && slotReassignments.reassignments.length > 0 ? (
                      <div className="reassignment-grid">
                        {slotReassignments.reassignments.map((reassignment, idx) => (
                          <div key={idx} className="reassignment-card">
                            <div className="reassignment-header">
                              <span className="reassignment-label">Patient {reassignment.patient_id}</span>
                              <span className="reassignment-confidence">{(reassignment.confidence * 100).toFixed(0)}% Confidence</span>
                            </div>
                            <div className="reassignment-details">
                              <p><strong>Current Slot:</strong> {reassignment.current_slot ? new Date(reassignment.current_slot).toLocaleString() : 'Not set'}</p>
                              <p><strong>Recommendation:</strong> {reassignment.recommendation}</p>
                              <p><strong>Suggested Time:</strong> {reassignment.suggested_time || 'No change needed'}</p>
                              <p><strong>Reason:</strong> {reassignment.reason}</p>
                              <p><strong>Priority Impact:</strong> <span className={reassignment.priority_change > 0 ? 'increase' : 'decrease'}>{reassignment.priority_change > 0 ? '↑' : '↓'} {Math.abs(reassignment.priority_change)}</span></p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-reassignments">
                        <p>✓ All slot assignments are optimal</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Graph-Based Queue Modeling */}
                {queueGraphModel && (
                  <div className="analytics-section">
                    <h2>🕸️ Graph-Based Queue Modeling</h2>
                    <div className="queue-model-info">
                      <div className="queue-metric">
                        <span className="metric-label">Queue Size:</span>
                        <span className="metric-value">{queueGraphModel.queue_size} patients</span>
                      </div>
                      <div className="queue-metric">
                        <span className="metric-label">Avg Priority Level:</span>
                        <span className="metric-value">{queueGraphModel.metrics?.average_priority?.toFixed(1) || '0'}</span>
                      </div>
                      <div className="queue-metric">
                        <span className="metric-label">Est. Total Wait Time:</span>
                        <span className="metric-value">{(queueGraphModel.metrics?.estimated_total_wait || 0).toFixed(0)} mins</span>
                      </div>
                    </div>

                    {/* Critical Path Analysis */}
                    <div className="critical-path-section">
                      <h3>Critical Path Analysis</h3>
                      {queueGraphModel.critical_path?.high_priority_patients && queueGraphModel.critical_path.high_priority_patients.length > 0 ? (
                        <div className="critical-patients">
                          {queueGraphModel.critical_path.high_priority_patients.map((patient, idx) => (
                            <div key={idx} className="critical-patient-card">
                              <span className="critical-rank">#{idx + 1}</span>
                              <span className="critical-id">Patient {patient.patient_id}</span>
                              <span className="critical-priority">Priority: {patient.priority}</span>
                              <span className="critical-est-time">{patient.estimated_time_in_queue}m</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p>No critical priority patients currently in queue</p>
                      )}
                      <p className="discharge-estimate">
                        <strong>Est. Discharge Time for Top 3:</strong> {queueGraphModel.critical_path?.estimated_discharge_time?.toFixed(0) || '0'} minutes
                      </p>
                    </div>

                    {/* Bottleneck Identification */}
                    {queueGraphModel.bottlenecks && queueGraphModel.bottlenecks.length > 0 && (
                      <div className="bottleneck-section">
                        <h3>⚠️ Queue Bottlenecks</h3>
                        <div className="bottleneck-list">
                          {queueGraphModel.bottlenecks.map((bottleneck, idx) => (
                            <div key={idx} className="bottleneck-item">
                              <span className="bottleneck-position">Position {bottleneck.position + 1}</span>
                              <span className="bottleneck-patient">Patient {bottleneck.patient_id}</span>
                              <span className="bottleneck-reason">{bottleneck.reason}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Graph Visualization Info */}
                    <div className="graph-info">
                      <p><strong>Nodes:</strong> {queueGraphModel.graph?.nodes?.length || 0} patients</p>
                      <p><strong>Connections:</strong> {queueGraphModel.graph?.edges?.length || 0} sequential relationships</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="loading">Loading analytics...</div>
            )}
          </div>
        )}

        {/* REPORTS TAB */}
        {activeTab === 'reports' && (
          <div className="tab-content">
            <div className="header-section">
              <h1 className="page-title">Patient Medical Reports</h1>
              <p className="page-subtitle">Review and manage patient medical records</p>
            </div>

            {/* View Type Tabs */}
            <div style={{display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid rgba(100, 116, 139, 0.3)', paddingBottom: '1rem'}}>
              <button 
                onClick={() => setReportViewType('pending')}
                style={{
                  background: reportViewType === 'pending' ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
                  color: reportViewType === 'pending' ? '#22c55e' : '#94a3b8',
                  border: reportViewType === 'pending' ? '2px solid #22c55e' : '1px solid rgba(100, 116, 139, 0.3)',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
              >
                ⏳ Pending Review ({pendingReports?.pending_count || 0})
              </button>
              <button 
                onClick={() => setReportViewType('all')}
                style={{
                  background: reportViewType === 'all' ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
                  color: reportViewType === 'all' ? '#22c55e' : '#94a3b8',
                  border: reportViewType === 'all' ? '2px solid #22c55e' : '1px solid rgba(100, 116, 139, 0.3)',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  fontWeight: '600',
                  transition: 'all 0.2s'
                }}
              >
                📋 All Reports ({allPatientReports?.total_reports || 0})
              </button>
            </div>

            {reportViewType === 'pending' && pendingReports ? (
              <>
                <div className="pending-summary">
                  <div className="pending-badge">
                    <span className="badge-number">{pendingReports.pending_count || 0}</span>
                    <span className="badge-text">Reports Awaiting Review</span>
                  </div>
                </div>

                {/* Report Filter Tabs */}
                <div className="report-filter-tabs">
                  <button 
                    className={`filter-tab ${reportFilterType === 'all' ? 'active' : ''}`}
                    onClick={() => setReportFilterType('all')}
                  >
                    📋 All Reports
                  </button>
                  <button 
                    className={`filter-tab ${reportFilterType === 'patient' ? 'active' : ''}`}
                    onClick={() => setReportFilterType('patient')}
                  >
                    👤 Patient Uploaded
                  </button>
                </div>

                <div className="reports-container">
                  {pendingReports.reports && Array.isArray(pendingReports.reports) && pendingReports.reports.length > 0 ? (
                    (() => {
                      const filteredReports = pendingReports.reports.filter(report => {
                        if (reportFilterType === 'patient') {
                          return report.is_patient_upload === true;
                        }
                        return true;
                      });

                      return filteredReports.length > 0 ? (
                        filteredReports.map((report) => (
                          <div key={report.report_id} className={`report-card-improved ${report.is_patient_upload ? 'patient-upload' : ''}`}>
                            <div className="report-header-improved">
                              <div className="report-title-group">
                                <h3 className="report-patient-name">{report.patient_name || "Unknown Patient"}</h3>
                                <div className="report-badges-group">
                                  <span className="report-type-badge">{report.report_type || 'General'}</span>
                                  {report.is_patient_upload && (
                                    <span className="report-source-badge">👤 Patient Uploaded</span>
                                  )}
                                </div>
                              </div>
                              <span className="report-id">ID: {report.report_id}</span>
                            </div>
                            <p className="report-description-text">{report.description || report.diagnosis || 'No description available'}</p>
                            <div className="report-uploader-info">
                              <small>Uploaded by: <strong>{report.uploaded_by}</strong></small>
                            </div>
                            <div className="report-actions-improved">
                              <button className="btn-action-approve" title="Approve Report" onClick={() => {
                                setSelectedReport(report);
                                setReportAction('approved');
                                setReportNotes('');
                                setShowReportActionModal(true);
                              }}>
                                <span className="action-icon">✓</span>
                                <span className="action-text">Approve</span>
                              </button>
                              <button className="btn-action-review" title="Review Report" onClick={() => {
                                setSelectedReport(report);
                                setReportAction('reviewed');
                                setReportNotes('');
                                setShowReportActionModal(true);
                              }}>
                                <span className="action-icon">👁</span>
                                <span className="action-text">Review</span>
                              </button>
                              <button className="btn-action-flag" title="Flag Report" onClick={() => {
                                setSelectedReport(report);
                                setReportAction('flagged');
                                setReportNotes('');
                                setShowReportActionModal(true);
                              }}>
                                <span className="action-icon">⚠</span>
                                <span className="action-text">Flag</span>
                              </button>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="empty-state-improved">
                          <div className="empty-icon">📭</div>
                          <p className="empty-text">
                            {reportFilterType === 'patient' ? 'No patient-uploaded reports' : 'No pending reports'}
                          </p>
                          <p className="empty-subtext">
                            {reportFilterType === 'patient' ? 'All reports uploaded by patients have been reviewed' : 'All reports have been reviewed'}
                          </p>
                        </div>
                      );
                    })()
                  ) : null}
                </div>
              </>
            ) : reportViewType === 'all' && allPatientReports ? (
              <div className="reports-container">
                {allPatientReports.reports && Array.isArray(allPatientReports.reports) && allPatientReports.reports.length > 0 ? (
                  allPatientReports.reports.map((report) => (
                    <div key={report.report_id} 
                      className="report-card-improved"
                      style={{
                        borderLeft: report.status === 'approved' ? '4px solid #22c55e' : report.status === 'pending' ? '4px solid #f59e0b' : report.status === 'flagged' ? '4px solid #ef4444' : '4px solid #6b7280'
                      }}
                    >
                      <div className="report-header-improved">
                        <div className="report-title-group">
                          <h3 className="report-patient-name">{report.patient_name || "Unknown Patient"}</h3>
                          <div className="report-badges-group">
                            <span className="report-type-badge">{report.report_type || 'General'}</span>
                            <span 
                              className="report-status-badge"
                              style={{
                                background: report.status === 'approved' ? 'rgba(34, 197, 94, 0.2)' : report.status === 'pending' ? 'rgba(245, 158, 11, 0.2)' : report.status === 'flagged' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(107, 114, 128, 0.2)',
                                color: report.status === 'approved' ? '#22c55e' : report.status === 'pending' ? '#f59e0b' : report.status === 'flagged' ? '#ef4444' : '#9ca3af'
                              }}
                            >
                              {report.status?.toUpperCase() || 'PENDING'}
                            </span>
                          </div>
                        </div>
                        <span className="report-id">ID: {report.report_id}</span>
                      </div>

                      <p className="report-description-text">{report.description || 'No description'}</p>
                      
                      <div style={{marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(100, 116, 139, 0.2)', fontSize: '0.85rem', color: '#94a3b8'}}>
                        <div style={{marginBottom: '0.5rem'}}>
                          <strong>👤 Uploaded by:</strong> {report.uploaded_by}
                          <span style={{float: 'right', color: '#64748b'}}>
                            📅 {new Date(report.created_at).toLocaleDateString()}
                          </span>
                        </div>

                        {report.reviewed_by && (
                          <div style={{marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(34, 197, 94, 0.08)', borderLeft: '2px solid #22c55e', borderRadius: '0.25rem'}}>
                            <div style={{color: '#22c55e', fontWeight: '600', marginBottom: '0.5rem'}}>
                              👨‍⚕️ Reviewed by: {report.reviewed_by}
                            </div>
                            {report.reviewed_at && (
                              <div style={{color: '#86efac', fontSize: '0.8rem', marginBottom: '0.5rem'}}>
                                📅 {new Date(report.reviewed_at).toLocaleDateString()}
                              </div>
                            )}
                            {report.review_notes && (
                              <div style={{color: '#cbd5e1', marginTop: '0.5rem', fontStyle: 'italic'}}>
                                📝 <strong>Notes:</strong> {report.review_notes}
                              </div>
                            )}
                            {report.findings && (
                              <div style={{color: '#cbd5e1', marginTop: '0.5rem'}}>
                                🔍 <strong>Findings:</strong> {report.findings}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {report.status === 'pending' && (
                        <div className="report-actions-improved">
                          <button className="btn-action-approve" onClick={() => {
                            setSelectedReport(report);
                            setReportAction('approved');
                            setReportNotes('');
                            setShowReportActionModal(true);
                          }}>
                            <span className="action-icon">✓</span>
                            <span className="action-text">Approve</span>
                          </button>
                          <button className="btn-action-review" onClick={() => {
                            setSelectedReport(report);
                            setReportAction('reviewed');
                            setReportNotes('');
                            setShowReportActionModal(true);
                          }}>
                            <span className="action-icon">👁</span>
                            <span className="action-text">Review</span>
                          </button>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="empty-state-improved">
                    <div className="empty-icon">📭</div>
                    <p className="empty-text">No reports found</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="loading-placeholder">
                <div className="loading-spinner"></div>
                <p>Loading reports...</p>
              </div>
            )}
          </div>
        )}

        {/* AI INSIGHTS TAB */}
        {activeTab === 'insights' && (
          <div className="tab-content">
            <h1>AI-Powered Insights</h1>
            {insights ? (
              <>
                <p className="insight-subtitle">Health Status: <span className={`status-${typeof insights.overall_health === 'string' ? insights.overall_health.toLowerCase() : 'unknown'}`}>{typeof insights.overall_health === 'string' ? insights.overall_health : 'Unknown'}</span></p>

                {/* Insights */}
                <div className="insights-section">
                  <h2>Key Insights</h2>
                  {insights.insights && insights.insights.length > 0 ? (
                    insights.insights.map((insight, idx) => (
                      <InsightCard 
                        key={idx} 
                        insight={insight}
                        recommendation={insights.recommendations && insights.recommendations[idx] ? insights.recommendations[idx] : null}
                      />
                    ))
                  ) : (
                    <NoDataPlaceholder message="No insights available at this time" />
                  )}
                </div>

                {/* Recommendations */}
                {insights.recommendations && insights.recommendations.length > 0 && (
                  <div className="recommendations-section">
                    <h2>Recommendations</h2>
                    {insights.recommendations.map((rec, idx) => (
                      <div key={idx} className="recommendation-item">
                        <span className="rec-icon">→</span>
                        <span className="rec-text">{rec}</span>
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="loading">Loading insights...</div>
            )}
          </div>
        )}
      </div>

      {/* Patient Detail Modal */}
      {showPatientModal && patientDetails && (
        <div className="modal-overlay" onClick={() => setShowPatientModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Patient Details</h2>
              <button className="modal-close" onClick={() => setShowPatientModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="patient-section">
                <h3>Personal Information</h3>
                <table className="info-table">
                  <tbody>
                    <tr><td>Name:</td><td>{patientDetails.patient_name}</td></tr>
                    <tr><td>ID:</td><td>{patientDetails.ps_id}</td></tr>
                    <tr><td>Age:</td><td>{patientDetails.age}</td></tr>
                    <tr><td>Email:</td><td>{patientDetails.patient_email}</td></tr>
                    <tr><td>Phone:</td><td>{patientDetails.patient_phone}</td></tr>
                  </tbody>
                </table>
              </div>

              <div className="patient-section">
                <h3>Medical History</h3>
                <table className="info-table">
                  <tbody>
                    <tr><td>Conditions:</td><td>{patientDetails.medical_conditions || 'None'}</td></tr>
                    <tr><td>Medications:</td><td>{patientDetails.medications || 'None'}</td></tr>
                    <tr><td>Allergies:</td><td>{patientDetails.allergies || 'None'}</td></tr>
                    <tr><td>Severity Score:</td><td>{patientDetails.severity_score.toFixed(1)}</td></tr>
                  </tbody>
                </table>
              </div>

              <div className="patient-section">
                <h3>Appointment History</h3>
                <div className="history-stats">
                  <div className="stat">Previous Visits: {patientDetails.previous_appointments_with_doctor}</div>
                  <div className="stat">Total Appointments: {patientDetails.total_appointments_system}</div>
                  <div className="stat">No-Shows: {patientDetails.no_show_count}</div>
                  <div className="stat">Late Arrivals: {patientDetails.late_arrival_count}</div>
                </div>
              </div>

              {patientDetails.previous_visits.length > 0 && (
                <div className="patient-section">
                  <h3>Recent Visits</h3>
                  <div className="visits-list">
                    {patientDetails.previous_visits.map((visit, idx) => (
                      <div key={idx} className="visit-item">
                        <div className="visit-date">{new Date(visit.date).toLocaleDateString()}</div>
                        <div className="visit-diagnosis">{visit.diagnosis || 'No diagnosis recorded'}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Complete Appointment Modal */}
      {showCompleteModal && (
        <div className="modal-overlay" onClick={() => setShowCompleteModal(false)}>
          <div className="modal-content-improved" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-improved">
              <div>
                <h2 className="modal-title">Complete Appointment</h2>
                <p className="modal-subtitle">finalize your notes and diagnosis</p>
              </div>
              <button className="modal-close-btn" onClick={() => setShowCompleteModal(false)}>✕</button>
            </div>
            <div className="modal-body-improved">
              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const notes = formData.get('notes')?.trim();
                const diagnosis = formData.get('diagnosis')?.trim();
                
                if (!notes) {
                  alert('Please enter doctor notes');
                  return;
                }
                
                handleCompleteAppointment(selectedAppointment, notes, diagnosis);
              }}>
                <div className="form-group-improved">
                  <label className="form-label">Doctor Notes *</label>
                  <textarea 
                    name="notes" 
                    required 
                    placeholder="Enter your clinical observations and findings..."
                    className="form-input-textarea"
                  ></textarea>
                </div>
                <div className="form-group-improved">
                  <label className="form-label">Diagnosis</label>
                  <textarea 
                    name="diagnosis" 
                    placeholder="Enter diagnosis and treatment plan..."
                    className="form-input-textarea"
                  ></textarea>
                </div>
                <div className="modal-actions-improved">
                  <button type="button" className="btn-action-cancel" onClick={() => setShowCompleteModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-action-submit">
                    <span>✓</span>
                    Complete Appointment
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Queue Analyzer Modal */}
      {showQueueAnalyzerModal && (
        <div className="modal-overlay" onClick={() => setShowQueueAnalyzerModal(false)}>
          <div className="dataset-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header-dataset">
              <h3>📊 Queue Analyzer</h3>
              <button className="modal-close-btn" onClick={() => setShowQueueAnalyzerModal(false)}>×</button>
            </div>
            <div className="modal-content-dataset">
              <div className="dataset-insight">
                <span className="insight-icon">👥</span>
                <div className="insight-content">
                  <div className="insight-title">Current Queue Status</div>
                  <div className="insight-text">
                    You have <strong>{todayQueue?.queue_size || 0}</strong> patients in queue. 
                    Average consultation time is <strong>{performance?.timing_metrics?.avg_consultation_minutes || 0} minutes</strong>.
                  </div>
                </div>
              </div>

              <div className="dataset-insight">
                <span className="insight-icon">⏱️</span>
                <div className="insight-content">
                  <div className="insight-title">Estimated Wait Times</div>
                  <div className="insight-text">
                    Total queue time: <strong>{todayQueue?.total_estimated_time || 0} minutes</strong>. 
                    Average per patient: <strong>{Math.round((todayQueue?.total_estimated_time || 0) / (todayQueue?.queue_size || 1))} minutes</strong>.
                  </div>
                </div>
              </div>

              {queueOptimization && (
                <div className="dataset-insight">
                  <span className="insight-icon">🎯</span>
                  <div className="insight-content">
                    <div className="insight-title">Queue Optimization Suggestion</div>
                    <div className="insight-text">
                      {queueOptimization.recommendation || "Consider reordering queue based on urgency and severity scores."}
                    </div>
                  </div>
                </div>
              )}

              <div className="dataset-stats-modal">
                <div className="stat-box-modal">
                  <div className="stat-box-modal-label">Show Rate</div>
                  <div className="stat-box-modal-value">{performance?.metrics?.show_rate_percent || 0}%</div>
                </div>
                <div className="stat-box-modal">
                  <div className="stat-box-modal-label">No-Show Risk</div>
                  <div className="stat-box-modal-value">{(delayPrediction?.delay_probability * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Patient Predictor Modal */}
      {showPatientPredictorModal && (
        <div className="modal-overlay" onClick={() => setShowPatientPredictorModal(false)}>
          <div className="dataset-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header-dataset">
              <h3>🔮 Patient Predictor</h3>
              <button className="modal-close-btn" onClick={() => setShowPatientPredictorModal(false)}>×</button>
            </div>
            <div className="modal-content-dataset">
              <div className="dataset-insight">
                <span className="insight-icon">⚠️</span>
                <div className="insight-content">
                  <div className="insight-title">No-Show Risk Analysis</div>
                  <div className="insight-text">
                    Current no-show probability: <strong>{(delayPrediction?.delay_probability * 100).toFixed(1)}%</strong>. 
                    {delayPrediction?.delay_probability > 0.5 
                      ? "High risk detected - consider confirming appointments." 
                      : "Risk is low - most patients will show up."}
                  </div>
                </div>
              </div>

              <div className="dataset-insight">
                <span className="insight-icon">⏰</span>
                <div className="insight-content">
                  <div className="insight-title">Appointment Duration Prediction</div>
                  <div className="insight-text">
                    Based on ML models, average consultation time is <strong>{performance?.timing_metrics?.avg_consultation_minutes || 0} minutes</strong> 
                    with average wait time of <strong>{performance?.timing_metrics?.avg_wait_time_minutes || 0} minutes</strong>.
                  </div>
                </div>
              </div>

              <div className="dataset-insight">
                <span className="insight-icon">📊</span>
                <div className="insight-content">
                  <div className="insight-title">Patient Completion Rate</div>
                  <div className="insight-text">
                    Your efficiency score: <strong>{performance?.quality_score?.toFixed(1) || 0}/100</strong>. 
                    {performance?.quality_score > 80 ? "Excellent performance - maintaining high standards." : "Keep improving - focus on patient satisfaction."}
                  </div>
                </div>
              </div>

              <div className="dataset-stats-modal">
                <div className="stat-box-modal">
                  <div className="stat-box-modal-label">Completion Rate</div>
                  <div className="stat-box-modal-value">{performance?.metrics?.completion_rate_percent || 0}%</div>
                </div>
                <div className="stat-box-modal">
                  <div className="stat-box-modal-label">Quality Score</div>
                  <div className="stat-box-modal-value">{performance?.quality_score?.toFixed(0) || 0}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Dataset Explorer Modal */}
      {showDatasetExplorerModal && (
        <div className="modal-overlay" onClick={() => setShowDatasetExplorerModal(false)}>
          <div className="dataset-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header-dataset">
              <h3>🗂️ Dataset Explorer</h3>
              <button className="modal-close-btn" onClick={() => setShowDatasetExplorerModal(false)}>×</button>
            </div>
            <div className="modal-content-dataset">
              <div className="dataset-insight">
                <span className="insight-icon">📈</span>
                <div className="insight-content">
                  <div className="insight-title">Your Performance Metrics</div>
                  <div className="insight-text">
                    Total appointments: <strong>{performance?.metrics?.total_appointments || 0}</strong>. 
                    Show rate: <strong>{performance?.metrics?.show_rate_percent || 0}%</strong>. 
                    No-show rate: <strong>{performance?.metrics?.no_show_rate_percent || 0}%</strong>.
                  </div>
                </div>
              </div>

              <div className="dataset-insight">
                <span className="insight-icon">⚡</span>
                <div className="insight-content">
                  <div className="insight-title">Efficiency Overview</div>
                  <div className="insight-text">
                    Appointments per day: <strong>{performance?.efficiency_metrics?.appointments_per_day || 0}</strong>. 
                    Utilization rate: <strong>{performance?.efficiency_metrics?.utilization_percent || 0}%</strong>. 
                    Active days: <strong>{performance?.efficiency_metrics?.working_days || 0}</strong>.
                  </div>
                </div>
              </div>

              <div className="dataset-insight">
                <span className="insight-icon">💡</span>
                <div className="insight-content">
                  <div className="insight-title">Key Insights</div>
                  <div className="insight-text">
                    {insights?.insights?.length > 0
                      ? insights.insights[0].insight
                      : "Maintain consistent patient care standards and monitor queue times for optimal efficiency."}
                  </div>
                </div>
              </div>

              <div className="dataset-stats-modal">
                <div className="stat-box-modal">
                  <div className="stat-box-modal-label">Working Days</div>
                  <div className="stat-box-modal-value">{performance?.efficiency_metrics?.working_days || 0}</div>
                </div>
                <div className="stat-box-modal">
                  <div className="stat-box-modal-label">Utilization %</div>
                  <div className="stat-box-modal-value">{performance?.efficiency_metrics?.utilization_percent || 0}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Report Action Modal */}
      {showReportActionModal && selectedReport && (
        <div className="modal-overlay" onClick={() => setShowReportActionModal(false)}>
          <div className="modal-container" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Review Report</h2>
              <button className="modal-close-btn" onClick={() => setShowReportActionModal(false)}>✕</button>
            </div>
            <div className="modal-content">
              <div className="form-group-improved">
                <label className="form-label">Report Details</label>
                <div className="report-summary-modal">
                  <p><strong>Patient:</strong> {selectedReport.patient_name}</p>
                  <p><strong>Report ID:</strong> {selectedReport.report_id}</p>
                  <p><strong>Type:</strong> {selectedReport.report_type || 'General'}</p>
                  <p><strong>Description:</strong> {selectedReport.description || selectedReport.diagnosis || 'N/A'}</p>
                </div>
              </div>
              
              <div className="form-group-improved">
                <label className="form-label">Review Notes (Optional)</label>
                <textarea 
                  placeholder="Enter your review notes, findings, or concerns..."
                  className="form-input-textarea"
                  value={reportNotes}
                  onChange={(e) => setReportNotes(e.target.value)}
                  rows="4"
                ></textarea>
              </div>

              <div className="modal-footer">
                <button 
                  className="btn-cancel"
                  onClick={() => setShowReportActionModal(false)}
                >
                  Cancel
                </button>
                <button 
                  className="btn-submit"
                  onClick={() => handleReportAction(reportAction)}
                >
                  {reportAction === 'approved' ? '✓ Approve' : reportAction === 'reviewed' ? '👁 Mark as Reviewed' : '⚠ Flag Report'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;
