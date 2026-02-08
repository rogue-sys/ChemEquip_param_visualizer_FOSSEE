import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import "../styles/Auth.css";

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [usernameExists, setUsernameExists] = useState(false);
  const [checking, setChecking] = useState(false);
  const [msg, setMsg] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    if (!username) return;

    const timer = setTimeout(async () => {
      try {
        setChecking(true);
        const res = await API.get(
          `check-username/?username=${username}`
        );
        setUsernameExists(res.data.exists);
      } catch {
        setUsernameExists(false);
      } finally {
        setChecking(false);
      }
    }, 600);

    return () => clearTimeout(timer);
  }, [username]);

  const handleRegister = async (e) => {
    e.preventDefault();
    setMsg("");

    if (usernameExists) {
      setMsg("Username already exists");
      return;
    }

    try {
      await API.post("register/", { username, password });
      setMsg("Account created! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch {
      setMsg("Registration failed. Try again.");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Create Account</h2>

        <form onSubmit={handleRegister}>
          <input
            className="auth-input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          {username && (
            <div className="username-status">
              {checking ? (
                "Checking availability..."
              ) : usernameExists ? (
                <span className="username-error">
                  Username already exists
                </span>
              ) : (
                <span className="username-ok">
                  Username available
                </span>
              )}
            </div>
          )}

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

          <button
            className="auth-btn"
            type="submit"
            disabled={usernameExists || checking}
          >
            Register
          </button>
        </form>

        {msg && (
          <div
            className={
              msg.includes("created") ? "auth-success" : "auth-error"
            }
          >
            {msg}
          </div>
        )}

        <div className="auth-footer">
          Already have an account?{" "}
          <span className="auth-link" onClick={() => navigate("/login")}>
            Login
          </span>
        </div>
      </div>
    </div>
  );
}

export default Register;
