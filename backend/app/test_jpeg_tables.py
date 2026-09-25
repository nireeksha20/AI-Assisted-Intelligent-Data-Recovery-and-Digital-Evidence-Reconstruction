from pathlib import Path

from core.fragment_association import split_into_blocks
from core.jpeg_analyzer import scan_jpeg_structure


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    structural_blocks = [3, 8, 12, 16, 28, 30, 32, 34]

    print("=" * 90)
    print("JPEG STRUCTURAL TABLE ANALYSIS")
    print("=" * 90)

    for block_id in structural_blocks:
        block = blocks[block_id]
        markers = scan_jpeg_structure(block)

        print(f"\nBLOCK {block_id:02d}")

        for marker in markers:
            name = marker["name"]
            offset = marker["offset"]

            print(
                f"  {name:<8} "
                f"offset={offset:<5} "
                f"length={marker.get('segment_length')}"
            )


if __name__ == "__main__":
    main()