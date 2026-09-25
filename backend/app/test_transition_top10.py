from pathlib import Path
from collections import Counter
import math

from core.jpeg_fragment_features import analyze_fragment


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18,
    11, 10, 27, 2, 9
]


def entropy(data):
    if not data:
        return 0.0

    counts = Counter(data)
    n = len(data)

    return -sum(
        (count / n) * math.log2(count / n)
        for count in counts.values()
    )


def distribution_similarity(a, b):
    if not a or not b:
        return 0.0

    ca = Counter(a)
    cb = Counter(b)

    total_a = len(a)
    total_b = len(b)

    difference = 0.0

    for value in range(256):

        p = ca[value] / total_a
        q = cb[value] / total_b

        difference += abs(p - q)

    return 1.0 - difference / 2.0


def statistical_transition_score(left, right):

    left_entropy = entropy(left)
    right_entropy = entropy(right)

    entropy_difference = abs(
        left_entropy - right_entropy
    )

    entropy_score = max(
        0.0,
        1.0 - entropy_difference / 8.0
    )

    distribution_score = distribution_similarity(
        left,
        right
    )

    return (
        0.30 * entropy_score
        + 0.70 * distribution_score
    )


# --------------------------------------------------
# Load storage
# --------------------------------------------------

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


# --------------------------------------------------
# Analyze blocks
# --------------------------------------------------

features = {
    block_id: analyze_fragment(
        block,
        block_id
    )
    for block_id, block in blocks.items()
}


# --------------------------------------------------
# Evaluate every TRUE transition
# --------------------------------------------------

print()
print("=== STATISTICAL MODEL: TOP 10 CANDIDATES ===")
print()


for left_id, correct_id in zip(
    GROUND_TRUTH,
    GROUND_TRUTH[1:]
):

    candidates = []

    for candidate_id, candidate_data in blocks.items():

        if candidate_id == left_id:
            continue

        score = statistical_transition_score(
            blocks[left_id],
            candidate_data
        )

        candidates.append(
            (
                score,
                candidate_id
            )
        )

    candidates.sort(
        reverse=True
    )

    correct_rank = None

    for rank, (score, candidate_id) in enumerate(
        candidates,
        start=1
    ):

        if candidate_id == correct_id:
            correct_rank = rank
            break


    print(
        f"{left_id:02d} → {correct_id:02d}"
        f"   Correct rank = {correct_rank}"
    )

    print("-" * 55)

    for rank, (score, candidate_id) in enumerate(
        candidates[:10],
        start=1
    ):

        marker = "  <-- TRUE" if candidate_id == correct_id else ""

        print(
            f"{rank:2d}. "
            f"Block {candidate_id:02d} "
            f"| score={score:.6f}"
            f"{marker}"
        )

    print()


print("=== END ===")