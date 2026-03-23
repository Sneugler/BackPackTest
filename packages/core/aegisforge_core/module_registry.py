from __future__ import annotations

from aegisforge_api_guard import APIGuardModule
from aegisforge_automation_engine import AutomationEngineModule
from aegisforge_code_guard import CodeGuardModule
from aegisforge_campaign_planner import CampaignPlannerModule
from aegisforge_config_audit import ConfigAuditModule
from aegisforge_dependency_lens import DependencyLensModule
from aegisforge_emulation_lab import EmulationLabModule
from aegisforge_engagement_flow import EngagementFlowModule
from aegisforge_evidence_vault import EvidenceVaultModule
from aegisforge_hardening_workbench import HardeningWorkbenchModule
from aegisforge_operator_workbench import OperatorWorkbenchModule
from aegisforge_preflight_guard import PreflightGuardModule
from aegisforge_report_smith import ReportSmithModule
from aegisforge_risk_prioritizer import RiskPrioritizerModule
from aegisforge_secret_scanner import SecretScannerModule
from aegisforge_surface_mapper import SurfaceMapperModule
from aegisforge_toolkit_planner import ToolkitPlannerModule
from aegisforge_upgrade_engine import UpgradeEngineModule


class ModuleRegistry:
    def __init__(self) -> None:
        self.modules = {
            SurfaceMapperModule.name: SurfaceMapperModule(),
            CampaignPlannerModule.name: CampaignPlannerModule(),
            ConfigAuditModule.name: ConfigAuditModule(),
            CodeGuardModule.name: CodeGuardModule(),
            HardeningWorkbenchModule.name: HardeningWorkbenchModule(),
            RiskPrioritizerModule.name: RiskPrioritizerModule(),
            EngagementFlowModule.name: EngagementFlowModule(),
            EmulationLabModule.name: EmulationLabModule(),
            OperatorWorkbenchModule.name: OperatorWorkbenchModule(),
            PreflightGuardModule.name: PreflightGuardModule(),
            UpgradeEngineModule.name: UpgradeEngineModule(),
            EvidenceVaultModule.name: EvidenceVaultModule(),
            ReportSmithModule.name: ReportSmithModule(),
            SecretScannerModule.name: SecretScannerModule(),
            DependencyLensModule.name: DependencyLensModule(),
            APIGuardModule.name: APIGuardModule(),
            AutomationEngineModule.name: AutomationEngineModule(),
            ToolkitPlannerModule.name: ToolkitPlannerModule(),
        }

    def get(self, name: str):
        return self.modules[name]
