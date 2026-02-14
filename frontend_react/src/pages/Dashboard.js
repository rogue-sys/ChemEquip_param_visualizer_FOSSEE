import React from "react";
import UploadCSV from "../components/UploadCSV";
import API from "../services/api";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const handleUpload = async () => {
    const res = await API.get("history/");
    if (res.data.length > 0) {
      navigate(`/summary/${res.data[0].id}`);
    }
  };

  return (
    <div className="px-4 py-10">
      <div className="max-w-2xl mx-auto">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-lg border p-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-2">
            Dashboard
          </h2>

          <p className="text-gray-500 mb-6">
            Upload a CSV file to visualize and analyze chemical equipment
            parameters.
          </p>

          <UploadCSV onUpload={handleUpload} />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
