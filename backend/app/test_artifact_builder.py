from pathlib import Path

from core.format_detector import detect_formats
from core.artifact_builder import build_artifacts


def main():

    sample_path = Path("samples/fragmented_storage.bin")

    data = sample_path.read_bytes()

    findings = detect_formats(data)

    artifacts = build_artifacts(findings)

    print()
    print("=" * 70)
    print("DETECTOR → ARTIFACT PIPELINE")
    print("=" * 70)

    print(f"\nRaw detections : {len(findings)}")
    print(f"Artifacts      : {len(artifacts)}")

    for artifact in artifacts:

        print()
        print(
            f"{artifact.artifact_id} | "
            f"{artifact.format:5s} | "
            f"{artifact.category:10s} | "
            f"offset={artifact.offset:7d} | "
            f"confidence={artifact.confidence:.2f} | "
            f"status={artifact.status}"
        )


if __name__ == "__main__":
    main()