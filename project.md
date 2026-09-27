AI Resume Analyzer and Interview Preparation Platform 

Name :- Careerlens version 2

Architecture :-

User
 │
 ├── Resume PDF (max 2 pages)
 └── Job Description (text)
          │
          ▼
   Resume Text Extraction
          │
          ▼
 ┌──────────────────────────────┐
 │        LANGGRAPH             │
 │                              │
 │  START                       │
 │    ↓                         │
 │  Preprocess                  │
 │    ↓                         │
 │  Resume Analysis Agent       │
 │    ↓                         │
 │  ┌────────┬────────┬────────┐│
 │  │Technical│  HR   │Behavior││
 │  │Question │Questions│Questions│
 │  └────────┴────────┴────────┘│
 │    ↓                         │
 │  Final Response              │
 │    ↓                         │
 │  END                         │
 └──────────────────────────────┘
          │
          ▼
       Frontend

Features :-  
1. Resume Analyzer Agent
{
  "summary": "...",
  "matched_skills": ["Python", "SQL", "REST APIs"],
  "missing_skills": ["Docker"],
  "suggested_roles": ["Python Backend Developer"],
  "recommendations": [
    "Add measurable impact to project bullets"
  ]
}

2. Interview Question Generation Platform
{
    "technical" : [],
    "hr" : [],
    "behavorial" : []
}

Flow :-

1. Resume Flow

Resume + JD
     ↓
LangChain Prompt
     ↓
Groq LLM
     ↓
Structured Output
     ↓
ResumeAnalysis
     ↓
LangGraph State

2. Interview Q Flow
Resume
   +
JD
   +
Resume Analysis
        ↓
Interview Question Agent
        ↓
 ┌──────┼───────┐
 ↓      ↓       ↓
Tech    HR   Behavioral


Problems :-

1. Speed -> Cause we have to generate all the content using LLM so we are dependent on it
2. LLM token -> We have to optimize Token consumption
3. LLM failure -> If LLM fails for unidentified reason we have to add fallback LLM


Future Scope :-

1. Also add a Last minute notes generation using LLM where using resume and JD we will generate a last minute all possible notes but we have to take care of LLM tokens cause it may consume way too much tokens



