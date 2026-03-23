from pathlib import Path

from aegisforge_core import AegisForgeService


def test_config_audit_flags_risky_configuration(tmp_path: Path):
    sample = tmp_path / "docker-compose.yml"
    sample.write_text(
        """services:
  web:
    image: nginx:latest
    privileged: true
""",
        encoding="utf-8",
    )
    result = AegisForgeService(tmp_path).audit_config(sample)
    assert len(result.findings) >= 2
