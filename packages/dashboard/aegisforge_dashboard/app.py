from fastapi import FastAPI

from aegisforge_core import AegisForgeService

app = FastAPI(title="AegisForge Dashboard", docs_url=None, redoc_url=None)
service = AegisForgeService()


def _render_layout(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #0b1020;
        --panel: #121a31;
        --panel-2: #0f1730;
        --text: #e8ecf8;
        --muted: #9fb0d9;
        --accent: #77aaff;
        --good: #43c59e;
        --warn: #f0b35d;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, ui-sans-serif, system-ui, sans-serif;
        background: linear-gradient(180deg, #0b1020 0%, #111933 100%);
        color: var(--text);
      }}
      .wrap {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 48px; }}
      .hero, .panel {{
        background: rgba(18, 26, 49, 0.92);
        border: 1px solid rgba(119, 170, 255, 0.18);
        border-radius: 18px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28);
      }}
      .hero {{ padding: 28px; margin-bottom: 20px; }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin: 20px 0;
      }}
      .card {{
        background: var(--panel-2);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 18px;
      }}
      .metric {{ font-size: 2rem; font-weight: 700; margin-top: 8px; }}
      .muted {{ color: var(--muted); }}
      h1, h2, h3 {{ margin: 0 0 10px; }}
      .panel {{ padding: 22px; margin-top: 18px; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.08); }}
      .pill {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.85rem;
        background: rgba(119, 170, 255, 0.15);
        color: var(--accent);
      }}
      a {{ color: #9bc0ff; text-decoration: none; }}
      ul {{ padding-left: 18px; }}
      .ok {{ color: var(--good); }}
      .warn {{ color: var(--warn); }}
    </style>
  </head>
  <body>
    <div class="wrap">{body}</div>
  </body>
</html>"""


@app.get("/")
def dashboard_home() -> str:
    summary = service.portfolio_summary()
    project_rows = []
    for project in summary["projects"]:
        project_rows.append(
            "<tr>"
            f"<td><a href=\"/projects/{project['id']}/dashboard\">{project['name']}</a></td>"
            f"<td>{project['findings']}</td>"
            f"<td>{project['quick_wins']}</td>"
            f"<td>{project['targets']}</td>"
            f"<td>{project['evidence']}</td>"
            "</tr>"
        )
    body = f"""
    <section class="hero">
      <span class="pill">AegisForge Dashboard</span>
      <h1>Authorized assessment operations</h1>
      <p class="muted">Portfolio overview for projects, findings, guardrails, and report-ready planning artifacts.</p>
      <div class="grid">
        <div class="card"><div class="muted">Projects</div><div class="metric">{summary['project_count']}</div></div>
        <div class="card"><div class="muted">Targets</div><div class="metric">{summary['target_count']}</div></div>
        <div class="card"><div class="muted">Evidence items</div><div class="metric">{summary['evidence_count']}</div></div>
        <div class="card"><div class="muted">Severities tracked</div><div class="metric">{len(summary['findings_by_severity'])}</div></div>
      </div>
    </section>
    <section class="panel">
      <h2>Projects</h2>
      <table>
        <thead><tr><th>Name</th><th>Findings</th><th>Quick wins</th><th>Targets</th><th>Evidence</th></tr></thead>
        <tbody>{''.join(project_rows) or '<tr><td colspan="5" class="muted">No projects yet.</td></tr>'}</tbody>
      </table>
    </section>
    """
    return _render_layout("AegisForge Dashboard", body)


@app.get("/projects/{project_id}/dashboard")
def project_dashboard(project_id: str) -> str:
    overview = service.operator_status(project_id).model_dump(mode="json")
    findings = service.project_findings(project_id).model_dump(mode="json")
    toolkit = service.plan_toolkit(project_id).model_dump(mode="json")
    preflight = service.run_preflight(project_id).model_dump(mode="json")
    campaign = service.plan_campaign(project_id).model_dump(mode="json")
    path_rows = []
    for path in toolkit["artifacts"]["path_ranking"]:
        state = "warn" if path["blocked_by_roe"] else "ok"
        path_rows.append(
            "<tr>"
            f"<td>{path['priority']}</td>"
            f"<td>{path['title']}</td>"
            f"<td>{path['least_resistance_score']}</td>"
            f"<td class=\"{state}\">{'blocked' if path['blocked_by_roe'] else 'ready'}</td>"
            "</tr>"
        )
    recent_events = "".join(f"<li>{item['event_type']}: {item['message']}</li>" for item in overview["artifacts"]["recent_events"]) or "<li class=\"muted\">No recent events.</li>"
    phase_items = "".join(
        f"<li><strong>{phase['name']}</strong>: {phase['objective']}</li>"
        for phase in campaign["artifacts"]["phases"]
    )
    body = f"""
    <section class="hero">
      <span class="pill">Project dashboard</span>
      <h1>{toolkit['project_id']}</h1>
      <p class="muted">{overview['summary']}</p>
      <div class="grid">
        <div class="card"><div class="muted">Targets</div><div class="metric">{overview['artifacts']['counts']['targets']}</div></div>
        <div class="card"><div class="muted">Findings</div><div class="metric">{findings['artifacts']['counts']['total']}</div></div>
        <div class="card"><div class="muted">Ready paths</div><div class="metric">{toolkit['artifacts']['counts']['ready_paths']}</div></div>
        <div class="card"><div class="muted">Pre-flight</div><div class="metric {'ok' if preflight['artifacts']['ready'] else 'warn'}">{'ready' if preflight['artifacts']['ready'] else 'review'}</div></div>
      </div>
    </section>
    <section class="panel">
      <h2>Path of least resistance</h2>
      <table>
        <thead><tr><th>Priority</th><th>Path</th><th>Score</th><th>Status</th></tr></thead>
        <tbody>{''.join(path_rows)}</tbody>
      </table>
    </section>
    <section class="panel">
      <h2>Quick actions</h2>
      <ul>{"".join(f"<li>{item}</li>" for item in overview["artifacts"]["quick_actions"])}</ul>
    </section>
    <section class="panel">
      <h2>Campaign plan</h2>
      <ul>{phase_items}</ul>
    </section>
    <section class="panel">
      <h2>Recent events</h2>
      <ul>{recent_events}</ul>
    </section>
    """
    return _render_layout(f"AegisForge Project {project_id}", body)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "local-only"}


@app.get("/doctor")
def doctor() -> dict:
    return service.doctor()


@app.get("/projects")
def projects() -> list[dict[str, str]]:
    return service.list_projects()


@app.get("/portfolio/summary")
def portfolio_summary() -> dict:
    return service.portfolio_summary()


@app.get("/projects/{project_id}/overview")
def project_overview(project_id: str) -> dict:
    return service.operator_status(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/flow")
def project_flow(project_id: str) -> dict:
    return service.run_engagement_flow(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/evidence")
def project_evidence(project_id: str) -> dict:
    return service.search_evidence(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/findings")
def project_findings(project_id: str) -> dict:
    return service.project_findings(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/toolkit")
def project_toolkit(project_id: str) -> dict:
    return service.plan_toolkit(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/preflight")
def project_preflight(project_id: str, targets: str = "", actions: str = "") -> dict:
    requested_targets = [item.strip() for item in targets.split(",") if item.strip()]
    planned_actions = [item.strip() for item in actions.split(",") if item.strip()]
    return service.run_preflight(project_id, requested_targets=requested_targets, planned_actions=planned_actions).model_dump(mode="json")


@app.get("/projects/{project_id}/toolkit/export")
def project_toolkit_export(project_id: str) -> dict:
    return service.export_toolkit_evidence(project_id)


@app.get("/projects/{project_id}/campaign")
def project_campaign(project_id: str) -> dict:
    return service.plan_campaign(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/report-pack")
def project_report_pack(project_id: str) -> dict:
    return service.prepare_report_pack(project_id).model_dump(mode="json")


@app.get("/projects/{project_id}/automation")
def project_automation(project_id: str) -> dict:
    return service.plan_automation(project_id).model_dump(mode="json")


@app.get("/api/review")
def api_review(path: str) -> dict:
    from pathlib import Path
    return service.analyze_api_schema(Path(path)).model_dump(mode="json")
