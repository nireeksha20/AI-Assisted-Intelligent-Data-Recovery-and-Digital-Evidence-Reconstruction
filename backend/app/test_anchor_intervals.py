from pathlib import Path

from core.fragment_association import split_into_blocks
from core.anchor_intervals import (
    get_strong_anchors,
    get_anchor_scan_types,
    get_valid_anchor_edges,
)


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():

    data = STORAGE_PATH.read_bytes()

    blocks = split_into_blocks(data)

    strong_anchors = get_strong_anchors(blocks)
    scan_types = get_anchor_scan_types(blocks)
    edges = get_valid_anchor_edges(blocks)

    print("=" * 70)
    print("ANCHOR-CONSTRAINED JPEG RECONSTRUCTION")
    print("=" * 70)

    print()
    print("STRONG ANCHORS")
    print("-" * 70)

    for block_id, role in strong_anchors.items():

        scan_type = scan_types.get(
            block_id,
            "-"
        )

        print(
            f"Block {block_id:02d} | "
            f"role={role:<6} | "
            f"scan={scan_type}"
        )

    print()
    print("VALID STRUCTURAL ANCHOR EDGES")
    print("-" * 70)

    for edge in edges:

        print(
            f"{edge['from']:02d} → "
            f"{edge['to']:02d} | "
            f"score={edge['score']:.2f}"
        )

        for reason in edge["reasons"]:
            print(f"    {reason}")


if __name__ == "__main__":
    main()