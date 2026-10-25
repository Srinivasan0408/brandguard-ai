# KNOWN LIMITATIONS AND SCOPE DISCLOSURES
## BrandGuard AI — Team: TECHSPARKZ

In accordance with Hackathon engineering principles and Responsible AI guidelines, the TECHSPARKZ team explicitly discloses the known limitations and boundaries of the Round 2 MVP:

---

### 1. Visual Brand Asset Analysis
- **Status in Round 2**: Automated computer vision (logo integrity, clear-space verification, color palette extraction) is currently **unavailable**.
- **Responsible AI Disclosure**: The application does not simulate or fake image recognition. When images are referenced, the engine evaluates submitted metadata (such as descriptive alternative text) rather than claiming computer vision capabilities. Visual asset analysis is scheduled for Round 3 (Improvement 2).

### 2. Document Format Support
- **Supported Formats**: `.txt`, `.md`, and `.markdown`.
- **Limitation**: PDF and DOCX binary parsing is currently not enabled to prevent encoding corruption, formatting loss, or sandbox security risks. Content from PDFs or Word documents can be easily pasted directly into the text editor or uploaded as markdown.

### 3. Automated Accessibility Coverage
- **Scope**: The engine checks for empty alternative text, non-descriptive alt text length, and vague link anchors ("click here").
- **Limitation**: These checks represent foundational digital accessibility hygiene and do **not** constitute complete WCAG 2.2 AA certification.

### 4. Deterministic Fact Scope
- **Limitation**: Fact contradiction checks operate strictly against explicitly registered records in the Approved Facts Registry (e.g., NovaTech Pro pricing, warranty, battery life). The system does not claim to crawl or verify unconfigured external internet sources.

### 5. Multi-User Authentication in Demo Mode
- **Current Behavior**: In local demo mode, role switching between "Creator" and "Reviewer" is simulated via an interactive toggle in the navigation bar to allow judges to test both permissions without registering separate accounts. In production mode, Supabase Auth and Row Level Security enforce authenticated user boundaries.
