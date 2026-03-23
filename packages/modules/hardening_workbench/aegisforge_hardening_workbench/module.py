from __future__ import annotations

from pathlib import Path

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import HardeningRecommendation, ModuleResult


class HardeningWorkbenchModule(BaseModule):
    name = "HardeningWorkbench"

    def run(self, context: ModuleContext) -> ModuleResult:
        path = Path(context.options["path"])
        text = path.read_text(encoding="utf-8")
        replacement = text
        if "FROM python:3.11" in replacement:
            replacement = replacement.replace(
                "FROM python:3.11",
                "FROM python:3.11-slim\nRUN adduser --disabled-password appuser\nUSER appuser",
            )
        checklist = [
            "Pin the base image digest",
            "Run as a non-root user",
            "Minimize build-time packages and copy only required artifacts",
            "Add a healthcheck or external liveness validation path",
        ]
        recommendation = HardeningRecommendation(
            target_type=context.options.get("target_type", "dockerfile"),
            title="Safer container baseline",
            rationale="Reduces privilege exposure and keeps builds more reproducible.",
            replacement=replacement,
            checklist=checklist,
        )
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary="Generated hardened baseline guidance.",
            artifacts={"recommendation": recommendation.model_dump()},
        )
