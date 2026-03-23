from pathlib import Path

from aegisforge_core import AegisForgeService


def test_dependency_lens_builds_sbom_artifact(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "requirements.txt").write_text('pyyaml==5.3\n', encoding="utf-8")
    result = AegisForgeService(tmp_path).analyze_dependencies(repo)
    assert result.artifacts["sbom"][0]["package"] == "pyyaml"
