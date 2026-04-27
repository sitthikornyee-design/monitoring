from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4


COLLECTION_COLUMNS = {
    "projects": (
        "id",
        "service_name",
        "project_name",
        "client_name",
        "project_status",
        "priority",
        "owner",
        "start_date",
        "due_date",
        "contact_number",
        "remark",
        "created_at",
        "updated_at",
    ),
    "actions": (
        "id",
        "project_id",
        "action_name",
        "description",
        "action_status",
        "priority",
        "assignee",
        "start_date",
        "due_date",
        "next_action",
        "progress_percent",
        "remark",
        "created_at",
        "updated_at",
    ),
    "activity_logs": (
        "id",
        "project_id",
        "action_id",
        "field_name",
        "old_value",
        "new_value",
        "updated_by",
        "updated_at",
        "comment",
    ),
}

DELETE_ORDER = ("activity_logs", "actions", "projects")
INSERT_ORDER = ("projects", "actions", "activity_logs")


class SQLiteRepository:
    def __init__(self, db_path: Path, schema_path: Path, seed_dir: Path | None = None):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self.seed_dir = Path(seed_dir) if seed_dir else None
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = MEMORY")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA temp_store = MEMORY")
        return connection

    def _initialize(self) -> None:
        schema = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as connection:
            connection.executescript(schema)
            self._ensure_action_columns(connection)
        self._seed_if_empty()

    def _ensure_action_columns(self, connection) -> None:
        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(actions)").fetchall()
        }
        if "next_action" not in existing_columns:
            connection.execute("ALTER TABLE actions ADD COLUMN next_action TEXT")

    def _seed_if_empty(self) -> None:
        if not self.seed_dir:
            return

        with self._connect() as connection:
            project_count = connection.execute("SELECT COUNT(1) FROM projects").fetchone()[0]

        if project_count:
            return

        projects = self._load_seed_file("projects.json")
        actions = self._load_seed_file("actions.json")
        activity_logs = self._load_seed_file("activity_logs.json")
        self.save_workspace(projects, actions, activity_logs)

    def _load_seed_file(self, filename: str):
        if not self.seed_dir:
            return []

        path = self.seed_dir / filename
        if not path.exists():
            return []

        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        return json.loads(raw)

    def _fetch_collection(self, table_name: str):
        columns = COLLECTION_COLUMNS[table_name]
        sql = f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY rowid ASC"
        with self._connect() as connection:
            rows = connection.execute(sql).fetchall()
        return [dict(row) for row in rows]

    def load_collection(self, table_name: str):
        return self._fetch_collection(table_name)

    def load_workspace(self):
        projects, actions, activity_logs = self.load_workspace_values()
        return {
            "projects": projects,
            "actions": actions,
            "activity_logs": activity_logs,
        }

    def load_workspace_values(self):
        return (
            self.load_collection("projects"),
            self.load_collection("actions"),
            self.load_collection("activity_logs"),
        )

    def save_workspace(self, projects, actions, activity_logs) -> None:
        collections = {
            "projects": projects,
            "actions": actions,
            "activity_logs": activity_logs,
        }

        with self._connect() as connection:
            for table_name in DELETE_ORDER:
                connection.execute(f"DELETE FROM {table_name}")

            for table_name in INSERT_ORDER:
                self._insert_many(connection, table_name, collections[table_name])

            connection.commit()

    def _insert_many(self, connection, table_name: str, rows) -> None:
        if not rows:
            return

        columns = COLLECTION_COLUMNS[table_name]
        placeholders = ", ".join("?" for _ in columns)
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        payload = [[row.get(column) for column in columns] for row in rows]
        connection.executemany(sql, payload)

    def new_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:8]}"

    def healthcheck(self):
        with self._connect() as connection:
            connection.execute("SELECT 1").fetchone()
        return {
            "storage": "sqlite",
            "status": "ok",
            "database_path": str(self.db_path),
        }
