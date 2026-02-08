import React, { useState } from "react";
import API from "../services/api";

function UploadCSV({ onUpload }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError("");

    if (!selectedFile) {
      setFile(null);
      return;
    }

    const isCSV =
      selectedFile.type === "text/csv" ||
      selectedFile.name.toLowerCase().endsWith(".csv");

    if (!isCSV) {
      setError("Only CSV files are allowed.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file || isUploading) return;

    setError("");
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await API.post("upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      onUpload(res.data);
      setFile(null);
    } catch (err) {
      setError("Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <h3>Upload CSV</h3>

      <input
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        disabled={isUploading}
      />

      {file && !isUploading && (
        <p style={{ fontSize: "13px", marginTop: "6px" }}>
          Selected: {file.name}
        </p>
      )}

      {isUploading && (
        <p style={{ color: "#0072ff", marginTop: "10px" }}>
          Uploading… please wait
        </p>
      )}

      {!isUploading && error && (
        <p style={{ color: "red", marginTop: "10px" }}>
          {error}
        </p>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || isUploading}
        style={{ marginTop: "10px" }}
      >
        {isUploading ? "Uploading..." : "Upload"}
      </button>
    </div>
  );
}

export default UploadCSV;
