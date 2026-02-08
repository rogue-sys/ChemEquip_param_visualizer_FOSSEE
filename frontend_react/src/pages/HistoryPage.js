import React, { useEffect, useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    API.get("history/").then((res) => setHistory(res.data));
  }, []);

  // 🔧 Format ISO datetime → "07 Feb 2026, 09:41"
  const formatDateTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    });
  };

  return (
    <div style={{ padding: "30px", maxWidth: "900px", margin: "auto" }}>
      <button onClick={() => navigate("/dashboard")}>
        ← Back to Dashboard
      </button>

      <h2 style={{ marginTop: "20px" }}>Upload History</h2>

      {history.length === 0 ? (
        /* ✅ Empty state */
        <p style={{ marginTop: "20px", color: "#666" }}>
          No history yet…
        </p>
      ) : (
        /* ✅ History table */
        <table border="1" width="100%" style={{ marginTop: "20px" }}>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Uploaded At</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h) => (
              <tr
                key={h.id}
                style={{ cursor: "pointer" }}
                onClick={() => navigate(`/summary/${h.id}`)}
              >
                <td>{h.filename}</td>
                <td>{formatDateTime(h.uploaded_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default HistoryPage;
