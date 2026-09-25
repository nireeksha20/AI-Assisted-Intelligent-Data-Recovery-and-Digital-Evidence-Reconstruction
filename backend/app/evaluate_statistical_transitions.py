from pathlib import Path
import math
from collections import Counter


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


TRUE_PAIRS = [
    (34, 24), (24, 3), (3, 16), (16, 32),
    (32, 7), (7, 21), (21, 30), (30, 8),
    (8, 14), (14, 5), (5, 35), (35, 33),
    (33, 0), (0, 19), (19, 23), (23, 12),
    (12, 13), (13, 26), (26, 22), (22, 17),
    (17, 28), (28, 18), (18, 11), (11, 10),
    (10, 27), (27, 2), (2, 9),
]


def entropy(data):

    counts = Counter(data)
    n = len(data)

    return -sum(
        (count / n) * math.log2(count / n)
        for count in counts.values()
    )


def distribution_similarity(left, right):

    left_counts = Counter(left)
    right_counts = Counter(right)

    total_left = len(left)
    total_right = len(right)

    difference = 0.0

    for value in range(256):

        p = left_counts[value] / total_left
        q = right_counts[value] / total_right

        difference += abs(p - q)

    return 1.0 - difference / 2.0


def ngram_similarity(left, right, n=2, window=256):

    left_tail = left[-window:]
    right_head = right[:window]

    left_ngrams = Counter(
        left_tail[i:i+n]
        for i in range(len(left_tail) - n + 1)
    )

    right_ngrams = Counter(
        right_head[i:i+n]
        for i in range(len(right_head) - n + 1)
    )

    if not left_ngrams or not right_ngrams:
        return 0.0

    intersection = sum(
        (left_ngrams & right_ngrams).values()
    )

    total = min(
        sum(left_ngrams.values()),
        sum(right_ngrams.values())
    )

    return intersection / total


def transition_score(left_id, right_id):

    left = blocks[left_id]
    right = blocks[right_id]

    left_entropy = entropy(left)
    right_entropy = entropy(right)

    entropy_difference = abs(
        left_entropy - right_entropy
    )

    entropy_score = max(
        0.0,
        1.0 - entropy_difference / 8.0
    )

    distribution = distribution_similarity(
        left,
        right
    )

    bigram = ngram_similarity(
        left,
        right,
        n=2
    )

    trigram = ngram_similarity(
        left,
        right,
        n=3
    )

    # Weak statistical model.
    score = (
        0.30 * entropy_score
        + 0.40 * distribution
        + 0.20 * bigram
        + 0.10 * trigram
    )

    return score


print("\n=== STATISTICAL TRANSITION RANKING ===\n")

ranks = []

for left, true_right in TRUE_PAIRS:

    candidates = []

    for right in blocks:

        if right == left:
            continue

        score = transition_score(left, right)

        candidates.append(
            (score, right)
        )

    candidates.sort(reverse=True)

    ranked_ids = [
        block_id
        for score, block_id in candidates
    ]

    rank = ranked_ids.index(true_right) + 1

    ranks.append(rank)

    top5 = candidates[:5]

    print(
        f"{left:02d} → {true_right:02d}"
        f" | Rank: {rank:2d}"
        f" | Top-5: "
        f"{[block_id for score, block_id in top5]}"
    )


print("\n=== SUMMARY ===")

total = len(ranks)

for k in [1, 3, 5, 10]:

    accuracy = sum(
        rank <= k
        for rank in ranks
    ) / total * 100

    print(
        f"Top-{k} accuracy: {accuracy:.2f}%"
    )

print(
    f"Average correct rank: "
    f"{sum(ranks) / total:.2f}"
)