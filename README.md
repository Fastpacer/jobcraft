# 🤖 Multi-Agent Job Search System

An **AI-powered job search assistant** that uses a **multi-agent architecture** to discover jobs, analyze resumes, score job–candidate fit, and generate personalized outreach messages.

Unlike traditional job portals, this system focuses on **intelligent automation and reasoning**, not just keyword matching.

---

## ✨ Features

- **Resume Parsing**
  - Extracts structured information from raw resume text (TXT / PDF-ready)
  - Identifies skills, roles, experience, and summaries using LLM reasoning

- **Job Discovery**
  - Fetches real job listings using external APIs (e.g. SerpAPI)
  - Supports query and location-based searches

- **AI-Driven Matching**
  - Scores resume–job compatibility (0–100)
  - Uses LLM-based semantic reasoning instead of keyword overlap

- **Personalized Outreach**
  - Generates concise, tailored outreach messages
  - References specific resume skills and job requirements

- **Application Tracking**
  - Persists applications in a SQLite database
  - Enables future analytics and history views

- **User-Friendly Interface**
  - Streamlit frontend for interactive exploration
  - Adjustable thresholds and search parameters

- **API Backend**
  - FastAPI backend for scalable, reusable processing
  - Clean separation between frontend and intelligence layer

---

## 🏗️ Architecture

The system is built with a **modular, agent-based design**:

### 🧠 Agents
- `ResumeAgent` – Parses and structures resume data
- `JobDiscoveryAgent` – Finds jobs using external APIs
- `MatcherAgent` – Scores job–resume fit using LLM reasoning
- `OutreachAgent` – Generates personalized outreach messages
- `TrackerAgent` – Persists application data

### ⚙️ Backend
- **FastAPI** for API endpoints
- **Pydantic** for request/response validation
- **SQLAlchemy + SQLite** for persistence

### 🖥️ Frontend
- **Streamlit** UI
- Resume input, job search controls, fit scores, outreach previews

### 🤖 AI Integration
- **Groq LLMs** for:
  - resume understanding
  - fit scoring
  - message generation

### 🔁 Development Process
The system evolved iteratively:
- Started from simple scripts
- Refactored to resolve import/config issues
- Introduced schemas and agents
- Optimized prompts for stable, non-repetitive outputs

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone <repo-url>
cd <repo-name>
