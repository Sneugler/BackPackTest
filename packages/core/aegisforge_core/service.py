from __future__ import annotations

from collections import Counter
from pathlib import Path
import json

import yaml

from aegisforge_config import load_settings
from aegisforge_core.module_base import ModuleContext
from aegisforge_core.module_registry import ModuleRegistry
from aegisforge_evidence import EvidenceManager
from aegisforge_logging import get_logger
from aegisforge_models.models import DetectionSuggestion, EnvironmentType, Finding, ModuleResult, OperatorNote, Project, ProjectEvent
from aegisforge_parsers import parse_authorization_text, parse_targets
from aegisforge_reporting import ReportRenderer
from aegisforge_storage import SQLiteRepository

logger = get_logger(__name__)


class AegisForgeService:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = Path(base_dir or Path.cwd())
        self.settings = load_settings(self.base_dir)
        self.workspace = self.base_dir / self.settings.workspace_dir
        self.repo = SQLiteRepository(self.workspace / self.settings.database_name)
        self.evidence_manager = EvidenceManager(self.workspace / self.settings.evidence_dir)
        self.renderer = ReportRenderer(self.workspace / self.settings.reports_dir)
        self.modules = ModuleRegistry()

    def _context(self, project: Project | None, **options) -> ModuleContext:
        return ModuleContext(project=project, base_dir=self.base_dir, options=options)

    def _persist_result(self, result: ModuleResult) -> ModuleResult:
        if result.project_id not in {"ad-hoc", "platform"}:
            self.repo.save_module_result(result)
        return result

    def init_workspace(self) -> Path:
        self.workspace.mkdir(parents=True, exist_ok=True)
        for child in [self.settings.reports_dir, self.settings.evidence_dir, self.settings.exports_dir]:
            (self.workspace / child).mkdir(parents=True, exist_ok=True)
        return self.workspace

    def doctor(self) -> dict[str, object]:
        workspace = self.init_workspace()
        return {
            "workspace": str(workspace),
            "database": str(self.workspace / self.settings.database_name),
            "reports_dir": str(self.workspace / self.settings.reports_dir),
            "evidence_dir": str(self.workspace / self.settings.evidence_dir),
            "project_count": len(self.repo.list_projects()),
            "module_count": len(self.modules.modules),
        }

    def list_projects(self) -> list[dict[str, object]]:
        return self.repo.list_projects()

    def portfolio_summary(self) -> dict[str, object]:
        projects = self.repo.list_projects()
        findings_by_severity: Counter[str] = Counter()
        evidence_count = 0
        target_count = 0
        project_summaries = []
        for item in projects:
            project = self.repo.load_project(item["id"])
            dashboard = self.project_findings(project.id)
            counts = dashboard.artifacts["counts"]
            findings_by_severity.update(counts["by_severity"])
            evidence_count += len(project.evidence)
            target_count += len(project.targets)
            project_summaries.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "targets": len(project.targets),
                    "evidence": len(project.evidence),
                    "findings": counts["total"],
                    "quick_wins": counts["quick_wins"],
                }
            )
        return {
            "project_count": len(projects),
            "target_count": target_count,
            "evidence_count": evidence_count,
            "findings_by_severity": dict(findings_by_severity),
            "projects": project_summaries,
        }

    def create_project(self, spec_path: Path) -> Project:
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        scope, roe, auth = parse_authorization_text(data["authorization_text"], locator=str(spec_path))
        project = Project(name=data["name"], environment_type=EnvironmentType(data["environment_type"]), authorization_evidence=auth, rules_of_engagement=roe, scope=scope, project_path=str(self.base_dir))
        project.notes.append(OperatorNote(body="Project created from specification.", tags=["project", "bootstrap"]))
        project.events.append(ProjectEvent(event_type="project.created", message="Project created", metadata={"spec": str(spec_path)}))
        self.repo.save_project(project)
        return project

    def bootstrap_project(self, spec_path: Path, targets_path: Path | None = None) -> Project:
        self.init_workspace()
        project = self.create_project(spec_path)
        if targets_path:
            project = self.add_targets(project.id, targets_path)
        return project

    def add_targets(self, project_id: str, path: Path) -> Project:
        project = self.repo.load_project(project_id)
        targets = parse_targets(path)
        project.targets.extend(targets)
        project.events.append(ProjectEvent(event_type="surface.imported", message=f"Imported {len(targets)} targets", metadata={"path": str(path)}))
        self.repo.save_project(project)
        return project

    def review_scope(self, text_path: Path) -> ModuleResult:
        scope, roe, evidence = parse_authorization_text(text_path.read_text(encoding="utf-8"), locator=str(text_path))
        summary = f"Readiness={scope.readiness.value}; in_scope={len(scope.in_scope_assets)}; allowed={len(roe.allowed_actions)}"
        return ModuleResult(module_name="PermissionScope", project_id="ad-hoc", summary=summary, evidence=[], artifacts={"scope": scope.model_dump(), "roe": roe.model_dump(), "auth_evidence": [item.model_dump(mode="json") for item in evidence]})

    def map_surface(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("SurfaceMapper").run(self._context(project)))

    def import_evidence(self, project_id: str, path: Path, module: str = "evidence_vault") -> Project:
        project = self.repo.load_project(project_id)
        items = [path] if path.is_file() else [candidate for candidate in path.iterdir() if candidate.is_file()]
        for item in items:
            evidence = self.evidence_manager.ingest_path(item, module=module, summary=f"Imported {item.name}")
            project.evidence.append(evidence)
        project.events.append(ProjectEvent(event_type="evidence.imported", message=f"Imported {len(items)} evidence items", metadata={"path": str(path)}))
        self.repo.save_project(project)
        return project

    def search_evidence(self, project_id: str, query: str = "") -> ModuleResult:
        project = self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("EvidenceVault").run(self._context(project, query=query)))

    def audit_config(self, path: Path, project_id: str = "ad-hoc", target_type: str = "generic") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        inferred = target_type
        name = path.name.lower()
        if inferred == "generic":
            if "docker-compose" in name:
                inferred = "docker-compose"
            elif name == "dockerfile":
                inferred = "dockerfile"
            elif name.endswith((".tf", ".tfvars")):
                inferred = "terraform"
            elif "workflow" in str(path).lower() or ".github" in str(path).lower():
                inferred = "github-actions"
        return self._persist_result(self.modules.get("ConfigAudit").run(self._context(project, path=str(path), target_type=inferred)))

    def audit_code(self, path: Path, project_id: str = "ad-hoc") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("CodeGuard").run(self._context(project, path=str(path))))


    def scan_secrets(self, path: Path, project_id: str = "ad-hoc") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("SecretScanner").run(self._context(project, path=str(path))))

    def analyze_dependencies(self, path: Path, project_id: str = "ad-hoc") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("DependencyLens").run(self._context(project, path=str(path))))

    def analyze_api_schema(self, path: Path, project_id: str = "ad-hoc") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("APIGuard").run(self._context(project, path=str(path))))

    def map_detections(self, findings: list[Finding], project_id: str = "ad-hoc") -> ModuleResult:
        suggestions = []
        for finding in findings:
            sigma = f"title: {finding.title}\nlogsource: application\ndetection:\n  keywords:\n    - {finding.title}\n"
            suggestions.append(DetectionSuggestion(title=f"Detect {finding.title}", telemetry_requirements=["process_creation", "application_logs"], sigma_like_rule=sigma, tuning_notes=["Tune per application baseline."], false_positive_notes=["Administrative maintenance can resemble this behavior."]))
        result = ModuleResult(module_name="DetectionForge", project_id=project_id, summary=f"Generated {len(suggestions)} detection ideas.", artifacts={"detections": [item.model_dump() for item in suggestions]})
        return self._persist_result(result)

    def prioritize_risk(self, findings: list[Finding], project_id: str = "ad-hoc") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("RiskPrioritizer").run(self._context(project, findings=findings)))

    def harden_dockerfile(self, path: Path, project_id: str = "ad-hoc") -> ModuleResult:
        project = None if project_id == "ad-hoc" else self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("HardeningWorkbench").run(self._context(project, path=str(path), target_type="dockerfile")))

    def run_engagement_flow(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        project.ensure_authorized()
        return self._persist_result(self.modules.get("EngagementFlow").run(self._context(project)))

    def build_emulation_plan(self, scenario_path: Path, project_id: str | None = None) -> ModuleResult:
        project = self.repo.load_project(project_id) if project_id else None
        payload = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
        roe_id = project.rules_of_engagement.id if project else None
        return self._persist_result(self.modules.get("EmulationLab").run(self._context(project, scenario=payload, rules_of_engagement_id=roe_id)))

    def operator_status(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        result = self.modules.get("OperatorWorkbench").run(self._context(project))
        result.artifacts["module_history"] = self.repo.list_module_results(project_id)
        return self._persist_result(result)

    def project_findings(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        findings = []
        for finding in project.findings:
            record = finding.model_dump(mode="json")
            record["source"] = "project"
            findings.append(record)

        for module_result in self.repo.list_module_result_payloads(project_id):
            for finding in module_result["result"].get("findings", []):
                finding_record = dict(finding)
                finding_record["source"] = module_result["module_name"]
                finding_record["recorded_at"] = module_result["created_at"]
                findings.append(finding_record)

        severity_counts = dict(Counter(item["severity"] for item in findings))
        source_counts = dict(Counter(item["source"] for item in findings))
        quick_wins = [
            item for item in findings if item.get("remediation", {}).get("quick_win")
        ]
        return self._persist_result(
            ModuleResult(
                module_name="FindingsDashboard",
                project_id=project_id,
                summary=f"Prepared findings dashboard with {len(findings)} findings.",
                artifacts={
                    "findings": findings,
                    "counts": {
                        "total": len(findings),
                        "by_severity": severity_counts,
                        "by_source": source_counts,
                        "quick_wins": len(quick_wins),
                    },
                    "project": {"id": project.id, "name": project.name},
                },
            )
        )

    def plan_toolkit(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("ToolkitPlanner").run(self._context(project)))

    def run_preflight(self, project_id: str, requested_targets: list[str] | None = None, planned_actions: list[str] | None = None) -> ModuleResult:
        project = self.repo.load_project(project_id)
        return self._persist_result(
            self.modules.get("PreflightGuard").run(
                self._context(project, requested_targets=requested_targets or [], planned_actions=planned_actions or [])
            )
        )

    def export_toolkit_evidence(self, project_id: str) -> dict[str, str]:
        project = self.repo.load_project(project_id)
        toolkit = self.plan_toolkit(project_id)
        export_dir = self.workspace / self.settings.exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        json_path = export_dir / f"{project.id}-toolkit-evidence.json"
        md_path = export_dir / f"{project.id}-toolkit-evidence.md"
        payload = {
            "project": {"id": project.id, "name": project.name},
            "toolkit_plan": toolkit.model_dump(mode="json"),
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        lines = [
            f"# Toolkit Evidence Export: {project.name}",
            "",
            f"Project ID: `{project.id}`",
            "",
            "## Path of Least Resistance Ranking",
        ]
        for item in toolkit.artifacts["path_ranking"]:
            lines.append(
                f"- P{item['priority']}: {item['title']} (score={item['least_resistance_score']}, blocked={item['blocked_by_roe']})"
            )
        lines.append("")
        lines.append("## Validation Paths")
        for path in toolkit.artifacts["validation_paths"]:
            lines.extend(
                [
                    f"### {path['title']}",
                    f"- Entry method: {path['entry_method']}",
                    f"- Objective: {path['objective']}",
                    f"- MITRE ATT&CK: {', '.join(path['mitre_techniques']) or 'n/a'}",
                    f"- Defensive methods: {', '.join(path['defensive_methods']) or 'n/a'}",
                    f"- Guardrails: {', '.join(path['guardrails']) or 'n/a'}",
                ]
            )
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path)}

    def plan_campaign(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        toolkit = self.plan_toolkit(project_id)
        validation_paths = toolkit.artifacts.get("validation_paths", [])
        return self._persist_result(
            self.modules.get("CampaignPlanner").run(self._context(project, validation_paths=validation_paths))
        )


    def plan_automation(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("AutomationEngine").run(self._context(project)))

    def inspect_upgrades(self, project_id: str | None = None) -> ModuleResult:
        project = self.repo.load_project(project_id) if project_id else None
        return self._persist_result(self.modules.get("UpgradeEngine").run(self._context(project)))

    def prepare_report_pack(self, project_id: str) -> ModuleResult:
        project = self.repo.load_project(project_id)
        return self._persist_result(self.modules.get("ReportSmith").run(self._context(project)))

    def build_report(self, project_id: str, report_type: str = "assessment") -> Project:
        project = self.repo.load_project(project_id)
        pack = self.prepare_report_pack(project_id)
        report = self.renderer.render_project_report(project, report_type=report_type, report_pack=pack.artifacts)
        project.events.append(ProjectEvent(event_type="report.built", message="Rendered project report", metadata={"paths": report.output_paths}))
        self.repo.save_project(project)
        return project
