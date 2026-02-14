import React, { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import API from "../services/api";
import Summary from "../components/Summary";
import Charts from "../components/Charts";

import jsPDF from "jspdf";
import html2canvas from "html2canvas";

function SummaryPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [dataset, setDataset] = useState(null);
  const [showCharts, setShowCharts] = useState(false);
  const reportRef = useRef(null);

  useEffect(() => {
    API.get("history/").then((res) => {
      const found = res.data.find((d) => String(d.id) === id);
      if (found) setDataset(found);
    });
  }, [id]);

  const generatePDF = async () => {
    if (!reportRef.current) return;

    const canvas = await html2canvas(reportRef.current, {
      scale: 2,
      useCORS: true,
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");

    const pageWidth = pdf.internal.pageSize.getWidth();
    const imgWidth = pageWidth * 0.9;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    const xOffset = (pageWidth - imgWidth) / 2;
    pdf.addImage(imgData, "PNG", xOffset, 15, imgWidth, imgHeight);
    pdf.save(`${dataset.filename}_summary.pdf`);
  };

  if (!dataset) {
    return (
      <div className="p-8 text-gray-500">
        Loading summary...
      </div>
    );
  }

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
        Summary
      </h2>

      {/* PDF CONTENT */}
      <div ref={reportRef} className="space-y-6">
        <div className="bg-slate-50 text-gray-900 rounded-2xl shadow-lg p-6">
          <Summary summary={dataset.summary} />
        </div>

        {showCharts && (
          <div className="bg-slate-50 text-gray-900 rounded-2xl shadow-lg p-6">
            <Charts summary={dataset.summary} />
          </div>
        )}
      </div>

      {/* ACTION BUTTONS */}
      <div className="mt-6 flex gap-3">
        <button
          onClick={() => setShowCharts(!showCharts)}
          className="
            px-4 py-2 rounded-lg
            bg-slate-700 text-white
            hover:bg-slate-600
            transition
          "
        >
          {showCharts ? "Hide Charts" : "View Charts"}
        </button>

        <button
          onClick={generatePDF}
          className="
            px-4 py-2 rounded-lg
            bg-indigo-600 text-white
            hover:bg-indigo-500
            transition
          "
        >
          📄 Download PDF
        </button>
      </div>

    </div>
  </div>
);

}

export default SummaryPage;
