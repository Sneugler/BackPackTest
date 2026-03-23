from aegisforge_core import AegisForgeService


def test_upgrade_engine_returns_critiques_and_proposals():
    result = AegisForgeService().inspect_upgrades()
    assert result.artifacts["critiques"][0]["area"] == "architecture"
    assert result.artifacts["proposals"][0]["title"] == "Persist module history"
