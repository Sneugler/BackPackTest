from __future__ import annotations

from pathlib import Path

from aegisforge_core.advisories import load_advisories
from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import Finding, ModuleResult, Remediation, Severity


class DependencyLensModule(BaseModule):
    name = "DependencyLens"

    def run(self, context: ModuleContext) -> ModuleResult:
        root = Path(context.options["path"])
        advisories = load_advisories()
        manifests = list(root.rglob("requirements*.txt")) + list(root.rglob("pyproject.toml"))
        sbom = []
        findings: list[Finding] = []
        for manifest in manifests:
            text = manifest.read_text(encoding="utf-8", errors="ignore").lower()
            for advisory in advisories:
                if advisory.package in text:
                    sbom.append({"manifest": str(manifest), "package": advisory.package, "advisory": advisory.id})
                    findings.append(
                        Finding(
                            title=f"Review dependency: {advisory.package}",
                            severity=Severity.MEDIUM,
                            description=f"{manifest.name} references {advisory.package}; compare installed version against {advisory.id} affected range {', '.join(advisory.affected_versions)}.",
                            remediation=Remediation(summary=f"Pin and upgrade {advisory.package} after validating compatibility."),
                            module=self.name,
                            confidence="medium",
                            references=[str(manifest), f"{advisory.id}: {advisory.summary}"],
                        )
                    )
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary=f"Analyzed {len(manifests)} dependency manifests.",
            findings=findings,
            artifacts={"sbom": sbom, "manifest_count": len(manifests)},
        )
