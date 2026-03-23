from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Template

from aegisforge_models.models import Project, Report

REPORT_TEMPLATE = Template(
    """
# {{ project.name }}

Report type: {{ report_type }}

Environment: {{ project.environment_type.value }}

Readiness: {{ project.scope.readiness.value }}

## Executive Summary
{{ executive_summary }}

## Scope
In scope: {% for item in project.scope.in_scope_assets %}- {{ item }} {% endfor %}

Out of scope: {% for item in project.scope.out_of_scope_assets %}- {{ item }} {% endfor %}

## Findings
{% for finding in project.findings %}- **{{ finding.title }}** ({{ finding.severity.value }}): {{ finding.description }}
{% endfor %}

## Remediation Roadmap
{% for item in roadmap %}- {{ item.title }} ({{ item.severity }}): {{ item.remediation }}
{% endfor %}

## Evidence
{% for evidence in project.evidence %}- {{ evidence.summary or evidence.path }} [{{ evidence.sha256[:12] }}]
{% endfor %}
"""
)


class ReportRenderer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render_project_report(self, project: Project, report_type: str = "assessment", report_pack: dict | None = None) -> Report:
        pack = report_pack or {}
        summary = pack.get("executive_summary", {})
        summary_text = json.dumps(summary, indent=2)
        roadmap = pack.get("roadmap", [])
        markdown = REPORT_TEMPLATE.render(project=project, report_type=report_type, executive_summary=summary_text, roadmap=roadmap)
        report = Report(project_id=project.id, report_type=report_type, title=f"{project.name} {report_type}", content={"markdown": markdown, "findings": [f.model_dump() for f in project.findings], "report_pack": pack})
        md_path = self.output_dir / f"{project.id}-{report_type}.md"
        html_path = self.output_dir / f"{project.id}-{report_type}.html"
        json_path = self.output_dir / f"{project.id}-{report_type}.json"
        md_path.write_text(markdown, encoding="utf-8")
        html_path.write_text("<html><body><pre>" + markdown + "</pre></body></html>", encoding="utf-8")
        json_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
        report.output_paths = [str(md_path), str(html_path), str(json_path)]
        return report
