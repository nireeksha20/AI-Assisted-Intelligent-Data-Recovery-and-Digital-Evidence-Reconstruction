from pathlib import Path

from core.jpeg_fragment_features import analyze_fragment
from core.global_reconstructor import (
    build_transition_matrix,
)


STORAGE_PATH = Path(
    "samples/fragmented_storage.bin"
)

BLOCK_SIZE = 4096

GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18,
    11, 10, 27, 2, 9
]


data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):

    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


features = {}

for block_id, block in blocks.items():

    features[block_id] = analyze_fragment(
        block,
        block_id
    )


matrix = build_transition_matrix(
    blocks
)


IMPORTANT_TRANSITIONS = [
    (21, 30),
    (8, 14),
    (12, 13),
    (2, 9),
]


for left, correct in IMPORTANT_TRANSITIONS:

    print()
    print("=" * 70)

    print(
        f"TRUE TRANSITION: "
        f"{left:02d} → {correct:02d}"
    )

    print("=" * 70)

    candidates = []

    for candidate in blocks:

        if candidate == left:
            continue

        candidates.append(
            (
                matrix[left][candidate],
                candidate
            )
        )

    candidates.sort(
        reverse=True
    )

    correct_rank = next(
        index
        for index, (_, candidate) in enumerate(
            candidates,
            start=1
        )
        if candidate == correct
    )

    print(
        f"True successor rank: "
        f"{correct_rank}"
    )

    print()

    print(
        "Top candidates:"
    )

    for rank, (score, candidate) in enumerate(
        candidates[:10],
        start=1
    ):

        candidate_features = (
            features[candidate]
        )

        print(
            f"{rank:2d}. "
            f"{candidate:02d} | "
            f"score={score:.6f} | "
            f"role={candidate_features['role']} | "
            f"markers={candidate_features['markers']} | "
            f"scans={candidate_features['scan_count']}"
        )

    print()

    print(
        "TRUE CANDIDATE FEATURES:"
    )

    print(
        features[correct]
    )