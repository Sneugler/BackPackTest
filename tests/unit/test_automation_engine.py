from pathlib import Path

from aegisforge_core import AegisForgeService


def test_automation_engine_plans_actions_from_project_state(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Auto
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
    result = service.plan_automation(project.id)
    assert result.artifacts["planned_actions"][0]["actions"][0] == "SurfaceMapper"
