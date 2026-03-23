# Architecture Overview

AegisForge uses a local-first monorepo with shared typed models, storage, evidence handling, reporting, and a Typer CLI. Modules call into `AegisForgeService`, which centralizes orchestration so workflows share one project model, one audit trail, and one export pattern.

## Layers
- **CLI**: Human-facing command surface with module-oriented verbs.
- **Core service**: Coordinates config loading, SQLite persistence, evidence intake, report rendering, and module execution.
- **Parsers**: Scope-text and inventory normalization logic.
- **Models**: Pydantic schemas for projects, evidence, findings, reports, scenarios, and upgrades.
- **Storage**: SQLite repository for local state.
- **Evidence and reporting**: Shared subsystems for evidentiary integrity and professional report export.
- **Dashboard**: Optional local-only FastAPI view.
