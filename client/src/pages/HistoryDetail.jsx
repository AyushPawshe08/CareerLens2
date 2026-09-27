import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getHistoryItem } from "../api/client";
import AnalysisResult from "../components/AnalysisResult";

export default function HistoryDetail() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [jdExpanded, setJdExpanded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    getHistoryItem(id)
      .then((data) => {
        if (!cancelled) setItem(data);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err.response?.status === 404) {
          setError("This history item doesn't exist or isn't yours.");
        } else {
          setError("Could not load this analysis.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return (
    <div className="page history-detail-page">
      <div className="detail-navigation">
        <Link to="/history" className="back-link">
          <span className="back-arrow">&larr;</span> Back to History
        </Link>
      </div>

      {loading && (
        <div className="card loading-state-container">
          <div className="spinner"></div>
          <p className="muted-text">Loading analysis details...</p>
        </div>
      )}

      {error && (
        <div className="card">
          <div className="form-error-banner">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {item && (
        <>
          <div className="card history-detail-header-card">
            <div className="detail-header-top">
              <div>
                <span className="card-badge">PAST APPLICATION RECORD</span>
                <h1 className="page-title">{item.summary || "Analysis Overview"}</h1>
              </div>
              <div className="detail-date-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span>
                  {new Date(item.created_at).toLocaleDateString(undefined, {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
            </div>

            <div className="jd-preview-section">
              <div className="jd-section-header">
                <h3>Target Job Description</h3>
                <button
                  type="button"
                  className="btn-toggle-jd"
                  onClick={() => setJdExpanded(!jdExpanded)}
                >
                  {jdExpanded ? "Collapse" : "Show Full Description"}
                </button>
              </div>
              <div className={`jd-preview ${jdExpanded ? "jd-preview-expanded" : ""}`}>
                {item.job_description}
              </div>
            </div>
          </div>

          <AnalysisResult
            resumeAnalysis={item.resume_analysis}
            interviewQuestions={item.interview_questions}
            errors={[]}
          />
        </>
      )}
    </div>
  );
}