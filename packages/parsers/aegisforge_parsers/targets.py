from __future__ import annotations

from pathlib import Path

import yaml

from aegisforge_models.models import AssetType, Target


def classify_asset(value: str) -> AssetType:
    if value.startswith("http://") or value.startswith("https://"):
        return AssetType.URL
    if "/" in value and any(ch.isdigit() for ch in value):
        return AssetType.IP_RANGE
    if value.endswith(".git") or "github.com" in value:
        return AssetType.REPOSITORY
    if value.count(".") >= 2:
        return AssetType.SUBDOMAIN
    if value.count(".") == 1:
        return AssetType.DOMAIN
    return AssetType.HOSTNAME


def parse_targets(path: Path) -> list[Target]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    targets: list[Target] = []
    for item in payload.get("targets", []):
        value = item["value"] if isinstance(item, dict) else str(item)
        meta = item if isinstance(item, dict) else {}
        targets.append(
            Target(
                value=value,
                asset_type=classify_asset(value),
                owner=meta.get("owner"),
                sensitivity=meta.get("sensitivity"),
                criticality=meta.get("criticality"),
                tags=meta.get("tags", []),
                scope_status=meta.get("scope_status", "reviewed"),
            )
        )
    return targets
