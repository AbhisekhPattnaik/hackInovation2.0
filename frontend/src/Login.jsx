import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok && data.access_token && data.role) {
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("email", data.email);
        
        setTimeout(() => {
          const role = data.role.toLowerCase();
          if (role === "doctor") {
            navigate("/doctor-dashboard");
          } else if (role === "admin") {
            navigate("/admin-dashboard");
          } else {
            navigate("/patient-dashboard");
          }
        }, 100);
      } else {
        setError(data.detail || "Login failed - Invalid credentials");
        setLoading(false);
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Server error. Please try again.");
      setLoading(false);
    }
  };

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setError("");
    setEmail("");
    setPassword("");
  };

  const handleBack = () => {
    setSelectedRole(null);
    setEmail("");
    setPassword("");
    setError("");
  };

  return (
    <div className="login-container">
      {/* Background */}
      <div className="login-background">
        <video 
          autoPlay 
          muted 
          loop 
          className="background-video"
        >
          <source src="/explore-bg.mp4" type="video/mp4" />
        </video>
        <div className="video-overlay"></div>
      </div>

      {/* Main Content */}
      <div className="login-content">
        {/* Header */}
        <div className="login-header">
          <div className="logo-section">
            <div className="logo-icon">🏥</div>
            <h1 className="logo-title">PulseSync</h1>
            <p className="logo-subtitle">Healthcare Command Center</p>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="login-main">
          {selectedRole === null ? (
            // Role Selection View
            <div className="role-selection">
              <div className="selection-header">
                <h2 className="selection-title">Choose Your Portal</h2>
                <p className="selection-subtitle">Sign in to access your dedicated healthcare interface</p>
              </div>

              <div className="role-cards">
                {/* Patient Card */}
                <div 
                  className="role-card patient-card"
                  onClick={() => handleRoleSelect('patient')}
                >
                  <div className="card-header">
                    <div className="card-icon patient-icon">👨‍⚕️</div>
                    <div className="card-status active"></div>
                  </div>
                  <div className="card-content">
                    <h3 className="card-title">Patient Portal</h3>
                    <p className="card-description">Access your medical records, appointments, and health insights</p>
                  </div>
                  <div className="card-footer">
                    <span className="card-status-text">Ready to access</span>
                    <svg className="card-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </div>

                {/* Doctor Card */}
                <div 
                  className="role-card doctor-card"
                  onClick={() => handleRoleSelect('doctor')}
                >
                  <div className="card-header">
                    <div className="card-icon doctor-icon">🩺</div>
                    <div className="card-status active"></div>
                  </div>
                  <div className="card-content">
                    <h3 className="card-title">Doctor Portal</h3>
                    <p className="card-description">Manage patients, appointments, and optimize your schedule</p>
                  </div>
                  <div className="card-footer">
                    <span className="card-status-text">Ready to access</span>
                    <svg className="card-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Bottom Section */}
              <div className="login-bottom-section">
                {/* Create Account Button */}
                <div className="create-account-section">
                  <p className="account-text">Don't have an account?</p>
                  <Link to="/register" className="create-account-btn">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Create Account
                  </Link>
                </div>

                {/* Back Button */}
                <div className="back-to-explore">
                  <Link to="/explore" className="explore-link">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back to Explore
                  </Link>
                </div>
              </div>
            </div>
          ) : (
            // Login Form View
            <div className="login-form-view">
              <div className="form-header">
                <button 
                  onClick={handleBack}
                  className="back-button"
                  title="Back to role selection"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <div className="form-title-section">
                  <h2 className="form-title">
                    {selectedRole === 'doctor' ? '🩺 Doctor Login' : '👨‍⚕️ Patient Login'}
                  </h2>
                  <p className="form-subtitle">Enter your credentials to continue</p>
                </div>
              </div>
              <form onSubmit={handleLogin} className="login-form">
                {/* Error Alert */}
                {error && (
                  <div className="error-alert">
                    <span className="error-icon">⚠️</span>
                    <span>{error}</span>
                  </div>
                )}

                {/* Email Input */}
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <div className="input-wrapper">
                    <span className="input-icon">📧</span>
                    <input
                      type="email"
                      placeholder={selectedRole === 'doctor' ? 'doctor@hospital.com' : 'john@patient.com'}
                      className="form-input"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Password Input */}
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <div className="input-wrapper">
                    <span className="input-icon">🔐</span>
                    <input
                      type="password"
                      placeholder="Enter your password"
                      className="form-input"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Login Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="signin-button"
                >
                  {loading ? (
                    <>
                      <span className="spinner">⏳</span>
                      <span>Logging in...</span>
                    </>
                  ) : (
                    <>
                      <span className="button-icon">→</span>
                      <span>SIGN IN</span>
                    </>
                  )}
                </button>

                {/* Create Account Link */}
                <div className="form-footer">
                  <p className="footer-text">Don't have an account?</p>
                  <Link to="/register" className="signup-link">
                    Create one here
                  </Link>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;