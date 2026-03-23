# Dependency Map

- `aegisforge_cli` depends on `aegisforge_core` and shared models for serialization.
- `aegisforge_core` depends on config, storage, parsers, evidence, reporting, logging, and models.
- `aegisforge_parsers` depends on models.
- `aegisforge_reporting` depends on models and templating.
- `aegisforge_storage` depends on models and SQLite.
- `aegisforge_dashboard` depends on `aegisforge_core`.
- Module directories are represented in the service orchestration and remain available for future extraction into independently versioned packages.
