from pathlib import Path

from aegisforge_core import AegisForgeService


def test_evidence_vault_filters_project_evidence(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Evidence
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform review.
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    note = tmp_path / "http.log"
    note.write_text("GET /health", encoding="utf-8")
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)
    service.import_evidence(project.id, note)
    result = service.search_evidence(project.id, "http")
    assert result.artifacts["items"][0]["path"].endswith("http.log")
