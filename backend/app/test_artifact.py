from core.artifact import Artifact


def main():
    artifact = Artifact(
        artifact_id="artifact_001",
        format="JPEG",
        category="image",
        offset=139264,
        extension=".jpg",
        mime_type="image/jpeg",
        confidence=0.96,
        status="recoverable_candidate",
        size_bytes=None,
        integrity_score=None,
        fragments=[34, 24, 3, 16],
        evidence=[
            "JPEG SOI detected",
            "Progressive JPEG structure detected",
            "Fragment sequence candidate identified",
        ],
    )

    print()
    print("=" * 70)
    print("FORENSIC ARTIFACT MODEL")
    print("=" * 70)

    for key, value in artifact.to_dict().items():
        print(f"{key:18s}: {value}")


if __name__ == "__main__":
    main()