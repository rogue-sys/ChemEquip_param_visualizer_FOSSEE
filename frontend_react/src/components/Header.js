import React from "react";
import { useNavigate } from "react-router-dom";

function Header() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    window.location.reload();
  };

  return (
    <div style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "15px 30px",
      background: "#1f2937",
      color: "white"
    }}>
      <h3 style={{ cursor: "pointer" }} onClick={() => navigate("/dashboard")}>
        Chemical Visualizer
      </h3>

      <div>
        <button onClick={() => navigate("/history")}
          style={{ marginRight: "15px" }}>
          History
        </button>
        <button onClick={logout}>Logout</button>
      </div>
    </div>
  );
}

export default Header;
