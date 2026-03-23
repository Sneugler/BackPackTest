from __future__ import annotations

from aegisforge_core.module_base import BaseModule, ModuleContext
from aegisforge_models.models import EmulationPlan, ModuleResult, Scenario


class EmulationLabModule(BaseModule):
    name = "EmulationLab"

    def run(self, context: ModuleContext) -> ModuleResult:
        payload = context.options["scenario"]
        scenario = payload if isinstance(payload, Scenario) else Scenario(**payload)
        telemetry = scenario.expected_telemetry or ["operator to define telemetry expectations"]
        plan = EmulationPlan(
            scenario=scenario,
            timeline=[
                "Kickoff and authorization verification",
                "Precondition validation",
                "Controlled scenario execution",
                "Telemetry and control review",
                "After-action analysis",
            ],
            controls_under_test=context.options.get("controls_under_test", ["EDR", "SIEM", "identity controls"]),
            gap_analysis=[
                f"Verify telemetry coverage for: {requirement}" for requirement in telemetry
            ],
            rules_of_engagement_id=context.options.get("rules_of_engagement_id"),
        )
        review = {
            "scenario": scenario.name,
            "attack_mapping": scenario.attack_mapping,
            "success_criteria": scenario.success_criteria,
            "observed_vs_expected_template": [
                {"telemetry": item, "expected": True, "observed": False, "notes": ""}
                for item in telemetry
            ],
        }
        return ModuleResult(
            module_name=self.name,
            project_id=context.project.id if context.project else "ad-hoc",
            summary=f"Prepared emulation plan for {scenario.name}.",
            artifacts={"plan": plan.model_dump(mode="json"), "review_template": review},
        )
