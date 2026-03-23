from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from aegisforge_core.advisories import load_advisories
from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import Finding, ModuleResult, Remediation, Severity


@dataclass(frozen=True)
class CodeRule:
    match: str
    title: str
    severity: Severity
    rationale: str
    remediation: str
    cves: tuple[str, ...] = field(default_factory=tuple)


RULES = [
    CodeRule("subprocess.", "Command execution surface", Severity.HIGH, "User-influenced command execution can become command injection.", "Prefer structured APIs and strict allowlists for permitted commands."),
    CodeRule("pickle.loads", "Unsafe deserialization", Severity.HIGH, "Deserializing untrusted blobs can lead to code execution.", "Replace pickle for untrusted data with a safe serializer and explicit schema checks."),
    CodeRule("requests.get(user", "Potential SSRF pattern", Severity.MEDIUM, "User-controlled destinations can pivot into internal services.", "Validate URL destinations against approved hosts or resolve via a trusted proxy."),
    CodeRule("SECRET", "Potential hardcoded secret", Severity.LOW, "Secrets in source increase leakage and rotation risk.", "Move secrets into a managed secret store or deployment-time injection path."),
    CodeRule("yaml.load(", "Unsafe YAML loading", Severity.MEDIUM, "Unsafe loaders can instantiate unexpected objects.", "Use a safe loader and validate the resulting schema.", ("CVE-2020-14343",)),
]


class CodeGuardModule(BaseModule):
    name = "CodeGuard"

    def run(self, context: ModuleContext) -> ModuleResult:
        root = Path(context.options["path"])
        advisories = load_advisories()
        findings: list[Finding] = []
        reviewed_files = 0
        advisory_hits = []
        for file in root.rglob("*.py"):
            reviewed_files += 1
            text = file.read_text(encoding="utf-8")
            for rule in RULES:
                if rule.match in text:
                    related = [f"{cve}: {item.summary}" for cve in rule.cves for item in advisories if item.id == cve]
                    findings.append(
                        Finding(
                            title=rule.title,
                            severity=rule.severity,
                            description=f"{rule.rationale} Pattern `{rule.match}` found in {file}.",
                            remediation=Remediation(summary=rule.remediation),
                            module=self.name,
                            confidence="medium",
                            references=[str(file), *related],
                        )
                    )
            lower = text.lower()
            for advisory in advisories:
                if advisory.detection_hint.lower() in lower:
                    advisory_hits.append(advisory.id)
        req_files = list(root.rglob("requirements*.txt")) + list(root.rglob("pyproject.toml"))
        for file in req_files:
            reviewed_files += 1
            text = file.read_text(encoding="utf-8").lower()
            for advisory in advisories:
                if advisory.package in text and any(token in text for token in ["==", "<", "<="]):
                    findings.append(
                        Finding(
                            title=f"Potential vulnerable dependency: {advisory.package}",
                            severity=Severity.HIGH,
                            description=f"Dependency manifest {file.name} references {advisory.package}; review against {advisory.id} affected versions {', '.join(advisory.affected_versions)}.",
                            remediation=Remediation(summary=f"Upgrade {advisory.package} beyond the affected range and verify exploitability in context.", quick_win=True),
                            module=self.name,
                            confidence="medium",
                            references=[str(file), f"{advisory.id}: {advisory.summary}"],
                        )
                    )
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary=f"Reviewed {reviewed_files} files and found {len(findings)} issues.",
            findings=findings,
            artifacts={"path": str(root), "reviewed_files": reviewed_files, "rule_count": len(RULES), "cve_hits": sorted(set(advisory_hits))},
        )
