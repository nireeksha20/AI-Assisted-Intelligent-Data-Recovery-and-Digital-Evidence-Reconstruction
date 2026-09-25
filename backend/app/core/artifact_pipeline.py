from .format_detector import detect_formats
from .artifact_builder import build_artifacts
from .artifact_validator import validate_artifact


def analyze_artifacts(data: bytes):
    """
    Complete artifact analysis pipeline:

    1. Detect possible formats
    2. Convert detections into Artifact objects
    3. Perform structural validation
    4. Return validated artifacts
    """

    findings = detect_formats(data)

    artifacts = build_artifacts(findings)

    validated_artifacts = []

    for artifact in artifacts:
        validated = validate_artifact(artifact, data)
        validated_artifacts.append(validated)

    return validated_artifacts