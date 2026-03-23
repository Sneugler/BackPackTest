from __future__ import annotations

from collections import Counter

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult, TargetGroup


class SurfaceMapperModule(BaseModule):
    name = "SurfaceMapper"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("SurfaceMapper requires a project context.")
        by_owner: dict[str, list] = {}
        for target in project.targets:
            by_owner.setdefault(target.owner or "unassigned", []).append(target)
        groups = [
            TargetGroup(name=owner, targets=targets, description=f"Assets owned by {owner}")
            for owner, targets in by_owner.items()
        ]
        sensitivity = Counter(target.sensitivity or "unspecified" for target in project.targets)
        criticality = Counter(target.criticality or "unspecified" for target in project.targets)
        summary = f"Organized {len(project.targets)} targets into {len(groups)} ownership groups."
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary=summary,
            artifacts={
                "groups": [group.model_dump() for group in groups],
                "sensitivity_breakdown": dict(sensitivity),
                "criticality_breakdown": dict(criticality),
            },
        )
