from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import ModuleResult, ToolkitRecommendation, ValidationPath


SAFE_TOOL_CATALOG = [
    {
        "phase": "scoping",
        "capability": "authorization review",
        "tool_name": "PermissionScope",
        "safe_use": "Validate in-scope targets, allowed actions, and approval contacts before any assessment work.",
        "requires_evidence": True,
        "references": ["scope.review", "project.create"],
    },
    {
        "phase": "recon",
        "capability": "asset inventory",
        "tool_name": "SurfaceMapper",
        "safe_use": "Summarize known targets from approved inventories without active discovery outside the provided scope.",
        "requires_evidence": False,
        "references": ["surface.import", "surface.map"],
    },
    {
        "phase": "review",
        "capability": "configuration analysis",
        "tool_name": "ConfigAudit",
        "safe_use": "Review approved configuration files for risky settings and known vulnerability patterns.",
        "requires_evidence": False,
        "references": ["audit.config"],
    },
    {
        "phase": "review",
        "capability": "code analysis",
        "tool_name": "CodeGuard",
        "safe_use": "Inspect authorized repositories for insecure coding patterns and secret exposure.",
        "requires_evidence": False,
        "references": ["audit.code", "audit.secrets", "audit.dependencies"],
    },
    {
        "phase": "api",
        "capability": "schema review",
        "tool_name": "APIGuard",
        "safe_use": "Review provided API schemas and enumerate documented paths without brute forcing endpoints.",
        "requires_evidence": False,
        "references": ["api.review"],
    },
    {
        "phase": "validation",
        "capability": "scenario planning",
        "tool_name": "EmulationLab",
        "safe_use": "Prepare controlled scenario timelines, telemetry expectations, and after-action review templates.",
        "requires_evidence": True,
        "references": ["emulate.plan"],
    },
    {
        "phase": "reporting",
        "capability": "remediation packaging",
        "tool_name": "ReportSmith",
        "safe_use": "Turn findings into executive summaries, technical appendices, and remediation roadmaps.",
        "requires_evidence": True,
        "references": ["report.pack", "report.build"],
    },
]

VALIDATION_PATH_CATALOG = [
    {
        "title": "Identity control validation",
        "entry_method": "authorized account workflow review",
        "objective": "Validate authentication logging, alerting, and approval boundaries around identity-centric access paths.",
        "prerequisites": [
            "Approved test account or lab identity",
            "Rules of engagement explicitly allow review or validation activity",
        ],
        "allowed_actions": ["review identity flow", "exercise approved login path", "collect telemetry"],
        "evidence_to_collect": ["authentication logs", "identity alerts", "operator notes"],
        "guardrails": ["No credential attacks", "No account lockout generation", "Use approved identities only"],
        "mitre_techniques": ["T1078", "T1110"],
        "defensive_methods": ["MFA enforcement", "authentication anomaly detection", "account lockout monitoring"],
    },
    {
        "title": "Exposed service posture review",
        "entry_method": "in-scope service and configuration inspection",
        "objective": "Validate whether exposed services are documented, hardened, and visible to monitoring without active exploitation.",
        "prerequisites": [
            "Approved target inventory",
            "Relevant configuration or schema artifacts",
        ],
        "allowed_actions": ["inspect known targets", "review configuration", "compare against baseline"],
        "evidence_to_collect": ["service inventory", "config excerpts", "screenshots or exported findings"],
        "guardrails": ["No brute force activity", "No unapproved payload delivery", "Stay within named targets"],
        "mitre_techniques": ["T1190", "T1595"],
        "defensive_methods": ["service hardening", "external attack surface monitoring", "WAF/ingress review"],
    },
    {
        "title": "Application abuse-case emulation",
        "entry_method": "approved user-path and scenario exercise",
        "objective": "Exercise expected control points for high-risk user journeys and confirm telemetry or response readiness.",
        "prerequisites": [
            "Documented scenario objective",
            "Rollback/containment contact",
        ],
        "allowed_actions": ["scenario planning", "walkthrough execution", "telemetry review"],
        "evidence_to_collect": ["scenario timeline", "alerts observed", "control owner feedback"],
        "guardrails": ["No destructive actions", "No persistence", "Stop if behavior deviates from authorization"],
        "mitre_techniques": ["T1199", "T1078"],
        "defensive_methods": ["detection engineering", "application logging review", "session control validation"],
    },
]


