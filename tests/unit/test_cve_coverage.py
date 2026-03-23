from pathlib import Path

from aegisforge_core import AegisForgeService


def test_code_guard_reports_cve_reference_for_unsafe_yaml(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("import yaml\n\ndef parse(data):\n    return yaml.load(data)\n", encoding="utf-8")
    result = AegisForgeService(tmp_path).audit_code(repo)
    refs = " ".join(ref for finding in result.findings for ref in finding.references)
    assert "CVE-2020-14343" in refs


def test_module_results_are_persisted_for_project_context(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Persist
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
    service.map_surface(project.id)
    overview = service.operator_status(project.id)
    assert overview.artifacts["module_history"][0]["module_name"] in {"OperatorWorkbench", "SurfaceMapper"}
