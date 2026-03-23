from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult, Severity


SEVERITY_ORDER = {
    Severity.CRITICAL: 5,
    Severity.HIGH: 4,
    Severity.MEDIUM: 3,
    Severity.LOW: 2,
    Severity.INFO: 1,
}


class ReportSmithModule(BaseModule):
    name = "ReportSmith"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("ReportSmith requires a project context.")
        sorted_findings = sorted(project.findings, key=lambda item: SEVERITY_ORDER[item.severity], reverse=True)
        executive_summary = {
            "project": project.name,
            "environment_type": project.environment_type.value,
            "readiness": project.scope.readiness.value,
            "finding_count": len(project.findings),
            "top_risks": [finding.title for finding in sorted_findings[:3]],
        }
        roadmap = [
            {
                "title": finding.title,
                "severity": finding.severity.value,
                "remediation": finding.remediation.summary,
            }
            for finding in sorted_findings
        ]
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary="Prepared report pack content.",
            artifacts={
                "executive_summary": executive_summary,
                "technical_appendix": [finding.model_dump(mode="json") for finding in sorted_findings],
                "roadmap": roadmap,
            },
        )
