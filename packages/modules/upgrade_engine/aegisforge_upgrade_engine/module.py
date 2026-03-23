from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult, UpgradeProposal


class UpgradeEngineModule(BaseModule):
    name = "UpgradeEngine"

    def run(self, context: ModuleContext) -> ModuleResult:
        critiques = [
            {
                "area": "architecture",
                "strength": "Module registry now separates orchestration from review modules.",
                "weakness": "Module results are still embedded in project blobs rather than stored independently.",
                "improvement": "Add a dedicated result/event table for queryable module history.",
            },
            {
                "area": "red-team UX",
                "strength": "Scenario planning and telemetry expectations are structured.",
                "weakness": "After-action templates should be promoted to report packs.",
                "improvement": "Add a report template family for emulation after-action output.",
            },
            {
                "area": "tests",
                "strength": "Unit, integration, and golden coverage exist.",
                "weakness": "Dashboard and workflow coverage are still relatively light.",
                "improvement": "Add endpoint and workflow regression tests.",
            },
        ]
        proposals = [
            UpgradeProposal(title="Persist module history", rationale=critiques[0]["improvement"], impact="auditability", complexity="medium"),
            UpgradeProposal(title="Emulation after-action report pack", rationale=critiques[1]["improvement"], impact="report_quality", complexity="medium"),
            UpgradeProposal(title="Dashboard workflow tests", rationale=critiques[2]["improvement"], impact="reliability", complexity="low"),
        ]
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "platform",
            summary="Completed critique-and-improve analysis.",
            artifacts={"critiques": critiques, "proposals": [proposal.model_dump() for proposal in proposals]},
        )
