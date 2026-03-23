from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from aegisforge_models.models import EvidenceItem


class EvidenceManager:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def ingest_path(self, path: Path, module: str, summary: str = "", tags: list[str] | None = None) -> EvidenceItem:
        path = path.resolve()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        destination = self.root / path.name
        if destination != path:
            shutil.copy2(path, destination)
        return EvidenceItem(
            path=str(destination),
            sha256=digest,
            module=module,
            summary=summary,
            tags=tags or [],
            metadata={"original_path": str(path)},
        )
