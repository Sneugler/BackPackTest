class Template:
    def __init__(self, text: str):
        self.text = text

    def render(self, **kwargs):
        project = kwargs.get('project')
        report_type = kwargs.get('report_type', '')
        findings = '\n'.join(
            f"- **{f.title}** ({f.severity.value if hasattr(f.severity,'value') else f.severity}): {f.description}"
            for f in project.findings
        ) or '- No findings yet.'
        evidence = '\n'.join(
            f"- {(e.summary or e.path)} [{e.sha256[:12]}]" for e in project.evidence
        ) or '- No evidence yet.'
        in_scope = '\n'.join(f"- {item}" for item in project.scope.in_scope_assets) or '- None declared.'
        out_scope = '\n'.join(f"- {item}" for item in project.scope.out_of_scope_assets) or '- None declared.'
        return (
            f"# {project.name}\n\n"
            f"Report type: {report_type}\n\n"
            f"Environment: {project.environment_type.value if hasattr(project.environment_type,'value') else project.environment_type}\n\n"
            f"Readiness: {project.scope.readiness.value if hasattr(project.scope.readiness,'value') else project.scope.readiness}\n\n"
            f"## Scope\nIn scope:\n{in_scope}\n\nOut of scope:\n{out_scope}\n\n"
            f"## Findings\n{findings}\n\n## Evidence\n{evidence}\n"
        )
