# BRANDGUARD AI
## TechCircuit Hackathon — Round 2: The Build
### Team: TECHSPARKZ
### Tagline: *Create Freely. Publish Confidently.*
## TechCircuit Hackathon — Round 3 Final Build & Hardening
### Team: TECHSPARKZ &bull; Tagline: *Create Freely. Publish Confidently.*

---

## 1. Product Overview

**BrandGuard AI** is an intelligent enterprise brand governance and pre-publication compliance platform. It serves as an automated and human-in-the-loop compliance firewall to ensure content published across distributed marketing teams, agencies, and generative AI pipelines strictly adheres to approved brand guidelines, verified pricing, terminology standards, and visual brand assets.

---

## 2. Key Features & Completed Round 3 Hardening Improvements

### A. Password Security — Modern Argon2id & Transparent Migration (Improvement 1)
- **OWASP-Recommended Argon2id Implementation**: Upgraded password security using `argon2-cffi` configured with industry-standard parameters (`time_cost=3`, `memory_cost=65536` [64 MiB], `parallelism=4`, `hash_len=32`, `salt_len=16`).
- **Seamless Auto-Migration**: Legacy SHA-256 credentials verify in constant time, then automatically re-hash and upgrade to Argon2id in the database upon successful authentication with zero user disruption.
- **Timing Leak Protection**: Constant-time verification protecting against credential enumeration attacks.
- **Plaintext Safeguards**: Plaintext passwords are never stored, cached, or logged.

### B. Multi-Tenant Organization-Level Data Isolation (Improvement 2)
- **Multi-Tenant Schema**: Introduced `organizations` schema with seeded organizations (`org-novatech` and `org-apex`).
- **Data Scoping**: Associated `brands`, `approved_facts`, `content_items`, `visual_analyses`, `audit_logs`, and `users` with their respective `organization_id`.
- **Strict Server-Side Authorization**: Enforced `validate_org_access` across all routes. Cross-organization access, modification, or approval attempts return `HTTP 403 Forbidden`.
- **Enforced Role Permissions**:
  - `admin`: Manages team users, brand rules, approved facts, and reviews within their organization.
  - `reviewer`: Reviews submissions and executes approvals/change requests within their organization.
  - `creator`: Submits content, views guidelines/facts, and applies corrections. Forbidden from approving content or modifying brand guidelines.

### C. OCR-Based Visual Brand Analysis & Accessibility (Improvement 3)
- **Tesseract Canvas OCR**: Integrated OCR extraction via `pytesseract` supporting PNG, JPEG, and WebP marketing images.
- **Graphic Canvas Governance**: Analyzes extracted text against brand guidelines for prohibited terminology, pricing contradictions, unapproved naming abbreviations, and absolute promotional claims.
- **WCAG 2.2 AA Contrast Validation**: Calculates relative luminance and tonal contrast ratios between dominant foreground and background colors against the 4.5:1 standard.
- **Explicit Uncertainty Notes & Resilient Fallback**: Honest disclosure when OCR confidence is impacted by stylized typography or background gradients. Graceful fallback mode ensures color, contrast, and resolution analysis function seamlessly when Tesseract binaries are absent.

---

## 3. Technology Stack

- **Frontend**: React 19, TypeScript, Vite 8, Tailwind CSS v4, Lucide React icons.
- **Backend**: Python 3.14, FastAPI, Pydantic v2, Argon2id (`argon2-cffi`), PyJWT, Pillow (PIL), PyTesseract, Pytest, HTTPX, ReportLab.
- **Database**: SQLite 3 with WAL persistence + Supabase PostgreSQL schema with RLS policies.
- **Deployment Compatibility**: Frontend ready for Vercel; Backend ready for Render.

---

## 4. Quick Start (Run Locally)

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+ and pip

### Step 1: Clone and Configure Environment
```bash
git clone <repository-url>
cd "Brand govern"
cp .env.example .env
```

