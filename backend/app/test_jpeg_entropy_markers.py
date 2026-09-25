from pathlib import Path

from core.fragment_association import split_into_blocks
from core.fragment_membership import classify_fragment_membership


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def find_jpeg_markers(data: bytes):
    markers = []

    i = 0

    while i < len(data) - 1:
        if data[i] == 0xFF:
            nxt = data[i + 1]

            # Restart markers: RST0-RST7
            if 0xD0 <= nxt <= 0xD7:
                markers.append({
                    "offset": i,
                    "marker": f"RST{nxt - 0xD0}",
                })

        i += 1

    return markers


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    print("=" * 90)
    print("JPEG ENTROPY RESTART MARKER ANALYSIS")
    print("=" * 90)

    total = 0

    for block_id, block_data in blocks.items():

        result = classify_fragment_membership(block_data)

        if result["membership"] != "jpeg":
            continue

        if result["role"] != "jpeg_entropy":
            continue

        markers = find_jpeg_markers(block_data)

        print(
            f"\nBlock {block_id:02d}"
            f" | RST markers: {len(markers)}"
        )

        for marker in markers:
            print(
                f"    {marker['marker']} "
                f"@ offset {marker['offset']}"
            )

        total += len(markers)

    print()
    print("=" * 90)
    print(f"TOTAL RESTART MARKERS: {total}")
    print("=" * 90)


if __name__ == "__main__":
    main()