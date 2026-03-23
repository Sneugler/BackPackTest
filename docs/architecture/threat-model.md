# Platform Threat Model

## Security objectives
- Preserve authorization context and evidence integrity.
- Prevent accidental scope drift by requiring scope-aware project metadata.
- Keep data local-first using SQLite and local filesystem exports.
- Maintain auditability through project events and deterministic exports.

## Key risks
- Unauthorized use without written approval.
- Evidence tampering or loss.
- Scope misinterpretation.
- Sensitive output leakage through reports or exports.

## Current mitigations
- Authorization evidence is a required project concept.
- Rules of engagement and environment type are first-class data fields.
- Evidence ingestion hashes files and stores capture metadata.
- Reports include environment and scope context.
- Dashboard is local-only by default.
