from pathlib import Path

from aegisforge_core import AegisForgeService


def test_toolkit_planner_recommends_safe_modules(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Toolkit
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

    result = service.plan_toolkit(project.id)

    assert result.module_name == "ToolkitPlanner"
    assert result.artifacts["counts"]["ready"] >= 1
    assert any(item["tool_name"] == "EmulationLab" for item in result.artifacts["recommendations"])
    assert any(item["entry_method"] for item in result.artifacts["validation_paths"])
    assert any("guardrails" in item for item in result.artifacts["validation_paths"])
    assert result.artifacts["path_ranking"][0]["least_resistance_score"] >= result.artifacts["path_ranking"][-1]["least_resistance_score"]
    assert any(item["mitre_techniques"] for item in result.artifacts["validation_paths"])
    assert any(item["defensive_methods"] for item in result.artifacts["validation_paths"])


def test_toolkit_planner_respects_forbidden_discovery_actions(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Restricted Toolkit
environment_type: internal_authorized
authorization_text: |
  In scope: restricted.example.com
  Allowed to perform configuration review.
  Forbidden: network scanning
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)

    result = service.plan_toolkit(project.id)
    surface_mapper = next(
        item for item in result.artifacts["recommendations"] if item["tool_name"] == "SurfaceMapper"
    )

    assert surface_mapper["blocked_by_roe"] is True
    assert "discovery/scanning" in surface_mapper["block_reason"]
    service_posture = next(
        item for item in result.artifacts["validation_paths"] if item["title"] == "Exposed service posture review"
    )
    assert service_posture["blocked_by_roe"] is True


def test_toolkit_evidence_export_writes_json_and_markdown(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Export Toolkit
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

    paths = service.export_toolkit_evidence(project.id)

    assert Path(paths["json"]).exists()
    assert Path(paths["markdown"]).exists()
    assert "toolkit-evidence" in paths["json"]
