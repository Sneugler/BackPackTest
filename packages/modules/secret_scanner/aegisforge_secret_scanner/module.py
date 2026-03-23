from __future__ import annotations

import re
from pathlib import Path

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import Finding, ModuleResult, Remediation, Severity


PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "Potential AWS access key"),
    (r"-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----", "Private key material"),
    (r"ghp_[A-Za-z0-9]{36}", "Potential GitHub token"),
    (r'''(?i)api[_-]?key\s*=\s*['\"][A-Za-z0-9_\-]{12,}['\"]''', "Potential API key assignment"),
]


class SecretScannerModule(BaseModule):
    name = "SecretScanner"

    def run(self, context: ModuleContext) -> ModuleResult:
        root = Path(context.options["path"])
        findings: list[Finding] = []
        reviewed_files = 0
        for file in root.rglob("*"):
            if not file.is_file() or file.suffix in {".png", ".jpg", ".gif", ".db"}:
                continue
            reviewed_files += 1
            text = file.read_text(encoding="utf-8", errors="ignore")
            for pattern, title in PATTERNS:
                if re.search(pattern, text):
                    findings.append(
                        Finding(
                            title=title,
                            severity=Severity.HIGH,
                            description=f"Detected a secret-like pattern in {file}.",
                            remediation=Remediation(summary="Rotate the secret, remove it from source control, and move it to a managed secret store.", quick_win=True),
                            module=self.name,
                            confidence="medium",
                            references=[str(file)],
                        )
                    )
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary=f"Reviewed {reviewed_files} files and found {len(findings)} potential secrets.",
            findings=findings,
            artifacts={"reviewed_files": reviewed_files, "pattern_count": len(PATTERNS)},
        )
