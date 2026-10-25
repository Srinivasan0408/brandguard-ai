import json
import sqlite3
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from ..config import settings
from .seed_data import SAMPLE_BRAND, SAMPLE_FACTS, SAMPLE_DEMO_POSTS, NOVATECH_BRAND_ID

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
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
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
                recommended_correction TEXT NOT NULL,
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

            conn.commit()

    def _seed_if_empty(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM brands")
            if cursor.fetchone()[0] == 0:
                self._seed_data(conn)

    def _seed_data(self, conn):
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        # Insert NovaTech Brand
        b = SAMPLE_BRAND
        cursor.execute("""
        INSERT INTO brands (id, name, description, preferred_tone, target_audience, approved_terminology, prohibited_terminology, required_phrases, style_guidelines, formatting_preferences, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b["id"], b["name"], b["description"], b["preferred_tone"], b["target_audience"],
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
            INSERT INTO approved_facts (id, brand_id, product_name, attribute, approved_value, unit_or_currency, source_title, source_url, verification_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f["id"], f["brand_id"], f["product_name"], f["attribute"], f["approved_value"],
                f.get("unit_or_currency"), f["source_title"], f.get("source_url"),
                f["verification_date"], f["status"], f["created_at"], f["updated_at"]
            ))

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
    def get_brand(self, brand_id: str = NOVATECH_BRAND_ID) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
            row = cursor.fetchone()
            if not row:
                # Return default brand if available
                cursor.execute("SELECT * FROM brands LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    return None
            return self._row_to_brand(row)

    def list_brands(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
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
    def list_facts(self, brand_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if brand_id:
                cursor.execute("SELECT * FROM approved_facts WHERE brand_id = ? ORDER BY product_name ASC, attribute ASC", (brand_id,))
            else:
                cursor.execute("SELECT * FROM approved_facts ORDER BY product_name ASC, attribute ASC")
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
            INSERT INTO approved_facts (id, brand_id, product_name, attribute, approved_value, unit_or_currency, source_title, source_url, verification_date, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fact_id,
                fact_data["brand_id"],
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
    def list_content_items(self, brand_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
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
        content_id = data.get("id") or f"content-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO content_items (id, brand_id, title, content_type, channel, raw_content, image_alt_text, campaign_ref, status, current_revision, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id,
                data["brand_id"],
                data["title"],
                data["content_type"],
                data["channel"],
                data["raw_content"],
                data.get("image_alt_text"),
                data.get("campaign_ref"),
                "draft",
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
                content_id,
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
                content_id,
                1,
                "created",
                data.get("created_by", "Creator (Demo User)"),
                "creator",
                "Content item created as draft",
                now
            ))

            conn.commit()
        return self.get_content_item(content_id)

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

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO review_runs (id, content_id, revision_number, analysis_mode, created_at, findings_count, critical_count, high_count, medium_count, low_count, informational_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                run_data["content_id"],
                run_data["revision_number"],
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
                INSERT INTO review_findings (id, review_run_id, category, severity, title, excerpt, explanation, applicable_guideline, approved_source, recommended_correction, detection_method, confidence, status, dismissal_reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    f["recommended_correction"],
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
    def get_governance_insights(self, brand_id: Optional[str] = None) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Content counts
            cursor.execute("SELECT COUNT(*) FROM content_items")
            total_items = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM content_items WHERE status = 'in_review'")
            pending_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM content_items WHERE status = 'approved'")
            approved_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM content_items WHERE status = 'changes_requested'")
            changes_requested_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM review_runs")
            total_runs = cursor.fetchone()[0]

            # Findings
            cursor.execute("SELECT COUNT(*) FROM review_findings")
            total_findings = cursor.fetchone()[0]

            # Category Distribution
            cursor.execute("""
            SELECT category, COUNT(*) as cnt 
            FROM review_findings 
            GROUP BY category 
            ORDER BY cnt DESC
            """)
            cat_rows = cursor.fetchall()
            cat_distribution = []
            for row in cat_rows:
                pct = round((row["cnt"] / max(total_findings, 1)) * 100, 1)
                cat_distribution.append({
                    "category": row["category"],
                    "count": row["cnt"],
                    "percentage": pct
                })

            # Severity Distribution
            cursor.execute("""
            SELECT severity, COUNT(*) as cnt 
            FROM review_findings 
            GROUP BY severity 
            ORDER BY CASE severity 
                WHEN 'critical' THEN 1 
                WHEN 'high' THEN 2 
                WHEN 'medium' THEN 3 
                WHEN 'low' THEN 4 
                ELSE 5 END
            """)
            sev_distribution = [{"severity": row["severity"], "count": row["cnt"]} for row in cursor.fetchall()]

            # Frequent Mistakes (repeated excerpts or titles)
            cursor.execute("""
            SELECT title, category, COUNT(*) as cnt 
            FROM review_findings 
            GROUP BY title, category 
            ORDER BY cnt DESC 
            LIMIT 5
            """)
            mistake_rows = cursor.fetchall()
            frequent_mistakes = []
            for row in mistake_rows:
                rec = "Review and train creators on standard brand guidelines."
                if row["category"] == "facts":
                    rec = "Ensure sales and marketing teams verify the latest Q4 pricing matrix."
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

            # Rule clarification suggestions based on observed friction
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

db = Database()
