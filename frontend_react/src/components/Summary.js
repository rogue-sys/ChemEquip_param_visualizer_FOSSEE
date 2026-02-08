import React from "react";

function Summary({ summary }) {
  return (
    <div>
      <h3>Summary</h3>
      <p>Total Equipment: {summary.total_count}</p>
      <p>Avg Flowrate: {summary.avg_flowrate}</p>
      <p>Avg Pressure: {summary.avg_pressure}</p>
      <p>Avg Temperature: {summary.avg_temperature}</p>
    </div>
  );
}

export default Summary;
