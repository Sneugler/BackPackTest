from pathlib import Path

from aegisforge_core import AegisForgeService


def test_preflight_guard_flags_unknown_targets_and_blocked_actions(tmp_path: Path):
    spec = tmp_path / "project.yaml"
    spec.write_text(
        """name: Preflight
environment_type: internal_authorized
authorization_text: |
  In scope: app.example.com
  Allowed to perform configuration review.
  Forbidden: network scanning
  Contact: owner@example.com
""",
        encoding="utf-8",
    )
    service = AegisForgeService(tmp_path)
    service.init_workspace()
    project = service.create_project(spec)

    result = service.run_preflight(
        project.id,
        requested_targets=["app.example.com", "unknown.example.com"],
        planned_actions=["configuration review", "network scanning"],
    )

    assert result.module_name == "PreflightGuard"
    assert result.artifacts["in_scope_targets"] == ["app.example.com"]
    assert result.artifacts["unknown_targets"] == ["unknown.example.com"]
    assert result.artifacts["blocked_actions"] == ["network scanning"]
    assert result.artifacts["ready"] is False
