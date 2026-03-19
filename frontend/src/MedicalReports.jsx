import { useState, useEffect } from "react";

function MedicalReports({ patientId, userId }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [diagnosis, setDiagnosis] = useState("");
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

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
      } else {
        setError("Failed to fetch reports");
      }
    } catch (error) {
      console.error("Error fetching reports:", error);
      setError("Error fetching reports");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Check file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError("File size exceeds 10MB limit");
        return;
      }
      setFile(selectedFile);
      setError("");
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", userId);
      formData.append("diagnosis", diagnosis);

      const response = await fetch(
        `http://127.0.0.1:8000/reports/upload/${patientId}`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (response.ok) {
        setFile(null);
        setDiagnosis("");
        document.querySelector('input[type="file"]').value = "";
        await fetchReports();
        alert("✅ Report uploaded successfully!");
      } else {
        setError(data.detail || "Failed to upload report");
      }
    } catch (error) {
      console.error("Error uploading report:", error);
      setError("Error uploading report");
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (reportId, fileName) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/reports/${reportId}/download`);
      const data = await response.json();

      if (response.ok) {
        // Decode base64 and create blob
        const binaryString = atob(data.file_data);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: data.file_type });

        // Create download link
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

  const handleDeleteReport = async (reportId) => {
    if (!window.confirm("Are you sure you want to delete this report?")) {
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/reports/${reportId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setReports(reports.filter(r => r.id !== reportId));
        alert("✅ Report deleted successfully!");
      } else {
        setError("Failed to delete report");
      }
    } catch (error) {
      console.error("Error deleting report:", error);
      setError("Error deleting report");
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800 p-6 rounded-lg border border-purple-500 border-opacity-30">
        <h3 className="text-xl font-bold text-purple-400 mb-4">📄 Medical Reports</h3>

        {/* Upload Form */}
        <form onSubmit={handleUpload} className="space-y-4 mb-6 p-4 bg-gray-900 rounded-lg">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Upload File
            </label>
            <input
              type="file"
              onChange={handleFileSelect}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 focus:border-purple-500 focus:outline-none text-sm"
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            />
            <p className="text-xs text-gray-500 mt-1">Supported: PDF, JPG, PNG, DOC, DOCX (Max 10MB)</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              placeholder="Add any notes about this report..."
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-300 focus:border-purple-500 focus:outline-none text-sm resize-none"
              rows="2"
            />
          </div>

          {error && (
            <div className="bg-red-500 bg-opacity-20 border border-red-500 text-red-300 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={uploading}
            className="w-full bg-gradient-to-r from-purple-600 to-purple-500 p-2 rounded-lg font-semibold hover:from-purple-700 hover:to-purple-600 transition disabled:opacity-50"
          >
            {uploading ? "Uploading..." : "Upload Report"}
          </button>
        </form>

        {/* Reports List */}
        <div className="space-y-3">
          <h4 className="text-lg font-semibold text-gray-300">Your Reports</h4>
          
          {loading ? (
            <p className="text-gray-400">Loading reports...</p>
          ) : reports.length === 0 ? (
            <p className="text-gray-500">No reports uploaded yet</p>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <div key={report.id} className="bg-gray-700 p-4 rounded-lg border border-gray-600">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-semibold text-purple-300">{report.file_name}</p>
                      <p className="text-xs text-gray-400">
                        Uploaded by {report.uploader_name} on{" "}
                        {new Date(report.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span className="text-xs bg-purple-500 bg-opacity-30 text-purple-300 px-2 py-1 rounded">
                      {report.file_type}
                    </span>
                  </div>

                  {report.diagnosis && (
                    <div className="bg-gray-600 p-3 rounded mb-3 text-sm text-gray-300">
                      <p className="font-medium mb-1">Notes:</p>
                      <p>{report.diagnosis}</p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDownload(report.id, report.file_name)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 p-2 rounded text-sm font-semibold text-white transition"
                    >
                      ⬇️ Download
                    </button>
                    <button
                      onClick={() => handleDeleteReport(report.id)}
                      className="flex-1 bg-red-600 hover:bg-red-700 p-2 rounded text-sm font-semibold text-white transition"
                    >
                      🗑️ Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MedicalReports;
