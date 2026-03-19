import React, { useState } from 'react';
import './SymptomChecker.css';

const SymptomChecker = () => {
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [filteredSymptoms, setFilteredSymptoms] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [error, setError] = useState(null);

  const API_URL = 'http://127.0.0.1:8000';

  React.useEffect(() => {
    fetchAvailableSymptoms();
  }, []);

  const fetchAvailableSymptoms = async () => {
    try {
      const response = await fetch(`${API_URL}/ml/disease/symptoms`);
      if (response.ok) {
        const data = await response.json();
        setAvailableSymptoms(data.symptoms);
        setFilteredSymptoms(data.symptoms);
      }
    } catch (err) {
      console.error('Error fetching symptoms:', err);
      setError('Could not load symptoms');
    }
  };

  const handleSymptomSearch = (text) => {
    setSearchText(text);
    const filtered = availableSymptoms.filter(symptom =>
      symptom.toLowerCase().includes(text.toLowerCase())
    );
    setFilteredSymptoms(filtered);
  };

  const toggleSymptom = (symptom) => {
    if (selectedSymptoms.includes(symptom)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symptom));
    } else {
      setSelectedSymptoms([...selectedSymptoms, symptom]);
    }
  };

  const predictDisease = async () => {
    if (selectedSymptoms.length === 0) {
      setError('Please select at least one symptom');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/ml/disease/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms: selectedSymptoms, top_k: 5 })
      });

      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
      } else {
        setError('Failed to predict disease. Please try again.');
      }
    } catch (err) {
      setError('Error connecting to prediction service');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const clearPrediction = () => {
    setPrediction(null);
    setSelectedSymptoms([]);
    setSearchText('');
  };

  return (
    <div className="symptom-checker-container">
      <div className="symptom-checker-header">
        <h2>🏥 AI Symptom Checker</h2>
        <p>Describe your symptoms to get preliminary disease prediction</p>
      </div>

      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {!prediction ? (
        <div className="symptom-checker-form">
          {/* Symptom Search */}
          <div className="symptom-search-section">
            <label>Search Symptoms:</label>
            <input
              type="text"
              placeholder="Type symptom name... (e.g., fever, cough, headache)"
              value={searchText}
              onChange={(e) => handleSymptomSearch(e.target.value)}
              className="symptom-search-input"
            />
          </div>

          {/* Filtered Symptom List */}
          <div className="symptom-list-section">
            <label>Available Symptoms ({filteredSymptoms.length})</label>
            <div className="symptom-chips">
              {filteredSymptoms.slice(0, 30).map((symptom) => (
                <button
                  key={symptom}
                  className={`symptom-chip ${selectedSymptoms.includes(symptom) ? 'selected' : ''}`}
                  onClick={() => toggleSymptom(symptom)}
                >
                  {symptom.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Selected Symptoms */}
          {selectedSymptoms.length > 0 && (
            <div className="selected-symptoms-section">
              <label>Selected Symptoms ({selectedSymptoms.length})</label>
              <div className="selected-symptom-tags">
                {selectedSymptoms.map((symptom) => (
                  <span key={symptom} className="symptom-tag">
                    {symptom.replace(/_/g, ' ')}
                    <button onClick={() => toggleSymptom(symptom)}>×</button>
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Predict Button */}
          <button
            onClick={predictDisease}
            disabled={selectedSymptoms.length === 0 || loading}
            className="predict-button"
          >
            {loading ? 'Analyzing Symptoms...' : '🔍 Predict Disease'}
          </button>
        </div>
      ) : (
        <div className="prediction-results">
          <div className="primary-prediction">
            <h3>Primary Diagnosis</h3>
            <div className="disease-card primary">
              <div className="disease-name">{prediction.primary_prediction.disease}</div>
              <div className="confidence-meter">
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${prediction.primary_prediction.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="confidence-text">
                  {(prediction.primary_prediction.confidence * 100).toFixed(1)}% Match
                </span>
              </div>
              <p className="disease-description">
                {prediction.primary_prediction.description}
              </p>
              <p className="recommendation">
                <strong>Recommendation:</strong> {prediction.primary_prediction.recommended_action}
              </p>
            </div>
          </div>

          {prediction.alternative_diagnoses.length > 0 && (
            <div className="alternative-predictions">
              <h3>Alternative Diagnoses</h3>
              <div className="alternative-cards">
                {prediction.alternative_diagnoses.map((alt, idx) => (
                  <div key={idx} className="disease-card alternative">
                    <div className="disease-name">{alt.disease}</div>
                    <div className="confidence-text">
                      {(alt.confidence * 100).toFixed(1)}% Match
                    </div>
                    <p className="disease-description">{alt.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="symptoms-summary">
            <h4>Your Symptoms:</h4>
            <div className="symptom-summary-tags">
              {prediction.input_symptoms.map((sym) => (
                <span key={sym} className="summary-tag">
                  {sym.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>

          <div className="disclaimer">
            <strong>⚠️ Important Disclaimer:</strong> This AI-based symptom checker provides preliminary
            assessment only and should NOT replace professional medical advice. Always consult with
            qualified healthcare professionals for accurate diagnosis and treatment. In case of
            emergency, immediately seek medical attention.
          </div>

          <button onClick={clearPrediction} className="check-again-button">
            Check Another Combination
          </button>
        </div>
      )}
    </div>
  );
};

export default SymptomChecker;
