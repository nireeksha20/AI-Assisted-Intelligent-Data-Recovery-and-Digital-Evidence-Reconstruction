from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.jpeg_stream_parser import parse_jpeg_stream
from core.jpeg_scan_parser import extract_scan_information
from core.jpeg_scan_transition import scan_transition_score

BLOCK_SIZE = 4096

STORAGE_PATH = Path("samples/fragmented_storage.bin")

# Evaluation only — never use this in reconstruction code.
GROUND_TRUTH_SEQUENCE = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18, 11,
    10, 27, 2, 9
]


def build_stream():
    storage = STORAGE_PATH.read_bytes()

    return b"".join(
        storage[
            block_id * BLOCK_SIZE:
            (block_id + 1) * BLOCK_SIZE
        ]
        for block_id in GROUND_TRUTH_SEQUENCE
    )


def main():
    data = build_stream()

    markers = parse_jpeg_stream(data)
    scans = extract_scan_information(data)

    print("=" * 90)
    print("JPEG SCAN TRANSITION ANALYSIS")
    print("=" * 90)

    print(f"\nTotal scans: {len(scans)}\n")

    for i in range(len(scans) - 1):
        left = scans[i]
        right = scans[i + 1]

        result = scan_transition_score(left, right)

        print("-" * 90)
        print(
            f"SCAN {i + 1} → SCAN {i + 2}"
        )

        print(
            f"  {result['left_type']} → "
            f"{result['right_type']}"
        )

        print(
            f"  Score: {result['score']}"
        )

        if result["reasons"]:
            for reason in result["reasons"]:
                print(f"  ✓ {reason}")
        else:
            print("  No semantic compatibility evidence")

    print("\n" + "=" * 90)


if __name__ == "__main__":
    main()