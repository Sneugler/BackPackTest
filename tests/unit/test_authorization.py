from aegisforge_parsers import parse_authorization_text
from aegisforge_models.models import Readiness


def test_parse_authorization_text_extracts_scope_and_contacts():
    text = "In scope: app.example.com, api.example.com. Allowed to perform authenticated review. Contact: sec@example.com"
    scope, roe, evidence = parse_authorization_text(text)
    assert scope.readiness == Readiness.GREEN
    assert "app.example.com" in scope.in_scope_assets
    assert roe.approval_contacts == ["sec@example.com"]
    assert evidence


def test_parse_authorization_text_extracts_forbidden_lines():
    text = """In scope: app.example.com
Allowed to perform configuration review.
Forbidden: network scanning
Contact: sec@example.com
"""
    _, roe, _ = parse_authorization_text(text)
    assert "network scanning" in roe.forbidden_actions
