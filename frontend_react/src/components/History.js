import React from "react";

function History({ history }) {
  return (
    <div>
      <h3>Upload History (Last 5)</h3>
      <table border="1">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Uploaded At</th>
          </tr>
        </thead>
        <tbody>
          {history.map((item) => (
            <tr key={item.id}>
              <td>{item.filename}</td>
              <td>{item.uploaded_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default History;
