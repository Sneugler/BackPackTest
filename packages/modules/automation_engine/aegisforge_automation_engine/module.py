from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult


DEFAULT_RULES = [
    {
        "if": "project_has_targets",
        "then": ["SurfaceMapper", "EngagementFlow"],
    },
    {
        "if": "project_has_findings",
        "then": ["ReportSmith", "RiskPrioritizer"],
    },
    {
        "if": "project_has_evidence",
        "then": ["EvidenceVault"],
    },
]


class AutomationEngineModule(BaseModule):
    name = "AutomationEngine"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("AutomationEngine requires a project context.")
        rules = context.options.get("rules", DEFAULT_RULES)
        facts = {
            "project_has_targets": bool(project.targets),
            "project_has_findings": bool(project.findings),
            "project_has_evidence": bool(project.evidence),
        }
        planned_actions = []
        for rule in rules:
            if facts.get(rule["if"], False):
                planned_actions.append({"trigger": rule["if"], "actions": rule["then"]})
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary=f"Prepared {len(planned_actions)} automation action groups.",
            artifacts={"facts": facts, "planned_actions": planned_actions, "rules": rules},
        )
