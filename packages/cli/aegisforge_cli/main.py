from __future__ import annotations

import json
from pathlib import Path

import typer

from aegisforge_core import AegisForgeService
from aegisforge_models.models import Finding

app = typer.Typer(help="AegisForge authorized-use operator platform")
project_app = typer.Typer()
scope_app = typer.Typer()
surface_app = typer.Typer()
audit_app = typer.Typer()
detect_app = typer.Typer()
evidence_app = typer.Typer()
report_app = typer.Typer()
harden_app = typer.Typer()
flow_app = typer.Typer()
emulate_app = typer.Typer()
upgrade_app = typer.Typer()
operator_app = typer.Typer()
api_app = typer.Typer()
automate_app = typer.Typer()
app.add_typer(project_app, name="project")
app.add_typer(scope_app, name="scope")
app.add_typer(surface_app, name="surface")
app.add_typer(audit_app, name="audit")
app.add_typer(detect_app, name="detect")
app.add_typer(evidence_app, name="evidence")
app.add_typer(report_app, name="report")
app.add_typer(harden_app, name="harden")
app.add_typer(flow_app, name="flow")
app.add_typer(emulate_app, name="emulate")
app.add_typer(upgrade_app, name="upgrade")
app.add_typer(operator_app, name="operator")
app.add_typer(api_app, name="api")
app.add_typer(automate_app, name="automate")


def service() -> AegisForgeService:
    return AegisForgeService()


def emit(payload: object) -> None:
    typer.echo(json.dumps(payload, indent=2, default=str))


@app.command()
def init() -> None:
    emit({"workspace": str(service().init_workspace())})


@app.command()
def doctor() -> None:
    emit(service().doctor())


@project_app.command("create")
def create_project(spec_path: Path) -> None:
    emit(service().create_project(spec_path).model_dump(mode="json"))


@project_app.command("bootstrap")
def bootstrap_project(spec_path: Path, targets_path: Path | None = None) -> None:
    emit(service().bootstrap_project(spec_path, targets_path).model_dump(mode="json"))


@project_app.command("list")
def list_projects() -> None:
    emit(service().list_projects())


@project_app.command("summary")
def project_summary() -> None:
    emit(service().portfolio_summary())


@scope_app.command("review")
def review_scope(text_path: Path) -> None:
    emit(service().review_scope(text_path).model_dump(mode="json"))


@surface_app.command("import")
def import_surface(project_id: str, path: Path) -> None:
    project = service().add_targets(project_id, path)
    emit({"project_id": project.id, "target_count": len(project.targets)})


@surface_app.command("map")
def map_surface(project_id: str) -> None:
    emit(service().map_surface(project_id).model_dump(mode="json"))


@audit_app.command("config")
def audit_config(path: Path, target_type: str = "generic") -> None:
    emit(service().audit_config(path, target_type=target_type).model_dump(mode="json"))


@audit_app.command("code")
def audit_code(path: Path) -> None:
    emit(service().audit_code(path).model_dump(mode="json"))


@audit_app.command("secrets")
def audit_secrets(path: Path) -> None:
    emit(service().scan_secrets(path).model_dump(mode="json"))


@audit_app.command("dependencies")
def audit_dependencies(path: Path) -> None:
    emit(service().analyze_dependencies(path).model_dump(mode="json"))


@api_app.command("review")
def review_api_schema(path: Path) -> None:
    emit(service().analyze_api_schema(path).model_dump(mode="json"))


@automate_app.command("plan")
def automation_plan(project_id: str) -> None:
    emit(service().plan_automation(project_id).model_dump(mode="json"))


@detect_app.command("from-findings")
def detect_from_findings(path: Path) -> None:
    findings = [Finding.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]
    emit(service().map_detections(findings).model_dump(mode="json"))


@evidence_app.command("add")
def add_evidence(project_id: str, path: Path) -> None:
    project = service().import_evidence(project_id, path)
    emit({"project_id": project.id, "evidence_count": len(project.evidence)})


@evidence_app.command("search")
def search_evidence(project_id: str, query: str = "") -> None:
    emit(service().search_evidence(project_id, query).model_dump(mode="json"))


@report_app.command("build")
def build_report(project_id: str, report_type: str = "assessment") -> None:
    project = service().build_report(project_id, report_type)
    emit({"project_id": project.id, "events": len(project.events)})


@report_app.command("pack")
def report_pack(project_id: str) -> None:
    emit(service().prepare_report_pack(project_id).model_dump(mode="json"))


@harden_app.command("dockerfile")
def harden_dockerfile(path: Path) -> None:
    emit(service().harden_dockerfile(path).model_dump(mode="json"))


@flow_app.command("run")
def run_flow(project_id: str) -> None:
    emit(service().run_engagement_flow(project_id).model_dump(mode="json"))


@emulate_app.command("plan")
def emulate_plan(scenario_path: Path, project_id: str = "") -> None:
    emit(service().build_emulation_plan(scenario_path, project_id=project_id or None).model_dump(mode="json"))


@operator_app.command("status")
def operator_status(project_id: str) -> None:
    emit(service().operator_status(project_id).model_dump(mode="json"))


@operator_app.command("findings")
def operator_findings(project_id: str) -> None:
    emit(service().project_findings(project_id).model_dump(mode="json"))


@operator_app.command("toolkit")
def operator_toolkit(project_id: str) -> None:
    emit(service().plan_toolkit(project_id).model_dump(mode="json"))


@operator_app.command("preflight")
def operator_preflight(project_id: str, targets_csv: str = "", actions_csv: str = "") -> None:
    targets = [item.strip() for item in targets_csv.split(",") if item.strip()]
    actions = [item.strip() for item in actions_csv.split(",") if item.strip()]
    emit(service().run_preflight(project_id, requested_targets=targets, planned_actions=actions).model_dump(mode="json"))


@operator_app.command("export-toolkit")
def operator_export_toolkit(project_id: str) -> None:
    emit(service().export_toolkit_evidence(project_id))


@operator_app.command("campaign")
def operator_campaign(project_id: str) -> None:
    emit(service().plan_campaign(project_id).model_dump(mode="json"))


@upgrade_app.command("inspect")
def inspect_upgrades(project_id: str = "") -> None:
    emit(service().inspect_upgrades(project_id=project_id or None).model_dump(mode="json"))


@upgrade_app.command("apply")
def apply_upgrades(project_id: str = "") -> None:
    result = service().inspect_upgrades(project_id=project_id or None)
    emit({"applied": [proposal for proposal in result.artifacts["proposals"] if proposal["apply"]], "count": len([proposal for proposal in result.artifacts["proposals"] if proposal["apply"]])})


if __name__ == "__main__":
    app()
