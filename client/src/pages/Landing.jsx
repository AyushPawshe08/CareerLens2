import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Landing() {
  const { isAuthenticated, loading } = useAuth();

  // If already logged in, redirect to /analyze
  if (loading) {
    return (
      <div className="page-centered">
        <div className="spinner"></div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/analyze" replace />;
  }

  return (
    <div className="landing-container">
      {/* Background Decorative Glow */}
      <div className="landing-glow" aria-hidden="true" />

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-badge">
          <span className="badge-sparkle">✦</span>
          <span>Next-Gen Career Intelligence</span>
        </div>

        <h1 className="hero-title">
          Land Your Target Role with <br />
          <span className="text-gradient">AI Resume & Interview Prep</span>
        </h1>

        <p className="hero-subtitle">
          CareerLens parses your resume against any job description in seconds.
          Detect critical skill gaps, calculate your real match score, and practice
          with tailored technical, behavioral, and HR interview questions.
        </p>

        <div className="hero-actions">
          <Link to="/register" className="btn-primary btn-large">
            Get Started Free &rarr;
          </Link>
          <Link to="/login" className="btn-secondary btn-large">
            Log In to Account
          </Link>
        </div>

        <div className="hero-proof-list">
          <div className="proof-item">
            <span className="proof-icon">✓</span> Free & instant analysis
          </div>
          <div className="proof-item">
            <span className="proof-icon">✓</span> Zero generic feedback
          </div>
          <div className="proof-item">
            <span className="proof-icon">✓</span> Deep JD role matching
          </div>
        </div>

        {/* Hero Product Preview Card */}
        <div className="hero-preview">
          <div className="preview-browser-bar">
            <div className="browser-dots">
              <span className="dot dot-red"></span>
              <span className="dot dot-yellow"></span>
              <span className="dot dot-green"></span>
            </div>
            <div className="browser-url">careerlens.app/analyze/preview</div>
          </div>

          <div className="preview-content">
            <div className="preview-header">
              <div className="preview-role-info">
                <span className="preview-tag">Senior Full-Stack Engineer</span>
                <h3>Match Report & Interview Breakdown</h3>
              </div>
              <div className="preview-score-circle">
                <span className="preview-score-num">88</span>
                <span className="preview-score-label">MATCH</span>
              </div>
            </div>

            <div className="preview-grid">
              <div className="preview-col">
                <div className="preview-label">Matched Skills</div>
                <div className="preview-tags">
                  <span className="tag-pill tag-matched">React</span>
                  <span className="tag-pill tag-matched">TypeScript</span>
                  <span className="tag-pill tag-matched">FastAPI</span>
                  <span className="tag-pill tag-matched">PostgreSQL</span>
                  <span className="tag-pill tag-matched">Docker</span>
                </div>

                <div className="preview-label" style={{ marginTop: "1rem" }}>
                  Missing / Key Gap Skills
                </div>
                <div className="preview-tags">
                  <span className="tag-pill tag-missing">Kafka</span>
                  <span className="tag-pill tag-missing">Kubernetes</span>
                </div>
              </div>

              <div className="preview-col">
                <div className="preview-label">Generated Interview Question</div>
                <div className="preview-qa-box">
                  <div className="preview-q-tag">TECHNICAL • SYSTEM DESIGN</div>
                  <p className="preview-q-text">
                    "How would you migrate a synchronous REST pipeline to an event-driven architecture using Kafka?"
                  </p>
                  <div className="preview-q-why">
                    <strong>Why this is asked:</strong> The job requires event-driven scaling, which isn't explicitly showcased on your resume.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-header">
          <span className="section-eyebrow">EFFORTLESS WORKFLOW</span>
          <h2 className="section-title">How CareerLens Works</h2>
          <p className="section-subtitle">
            Three simple steps to transform your raw resume into an interview-ready application.
          </p>
        </div>

        <div className="steps-grid">
          <div className="step-card">
            <div className="step-number">01</div>
            <div className="step-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="12" y1="18" x2="12" y2="12"></line>
                <line x1="9" y1="15" x2="15" y2="15"></line>
              </svg>
            </div>
            <h3>Upload Your Resume</h3>
            <p>
              Attach your PDF resume. Our extraction engine securely identifies your projects, skills, and work history.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">02</div>
            <div className="step-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                <path d="M9 12h6"></path>
                <path d="M9 16h6"></path>
              </svg>
            </div>
            <h3>Paste the Job Description</h3>
            <p>
              Paste the target job posting. CareerLens cross-references expectations, qualifications, and domain keywords.
            </p>
          </div>

          <div className="step-card">
            <div className="step-number">03</div>
            <div className="step-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
            </div>
            <h3>Get Analysis & Prep</h3>
            <p>
              Receive an instant match score, missing competencies list, and tailored technical, HR, and behavioral questions.
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <span className="section-eyebrow">BUILT FOR CANDIDATE SUCCESS</span>
          <h2 className="section-title">Everything You Need to Stand Out</h2>
          <p className="section-subtitle">
            Engineered to bridge the gap between your resume and what hiring teams actually look for.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon feature-icon-purple">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                <line x1="8" y1="11" x2="14" y2="11"></line>
              </svg>
            </div>
            <h3>Skill Gap Detection</h3>
            <p>
              Don't guess what's missing. Identify critical keywords, frameworks, and technologies required by the employer before applying.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon feature-icon-emerald">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <h3>Accurate Match Scoring</h3>
            <p>
              Get a quantitative 0-100 fit rating. Gauge how well your profile aligns with seniority requirements and core responsibilities.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon feature-icon-blue">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <h3>Tailored Interview Questions</h3>
            <p>
              Generate realistic Technical, Behavioral, and HR questions mapped to your background, plus explanations of why interviewers ask them.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon feature-icon-amber">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <h3>Saved History & Comparisons</h3>
            <p>
              Every report is automatically saved to your history. Revisit previous job applications, compare scores, and sharpen your prep anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="cta-banner-section">
        <div className="cta-banner">
          <h2>Ready to optimize your job hunt?</h2>
          <p>
            Create your account in seconds and run your first AI resume and interview analysis.
          </p>
          <div className="cta-banner-actions">
            <Link to="/register" className="btn-primary btn-large btn-cta-white">
              Create Free Account &rarr;
            </Link>
            <Link to="/login" className="btn-secondary btn-large btn-cta-outline">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="brand-logo-mark">⚡</span>
            <span className="footer-title">CareerLens</span>
            <p className="footer-tagline">
              AI resume analysis and tailored interview preparation.
            </p>
          </div>
          <div className="footer-links">
            <Link to="/login">Log in</Link>
            <Link to="/register">Sign up</Link>
            <a href="#how-it-works" onClick={(e) => {
              e.preventDefault();
              document.querySelector(".how-it-works-section")?.scrollIntoView({ behavior: "smooth" });
            }}>How It Works</a>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} CareerLens. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
