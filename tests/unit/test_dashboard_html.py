from pathlib import Path

import aegisforge_dashboard.app as dashboard_app
from aegisforge_core import AegisForgeService


def test_dashboard_home_renders_html(tmp_path: Path):
    dashboard_app.service = AegisForgeService(tmp_path)
    dashboard_app.service.init_workspace()

    html = dashboard_app.dashboard_home()

    assert "<html" in html
    assert "AegisForge Dashboard" in html


def test_project_dashboard_renders_ranked_paths(tmp_path: Path):
    dashboard_app.service = AegisForgeService(tmp_path)
    dashboard_app.service.init_workspace()

    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: GUI
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform configuration review and validation planning.
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    project = dashboard_app.service.create_project(spec)

    html = dashboard_app.project_dashboard(project.id)

    assert "Path of least resistance" in html
    assert "Project dashboard" in html
    assert "ready" in html or "review" in html
    assert "Campaign plan" in html
