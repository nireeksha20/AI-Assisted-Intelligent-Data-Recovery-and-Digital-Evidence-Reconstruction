from pathlib import Path

from core.format_detector import detect_formats


def main():
    sample_path = Path("samples/fragmented_storage.bin")

    data = sample_path.read_bytes()

    findings = detect_formats(data)

    print()
    print("=" * 70)
    print("GENERIC FORMAT DETECTOR")
    print("=" * 70)

    print(f"\nStorage size: {len(data):,} bytes")
    print(f"Artifacts detected: {len(findings)}")

    for finding in findings:
        print()
        print(
            f"{finding['format']:6s} "
            f"offset={finding['offset']:7d} "
            f"category={finding['category']:10s} "
            f"confidence={finding['confidence']}"
        )


if __name__ == "__main__":
    main()