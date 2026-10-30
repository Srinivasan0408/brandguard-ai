import json
import sqlite3
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from ..config import settings
from .seed_data import (
    SAMPLE_BRAND,
    SAMPLE_FACTS,
    SAMPLE_DEMO_POSTS,
    NOVATECH_BRAND_ID,
    SAMPLE_USERS,
    SAMPLE_ORGANIZATIONS,
    SAMPLE_APEX_BRAND
)

class Database:
    def __init__(self, db_path: str = "brandguard.db"):
        self.db_path = db_path
        self._init_sqlite()
        self._seed_if_empty()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                organization_id TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                username TEXT NOT NULL,
                organization_id TEXT NOT NULL DEFAULT 'org-novatech',
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                created_at TEXT NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS visual_analyses (
                id TEXT PRIMARY KEY,
                brand_id TEXT NOT NULL,
                organization_id TEXT NOT NULL DEFAULT 'org-novatech',
                user_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                dimensions TEXT NOT NULL,
                format TEXT NOT NULL,
                dominant_colors TEXT NOT NULL,
                palette_compliance_score REAL NOT NULL,
                contrast_ratio REAL,
                wcag_aa_compliant INTEGER,
                checks TEXT NOT NULL,
                extracted_text TEXT,
                ocr_confidence REAL,
                ocr_findings TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
                organization_id TEXT NOT NULL DEFAULT 'org-novatech',
                name TEXT NOT NULL,
                description TEXT,
                preferred_tone TEXT,
                target_audience TEXT,
                approved_terminology TEXT, -- JSON
                prohibited_terminology TEXT, -- JSON
                required_phrases TEXT, -- JSON
                style_guidelines TEXT, -- JSON
                formatting_preferences TEXT, -- JSON
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS approved_facts (
                id TEXT PRIMARY KEY,
                brand_id TEXT NOT NULL,
                organization_id TEXT NOT NULL DEFAULT 'org-novatech',
                product_name TEXT NOT NULL,
                attribute TEXT NOT NULL,
                approved_value TEXT NOT NULL,
                unit_or_currency TEXT,
                source_title TEXT NOT NULL,
                source_url TEXT,
                verification_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id TEXT PRIMARY KEY,
                brand_id TEXT NOT NULL,
                organization_id TEXT NOT NULL DEFAULT 'org-novatech',
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                raw_content TEXT NOT NULL,
                image_alt_text TEXT,
                campaign_ref TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                current_revision INTEGER NOT NULL DEFAULT 1,
                created_by TEXT NOT NULL,
                reviewer_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_revisions (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                content_text TEXT NOT NULL,
                image_alt_text TEXT,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                change_summary TEXT,
                FOREIGN KEY (content_id) REFERENCES content_items(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_runs (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                analysis_mode TEXT NOT NULL,
                created_at TEXT NOT NULL,
                findings_count INTEGER NOT NULL,
                critical_count INTEGER NOT NULL,
                high_count INTEGER NOT NULL,
                medium_count INTEGER NOT NULL,
                low_count INTEGER NOT NULL,
                informational_count INTEGER NOT NULL,
                FOREIGN KEY (content_id) REFERENCES content_items(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_findings (
                id TEXT PRIMARY KEY,
                review_run_id TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                explanation TEXT NOT NULL,
                applicable_guideline TEXT NOT NULL,
                approved_source TEXT,
                evidence_record_id TEXT,
                evidence_status TEXT DEFAULT 'verified',
                recommended_correction TEXT NOT NULL,
                correction_rationale TEXT,
                detection_method TEXT NOT NULL,
                confidence TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                dismissal_reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (review_run_id) REFERENCES review_runs(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_comments (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                author_name TEXT NOT NULL,
                author_role TEXT NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (content_id) REFERENCES content_items(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS approval_events (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                revision_number INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                actor_name TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                comments TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (content_id) REFERENCES content_items(id)
            )
            """)

            # Migration for evidence columns if table existed from round 2
            try:
                cursor.execute("ALTER TABLE review_findings ADD COLUMN evidence_record_id TEXT")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE review_findings ADD COLUMN evidence_status TEXT DEFAULT 'verified'")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE review_findings ADD COLUMN correction_rationale TEXT")
            except Exception:
                pass

            # Migration for organization_id across entity tables
            for tbl in ["brands", "approved_facts", "content_items", "visual_analyses", "audit_logs"]:
                try:
                    cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN organization_id TEXT DEFAULT 'org-novatech'")
                except Exception:
                    pass

            # Migration for OCR columns in visual_analyses
            try:
                cursor.execute("ALTER TABLE visual_analyses ADD COLUMN ocr_confidence REAL")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE visual_analyses ADD COLUMN ocr_findings TEXT")
            except Exception:
                pass

            conn.commit()

    def _seed_if_empty(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM brands")
            if cursor.fetchone()[0] == 0:
                self._seed_data(conn)
            else:
                # Ensure organizations and apex brand exist even if database already has novatech
                self._ensure_multi_org_seed(conn)

    def _ensure_multi_org_seed(self, conn):
        cursor = conn.cursor()
        for org in SAMPLE_ORGANIZATIONS:
            cursor.execute("""
            INSERT OR IGNORE INTO organizations (id, name, slug, created_at)
            VALUES (?, ?, ?, ?)
            """, (org["id"], org["name"], org["slug"], org["created_at"]))

        for b in [SAMPLE_BRAND, SAMPLE_APEX_BRAND]:
            cursor.execute("""
            INSERT OR IGNORE INTO brands (id, organization_id, name, description, preferred_tone, target_audience, approved_terminology, prohibited_terminology, required_phrases, style_guidelines, formatting_preferences, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                b["id"], b.get("organization_id", "org-novatech"), b["name"], b["description"], b["preferred_tone"], b["target_audience"],
                json.dumps(b["approved_terminology"]),
                json.dumps(b["prohibited_terminology"]),
                json.dumps(b["required_phrases"]),
                json.dumps(b["style_guidelines"]),
                json.dumps(b["formatting_preferences"]),
                b["created_at"], b["updated_at"]
            ))

        for u in SAMPLE_USERS:
            cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, email, full_name, role, organization_id, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                u["id"], u["username"], u["email"], u["full_name"], u["role"], u["organization_id"], u["password_hash"], u["created_at"]
            ))
        self._seed_demo_posts(conn)
        self._cleanup_duplicate_drafts(conn)
        conn.commit()

    def _seed_data(self, conn):
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        # Insert Organizations
        for org in SAMPLE_ORGANIZATIONS:
            cursor.execute("""
            INSERT OR IGNORE INTO organizations (id, name, slug, created_at)
            VALUES (?, ?, ?, ?)
            """, (org["id"], org["name"], org["slug"], org["created_at"]))

        # Insert Brands
        for b in [SAMPLE_BRAND, SAMPLE_APEX_BRAND]:
            cursor.execute("""
            INSERT OR IGNORE INTO brands (id, organization_id, name, description, preferred_tone, target_audience, approved_terminology, prohibited_terminology, required_phrases, style_guidelines, formatting_preferences, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                b["id"], b.get("organization_id", "org-novatech"), b["name"], b["description"], b["preferred_tone"], b["target_audience"],
                json.dumps(b["approved_terminology"]),
                json.dumps(b["prohibited_terminology"]),
                json.dumps(b["required_phrases"]),
                json.dumps(b["style_guidelines"]),
                json.dumps(b["formatting_preferences"]),
                b["created_at"], b["updated_at"]
            ))

        # Insert Facts
        for f in SAMPLE_FACTS:
            cursor.execute("""
            INSERT OR IGNORE INTO approved_facts (id, brand_id, organization_id, product_name, attribute, approved_value, unit_or_currency, source_title, source_url, verification_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f["id"], f["brand_id"], f.get("organization_id", "org-novatech"), f["product_name"], f["attribute"], f["approved_value"],
                f.get("unit_or_currency"), f["source_title"], f.get("source_url"),
                f["verification_date"], f["status"], f["created_at"], f["updated_at"]
            ))

        # Insert Default Users for Round 3 Auth
        for u in SAMPLE_USERS:
            cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, email, full_name, role, organization_id, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                u["id"], u["username"], u["email"], u["full_name"], u["role"], u["organization_id"], u["password_hash"], u["created_at"]
            ))

        self._seed_demo_posts(conn)
        conn.commit()


    def _cleanup_duplicate_drafts(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
        SELECT brand_id, title, COUNT(*) as cnt
        FROM content_items
        WHERE status = 'draft'
        GROUP BY brand_id, title
        HAVING cnt > 1
        """)
        dup_groups = cursor.fetchall()
        for group in dup_groups:
            b_id = group["brand_id"] if isinstance(group, dict) or hasattr(group, "keys") else group[0]
            t = group["title"] if isinstance(group, dict) or hasattr(group, "keys") else group[1]
            cursor.execute("""
            SELECT id FROM content_items
            WHERE brand_id = ? AND title = ? AND status = 'draft'
            ORDER BY created_at DESC
            """, (b_id, t))
            items = cursor.fetchall()
            for dup in items[1:]:
                dup_id = dup["id"] if isinstance(dup, dict) or hasattr(dup, "keys") else dup[0]
                cursor.execute("SELECT id FROM review_runs WHERE content_id = ?", (dup_id,))
                runs = cursor.fetchall()
                for r in runs:
                    rid = r["id"] if isinstance(r, dict) or hasattr(r, "keys") else r[0]
                    cursor.execute("DELETE FROM review_findings WHERE review_run_id = ?", (rid,))
                cursor.execute("DELETE FROM review_runs WHERE content_id = ?", (dup_id,))
                cursor.execute("DELETE FROM content_revisions WHERE content_id = ?", (dup_id,))
                cursor.execute("DELETE FROM approval_events WHERE content_id = ?", (dup_id,))
                cursor.execute("DELETE FROM review_comments WHERE content_id = ?", (dup_id,))
                cursor.execute("DELETE FROM content_items WHERE id = ?", (dup_id,))
        conn.commit()

    def _seed_demo_posts(self, conn):
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

        # 1. Non-compliant post: "High-Risk Promotional Campaign (Contains Violations)"
        cursor.execute("SELECT id FROM content_items WHERE id = 'demo-content-invalid'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO content_items (id, brand_id, organization_id, title, content_type, channel, raw_content, image_alt_text, campaign_ref, status, current_revision, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "demo-content-invalid",
                "brand-novatech-001",
                "org-novatech",
                "High-Risk Promotional Campaign (Contains Violations)",
                "social",
                "LinkedIn & X / Twitter",
                "Get the all-new Nova Pro today for a cheap price of only ₹5,999! Our revolutionary system provides 100% guaranteed results and unbreakable cyber protection. The best in the world for enterprise infrastructure, risk-free!",
                "",
                "Q1-LAUNCH-CAMPAIGN",
                "in_review",
                1,
                "Alice Creator (creator)",
                now,
                now
            ))

            cursor.execute("""
            INSERT INTO content_revisions (id, content_id, revision_number, content_text, image_alt_text, created_by, created_at, change_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "rev-demo-invalid-01",
                "demo-content-invalid",
                1,
                "Get the all-new Nova Pro today for a cheap price of only ₹5,999! Our revolutionary system provides 100% guaranteed results and unbreakable cyber protection. The best in the world for enterprise infrastructure, risk-free!",
                "",
                "Alice Creator (creator)",
                now,
                "Initial creation"
            ))

            cursor.execute("""
            INSERT INTO approval_events (id, content_id, revision_number, event_type, actor_name, actor_role, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "evt-demo-invalid-01",
                "demo-content-invalid",
                1,
                "in_review",
                "Alice Creator",
                "creator",
                "Submitted for human governance review",
                now
            ))

            run_id = "run-demo-invalid-01"
            cursor.execute("""
            INSERT INTO review_runs (id, content_id, revision_number, analysis_mode, created_at, findings_count, critical_count, high_count, medium_count, low_count, informational_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (run_id, "demo-content-invalid", 1, "deterministic", now, 9, 1, 5, 2, 1, 0))

            demo_findings = [
                ("find-seed-01", run_id, "facts", "critical", "Product Price Contradiction", "₹5,999", "Content claims price is ₹5,999, but approved product fact states ₹4,999.", "NovaTech Enterprise Pricing Policy", "Pricing Matrix Q4 2025", "fact-001", "verified", "₹4,999", "Matches verified pricing matrix.", "deterministic_rule", "high", "open"),
                ("find-seed-02", run_id, "terminology", "high", "Prohibited Term 'cheap'", "cheap", "Brand guidelines strictly prohibit the term 'cheap'.", "Brand Tone & Terminology Standards", "Corporate Style Manual", None, "verified", "cost-effective", "Aligns with premium brand perception.", "deterministic_rule", "high", "open"),
                ("find-seed-03", run_id, "terminology", "high", "Unapproved Product Name 'Nova Pro'", "Nova Pro", "The approved brand name is 'NovaTech Pro'.", "Product Naming Architecture", "Product Registry 2026", "fact-001", "verified", "NovaTech Pro", "Standardizes official trademark naming.", "deterministic_rule", "high", "open"),
                ("find-seed-04", run_id, "claims", "high", "Absolute Guarantee Claim '100% guaranteed'", "100% guaranteed results", "Unsubstantiated absolute guarantee.", "Marketing Claims Substantiation Policy", "Legal Compliance Code §4", None, "verified", "enterprise-grade reliability", "Removes absolute liability risk.", "deterministic_rule", "high", "open"),
                ("find-seed-05", run_id, "claims", "high", "Unsubstantiated Claim 'risk-free'", "risk-free", "Regulatory compliance forbids absolute risk-free security claims.", "Legal & Regulatory Compliance Guidelines", "Security Warranty Policy", None, "verified", "risk-mitigated", "Accurately reflects security safeguards.", "deterministic_rule", "high", "open"),
                ("find-seed-06", run_id, "claims", "high", "Superlative Claim 'best in the world'", "The best in the world", "Unsubstantiated comparative claim without third-party audit.", "Substantiated Claims Policy", "FTC Advertising Substantiation", None, "verified", "leading enterprise choice", "Complies with competitive claim rules.", "deterministic_rule", "high", "open"),
                ("find-seed-07", run_id, "terminology", "medium", "Prohibited Term 'unbreakable'", "unbreakable", "Absolute security term prohibited by legal policy.", "Brand Tone Guidelines", "Legal Safeguards Doc", None, "verified", "resilient", "Approved resilience terminology.", "deterministic_rule", "high", "open"),
                ("find-seed-08", run_id, "accessibility", "medium", "Missing Image Alt Text", "[Attached Media / Promotional Image]", "Social media post lacks descriptive alternative text for screen readers.", "WCAG 2.1 AA Accessibility Standard", "Accessibility Guidelines v2", None, "verified", "Executive workstation showing the sleek NovaTech Pro hardware unit with security dashboard", "Required for screen reader accessibility.", "deterministic_rule", "high", "open"),
                ("find-seed-09", run_id, "requirements", "low", "Missing Required Legal Disclaimer", "[Omitted from submitted copy]", "Promotional announcements require standard copyright & trademark disclosure.", "Mandatory Legal Disclaimers", "Compliance Boilerplates", None, "verified", "\n\nEnterprise security powered by NovaTech. Terms & conditions apply.", "Mandatory legal safe harbor clause.", "deterministic_rule", "high", "open")
            ]
            for f in demo_findings:
                cursor.execute("""
                INSERT OR IGNORE INTO review_findings (id, review_run_id, category, severity, title, excerpt, explanation, applicable_guideline, approved_source, evidence_record_id, evidence_status, recommended_correction, correction_rationale, detection_method, confidence, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (*f, now))

        # 2. Compliant post: "Approved Product Announcement (Compliant)"
        cursor.execute("SELECT id FROM content_items WHERE id = 'demo-content-valid'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO content_items (id, brand_id, organization_id, title, content_type, channel, raw_content, image_alt_text, campaign_ref, status, current_revision, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "demo-content-valid",
                "brand-novatech-001",
                "org-novatech",
                "Approved Product Announcement (Compliant)",
                "social",
                "LinkedIn",
                "Introducing the NovaTech Pro, engineered for resilient enterprise infrastructure. Available now starting at ₹4,999 with a comprehensive 12 months hardware warranty. Experience proactive zero-trust threat management with seamless deployment.\n\nEnterprise security powered by NovaTech. Terms & conditions apply.",
                "Executive workstation showing the sleek NovaTech Pro hardware unit with security dashboard",
                "Q1-ENTERPRISE-ANNOUNCE",
                "approved",
                1,
                "Alice Creator (creator)",
                now,
                now
            ))

            cursor.execute("""
            INSERT INTO content_revisions (id, content_id, revision_number, content_text, image_alt_text, created_by, created_at, change_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "rev-demo-valid-01",
                "demo-content-valid",
                1,
                "Introducing the NovaTech Pro, engineered for resilient enterprise infrastructure...",
                "Executive workstation showing the sleek NovaTech Pro hardware unit with security dashboard",
                "Alice Creator (creator)",
                now,
                "Compliant submission approved by Chief Governance Administrator"
            ))

            cursor.execute("""
            INSERT INTO approval_events (id, content_id, revision_number, event_type, actor_name, actor_role, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "evt-demo-valid-01",
                "demo-content-valid",
                1,
                "approved",
                "Chief Governance Administrator",
                "admin",
                "Content approved for publication across enterprise channels.",
                now
            ))

            cursor.execute("""
            INSERT INTO review_runs (id, content_id, revision_number, analysis_mode, created_at, findings_count, critical_count, high_count, medium_count, low_count, informational_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("run-demo-valid-01", "demo-content-valid", 1, "deterministic", now, 0, 0, 0, 0, 0, 0))

        # 3. Apex Demo Post: "Apex Cloud Governance Suite Launch"
        cursor.execute("SELECT id FROM content_items WHERE id = 'demo-content-apex'")
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO content_items (id, brand_id, organization_id, title, content_type, channel, raw_content, image_alt_text, campaign_ref, status, current_revision, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "demo-content-apex",
                "brand-apex-001",
                "org-apex",
                "Apex Cloud Governance Suite Launch",
                "social",
                "LinkedIn",
                "Apex Global Corporation delivers enterprise cloud orchestration with military-grade redundancy.",
                "Apex cloud governance architecture dashboard",
                "APEX-CLOUD-2026",
                "approved",
                1,
                "Apex Administrator (admin)",
                now,
                now
            ))

            cursor.execute("""
            INSERT INTO content_revisions (id, content_id, revision_number, content_text, image_alt_text, created_by, created_at, change_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "rev-demo-apex-01",
                "demo-content-apex",
                1,
                "Apex Global Corporation delivers enterprise cloud orchestration with military-grade redundancy.",
                "Apex cloud governance architecture dashboard",
                "Apex Administrator (admin)",
                now,
                "Initial compliant release"
            ))

            cursor.execute("""
            INSERT INTO approval_events (id, content_id, revision_number, event_type, actor_name, actor_role, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "evt-demo-apex-01",
                "demo-content-apex",
                1,
                "approved",
                "Apex Administrator",
                "admin",
                "Approved compliant release for Apex Global Corporation.",
                now
            ))

            cursor.execute("""
            INSERT INTO review_runs (id, content_id, revision_number, analysis_mode, created_at, findings_count, critical_count, high_count, medium_count, low_count, informational_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("run-demo-apex-01", "demo-content-apex", 1, "deterministic", now, 0, 0, 0, 0, 0, 0))

        conn.commit()

    def reset_database(self):

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM approval_events")
            cursor.execute("DELETE FROM review_comments")
            cursor.execute("DELETE FROM review_findings")
            cursor.execute("DELETE FROM review_runs")
            cursor.execute("DELETE FROM content_revisions")
            cursor.execute("DELETE FROM content_items")
            cursor.execute("DELETE FROM approved_facts")
            cursor.execute("DELETE FROM brands")
            conn.commit()
            self._seed_data(conn)

    # --- Brands ---
    def get_brand(self, brand_id: Optional[str] = None, organization_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if brand_id and organization_id:
                cursor.execute("SELECT * FROM brands WHERE id = ? AND organization_id = ?", (brand_id, organization_id))
                row = cursor.fetchone()
                if row:
                    return self._row_to_brand(row)

            if brand_id and not organization_id:
                cursor.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_brand(row)

            if organization_id:
                cursor.execute("SELECT * FROM brands WHERE organization_id = ? ORDER BY name ASC LIMIT 1", (organization_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_brand(row)

            cursor.execute("SELECT * FROM brands WHERE id = ?", (NOVATECH_BRAND_ID,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT * FROM brands LIMIT 1")
                row = cursor.fetchone()
            return self._row_to_brand(row) if row else None

    def list_brands(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if organization_id:
                cursor.execute("SELECT * FROM brands WHERE organization_id = ? ORDER BY name ASC", (organization_id,))
            else:
                cursor.execute("SELECT * FROM brands ORDER BY name ASC")
            return [self._row_to_brand(row) for row in cursor.fetchall()]

    def update_brand(self, brand_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        brand = self.get_brand(brand_id)
        if not brand:
            return None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
            UPDATE brands SET
                name = ?, description = ?, preferred_tone = ?, target_audience = ?,
                approved_terminology = ?, prohibited_terminology = ?, required_phrases = ?,
                style_guidelines = ?, formatting_preferences = ?, updated_at = ?
            WHERE id = ?
            """, (
                updates.get("name", brand["name"]),
                updates.get("description", brand["description"]),
                updates.get("preferred_tone", brand["preferred_tone"]),
                updates.get("target_audience", brand["target_audience"]),
                json.dumps(updates.get("approved_terminology", brand["approved_terminology"])),
                json.dumps(updates.get("prohibited_terminology", brand["prohibited_terminology"])),
                json.dumps(updates.get("required_phrases", brand["required_phrases"])),
                json.dumps(updates.get("style_guidelines", brand["style_guidelines"])),
                json.dumps(updates.get("formatting_preferences", brand["formatting_preferences"])),
                now,
                brand_id
            ))
            conn.commit()
        return self.get_brand(brand_id)

    def _row_to_brand(self, row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "organization_id": row["organization_id"] if "organization_id" in row.keys() else "org-novatech",
            "name": row["name"],
            "description": row["description"],
            "preferred_tone": row["preferred_tone"],
            "target_audience": row["target_audience"],
            "approved_terminology": json.loads(row["approved_terminology"] or "[]"),
            "prohibited_terminology": json.loads(row["prohibited_terminology"] or "[]"),
            "required_phrases": json.loads(row["required_phrases"] or "[]"),
            "style_guidelines": json.loads(row["style_guidelines"] or "[]"),
            "formatting_preferences": json.loads(row["formatting_preferences"] or "{}"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }

    # --- Approved Facts ---
    def list_facts(self, brand_id: Optional[str] = None, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM approved_facts WHERE 1=1"
            params = []
            if brand_id:
                query += " AND brand_id = ?"
                params.append(brand_id)
            if organization_id:
                query += " AND organization_id = ?"
                params.append(organization_id)
            query += " ORDER BY product_name ASC, attribute ASC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_fact(self, fact_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM approved_facts WHERE id = ?", (fact_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_fact(self, fact_data: Dict[str, Any]) -> Dict[str, Any]:
        fact_id = fact_data.get("id") or f"fact-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO approved_facts (id, brand_id, organization_id, product_name, attribute, approved_value, unit_or_currency, source_title, source_url, verification_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact_id,
                fact_data["brand_id"],
                fact_data.get("organization_id", "org-novatech"),
                fact_data["product_name"],
                fact_data["attribute"],
                fact_data["approved_value"],
                fact_data.get("unit_or_currency"),
                fact_data["source_title"],
                fact_data.get("source_url"),
                fact_data.get("verification_date") or now[:10],
                fact_data.get("status", "active"),
                now,
                now
            ))
            conn.commit()
        return self.get_fact(fact_id)

    def update_fact(self, fact_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fact = self.get_fact(fact_id)
        if not fact:
            return None
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE approved_facts SET
                product_name = ?, attribute = ?, approved_value = ?, unit_or_currency = ?,
                source_title = ?, source_url = ?, verification_date = ?, status = ?, updated_at = ?
            WHERE id = ?
            """, (
                updates.get("product_name", fact["product_name"]),
                updates.get("attribute", fact["attribute"]),
                updates.get("approved_value", fact["approved_value"]),
                updates.get("unit_or_currency", fact.get("unit_or_currency")),
                updates.get("source_title", fact["source_title"]),
                updates.get("source_url", fact.get("source_url")),
                updates.get("verification_date", fact["verification_date"]),
                updates.get("status", fact["status"]),
                now,
                fact_id
            ))
            conn.commit()
        return self.get_fact(fact_id)

    def delete_fact(self, fact_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM approved_facts WHERE id = ?", (fact_id,))
            conn.commit()
            return cursor.rowcount > 0

    # --- Content Items & Review Workflow ---
    def list_content_items(self, brand_id: Optional[str] = None, status: Optional[str] = None, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM content_items WHERE 1=1"
            params = []
            if brand_id:
                query += " AND brand_id = ?"
                params.append(brand_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            if organization_id:
                query += " AND organization_id = ?"
                params.append(organization_id)
            query += " ORDER BY created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self.get_content_item(row["id"]) for row in rows]

    def get_content_item(self, content_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM content_items WHERE id = ?", (content_id,))
            item_row = cursor.fetchone()
            if not item_row:
                return None
            item = dict(item_row)

            # Revisions
            cursor.execute("SELECT * FROM content_revisions WHERE content_id = ? ORDER BY revision_number ASC", (content_id,))
            item["revisions"] = [dict(r) for r in cursor.fetchall()]

            # Comments
            cursor.execute("SELECT * FROM review_comments WHERE content_id = ? ORDER BY created_at ASC", (content_id,))
            item["comments"] = [dict(r) for r in cursor.fetchall()]

            # Approval History
            cursor.execute("SELECT * FROM approval_events WHERE content_id = ? ORDER BY created_at ASC", (content_id,))
            item["approval_history"] = [dict(r) for r in cursor.fetchall()]

            # Latest review run
            cursor.execute("SELECT * FROM review_runs WHERE content_id = ? ORDER BY created_at DESC LIMIT 1", (content_id,))
            run_row = cursor.fetchone()
            if run_row:
                run = dict(run_row)
                cursor.execute("SELECT * FROM review_findings WHERE review_run_id = ? ORDER BY severity ASC", (run["id"],))
                run["findings"] = [dict(f) for f in cursor.fetchall()]
                item["latest_review"] = run
            else:
                item["latest_review"] = None

            return item

    def create_content_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        content_id = data.get("id")
        brand_id = data["brand_id"]
        org_id = data.get("organization_id", "org-novatech")
        title = data.get("title", "Untitled Content")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Idempotency / Deduplication check:
            existing_id = None
            if content_id:
                cursor.execute("SELECT id FROM content_items WHERE id = ?", (content_id,))
                row = cursor.fetchone()
                if row:
                    existing_id = row["id"]

            if not existing_id and data.get("campaign_ref"):
                cursor.execute(
                    "SELECT id FROM content_items WHERE brand_id = ? AND campaign_ref = ? AND status IN ('draft', 'in_review') ORDER BY created_at DESC LIMIT 1",
                    (brand_id, data["campaign_ref"])
                )
                row = cursor.fetchone()
                if row:
                    existing_id = row["id"]

            if not existing_id and title:
                cursor.execute(
                    "SELECT id FROM content_items WHERE brand_id = ? AND title = ? AND status = 'draft' ORDER BY created_at DESC LIMIT 1",
                    (brand_id, title)
                )
                row = cursor.fetchone()
                if row:
                    existing_id = row["id"]

            if existing_id:
                cursor.execute("""
                UPDATE content_items
                SET raw_content = ?, image_alt_text = ?, channel = ?, content_type = ?, campaign_ref = ?, updated_at = ?
                WHERE id = ?
                """, (
                    data["raw_content"],
                    data.get("image_alt_text"),
                    data.get("channel", "general"),
                    data.get("content_type", "social"),
                    data.get("campaign_ref"),
                    now,
                    existing_id
                ))
                conn.commit()
                return self.get_content_item(existing_id)

            new_id = content_id or f"content-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
            INSERT INTO content_items (id, brand_id, organization_id, title, content_type, channel, raw_content, image_alt_text, campaign_ref, status, current_revision, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_id,
                brand_id,
                org_id,
                title,
                data.get("content_type", "social"),
                data.get("channel", "general"),
                data["raw_content"],
                data.get("image_alt_text"),
                data.get("campaign_ref"),
                data.get("status", "draft"),
                1,
                data.get("created_by", "Creator (Demo User)"),
                now,
                now
            ))

            # Initial revision 1
            rev_id = f"rev-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
            INSERT INTO content_revisions (id, content_id, revision_number, content_text, image_alt_text, created_by, created_at, change_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rev_id,
                new_id,
                1,
                data["raw_content"],
                data.get("image_alt_text"),
                data.get("created_by", "Creator (Demo User)"),
                now,
                "Initial creation"
            ))

            # Approval Event (Created)
            cursor.execute("""
            INSERT INTO approval_events (id, content_id, revision_number, event_type, actor_name, actor_role, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"evt-{uuid.uuid4().hex[:8]}",
                new_id,
                1,
                "created",
                data.get("created_by", "Creator (Demo User)"),
                "creator",
                "Content item created as draft",
                now
            ))

            conn.commit()
            return self.get_content_item(new_id)
    def revise_content_item(self, content_id: str, new_text: str, new_alt_text: Optional[str], change_summary: str, actor_name: str, actor_role: str) -> Optional[Dict[str, Any]]:
        item = self.get_content_item(content_id)
        if not item:
            return None
        
        now = datetime.now(timezone.utc).isoformat()
        new_rev_number = item["current_revision"] + 1

        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert revision
            rev_id = f"rev-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
            INSERT INTO content_revisions (id, content_id, revision_number, content_text, image_alt_text, created_by, created_at, change_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rev_id,
                content_id,
                new_rev_number,
                new_text,
                new_alt_text,
                actor_name,
                now,
                change_summary
            ))

            # Update content item
            cursor.execute("""
            UPDATE content_items SET
                raw_content = ?,
                image_alt_text = ?,
                current_revision = ?,
                updated_at = ?
            WHERE id = ?
            """, (new_text, new_alt_text, new_rev_number, now, content_id))

            # Event
            cursor.execute("""
            INSERT INTO approval_events (id, content_id, revision_number, event_type, actor_name, actor_role, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"evt-{uuid.uuid4().hex[:8]}",
                content_id,
                new_rev_number,
                "revised",
                actor_name,
                actor_role,
                f"Revision #{new_rev_number}: {change_summary}",
                now
            ))

            conn.commit()

        return self.get_content_item(content_id)

    def update_content_status(self, content_id: str, new_status: str, actor_name: str, actor_role: str, comments: Optional[str] = None) -> Optional[Dict[str, Any]]:
        item = self.get_content_item(content_id)
        if not item:
            return None
        
        now = datetime.now(timezone.utc).isoformat()
        rev_num = item["current_revision"]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE content_items SET status = ?, updated_at = ? WHERE id = ?
            """, (new_status, now, content_id))

            cursor.execute("""
            INSERT INTO approval_events (id, content_id, revision_number, event_type, actor_name, actor_role, comments, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"evt-{uuid.uuid4().hex[:8]}",
                content_id,
                rev_num,
                new_status,
                actor_name,
                actor_role,
                comments or f"Status changed to {new_status}",
                now
            ))

            if comments:
                cursor.execute("""
                INSERT INTO review_comments (id, content_id, revision_number, author_name, author_role, comment_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"cmt-{uuid.uuid4().hex[:8]}",
                    content_id,
                    rev_num,
                    actor_name,
                    actor_role,
                    comments,
                    now
                ))

            conn.commit()

        return self.get_content_item(content_id)

    def save_review_run(self, run_data: Dict[str, Any], findings_data: List[Dict[str, Any]]) -> str:
        run_id = run_data.get("id") or f"run-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        content_id = run_data["content_id"]
        rev_num = run_data["revision_number"]

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Prevent accumulation of duplicate review runs / findings for the same revision
            cursor.execute("SELECT id FROM review_runs WHERE content_id = ? AND revision_number = ?", (content_id, rev_num))
            old_runs = cursor.fetchall()
            for old_r in old_runs:
                rid = old_r["id"] if isinstance(old_r, dict) or hasattr(old_r, "keys") else old_r[0]
                cursor.execute("DELETE FROM review_findings WHERE review_run_id = ?", (rid,))
                cursor.execute("DELETE FROM review_runs WHERE id = ?", (rid,))

            cursor.execute("""
            INSERT INTO review_runs (id, content_id, revision_number, analysis_mode, created_at, findings_count, critical_count, high_count, medium_count, low_count, informational_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                content_id,
                rev_num,
                run_data.get("analysis_mode", "deterministic"),
                now,
                len(findings_data),
                sum(1 for f in findings_data if f["severity"] == "critical"),
                sum(1 for f in findings_data if f["severity"] == "high"),
                sum(1 for f in findings_data if f["severity"] == "medium"),
                sum(1 for f in findings_data if f["severity"] == "low"),
                sum(1 for f in findings_data if f["severity"] == "informational")
            ))

            for f in findings_data:
                f_id = f.get("id") or f"find-{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                INSERT INTO review_findings (id, review_run_id, category, severity, title, excerpt, explanation, applicable_guideline, approved_source, evidence_record_id, evidence_status, recommended_correction, correction_rationale, detection_method, confidence, status, dismissal_reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f_id,
                    run_id,
                    f["category"],
                    f["severity"],
                    f["title"],
                    f["excerpt"],
                    f["explanation"],
                    f["applicable_guideline"],
                    f.get("approved_source"),
                    f.get("evidence_record_id"),
                    f.get("evidence_status", "verified"),
                    f["recommended_correction"],
                    f.get("correction_rationale"),
                    f.get("detection_method", "deterministic_rule"),
                    f.get("confidence", "high"),
                    f.get("status", "open"),
                    f.get("dismissal_reason"),
                    now
                ))

            conn.commit()

        return run_id
    def update_finding_status(self, finding_id: str, new_status: str, dismissal_reason: Optional[str] = None) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE review_findings SET status = ?, dismissal_reason = ? WHERE id = ?
            """, (new_status, dismissal_reason, finding_id))
            conn.commit()
            return cursor.rowcount > 0

    # --- Governance Insights ---
    def get_governance_insights(self, brand_id: Optional[str] = None, organization_id: Optional[str] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_ci = []
            params_ci = []
            if organization_id:
                where_ci.append("ci.organization_id = ?")
                params_ci.append(organization_id)
            if brand_id:
                where_ci.append("ci.brand_id = ?")
                params_ci.append(brand_id)

            where_ci_str = f"WHERE {' AND '.join(where_ci)}" if where_ci else ""
            def_where = (where_ci_str + " AND ") if where_ci_str else "WHERE "

            # Content counts
            cursor.execute(f"SELECT COUNT(*) FROM content_items ci {where_ci_str}", params_ci)
            total_items = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM content_items ci {def_where} ci.status = 'in_review'", params_ci)
            pending_count = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM content_items ci {def_where} ci.status = 'approved'", params_ci)
            approved_count = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM content_items ci {def_where} ci.status = 'changes_requested'", params_ci)
            changes_requested_count = cursor.fetchone()[0]

            cursor.execute(f"""
            SELECT COUNT(DISTINCT rr.id)
            FROM review_runs rr
            JOIN content_items ci ON ci.id = rr.content_id
            {where_ci_str}
            """, params_ci)
            total_runs = cursor.fetchone()[0]

            # Findings
            cursor.execute(f"""
            SELECT COUNT(rf.id)
            FROM review_findings rf
            JOIN review_runs rr ON rr.id = rf.review_run_id
            JOIN content_items ci ON ci.id = rr.content_id
            {where_ci_str}
            """, params_ci)
            total_findings = cursor.fetchone()[0]

            # Category Distribution
            cursor.execute(f"""
            SELECT rf.category, COUNT(rf.id) as cnt
            FROM review_findings rf
            JOIN review_runs rr ON rr.id = rf.review_run_id
            JOIN content_items ci ON ci.id = rr.content_id
            {where_ci_str}
            GROUP BY rf.category
            ORDER BY cnt DESC
            """, params_ci)
            cat_rows = cursor.fetchall()

            cat_distribution = []
            if total_findings > 0 and cat_rows:
                raw_pcts = [round((row["cnt"] / total_findings) * 100.0, 1) for row in cat_rows]
                # Ensure sum equals 100.0% by adjusting largest category
                diff = round(100.0 - sum(raw_pcts), 1)
                if diff != 0:
                    raw_pcts[0] = round(raw_pcts[0] + diff, 1)

                for row, pct in zip(cat_rows, raw_pcts):
                    cat_distribution.append({
                        "category": row["category"],
                        "count": row["cnt"],
                        "percentage": pct
                    })

            # Severity Distribution
            cursor.execute(f"""
            SELECT rf.severity, COUNT(rf.id) as cnt
            FROM review_findings rf
            JOIN review_runs rr ON rr.id = rf.review_run_id
            JOIN content_items ci ON ci.id = rr.content_id
            {where_ci_str}
            GROUP BY rf.severity
            ORDER BY CASE rf.severity
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
                ELSE 5 END
            """, params_ci)
            sev_distribution = [{"severity": row["severity"], "count": row["cnt"]} for row in cursor.fetchall()]

            # Frequent Mistakes
            cursor.execute(f"""
            SELECT rf.title, rf.category, COUNT(rf.id) as cnt
            FROM review_findings rf
            JOIN review_runs rr ON rr.id = rf.review_run_id
            JOIN content_items ci ON ci.id = rr.content_id
            {where_ci_str}
            GROUP BY rf.title, rf.category
            ORDER BY cnt DESC
            LIMIT 5
            """, params_ci)
            mistake_rows = cursor.fetchall()
            frequent_mistakes = []
            for row in mistake_rows:
                rec = "Review and train creators on standard brand guidelines."
                if row["category"] == "facts":
                    rec = "Ensure sales and marketing teams verify the latest pricing matrix."
                elif row["category"] == "claims":
                    rec = "Require third-party audit citations before claiming absolute guarantees."
                elif row["category"] == "terminology":
                    rec = "Enforce copyeditor approved terminology checklist."
                frequent_mistakes.append({
                    "issue": row["title"],
                    "category": row["category"],
                    "count": row["cnt"],
                    "recommendation": rec
                })

            rule_clarifications = []
            if total_findings > 0:
                rule_clarifications.append("Clarify acceptable currency notation in social copy to reduce price contradiction flags.")
                rule_clarifications.append("Provide approved boilerplate disclaimers for quick insertion by creators.")
                rule_clarifications.append("Update terminology glossary with prohibited synonyms like 'cheap' vs approved 'cost-effective'.")

            return {
                "total_reviews_run": total_runs,
                "total_content_items": total_items,
                "pending_approval_count": pending_count,
                "approved_count": approved_count,
                "changes_requested_count": changes_requested_count,
                "total_findings_detected": total_findings,
                "category_distribution": cat_distribution,
                "severity_distribution": sev_distribution,
                "frequent_mistakes": frequent_mistakes,
                "rule_clarification_suggestions": rule_clarifications,
                "has_sufficient_data": total_runs > 0
            }
    # --- Users & Auth (Round 3) ---
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_data.get("id") or f"usr-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (id, username, email, full_name, role, organization_id, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data["username"],
                user_data["email"],
                user_data["full_name"],
                user_data["role"],
                user_data.get("organization_id", "org-novatech"),
                user_data["password_hash"],
                now
            ))
            conn.commit()
        return self.get_user_by_id(user_id)

    def update_user_password_hash(self, user_id: str, new_hash: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def list_users(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if organization_id:
                cursor.execute("SELECT id, username, email, full_name, role, organization_id, created_at FROM users WHERE organization_id = ?", (organization_id,))
            else:
                cursor.execute("SELECT id, username, email, full_name, role, organization_id, created_at FROM users")
            return [dict(r) for r in cursor.fetchall()]

    # --- Organizations (Round 3) ---
    def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM organizations WHERE id = ?", (org_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_organizations(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM organizations ORDER BY name ASC")
            return [dict(r) for r in cursor.fetchall()]

    # --- Audit Logs (Round 3) ---
    def record_audit_log(
        self,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        organization_id: str = "org-novatech"
    ) -> str:
        log_id = f"aud-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO audit_logs (id, user_id, username, organization_id, action, resource_type, resource_id, details, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id, user_id, username, organization_id, action, resource_type, resource_id, details, ip_address, now
            ))
            conn.commit()
        return log_id

    def list_audit_logs(self, limit: int = 50, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if organization_id:
                cursor.execute("SELECT * FROM audit_logs WHERE organization_id = ? ORDER BY created_at DESC LIMIT ?", (organization_id, limit))
            else:
                cursor.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    # --- Visual Analysis Persistence (Round 3) ---
    def save_visual_analysis(self, data: Dict[str, Any]) -> str:
        v_id = data.get("id") or f"vis-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO visual_analyses (
                id, brand_id, organization_id, user_id, file_name, file_size_bytes, dimensions,
                format, dominant_colors, palette_compliance_score, contrast_ratio, wcag_aa_compliant,
                checks, extracted_text, ocr_confidence, ocr_findings, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                v_id,
                data.get("brand_id", NOVATECH_BRAND_ID),
                data.get("organization_id", "org-novatech"),
                data.get("user_id", "demo"),
                data["file_name"],
                data["file_size_bytes"],
                json.dumps(data["dimensions"]),
                data["format"],
                json.dumps(data["dominant_colors"]),
                data["palette_compliance_score"],
                data.get("contrast_ratio"),
                1 if data.get("wcag_aa_compliant") else (0 if data.get("wcag_aa_compliant") is False else None),
                json.dumps(data["checks"]),
                data.get("extracted_text"),
                data.get("ocr_confidence"),
                json.dumps(data.get("ocr_findings", [])),
                now
            ))
            conn.commit()
        return v_id

    def list_visual_analyses(self, brand_id: Optional[str] = None, limit: int = 20, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM visual_analyses WHERE 1=1"
            params = []
            if brand_id:
                query += " AND brand_id = ?"
                params.append(brand_id)
            if organization_id:
                query += " AND organization_id = ?"
                params.append(organization_id)
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["dimensions"] = json.loads(item["dimensions"])
                item["dominant_colors"] = json.loads(item["dominant_colors"])
                item["checks"] = json.loads(item["checks"])
                item["ocr_findings"] = json.loads(item["ocr_findings"] or "[]") if "ocr_findings" in item and item["ocr_findings"] else []
                item["wcag_aa_compliant"] = bool(item["wcag_aa_compliant"]) if item["wcag_aa_compliant"] is not None else None
                results.append(item)
            return results


db = Database()
