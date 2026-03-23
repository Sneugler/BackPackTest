# Repository Structure

- `packages/core`: orchestration service.
- `packages/cli`: top-level `aegisforge` command.
- `packages/dashboard`: optional local FastAPI dashboard.
- `packages/models`: typed platform schemas.
- `packages/storage`: SQLite repository.
- `packages/config`: shared settings loader.
- `packages/logging`: centralized logger setup.
- `packages/parsers`: scope and target ingestion.
- `packages/evidence`: evidence hashing and intake.
- `packages/reporting`: Markdown, HTML, and JSON report output.
- `packages/workflows`: reusable workflow definitions.
- `packages/modules/*`: module namespaces reserved for module-specific evolution.
- `packages/plugins`: plugin registry.
- `tests`: unit, integration, and golden coverage.
- `examples`: authorization, scope, code, config, report, and scenario examples.
- `docs`: architecture, modules, workflows, examples, and policy guidance.
