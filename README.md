# CareerLens

CareerLens is an AI powered resume analysis and interview preparation app. Upload a text based PDF resume, add a target job description, and get a structured view of your fit, skill gaps, role suggestions, actionable resume feedback, and interview questions tailored to the role.

[Try the live app](https://careerlens-eosin.vercel.app/) · [Watch the walkthrough](https://www.youtube.com/watch?v=BPuIvwDfkkw) · [Source repository](https://github.com/AyushPawshe08/CareerLens2)

![CareerLens landing page](assets/hero.png)

![CareerLens resume analysis screen](assets/analysis.png)

## Features

- Resume to job description match score, summary, matched and missing skills, suggested roles, and specific recommendations.
- Technical, HR, and behavioral interview questions with difficulty and a reason for each question.
- Account registration and login with JWT authentication.
- Saved analysis history, scoped to the signed in user.
- PDF text extraction and input validation (up to 2 pages and 5 MB by default).
- Structured LLM output through LangChain, with Groq as the primary provider and Gemini as the fallback.

## Architecture

![CareerLens system architecture](assets/architecture.png)

The React client sends the PDF and job description to the FastAPI service. The backend extracts and trims text, then a LangGraph workflow runs resume analysis and question generation concurrently. LangChain requests schema-constrained results from Groq, falling back to Gemini if needed. The API returns the results and saves them with the user's history in PostgreSQL. Authentication and history endpoints use JWTs.

## Tech stack

| Area | Technology | Role |
| --- | --- | --- |
| Frontend | React 19, Vite, React Router, Axios | UI, navigation, and API requests |
| API | Python 3.11+, FastAPI, Uvicorn, Pydantic | REST endpoints, validation, and schemas |
| AI workflow | LangGraph, LangChain, Groq, Google Gemini | Parallel analysis and interview question generation |
| Data | PostgreSQL, SQLAlchemy async, asyncpg | Users and saved analysis history |
| Auth and files | JWT, Argon2, pypdf | Protected endpoints, password hashing, and PDF text extraction |

## Run locally

Prerequisites: Python 3.11 or later, Node.js with npm, and a PostgreSQL database that accepts SSL connections. LLM provider keys are required for analysis. The supplied defaults use Groq with Gemini as fallback.

1. Clone the repository and enter the project directory.

   ```bash
   git clone https://github.com/AyushPawshe08/CareerLens2.git
   cd CareerLens2
   ```

2. Configure and start the backend. From `server/`, copy the example file to `.env` (PowerShell: `Copy-Item .env.example .env`; macOS/Linux: `cp .env.example .env`), then set the database URL, JWT secret, and provider keys in `.env`.

   ```bash
   cd server
   python -m venv .venv
   # Activate it: Windows: .venv\Scripts\activate
   #              macOS/Linux: source .venv/bin/activate
   python -m pip install -r requirements.txt
   uvicorn main:app --reload
   ```

   The API runs at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`. The service creates its database tables on startup.

3. In a second terminal, install and run the frontend.

   ```bash
   cd client
   npm install
   npm run dev
   ```

   Open the local URL printed by Vite. The client defaults to `http://localhost:8000` for its API. Set `VITE_API_BASE_URL` in `client/.env` only if your backend uses a different URL.

## Environment variables

Backend variables are documented in [`server/.env.example`](server/.env.example). Replace the example values with your own secrets and service URLs; never commit `.env` files.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async PostgreSQL URL, e.g. `postgresql+asyncpg://user:password@host:5432/dbname`; the database connection must support SSL. |
| `JWT_SECRET_KEY` | Yes | Secret used to sign access tokens. Use a random secret for local development and a secure secret in deployment. |
| `GROQ_API_KEY` | Yes with default provider | Groq credentials for the primary LLM. |
| `GOOGLE_API_KEY` | Recommended | Gemini credentials for the configured fallback provider. |
| `JWT_ALGORITHM` | No | Token signing algorithm; defaults to `HS256`. |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token lifetime; defaults to `1440`. |
| `ENVIRONMENT`, `DEBUG` | No | Backend environment and debug settings. |
| `VITE_API_BASE_URL` | No | Frontend API origin; defaults to `http://localhost:8000`. Configure in `client/.env` for a non-default backend. |

Additional LLM and input-size settings, including `PRIMARY_PROVIDER`, `FALLBACK_PROVIDERS`, `GROQ_MODEL`, `GEMINI_MODEL`, `MAX_RESUME_PAGES`, and `MAX_UPLOAD_SIZE_MB`, have defaults in `server/core/config.py`. The Pydantic settings loader reads environment variables case-insensitively.

## Use the API

Register or log in to receive a bearer token, then send it with an analysis request. `resume` must be a PDF and `job_description` must contain at least 20 characters.

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "resume=@resume.pdf;type=application/pdf" \
  -F "job_description=Paste the target role requirements here..."
```

Other endpoints include `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `GET /api/history`, `GET /api/history/{id}`, and `GET /health`.

## Project layout

```text
assets/                 UI, analysis, and architecture images
client/src/pages/       Landing, auth, analysis, and history screens
client/src/components/  Shared UI and analysis result components
client/src/api/         Axios client and API calls
server/api/             FastAPI auth, analysis, and history routes
server/graph/           LangGraph workflow, PDF preprocessing, and LLM agents
server/models/          Pydantic schemas and SQLAlchemy models
server/core/            Settings, database, and security
```

## Limitations and next steps

- Analysis is generated by LLMs and should be treated as guidance, not a hiring decision or a verified ATS score.
- The extractor handles text based PDFs; scanned/image-only PDFs are rejected. Resumes are limited to 2 pages, 5 MB, and 8,000 extracted characters by default; job descriptions are trimmed to 4,000 characters.
- Analysis quality and response time depend on the configured model providers. The Gemini fallback must also have a valid key to be usable.
- Useful next steps include reducing token use and response time, adding operational observability and stronger automated coverage, and generating concise last-minute interview notes.

