# AegisForge

AegisForge is a local-first, modular cybersecurity operator platform for **authorized use only**. It unifies project setup, scope validation, evidence handling, configuration and code review, detection mapping, hardening guidance, risk prioritization, reporting, engagement workflows, and structured adversary emulation planning.

## Why keep the name AegisForge?
AegisForge is already strong: **Aegis** conveys protection and governance, while **Forge** conveys deliberate operator craftsmanship. It fits the product better than trendier alternatives because it spans defensive, validation, and authorized red-team planning without sounding disposable.

## Platform highlights
- Single `aegisforge` CLI with consistent module dispatch.
- Shared Pydantic models, SQLite storage, evidence metadata, reporting, and audit trail.
- Authorization-first project model with rules-of-engagement, environment type, and dangerous-action acknowledgements.
- Real parsers and analyzers for scope text, asset inventories, config files, and code repositories.
- First-class emulation and purple-team planning support oriented around scenarios, ATT&CK mapping, telemetry expectations, and after-action reporting.
- Authorized toolkit planning that maps safe assessment modules to project phases and filters recommendations through rules of engagement, plus validation-path plans with entry methods and guardrails.
- Path-of-least-resistance ranking, MITRE/defensive mapping, pre-flight guardrail checks, and exportable evidence packs for report-ready validation plans.
- Campaign planning that converts top-ranked validation paths into phased red/purple-team exercise plans with evidence and communication checkpoints.
- Upgrade engine that critiques coverage and suggests maintainable improvements.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
aegisforge init
aegisforge project create examples/authorization/project.yaml
pytest
```

## Safe use policy
AegisForge is designed only for environments you own, operate, or have explicit written authorization to assess. The platform captures scope context and authorization evidence so operators can demonstrate professional, permissioned use.

## Phase 2 improvements
- Refactored the monolithic Phase 1 service into module-oriented implementations with a shared module registry and execution context.
- Expanded SurfaceMapper, ConfigAudit, CodeGuard, HardeningWorkbench, and RiskPrioritizer into dedicated packages under `packages/modules`.
- Improved remediation output quality with rule metadata, grouped surface views, and roadmap-oriented prioritization.

## Phase 3 and 4 improvements
- Added dedicated workflow, operator, emulation, and upgrade modules so authorized purple-team and red-team planning are no longer service-only helpers.
- Expanded the optional local dashboard with project overview and workflow endpoints.
- Added explicit critique-pass documentation for Phase 3/4 and stronger workflow/emulation tests.

## Defensive upgrades
- Added curated CVE-aware scanning hooks to config and code review so findings can point operators toward known vulnerability families during triage.
- Added persistent module-result history in SQLite for stronger local auditability and operator review.
- Red-team support remains centered on authorized planning and validation rather than offensive automation.

## Plug-and-play upgrades
- Added `doctor`, `project bootstrap`, and `project list` workflows for faster onboarding.
- Added evidence search and report-pack generation for a more usable operator experience.
- Expanded dashboard endpoints with doctor, evidence, and report-pack views.

## Coverage upgrades
- Added secret scanning, dependency review/SBOM-style output, and API schema review so the toolkit covers more practical assessment workflows.
- Expanded the CLI and dashboard with dedicated access to those capabilities.
- Added more example inputs for manifests, secrets, and API schemas.

## Automation upgrades
- Added a safe rule-driven automation planner that evaluates project facts and suggests module sequences.
- Added `automate plan` and matching dashboard support for workflow orchestration.
- Automatic path enumeration is limited to safe schema-based path inventory in `APIGuard`, not active path brute forcing.
