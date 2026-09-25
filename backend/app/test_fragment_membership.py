from pathlib import Path

from core.fragment_association import split_into_blocks
from core.fragment_membership import classify_fragment_membership


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    print("=" * 70)
    print("FRAGMENT MEMBERSHIP CLASSIFICATION")
    print("=" * 70)

    counts = {}

    for block_id, block_data in blocks.items():
        result = classify_fragment_membership(block_data)

        membership = result["membership"]
        counts[membership] = counts.get(membership, 0) + 1

        print(
            f"Block {block_id:02d} | "
            f"{membership:17s} | "
            f"role={result['role']:16s} | "
            f"score={result['score']:.4f} | "
            f"FF00={result['ff00_count']:3d} | "
            f"invalidFF={result['invalid_ff_count']:2d}"
        )

    print()
    print("SUMMARY")
    print("-" * 70)

    for membership, count in counts.items():
        print(f"{membership:20s}: {count}")


if __name__ == "__main__":
    main()