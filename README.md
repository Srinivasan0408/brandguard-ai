# BRANDGUARD AI
## TechCircuit Hackathon — Round 2: The Build
### Team: TECHSPARKZ
### Tagline: *Create Freely. Publish Confidently.*

---

## 1. Overview

**BrandGuard AI** is an intelligent enterprise brand governance and pre-publication compliance platform designed to ensure organizations publish marketing content, social media posts, and product communications that strictly align with approved brand guidelines, verified product facts, pricing matrices, and trademark standards.

---

## 2. Key Features

- **Brand Knowledge Hub**: Full configuration for fictional enterprise brand **NovaTech**, including tone, approved terminology tags, prohibited buzzwords, and mandatory disclaimers.
- **Approved Facts Registry**: Ground-truth facts registry comparing prices and product specs deterministically with source citations.
- **Content Submission & Ingestion**: Text submission, metadata tagging, and `.txt`/`.md`/`.markdown` document upload with file validation.
- **Demonstration Presets**: 1-click loading of realistic non-compliant and compliant sample posts for instant testing.
- **Multi-Pipeline Review Engine**: Terminology boundary regex matcher, fact contradiction detector, promotional claims guardrails, tone heuristics, accessibility checks, and disclaimer verification.
- **Interactive Corrections**: 1-click [Apply Correction] automatically rewrites text and generates versioned revision snapshots.
- **Human-in-the-Loop Review Queue**: Full review workflow (`draft` &rarr; `in_review` &rarr; `changes_requested` &rarr; `approved`) with role-based access control (RBAC).
- **Audit Trail & Revision History**: Immutable snapshot history (`v1`, `v2`, etc.) and chronological event timeline tracking all decisions and reviewer feedback.
- **Governance Insights**: Real-time analytics computed strictly from stored review records without fabricated statistics.
- **Zero-Setup Demo Persistence**: Self-seeding SQLite database ensures evaluators can test immediately without provisioning cloud database credentials.

---

## 3. Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide React icons.
- **Backend**: Python 3.14, FastAPI, Pydantic v2, Pytest, HTTPX.
- **Database**: Supabase PostgreSQL schema with Row Level Security (RLS) + Fallback local SQLite database for zero-setup offline evaluation.
- **Deployment Compatibility**: Frontend ready for Vercel; Backend ready for Render.

---

## 4. Quick Start (Run Locally)

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+ and pip

### Step 1: Clone and Setup Environment
```bash
git clone <repository-url>
cd "Brand govern"
cp .env.example .env
```

### Step 2: Start the Backend Service
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Run the FastAPI server (starts on http://127.0.0.1:8000)
python backend/run.py
```
*API documentation is available at `http://127.0.0.1:8000/docs`.*
*Health status endpoint is available at `http://127.0.0.1:8000/health`.*

### Step 3: Start the Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Running Automated Tests

Run the 12 automated test scenarios verifying the review engine, RBAC policies, and file validation:
```bash
python -m pytest backend/tests/test_brandguard.py -v
```
All 12 test scenarios pass with a 100% pass rate in ~2.8 seconds.

---

## 6. Environment Variables

| Variable | Description | Default / Example |
|---|---|---|
| `PORT` | Backend server port | `8000` |
| `ENVIRONMENT` | Runtime mode | `development` or `production` |
| `DEMO_MODE` | Enables pre-seeded demo mode | `true` |
| `SUPABASE_URL` | Supabase Cloud PostgreSQL endpoint (optional) | `https://xyz.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon Key (optional) | `eyJ...` |
| `OPENAI_API_KEY` | Optional OpenAI key for AI-assisted tone analysis | `sk-...` |
| `GEMINI_API_KEY` | Optional Gemini key for AI-assisted tone analysis | `AIza...` |
| `VITE_API_URL` | Frontend API URL for production deployment | `https://brandguard-api.onrender.com` |

---

## 7. Round 2 Submission Materials

The `submission/` folder contains the complete required documentation for Round 2:
1. `ROUND2_PROJECT_SUMMARY.md`: Executive summary and problem statement.
2. `COMPLETED_FEATURES.md`: Full catalog of implemented features.
3. `TECHNOLOGY_AND_ARCHITECTURE.md`: Architecture diagrams, component breakdown, and tech choices.
4. `CHANGES_FROM_ROUND1.md`: Specific progress and changes from Round 1.
5. `KNOWN_LIMITATIONS.md`: Honest technical boundaries and responsible AI disclosures.
6. `ROUND3_IMPROVEMENTS.md`: The exact three planned Round 3 engineering improvements.
7. `DEMO_SCRIPT.md`: Step-by-step 5-minute hackathon evaluation script.
8. `TEST_RESULTS.md`: Detailed test matrix and Pytest execution logs.
9. `BRANDGUARD_AI_ROUND2_REPORT.md` & `BRANDGUARD_AI_ROUND2_REPORT.pdf`: Complete updated project report suitable for judges.
