from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from aegisforge_models.models import ModuleResult, Project


class SQLiteRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS module_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                module_name TEXT NOT NULL,
                summary TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        self.conn.commit()

    def save_project(self, project: Project) -> None:
        payload = project.model_dump_json()
        self.conn.execute(
            "INSERT OR REPLACE INTO projects (id, name, payload) VALUES (?, ?, ?)",
            (project.id, project.name, payload),
        )
        self.conn.commit()

    def load_project(self, project_id: str) -> Project:
        row = self.conn.execute("SELECT payload FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            raise KeyError(f"Unknown project: {project_id}")
        return Project.model_validate_json(row[0])

    def list_projects(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT id, name FROM projects ORDER BY name").fetchall()
        return [dict(row) for row in rows]

    def log_event(self, project_id: str, event_type: str, message: str, payload: dict[str, Any]) -> None:
        self.conn.execute(
            "INSERT INTO events (project_id, event_type, message, payload) VALUES (?, ?, ?, ?)",
            (project_id, event_type, message, json.dumps(payload)),
        )
        self.conn.commit()

    def save_module_result(self, result: ModuleResult) -> None:
        self.conn.execute(
            "INSERT INTO module_results (project_id, module_name, summary, payload) VALUES (?, ?, ?, ?)",
            (
                result.project_id,
                result.module_name,
                result.summary,
                json.dumps(result.model_dump(mode="json")),
            ),
        )
        self.conn.commit()

    def list_module_results(self, project_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT module_name, summary, created_at FROM module_results WHERE project_id = ? ORDER BY id DESC",
            (project_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def list_module_result_payloads(self, project_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT module_name, payload, created_at FROM module_results WHERE project_id = ? ORDER BY id DESC",
            (project_id,),
        ).fetchall()
        results = []
        for row in rows:
            payload = json.loads(row["payload"])
            results.append(
                {
                    "module_name": row["module_name"],
                    "created_at": row["created_at"],
                    "result": payload,
                }
            )
        return results
