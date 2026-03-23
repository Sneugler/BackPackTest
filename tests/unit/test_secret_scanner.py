from pathlib import Path

from aegisforge_core import AegisForgeService


def test_secret_scanner_finds_api_key(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "secrets.env").write_text('API_KEY="EXAMPLESECRETKEY12345"\n', encoding="utf-8")
    result = AegisForgeService(tmp_path).scan_secrets(repo)
    assert result.findings[0].title == "Potential API key assignment"
