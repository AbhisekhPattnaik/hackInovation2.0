import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Login from "./login";
import Register from "./Register";
import OTPVerification from "./OTPVerification";
import Explore from "./Explore";
import DoctorDashboard from "./DoctorDashboard";
import PatientDashboard from "./PatientDashboard";
import AdminDashboard from "./AdminDashboard";
import SymptomChecker from "./SymptomChecker";
import AppointmentOptimizer from "./AppointmentOptimizer";

function App() {
  const [role, setRole] = useState(localStorage.getItem("role"));

  useEffect(() => {
    const handleStorageChange = () => {
      setRole(localStorage.getItem("role"));
    };

    // Listen for storage changes (from other tabs)
    window.addEventListener("storage", handleStorageChange);

    // Check for role changes every 100ms (for same tab updates)
    const interval = setInterval(() => {
      const currentRole = localStorage.getItem("role");
      if (currentRole !== role) {
        setRole(currentRole);
      }
    }, 100);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      clearInterval(interval);
    };
  }, [role]);

  return (
    <Router>
      <Routes>
        <Route path="/explore" element={<Explore />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<OTPVerification />} />
        
        {/* AI Features - Public Access */}
        <Route path="/ai/symptom-checker" element={<SymptomChecker />} />
        <Route path="/ai/appointment-optimizer" element={<AppointmentOptimizer />} />

        {/* Protected Routes */}
        <Route
          path="/doctor-dashboard"
          element={role === "doctor" ? <DoctorDashboard /> : <Navigate to="/login" />}
        />

        <Route
          path="/patient-dashboard"
          element={role === "patient" ? <PatientDashboard /> : <Navigate to="/login" />}
        />

        <Route
          path="/admin-dashboard"
          element={role === "admin" ? <AdminDashboard /> : <Navigate to="/login" />}
        />

        {/* Home Route */}
        <Route 
          path="/" 
          element={
            role === "doctor" ? <Navigate to="/doctor-dashboard" /> :
            role === "admin" ? <Navigate to="/admin-dashboard" /> :
            role === "patient" ? <Navigate to="/patient-dashboard" /> :
            <Navigate to="/explore" />
          } 
        />
        
        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/explore" />} />
      </Routes>
    </Router>
  );
}

export default App;