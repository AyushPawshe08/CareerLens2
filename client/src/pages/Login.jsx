import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/analyze");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-centered">
      <div className="auth-card-wrapper">
        <form className="card auth-card" onSubmit={handleSubmit}>
          <div className="auth-header">
            <div className="auth-icon-circle">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                <polyline points="10 17 15 12 10 7"></polyline>
                <line x1="15" y1="12" x2="3" y2="12"></line>
              </svg>
            </div>
            <h1 className="auth-title">Welcome back</h1>
            <p className="auth-subtitle">Sign in to access your analyses and interview preps</p>
          </div>

          {error && (
            <div className="form-error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="login-email">Email address</label>
            <input
              id="login-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="btn-primary btn-auth-submit" disabled={loading}>
            {loading ? (
              <span className="btn-loading-flex">
                <span className="btn-spinner"></span>
                <span>Signing in...</span>
              </span>
            ) : (
              "Sign in"
            )}
          </button>

          <div className="auth-footer">
            <p className="muted-text">
              Don't have an account?{" "}
              <Link to="/register" className="auth-link">
                Create an account
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}