import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

function OTPVerification() {
  const [otp, setOtp] = useState("");
  const [timer, setTimer] = useState(60);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState("wait"); // wait, verify, success
  const navigate = useNavigate();
  const location = useLocation();
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    // Get user data from navigation state
    const data = location.state?.usr;
    if (!data) {
      navigate("/register");
      return;
    }
    setUserData(data);
    
    // Send OTP automatically
    sendOTPToPhone(data);
  }, []);

  useEffect(() => {
    // Countdown timer
    if (timer > 0 && phase === "wait") {
      const interval = setInterval(() => {
        setTimer(t => t - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer, phase]);

  const sendOTPToPhone = async (data) => {
    setError("");
    setLoading(true);
    
    try {
      const response = await fetch("http://127.0.0.1:8000/send-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          phone_number: data.phone,
          password: data.password,
          role: data.role,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setPhase("wait");
        setError("");
      } else {
        setError(result.detail || "Failed to send OTP");
      }
    } catch (error) {
      console.error("Error sending OTP:", error);
      setError("Server error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (otp.length !== 6) {
      setError("OTP must be 6 digits");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/verify-otp", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: userData.email,
          otp_code: otp,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store JWT token and user info from response
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("email", data.email);
        
        setPhase("success");
        
        // Redirect to dashboard based on role
        setTimeout(() => {
          const role = data.role.toLowerCase();
          if (role === "doctor") {
            navigate("/doctor-dashboard");
          } else if (role === "admin") {
            navigate("/admin-dashboard");
          } else {
            navigate("/patient-dashboard");
          }
        }, 1500);
      } else {
        setError(data.detail || "Invalid OTP");
      }
    } catch (error) {
      console.error("Error:", error);
      setError("Server error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setTimer(60);
    setOtp("");
    await sendOTPToPhone(userData);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950 text-white p-4">
      <div className="bg-gray-900 p-8 rounded-2xl shadow-2xl w-full max-w-md border border-purple-500 border-opacity-30">
        {phase === "success" ? (
          <div className="text-center">
            <div className="text-6xl mb-4">✅</div>
            <h1 className="text-3xl font-bold text-green-400 mb-2">Registration Complete!</h1>
            <p className="text-gray-400">Your account has been verified successfully.</p>
            <p className="text-gray-500 text-sm mt-4">Redirecting to login...</p>
          </div>
        ) : (
          <>
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-purple-400 mb-2">📱 Verify OTP</h1>
              <p className="text-gray-400 text-sm">
                Enter the 6-digit OTP sent to {userData?.phone}
              </p>
              <p className="text-gray-500 text-xs mt-2">
                OTP is valid for 5 minutes
              </p>
            </div>

            {error && (
              <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-300 p-3 rounded-lg mb-6 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-4">
                  One-Time Password
                </label>
                <div className="flex gap-2 justify-center mb-4">
                  {[0, 1, 2, 3, 4, 5].map((index) => (
                    <input
                      key={index}
                      type="text"
                      maxLength="1"
                      inputMode="numeric"
                      className="w-12 h-12 text-center text-2xl font-bold rounded-lg bg-gray-800 border-2 border-gray-700 focus:border-purple-500 focus:outline-none text-white"
                      value={otp[index] || ""}
                      onChange={(e) => {
                        const newOtp = otp.split("");
                        newOtp[index] = e.target.value.replace(/\D/g, "");
                        const joined = newOtp.join("");
                        setOtp(joined.slice(0, 6));
                        
                        // Auto-focus next input
                        if (e.target.value && index < 5) {
                          e.target.parentElement.children[index + 1]?.focus();
                        }
                      }}
                    />
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full bg-gradient-to-r from-purple-600 to-purple-500 p-3 rounded-lg font-semibold hover:from-purple-700 hover:to-purple-600 transition disabled:opacity-50"
              >
                {loading ? "Verifying..." : "Verify OTP"}
              </button>
            </form>

            <div className="mt-6 text-center border-t border-gray-700 pt-4">
              {timer > 0 ? (
                <p className="text-gray-400 text-sm">
                  Resend OTP in{" "}
                  <span className="font-bold text-purple-400">{timer}s</span>
                </p>
              ) : (
                <button
                  onClick={handleResendOTP}
                  disabled={loading}
                  className="text-purple-400 hover:text-purple-300 font-semibold text-sm transition disabled:opacity-50"
                >
                  Resend OTP
                </button>
              )}
            </div>

            <div className="mt-4 text-xs text-gray-500 text-center bg-gray-800 p-3 rounded-lg">
              <p className="font-semibold mb-1">� SMS Configuration:</p>
              <p>Configure SMS_PROVIDER in .env (twilio, fast2sms, or demo)</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default OTPVerification;
