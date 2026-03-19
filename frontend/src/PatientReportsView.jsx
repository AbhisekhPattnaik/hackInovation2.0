import { useState, useEffect } from "react";

function PatientReports({ patientId, patientName }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState("");
  const [selectedReportId, setSelectedReportId] = useState(null);
  const [updatingReportId, setUpdatingReportId] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [patientId]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/reports/patient/${patientId}`);
      const data = await response.json();
      if (response.ok) {
        setReports(data);
      }
    } catch (error) {
      console.error("Error fetching reports:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateDiagnosis = async (reportId) => {
    if (!diagnosis.trim()) {
      alert("Please enter diagnosis/notes");
      return;
    }

    setUpdatingReportId(reportId);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/reports/${reportId}/diagnosis`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ diagnosis }),
        }
      );

      if (response.ok) {
        alert("✅ Diagnosis updated successfully!");
        setDiagnosis("");
        setSelectedReportId(null);
        await fetchReports();
      } else {
        alert("Failed to update diagnosis");
      }
    } catch (error) {
      console.error("Error updating diagnosis:", error);
      alert("Error updating diagnosis");
    } finally {
      setUpdatingReportId(null);
    }
  };

  const handleDownload = async (reportId, fileName) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/reports/${reportId}/download`);
      const data = await response.json();

      if (response.ok) {
        const binaryString = atob(data.file_data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: data.file_type });

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error("Error downloading report:", error);
      alert("Failed to download report");
    }
  };

  return (
    <div className="bg-gray-900 p-6 rounded-xl border border-blue-500 border-opacity-30 mt-6">
      <h4 className="text-lg font-semibold text-blue-300 mb-4">📄 Patient Medical Reports</h4>

      {loading ? (
        <p className="text-gray-400">Loading reports...</p>
      ) : reports.length === 0 ? (
        <p className="text-gray-500">No medical reports available for this patient</p>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <div key={report.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-semibold text-blue-300">{report.file_name}</p>
                  <p className="text-xs text-gray-400">
                    Uploaded by {report.uploader_name} on{" "}
                    {new Date(report.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDownload(report.id, report.file_name)}
                  className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-xs font-semibold text-white transition"
                >
                  ⬇️ Download
                </button>
              </div>

              {/* Existing diagnosis */}
              {report.diagnosis && (
                <div className="bg-gray-700 p-3 rounded mb-3 text-sm text-gray-300">
                  <p className="font-medium mb-1">Previous Notes:</p>
                  <p>{report.diagnosis}</p>
                </div>
              )}

              {/* Add/Edit diagnosis section */}
              {selectedReportId !== report.id ? (
                <button
                  onClick={() => {
                    setSelectedReportId(report.id);
                    setDiagnosis(report.diagnosis || "");
                  }}
                  className="w-full bg-green-600 hover:bg-green-700 p-2 rounded text-sm font-semibold text-white transition"
                >
                  ✏️ Add/Edit Diagnosis
                </button>
              ) : (
                <div className="space-y-2">
                  <textarea
                    value={diagnosis}
                    onChange={(e) => setDiagnosis(e.target.value)}
                    placeholder="Enter your diagnosis and notes..."
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-200 focus:border-green-500 focus:outline-none text-sm resize-none"
                    rows="3"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleUpdateDiagnosis(report.id)}
                      disabled={updatingReportId === report.id}
                      className="flex-1 bg-green-600 hover:bg-green-700 p-2 rounded text-sm font-semibold text-white transition disabled:opacity-50"
                    >
                      {updatingReportId === report.id ? "Saving..." : "Save"}
                    </button>
                    <button
                      onClick={() => {
                        setSelectedReportId(null);
                        setDiagnosis("");
                      }}
                      className="flex-1 bg-gray-700 hover:bg-gray-600 p-2 rounded text-sm font-semibold text-white transition"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PatientReports;
