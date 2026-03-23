from __future__ import annotations

import re

from aegisforge_models.models import AuthorizationEvidence, ProjectScope, Readiness, RulesOfEngagement

ALLOW_PATTERNS = [r"allowed to ([^.]+)", r"may ([^.]+)"]
FORBID_PATTERNS = [
    r"must not ([^.]+)",
    r"forbidden to ([^.]+)",
    r"forbidden[:\-]\s*([^\n.]+)",
    r"out of scope[:\-]\s*([^\n]+)",
]
TIME_PATTERNS = [r"between ([^.\n]+)", r"window[:\-]\s*([^\n]+)"]
CONTACT_PATTERNS = [r"contact[:\-]\s*([\w@.\- ,]+)"]


def _capture(patterns: list[str], text: str) -> list[str]:
    values: list[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            values.append(match.group(1).strip())
    return values


def _extract_in_scope(text: str) -> list[str]:
    assets: list[str] = []
    for line in text.splitlines():
        if line.lower().startswith("in scope"):
            _, rhs = line.split(":", 1)
            assets.extend([part.strip().strip('.') for part in rhs.split(",") if part.strip()])
    return assets


def parse_authorization_text(
    text: str, locator: str = "inline"
) -> tuple[ProjectScope, RulesOfEngagement, list[AuthorizationEvidence]]:
    allowed = _capture(ALLOW_PATTERNS, text)
    forbidden = _capture(FORBID_PATTERNS, text)
    time_limits = _capture(TIME_PATTERNS, text)
    contacts = _capture(CONTACT_PATTERNS, text)
    in_scope = _extract_in_scope(text)
    out_scope = []
    for item in forbidden:
        if any(token in item.lower() for token in ["domain", "host", "service", "."]):
            out_scope.append(item)
    ambiguities = []
    if not allowed:
        ambiguities.append("No explicit allowed actions found.")
    if not in_scope:
        ambiguities.append("No explicit in-scope assets found.")
    readiness = (
        Readiness.GREEN
        if allowed and in_scope and contacts
        else Readiness.YELLOW if (allowed or in_scope) else Readiness.RED
    )
    scope = ProjectScope(
        in_scope_assets=in_scope,
        out_of_scope_assets=out_scope,
        ambiguities=ambiguities,
        readiness=readiness,
    )
    roe = RulesOfEngagement(
        allowed_actions=allowed,
        forbidden_actions=forbidden,
        time_limits=time_limits,
        approval_contacts=contacts,
        notes=ambiguities,
    )
    evidence = [
        AuthorizationEvidence(
            source_type="authorization_text",
            description="Parsed authorization statement",
            locator=locator,
            excerpt=text[:400],
        )
    ]
    return scope, roe, evidence
