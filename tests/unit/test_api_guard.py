from pathlib import Path

from aegisforge_core import AegisForgeService


def test_api_guard_flags_unsecured_operation(tmp_path: Path):
    spec = tmp_path / "openapi.yaml"
    spec.write_text(
        """openapi: 3.0.0
info:
  title: Demo API
  version: 1.0.0
paths:
  /health:
    get:
      responses:
        "200":
          description: ok
""",
        encoding="utf-8",
    )
    result = AegisForgeService(tmp_path).analyze_api_schema(spec)
    assert result.findings[0].title == "Unauthenticated API operation"
