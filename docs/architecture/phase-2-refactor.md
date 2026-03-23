# Phase 2 Refactor Notes

The initial implementation concentrated too much behavior in `AegisForgeService`. Phase 2 improves that by moving core review capabilities into dedicated module packages with a shared `ModuleContext`, `BaseModule`, and `ModuleRegistry`. This keeps the service as an orchestration boundary while allowing modules to evolve independently.

## Improvements applied
- `SurfaceMapper` now produces owner-based target groups and sensitivity/criticality summaries.
- `ConfigAudit` moved to an extensible rule registry with rationale and safer replacement guidance.
- `CodeGuard` moved to a rule-driven review pass that counts reviewed files and captures references.
- `HardeningWorkbench` now emits a reusable hardened baseline recommendation object.
- `RiskPrioritizer` now outputs a remediation roadmap with quick-win and ownership fields.
