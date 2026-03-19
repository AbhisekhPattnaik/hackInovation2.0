import React, { useState } from 'react';
import './AppointmentOptimizer.css';

const AppointmentOptimizer = () => {
  const [appointmentData, setAppointmentData] = useState({
    age: 35,
    is_female: 0,
    age_group: 1,
    days_advance_booking: 7,
    has_hypertension: 0,
    has_diabetes: 0,
    has_alcoholism: 0,
    medical_complexity: 0,
    received_sms_reminder: 1,
    appointment_month: new Date().getMonth() + 1,
    appointment_weekday: new Date().getDay(),
    is_weekend_appt: 0
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://127.0.0.1:8000';

  const handleInputChange = (field, value) => {
    setAppointmentData({
      ...appointmentData,
      [field]: parseInt(value) || value
    });

    // Auto-calculate medical complexity
    if (['has_hypertension', 'has_diabetes', 'has_alcoholism'].includes(field)) {
      const updated = { ...appointmentData, [field]: parseInt(value) };
      const complexity = updated.has_hypertension + updated.has_diabetes + updated.has_alcoholism;
      setAppointmentData({ ...updated, medical_complexity: complexity });
    }

    // Auto-detect weekend
    if (field === 'appointment_weekday') {
      const weekday = parseInt(value);
      setAppointmentData({
        ...appointmentData,
        appointment_weekday: weekday,
        is_weekend_appt: weekday >= 5 ? 1 : 0
      });
    }
  };

  const predictNoShow = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/ml/appointment/predict-noshow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appointmentData)
      });

      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
      } else {
        setError('Failed to predict no-show risk');
      }
    } catch (err) {
      setError('Error connecting to prediction service');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'Low Risk':
        return '#10b981';
      case 'Medium Risk':
        return '#f59e0b';
      case 'High Risk':
      case 'Very High Risk':
        return '#ef4444';
      default:
        return '#06b6d4';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'Low Risk':
        return '✓';
      case 'Medium Risk':
        return '⚠';
      case 'High Risk':
      case 'Very High Risk':
        return '✗';
      default:
        return '?';
    }
  };

  return (
    <div className="appointment-optimizer-container">
      <div className="optimizer-header">
        <h2>📅 Appointment No-Show Predictor</h2>
        <p>Analyze appointment characteristics to predict no-show probability</p>
      </div>

      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="form-sections">
        {/* Patient Demographics */}
        <div className="form-section">
          <h3>👤 Patient Demographics</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Age</label>
              <input
                type="number"
                value={appointmentData.age}
                onChange={(e) => handleInputChange('age', e.target.value)}
                min="0"
                max="100"
              />
            </div>

            <div className="form-group">
              <label>Gender</label>
              <select
                value={appointmentData.is_female}
                onChange={(e) => handleInputChange('is_female', e.target.value)}
              >
                <option value="0">Male</option>
                <option value="1">Female</option>
              </select>
            </div>

            <div className="form-group">
              <label>Age Group</label>
              <select
                value={appointmentData.age_group}
                onChange={(e) => handleInputChange('age_group', e.target.value)}
              >
                <option value="0">0-18</option>
                <option value="1">19-35</option>
                <option value="2">36-50</option>
                <option value="3">51-65</option>
                <option value="4">65+</option>
              </select>
            </div>
          </div>
        </div>

        {/* Medical Conditions */}
        <div className="form-section">
          <h3>🏥 Medical Conditions</h3>
          <div className="form-grid">
            <div className="form-group checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={appointmentData.has_hypertension === 1}
                  onChange={(e) => handleInputChange('has_hypertension', e.target.checked ? 1 : 0)}
                />
                Hypertension
              </label>
            </div>

            <div className="form-group checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={appointmentData.has_diabetes === 1}
                  onChange={(e) => handleInputChange('has_diabetes', e.target.checked ? 1 : 0)}
                />
                Diabetes
              </label>
            </div>

            <div className="form-group checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={appointmentData.has_alcoholism === 1}
                  onChange={(e) => handleInputChange('has_alcoholism', e.target.checked ? 1 : 0)}
                />
                Alcoholism
              </label>
            </div>

            <div className="form-group readonly">
              <label>Medical Complexity</label>
              <div className="complexity-display">{appointmentData.medical_complexity}</div>
            </div>
          </div>
        </div>

        {/* Appointment Details */}
        <div className="form-section">
          <h3>📋 Appointment Details</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Days in Advance</label>
              <input
                type="number"
                value={appointmentData.days_advance_booking}
                onChange={(e) => handleInputChange('days_advance_booking', e.target.value)}
                min="0"
                max="365"
              />
            </div>

            <div className="form-group">
              <label>Month</label>
              <select
                value={appointmentData.appointment_month}
                onChange={(e) => handleInputChange('appointment_month', e.target.value)}
              >
                {[...Array(12)].map((_, i) => (
                  <option key={i} value={i + 1}>
                    {new Date(2024, i).toLocaleString('default', { month: 'long' })}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Day of Week</label>
              <select
                value={appointmentData.appointment_weekday}
                onChange={(e) => handleInputChange('appointment_weekday', e.target.value)}
              >
                <option value="0">Sunday</option>
                <option value="1">Monday</option>
                <option value="2">Tuesday</option>
                <option value="3">Wednesday</option>
                <option value="4">Thursday</option>
                <option value="5">Friday</option>
                <option value="6">Saturday</option>
              </select>
            </div>

            <div className="form-group checkbox">
              <label>
                <input
                  type="checkbox"
                  checked={appointmentData.received_sms_reminder === 1}
                  onChange={(e) => handleInputChange('received_sms_reminder', e.target.checked ? 1 : 0)}
                />
                SMS Reminder Sent
              </label>
            </div>
          </div>
        </div>

        {/* Predict Button */}
        <button
          onClick={predictNoShow}
          disabled={loading}
          className="predict-button"
        >
          {loading ? 'Analyzing...' : '🔍 Predict No-Show Risk'}
        </button>
      </div>

      {/* Prediction Results */}
      {prediction && (
        <div className="prediction-results">
          <div className="risk-indicator" style={{ borderColor: getRiskColor(prediction.risk_level) }}>
            <div className="risk-badge" style={{ background: getRiskColor(prediction.risk_level) }}>
              <span className="risk-icon">{getRiskIcon(prediction.risk_level)}</span>
              <span className="risk-label">{prediction.risk_level}</span>
            </div>

            <div className="probability-section">
              <div className="probability-marker">
                <div className="probability-bar">
                  <div
                    className="probability-fill"
                    style={{
                      width: `${prediction.no_show_probability * 100}%`,
                      background: getRiskColor(prediction.risk_level)
                    }}
                  ></div>
                </div>
                <div className="probability-text">
                  <strong>No-Show Probability:</strong> {(prediction.no_show_probability * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="confidence-info">
              Confidence: {(prediction.confidence * 100).toFixed(1)}%
            </div>
          </div>

          {/* Recommendations */}
          {prediction.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h3>💡 Recommendations</h3>
              <ul className="recommendations-list">
                {prediction.recommendations.map((rec, idx) => (
                  <li key={idx}>
                    <span className="rec-bullet">●</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Items */}
          <div className="action-items">
            {prediction.no_show_probability > 0.35 && (
              <div className="action-item urgent">
                <span className="action-icon">🔔</span>
                <span>Consider sending reminder notifications</span>
              </div>
            )}

            {appointmentData.days_advance_booking > 21 && (
              <div className="action-item warning">
                <span className="action-icon">📆</span>
                <span>Appointment scheduled far in advance - send confirmations closer to date</span>
              </div>
            )}

            {appointmentData.received_sms_reminder === 0 && (
              <div className="action-item info">
                <span className="action-icon">💬</span>
                <span>Enable SMS reminders to reduce no-show likelihood</span>
              </div>
            )}

            {appointmentData.is_weekend_appt === 1 && (
              <div className="action-item warning">
                <span className="action-icon">📅</span>
                <span>Weekend appointments have higher no-show rates</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AppointmentOptimizer;
