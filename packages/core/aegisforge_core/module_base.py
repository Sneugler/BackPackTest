from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegisforge_models.models import ModuleResult, Project


@dataclass
class ModuleContext:
    project: Project | None
    base_dir: Path
    options: dict[str, Any]


class BaseModule:
    name = "base"

    def run(self, context: ModuleContext) -> ModuleResult:
        raise NotImplementedError
