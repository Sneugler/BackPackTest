from pathlib import Path

from aegisforge_core import AegisForgeService


def test_engagement_flow_builds_steps_and_checklist(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Flow
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform review.
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    targets = tmp_path / "targets.yaml"
    targets.write_text(
        """targets:
  - value: app.example.com
    owner: web
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    service.add_targets(project.id, targets)
    result = service.run_engagement_flow(project.id)
    assert result.artifacts["steps"][0]["name"] == "authorization_precheck"
    assert any("red-team" in item.lower() for item in result.artifacts["operator_checklist"])
