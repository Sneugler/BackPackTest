from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Settings(BaseModel):
    workspace_dir: Path = Path(".aegisforge")
    database_name: str = "aegisforge.db"
    reports_dir: str = "reports"
    evidence_dir: str = "evidence"
    exports_dir: str = "exports"
    local_dashboard_host: str = "127.0.0.1"
    local_dashboard_port: int = 8877
    log_level: str = "INFO"
    dangerous_ack_required: bool = True
    plugin_paths: list[str] = Field(default_factory=list)


def load_settings(base_dir: Path | None = None) -> Settings:
    base = Path(base_dir or Path.cwd())
    config_path = base / "aegisforge.yaml"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            return Settings.model_validate(yaml.safe_load(handle) or {})
    return Settings()
