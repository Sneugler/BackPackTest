from pathlib import Path

from aegisforge_core import AegisForgeService


def test_surface_mapper_groups_targets_by_owner(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Mapper
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
    sensitivity: internal
    criticality: high
  - value: api.example.com
    owner: web
    sensitivity: confidential
    criticality: critical
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    service.add_targets(project.id, targets)
    result = service.map_surface(project.id)
    assert result.artifacts["groups"][0]["name"] == "web"
    assert result.artifacts["criticality_breakdown"]["high"] == 1
