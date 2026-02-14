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
          "#22c55e", // green
          "#3b82f6", // blue
          "#facc15", // yellow
          "#ec4899", // pink
          "#8b5cf6", // violet
        ],
        borderColor: "#ffffff",
        borderWidth: 2,
      },
    ],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: false, // handled by UI heading
      },
      legend: {
        position: "bottom",
        labels: {
          boxWidth: 14,
          padding: 16,
        },
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
        backgroundColor: [
          "#6366f1", // indigo
          "#14b8a6", // teal
          "#f97316", // orange
        ],
        borderRadius: 8,
      },
    ],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: false, // handled by UI heading
      },
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: "#e5e7eb",
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <div className="space-y-8">
      
      {/* PIE CHART CARD */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
          Equipment Type Distribution
        </h3>

        <div className="relative h-[320px] max-w-md mx-auto">
          <Pie data={pieData} options={pieOptions} />
        </div>
      </div>

      {/* BAR CHART CARD */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
          Average Equipment Parameters
        </h3>

        <div className="relative h-[360px] max-w-2xl mx-auto">
          <Bar data={barData} options={barOptions} />
        </div>
      </div>

    </div>
  );
}

export default Charts;
