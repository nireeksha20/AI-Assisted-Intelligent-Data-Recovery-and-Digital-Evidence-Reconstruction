from pathlib import Path

from core.artifact_pipeline import analyze_artifacts


def main():

    sample_path = Path("samples/fragmented_storage.bin")
    data = sample_path.read_bytes()

    artifacts = analyze_artifacts(data)

    print()
    print("=" * 70)
    print("COMPLETE ARTIFACT ANALYSIS PIPELINE")
    print("=" * 70)

    print()
    print(f"Storage size : {len(data):,} bytes")
    print(f"Artifacts    : {len(artifacts)}")

    for artifact in artifacts:

        print()
        print(
            f"{artifact.artifact_id} | "
            f"{artifact.format:5s} | "
            f"category={artifact.category:10s} | "
            f"confidence={artifact.confidence:.2f} | "
            f"status={artifact.status}"
        )

        print(f"  offset     : {artifact.offset}")

        for evidence in artifact.evidence:
            print(f"  evidence   : {evidence}")


if __name__ == "__main__":
    main()