import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getHistoryList } from "../api/client";

export default function History() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    getHistoryList()
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load your history.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function getScoreBadgeClass(score) {
    if (score == null) return "score-badge-neutral";
    if (score >= 80) return "score-badge-emerald";
    if (score >= 60) return "score-badge-purple";
    return "score-badge-amber";
  }

  return (
    <div className="page history-page">
      <div className="page-header history-header">
        <div>
          <span className="card-badge">APPLICATION ARCHIVE</span>
          <h1 className="page-title">Analysis History</h1>
          <p className="page-subtitle">
            Review your past resume analyses, score trends, and tailored interview questions.
          </p>
        </div>
        <Link to="/analyze" className="btn-primary btn-header-action">
          + New Analysis
        </Link>
      </div>

      <div className="card history-card">
        {loading && (
          <div className="loading-state-container">
            <div className="spinner"></div>
            <p className="muted-text">Loading your past analyses...</p>
          </div>
        )}

        {error && (
          <div className="form-error-banner">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="empty-state-box">
            <div className="empty-state-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <circle cx="12" cy="14" r="3"></circle>
                <line x1="12" y1="2" x2="12" y2="4"></line>
              </svg>
            </div>
            <h3>No analyses yet</h3>
            <p className="muted-text">
              Run your first resume analysis to compare your qualifications against any job description.
            </p>
            <Link to="/analyze" className="btn-primary btn-empty-cta">
              Run Your First Analysis &rarr;
            </Link>
          </div>
        )}

        {!loading && items.length > 0 && (
          <ul className="history-list">
            {items.map((item) => (
              <li key={item.id} className="history-list-item">
                <Link to={`/history/${item.id}`} className="history-item">
                  <div className="history-item-main">
                    <h3 className="history-summary">{item.summary}</h3>
                    <div className="history-item-meta">
                      <span className="history-date">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <circle cx="12" cy="12" r="10"></circle>
                          <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        {new Date(item.created_at).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                  </div>

                  <div className="history-item-right">
                    {item.match_score != null && (
                      <div className={`score-badge ${getScoreBadgeClass(item.match_score)}`}>
                        <span className="score-val">{item.match_score}</span>
                        <span className="score-denom">/100</span>
                      </div>
                    )}
                    <span className="history-arrow" aria-hidden="true">&rarr;</span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}