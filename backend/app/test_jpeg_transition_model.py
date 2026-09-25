from pathlib import Path

from core.jpeg_fragment_features import analyze_fragment
from core.jpeg_transition import transition_score


STORAGE_PATH = Path(
    "samples/fragmented_storage.bin"
)

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


features = {
    block_id: analyze_fragment(
        block,
        block_id
    )
    for block_id, block in blocks.items()
}


GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21,
    30, 8, 14, 5, 35, 33, 0,
    19, 23, 12, 13, 26, 22,
    17, 28, 18, 11, 10, 27,
    2, 9
]


def rank_candidates(left_id, correct_id):

    scores = []

    for right_id in blocks:

        if right_id == left_id:
            continue

        result = transition_score(
            features[left_id],
            features[right_id]
        )

        scores.append(
            (
                result["score"],
                right_id,
                result
            )
        )

    scores.sort(
        key=lambda item: item[0],
        reverse=True
    )

    for rank, item in enumerate(
        scores,
        start=1
    ):
        if item[1] == correct_id:
            return rank, scores

    return None, scores


print(
    "\n=== JPEG-AWARE TRANSITION MODEL ===\n"
)


ranks = []

for left, right in zip(
    GROUND_TRUTH,
    GROUND_TRUTH[1:]
):

    rank, scores = rank_candidates(
        left,
        right
    )

    ranks.append(rank)

    correct_result = next(
        item[2]
        for item in scores
        if item[1] == right
    )

    print(
        f"{left:02d} → {right:02d} | "
        f"Rank={rank:2d} | "
        f"Score={correct_result['score']:.2f} | "
        f"Role={correct_result['role_score']:.2f} | "
        f"Scan={correct_result['scan_score']:.2f}"
    )

    print(
        "    "
        + "; ".join(
            correct_result["reasons"]
        )
    )


top1 = sum(
    rank == 1
    for rank in ranks
)

top3 = sum(
    rank <= 3
    for rank in ranks
)

top5 = sum(
    rank <= 5
    for rank in ranks
)

top10 = sum(
    rank <= 10
    for rank in ranks
)


print("\nSUMMARY")
print("-" * 50)

print(
    f"Transitions evaluated: {len(ranks)}"
)

print(
    f"Top-1 accuracy: "
    f"{top1 / len(ranks) * 100:.2f}%"
)

print(
    f"Top-3 accuracy: "
    f"{top3 / len(ranks) * 100:.2f}%"
)

print(
    f"Top-5 accuracy: "
    f"{top5 / len(ranks) * 100:.2f}%"
)

print(
    f"Top-10 accuracy: "
    f"{top10 / len(ranks) * 100:.2f}%"
)

print(
    f"Average correct rank: "
    f"{sum(ranks) / len(ranks):.2f}"
)