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
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgWidth = pageWidth * 0.9; // leave margins
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    const xOffset = (pageWidth - imgWidth) / 2;
    const yOffset = 15; // top margin

    // Handle overflow to next page (basic)
    if (imgHeight > pageHeight) {
      let heightLeft = imgHeight;
      let position = yOffset;

      pdf.addImage(imgData, "PNG", xOffset, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft > 0) {
        pdf.addPage();
        position = heightLeft - imgHeight;
        pdf.addImage(imgData, "PNG", xOffset, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }
    } else {
      pdf.addImage(imgData, "PNG", xOffset, yOffset, imgWidth, imgHeight);
    }

    pdf.save(`${dataset.filename}_summary.pdf`);
  };

  if (!dataset) {
    return <p style={{ padding: "30px" }}>Loading summary...</p>;
  }

  return (
    <div style={{ padding: "30px", maxWidth: "900px", margin: "auto" }}>
      <button onClick={() => navigate("/dashboard")}>
        ← Back to Dashboard
      </button>

      <h2 style={{ marginTop: "20px" }}>Summary</h2>

      {/* 📄 CONTENT FOR PDF */}
      <div ref={reportRef}>
        <Summary summary={dataset.summary} />

        {showCharts && (
          <div style={{ marginTop: "30px" }}>
            <Charts summary={dataset.summary} />
          </div>
        )}
      </div>

      {/* ACTION BUTTONS */}
      <div style={{ marginTop: "25px", display: "flex", gap: "12px" }}>
        <button onClick={() => setShowCharts(!showCharts)}>
          {showCharts ? "Hide Charts" : "View Charts"}
        </button>

        <button onClick={generatePDF}>
          📄 Download PDF Report
        </button>
      </div>
    </div>
  );
}

export default SummaryPage;
