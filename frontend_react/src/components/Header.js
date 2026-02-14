import React from "react";
import { useNavigate } from "react-router-dom";

function Header() {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    window.location.reload();
  };

  return (
    <header className="bg-gray-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        
        {/* App title */}
        <h3
          className="text-lg font-semibold cursor-pointer hover:text-gray-300 transition"
          onClick={() => navigate("/dashboard")}
        >
          Chemical Visualizer
        </h3>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/history")}
            className="
              px-4 py-2 rounded-lg
              bg-gray-800 hover:bg-gray-700
              transition text-sm
            "
          >
            History
          </button>

          <button
            onClick={logout}
            className="
              px-4 py-2 rounded-lg
              bg-red-600 hover:bg-red-500
              transition text-sm
            "
          >
            Logout
          </button>
        </div>

      </div>
    </header>
  );
}

export default Header;
