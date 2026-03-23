from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult, Severity


SEVERITY_SCORE = {
    Severity.INFO: 1,
    Severity.LOW: 2,
    Severity.MEDIUM: 3,
    Severity.HIGH: 4,
    Severity.CRITICAL: 5,
}


class RiskPrioritizerModule(BaseModule):
    name = "RiskPrioritizer"

    def run(self, context: ModuleContext) -> ModuleResult:
        findings = list(context.options["findings"])
        ranked = sorted(findings, key=lambda finding: SEVERITY_SCORE[finding.severity], reverse=True)
        roadmap = []
        for index, finding in enumerate(ranked, start=1):
            roadmap.append(
                {
                    "priority": index,
                    "title": finding.title,
                    "severity": finding.severity.value,
                    "quick_win": finding.remediation.quick_win,
                    "owner": finding.remediation.owner or "unassigned",
                    "rationale": "Address high-severity and easily remediated issues first.",
                }
            )
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary="Ranked findings into a remediation roadmap.",
            findings=ranked,
            artifacts={"roadmap": roadmap},
        )
