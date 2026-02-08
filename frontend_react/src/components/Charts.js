import React from "react";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title,
} from "chart.js";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title
);

function Charts({ summary }) {
  // ---- PIE CHART (Equipment Type Distribution) ----
  const pieData = {
    labels: Object.keys(summary.type_distribution),
    datasets: [
      {
        label: "Equipment Count",
        data: Object.values(summary.type_distribution),
        backgroundColor: [
          "#4CAF50",
          "#2196F3",
          "#FFC107",
          "#E91E63",
          "#9C27B0",
        ],
        borderColor: "#ffffff",
        borderWidth: 2,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "Equipment Type Distribution",
        font: { size: 18 },
      },
      legend: {
        position: "bottom",
      },
    },
  };

  // ---- BAR CHART (Averages) ----
  const barData = {
    labels: ["Flowrate", "Pressure", "Temperature"],
    datasets: [
      {
        label: "Average Values",
        data: [
          summary.avg_flowrate,
          summary.avg_pressure,
          summary.avg_temperature,
        ],
        backgroundColor: ["#3F51B5", "#009688", "#FF5722"],
        borderRadius: 6,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "Average Equipment Parameters",
        font: { size: 18 },
      },
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ marginTop: "30px" }}>
      <div style={{ width: "400px", margin: "0 auto" }}>
        <Pie data={pieData} options={pieOptions} />
      </div>

      <div style={{ width: "600px", margin: "40px auto" }}>
        <Bar data={barData} options={barOptions} />
      </div>
    </div>
  );
}

export default Charts;
