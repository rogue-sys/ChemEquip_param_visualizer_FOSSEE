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
    <div style={{ padding: "30px", maxWidth: "700px", margin: "auto" }}>
      <h2>Dashboard</h2>

      <UploadCSV onUpload={handleUpload} />
    </div>
  );
}

export default Dashboard;
