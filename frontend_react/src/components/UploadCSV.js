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
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-800">
        Upload CSV
      </h3>

      <div className="flex items-center gap-4">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          disabled={isUploading}
          className="
            block w-full text-sm text-gray-600
            file:mr-4 file:py-2 file:px-4
            file:rounded-lg file:border-0
            file:bg-gray-100 file:text-gray-700
            hover:file:bg-gray-200
          "
        />

        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className={`
            px-5 py-2 rounded-lg text-sm font-medium
            transition
            ${
              !file || isUploading
                ? "bg-gray-300 text-gray-600 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-500"
            }
          `}
        >
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {file && !isUploading && (
        <p className="text-sm text-gray-500">
          Selected: {file.name}
        </p>
      )}

      {isUploading && (
        <p className="text-sm text-blue-600">
          Uploading… please wait
        </p>
      )}

      {error && !isUploading && (
        <p className="text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}

export default UploadCSV;
