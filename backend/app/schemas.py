from typing import Any, Literal
from pydantic import BaseModel, Field

class StorageInfo(BaseModel):
    size_bytes: int
    block_size: int
    block_count: int
    sha256: str

class FragmentEvidence(BaseModel):
    block_id: int
    offset: int
    size: int
    entropy: float
    zero_ratio: float
    printable_ratio: float
    signatures: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    artifact_types: list[str] = Field(default_factory=list)

class EdgeEvidence(BaseModel):
    source: int
    target: int
    score: float
    signals: dict[str, float]

class ArtifactCandidate(BaseModel):
    artifact_id: str
    format: str
    category: str
    fragment_ids: list[int]
    start_block: int | None = None
    end_block: int | None = None
    reconstruction_confidence: float
    validation: dict[str, Any] = Field(default_factory=dict)
    integrity: dict[str, Any] = Field(default_factory=dict)
    recoverability: float = 0.0
    priority: dict[str, Any] = Field(default_factory=dict)

class AIReport(BaseModel):
    executive_summary: str
    key_findings: list[str]
    artifact_assessments: list[dict[str, Any]]
    recommended_actions: list[str]
    limitations: list[str]
    confidence_explanation: str

class AnalysisResponse(BaseModel):
    case_id: str
    storage: StorageInfo
    fragments: list[FragmentEvidence]
    artifacts: list[ArtifactCandidate]
    edges: list[EdgeEvidence]
    metrics: dict[str, Any]
    ai_report: AIReport | None = None

class PipelineResponse(AnalysisResponse):
    pipeline_version: str = "1.0"
    stages: list[dict[str, Any]] = Field(default_factory=list)
