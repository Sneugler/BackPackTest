from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import CampaignPhase, ModuleResult


class CampaignPlannerModule(BaseModule):
    name = "CampaignPlanner"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("CampaignPlanner requires a project context.")

        validation_paths = context.options.get("validation_paths", [])
        top_paths = validation_paths[:3]
        path_titles = [item["title"] for item in top_paths]
        top_attack_refs = sorted({ref for item in top_paths for ref in item.get("mitre_techniques", [])})

        phases = [
            CampaignPhase(
                name="authorization_and_preflight",
                objective="Confirm authorization, scope, and communications before exercise execution.",
                planned_actions=["Review rules of engagement", "Run preflight checks", "Confirm escalation contacts"],
                success_criteria=["Scope validated", "Contacts confirmed", "Guardrails acknowledged"],
                evidence_goals=["ROE snapshot", "Preflight checklist", "Operator notes"],
                communication_checkpoints=["Kickoff approved by engagement owner"],
            ),
            CampaignPhase(
                name="path_validation",
                objective="Exercise the highest-priority authorized validation paths.",
                planned_actions=path_titles or ["Select top-ranked validation path"],
                success_criteria=["Expected telemetry reviewed", "Observations recorded for each path"],
                evidence_goals=["Timeline notes", "Screenshots/exports", "Observed detections"],
                communication_checkpoints=["Mid-exercise status update to stakeholders"],
            ),
            CampaignPhase(
                name="blue_team_review",
                objective="Translate observations into defender actions and report artifacts.",
                planned_actions=["Map mitigations", "Package evidence", "Review control gaps"],
                success_criteria=["Mitigations agreed", "Evidence export complete", "Report inputs ready"],
                evidence_goals=["Mitigation mapping", "Evidence export", "After-action summary"],
                communication_checkpoints=["After-action review scheduled"],
            ),
        ]

        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary=f"Prepared campaign plan with {len(phases)} phases.",
            artifacts={
                "phases": [item.model_dump(mode="json") for item in phases],
                "top_paths": path_titles,
                "mitre_focus": top_attack_refs,
            },
        )
