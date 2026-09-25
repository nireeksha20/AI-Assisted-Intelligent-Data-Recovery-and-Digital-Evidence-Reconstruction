from pathlib import Path

from core.format_detector import detect_formats
from core.artifact_builder import build_artifacts
from core.artifact_validator import validate_artifact


def main():

    sample_path = Path("samples/fragmented_storage.bin")
    data = sample_path.read_bytes()

    findings = detect_formats(data)
    artifacts = build_artifacts(findings)

    validated = []

    for artifact in artifacts:
        validated.append(
            validate_artifact(artifact, data)
        )

    print()
    print("=" * 70)
    print("ARTIFACT VALIDATION")
    print("=" * 70)

    for artifact in validated:

        print()
        print(
            f"{artifact.artifact_id} | "
            f"{artifact.format:5s} | "
            f"confidence={artifact.confidence:.2f} | "
            f"status={artifact.status}"
        )

        for evidence in artifact.evidence:
            print(f"  ✓ {evidence}")


if __name__ == "__main__":
    main()