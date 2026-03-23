from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult


class PreflightGuardModule(BaseModule):
    name = "PreflightGuard"

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("PreflightGuard requires a project context.")

        requested_targets = context.options.get("requested_targets") or []
        planned_actions = context.options.get("planned_actions") or []
        known_targets = {target.value for target in project.targets}
        scoped_assets = set(project.scope.in_scope_assets)
        allowed_targets = known_targets | scoped_assets
        in_scope_targets = [item for item in requested_targets if item in allowed_targets]
        unknown_targets = [item for item in requested_targets if item not in allowed_targets]

        forbidden = [item.lower() for item in project.rules_of_engagement.forbidden_actions]
        blocked_actions = []
        for action in planned_actions:
            lowered = action.lower()
            if any(term in lowered for term in forbidden):
                blocked_actions.append(action)

        checklist = [
            {"name": "authorization_evidence", "status": bool(project.authorization_evidence)},
            {"name": "scope_targets_selected", "status": bool(in_scope_targets or not requested_targets)},
            {"name": "forbidden_action_check", "status": not blocked_actions},
            {"name": "approval_contacts_present", "status": bool(project.rules_of_engagement.approval_contacts)},
        ]
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary="Prepared pre-flight scope and guardrail checklist.",
            artifacts={
                "requested_targets": requested_targets,
                "planned_actions": planned_actions,
                "in_scope_targets": in_scope_targets,
                "unknown_targets": unknown_targets,
                "blocked_actions": blocked_actions,
                "checklist": checklist,
                "ready": all(item["status"] for item in checklist),
            },
        )
