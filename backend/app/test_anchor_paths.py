from pathlib import Path
from collections import Counter
import math


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


def pair_score(a, b):

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
        +
        0.70 * distribution_score
    )


def beam_between(
    start,
    end,
    beam_width=20,
    max_length=12
):

    initial = {
        "path": [start],
        "score": 0.0
    }

    beam = [initial]

    for depth in range(1, max_length + 1):

        candidates = []

        for state in beam:

            current = state["path"][-1]

            # Direct arrival at endpoint
            if current != end:

                for candidate in blocks:

                    if candidate in state["path"]:
                        continue

                    # Don't use the endpoint until
                    # we explicitly score arrival.
                    if candidate == end:

                        score = (
                            state["score"]
                            +
                            pair_score(
                                blocks[current],
                                blocks[end]
                            )
                        )

                        candidates.append({
                            "path":
                                state["path"]
                                + [end],
                            "score": score
                        })

                    else:

                        score = (
                            state["score"]
                            +
                            pair_score(
                                blocks[current],
                                blocks[candidate]
                            )
                        )

                        candidates.append({
                            "path":
                                state["path"]
                                + [candidate],
                            "score": score
                        })

        if not candidates:
            break

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        beam = candidates[:beam_width]

        # Keep only paths that have reached
        # the endpoint if one exists.
        completed = [
            state
            for state in beam
            if state["path"][-1] == end
        ]

        if completed:
            completed.sort(
                key=lambda x: x["score"],
                reverse=True
            )

            return completed

    return []


TESTS = [
    (34, 3, [34, 24, 3]),
    (16, 30, [16, 32, 7, 21, 30]),
    (30, 12, [
        30, 8, 14, 5, 35,
        33, 0, 19, 23, 12
    ]),
]


print()
print("=== ANCHOR-TO-ANCHOR PATH TEST ===")
print()


for start, end, truth in TESTS:

    print(
        f"{start:02d} → {end:02d}"
    )

    print(
        "Ground truth:",
        " → ".join(
            f"{x:02d}"
            for x in truth
        )
    )

    results = beam_between(
        start,
        end
    )

    if not results:

        print(
            "No candidate path found."
        )
        print()

        continue

    for rank, result in enumerate(
        results[:5],
        start=1
    ):

        path = result["path"]

        matches = sum(
            a == b
            for a, b in zip(
                path,
                truth
            )
        )

        print(
            f"{rank}.",
            " → ".join(
                f"{x:02d}"
                for x in path
            ),
            f"| score={result['score']:.4f}",
            f"| prefix_matches={matches}"
        )

    print()