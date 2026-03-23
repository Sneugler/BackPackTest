from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EnvironmentType(str, Enum):
    LAB = "lab"
    INTERNAL_AUTHORIZED = "internal_authorized"
    CLIENT_AUTHORIZED = "client_authorized"


class Readiness(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetType(str, Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP_RANGE = "ip_range"
    URL = "url"
    HOSTNAME = "hostname"
    REPOSITORY = "repository"
    CLOUD_ASSET = "cloud_asset"
    ENVIRONMENT = "environment"
    FILE = "file"


class AuthorizationEvidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source_type: str
    description: str
    locator: str
    excerpt: str | None = None
    captured_at: datetime = Field(default_factory=utc_now)


class RulesOfEngagement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    allowed_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    time_limits: list[str] = Field(default_factory=list)
    approval_contacts: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ProjectScope(BaseModel):
    in_scope_assets: list[str] = Field(default_factory=list)
    out_of_scope_assets: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
    readiness: Readiness = Readiness.YELLOW


class Target(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    value: str
    asset_type: AssetType
    owner: str | None = None
    sensitivity: str | None = None
    criticality: str | None = None
    tags: list[str] = Field(default_factory=list)
    scope_status: str = "unreviewed"


class TargetGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    targets: list[Target] = Field(default_factory=list)
    description: str | None = None


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    path: str
    sha256: str
    recorded_at: datetime = Field(default_factory=utc_now)
    module: str
    finding_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    summary: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Remediation(BaseModel):
    summary: str
    quick_win: bool = False
    strategic: bool = True
    owner: str | None = None
    effort: str = "medium"


class DetectionSuggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    telemetry_requirements: list[str] = Field(default_factory=list)
    sigma_like_rule: str = ""
    tuning_notes: list[str] = Field(default_factory=list)
    false_positive_notes: list[str] = Field(default_factory=list)


class HardeningRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    target_type: str
    title: str
    rationale: str
    replacement: str
    checklist: list[str] = Field(default_factory=list)


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    severity: Severity
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    remediation: Remediation
    confidence: str = "medium"
    module: str
    business_impact: str = ""
    references: list[str] = Field(default_factory=list)
    detection_suggestions: list[DetectionSuggestion] = Field(default_factory=list)


class Report(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    report_type: str
    title: str
    created_at: datetime = Field(default_factory=utc_now)
    content: dict[str, Any]
    output_paths: list[str] = Field(default_factory=list)


class WorkflowStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: str = "pending"
    description: str = ""
    evidence_required: bool = False


class Scenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    objective: str
    attack_mapping: list[str] = Field(default_factory=list)
    preconditions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    expected_telemetry: list[str] = Field(default_factory=list)


class EmulationPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario: Scenario
    timeline: list[str] = Field(default_factory=list)
    controls_under_test: list[str] = Field(default_factory=list)
    gap_analysis: list[str] = Field(default_factory=list)
    rules_of_engagement_id: str | None = None


class ProjectEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: str
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModuleResult(BaseModel):
    module_name: str
    project_id: str
    summary: str
    findings: list[Finding] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class OperatorNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    author: str = "operator"
    body: str
    created_at: datetime = Field(default_factory=utc_now)
    tags: list[str] = Field(default_factory=list)


class UpgradeProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    rationale: str
    impact: str
    complexity: str
    apply: bool = True


class UpgradeResult(BaseModel):
    proposal: UpgradeProposal
    status: str
    notes: str


class ToolkitRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    phase: str
    capability: str
    tool_name: str
    safe_use: str
    requires_evidence: bool = False
    references: list[str] = Field(default_factory=list)
    blocked_by_roe: bool = False
    block_reason: str | None = None


class ValidationPath(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    entry_method: str
    objective: str
    prerequisites: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    evidence_to_collect: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    defensive_methods: list[str] = Field(default_factory=list)
    least_resistance_score: int = 0
    priority: int = 0
    blocked_by_roe: bool = False
    block_reason: str | None = None


class CampaignPhase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    objective: str
    planned_actions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    evidence_goals: list[str] = Field(default_factory=list)
    communication_checkpoints: list[str] = Field(default_factory=list)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    environment_type: EnvironmentType
    authorization_evidence: list[AuthorizationEvidence] = Field(default_factory=list)
    rules_of_engagement: RulesOfEngagement
    scope: ProjectScope
    targets: list[Target] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    notes: list[OperatorNote] = Field(default_factory=list)
    events: list[ProjectEvent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    project_path: str = "."

    def ensure_authorized(self) -> None:
        if not self.authorization_evidence:
            raise ValueError("Projects must store authorization evidence before running workflows.")

    @property
    def root(self) -> Path:
        return Path(self.project_path)
