from pathlib import Path

from aegisforge_core import AegisForgeService


def test_code_guard_finds_multiple_patterns(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    sample = repo / "app.py"
    sample.write_text(
        """import subprocess
import yaml
SECRET = 'x'

def load_blob(data):
    yaml.load(data)
    return subprocess.check_output('id', shell=True)
""",
        encoding="utf-8",
    )
    result = AegisForgeService(tmp_path).audit_code(repo)
    titles = {finding.title for finding in result.findings}
    assert "Command execution surface" in titles
    assert "Unsafe YAML loading" in titles
    assert "Potential hardcoded secret" in titles
