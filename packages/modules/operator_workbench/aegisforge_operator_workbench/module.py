from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult


class OperatorWorkbenchModule(BaseModule):
    name = "OperatorWorkbench"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("OperatorWorkbench requires a project context.")
        quick_actions = [
            "Import new targets",
            "Add evidence artifacts",
            "Review engagement flow",
            "Build assessment report",
            "Prepare emulation after-action report",
        ]
        saved_views = [
            {"name": "Scope health", "description": "Authorization, in-scope assets, and ambiguities"},
            {"name": "Evidence backlog", "description": "Artifacts needing finding linkage"},
            {"name": "Authorized toolkit plan", "description": "Safe tool recommendations filtered by rules of engagement"},
            {"name": "Pre-flight guardrails", "description": "Scope and forbidden-action checks before validation work"},
            {"name": "Campaign planner", "description": "Phase-based red/purple-team execution and review plan"},
            {"name": "Red-team timeline", "description": "Scenario, telemetry, and after-action review progress"},
        ]
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary="Prepared operator workbench overview.",
            artifacts={
                "recent_events": [event.model_dump(mode="json") for event in project.events[-10:]],
                "quick_actions": quick_actions,
                "saved_views": saved_views,
                "counts": {
                    "targets": len(project.targets),
                    "findings": len(project.findings),
                    "evidence": len(project.evidence),
                },
            },
        )
