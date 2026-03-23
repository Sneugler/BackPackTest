from pathlib import Path

from aegisforge_core import AegisForgeService
from aegisforge_models.models import Finding, Remediation, Severity


def test_report_smith_creates_executive_summary(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Reports
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform review.
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    project.findings.append(Finding(title="Admin exposure", severity=Severity.HIGH, description="desc", remediation=Remediation(summary="fix"), module="test"))
    service.repo.save_project(project)
    result = service.prepare_report_pack(project.id)
    assert result.artifacts["executive_summary"]["top_risks"][0] == "Admin exposure"
