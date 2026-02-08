import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import API, { setAuthToken } from "../services/api";
import "../styles/Auth.css";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await API.post(
        "login/",
        new URLSearchParams({ username, password })
      );

      const token = res.data.token;
      localStorage.setItem("token", token);
      setAuthToken(token);
      onLogin();
      navigate("/dashboard");
    } catch {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Welcome Back</h2>

        <form onSubmit={handleLogin}>
          <input
            className="auth-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <div className="password-wrapper">
            <input
              className="auth-input"
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <span
              className="show-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "Hide" : "Show"}
            </span>
          </div>

          <button className="auth-btn" type="submit">
            Login
          </button>
        </form>

        {error && <div className="auth-error">{error}</div>}

        <div className="auth-footer">
          New user?{" "}
          <span className="auth-link" onClick={() => navigate("/register")}>
            Create an account
          </span>
        </div>
      </div>
    </div>
  );
}

export default Login;
