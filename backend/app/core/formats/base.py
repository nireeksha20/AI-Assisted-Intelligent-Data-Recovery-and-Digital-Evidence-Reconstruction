from abc import ABC, abstractmethod
from dataclasses import dataclass, field

@dataclass
class FragmentAnalysis:
    format: str
    role: str
    confidence: float
    signals: dict[str, float] = field(default_factory=dict)

@dataclass
class ValidationResult:
    valid: bool
    score: float
    status: str
    reasons: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

class FormatPlugin(ABC):
    name: str = "UNKNOWN"
    category: str = "OTHER"

    @abstractmethod
    def detect(self, data: bytes) -> float: ...

    @abstractmethod
    def analyze_fragment(self, data: bytes) -> FragmentAnalysis | None: ...

    @abstractmethod
    def transition_score(self, left: bytes, right: bytes) -> tuple[float, dict[str, float]]: ...

    @abstractmethod
    def validate(self, data: bytes) -> ValidationResult: ...

    def recoverability(self, validation: ValidationResult, fragment_count: int, expected_count: int | None = None) -> float:
        completeness = 1.0 if expected_count is None else min(1.0, fragment_count / max(1, expected_count))
        return round(100 * (0.65*validation.score + 0.35*completeness), 2)
