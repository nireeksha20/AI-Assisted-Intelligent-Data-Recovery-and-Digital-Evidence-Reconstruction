from pathlib import Path

from core.fragment_association import split_into_blocks
from core.fragment_membership import classify_fragment_membership
from core.jpeg_analyzer import scan_jpeg_structure


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    print("=" * 90)
    print("JPEG RECONSTRUCTION CANDIDATES")
    print("=" * 90)

    jpeg_blocks = []

    for block_id, block_data in blocks.items():

        membership = classify_fragment_membership(block_data)

        if membership["membership"] != "jpeg":
            continue

        markers = scan_jpeg_structure(block_data)

        marker_info = []

        for marker in markers:
            marker_info.append(
                f"{marker['name']}@{marker['offset']}"
            )

        jpeg_blocks.append(
            (
                block_id,
                membership["role"],
                membership["score"],
                marker_info,
            )
        )

    for block_id, role, score, markers in jpeg_blocks:

        marker_text = ", ".join(markers)

        print(
            f"Block {block_id:02d} | "
            f"role={role:16s} | "
            f"score={score:.4f} | "
            f"markers={marker_text}"
        )

    print()
    print("=" * 90)
    print(f"JPEG CANDIDATE COUNT: {len(jpeg_blocks)}")
    print("=" * 90)


if __name__ == "__main__":
    main()