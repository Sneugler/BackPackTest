from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from aegisforge_core.advisories import load_advisories
from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import Finding, ModuleResult, Remediation, Severity


@dataclass(frozen=True)
class ConfigRule:
    match: str
    title: str
    severity: Severity
    risk: str
    replacement: str
    target_types: tuple[str, ...] = ("generic",)
    cves: tuple[str, ...] = field(default_factory=tuple)


RULES = [
    ConfigRule("privileged: true", "Container runs privileged", Severity.HIGH, "Privileged containers expand host compromise blast radius.", "Drop privileged mode and add only required Linux capabilities.", ("docker-compose", "kubernetes"), ("CVE-2019-5736",)),
    ConfigRule(":latest", "Unpinned image tag", Severity.MEDIUM, "Mutable tags make deployments unreproducible and hard to audit.", "Pin images to immutable version tags or digests.", ("dockerfile", "docker-compose", "kubernetes")),
    ConfigRule("0.0.0.0/0", "Overly broad network exposure", Severity.HIGH, "World-open network ranges violate least privilege.", "Restrict ingress CIDRs to approved administrative or service ranges.", ("terraform", "iam", "generic")),
    ConfigRule("pull_request_target", "Privileged CI trigger", Severity.HIGH, "This trigger can expose secrets in unsafe CI workflows.", "Prefer safer triggers and isolate secret-bearing jobs.", ("github-actions", "ci")),
    ConfigRule("CAP_SYS_ADMIN", "High-risk capability granted", Severity.HIGH, "This capability is broadly equivalent to elevated system control.", "Remove the capability or isolate the workload into a hardened sandbox.", ("docker-compose", "kubernetes")),
]


class ConfigAuditModule(BaseModule):
    name = "ConfigAudit"

    def run(self, context: ModuleContext) -> ModuleResult:
        path = Path(context.options["path"])
        target_type = context.options.get("target_type", "generic")
        text = path.read_text(encoding="utf-8")
        advisories = {item.id: item for item in load_advisories()}
        findings: list[Finding] = []
        for rule in RULES:
            if rule.match in text and ("generic" in rule.target_types or target_type in rule.target_types):
                related = [f"{cve}: {advisories[cve].summary}" for cve in rule.cves if cve in advisories]
                findings.append(
                    Finding(
                        title=rule.title,
                        severity=rule.severity,
                        description=f"{rule.risk} Indicator `{rule.match}` was found in {path.name}.",
                        remediation=Remediation(summary=rule.replacement, quick_win=rule.severity in {Severity.MEDIUM, Severity.HIGH}),
                        module=self.name,
                        confidence="high",
                        references=[str(path), *related],
                    )
                )
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary=f"Found {len(findings)} configuration issues in {path.name}.",
            findings=findings,
            artifacts={"file": str(path), "target_type": target_type, "rule_count": len(RULES), "cve_coverage": sorted({cve for rule in RULES for cve in rule.cves})},
        )
