from pathlib import Path

from aegisforge_core import AegisForgeService


def test_report_contains_expected_sections(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Golden
environment_type: lab
authorization_text: |
  In scope: lab.example.com
  Allowed to perform validation.
  Contact: lab@example.com
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    service.build_report(project.id, "validation")
    content = (tmp_path / ".aegisforge" / "reports" / f"{project.id}-validation.md").read_text(
        encoding="utf-8"
    )
    assert "## Scope" in content
    assert "## Findings" in content
