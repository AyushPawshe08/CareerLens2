import { useState } from "react";

export default function AnalysisResult({ resumeAnalysis, interviewQuestions, errors }) {
  if (!resumeAnalysis && !interviewQuestions) return null;

  const score = resumeAnalysis?.match_score ?? null;

  // Determine score status tier and color
  let scoreClass = "score-purple";
  let scoreLabel = "Moderate Fit";
  if (score !== null) {
    if (score >= 80) {
      scoreClass = "score-emerald";
      scoreLabel = "Strong Match";
    } else if (score < 60) {
      scoreClass = "score-amber";
      scoreLabel = "Growth Opportunity";
    }
  }

  // Calculate SVG stroke offset for a circle radius of 42 (circumference ~ 264)
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset =
    score !== null ? circumference - (score / 100) * circumference : circumference;

  return (
    <div className="results-container">
      {/* Errors or Warnings Banner */}
      {errors?.length > 0 && (
        <div className="card warning-card">
          <div className="warning-header">
            <span className="warning-icon">⚠️</span>
            <strong>Analysis Notice</strong>
          </div>
          <div className="warning-list">
            {errors.map((e, i) => (
              <p key={i} className="warning-item">
                {e}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Resume Analysis Card */}
      {resumeAnalysis && (
        <div className="card result-card">
          <div className="result-card-header">
            <div>
              <span className="card-badge">EVALUATION REPORT</span>
              <h2 className="result-heading">Resume Analysis</h2>
            </div>
            {score !== null && (
              <span className={`status-pill ${scoreClass}`}>{scoreLabel}</span>
            )}
          </div>

          {/* Visual Score Gauge + Summary Section */}
          {score !== null && (
            <div className="score-overview-section">
              <div className="score-ring-wrapper">
                <svg className="score-ring-svg" width="110" height="110" viewBox="0 0 100 100">
                  <circle
                    className="score-ring-bg"
                    cx="50"
                    cy="50"
                    r={radius}
                  />
                  <circle
                    className={`score-ring-progress ${scoreClass}`}
                    cx="50"
                    cy="50"
                    r={radius}
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                  />
                </svg>
                <div className="score-ring-content">
                  <span className="score-number">{score}</span>
                  <span className="score-max">/100</span>
                </div>
              </div>

              <div className="score-summary-content">
                <h3 className="score-title">Role Match Score</h3>
                <p className="analysis-summary-text">{resumeAnalysis.summary}</p>
              </div>
            </div>
          )}

          {/* If there was no score but a summary exists */}
          {score === null && resumeAnalysis.summary && (
            <p className="analysis-summary-text">{resumeAnalysis.summary}</p>
          )}

          {/* Skill Breakdown Grid */}
          <div className="skills-layout-grid">
            <SkillBadgeSection
              title="Matched Skills"
              items={resumeAnalysis.matched_skills}
              type="matched"
              icon="✓"
            />
            <SkillBadgeSection
              title="Missing / Skill Gaps"
              items={resumeAnalysis.missing_skills}
              type="missing"
              icon="!"
            />
            <SkillBadgeSection
              title="Suggested Roles"
              items={resumeAnalysis.suggested_roles}
              type="suggested"
              icon="✦"
            />
          </div>

          {/* Recommendations Section */}
          {resumeAnalysis.recommendations?.length > 0 && (
            <div className="recommendations-box">
              <h3 className="sub-heading">
                <span className="sub-heading-icon">💡</span> Strategic Recommendations
              </h3>
              <ul className="recommendations-list">
                {resumeAnalysis.recommendations.map((rec, i) => (
                  <li key={i} className="recommendation-item">
                    <span className="rec-bullet-num">{i + 1}</span>
                    <span className="rec-text">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Interview Questions Card */}
      {interviewQuestions && (
        <div className="card result-card">
          <div className="result-card-header">
            <div>
              <span className="card-badge">PRACTICE SUITE</span>
              <h2 className="result-heading">Tailored Interview Questions</h2>
            </div>
            <p className="muted-text section-desc">
              Practice answering these targeted questions formulated directly from your background and the role requirements.
            </p>
          </div>

          <div className="questions-container">
            <QuestionCategory
              title="Technical & Role Specific"
              tag="Technical"
              color="tech"
              questions={interviewQuestions.technical}
            />
            <QuestionCategory
              title="Behavioral & Situational"
              tag="Behavioral"
              color="behavioral"
              questions={interviewQuestions.behavioral}
            />
            <QuestionCategory
              title="Culture & HR Expectations"
              tag="HR"
              color="hr"
              questions={interviewQuestions.hr}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function SkillBadgeSection({ title, items, type, icon }) {
  if (!items || items.length === 0) return null;
  return (
    <div className={`skill-category-box skill-box-${type}`}>
      <div className="skill-box-header">
        <span className="skill-type-icon">{icon}</span>
        <h4>{title}</h4>
        <span className="skill-count">{items.length}</span>
      </div>
      <div className="skill-pill-container">
        {items.map((skill, index) => (
          <span key={index} className={`skill-pill pill-${type}`}>
            {skill}
          </span>
        ))}
      </div>
    </div>
  );
}

function QuestionCategory({ title, tag, color, questions }) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="question-group">
      <div className="question-group-header">
        <h3 className="question-group-title">
          <span className={`category-dot dot-${color}`}></span>
          {title}
        </h3>
        <span className="question-count-badge">
          {questions.length} {questions.length === 1 ? "question" : "questions"}
        </span>
      </div>

      <div className="question-cards-list">
        {questions.map((q, i) => (
          <QuestionCard key={i} questionItem={q} index={i} tag={tag} />
        ))}
      </div>
    </div>
  );
}

function QuestionCard({ questionItem, index, tag }) {
  const [showInsight, setShowInsight] = useState(true);

  return (
    <div className="question-item-card">
      <div className="question-card-top">
        <div className="question-meta">
          <span className="question-index-chip">Q{index + 1}</span>
          <span className="question-category-tag">{tag}</span>
        </div>
        {questionItem.why_asked && (
          <button
            type="button"
            className="btn-toggle-insight"
            onClick={() => setShowInsight(!showInsight)}
            title="Toggle interview insight"
          >
            {showInsight ? "Hide Rationale" : "Why is this asked?"}
          </button>
        )}
      </div>

      <p className="question-title-text">{questionItem.question}</p>

      {questionItem.why_asked && showInsight && (
        <div className="question-insight-box">
          <div className="insight-label">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z"></path>
              <line x1="9" y1="21" x2="15" y2="21"></line>
            </svg>
            <span>Interviewer Insight</span>
          </div>
          <p className="insight-text">{questionItem.why_asked}</p>
        </div>
      )}
    </div>
  );
}