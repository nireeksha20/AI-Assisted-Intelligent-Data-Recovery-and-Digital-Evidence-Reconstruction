from pathlib import Path

from core.fragment_association import split_into_blocks
from core.fragment_membership import classify_fragment_membership


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def byte_transition_similarity(left: bytes, right: bytes, window=64):
    left_tail = left[-window:]
    right_head = right[:window]

    if not left_tail or not right_head:
        return 0.0

    # Compare byte-frequency distributions in the boundary windows.
    left_counts = [0] * 256
    right_counts = [0] * 256

    for byte in left_tail:
        left_counts[byte] += 1

    for byte in right_head:
        right_counts[byte] += 1

    left_total = len(left_tail)
    right_total = len(right_head)

    score = 0.0

    for i in range(256):
        p = left_counts[i] / left_total
        q = right_counts[i] / right_total

        score += min(p, q)

    return score


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    entropy_blocks = []

    for block_id, block_data in blocks.items():
        result = classify_fragment_membership(block_data)

        if (
            result["membership"] == "jpeg"
            and result["role"] == "jpeg_entropy"
        ):
            entropy_blocks.append(block_id)

    print("=" * 90)
    print("ENTROPY BLOCK BOUNDARY ANALYSIS")
    print("=" * 90)

    print(f"Entropy candidates: {len(entropy_blocks)}")
    print()

    for left_id in entropy_blocks:

        candidates = []

        for right_id in entropy_blocks:

            if left_id == right_id:
                continue

            score = byte_transition_similarity(
                blocks[left_id],
                blocks[right_id],
            )

            candidates.append(
                (right_id, score)
            )

        candidates.sort(
            key=lambda item: item[1],
            reverse=True
        )

        print(
            f"\nBlock {left_id:02d} best successors:"
        )

        for right_id, score in candidates[:5]:
            print(
                f"    {left_id:02d} → {right_id:02d}"
                f"  score={score:.4f}"
            )


if __name__ == "__main__":
    main()