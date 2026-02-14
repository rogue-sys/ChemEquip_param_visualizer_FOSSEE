import React, { useEffect, useState } from "react";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function HistoryPage() {
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    API.get("history/").then((res) => setHistory(res.data));
  }, []);

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
  <div className="py-10 px-4 text-slate-200">
    <div className="max-w-4xl mx-auto">

      {/* Back Button */}
      <button
        onClick={() => navigate("/dashboard")}
        className="text-sm text-slate-400 hover:text-white transition mb-4"
      >
        ← Back to Dashboard
      </button>

      {/* Heading */}
      <h2 className="text-2xl font-semibold text-white mb-6">
        Uploaded History
      </h2>

      {history.length === 0 ? (
        <p className="text-slate-400">
          No history yet…
        </p>
      ) : (
        <div className="space-y-4">
          {history.map((h) => (
            <div
              key={h.id}
              onClick={() => navigate(`/summary/${h.id}`)}
              className="
                bg-slate-50 text-gray-900
                rounded-xl border border-slate-200
                p-5 cursor-pointer
                hover:shadow-lg hover:scale-[1.02]
                transition
              "
            >
              <p className="font-medium">
                {h.filename}
              </p>
              <p className="text-sm text-gray-500">
                Uploaded: {formatDateTime(h.uploaded_at)}
              </p>
            </div>
          ))}
        </div>
      )}

    </div>
  </div>
);

}

export default HistoryPage;
