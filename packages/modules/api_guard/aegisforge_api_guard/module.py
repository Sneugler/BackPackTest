from __future__ import annotations

from pathlib import Path

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import Finding, ModuleResult, Remediation, Severity


HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}


class APIGuardModule(BaseModule):
    name = "APIGuard"

    def run(self, context: ModuleContext) -> ModuleResult:
        spec_path = Path(context.options["path"])
        lines = spec_path.read_text(encoding="utf-8").splitlines()
        findings: list[Finding] = []
        inventory = []
        current_path = None
        current_method = None
        current_has_security = False
        current_indent = None

        def flush_method():
            nonlocal current_method, current_has_security, current_path, current_indent
            if current_path and current_method:
                inventory.append({"path": current_path, "methods": [current_method]})
                if not current_has_security:
                    findings.append(
                        Finding(
                            title="Unauthenticated API operation",
                            severity=Severity.MEDIUM,
                            description=f"{current_method.upper()} {current_path} has no declared security requirement in the schema.",
                            remediation=Remediation(summary="Define explicit authentication/authorization requirements in the API contract and validate them in implementation."),
                            module=self.name,
                            confidence="medium",
                            references=[str(spec_path)],
                        )
                    )
            current_method = None
            current_has_security = False
            current_indent = None

        for raw in lines:
            stripped = raw.strip()
            if not stripped:
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if stripped.startswith("/") and stripped.endswith(":"):
                flush_method()
                current_path = stripped[:-1]
                continue
            token = stripped.rstrip(":")
            if token in HTTP_METHODS:
                flush_method()
                current_method = token
                current_indent = indent
                continue
            if current_method and indent > (current_indent or 0) and stripped.startswith("security"):
                current_has_security = True
            if current_method and indent <= (current_indent or 0) and token not in HTTP_METHODS:
                flush_method()
        flush_method()
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary=f"Parsed API schema and found {len(findings)} operations without declared security.",
            findings=findings,
            artifacts={"inventory": inventory, "path_count": len({item['path'] for item in inventory})},
        )
