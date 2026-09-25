from pathlib import Path

from core.jpeg_fragment_state import (
    analyze_fragment_state,
)

from core.jpeg_state_transition import (
    state_transition_score,
)


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


states = {
    block_id: analyze_fragment_state(
        block
    )
    for block_id, block in blocks.items()
}


GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18, 11,
    10, 27, 2, 9
]


print("\n=== JPEG STATE TRANSITION TEST ===\n")


print("GROUND-TRUTH TRANSITIONS\n")


for left, right in zip(
    GROUND_TRUTH,
    GROUND_TRUTH[1:]
):

    score = state_transition_score(
        states[left],
        states[right],
    )

    print(
        f"{left:02d} → {right:02d} "
        f"| "
        f"{states[left]['role']} → "
        f"{states[right]['role']} "
        f"| Score: {score:+.1f}"
    )


print("\nSELECTED FALSE TRANSITIONS\n")


FALSE_TRANSITIONS = [
    (34, 3),
    (34, 9),
    (34, 4),
    (24, 16),
    (24, 3),
    (3, 24),
    (3, 16),
    (16, 3),
    (30, 16),
    (30, 8),
    (32, 7),
    (2, 9),
    (31, 9),
]


for left, right in FALSE_TRANSITIONS:

    score = state_transition_score(
        states[left],
        states[right],
    )

    print(
        f"{left:02d} → {right:02d} "
        f"| "
        f"{states[left]['role']} → "
        f"{states[right]['role']} "
        f"| Score: {score:+.1f}"
    )