class ToolkitPlannerModule(BaseModule):
    name = "ToolkitPlanner"

    @staticmethod
    def _least_resistance_score(entry: dict[str, object], blocked: bool) -> int:
        if blocked:
            return 0
        prerequisites = len(entry.get("prerequisites", []))
        guardrails = len(entry.get("guardrails", []))
        allowed_actions = len(entry.get("allowed_actions", []))
        score = 100 - (prerequisites * 12) - (guardrails * 5) + (allowed_actions * 2)
        return max(score, 1)

    def run(self, context: ModuleContext) -> ModuleResult:
        project = context.project
        if project is None:
            raise ValueError("ToolkitPlanner requires a project context.")

        forbidden = [item.lower() for item in project.rules_of_engagement.forbidden_actions]
        allowed = [item.lower() for item in project.rules_of_engagement.allowed_actions]

        recommendations = []
        for entry in SAFE_TOOL_CATALOG:
            blocked = False
            block_reason = None
            if entry["phase"] == "recon" and any("discovery" in item or "scanning" in item for item in forbidden):
                blocked = True
                block_reason = "Rules of engagement forbid discovery/scanning activity."
            if entry["phase"] == "validation" and not any(
                keyword in " ".join(allowed)
                for keyword in ["review", "validation", "emulation", "assessment"]
            ):
                blocked = True
                block_reason = "Allowed actions do not clearly authorize validation or emulation work."

            recommendations.append(
                ToolkitRecommendation(
                    phase=entry["phase"],
                    capability=entry["capability"],
                    tool_name=entry["tool_name"],
                    safe_use=entry["safe_use"],
                    requires_evidence=entry["requires_evidence"],
                    references=entry["references"],
                    blocked_by_roe=blocked,
                    block_reason=block_reason,
                )
            )

        validation_paths = []
        for entry in VALIDATION_PATH_CATALOG:
            blocked = False
            block_reason = None
            if "identity" in entry["title"].lower() and not any(
                keyword in " ".join(allowed) for keyword in ["review", "validation", "assessment", "authenticated"]
            ):
                blocked = True
                block_reason = "Rules of engagement do not clearly authorize identity-path validation."
            if any("scanning" in item for item in forbidden) and "service posture" in entry["title"].lower():
                blocked = True
                block_reason = "Rules of engagement restrict service discovery/scanning activities."
            score = self._least_resistance_score(entry, blocked)
            validation_paths.append(
                ValidationPath(
                    title=entry["title"],
                    entry_method=entry["entry_method"],
                    objective=entry["objective"],
                    prerequisites=entry["prerequisites"],
                    allowed_actions=entry["allowed_actions"],
                    evidence_to_collect=entry["evidence_to_collect"],
                    guardrails=entry["guardrails"],
                    mitre_techniques=entry["mitre_techniques"],
                    defensive_methods=entry["defensive_methods"],
                    least_resistance_score=score,
                    blocked_by_roe=blocked,
                    block_reason=block_reason,
                )
            )

        ready = [item for item in recommendations if not item.blocked_by_roe]
        blocked = [item for item in recommendations if item.blocked_by_roe]
        ranked_paths = sorted(
            validation_paths,
            key=lambda item: (item.blocked_by_roe, -item.least_resistance_score, item.title),
        )
        for index, item in enumerate(ranked_paths, start=1):
            item.priority = index
        ready_paths = [item for item in ranked_paths if not item.blocked_by_roe]
        blocked_paths = [item for item in ranked_paths if item.blocked_by_roe]
        return ModuleResult(
            module_name=self.name,
            project_id=project.id,
            summary=f"Prepared authorized toolkit plan with {len(ready)} ready recommendations.",
            artifacts={
                "recommendations": [item.model_dump(mode="json") for item in recommendations],
                "validation_paths": [item.model_dump(mode="json") for item in ranked_paths],
                "path_ranking": [
                    {
                        "priority": item.priority,
                        "title": item.title,
                        "least_resistance_score": item.least_resistance_score,
                        "blocked_by_roe": item.blocked_by_roe,
                        "rationale": (
                            item.block_reason
                            if item.blocked_by_roe
                            else "Fewer prerequisites and lower execution friction make this path easier to validate."
                        ),
                    }
                    for item in ranked_paths
                ],
                "counts": {
                    "ready": len(ready),
                    "blocked": len(blocked),
                    "ready_paths": len(ready_paths),
                    "blocked_paths": len(blocked_paths),
                },
                "rules_of_engagement": {
                    "allowed_actions": project.rules_of_engagement.allowed_actions,
                    "forbidden_actions": project.rules_of_engagement.forbidden_actions,
                },
            },
        )
