import { useState, useEffect } from "react";

function PatientQueueStatus({ patientId }) {
  const [queueStatus, setQueueStatus] = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOptimization, setShowOptimization] = useState(false);

  useEffect(() => {
    fetchQueueStatus();
    const timer = setInterval(fetchQueueStatus, 10000); // Refresh every 10 seconds
    return () => clearInterval(timer);
  }, [patientId]);

  const fetchQueueStatus = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/queue/patient/${patientId}`);
      const data = await response.json();

      if (response.ok) {
        setQueueStatus(data);
        setLoading(false);
      } else if (data.status === "no_appointment") {
        setQueueStatus(data);
        setLoading(false);
      }
    } catch (error) {
      console.error("Error fetching queue status:", error);
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!queueStatus || !queueStatus.ps_id) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/queue/optimize/${queueStatus.ps_id}`,
        { method: "POST" }
      );
      const data = await response.json();

      if (response.ok) {
        setOptimization(data);
        setShowOptimization(true);
      }
    } catch (error) {
      console.error("Error optimizing queue:", error);
    }
  };

  const handleApplyOptimization = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/queue/optimize/${queueStatus.ps_id}/apply`,
        { method: "POST" }
      );
      const data = await response.json();

      if (response.ok) {
        alert("✅ Optimization applied! Your appointment has been updated.");
        setShowOptimization(false);
        fetchQueueStatus();
      } else {
        alert("Error applying optimization");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to apply optimization");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-10">
        <div className="text-center">
          <div className="animate-spin text-3xl mb-3">⏳</div>
          <p className="text-gray-300">Loading queue status...</p>
        </div>
      </div>
    );
  }

  if (queueStatus?.status === "no_appointment") {
    return (
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <p className="text-gray-300">No active appointments</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Queue Status */}
      <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-8 rounded-xl border border-purple-500 border-opacity-30">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h3 className="text-3xl font-bold text-purple-300 mb-2">📍 Queue Position</h3>
            <p className="text-gray-300">Your current status and predictions</p>
          </div>
          <span className="text-5xl">🎯</span>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* Position & Time */}
          <div className="space-y-4">
            <div className="bg-purple-950 p-4 rounded-lg">
              <p className="text-gray-400 mb-1">Queue Position</p>
              <p className="text-4xl font-bold text-purple-300">
                #{queueStatus?.queue_position || "Pending"}
              </p>
            </div>

            <div className="bg-purple-950 p-4 rounded-lg">
              <p className="text-gray-400 mb-1">Scheduled Time</p>
              <p className="text-lg font-semibold text-purple-300">
                {new Date(queueStatus?.scheduled_time).toLocaleString()}
              </p>
            </div>

            <div className="bg-purple-950 p-4 rounded-lg">
              <p className="text-gray-400 mb-1">PS ID</p>
              <p className="text-lg font-mono font-bold text-yellow-400">{queueStatus?.ps_id}</p>
            </div>
          </div>

          {/* Predictions */}
          <div className="space-y-4">
            <div className="bg-blue-950 p-4 rounded-lg border border-blue-500 border-opacity-20">
              <p className="text-gray-400 mb-1">⏱️ Estimated Wait Time</p>
              <p className="text-4xl font-bold text-blue-300">{queueStatus?.predicted_wait_time}</p>
              <p className="text-xs text-gray-400 mt-1">Based on queue analysis</p>
            </div>

            <div className="bg-cyan-950 p-4 rounded-lg border border-cyan-500 border-opacity-20">
              <p className="text-gray-400 mb-1">⏲️ Consultation Duration</p>
              <p className="text-4xl font-bold text-cyan-300">{queueStatus?.predicted_consultation_duration}</p>
            </div>

            <div className="bg-green-950 p-4 rounded-lg border border-green-500 border-opacity-20">
              <p className="text-gray-400 mb-1">Total Time (Estimated)</p>
              <p className="text-4xl font-bold text-green-300">{queueStatus?.total_estimated_time}</p>
            </div>
          </div>
        </div>

        {/* Doctor & Risk Assessment */}
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-purple-950 p-4 rounded-lg">
            <p className="text-gray-400 text-sm mb-1">Assigned Doctor</p>
            <p className="text-xl font-bold text-purple-300">{queueStatus?.doctor || "Pending"}</p>
          </div>

          <div className="bg-purple-950 p-4 rounded-lg">
            <p className="text-gray-400 text-sm mb-1">Priority Level</p>
            <p className="text-xl font-bold text-purple-300">{queueStatus?.priority_level}</p>
          </div>

          {queueStatus?.no_show_risk && (
            <div className={`p-4 rounded-lg ${
              parseFloat(queueStatus.no_show_risk) > 0.4 
                ? "bg-red-950 border border-red-500 border-opacity-30" 
                : "bg-green-950 border border-green-500 border-opacity-30"
            }`}>
              <p className="text-gray-400 text-sm mb-1">No-Show Risk</p>
              <p className={`text-xl font-bold ${
                parseFloat(queueStatus.no_show_risk) > 0.4 
                  ? "text-red-300" 
                  : "text-green-300"
              }`}>
                {queueStatus.no_show_risk}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Optimization Recommendation */}
      {!showOptimization && (
        <button
          onClick={handleOptimize}
          className="w-full bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-700 hover:to-indigo-600 p-4 rounded-lg font-semibold transition"
        >
          🤖 Check AI Optimization Recommendations
        </button>
      )}

      {/* Optimization Modal */}
      {showOptimization && optimization && (
        <div className="bg-gradient-to-br from-amber-900 to-amber-800 p-8 rounded-xl border border-amber-500 border-opacity-30">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h4 className="text-2xl font-bold text-amber-300 mb-2">
                💡 AI Recommendation
              </h4>
              <p className="text-amber-100">
                {optimization.recommendation !== "none"
                  ? `Optimization: ${optimization.recommendation}`
                  : "No changes recommended"}
              </p>
            </div>
            <button
              onClick={() => setShowOptimization(false)}
              className="text-2xl hover:text-amber-200"
            >
              ✕
            </button>
          </div>

          {optimization.recommendation !== "none" && (
            <>
              <div className="bg-amber-950 p-4 rounded-lg mb-6">
                <p className="text-amber-100 mb-4">{optimization.explanation}</p>

                <div className="bg-amber-900 p-3 rounded-lg mb-4">
                  <p className="text-amber-200 text-sm font-semibold mb-2">
                    📱 You'll receive notification:
                  </p>
                  <p className="text-amber-100 text-sm italic">
                    {optimization.patient_notification}
                  </p>
                </div>

                <div className="text-sm text-amber-300 mb-4">
                  <p>
                    <strong>Confidence Level:</strong> {optimization.confidence}
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleApplyOptimization}
                  className="flex-1 bg-green-600 hover:bg-green-700 p-3 rounded-lg font-semibold text-white transition"
                >
                  ✅ Accept & Apply
                </button>
                <button
                  onClick={() => setShowOptimization(false)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 p-3 rounded-lg font-semibold transition"
                >
                  ❌ Decline
                </button>
              </div>
            </>
          )}
        </div>
      )}

      {/* Info Card */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 text-sm text-gray-300">
        <p>
          <strong>💡 Tip:</strong> This queue system uses AI to predict wait times and suggest optimizations in real-time.
          Times update automatically every 10 seconds.
        </p>
      </div>
    </div>
  );
}

export default PatientQueueStatus;
