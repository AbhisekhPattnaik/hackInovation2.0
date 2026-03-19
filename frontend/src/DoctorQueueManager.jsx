import { useState, useEffect } from "react";

function DoctorQueueManager({ doctorId }) {
  const [queueData, setQueueData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchQueueData();
    const timer = setInterval(fetchQueueData, 5000); // Refresh every 5 seconds
    return () => clearInterval(timer);
  }, [doctorId]);

  const fetchQueueData = async () => {
    try {
      const token = localStorage.getItem("token");
      const headers = {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      };

      const [queueRes, metricsRes] = await Promise.all([
        fetch(`http://127.0.0.1:8000/queue/doctor/${doctorId}/queue`, { headers }),
        fetch(`http://127.0.0.1:8000/queue/metrics/doctor/${doctorId}`, { headers })
      ]);

      if (!queueRes.ok || !metricsRes.ok) {
        throw new Error("Failed to fetch queue data");
      }

      const queueDataJSON = await queueRes.json();
      const metricsJSON = await metricsRes.json();

      setQueueData(queueDataJSON);
      setMetrics(metricsJSON);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching queue data:", error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-10">
        <div className="text-center">
          <div className="animate-spin text-3xl mb-3">⏳</div>
          <p className="text-gray-300">Loading your queue...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-800 p-6 rounded-xl border border-blue-500 border-opacity-30">
        <h2 className="text-3xl font-bold text-blue-300 mb-2">👨‍⚕️ Queue Management</h2>
        <p className="text-blue-100">Real-time patient flow optimization for your consultation room</p>
      </div>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-4 gap-4">
        <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
          <p className="text-gray-400 text-sm mb-1">Queue Size</p>
          <p className="text-4xl font-bold text-blue-400">{queueData?.queue_size || 0}</p>
        </div>

        <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
          <p className="text-gray-400 text-sm mb-1">Total Est. Time</p>
          <p className="text-4xl font-bold text-purple-400">{queueData?.total_estimated_time || "0m"}</p>
        </div>

        <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
          <p className="text-gray-400 text-sm mb-1">Specialization</p>
          <p className="text-xl font-bold text-cyan-400">{queueData?.specialization || "N/A"}</p>
        </div>

        <div className={`p-4 rounded-lg border border-opacity-30 ${
          queueData?.bottlenecks?.length > 0
            ? "bg-red-900 border-red-500"
            : "bg-green-900 border-green-500"
        }`}>
          <p className="text-gray-400 text-sm mb-1">Bottlenecks</p>
          <p className="text-4xl font-bold text-red-400">{queueData?.bottlenecks?.length || 0}</p>
        </div>
      </div>

      {/* Performance Metrics */}
      {metrics && (
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
          <h3 className="text-lg font-bold text-indigo-300 mb-4">📊 Performance Metrics</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm mb-2">Avg Wait Time</p>
              <p className="text-2xl font-bold text-blue-300">{metrics.avg_wait_time}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm mb-2">Avg Duration</p>
              <p className="text-2xl font-bold text-purple-300">{metrics.avg_consultation_duration}</p>
            </div>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-gray-400 text-sm mb-2">No-Show Rate</p>
              <p className="text-2xl font-bold text-red-300">{metrics.no_show_rate}</p>
            </div>
          </div>
        </div>
      )}

      {/* Patient Queue */}
      <div className="bg-gray-900 p-6 rounded-xl border border-gray-800">
        <h3 className="text-xl font-bold text-indigo-300 mb-4">📋 Current Queue</h3>

        {queueData?.patients && queueData.patients.length > 0 ? (
          <div className="space-y-3">
            {queueData.patients.map((patient, idx) => (
              <div
                key={idx}
                onClick={() => setSelectedPatient(patient)}
                className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-indigo-500 cursor-pointer transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl font-bold text-indigo-400 w-8 text-center">
                        #{patient.queue_position}
                      </span>
                      <div>
                        <p className="font-semibold text-white">{patient.patient_name}</p>
                        <p className="text-xs text-gray-500">ID: {patient.patient_ps_id}</p>
                      </div>
                    </div>

                    <div className="flex gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Severity:</span>
                        <span className="ml-2 font-mono text-cyan-400">
                          {(patient.severity * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-400">Duration:</span>
                        <span className="ml-2 font-mono text-purple-400">{patient.predicted_duration}m</span>
                      </div>
                      <div>
                        <span className="text-gray-400">No-Show Risk:</span>
                        <span className="ml-2 font-mono text-red-400">{patient.no_show_risk}</span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-xl mb-2">
                      {patient.priority > 0.7
                        ? "⭐"
                        : patient.priority > 0.5
                        ? "👤"
                        : "📍"}
                    </div>
                    <div className="flex gap-1">
                      {patient.priority > 0.7 && (
                        <span className="text-xs bg-red-500 text-white px-2 py-1 rounded">HIGH</span>
                      )}
                      {parseFloat(patient.no_show_risk) > 0.4 && (
                        <span className="text-xs bg-yellow-500 text-white px-2 py-1 rounded">RISK</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Progress bar for time */}
                <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                    style={{ width: `${Math.min(100, (patient.priority || 0) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-10 text-gray-400">
            <p>No patients in queue</p>
          </div>
        )}
      </div>

      {/* Bottleneck Alerts */}
      {queueData?.bottlenecks && queueData.bottlenecks.length > 0 && (
        <div className="bg-red-900 bg-opacity-20 border border-red-500 border-opacity-30 p-6 rounded-xl">
          <h3 className="text-lg font-bold text-red-400 mb-4">⚠️ Queue Bottlenecks</h3>
          <div className="space-y-3">
            {queueData.bottlenecks.map((bottleneck, idx) => (
              <div key={idx} className="bg-red-900 bg-opacity-30 p-4 rounded-lg border border-red-500 border-opacity-20">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-red-300">Patient #{bottleneck.patient_id}</p>
                    <p className="text-sm text-red-200 mt-1">
                      Expected wait: {bottleneck.predicted_wait} minutes
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    bottleneck.severity === 'HIGH'
                      ? 'bg-red-500 text-white'
                      : 'bg-yellow-500 text-white'
                  }`}>
                    {bottleneck.severity}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-indigo-900 bg-opacity-20 border border-indigo-500 border-opacity-30 p-4 rounded-lg text-sm text-indigo-100">
        <p>
          <strong>💡 AI Tips:</strong> This queue system automatically predicts consultation times and no-show risks.
          The system refreshes every 5 seconds. Click on a patient to see detailed optimization recommendations.
        </p>
      </div>
    </div>
  );
}

export default DoctorQueueManager;
