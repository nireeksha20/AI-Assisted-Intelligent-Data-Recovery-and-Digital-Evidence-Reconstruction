from pathlib import Path

from core.fragment_association import split_into_blocks
from core.jpeg_anchors import extract_jpeg_anchors
from core.jpeg_anchor_graph import classify_scan, progressive_compatibility


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def describe_scan(scan):
    scan_type = classify_scan(scan)

    components = [
        component["component_id"]
        for component in scan["components"]
    ]

    return (
        f"{scan_type}, "
        f"components={components}, "
        f"SS={scan['spectral_start']}, "
        f"SE={scan['spectral_end']}, "
        f"Ah={scan['successive_high']}, "
        f"Al={scan['successive_low']}"
    )


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)
    anchors = extract_jpeg_anchors(blocks)

    scan_blocks = []

    for block_id, anchor in anchors.items():
        if anchor["scans"]:
            scan_blocks.append(block_id)

    print("=" * 90)
    print("JPEG SCAN ANCHORS")
    print("=" * 90)

    for block_id in scan_blocks:
        scans = anchors[block_id]["scans"]

        print(f"\nBlock {block_id:02d}")

        for index, scan in enumerate(scans, start=1):
            print(f"  Scan {index}: {describe_scan(scan)}")

    print()
    print("=" * 90)
    print("PAIRWISE SCAN COMPATIBILITY")
    print("=" * 90)

    for left_id in scan_blocks:

        left_scans = anchors[left_id]["scans"]

        for right_id in scan_blocks:

            if left_id == right_id:
                continue

            right_scans = anchors[right_id]["scans"]

            score, reasons = progressive_compatibility(
                left_scans[-1],
                right_scans[0],
            )

            if score > 0:
                print(
                    f"{left_id:02d} → {right_id:02d} "
                    f"| score={score:.1f} "
                    f"| {', '.join(reasons)}"
                )


if __name__ == "__main__":
    main()