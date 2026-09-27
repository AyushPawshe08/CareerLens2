import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName);
      navigate("/analyze");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
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
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7.5" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="23" y1="11" x2="17" y2="11"></line>
              </svg>
            </div>
            <h1 className="auth-title">Create your account</h1>
            <p className="auth-subtitle">Start analyzing resumes and generating interview answers</p>
          </div>

          {error && (
            <div className="form-error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="reg-fullname">Full name</label>
            <input
              id="reg-fullname"
              type="text"
              placeholder="e.g. Alex Taylor"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="form-input"
              autoComplete="name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="reg-email">Email address</label>
            <input
              id="reg-email"
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
            <div className="form-label-header">
              <label htmlFor="reg-password">Password</label>
              <span className="label-hint">Min. 8 characters</span>
            </div>
            <input
              id="reg-password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="form-input"
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="btn-primary btn-auth-submit" disabled={loading}>
            {loading ? (
              <span className="btn-loading-flex">
                <span className="btn-spinner"></span>
                <span>Creating account...</span>
              </span>
            ) : (
              "Get Started Free"
            )}
          </button>

          <div className="auth-footer">
            <p className="muted-text">
              Already have an account?{" "}
              <Link to="/login" className="auth-link">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}