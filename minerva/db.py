import sqlite3
import os
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to user home directory
            db_path = os.getenv("MINERVA_DB_PATH", os.path.expanduser("~/.minerva/minerva.db"))
        
        self.db_path = db_path
        if db_path != ":memory:":
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
                
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.create_tables()
        self.migrate_schema()

    def close(self):
        self.conn.close()

    def migrate_schema(self):
        # Ensure projects table exists and default project is present
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.execute("INSERT OR IGNORE INTO projects (id, name) VALUES ('default', 'Default Project');")

        # Ensure audit_log table exists
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_type TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Add missing columns to existing tables for backwards compatibility
        tables_columns = {
            "goals": [
                ("project_id", "TEXT DEFAULT 'default'"),
                ("deleted_at", "TEXT DEFAULT NULL"),
                ("source", "TEXT DEFAULT NULL"),
                ("confidence", "REAL DEFAULT 1.0"),
                ("superseded_by", "INTEGER DEFAULT NULL REFERENCES goals(id) ON DELETE SET NULL")
            ],
            "constraints": [
                ("project_id", "TEXT DEFAULT 'default'"),
                ("deleted_at", "TEXT DEFAULT NULL"),
                ("source", "TEXT DEFAULT NULL")
            ],
            "decisions": [
                ("project_id", "TEXT DEFAULT 'default'"),
                ("deleted_at", "TEXT DEFAULT NULL"),
                ("alternatives_considered", "TEXT DEFAULT NULL"),
                ("decided_by", "TEXT DEFAULT NULL"),
                ("superseded_by", "INTEGER DEFAULT NULL REFERENCES decisions(id) ON DELETE SET NULL")
            ],
            "tasks": [
                ("project_id", "TEXT DEFAULT 'default'"),
                ("deleted_at", "TEXT DEFAULT NULL"),
                ("updated_at", "TEXT DEFAULT NULL"),
                ("assignee", "TEXT DEFAULT NULL"),
                ("depends_on", "TEXT DEFAULT NULL"),
                ("blocks", "TEXT DEFAULT NULL"),
                ("context_refs", "TEXT DEFAULT NULL"),
                ("learned_facts", "TEXT DEFAULT NULL")
            ],
            "facts": [
                ("project_id", "TEXT DEFAULT 'default'"),
                ("deleted_at", "TEXT DEFAULT NULL"),
                ("source", "TEXT DEFAULT NULL"),
                ("verified", "INTEGER DEFAULT 0"),
                ("contradicts", "TEXT DEFAULT NULL")
            ]
        }

        # Turn off foreign keys temporarily to allow adding columns with foreign keys
        self.conn.execute("PRAGMA foreign_keys = OFF;")
        try:
            for table, cols in tables_columns.items():
                cursor = self.conn.execute(f"PRAGMA table_info({table});")
                existing_cols = {row["name"] for row in cursor.fetchall()}
                for col_name, col_def in cols:
                    if col_name not in existing_cols:
                        self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def};")
            self.conn.commit()
        finally:
            self.conn.execute("PRAGMA foreign_keys = ON;")

    def log_audit(self, record_type: str, record_id: int, action: str, details: str = None):
        with self.conn:
            self.conn.execute(
                "INSERT INTO audit_log (record_type, record_id, action, details) VALUES (?, ?, ?, ?)",
                (record_type, record_id, action, details)
            )

    def create_tables(self):
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goals';")
        goals_exists = cursor.fetchone() is not None
        
        # We always want projects and audit_log to exist
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.execute("INSERT OR IGNORE INTO projects (id, name) VALUES ('default', 'Default Project');")

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_type TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        if goals_exists:
            return

        with self.conn:
            # 1. Goals
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT DEFAULT 'default' REFERENCES projects(id),
                text TEXT NOT NULL,
                priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'superseded', 'achieved')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                deleted_at TEXT DEFAULT NULL,
                source TEXT DEFAULT NULL,
                confidence REAL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
                superseded_by INTEGER REFERENCES goals(id) ON DELETE SET NULL
            );
            """)
            
            # 2. Constraints
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS constraints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT DEFAULT 'default' REFERENCES projects(id),
                text TEXT NOT NULL,
                severity TEXT DEFAULT 'hard' CHECK(severity IN ('hard', 'soft')),
                type TEXT DEFAULT 'technical' CHECK(type IN ('technical', 'business', 'legal', 'budget', 'time')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                deleted_at TEXT DEFAULT NULL,
                source TEXT DEFAULT NULL
            );
            """)

            # 3. Decisions
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT DEFAULT 'default' REFERENCES projects(id),
                decision TEXT NOT NULL,
                rationale TEXT NOT NULL,
                status TEXT DEFAULT 'current' CHECK(status IN ('current', 'superseded')),
                decided_at TEXT DEFAULT CURRENT_TIMESTAMP,
                supersedes_id INTEGER,
                superseded_by INTEGER REFERENCES decisions(id) ON DELETE SET NULL,
                deleted_at TEXT DEFAULT NULL,
                alternatives_considered TEXT DEFAULT NULL,
                decided_by TEXT DEFAULT NULL,
                FOREIGN KEY (supersedes_id) REFERENCES decisions(id) ON DELETE SET NULL
            );
            """)

            # 4. Tasks
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT DEFAULT 'default' REFERENCES projects(id),
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'blocked', 'done')),
                priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                outcome TEXT,
                deleted_at TEXT DEFAULT NULL,
                assignee TEXT DEFAULT NULL,
                depends_on TEXT DEFAULT NULL,
                blocks TEXT DEFAULT NULL,
                context_refs TEXT DEFAULT NULL,
                learned_facts TEXT DEFAULT NULL
            );
            """)

            # 5. Facts
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT DEFAULT 'default' REFERENCES projects(id),
                text TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                confidence REAL DEFAULT 1.0 CHECK(confidence >= 0.0 AND confidence <= 1.0),
                reference_count INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_referenced_at TEXT DEFAULT CURRENT_TIMESTAMP,
                deleted_at TEXT DEFAULT NULL,
                source TEXT DEFAULT NULL,
                verified INTEGER DEFAULT 0 CHECK(verified IN (0, 1)),
                contradicts TEXT DEFAULT NULL
            );
            """)

            # 6. Links (generic relationship table)
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_type TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                source_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target_type, target_id, source_type, source_id)
            );
            """)

            # 7. Embeddings
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_type TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                vector_blob BLOB NOT NULL,
                UNIQUE(record_type, record_id)
            );
            """)

            # --- FTS5 Virtual Tables ---
            # Using external content tables to keep indices small and fast
            self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS goals_fts USING fts5(text, content='goals', content_rowid='id');")
            self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS constraints_fts USING fts5(text, content='constraints', content_rowid='id');")
            self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS decisions_fts USING fts5(decision, rationale, content='decisions', content_rowid='id');")
            self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts USING fts5(title, description, content='tasks', content_rowid='id');")
            self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(text, content='facts', content_rowid='id');")

            # --- Triggers for FTS5 Sync ---
            # Goals Triggers
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS goals_ai AFTER INSERT ON goals BEGIN
                INSERT INTO goals_fts(rowid, text) VALUES (new.id, new.text);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS goals_ad AFTER DELETE ON goals BEGIN
                INSERT INTO goals_fts(goals_fts, rowid, text) VALUES ('delete', old.id, old.text);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS goals_au AFTER UPDATE ON goals BEGIN
                INSERT INTO goals_fts(goals_fts, rowid, text) VALUES ('delete', old.id, old.text);
                INSERT INTO goals_fts(rowid, text) VALUES (new.id, new.text);
            END;
            """)

            # Constraints Triggers
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS constraints_ai AFTER INSERT ON constraints BEGIN
                INSERT INTO constraints_fts(rowid, text) VALUES (new.id, new.text);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS constraints_ad AFTER DELETE ON constraints BEGIN
                INSERT INTO constraints_fts(constraints_fts, rowid, text) VALUES ('delete', old.id, old.text);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS constraints_au AFTER UPDATE ON constraints BEGIN
                INSERT INTO constraints_fts(constraints_fts, rowid, text) VALUES ('delete', old.id, old.text);
                INSERT INTO constraints_fts(rowid, text) VALUES (new.id, new.text);
            END;
            """)

            # Decisions Triggers
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS decisions_ai AFTER INSERT ON decisions BEGIN
                INSERT INTO decisions_fts(rowid, decision, rationale) VALUES (new.id, new.decision, new.rationale);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS decisions_ad AFTER DELETE ON decisions BEGIN
                INSERT INTO decisions_fts(decisions_fts, rowid, decision, rationale) VALUES ('delete', old.id, old.decision, old.rationale);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS decisions_au AFTER UPDATE ON decisions BEGIN
                INSERT INTO decisions_fts(decisions_fts, rowid, decision, rationale) VALUES ('delete', old.id, old.decision, old.rationale);
                INSERT INTO decisions_fts(rowid, decision, rationale) VALUES (new.id, new.decision, new.rationale);
            END;
            """)

            # Tasks Triggers
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS tasks_ai AFTER INSERT ON tasks BEGIN
                INSERT INTO tasks_fts(rowid, title, description) VALUES (new.id, new.title, new.description);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS tasks_ad AFTER DELETE ON tasks BEGIN
                INSERT INTO tasks_fts(tasks_fts, rowid, title, description) VALUES ('delete', old.id, old.title, old.description);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS tasks_au AFTER UPDATE ON tasks BEGIN
                INSERT INTO tasks_fts(tasks_fts, rowid, title, description) VALUES ('delete', old.id, old.title, old.description);
                INSERT INTO tasks_fts(rowid, title, description) VALUES (new.id, new.title, new.description);
            END;
            """)

            # Facts Triggers
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
                INSERT INTO facts_fts(rowid, text) VALUES (new.id, new.text);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
                INSERT INTO facts_fts(facts_fts, rowid, text) VALUES ('delete', old.id, old.text);
            END;
            """)
            self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
                INSERT INTO facts_fts(facts_fts, rowid, text) VALUES ('delete', old.id, old.text);
                INSERT INTO facts_fts(rowid, text) VALUES (new.id, new.text);
            END;
            """)

    # ==========================================
    # GOALS CRUD
    # ==========================================
    # ==========================================
    # GOALS CRUD
    # ==========================================
    def add_goal(self, text: str, priority: int = 3, status: str = 'active', project_id: str = 'default', source: str = None, confidence: float = 1.0, superseded_by: int = None) -> int:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO goals (text, priority, status, project_id, source, confidence, superseded_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (text, priority, status, project_id, source, confidence, superseded_by)
            )
            goal_id = cursor.lastrowid
            self.log_audit('goal', goal_id, 'insert', f"text={text[:30]}, priority={priority}")
            return goal_id

    def update_goal(self, goal_id: int, text: str = None, priority: int = None, status: str = None, source: str = None, confidence: float = None, superseded_by: int = None, deleted_at: str = None) -> bool:
        updates = []
        params = []
        if text is not None:
            updates.append("text = ?")
            params.append(text)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if source is not None:
            updates.append("source = ?")
            params.append(source)
        if confidence is not None:
            updates.append("confidence = ?")
            params.append(confidence)
        if superseded_by is not None:
            updates.append("superseded_by = ?")
            params.append(superseded_by)
        if deleted_at is not None:
            if deleted_at == 'NULL':
                updates.append("deleted_at = NULL")
            else:
                updates.append("deleted_at = ?")
                params.append(deleted_at)
        
        if not updates:
            return False
            
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(goal_id)
        
        with self.conn:
            cursor = self.conn.execute(
                f"UPDATE goals SET {', '.join(updates)} WHERE id = ?",
                params
            )
            success = cursor.rowcount > 0
            if success:
                self.log_audit('goal', goal_id, 'update', f"fields={list(updates)}")
            return success

    def get_goal(self, goal_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM goals WHERE id = ? AND deleted_at IS NULL", (goal_id,)).fetchone()
        return dict(row) if row else None

    def list_goals(self, status: str = None, project_id: str = 'default') -> list:
        query = "SELECT * FROM goals WHERE project_id = ? AND deleted_at IS NULL"
        params = [project_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY priority DESC, created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def delete_goal(self, goal_id: int, hard: bool = False) -> bool:
        with self.conn:
            if hard:
                cursor = self.conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
                self.conn.execute("DELETE FROM embeddings WHERE record_type = 'goal' AND record_id = ?", (goal_id,))
                self.conn.execute("DELETE FROM links WHERE (target_type = 'goal' AND target_id = ?) OR (source_type = 'goal' AND source_id = ?)", (goal_id, goal_id))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('goal', goal_id, 'hard_delete')
                return success
            else:
                cursor = self.conn.execute("UPDATE goals SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (goal_id,))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('goal', goal_id, 'soft_delete')
                return success

    def restore_goal(self, goal_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute("UPDATE goals SET deleted_at = NULL WHERE id = ?", (goal_id,))
            success = cursor.rowcount > 0
            if success:
                self.log_audit('goal', goal_id, 'restore')
            return success

    # ==========================================
    # CONSTRAINTS CRUD
    # ==========================================
    def add_constraint(self, text: str, severity: str = 'hard', type_val: str = 'technical', project_id: str = 'default', source: str = None) -> int:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO constraints (text, severity, type, project_id, source) VALUES (?, ?, ?, ?, ?)",
                (text, severity, type_val, project_id, source)
            )
            constraint_id = cursor.lastrowid
            self.log_audit('constraint', constraint_id, 'insert', f"severity={severity}, type={type_val}")
            return constraint_id

    def update_constraint(self, constraint_id: int, text: str = None, severity: str = None, type_val: str = None, source: str = None, deleted_at: str = None) -> bool:
        updates = []
        params = []
        if text is not None:
            updates.append("text = ?")
            params.append(text)
        if severity is not None:
            updates.append("severity = ?")
            params.append(severity)
        if type_val is not None:
            updates.append("type = ?")
            params.append(type_val)
        if source is not None:
            updates.append("source = ?")
            params.append(source)
        if deleted_at is not None:
            if deleted_at == 'NULL':
                updates.append("deleted_at = NULL")
            else:
                updates.append("deleted_at = ?")
                params.append(deleted_at)
        if not updates:
            return False
        params.append(constraint_id)
        with self.conn:
            cursor = self.conn.execute(
                f"UPDATE constraints SET {', '.join(updates)} WHERE id = ?",
                params
            )
            success = cursor.rowcount > 0
            if success:
                self.log_audit('constraint', constraint_id, 'update', f"fields={list(updates)}")
            return success

    def get_constraint(self, constraint_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM constraints WHERE id = ? AND deleted_at IS NULL", (constraint_id,)).fetchone()
        return dict(row) if row else None

    def list_constraints(self, type_val: str = None, project_id: str = 'default') -> list:
        query = "SELECT * FROM constraints WHERE project_id = ? AND deleted_at IS NULL"
        params = [project_id]
        if type_val:
            query += " AND type = ?"
            params.append(type_val)
        query += " ORDER BY severity DESC, created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def delete_constraint(self, constraint_id: int, hard: bool = False) -> bool:
        with self.conn:
            if hard:
                cursor = self.conn.execute("DELETE FROM constraints WHERE id = ?", (constraint_id,))
                self.conn.execute("DELETE FROM embeddings WHERE record_type = 'constraint' AND record_id = ?", (constraint_id,))
                self.conn.execute("DELETE FROM links WHERE (target_type = 'constraint' AND target_id = ?) OR (source_type = 'constraint' AND source_id = ?)", (constraint_id, constraint_id))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('constraint', constraint_id, 'hard_delete')
                return success
            else:
                cursor = self.conn.execute("UPDATE constraints SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (constraint_id,))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('constraint', constraint_id, 'soft_delete')
                return success

    def restore_constraint(self, constraint_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute("UPDATE constraints SET deleted_at = NULL WHERE id = ?", (constraint_id,))
            success = cursor.rowcount > 0
            if success:
                self.log_audit('constraint', constraint_id, 'restore')
            return success

    # ==========================================
    # DECISIONS CRUD
    # ==========================================
    def add_decision(self, decision: str, rationale: str, status: str = 'current', supersedes_id: int = None, project_id: str = 'default', alternatives_considered: str = None, decided_by: str = None) -> int:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO decisions (decision, rationale, status, supersedes_id, project_id, alternatives_considered, decided_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (decision, rationale, status, supersedes_id, project_id, alternatives_considered, decided_by)
            )
            decision_id = cursor.lastrowid
            
            # If this decision supersedes another one, update the superseded decision's status and superseded_by back-link
            if supersedes_id:
                self.conn.execute(
                    "UPDATE decisions SET status = 'superseded', superseded_by = ? WHERE id = ?",
                    (decision_id, supersedes_id)
                )
            
            self.log_audit('decision', decision_id, 'insert', f"supersedes={supersedes_id}")
            return decision_id

    def update_decision(self, decision_id: int, decision: str = None, rationale: str = None, status: str = None, supersedes_id: int = None, superseded_by: int = None, alternatives_considered: str = None, decided_by: str = None, deleted_at: str = None) -> bool:
        updates = []
        params = []
        if decision is not None:
            updates.append("decision = ?")
            params.append(decision)
        if rationale is not None:
            updates.append("rationale = ?")
            params.append(rationale)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if supersedes_id is not None:
            updates.append("supersedes_id = ?")
            params.append(supersedes_id)
        if superseded_by is not None:
            updates.append("superseded_by = ?")
            params.append(superseded_by)
        if alternatives_considered is not None:
            updates.append("alternatives_considered = ?")
            params.append(alternatives_considered)
        if decided_by is not None:
            updates.append("decided_by = ?")
            params.append(decided_by)
        if deleted_at is not None:
            if deleted_at == 'NULL':
                updates.append("deleted_at = NULL")
            else:
                updates.append("deleted_at = ?")
                params.append(deleted_at)
            
        if not updates:
            return False
            
        params.append(decision_id)
        with self.conn:
            cursor = self.conn.execute(
                f"UPDATE decisions SET {', '.join(updates)} WHERE id = ?",
                params
            )
            success = cursor.rowcount > 0
            if success:
                self.log_audit('decision', decision_id, 'update', f"fields={list(updates)}")
                if supersedes_id and status == 'current':
                    self.conn.execute(
                        "UPDATE decisions SET status = 'superseded', superseded_by = ? WHERE id = ?",
                        (decision_id, supersedes_id)
                    )
            return success

    def get_decision(self, decision_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM decisions WHERE id = ? AND deleted_at IS NULL", (decision_id,)).fetchone()
        return dict(row) if row else None

    def list_decisions(self, status: str = None, project_id: str = 'default') -> list:
        query = "SELECT * FROM decisions WHERE project_id = ? AND deleted_at IS NULL"
        params = [project_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY decided_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def delete_decision(self, decision_id: int, hard: bool = False) -> bool:
        with self.conn:
            if hard:
                cursor = self.conn.execute("DELETE FROM decisions WHERE id = ?", (decision_id,))
                self.conn.execute("DELETE FROM embeddings WHERE record_type = 'decision' AND record_id = ?", (decision_id,))
                self.conn.execute("DELETE FROM links WHERE (target_type = 'decision' AND target_id = ?) OR (source_type = 'decision' AND source_id = ?)", (decision_id, decision_id))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('decision', decision_id, 'hard_delete')
                return success
            else:
                cursor = self.conn.execute("UPDATE decisions SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (decision_id,))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('decision', decision_id, 'soft_delete')
                return success

    def restore_decision(self, decision_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute("UPDATE decisions SET deleted_at = NULL WHERE id = ?", (decision_id,))
            success = cursor.rowcount > 0
            if success:
                self.log_audit('decision', decision_id, 'restore')
            return success

    # ==========================================
    # TASKS CRUD
    # ==========================================
    def add_task(self, title: str, description: str = None, status: str = 'todo', priority: int = 3, project_id: str = 'default', assignee: str = None, depends_on: str = None, blocks: str = None, context_refs: str = None, learned_facts: str = None) -> int:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO tasks (title, description, status, priority, project_id, assignee, depends_on, blocks, context_refs, learned_facts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (title, description, status, priority, project_id, assignee, depends_on, blocks, context_refs, learned_facts)
            )
            task_id = cursor.lastrowid
            self.log_audit('task', task_id, 'insert', f"title={title[:30]}")
            return task_id

    def update_task(self, task_id: int, title: str = None, description: str = None, status: str = None, priority: int = None, outcome: str = None, assignee: str = None, depends_on: str = None, blocks: str = None, context_refs: str = None, learned_facts: str = None, deleted_at: str = None) -> bool:
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            if status == 'done':
                updates.append("completed_at = CURRENT_TIMESTAMP")
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if outcome is not None:
            updates.append("outcome = ?")
            params.append(outcome)
        if assignee is not None:
            updates.append("assignee = ?")
            params.append(assignee)
        if depends_on is not None:
            updates.append("depends_on = ?")
            params.append(depends_on)
        if blocks is not None:
            updates.append("blocks = ?")
            params.append(blocks)
        if context_refs is not None:
            updates.append("context_refs = ?")
            params.append(context_refs)
        if learned_facts is not None:
            updates.append("learned_facts = ?")
            params.append(learned_facts)
        if deleted_at is not None:
            if deleted_at == 'NULL':
                updates.append("deleted_at = NULL")
            else:
                updates.append("deleted_at = ?")
                params.append(deleted_at)
            
        if not updates:
            return False
            
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(task_id)
        with self.conn:
            cursor = self.conn.execute(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
                params
            )
            success = cursor.rowcount > 0
            if success:
                self.log_audit('task', task_id, 'update', f"fields={list(updates)}")
            return success

    def get_task(self, task_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ? AND deleted_at IS NULL", (task_id,)).fetchone()
        return dict(row) if row else None

    def list_tasks(self, status: str = None, project_id: str = 'default') -> list:
        query = "SELECT * FROM tasks WHERE project_id = ? AND deleted_at IS NULL"
        params = [project_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY priority DESC, created_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def delete_task(self, task_id: int, hard: bool = False) -> bool:
        with self.conn:
            if hard:
                cursor = self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                self.conn.execute("DELETE FROM embeddings WHERE record_type = 'task' AND record_id = ?", (task_id,))
                self.conn.execute("DELETE FROM links WHERE (target_type = 'task' AND target_id = ?) OR (source_type = 'task' AND source_id = ?)", (task_id, task_id))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('task', task_id, 'hard_delete')
                return success
            else:
                cursor = self.conn.execute("UPDATE tasks SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('task', task_id, 'soft_delete')
                return success

    def restore_task(self, task_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute("UPDATE tasks SET deleted_at = NULL WHERE id = ?", (task_id,))
            success = cursor.rowcount > 0
            if success:
                self.log_audit('task', task_id, 'restore')
            return success

    # ==========================================
    # FACTS CRUD
    # ==========================================
    def add_fact(self, text: str, category: str = 'general', confidence: float = 1.0, project_id: str = 'default', source: str = None, verified: int = 0, contradicts: str = None) -> int:
        with self.conn:
            cursor = self.conn.execute(
                "INSERT INTO facts (text, category, confidence, project_id, source, verified, contradicts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (text, category, confidence, project_id, source, verified, contradicts)
            )
            fact_id = cursor.lastrowid
            self.log_audit('fact', fact_id, 'insert', f"category={category}")
            return fact_id

    def update_fact(self, fact_id: int, text: str = None, category: str = None, confidence: float = None, source: str = None, verified: int = None, contradicts: str = None, deleted_at: str = None) -> bool:
        updates = []
        params = []
        if text is not None:
            updates.append("text = ?")
            params.append(text)
        if category is not None:
            updates.append("category = ?")
            params.append(category)
        if confidence is not None:
            updates.append("confidence = ?")
            params.append(confidence)
        if source is not None:
            updates.append("source = ?")
            params.append(source)
        if verified is not None:
            updates.append("verified = ?")
            params.append(verified)
        if contradicts is not None:
            updates.append("contradicts = ?")
            params.append(contradicts)
        if deleted_at is not None:
            if deleted_at == 'NULL':
                updates.append("deleted_at = NULL")
            else:
                updates.append("deleted_at = ?")
                params.append(deleted_at)
        if not updates:
            return False
        params.append(fact_id)
        with self.conn:
            cursor = self.conn.execute(
                f"UPDATE facts SET {', '.join(updates)} WHERE id = ?",
                params
            )
            success = cursor.rowcount > 0
            if success:
                self.log_audit('fact', fact_id, 'update', f"fields={list(updates)}")
            return success

    def increment_fact_reference(self, fact_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute(
                "UPDATE facts SET reference_count = reference_count + 1, last_referenced_at = CURRENT_TIMESTAMP WHERE id = ? AND deleted_at IS NULL",
                (fact_id,)
            )
            return cursor.rowcount > 0

    def get_fact(self, fact_id: int) -> dict:
        row = self.conn.execute("SELECT * FROM facts WHERE id = ? AND deleted_at IS NULL", (fact_id,)).fetchone()
        return dict(row) if row else None

    def list_facts(self, category: str = None, project_id: str = 'default') -> list:
        query = "SELECT * FROM facts WHERE project_id = ? AND deleted_at IS NULL"
        params = [project_id]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY reference_count DESC, last_referenced_at DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def delete_fact(self, fact_id: int, hard: bool = False) -> bool:
        with self.conn:
            if hard:
                cursor = self.conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
                self.conn.execute("DELETE FROM embeddings WHERE record_type = 'fact' AND record_id = ?", (fact_id,))
                self.conn.execute("DELETE FROM links WHERE (target_type = 'fact' AND target_id = ?) OR (source_type = 'fact' AND source_id = ?)", (fact_id, fact_id))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('fact', fact_id, 'hard_delete')
                return success
            else:
                cursor = self.conn.execute("UPDATE facts SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?", (fact_id,))
                success = cursor.rowcount > 0
                if success:
                    self.log_audit('fact', fact_id, 'soft_delete')
                return success

    def restore_fact(self, fact_id: int) -> bool:
        with self.conn:
            cursor = self.conn.execute("UPDATE facts SET deleted_at = NULL WHERE id = ?", (fact_id,))
            success = cursor.rowcount > 0
            if success:
                self.log_audit('fact', fact_id, 'restore')
            return success

    # ==========================================
    # LINKS (GENERIC ENTITY LINKING)
    # ==========================================
    def link_entities(self, target_type: str, target_id: int, source_type: str, source_id: int) -> int:
        if target_type > source_type or (target_type == source_type and target_id > source_id):
            target_type, source_type = source_type, target_type
            target_id, source_id = source_id, target_id

        with self.conn:
            self.conn.execute(
                """
                INSERT INTO links (target_type, target_id, source_type, source_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(target_type, target_id, source_type, source_id) DO UPDATE SET created_at = CURRENT_TIMESTAMP
                """,
                (target_type, target_id, source_type, source_id)
            )
            # Fetch the link ID explicitly to be immune to lastrowid resets
            row = self.conn.execute(
                "SELECT id FROM links WHERE target_type = ? AND target_id = ? AND source_type = ? AND source_id = ?",
                (target_type, target_id, source_type, source_id)
            ).fetchone()
            link_id = row[0]
            self.log_audit('link', link_id, 'insert', f"{target_type}#{target_id}<->{source_type}#{source_id}")
            return link_id

    def unlink_entities(self, target_type: str, target_id: int, source_type: str, source_id: int) -> bool:
        if target_type > source_type or (target_type == source_type and target_id > source_id):
            target_type, source_type = source_type, target_type
            target_id, source_id = source_id, target_id

        with self.conn:
            cursor = self.conn.execute(
                "DELETE FROM links WHERE target_type = ? AND target_id = ? AND source_type = ? AND source_id = ?",
                (target_type, target_id, source_type, source_id)
            )
            success = cursor.rowcount > 0
            if success:
                self.log_audit('link', 0, 'delete', f"{target_type}#{target_id}<->{source_type}#{source_id}")
            return success

    def get_links_for_entity(self, entity_type: str, entity_id: int) -> list:
        rows = self.conn.execute(
            """
            SELECT target_type AS type, target_id AS id, created_at FROM links WHERE source_type = ? AND source_id = ?
            UNION
            SELECT source_type AS type, source_id AS id, created_at FROM links WHERE target_type = ? AND target_id = ?
            """,
            (entity_type, entity_id, entity_type, entity_id)
        ).fetchall()
        
        results = []
        for r in rows:
            linked_type = r['type']
            linked_id = r['id']
            item = None
            if linked_type == 'goal':
                item = self.get_goal(linked_id)
            elif linked_type == 'constraint':
                item = self.get_constraint(linked_id)
            elif linked_type == 'decision':
                item = self.get_decision(linked_id)
            elif linked_type == 'task':
                item = self.get_task(linked_id)
            elif linked_type == 'fact':
                item = self.get_fact(linked_id)
            
            if item:
                results.append({
                    "type": linked_type,
                    "id": linked_id,
                    "created_at": r['created_at'],
                    "details": item
                })
        return results

    # ==========================================
    # EMBEDDINGS CRUD
    # ==========================================
    def set_embedding(self, record_type: str, record_id: int, vector: "np.ndarray"):
        import numpy as np
        blob = vector.astype(np.float32).tobytes()
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO embeddings (record_type, record_id, vector_blob)
                VALUES (?, ?, ?)
                ON CONFLICT(record_type, record_id) DO UPDATE SET vector_blob = excluded.vector_blob
                """,
                (record_type, record_id, blob)
            )

    def get_embedding(self, record_type: str, record_id: int) -> "np.ndarray":
        row = self.conn.execute(
            "SELECT vector_blob FROM embeddings WHERE record_type = ? AND record_id = ?",
            (record_type, record_id)
        ).fetchone()
        if not row:
            return None
        import numpy as np
        return np.frombuffer(row['vector_blob'], dtype=np.float32)

    def get_all_embeddings(self, record_type: str) -> list:
        rows = self.conn.execute(
            "SELECT record_id, vector_blob FROM embeddings WHERE record_type = ?",
            (record_type,)
        ).fetchall()
        import numpy as np
        return [(r['record_id'], np.frombuffer(r['vector_blob'], dtype=np.float32)) for r in rows]

    # ==========================================
    # FTS5 SEARCH METHODS
    # ==========================================
    def fts_search(self, record_type: str, query: str, limit: int = 10, project_id: str = 'default') -> list:
        # Clean query: replace non-alphanumeric characters with spaces to avoid FTS5 syntax/column errors
        clean_chars = [char if (char.isalnum() or char.isspace()) else " " for char in query]
        clean_query = "".join(clean_chars)
        words = [w for w in clean_query.split() if w]
        if not words:
            return []
        fts_query = " OR ".join(words)

        fts_table = f"{record_type}s_fts"
        content_table = f"{record_type}s"
        if record_type == 'constraint':
            content_table = 'constraints'
            
        try:
            rows = self.conn.execute(
                f"""
                SELECT f.rowid AS id, -bm25({fts_table}) AS score, c.*
                FROM {fts_table} f
                JOIN {content_table} c ON c.id = f.rowid
                WHERE {fts_table} MATCH ? AND c.project_id = ? AND c.deleted_at IS NULL
                ORDER BY score DESC
                LIMIT ?
                """,
                (fts_query, project_id, limit)
            ).fetchall()
            return [{"id": r['id'], "score": r['score'], "details": dict(r)} for r in rows]
        except sqlite3.OperationalError:
            text_match_clause = "text LIKE ?"
            if record_type == 'decision':
                text_match_clause = "decision LIKE ? OR rationale LIKE ?"
            elif record_type == 'task':
                text_match_clause = "title LIKE ? OR description LIKE ?"
                
            like_param = f"%{query}%"
            if record_type == 'decision' or record_type == 'task':
                params = [like_param, like_param, project_id, limit]
            else:
                params = [like_param, project_id, limit]
            
            rows = self.conn.execute(
                f"""
                SELECT id, 1.0 AS score, *
                FROM {content_table}
                WHERE ({text_match_clause}) AND project_id = ? AND deleted_at IS NULL
                LIMIT ?
                """,
                params
            ).fetchall()
            return [{"id": r['id'], "score": r['score'], "details": dict(r)} for r in rows]
