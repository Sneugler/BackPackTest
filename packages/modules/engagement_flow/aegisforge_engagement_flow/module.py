from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult, WorkflowStep


class EngagementFlowModule(BaseModule):
    name = "EngagementFlow"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("EngagementFlow requires a project context.")
        steps = [
            WorkflowStep(name="authorization_precheck", status="done" if project.authorization_evidence else "blocked", description="Validate authorization evidence and rules of engagement.", evidence_required=True),
            WorkflowStep(name="target_definition", status="done" if project.targets else "in_progress", description="Import, normalize, and classify in-scope assets."),
            WorkflowStep(name="artifact_intake", status="done" if project.evidence else "pending", description="Collect screenshots, notes, logs, and artifacts."),
            WorkflowStep(name="finding_development", status="pending", description="Develop findings linked to supporting evidence.", evidence_required=True),
            WorkflowStep(name="detection_mapping", status="pending", description="Attach telemetry and validation notes to findings."),
            WorkflowStep(name="report_generation", status="pending", description="Build executive, technical, and after-action reports."),
        ]
        checklist = [
            "Confirm environment type matches the engagement",
            "Confirm dangerous actions were acknowledged before execution",
            "Validate red-team scenario preconditions before exercise start",
            "Ensure every major finding links to evidence where possible",
        ]
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary="Generated engagement lifecycle workflow.",
            artifacts={"steps": [step.model_dump() for step in steps], "operator_checklist": checklist},
        )
