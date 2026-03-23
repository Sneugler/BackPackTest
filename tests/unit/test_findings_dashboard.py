from pathlib import Path

from aegisforge_core import AegisForgeService


def test_project_findings_aggregates_project_and_module_findings(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Findings
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform configuration review.
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    config = tmp_path / "docker-compose.yml"
    config.write_text(
        """services:
  web:
    image: nginx:latest
    privileged: true
""",
        encoding="utf-8",
    )

    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    service.audit_config(config, project_id=project.id)

    result = service.project_findings(project.id)

    assert result.module_name == "FindingsDashboard"
    assert result.artifacts["counts"]["total"] >= 1
    assert result.artifacts["counts"]["by_source"]["ConfigAudit"] >= 1
    assert result.artifacts["findings"][0]["source"] in {"project", "ConfigAudit"}


def test_portfolio_summary_aggregates_project_counts(tmp_path: Path):
    service = AegisForgeService(tmp_path)
    service.init_workspace()

    for name in ("Alpha", "Beta"):
        spec = tmp_path / f"{name.lower()}.yaml"
        spec.write_text(
            f"""name: {name}
environment_type: internal_authorized
authorization_text: |
  In scope: {name.lower()}.example.com
  Allowed to perform configuration review.
  Contact: owner@example.com
""",
            encoding="utf-8",
        )
        config = tmp_path / f"{name.lower()}-docker-compose.yml"
        config.write_text(
            """services:
  web:
    image: nginx:latest
    privileged: true
""",
            encoding="utf-8",
        )
        project = service.create_project(spec)
        service.audit_config(config, project_id=project.id)

    summary = service.portfolio_summary()

    assert summary["project_count"] == 2
    assert summary["findings_by_severity"]["high"] >= 2
    assert len(summary["projects"]) == 2
