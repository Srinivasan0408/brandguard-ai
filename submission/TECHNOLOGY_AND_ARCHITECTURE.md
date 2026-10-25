# TECHNOLOGY AND ARCHITECTURE
## BrandGuard AI — Team: TECHSPARKZ

---

## 1. System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                              CLIENT BROWSER (UI/UX)                               |
|   React 19 + TypeScript + Vite + Tailwind CSS v4 + Lucide Icons                   |
|   • Overview Dashboard      • Content Review Cockpit      • Brand Hub             |
|   • Approved Facts Registry • Review Queue (RBAC)         • Revision History      |
|   • Governance Insights     • System Settings                                     |
+-----------------------------------------+-----------------------------------------+
                                          | REST API (JSON / Multipart)
                                          v
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND SERVICE                              |
|   Python 3.14 + FastAPI + Pydantic v2                                             |
|                                                                                   |
|   +-----------------------+   +-----------------------------------------------+   |
|   | API Routers           |   | Review Engine Orchestrator                    |   |
|   | • /health             |   | • Terminology Matcher (Regex Word Boundaries) |   |
|   | • /api/brands         |   | • Approved Facts & Price Contradiction Engine |   |
|   | • /api/facts          |   | • Promotional Claims & Risk Guardrails        |   |
|   | • /api/reviews        |   | • Tone & Composure Heuristics                 |   |
|   | • /api/insights       |   | • Digital Accessibility Verifier              |   |
|   | • /api/reset-demo     |   | • Mandatory Disclaimer Checker                |   |
|   +-----------+-----------+   +-----------------------+-----------------------+   |
+---------------|---------------------------------------|---------------------------+
                |                                       |
                v                                       v
+-------------------------------+       +-------------------------------------------+
|      PERSISTENCE LAYER        |       |        EXTERNAL LLM ADAPTER (OPTIONAL)     |
| • Supabase Managed PostgreSQL |       | • OpenAI / Google Gemini (via Env Vars)   |
| • Fallback Local SQLite DB    |       | • Graceful deterministic fallback when no |
| • RLS Policies & Audit Logs   |       |   API key is configured                   |
+-------------------------------+       +-------------------------------------------+
```

---

## 2. Technology Choices & Justification

| Layer | Technology | Version | Rationale |
|---|---|---|---|
| **Frontend Framework** | React + TypeScript | 19.x / 5.x | Type-safe enterprise UI development, rapid state synchronization, robust component architecture. |
| **Build Tool** | Vite | 8.x | Sub-second hot module replacement (HMR), optimized production bundling (`dist/` built in 1.38s). |
| **Styling** | Tailwind CSS + PostCSS | 4.x | Dark enterprise cybersecurity aesthetic (`#0a0f1d`), fine-grained contrast control, no unnecessary CSS bloat. |
| **Icons** | Lucide React | 1.x | Clean, accessible, modern SVG icon set for enterprise governance dashboards. |
| **Backend Framework** | FastAPI | 0.115.x | High-performance asynchronous Python web framework with native Pydantic validation and automatic OpenAPI documentation. |
| **Data Validation** | Pydantic | 2.8+ | Strict input/output schema validation, preventing malformed payloads and injection risks. |
| **Testing** | Pytest + HTTPX | 8.x / 0.28+ | Fast, robust integration and unit test suite verifying the review engine and RBAC enforcement. |
| **Primary Database** | Supabase PostgreSQL | 15+ | Enterprise relational storage with Row Level Security (RLS) policies, foreign keys, and indexes. |
| **Zero-Setup Database** | SQLite 3 | Built-in | Standalone relational persistence enabling judges to run and evaluate the application without requiring cloud credentials. |
| **AI Integration** | OpenAI / Gemini API | External | Optional tone and context evaluation with strict fallback to deterministic rules when keys are absent. |

---

## 3. Review Engine Architecture

The Review Engine (`backend/app/engine/reviewer.py`) operates as a pipeline of independent analysis stages:

1. **Brand Context Loader**: Retrieves active brand guidelines (tone, forbidden buzzwords, approved terms) and active verified facts.
2. **Terminology Pipeline**: Evaluates prohibited terms using boundary regexes (`\bterm\b`), preventing naive substring errors (e.g., "cheap" vs "cheapen").
3. **Fact Comparison Pipeline**: Extracts numerical and currency claims from the copy, compares against ground truth (e.g. ₹5,999 vs ₹4,999), and attaches source citations.
4. **Claims & Regulatory Pipeline**: Flags absolute performance guarantees ("100% guaranteed results"), "risk-free" claims, and superlatives.
5. **Tone Analysis Pipeline**: Analyzes capitalization patterns, aggressive urgency slang, and hype punctuation.
6. **Accessibility Pipeline**: Inspects media alt text completeness and hyperlink descriptive quality.
7. **Requirements Pipeline**: Verifies presence of mandatory corporate disclaimers and legal phrases.
8. **Severity Ranker**: Normalizes and prioritizes findings: Critical &rarr; High &rarr; Medium &rarr; Low &rarr; Informational.
