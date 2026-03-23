from pathlib import Path

from aegisforge_core import AegisForgeService


def test_project_creation_and_reporting(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Demo
environment_type: internal_authorized
authorization_text: |
  In scope: demo.example.com
  Allowed to perform configuration review.
  Contact: demo@example.com
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    service.build_report(project.id)
    report_path = tmp_path / ".aegisforge" / "reports" / f"{project.id}-assessment.md"
    assert report_path.exists()
