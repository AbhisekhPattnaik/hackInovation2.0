import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PatientDashboard.css';

const PatientDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [patient, setPatient] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showSymptomsModal, setShowSymptomsModal] = useState(false);
  const [showQueueInsightsModal, setShowQueueInsightsModal] = useState(false);
  const [showHealthActionModal, setShowHealthActionModal] = useState(false);
  const [healthActionType, setHealthActionType] = useState(null);
  const [symptomsInput, setSymptomsInput] = useState('');
  const [doctors, setDoctors] = useState([]);
  const [appointmentForm, setAppointmentForm] = useState({
    doctor: '',
    date: '',
    time: '',
    reason: ''
  });
  const token = localStorage.getItem('token');
  const API_URL = 'http://127.0.0.1:8000';

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch patient info
        const patientRes = await fetch(`${API_URL}/users/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!patientRes.ok) {
          throw new Error('Failed to fetch patient info');
        }

        const patientData = await patientRes.json();
        setPatient(patientData);

        // Fetch health status with AI data
        const healthRes = await fetch(`${API_URL}/health/health-status`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (healthRes.ok) {
          const healthData = await healthRes.json();
          setHealthStatus(healthData);
        }

        // Fetch AI recommendations
        const recsRes = await fetch(`${API_URL}/health/recommendations`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (recsRes.ok) {
          const recsData = await recsRes.json();
          setRecommendations(recsData);
        }

        // Fetch appointments
        const appointmentsRes = await fetch(`${API_URL}/appointments/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (appointmentsRes.ok) {
          const appointmentsData = await appointmentsRes.json();
          setAppointments(appointmentsData);
        }

        // Fetch medical records
        try {
          const reportsRes = await fetch(`${API_URL}/reports/my-reports`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (reportsRes.ok) {
            const reportsData = await reportsRes.json();
            setMedicalRecords(reportsData);
          }
        } catch (err) {
          console.log('Note: Could not fetch medical records', err);
        }

        // Fetch prescriptions
        try {
          const prescRes = await fetch(`${API_URL}/prescriptions/my-prescriptions`, {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });

          if (prescRes.ok) {
            const prescData = await prescRes.json();
            setPrescriptions(prescData);
          }
        } catch (err) {
          console.log('Note: Could not fetch prescriptions', err);
        }

        // Fetch available doctors
        try {
          const doctorsRes = await fetch(`${API_URL}/users/doctors`);
          if (doctorsRes.ok) {
            const doctorsData = await doctorsRes.json();
            setDoctors(doctorsData);
          }
        } catch (err) {
          console.log('Note: Could not fetch doctors list', err);
        }

        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, navigate]);

  const handleUpdateSymptoms = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/health/update-symptoms`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symptoms: symptomsInput
        })
      });

      if (response.ok) {
        alert('Symptoms updated! AI recommendations refreshed.');
        setSymptomsInput('');
        setShowSymptomsModal(false);
        window.location.reload();
      } else {
        alert('Failed to update symptoms');
      }
    } catch (err) {
      console.error('Error updating symptoms:', err);
      alert('Error updating symptoms');
    }
  };

  const handleScheduleAppointment = async (e) => {
    e.preventDefault();
    try {
      // Validate doctor selection
      if (!appointmentForm.doctor) {
        alert('Please select a doctor');
        return;
      }

      // The appointment reason becomes the symptoms for AI processing
      const symptomsArray = appointmentForm.reason
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
      
      const response = await fetch(`${API_URL}/appointments/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          doctor_id: parseInt(appointmentForm.doctor),
          appointment_date: appointmentForm.date,
          appointment_time: appointmentForm.time,
          symptoms: symptomsArray.length > 0 ? symptomsArray : ["General checkup"]
        })
      });

      if (response.ok) {
        alert('Appointment scheduled successfully!');
        setShowScheduleModal(false);
        setAppointmentForm({ doctor: '', date: '', time: '', reason: '' });
        // Refresh appointments
        window.location.reload();
      } else {
        alert('Failed to schedule appointment');
      }
    } catch (err) {
      console.error('Error scheduling appointment:', err);
      alert('Error scheduling appointment');
    }
  };

  const handleReportUpload = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('reportFile');
    if (!fileInput.files[0]) {
      alert('Please select a file');
      return;
    }

    if (!patient || !patient.patient_id) {
      alert('Patient information not loaded');
      return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('user_id', patient.id); // User ID from authentication
    formData.append('diagnosis', ''); // Optional field

    try {
      const response = await fetch(`${API_URL}/reports/upload/${patient.patient_id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        alert('Report uploaded successfully!');
        setShowReportModal(false);
        fileInput.value = ''; // Clear file input
        // Refresh medical records
        await refreshMedicalRecords();
      } else {
        const errorData = await response.json().catch(() => ({}));
        alert(`Failed to upload report: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error uploading report:', err);
      alert('Error uploading report');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
  };

  const refreshMedicalRecords = async () => {
    try {
      const reportsRes = await fetch(`${API_URL}/reports/my-reports`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (reportsRes.ok) {
        const reportsData = await reportsRes.json();
        setMedicalRecords(reportsData);
      }
    } catch (err) {
      console.log('Error refreshing medical records:', err);
    }
  };

  const handleHealthAction = (actionType) => {
    setHealthActionType(actionType);
    setShowHealthActionModal(true);
  };

  const executeHealthAction = () => {
    switch(healthActionType) {
      case 'emergency':
        setShowScheduleModal(true);
        setShowHealthActionModal(false);
        break;
      case 'track':
        alert('Tracking functionality coming soon. For now, navigate to Medical Records to view your health history.');
        setShowHealthActionModal(false);
        break;
      case 'schedule':
        setShowScheduleModal(true);
        setShowHealthActionModal(false);
        break;
      default:
        setShowHealthActionModal(false);
    }
  };

  if (loading) {
    return (
      <div className="patient-dashboard">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="patient-dashboard">
      {/* Sidebar */}
      <div className="patient-sidebar">
        <div className="patient-logo">
          <span className="patient-logo-icon">🏥</span>
          <span className="patient-logo-text">PulseSync</span>
        </div>

        <nav className="patient-nav">
          <div 
            className={`patient-nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="patient-nav-icon">📊</span>
            <span className="patient-nav-label">Dashboard</span>
          </div>
          <div 
            className={`patient-nav-item ${activeTab === 'appointments' ? 'active' : ''}`}
            onClick={() => setActiveTab('appointments')}
          >
            <span className="patient-nav-icon">📋</span>
            <span className="patient-nav-label">Appointments</span>
          </div>
          <div 
            className={`patient-nav-item ${activeTab === 'medicalRecords' ? 'active' : ''}`}
            onClick={() => setActiveTab('medicalRecords')}
          >
            <span className="patient-nav-icon">📄</span>
            <span className="patient-nav-label">Medical Records</span>
          </div>
          <div 
            className={`patient-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <span className="patient-nav-icon">⚙️</span>
            <span className="patient-nav-label">Settings</span>
          </div>
        </nav>

        <button className="patient-logout" onClick={handleLogout}>
          <span>🚪</span>
          Logout
        </button>
      </div>

      {/* Main Content */}
      <div className="patient-main">
        {/* Header */}
        <div className="patient-header">
          <div className="patient-header-content">
            <h1>Your Dashboard</h1>
            <div className="patient-header-status">
              <span className="patient-status-dot"></span>
              <span className="patient-status-text">Active</span>
            </div>
          </div>
          <div className="patient-header-subtitle">
            Welcome back, {patient?.name || 'Patient'}
          </div>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <>
            {/* Stats Grid */}
            <div className="patient-stats-grid">
              <div className="patient-stat-card">
                <div className="patient-stat-label">Upcoming Appointments</div>
                <div className="patient-stat-value">{appointments?.length || 0}</div>
                <div className="patient-stat-change">Scheduled</div>
              </div>
              <div className="patient-stat-card">
                <div className="patient-stat-label">Health Score</div>
                <div className="patient-stat-value">{healthStatus?.health_score?.toFixed(0) || 100}%</div>
                <div className="patient-stat-change">{healthStatus?.health_status || 'Excellent'}</div>
              </div>
              <div className="patient-stat-card">
                <div className="patient-stat-label">Priority Level</div>
                <div className="patient-stat-value">{healthStatus?.priority_level || 'LOW'}</div>
                <div className="patient-stat-change">Current Status</div>
              </div>
              <div className="patient-stat-card">
                <div className="patient-stat-label">Severity Score</div>
                <div className="patient-stat-value">{healthStatus?.severity_score?.toFixed(1) || 0}</div>
                <div className="patient-stat-change">AI Assessed</div>
              </div>
            </div>

            {/* AI Health Insights */}
            <div className="patient-insights-section">
              <h2>AI Health Insights</h2>
              {recommendations && recommendations.length > 0 ? (
                <div className="patient-recommendations">
                  {recommendations.slice(0, 4).map((rec, index) => (
                    <div key={rec.id || index} className={`patient-recommendation ${rec.priority.toLowerCase()}-priority`}>
                      <div className="patient-rec-header">
                        <span className="patient-rec-time">{rec.time}</span>
                        <span className="patient-rec-priority">{rec.priority}</span>
                      </div>
                      <div className="patient-rec-icon" style={{fontSize: '24px', margin: '8px 0'}}>
                        {rec.icon}
                      </div>
                      <div className="patient-rec-title">{rec.title}</div>
                      <div className="patient-rec-description">{rec.description}</div>
                      <button 
                        className="patient-rec-action"
                        onClick={() => {
                          const actionLower = rec.action.toLowerCase();
                          if (actionLower.includes('emergency')) {
                            handleHealthAction('emergency');
                          } else if (actionLower.includes('track')) {
                            handleHealthAction('track');
                          } else if (actionLower.includes('schedule')) {
                            handleHealthAction('schedule');
                          }
                        }}
                      >
                        {rec.action}
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="patient-empty-state">
                  <span className="patient-empty-icon">✨</span>
                  <p>No AI recommendations yet. Update your symptoms to get personalized insights.</p>
                  <button className="patient-action-btn" onClick={() => setShowSymptomsModal(true)}>
                    Update Symptoms
                  </button>
                </div>
              )}
            </div>

            {/* Appointments List */}
            <div className="patient-appointments-section">
              <h2>Upcoming Appointments</h2>
              {appointments && appointments.length > 0 ? (
                <div className="patient-appointments-list">
                  {appointments.map((apt, index) => (
                    <div key={apt.id || index} className="patient-appointment-card">
                      <div className="patient-apt-time">
                        {apt.time || 'TBD'}
                      </div>
                      <div className="patient-apt-details">
                        <div className="patient-apt-doctor">{apt.doctor_name || 'Dr. Unknown'}</div>
                        <div className="patient-apt-location">{apt.location || 'General Checkup'}</div>
                      </div>
                      <span className={`patient-apt-status ${apt.status?.toLowerCase() || 'pending'}`}>
                        {apt.status || 'Pending'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="patient-empty-state">
                  <span className="patient-empty-icon">📭</span>
                  <p>No appointments scheduled</p>
                </div>
              )}
            </div>

            {/* AI Tools & Quick Actions */}
            <div className="patient-actions-section">
              <h2>🧠 AI Tools & Actions</h2>
              
              {/* AI Tools Grid */}
              <div className="ai-tools-premium-grid">
                <div className="ai-tool-premium-card">
                  <div className="ai-tool-icon">🏥</div>
                  <h3>Symptom Checker</h3>
                  <p>Get AI-powered diagnosis based on your symptoms</p>
                  <button className="ai-tool-btn primary" onClick={() => setShowSymptomsModal(true)}>
                    Analyze Symptoms
                  </button>
                </div>

                <div className="ai-tool-premium-card">
                  <div className="ai-tool-icon">📅</div>
                  <h3>Appointment Optimizer</h3>
                  <p>Schedule smart appointments with doctor recommendations</p>
                  <button className="ai-tool-btn primary" onClick={() => setShowScheduleModal(true)}>
                    Schedule Now
                  </button>
                </div>

                <div className="ai-tool-premium-card">
                  <div className="ai-tool-icon">📊</div>
                  <h3>Queue Insights</h3>
                  <p>View real-time queue status and wait time predictions</p>
                  <button className="ai-tool-btn primary" onClick={() => setShowQueueInsightsModal(true)}>
                    View Queue Info
                  </button>
                </div>
              </div>

              {/* Additional Actions */}
              <div className="patient-actions-grid">
                <button className="patient-action-btn secondary" onClick={() => setShowReportModal(true)}>
                  <span className="patient-action-icon">📤</span>
                  <span>Upload Report</span>
                </button>
                <button className="patient-action-btn secondary" onClick={() => setActiveTab('settings')}>
                  <span className="patient-action-icon">⚙️</span>
                  <span>Settings</span>
                </button>
              </div>
            </div>
          </>
        )}

        {/* Appointments Tab */}
        {activeTab === 'appointments' && (
          <div style={{paddingTop: '2rem'}}>
            <h2 style={{marginBottom: '1.5rem', fontSize: '1.5rem', color: '#f1f5f9'}}>Your Appointments</h2>
            {appointments && appointments.length > 0 ? (
              <div className="patient-appointments-list">
                {appointments.map((apt, index) => (
                  <div key={apt.id || index} className="patient-appointment-card" style={{marginBottom: '1rem'}}>
                    <div className="patient-apt-time">
                      {apt.appointment_date || apt.date || 'TBD'} @ {apt.appointment_time || apt.time || 'TBD'}
                    </div>
                    <div className="patient-apt-details">
                      <div className="patient-apt-doctor">{apt.doctor_name || apt.doctor || 'Dr. Unknown'}</div>
                      <div className="patient-apt-location">{apt.location || apt.reason || 'General Checkup'}</div>
                    </div>
                    <span className={`patient-apt-status ${apt.status?.toLowerCase() || 'pending'}`}>
                      {apt.status || 'Pending'}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="patient-empty-state">
                <span className="patient-empty-icon">📭</span>
                <p>No appointments scheduled</p>
                <button className="patient-action-btn" onClick={() => setShowScheduleModal(true)}>
                  Schedule an Appointment
                </button>
              </div>
            )}
          </div>
        )}

        {/* Medical Records Tab */}
        {activeTab === 'medicalRecords' && (
          <div style={{paddingTop: '2rem'}}>
            {/* Prescriptions Section */}
            <div style={{marginBottom: '3rem'}}>
              <h2 style={{marginBottom: '1.5rem', fontSize: '1.5rem', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                💊 Doctor Prescriptions
              </h2>
              {prescriptions && prescriptions.length > 0 ? (
                <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem'}}>
                  {prescriptions.map((prescription, index) => (
                    <div 
                      key={prescription.id || index} 
                      style={{
                        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.9) 100%)',
                        border: '2px solid rgba(34, 197, 94, 0.3)',
                        borderRadius: '1rem',
                        padding: '1.75rem',
                        color: '#cbd5e1',
                        boxShadow: '0 4px 15px rgba(34, 197, 94, 0.1)'
                      }}
                    >
                      <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem'}}>
                        <span style={{fontSize: '1.5rem'}}>👨‍⚕️</span>
                        <div>
                          <div style={{color: '#22c55e', fontWeight: '700', fontSize: '0.95rem'}}>
                            {prescription.doctor_name || 'Dr. Unknown'}
                          </div>
                          <div style={{color: '#94a3b8', fontSize: '0.85rem'}}>
                            📅 {prescription.prescription_date || prescription.created_at?.split('T')[0] || 'Unknown Date'}
                          </div>
                        </div>
                      </div>
                      <div style={{marginBottom: '1rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(148, 163, 184, 0.2)'}}>
                        <p style={{margin: '0 0 0.5rem 0', color: '#f1f5f9', fontWeight: '600', fontSize: '1rem'}}>
                          ✓ Doctor prescribed you to take:
                        </p>
                        <p style={{margin: '0', color: '#e0f2fe', fontSize: '1.05rem', fontWeight: '500'}}>
                          {prescription.medication || prescription.diagnosis || 'Medication'}
                        </p>
                      </div>
                      {prescription.dosage && (
                        <div style={{marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(148, 163, 184, 0.2)'}}>
                          <p style={{margin: '0 0 0.5rem 0', color: '#94a3b8', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em'}}>
                            Dosage
                          </p>
                          <p style={{margin: '0', color: '#cbd5e1', fontSize: '0.95rem'}}>
                            {prescription.dosage}
                          </p>
                        </div>
                      )}
                      {prescription.description && (
                        <div style={{marginBottom: '0.75rem'}}>
                          <p style={{margin: '0 0 0.5rem 0', color: '#94a3b8', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em'}}>
                            Notes
                          </p>
                          <p style={{margin: '0', color: '#cbd5e1', fontSize: '0.9rem', lineHeight: '1.5'}}>
                            {prescription.description}
                          </p>
                        </div>
                      )}
                      {prescription.days_supply && (
                        <div style={{marginTop: '1rem', padding: '0.75rem', background: 'rgba(34, 197, 94, 0.08)', borderRadius: '0.5rem', borderLeft: '3px solid #22c55e'}}>
                          <p style={{margin: '0', color: '#86efac', fontSize: '0.85rem'}}>
                            ⏱️ {prescription.days_supply} days supply available
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="patient-empty-state">
                  <span className="patient-empty-icon">💊</span>
                  <p>No prescriptions yet</p>
                </div>
              )}
            </div>

            {/* Medical Records Section */}
            <h2 style={{marginBottom: '1.5rem', fontSize: '1.5rem', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
              📋 Medical Records
            </h2>
            {medicalRecords && medicalRecords.length > 0 ? (
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem'}}>
                {medicalRecords.map((record, index) => (
                  <div 
                    key={record.id || index} 
                    style={{
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid rgba(100, 116, 139, 0.3)',
                      borderRadius: '0.75rem',
                      padding: '1.5rem',
                      color: '#cbd5e1'
                    }}
                  >
                    <div style={{marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'start'}}>
                      <div>
                        <div style={{color: '#94a3b8', fontSize: '0.85rem'}}>
                          📅 {record.created_at ? new Date(record.created_at).toLocaleDateString() : 'Unknown Date'}
                        </div>
                        <h3 style={{color: '#f1f5f9', marginBottom: '0.5rem', fontSize: '1.1rem', margin: '0.5rem 0 0 0'}}>
                          {record.file_name || `Report ${index + 1}`}
                        </h3>
                      </div>
                      <span 
                        style={{
                          background: record.status === 'approved' ? 'rgba(34, 197, 94, 0.2)' : record.status === 'pending' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                          color: record.status === 'approved' ? '#22c55e' : record.status === 'pending' ? '#f59e0b' : '#ef4444',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '0.25rem',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'uppercase'
                        }}
                      >
                        {record.status || 'pending'}
                      </span>
                    </div>

                    {record.report_type && (
                      <div style={{fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.75rem'}}>
                        📎 Type: <strong>{record.report_type}</strong>
                      </div>
                    )}

                    {record.description && (
                      <div style={{fontSize: '0.9rem', marginBottom: '1rem', padding: '0.75rem', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '0.5rem', borderLeft: '2px solid rgba(6, 182, 212, 0.5)'}}>
                        <p style={{margin: '0 0 0.5rem 0', color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase'}}>
                          Report Notes
                        </p>
                        <p style={{margin: '0', color: '#cbd5e1'}}>
                          {record.description}
                        </p>
                      </div>
                    )}

                    {record.reviewed_by && (
                      <div style={{
                        background: 'rgba(34, 197, 94, 0.08)',
                        border: '1px solid rgba(34, 197, 94, 0.3)',
                        borderRadius: '0.5rem',
                        padding: '1rem',
                        marginBottom: '1rem'
                      }}>
                        <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem'}}>
                          <span style={{fontSize: '1.2rem'}}>👨‍⚕️</span>
                          <div>
                            <p style={{margin: '0', color: '#22c55e', fontWeight: '600', fontSize: '0.9rem'}}>
                              Reviewed by Dr. {record.reviewed_by}
                            </p>
                            {record.reviewed_at && (
                              <p style={{margin: '0.25rem 0 0 0', color: '#86efac', fontSize: '0.8rem'}}>
                                {new Date(record.reviewed_at).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                        </div>
                        
                        {record.review_notes && (
                          <div style={{marginBottom: '0.75rem', paddingBottom: '0.75rem', borderBottom: '1px solid rgba(34, 197, 94, 0.2)'}}>
                            <p style={{margin: '0 0 0.5rem 0', color: '#94a3b8', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em'}}>
                              Doctor's Notes
                            </p>
                            <p style={{margin: '0', color: '#e0f2fe', fontSize: '0.9rem', lineHeight: '1.5'}}>
                              {record.review_notes}
                            </p>
                          </div>
                        )}

                        {record.findings && (
                          <div>
                            <p style={{margin: '0 0 0.5rem 0', color: '#94a3b8', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em'}}>
                              Findings
                            </p>
                            <p style={{margin: '0', color: '#e0f2fe', fontSize: '0.9rem', lineHeight: '1.5'}}>
                              {record.findings}
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    {!record.reviewed_by && record.status !== 'pending' && (
                      <div style={{padding: '0.75rem', background: 'rgba(245, 158, 11, 0.08)', borderRadius: '0.5rem', borderLeft: '3px solid #f59e0b'}}>
                        <p style={{margin: '0', color: '#fbbf24', fontSize: '0.85rem'}}>
                          ⏳ Awaiting doctor review
                        </p>
                      </div>
                    )}

                    <button 
                      style={{
                        width: '100%',
                        marginTop: '1rem',
                        background: 'rgba(6, 182, 212, 0.2)',
                        color: '#06b6d4',
                        border: '1px solid rgba(6, 182, 212, 0.5)',
                        padding: '0.75rem 1rem',
                        borderRadius: '0.5rem',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(6, 182, 212, 0.3)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(6, 182, 212, 0.2)';
                      }}
                    >
                      📥 Download
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="patient-empty-state">
                <span className="patient-empty-icon">📄</span>
                <p>No medical records uploaded yet</p>
                <button className="patient-action-btn" onClick={() => setShowReportModal(true)}>
                  Upload a Report
                </button>
              </div>
            )}
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div style={{paddingTop: '2rem'}}>
            <h2 style={{marginBottom: '1.5rem', fontSize: '1.5rem', color: '#f1f5f9'}}>Settings & Preferences</h2>
            <div style={{
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '0.75rem',
              padding: '2rem',
              color: '#cbd5e1'
            }}>
              <h3 style={{color: '#f1f5f9', marginBottom: '1rem'}}>Account Information</h3>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{display: 'block', marginBottom: '0.5rem', color: '#94a3b8'}}>Name</label>
                <input 
                  type="text" 
                  value={patient?.name || ''} 
                  disabled
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(100, 116, 139, 0.3)',
                    borderRadius: '0.5rem',
                    color: '#cbd5e1',
                    cursor: 'not-allowed'
                  }}
                />
              </div>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{display: 'block', marginBottom: '0.5rem', color: '#94a3b8'}}>Email</label>
                <input 
                  type="email" 
                  value={patient?.email || ''} 
                  disabled
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: 'rgba(30, 41, 59, 0.8)',
                    border: '1px solid rgba(100, 116, 139, 0.3)',
                    borderRadius: '0.5rem',
                    color: '#cbd5e1',
                    cursor: 'not-allowed'
                  }}
                />
              </div>
              <div style={{marginBottom: '1.5rem'}}>
                <label style={{display: 'block', marginBottom: '0.5rem', color: '#94a3b8'}}>Health Score</label>
                <div style={{
                  padding: '0.75rem',
                  background: 'rgba(30, 41, 59, 0.8)',
                  border: '1px solid rgba(100, 116, 139, 0.3)',
                  borderRadius: '0.5rem',
                  color: '#06b6d4'
                }}>
                  {healthStatus?.health_score?.toFixed(0) || 100}% - {healthStatus?.health_status || 'Excellent'}
                </div>
              </div>
              <h3 style={{color: '#f1f5f9', marginTop: '2rem', marginBottom: '1rem'}}>Preferences</h3>
              <div style={{marginBottom: '1rem'}}>
                <label style={{display: 'flex', alignItems: 'center', cursor: 'pointer'}}>
                  <input type="checkbox" defaultChecked style={{marginRight: '0.75rem'}} />
                  <span>Receive appointment reminders</span>
                </label>
              </div>
              <div style={{marginBottom: '1rem'}}>
                <label style={{display: 'flex', alignItems: 'center', cursor: 'pointer'}}>
                  <input type="checkbox" defaultChecked style={{marginRight: '0.75rem'}} />
                  <span>Receive AI health recommendations</span>
                </label>
              </div>
              <div style={{marginBottom: '1rem'}}>
                <label style={{display: 'flex', alignItems: 'center', cursor: 'pointer'}}>
                  <input type="checkbox" defaultChecked style={{marginRight: '0.75rem'}} />
                  <span>Receive queue updates</span>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Queue Insights Modal */}
      {showQueueInsightsModal && (
        <div className="patient-modal-overlay" onClick={() => setShowQueueInsightsModal(false)}>
          <div className="patient-modal" onClick={e => e.stopPropagation()}>
            <div className="patient-modal-header">
              <h3>📊 Queue Insights & Wait Times</h3>
              <button className="patient-modal-close" onClick={() => setShowQueueInsightsModal(false)}>×</button>
            </div>
            <div style={{padding: '2rem', color: '#cbd5e1', fontSize: '0.95rem', lineHeight: '1.8'}}>
              <div style={{marginBottom: '1.5rem', padding: '1rem', background: 'rgba(6, 182, 212, 0.08)', borderLeft: '4px solid #06b6d4', borderRadius: '0.5rem'}}>
                <strong style={{color: '#06b6d4'}}>Current Queue Status:</strong><br/>
                Most healthcare facilities experience shorter wait times during off-peak hours (late afternoon, early morning).
              </div>
              <div style={{marginBottom: '1.5rem', padding: '1rem', background: 'rgba(6, 182, 212, 0.08)', borderLeft: '4px solid #06b6d4', borderRadius: '0.5rem'}}>
                <strong style={{color: '#06b6d4'}}>Optimal Times to Visit:</strong><br/>
                Tuesday-Thursday, 10:00 AM - 12:00 PM typically have shorter wait times. Peak times are Monday mornings and Friday afternoons.
              </div>
              <div style={{marginBottom: '1.5rem', padding: '1rem', background: 'rgba(6, 182, 212, 0.08)', borderLeft: '4px solid #06b6d4', borderRadius: '0.5rem'}}>
                <strong style={{color: '#06b6d4'}}>AI Recommendation:</strong><br/>
                Based on your health priority and typical patterns, we recommend scheduling appointments mid-week for faster service.
              </div>
              <button className="patient-modal-submit" onClick={() => setShowQueueInsightsModal(false)}>
                Got it, Thanks!
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Health Action Modal */}
      {showHealthActionModal && (
        <div className="patient-modal-overlay" onClick={() => setShowHealthActionModal(false)}>
          <div className="patient-modal" onClick={e => e.stopPropagation()}>
            <div className="patient-modal-header">
              <h3>
                {healthActionType === 'emergency' && '🚨 Schedule Emergency Appointment'}
                {healthActionType === 'track' && '📊 Track Your Health'}
                {healthActionType === 'schedule' && '📅 Schedule Appointment'}
              </h3>
              <button className="patient-modal-close" onClick={() => setShowHealthActionModal(false)}>×</button>
            </div>
            <div style={{padding: '2rem', color: '#cbd5e1'}}>
              {healthActionType === 'emergency' && (
                <div>
                  <p style={{marginBottom: '1.5rem', lineHeight: '1.6'}}>
                    Urgent medical attention recommended. We'll help you schedule an emergency appointment with an available doctor as soon as possible.
                  </p>
                  <button 
                    className="patient-modal-submit" 
                    onClick={executeHealthAction}
                    style={{marginRight: '1rem'}}
                  >
                    Schedule Emergency
                  </button>
                  <button 
                    className="patient-modal-submit" 
                    style={{
                      background: 'rgba(100, 116, 139, 0.2)',
                      color: '#cbd5e1'
                    }}
                    onClick={() => setShowHealthActionModal(false)}
                  >
                    Cancel
                  </button>
                </div>
              )}
              {healthActionType === 'track' && (
                <div>
                  <p style={{marginBottom: '1.5rem', lineHeight: '1.6'}}>
                    You can track your health metrics in the <strong>Medical Records</strong> section. View your health score, previous reports, and AI recommendations there.
                  </p>
                  <button 
                    className="patient-modal-submit" 
                    onClick={() => {
                      setShowHealthActionModal(false);
                      setActiveTab('medicalRecords');
                    }}
                  >
                    Go to Medical Records
                  </button>
                </div>
              )}
              {healthActionType === 'schedule' && (
                <div>
                  <p style={{marginBottom: '1.5rem', lineHeight: '1.6'}}>
                    Schedule a regular appointment with your preferred doctor. Choose a date and time that works best for you.
                  </p>
                  <button 
                    className="patient-modal-submit" 
                    onClick={executeHealthAction}
                    style={{marginRight: '1rem'}}
                  >
                    Continue to Scheduler
                  </button>
                  <button 
                    className="patient-modal-submit" 
                    style={{
                      background: 'rgba(100, 116, 139, 0.2)',
                      color: '#cbd5e1'
                    }}
                    onClick={() => setShowHealthActionModal(false)}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Update Symptoms Modal */}
      {showSymptomsModal && (
        <div className="patient-modal-overlay" onClick={() => setShowSymptomsModal(false)}>
          <div className="patient-modal" onClick={e => e.stopPropagation()}>
            <div className="patient-modal-header">
              <h3>Update Your Symptoms</h3>
              <button className="patient-modal-close" onClick={() => setShowSymptomsModal(false)}>×</button>
            </div>
            <form onSubmit={handleUpdateSymptoms} className="patient-modal-form">
              <div className="patient-form-group">
                <label>Current Symptoms</label>
                <textarea 
                  placeholder="Enter symptoms separated by commas (e.g., headache, cough, fever)"
                  value={symptomsInput}
                  onChange={e => setSymptomsInput(e.target.value)}
                  required
                  rows="5"
                ></textarea>
              </div>
              <div style={{fontSize: '12px', color: '#94a3b8', marginTop: '8px'}}>
                Example: chest pain, breathing difficulty, high fever
              </div>
              <button type="submit" className="patient-modal-submit">Update & Get Recommendations</button>
            </form>
          </div>
        </div>
      )}

      {/* Schedule Appointment Modal */}
      {showScheduleModal && (
        <div className="patient-modal-overlay" onClick={() => setShowScheduleModal(false)}>
          <div className="patient-modal" onClick={e => e.stopPropagation()}>
            <div className="patient-modal-header">
              <h3>Schedule Appointment</h3>
              <button className="patient-modal-close" onClick={() => setShowScheduleModal(false)}>×</button>
            </div>
            <form onSubmit={handleScheduleAppointment} className="patient-modal-form">
              <div className="patient-form-group">
                <label>Doctor</label>
                <select 
                  value={appointmentForm.doctor}
                  onChange={e => setAppointmentForm({...appointmentForm, doctor: e.target.value})}
                  required
                >
                  <option value="">Select a doctor</option>
                  {doctors && doctors.length > 0 ? (
                    doctors.map((doc) => (
                      <option key={doc.id} value={doc.id}>
                        {doc.name || 'Dr. Unknown'} ({doc.specialization || 'General'})
                      </option>
                    ))
                  ) : (
                    <option>No doctors available</option>
                  )}
                </select>
              </div>
              <div className="patient-form-group">
                <label>Date</label>
                <input 
                  type="date"
                  value={appointmentForm.date}
                  onChange={e => setAppointmentForm({...appointmentForm, date: e.target.value})}
                  required
                />
              </div>
              <div className="patient-form-group">
                <label>Time</label>
                <input 
                  type="time"
                  value={appointmentForm.time}
                  onChange={e => setAppointmentForm({...appointmentForm, time: e.target.value})}
                  required
                />
              </div>
              <div className="patient-form-group">
                <label>Reason</label>
                <textarea 
                  placeholder="Describe your symptoms or reason for visit"
                  value={appointmentForm.reason}
                  onChange={e => setAppointmentForm({...appointmentForm, reason: e.target.value})}
                  required
                ></textarea>
              </div>
              <button type="submit" className="patient-modal-submit">Schedule</button>
            </form>
          </div>
        </div>
      )}

      {/* Upload Report Modal */}
      {showReportModal && (
        <div className="patient-modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="patient-modal" onClick={e => e.stopPropagation()}>
            <div className="patient-modal-header">
              <h3>Upload Medical Report</h3>
              <button className="patient-modal-close" onClick={() => setShowReportModal(false)}>×</button>
            </div>
            <form onSubmit={handleReportUpload} className="patient-modal-form">
              <div className="patient-form-group">
                <label>Select File</label>
                <input 
                  id="reportFile"
                  type="file"
                  accept=".pdf,.jpg,.png,.doc,.docx"
                  required
                />
              </div>
              <button type="submit" className="patient-modal-submit">Upload</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDashboard;
