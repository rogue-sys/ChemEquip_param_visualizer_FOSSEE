import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import SummaryPage from "./pages/SummaryPage";
import HistoryPage from "./pages/HistoryPage";
import Header from "./components/Header";

import { setAuthToken } from "./services/api";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setAuthToken(token);
      setLoggedIn(true);
    }
  }, []);

  return (
  <BrowserRouter>
    <div className="min-h-screen bg-gradient-to-br from-slate-800 via-slate-700 to-blue-900">

      {loggedIn && <Header />}

      <Routes>
        <Route
          path="/login"
          element={
            loggedIn ? (
              <Navigate to="/dashboard" />
            ) : (
              <Login onLogin={() => setLoggedIn(true)} />
            )
          }
        />

        <Route
          path="/register"
          element={loggedIn ? <Navigate to="/dashboard" /> : <Register />}
        />

        <Route
          path="/dashboard"
          element={loggedIn ? <Dashboard /> : <Navigate to="/login" />}
        />

        <Route
          path="/summary/:id"
          element={loggedIn ? <SummaryPage /> : <Navigate to="/login" />}
        />

        <Route
          path="/history"
          element={loggedIn ? <HistoryPage /> : <Navigate to="/login" />}
        />

        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </div>
  </BrowserRouter>
);

}

export default App;
