from pathlib import Path

from aegisforge_core import AegisForgeService


def test_emulation_plan_contains_review_template(tmp_path: Path):
    scenario = tmp_path / "scenario.yaml"
    scenario.write_text(
        """name: Control Validation
objective: Validate identity telemetry in a lab.
attack_mapping:
  - T1110
success_criteria:
  - Telemetry captured
expected_telemetry:
  - identity alerts
  - authentication logs
""",
        encoding="utf-8",
    )
    result = AegisForgeService(tmp_path).build_emulation_plan(scenario)
    assert result.artifacts["plan"]["scenario"]["name"] == "Control Validation"
    assert len(result.artifacts["review_template"]["observed_vs_expected_template"]) == 2
