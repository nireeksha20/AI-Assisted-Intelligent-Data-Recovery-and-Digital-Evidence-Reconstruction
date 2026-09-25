from pathlib import Path

from core.fragment_association import split_into_blocks
from core.fragment_membership import classify_fragment_membership
from core.jpeg_stream_parser import parse_jpeg_stream


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    jpeg_blocks = []

    for block_id, block_data in blocks.items():
        result = classify_fragment_membership(block_data)

        if result["membership"] == "jpeg":
            jpeg_blocks.append(block_id)

    print("=" * 90)
    print("CANDIDATE EXTENSION TEST")
    print("=" * 90)

    current = [34]

    print(f"\nCurrent sequence: {current}")

    for candidate in jpeg_blocks:

        if candidate == 34:
            continue

        test_sequence = current + [candidate]

        reconstructed = b"".join(
            blocks[block_id]
            for block_id in test_sequence
        )

        markers = parse_jpeg_stream(reconstructed)

        names = [marker["name"] for marker in markers]

        print(
            f"34 → {candidate:02d}"
            f" | markers={len(markers):2d}"
            f" | {names}"
        )


if __name__ == "__main__":
    main()