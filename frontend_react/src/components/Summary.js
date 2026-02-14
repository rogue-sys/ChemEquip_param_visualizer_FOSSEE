import React from "react";

function Summary({ summary }) {
  const stats = [
    {
      label: "Total Equipment",
      value: summary.total_count,
    },
    {
      label: "Avg Flowrate",
      value: summary.avg_flowrate,
    },
    {
      label: "Avg Pressure",
      value: summary.avg_pressure,
    },
    {
      label: "Avg Temperature",
      value: summary.avg_temperature,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="
            bg-white rounded-xl
            border border-slate-200
            p-6 shadow-sm
            hover:shadow-lg hover:scale-[1.02]
            transition
          "
        >
          <p className="text-sm text-slate-500 mb-2">
            {stat.label}
          </p>
          <p className="text-3xl font-semibold text-slate-800">
            {stat.value}
          </p>
        </div>
      ))}
    </div>
  );
}

export default Summary;
