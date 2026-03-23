from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Advisory:
    id: str
    package: str
    affected_versions: list[str]
    summary: str
    detection_hint: str


DEFAULT_ADVISORY_PATH = Path(__file__).resolve().parents[3] / "examples" / "advisories" / "cves.json"


def load_advisories(path: Path | None = None) -> list[Advisory]:
    advisory_path = path or DEFAULT_ADVISORY_PATH
    payload = json.loads(advisory_path.read_text(encoding="utf-8"))
    return [Advisory(**item) for item in payload]


def advisory_map() -> dict[str, Advisory]:
    return {item.id: item for item in load_advisories()}
