import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Register.css";

function Register() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
    role: "patient",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("register");
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    if (formData.phone.length < 10) {
      setError("Phone number must be at least 10 digits");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          phone_number: formData.phone,
          password: formData.password,
          role: formData.role,
        }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("email", data.email);
        
        // Redirect to appropriate dashboard based on role
        const dashboard = data.role === "doctor" ? "/doctor-dashboard" : "/patient-dashboard";
        setTimeout(() => {
          navigate(dashboard);
        }, 500);
      } else {
        setError(data.detail || "Registration failed");
        setLoading(false);
      }
    } catch (error) {
      console.error("Register error:", error);
      setError("Server error. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      {/* Left Side - Background Video */}
      <div className="register-background">
        <video 
          autoPlay 
          muted 
          loop 
          className="background-video"
        >
          <source src="/explore-bg.mp4" type="video/mp4" />
        </video>
        <div className="video-overlay"></div>
        
        {/* Left Side Content */}
        <div className="left-content">
          <div className="logo-section">
            <div className="logo-icon">🏥</div>
            <h1 className="logo-title">PulseSync</h1>
            <p className="logo-subtitle">Healthcare Management System</p>
          </div>
        </div>
      </div>

      {/* Right Side - Register Form */}
      <div className="register-form-container">
        {/* Navigation Tabs */}
        <div className="tabs-container">
          <button 
            className={`tab-button ${activeTab === 'patient' ? 'active' : ''}`}
            onClick={() => setActiveTab('patient')}
          >
            PATIENT
          </button>
          <button 
            className={`tab-button ${activeTab === 'doctor' ? 'active' : ''}`}
            onClick={() => setActiveTab('doctor')}
          >
            DOCTOR
          </button>
          <button 
            className={`tab-button ${activeTab === 'sign-in' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('sign-in');
              navigate('/login');
            }}
          >
            SIGN IN
          </button>
          <button 
            className={`tab-button ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => setActiveTab('register')}
          >
            REGISTER
          </button>
        </div>

        {/* Form Card */}
        <div className="form-card">
          {/* Welcome Section */}
          <div className="welcome-section">
            <h2 className="welcome-title">Create Account</h2>
            <p className="welcome-subtitle">Join PulseSync as a {formData.role === 'doctor' ? 'Healthcare Provider' : 'Patient'}</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="error-alert">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleRegister} className="register-form">
            {/* Full Name Input */}
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div className="input-wrapper">
                <span className="input-icon">👤</span>
                <input
                  type="text"
                  name="name"
                  placeholder="John Doe"
                  className="form-input"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Email Input */}
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <div className="input-wrapper">
                <span className="input-icon">📧</span>
                <input
                  type="email"
                  name="email"
                  placeholder={formData.role === 'doctor' ? 'doctor@hospital.com' : 'john@patient.com'}
                  className="form-input"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Phone Number Input */}
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <div className="input-wrapper">
                <span className="input-icon">📱</span>
                <input
                  type="tel"
                  name="phone"
                  placeholder="+1 (555) 000-0000"
                  className="form-input"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Role Selection */}
            <div className="form-group">
              <label className="form-label">Account Type</label>
              <div className="role-selector">
                <button
                  type="button"
                  className={`role-option ${formData.role === 'patient' ? 'active' : ''}`}
                  onClick={() => setFormData(prev => ({ ...prev, role: 'patient' }))}
                >
                  <span className="role-icon">👥</span>
                  <span className="role-text">Patient</span>
                </button>
                <button
                  type="button"
                  className={`role-option ${formData.role === 'doctor' ? 'active' : ''}`}
                  onClick={() => setFormData(prev => ({ ...prev, role: 'doctor' }))}
                >
                  <span className="role-icon">👨‍⚕️</span>
                  <span className="role-text">Doctor</span>
                </button>
              </div>
            </div>

            {/* Password Input */}
            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="input-wrapper">
                <span className="input-icon">🔐</span>
                <input
                  type="password"
                  name="password"
                  placeholder="Create a strong password"
                  className="form-input"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Confirm Password Input */}
            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <div className="input-wrapper">
                <span className="input-icon">✔️</span>
                <input
                  type="password"
                  name="confirmPassword"
                  placeholder="Confirm your password"
                  className="form-input"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Register Button */}
            <button
              type="submit"
              disabled={loading}
              className="register-button"
            >
              {loading ? (
                <>
                  <span className="spinner">⏳</span>
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span className="button-icon">→</span>
                  <span>CREATE ACCOUNT</span>
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="login-section">
            <p className="login-text">Already have an account?</p>
            <Link to="/login" className="login-link">
              Sign in here
            </Link>
          </div>
        </div>

        {/* Back to Explore */}
        <div className="back-button">
          <Link to="/explore" className="back-link">
            <svg className="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Explore
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
