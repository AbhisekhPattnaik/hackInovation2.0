import { useState, useEffect } from "react";

function QueueDashboard() {
  const [systemData, setSystemData] = useState(null);
  const [doctorQueues, setDoctorQueues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds

  useEffect(() => {
    fetchDashboardData();
    const timer = setInterval(fetchDashboardData, refreshInterval);
    return () => clearInterval(timer);
  }, [refreshInterval]);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/queue/hospital/dashboard");
      const data = await response.json();
      
      setSystemData({
        total_patients: data.total_patients_waiting,
        total_wait: data.total_estimated_wait,
        system_health: data.system_health,
        recommended_actions: data.recommended_actions,
        bottlenecks: data.bottlenecks_detected
      });
      
      setDoctorQueues(data.doctor_summaries || []);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
      setLoading(false);
    }
  };

  const getHealthColor = (health) => {
    if (health.includes("🟢")) return "text-green-400 bg-green-500 bg-opacity-10";
    if (health.includes("🟡")) return "text-yellow-400 bg-yellow-500 bg-opacity-10";
    if (health.includes("🟠")) return "text-orange-400 bg-orange-500 bg-opacity-10";
    return "text-red-400 bg-red-500 bg-opacity-10";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950 to-gray-950 flex items-center justify-center text-white">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p>Loading queue data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950 to-gray-950 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-indigo-400 mb-2">📊 Real-Time Queue Dashboard</h1>
        <p className="text-gray-400">AI-Powered Patient Flow Optimization</p>
      </div>

      {/* System Health Overview */}
      <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900 p-6 rounded-xl border border-indigo-500 border-opacity-30">
          <p className="text-gray-400 text-sm mb-2">Total in Queue</p>
          <p className="text-4xl font-bold text-indigo-400">{systemData?.total_patients || 0}</p>
          <p className="text-xs text-gray-500 mt-2">Patients waiting</p>
        </div>

        <div className="bg-gray-900 p-6 rounded-xl border border-purple-500 border-opacity-30">
          <p className="text-gray-400 text-sm mb-2">Total Wait Time</p>
          <p className="text-4xl font-bold text-purple-400">{systemData?.total_wait || "0"}</p>
          <p className="text-xs text-gray-500 mt-2">Combined estimate</p>
        </div>

        <div className={`p-6 rounded-xl border border-opacity-30 ${getHealthColor(systemData?.system_health || "")}`}>
          <p className="text-gray-400 text-sm mb-2">System Health</p>
          <p className="text-2xl font-bold">{systemData?.system_health}</p>
        </div>

        <div className="bg-gray-900 p-6 rounded-xl border border-red-500 border-opacity-30">
          <p className="text-gray-400 text-sm mb-2">Bottlenecks</p>
          <p className="text-4xl font-bold text-red-400">{systemData?.bottlenecks || 0}</p>
          <p className="text-xs text-gray-500 mt-2">Detected issues</p>
        </div>
      </div>

      {/* Recommended Actions */}
      {systemData?.recommended_actions && systemData.recommended_actions.length > 0 && (
        <div className="max-w-7xl mx-auto mb-8 bg-yellow-500 bg-opacity-10 border border-yellow-500 border-opacity-30 p-6 rounded-xl">
          <h3 className="text-lg font-bold text-yellow-400 mb-3">⚠️ Recommended Actions</h3>
          <ul className="space-y-2">
            {systemData.recommended_actions.map((action, idx) => (
              <li key={idx} className="text-yellow-300 text-sm flex items-start">
                <span className="mr-3">→</span>
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Doctor Queue Overview */}
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold text-indigo-300 mb-6">Doctors & Queue Status</h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctorQueues.map((doctor) => (
            <div
              key={doctor.doctor_id}
              className="bg-gray-900 p-6 rounded-xl border border-gray-800 hover:border-indigo-500 transition"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-indigo-300">{doctor.doctor_name}</h3>
                  <p className="text-sm text-gray-500">{doctor.specialty}</p>
                </div>
                <span className="text-2xl">{doctor.health}</span>
              </div>

              <div className="space-y-3">
                <div className="bg-gray-800 p-3 rounded-lg">
                  <p className="text-gray-400 text-xs mb-1">Queue Size</p>
                  <p className="text-2xl font-bold text-indigo-400">{doctor.queue_size}</p>
                </div>

                <div className="bg-gray-800 p-3 rounded-lg">
                  <p className="text-gray-400 text-xs mb-1">Avg Wait Time</p>
                  <p className="text-xl font-bold text-purple-400">{doctor.avg_wait_time} min</p>
                </div>

                {doctor.bottleneck_count > 0 && (
                  <div className="bg-red-500 bg-opacity-10 border border-red-500 border-opacity-30 p-3 rounded-lg">
                    <p className="text-red-300 text-sm font-semibold">
                      ⚠️ {doctor.bottleneck_count} bottleneck{doctor.bottleneck_count > 1 ? 's' : ''}
                    </p>
                  </div>
                )}

                <button className="w-full bg-indigo-600 hover:bg-indigo-700 p-2 rounded-lg text-sm font-semibold transition">
                  View Queue Details
                </button>
              </div>
            </div>
          ))}
        </div>

        {doctorQueues.length === 0 && (
          <div className="text-center py-10 text-gray-400">
            <p>No active queues at the moment</p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="max-w-7xl mx-auto mt-12 p-6 bg-gray-900 rounded-xl border border-gray-800">
        <h3 className="font-bold text-indigo-300 mb-3">System Status Legend</h3>
        <div className="grid md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-green-400">🟢</span>
            <p className="text-gray-400">Healthy: Optimal flow</p>
          </div>
          <div>
            <span className="text-yellow-400">🟡</span>
            <p className="text-gray-400">Good: Minor delays</p>
          </div>
          <div>
            <span className="text-orange-400">🟠</span>
            <p className="text-gray-400">Moderate: Action needed</p>
          </div>
          <div>
            <span className="text-red-400">🔴</span>
            <p className="text-gray-400">Concern: Urgent</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QueueDashboard;
