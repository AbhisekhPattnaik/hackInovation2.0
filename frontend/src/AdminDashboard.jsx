import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AdminDashboard.css";

function AdminDashboard() {
  const navigate = useNavigate();
  const [systemData, setSystemData] = useState({
    totalUsers: 0,
    totalDoctors: 0,
    totalPatients: 0,
    appointmentsToday: 0,
    activeSessions: 0,
    systemStatus: "online",
  });

  const [healthData, setHealthData] = useState({
    uptime: "99.9%",
    apiResponseTime: "45ms",
    dbStatus: "connected",
    errorLogs: [],
    failedLogins: 0,
    otpFailures: 0,
  });

  const [doctors, setDoctors] = useState([]);
  const [users, setUsers] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    if (!token || role !== "admin") {
      navigate("/login");
      return;
    }

    // Fetch system data
    fetchSystemData();
    fetchDoctors();
    fetchUsers();

    // Refresh every 5 seconds
    const interval = setInterval(() => {
      fetchSystemData();
    }, 5000);

    return () => clearInterval(interval);
  }, [navigate]);

  const fetchSystemData = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/admin/system-stats", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setSystemData(data);
      }
    } catch (error) {
      console.error("Error fetching system data:", error);
    }
  };

  const fetchDoctors = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/admin/doctors", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setDoctors(data);
      }
    } catch (error) {
      console.error("Error fetching doctors:", error);
    }
  };

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://127.0.0.1:8000/admin/users", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("email");
    navigate("/explore");
  };

  const verifyDoctor = async (doctorId) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`http://127.0.0.1:8000/admin/verify-doctor/${doctorId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        fetchDoctors();
      }
    } catch (error) {
      console.error("Error verifying doctor:", error);
    }
  };

  return (
    <div className="admin-container">
      {/* Sidebar */}
      <div className="admin-sidebar">
        <div className="sidebar-header">
          <h2>🏥 Admin Panel</h2>
        </div>
        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            📊 Dashboard
          </button>
          <button
            className={`nav-item ${activeTab === "health" ? "active" : ""}`}
            onClick={() => setActiveTab("health")}
          >
            ⚙️ System Health
          </button>
          <button
            className={`nav-item ${activeTab === "doctors" ? "active" : ""}`}
            onClick={() => setActiveTab("doctors")}
          >
            👨‍⚕️ Doctors
          </button>
          <button
            className={`nav-item ${activeTab === "users" ? "active" : ""}`}
            onClick={() => setActiveTab("users")}
          >
            👥 Users
          </button>
          <button
            className={`nav-item ${activeTab === "ai" ? "active" : ""}`}
            onClick={() => setActiveTab("ai")}
          >
            🤖 AI Monitoring
          </button>
        </nav>
        <button className="logout-btn" onClick={handleLogout}>
          🚪 Logout
        </button>
      </div>

      {/* Main Content */}
      <div className="admin-main">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="tab-content">
            <h1>📊 System Overview</h1>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-info">
                  <p className="stat-label">Total Users</p>
                  <p className="stat-value">{systemData.totalUsers}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">👨‍⚕️</div>
                <div className="stat-info">
                  <p className="stat-label">Total Doctors</p>
                  <p className="stat-value">{systemData.totalDoctors}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🏥</div>
                <div className="stat-info">
                  <p className="stat-label">Total Patients</p>
                  <p className="stat-value">{systemData.totalPatients}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">📅</div>
                <div className="stat-info">
                  <p className="stat-label">Appointments Today</p>
                  <p className="stat-value">{systemData.appointmentsToday}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🟢</div>
                <div className="stat-info">
                  <p className="stat-label">Active Sessions</p>
                  <p className="stat-value">{systemData.activeSessions}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className={`stat-icon ${systemData.systemStatus === "online" ? "online" : "offline"}`}>
                  {systemData.systemStatus === "online" ? "✅" : "⚠️"}
                </div>
                <div className="stat-info">
                  <p className="stat-label">System Status</p>
                  <p className="stat-value capitalize">{systemData.systemStatus}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Health Tab */}
        {activeTab === "health" && (
          <div className="tab-content">
            <h1>⚙️ System Health</h1>
            <div className="health-grid">
              <div className="health-card">
                <h3>Server Uptime</h3>
                <p className="health-value">{healthData.uptime}</p>
              </div>
              <div className="health-card">
                <h3>API Response Time</h3>
                <p className="health-value">{healthData.apiResponseTime}</p>
              </div>
              <div className="health-card">
                <h3>Database Status</h3>
                <p className="health-value health-connected">{healthData.dbStatus}</p>
              </div>
              <div className="health-card">
                <h3>Failed Logins (Today)</h3>
                <p className="health-value health-warning">{healthData.failedLogins}</p>
              </div>
              <div className="health-card">
                <h3>OTP Failures (Today)</h3>
                <p className="health-value health-warning">{healthData.otpFailures}</p>
              </div>
            </div>

            <div className="error-logs">
              <h3>📋 Recent Error Logs</h3>
              {healthData.errorLogs.length > 0 ? (
                <div className="logs-list">
                  {healthData.errorLogs.map((log, idx) => (
                    <div key={idx} className="log-item">
                      <p className="log-time">{log.timestamp}</p>
                      <p className="log-message">{log.message}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-logs">✅ No errors detected</p>
              )}
            </div>
          </div>
        )}

        {/* Doctors Tab */}
        {activeTab === "doctors" && (
          <div className="tab-content">
            <h1>👨‍⚕️ Doctor Management</h1>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Specialty</th>
                  <th>Status</th>
                  <th>Utilization</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {doctors.map((doctor) => (
                  <tr key={doctor.id}>
                    <td>{doctor.name}</td>
                    <td>{doctor.specialty}</td>
                    <td>
                      <span className={`badge badge-${doctor.verificationStatus?.toLowerCase()}`}>
                        {doctor.verificationStatus || "PENDING"}
                      </span>
                    </td>
                    <td>{(doctor.utilization * 100).toFixed(0)}%</td>
                    <td>
                      {doctor.verificationStatus === "PENDING" && (
                        <button
                          className="btn-verify"
                          onClick={() => verifyDoctor(doctor.id)}
                        >
                          Verify
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="tab-content">
            <h1>👥 User Monitoring</h1>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Joined</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.slice(0, 20).map((user) => (
                  <tr key={user.id}>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>
                      <span className={`badge badge-${user.role?.toLowerCase()}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className="status-active">🟢 Active</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* AI Monitoring Tab */}
        {activeTab === "ai" && (
          <div className="tab-content">
            <h1>🤖 AI Monitoring</h1>
            <div className="ai-stats">
              <div className="ai-card">
                <h3>Total Recommendations</h3>
                <p className="ai-value">1,247</p>
              </div>
              <div className="ai-card">
                <h3>Reschedules Today</h3>
                <p className="ai-value">23</p>
              </div>
              <div className="ai-card">
                <h3>Avg Wait Time Reduction</h3>
                <p className="ai-value">-18%</p>
              </div>
              <div className="ai-card">
                <h3>AI Confidence Score</h3>
                <p className="ai-value">94.2%</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
