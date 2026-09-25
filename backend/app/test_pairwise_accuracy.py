from pathlib import Path
from collections import Counter
import math


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

    difference = 0.0

    for value in range(256):

        p = ca[value] / len(a)
        q = cb[value] / len(b)

        difference += abs(p - q)

    return 1.0 - difference / 2.0


def score(a, b):

    entropy_score = max(
        0.0,
        1.0 - abs(
            entropy(a) - entropy(b)
        ) / 8.0
    )

    distribution_score = (
        distribution_similarity(a, b)
    )

    return (
        0.30 * entropy_score
        + 0.70 * distribution_score
    )


data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


ranks = []

for left, correct in zip(
    GROUND_TRUTH,
    GROUND_TRUTH[1:]
):

    candidates = []

    for candidate, candidate_data in blocks.items():

        if candidate == left:
            continue

        candidates.append(
            (
                score(
                    blocks[left],
                    candidate_data
                ),
                candidate
            )
        )

    candidates.sort(
        reverse=True
    )

    rank = next(
        i
        for i, (_, candidate) in enumerate(
            candidates,
            start=1
        )
        if candidate == correct
    )

    ranks.append(rank)


total = len(ranks)

print()
print("=== PAIRWISE STATISTICAL MODEL ===")
print()

print(f"Transitions: {total}")

for k in [1, 3, 5, 10]:

    hits = sum(
        rank <= k
        for rank in ranks
    )

    print(
        f"Top-{k}: "
        f"{hits}/{total} "
        f"= {hits / total * 100:.2f}%"
    )

print(
    f"Average rank: "
    f"{sum(ranks) / total:.2f}"
)

print()
print("Ranks:")
print(ranks)