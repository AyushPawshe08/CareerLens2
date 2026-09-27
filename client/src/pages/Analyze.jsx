import { useState, useRef } from "react";
import { analyzeResume } from "../api/client";
import AnalysisResult from "../components/AnalysisResult";

export default function Analyze() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    if (!resumeFile) {
      setError("Please attach a resume PDF.");
      return;
    }
    if (jobDescription.trim().length < 20) {
      setError("Job description looks too short — paste the full JD.");
      return;
    }

    setLoading(true);
    try {
      const data = await analyzeResume({ resumeFile, jobDescription });
      setResult(data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === "string") {
        setError(detail);
      } else if (detail?.message) {
        // backend's 422 shape: { message, errors: [...] }
        setError([detail.message, ...(detail.errors || [])].join(" "));
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
        setResumeFile(file);
        setError("");
      } else {
        setError("Please upload a PDF document.");
      }
    }
  }

  function formatFileSize(bytes) {
    if (!bytes) return "";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
  }

  return (
    <div className="page analyze-page">
      <div className="page-header">
        <span className="card-badge">NEW ANALYSIS</span>
        <h1 className="page-title">Analyze Your Resume</h1>
        <p className="page-subtitle">
          Upload your resume and target job description to pinpoint skill gaps and generate role-tailored interview questions.
        </p>
      </div>

      <div className="card analyze-card">
        <form onSubmit={handleSubmit} className="analyze-form">
          {/* File Upload Area */}
          <div className="form-group">
            <label className="form-label-header">
              <span>Resume PDF</span>
              <span className="label-hint">PDF up to 2 pages</span>
            </label>

            <div
              className={`file-upload-dropzone ${isDragging ? "dropzone-active" : ""} ${
                resumeFile ? "dropzone-selected" : ""
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                className="file-input-hidden"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
              />

              {!resumeFile ? (
                <div className="dropzone-empty">
                  <div className="dropzone-icon-circle">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="17 8 12 3 7 8"></polyline>
                      <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                  </div>
                  <div className="dropzone-text-group">
                    <p className="dropzone-main-text">
                      <span className="upload-link-text">Click to choose a file</span> or drag and drop
                    </p>
                    <p className="dropzone-sub-text">PDF format only (max 2 pages)</p>
                  </div>
                </div>
              ) : (
                <div className="dropzone-filled">
                  <div className="file-info-badge">
                    <div className="file-icon-wrap">
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                      </svg>
                    </div>
                    <div className="file-details">
                      <span className="file-name">{resumeFile.name}</span>
                      <span className="file-size">{formatFileSize(resumeFile.size)}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="btn-change-file"
                    onClick={(e) => {
                      e.stopPropagation();
                      setResumeFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }}
                  >
                    Change file
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Job Description Textarea */}
          <div className="form-group">
            <div className="form-label-header">
              <label htmlFor="jd-input">Job description</label>
              <span className="label-hint">
                {jobDescription.length > 0 ? `${jobDescription.length} characters` : "Min 20 characters"}
              </span>
            </div>
            <textarea
              id="jd-input"
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the target job description here (responsibilities, required qualifications, key technologies)..."
              className="form-textarea"
            />
          </div>

          {error && (
            <div className="form-error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            className="btn-primary btn-submit-analyze"
            disabled={loading}
          >
            {loading ? (
              <span className="btn-loading-flex">
                <span className="btn-spinner"></span>
                <span>Analyzing Resume & Generating Questions...</span>
              </span>
            ) : (
              <span>Start Analysis & Interview Prep &rarr;</span>
            )}
          </button>
        </form>
      </div>

      {result && (
        <AnalysisResult
          resumeAnalysis={result.resume_analysis}
          interviewQuestions={result.interview_questions}
          errors={result.errors}
        />
      )}
    </div>
  );
}