### Step 2: Start the FastAPI Backend Service
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Run the FastAPI server (starts on http://127.0.0.1:8000)
python backend/run.py
```
- API Documentation (Swagger): `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/health`

### Step 3: Start the React Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 5. Demo Accounts for Hackathon Judges

BrandGuard AI includes pre-seeded demonstration accounts with distinct RBAC permissions across organizations:

| Role | Username | Password | Organization | Permitted Actions |
|---|---|---|---|---|
| **Reviewer** | `reviewer` | `reviewer123` | NovaTech (`org-novatech`) | Approves content, requests changes, reviews queue |
| **Creator** | `creator` | `creator123` | NovaTech (`org-novatech`) | Creates drafts, runs reviews, applies corrections |
| **Administrator** | `admin` | `admin123` | NovaTech (`org-novatech`) | Full governance access across NovaTech rules & team |
| **Apex Admin** | `apex_admin` | `admin123` | Apex Corp (`org-apex`) | Multi-tenant test account for cross-org boundary verification |

---

## 6. Running Automated Tests

Run the full automated test suite containing 27 regression, Round 3, and hardening test scenarios:
```bash
python -m pytest backend/tests -v
```
**All 27 tests pass with a 100% pass rate in ~5.3 seconds.**

---

## 7. Main End-to-End Judge Journey

1. **Open Dashboard**: Visit `http://localhost:5173`. Observe real-time governance metrics and health status.
2. **Authenticate**: Click **Login** in the top navigation bar. Select the **Creator** demo account (`creator` / `creator123`). Notice Argon2id authentication.
3. **Inspect Brand Hub & Facts**: In the sidebar, navigate to **Brand Guidelines** and **Approved Facts** to review NovaTech's ground truth (NovaTech Pro price: ₹4,999; warranty: 12 months).
4. **Run Compliance Review**: Go to **Content Review**. Click the preset **"High-Risk Non-Compliant Campaign"** and click **Run Brand Compliance Review**.
5. **Inspect Evidence**: Observe the findings with linked fact IDs (`fact-novatech-001`), evidence statuses (*Ground-Truth Verified* vs *Insufficient Evidence*), and correction rationales.
6. **Apply Correction**: Click **Apply Correction** on the price contradiction finding. Notice that the text updates to ₹4,999 and creates **Rev #2**.
7. **Submit for Human Review**: Click **Submit for Human Review**. The content status updates to `In Review`.
8. **Test Visual Analysis & OCR**: In the sidebar, click **Visual Analysis**. Click **Load Sample Brand Banner** and click **Run Visual Consistency Analysis**. Observe dominant color swatches, palette harmony score, WCAG 2.2 AA contrast ratios, and the OCR canvas text & brand rule inspection panel.
9. **Log in as Reviewer**: Click the user profile pill &rarr; switch to **Reviewer** (`reviewer` / `reviewer123`).
10. **Review Queue Sign-Off**: Go to **Review Queue**, select the submitted post, enter feedback, and click **Approve Content**.
11. **Inspect Audit History**: In **Review History**, inspect the revision snapshots and the immutable governance event timeline.
12. **Multi-Tenant Boundary Test**: Log in as `apex_admin` and observe that NovaTech reviews and guidelines are completely isolated (`HTTP 403 Forbidden`).

---

## 8. Deployment Configuration

- **Frontend on Vercel**: Configured via [`vercel.json`](file:///c:/Users/srini/OneDrive/Documents/Brand%20govern/vercel.json).
- **Backend on Render**: Configured via [`render.yaml`](file:///c:/Users/srini/OneDrive/Documents/Brand%20govern/render.yaml).
- **Health Check**: Endpoint `GET /health` returns JSON status, database health, and review engine mode.

---

## 9. Product Roadmap

| Milestone | Status | Key Features |
|---|---|---|
| **Round 2** | Completed | Full-stack MVP, deterministic review engine, approved facts registry, human review queue, revision snapshots, audit history. |
| **Round 3** | Completed | Evidence-grounded traceability, deterministic visual asset analysis, WCAG 2.2 contrast checking, JWT authentication, server-side RBAC, and audit logs. |
| **Round 3 Final Hardening** | Completed | Modern Argon2id password security with on-login transparent migration, multi-tenant organization-level data isolation, OCR-based visual canvas brand rule checking, and 27 passing automated tests. |
| **Future Enterprise** | Planned | SAML 2.0 / Okta single sign-on integration, multi-signature approval quorums, and localized OCR models for non-Latin typography. |

---

## 10. Team Contributions (Team: TECHSPARKZ)

- **Full-Stack Lead**: Full-stack application architecture, multi-tenant scoping, FastAPI endpoints, React SPA components, and Vite bundling.
- **AI & Review Engine Engineer**: Boundary regex engines, fact contradiction comparator, OCR canvas rule validator, and Pillow/WCAG 2.2 visual analysis.
- **Security & QA Engineer**: OWASP Argon2id hashing & on-login migration, multi-tenant boundary checks, server-side RBAC enforcement, and 27-scenario automated test suite.
