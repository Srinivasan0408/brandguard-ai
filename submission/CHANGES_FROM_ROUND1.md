# CHANGES FROM ROUND 1
## BrandGuard AI — Team: TECHSPARKZ

---

## 1. Evolution from Concept to Working Codebase

In Round 1, BrandGuard AI was presented as a high-level architectural proposal, problem analysis, and wireframe blueprint for automated brand governance.

In Round 2: The Build, **the complete end-to-end platform was engineered into functional software**:

| Aspect | Round 1 (Proposal & Concept) | Round 2 (Implemented Application) |
|---|---|---|
| **System State** | Conceptual architecture, slides, mockups | Fully functional web application with live React frontend and FastAPI backend. |
| **Review Engine** | Theoretical algorithmic flow | Working multi-pipeline review engine checking terminology, facts, claims, tone, and accessibility. |
| **Approved Facts** | Fictional specification examples | Operational Approved Facts Registry with real deterministic price mismatch detection and source citation. |
| **Approval Workflow** | Flowchart diagram | Enforced multi-state workflow (`draft` &rarr; `in_review` &rarr; `changes_requested` &rarr; `approved`) with backend RBAC. |
| **Revision History** | Concept of version tracking | Stored snapshot revisions (`v1`, `v2`, etc.) with diff inspection and audit event trail. |
| **Governance Metrics** | Static sample dashboard charts | Real-time governance metrics calculated strictly from stored database review runs. |
| **Persistence** | Planned database schema | Implemented dual-persistence layer: Supabase PostgreSQL schema with RLS + self-contained SQLite demo mode. |
| **Testing** | Conceptual test plan | 12 automated Pytest test suites executing against real endpoints with 100% pass rate. |

---

## 2. Key Architectural Decisions Made in Round 2

1. **Separation of Deterministic Rules from LLMs**:
   - Rather than relying solely on non-deterministic generative models that can hallucinate facts, Round 2 established a strict deterministic foundation for pricing and terminology. This guarantees 100% reproducibility and legal safety.

2. **Zero-Setup Local Persistence**:
   - Implemented an intelligent database abstraction layer. If Supabase credentials are not supplied, BrandGuard AI transparently boots a pre-seeded local SQLite database so evaluators can test immediately without configuration barriers.

3. **Interactive Human-in-the-Loop Corrections**:
   - Added 1-click correction application directly within finding cards, generating immediate new revision snapshots and re-evaluating compliance in real time.
