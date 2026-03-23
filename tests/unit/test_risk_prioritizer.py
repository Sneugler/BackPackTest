from aegisforge_core import AegisForgeService
from aegisforge_models.models import Finding, Remediation, Severity


def test_risk_prioritizer_orders_by_severity():
    findings = [
        Finding(title="Low", severity=Severity.LOW, description="l", remediation=Remediation(summary="fix"), module="test"),
        Finding(title="High", severity=Severity.HIGH, description="h", remediation=Remediation(summary="fix", quick_win=True), module="test"),
    ]
    result = AegisForgeService().prioritize_risk(findings)
    assert result.artifacts["roadmap"][0]["title"] == "High"
    assert result.artifacts["roadmap"][0]["quick_win"] is True
