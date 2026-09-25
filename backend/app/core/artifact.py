from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Artifact:
    """
    Standard representation of a detected forensic artifact.
    """

    artifact_id: str
    format: str
    category: str
    offset: int

    extension: Optional[str] = None
    mime_type: Optional[str] = None

    confidence: float = 0.0
    status: str = "candidate"

    size_bytes: Optional[int] = None
    integrity_score: Optional[float] = None

    fragments: list[int] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "artifact_id": self.artifact_id,
            "format": self.format,
            "category": self.category,
            "offset": self.offset,
            "extension": self.extension,
            "mime_type": self.mime_type,
            "confidence": self.confidence,
            "status": self.status,
            "size_bytes": self.size_bytes,
            "integrity_score": self.integrity_score,
            "fragments": self.fragments,
            "evidence": self.evidence,
        }