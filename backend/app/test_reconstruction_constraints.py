from pathlib import Path

from core.fragment_association import split_into_blocks
from core.reconstruction_constraints import (
    identify_jpeg_roles,
    get_structural_order_candidates,
)


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():

    data = STORAGE_PATH.read_bytes()

    blocks = split_into_blocks(data)

    result = identify_jpeg_roles(blocks)

    roles = result["roles"]
    details = result["details"]

    print("=" * 70)
    print("JPEG RECONSTRUCTION CONSTRAINT ANALYSIS")
    print("=" * 70)

    print()
    print("START ANCHORS:")
    print(
        " → ".join(
            f"{block_id:02d}"
            for block_id in roles["start"]
        )
    )

    print()
    print("SCAN ANCHORS:")
    print(
        " → ".join(
            f"{block_id:02d}"
            for block_id in roles["scan_anchors"]
        )
    )

    print()
    print("END ANCHORS:")
    print(
        " → ".join(
            f"{block_id:02d}"
            for block_id in roles["end"]
        )
    )

    print()
    print("WEAK STRUCTURAL BLOCKS:")
    print(
        " → ".join(
            f"{block_id:02d}"
            for block_id in roles["weak_structural"]
        )
    )

    print()
    print("ENTROPY/DATA BLOCKS:")
    print(
        " → ".join(
            f"{block_id:02d}"
            for block_id in roles["entropy"]
        )
    )

    print()
    print("BLOCK DETAILS:")
    print("-" * 70)

    for block_id in sorted(details):

        info = details[block_id]

        print(
            f"Block {block_id:02d} | "
            f"role={info['role']:<18} | "
            f"scans={info['scan_count']} | "
            f"markers={','.join(info['markers'])}"
        )

    print()
    print("TOP STRUCTURAL TRANSITIONS:")
    print("-" * 70)

    candidates = get_structural_order_candidates(blocks)

    for candidate in candidates[:20]:

        print(
            f"{candidate['from']:02d} → "
            f"{candidate['to']:02d} | "
            f"score={candidate['score']:.2f}"
        )

        for reason in candidate["reasons"]:
            print(f"    {reason}")


if __name__ == "__main__":
    main()