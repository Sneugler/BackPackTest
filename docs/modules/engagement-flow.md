# EngagementFlow Module

EngagementFlow turns project state into a structured operator workflow. It emphasizes authorization, target readiness, evidence linkage, and reporting milestones so professional engagements remain auditable and organized.

## Critique pass
- **Architecture**: Now implemented as a dedicated module instead of inline service logic.
- **UX**: Added operator checklist items for dangerous-action acknowledgement and red-team precondition validation.
- **Output quality**: Returns structured workflow steps instead of an untyped list.
- **Maintainability**: Uses shared `WorkflowStep` models for future dashboard/report reuse.
