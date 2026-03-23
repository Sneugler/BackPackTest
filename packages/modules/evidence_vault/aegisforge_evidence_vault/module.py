from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult


class EvidenceVaultModule(BaseModule):
    name = "EvidenceVault"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("EvidenceVault requires a project context.")
        query = context.options.get("query", "").lower()
        items = []
        for evidence in project.evidence:
            haystack = " ".join([evidence.summary, evidence.path, " ".join(evidence.tags)]).lower()
            if not query or query in haystack:
                items.append(evidence.model_dump(mode="json"))
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary=f"Found {len(items)} evidence items matching query.",
            artifacts={"query": query, "items": items},
        )
