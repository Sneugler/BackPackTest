from pathlib import Path

from aegisforge_core import AegisForgeService


def test_campaign_planner_generates_phases_from_toolkit_paths(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Campaign
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform configuration review and validation planning.
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)

    result = service.plan_campaign(project.id)

    assert result.module_name == "CampaignPlanner"
    assert len(result.artifacts["phases"]) == 3
    assert "authorization_and_preflight" == result.artifacts["phases"][0]["name"]
    assert result.artifacts["mitre_focus"]
