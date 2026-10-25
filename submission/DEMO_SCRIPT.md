# BRANDGUARD AI — HACKATHON DEMO EVALUATION SCRIPT
## Team: TECHSPARKZ &bull; Tagline: Create Freely. Publish Confidently.

This walk-through script guides a hackathon judge through the complete end-to-end governance lifecycle in under 5 minutes.

---

### Step 1: Open the Application
1. Start the application locally or open the live deployment URL.
2. The judge arrives at the **Overview Dashboard** (`http://localhost:5173`).
3. Notice the dark-navy enterprise cybersecurity aesthetic, real-time KPI metrics cards, and the prompt offering to load sample demonstration data.

---

### Step 2: Inspect Brand Guidelines
1. In the left navigation, click **Brand Guidelines**.
2. Inspect the pre-configured fictional brand **NovaTech**:
   - Preferred Tone: *"Professional, clear, helpful, and trustworthy."*
   - Approved Terminology: `NovaTech Pro`, `NovaTech AI Suite`, `QuantumSync`, `ZeroTrust Cloud`.
   - Prohibited Terminology: `cheap`, `unbreakable`, `foolproof`, `magic solution`, `hack-proof`, `100% secure`.
   - Mandatory Disclaimers: *"Enterprise security powered by NovaTech"*, *"Terms & conditions apply"*.
3. Add a custom prohibited word (e.g. `miraculous`) or click **Save Guidelines** to see persistence in action.

---

### Step 3: Inspect the Approved Facts Registry
1. In the left navigation, click **Approved Facts**.
2. Notice the verified ground truth records:
   - **Product**: NovaTech Pro &bull; **Attribute**: Price &bull; **Approved Value**: `₹4,999`
   - **Product**: NovaTech Pro &bull; **Attribute**: Warranty &bull; **Approved Value**: `12 months`
   - **Product**: NovaTech AI Suite &bull; **Attribute**: Deployment Time &bull; **Approved Value**: `under 15 minutes`
3. Notice the explicit disclosure explaining how deterministic fact matching works without hallucination.

---

### Step 4: Run a Brand Compliance Review (Non-Compliant Sample)
1. Click **Content Review** in the navigation bar.
2. Under "Hackathon Quick-Demonstration Presets", click **"High-Risk Non-Compliant Campaign"**.
3. Notice how the form instantly populates with problematic copy:
   - Incorrect price: `₹5,999` instead of `₹4,999`
   - Prohibited buzzword: `cheap`
   - Unapproved product name: `Nova Pro`
   - Unsupported absolute guarantee: `100% guaranteed results`
   - Hyperbolic claim: `the best in the world`
   - Missing required disclaimer: `Enterprise security powered by NovaTech`
4. Click the cyan **"Run Brand Compliance Review"** button.
5. In under 250ms, the review results appear on the right side:
   - Notice the **Critical Finding**: Approved Fact Contradiction (*"Detected price '₹5,999' directly contradicts approved price '₹4,999' for NovaTech Pro"*).
   - Notice the source citation: *NovaTech Official Q4 Product Catalog & Pricing Matrix*.
   - Notice findings for prohibited terms, unsupported guarantees, and missing disclaimers.

---

### Step 5: Interactively Apply Corrections
1. On the price contradiction finding card, click **"Apply Correction"**.
2. Notice that the copy automatically updates from `₹5,999` to `₹4,999`, creating a new revision (**Rev #2**).
3. On the prohibited term finding ("cheap"), click **"Apply Correction"** to substitute "cost-effective".
4. Notice how critical violations drop to zero as corrections are accepted.

---

### Step 6: Test Document Upload
1. Click **Import .txt / .md** at the top right of the submission card.
2. Select any local `.txt` or `.md` file to see instant text ingestion with file validation.

---

### Step 7: Submit Content for Human Review
1. Click **"Submit for Human Review"**.
2. The item status transitions from `Draft` &rarr; `In Review`.
3. Notice the **Review Queue** tab in the sidebar now displays a badge counter (`1`).

---

### Step 8: Reviewer Cockpit & RBAC Enforcement
1. In the top navigation bar, toggle the simulated role from **Creator** to **Reviewer**.
2. Click **Review Queue** in the sidebar.
3. Select the pending item:
   - Inspect the copy, revision level, and engine findings.
   - Enter feedback in the Reviewer Decision Notes box (e.g. *"Approved after price adjustment."*).
   - Click the green **"Approve Content"** button.
4. The item status changes to `Approved`.
5. *(Optional RBAC Test)*: Switch back to "Creator" and try approving another item. Notice the warning banner informing the user that approvals are restricted to authorized reviewers.

---

### Step 9: Audit Trail & Revision History
1. Click **Review History** in the navigation bar.
2. Select the approved item:
   - Inspect the side-by-side revision snapshots (Rev #1 vs Rev #2).
   - Scroll down to the **Chronological Governance Event Log** to see timestamps, actor identities (`Alice Creator`, `Bob Reviewer`), and status transitions.

---

### Step 10: Governance Insights & Analytics
1. Click **Governance Insights** in the navigation bar.
2. Observe real analytics computed from actual review records:
   - Total Evaluated Runs & Intercepted Violations.
   - Breakdown of issue categories (Facts, Terminology, Claims, Accessibility).
   - Most frequent repeated mistakes identified across team submissions.
   - Empirically derived guideline clarification suggestions.

---

### Step 11: System Settings & Reset
1. Click **Settings** in the navigation bar.
2. Inspect system diagnostics, database connection type, and review engine status.
3. Click **Reset Demonstration Data** to clean the database back to initial defaults at any time.
