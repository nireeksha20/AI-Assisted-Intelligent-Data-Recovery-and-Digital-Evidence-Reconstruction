import json
from pathlib import Path

from core.fragment_relationship import (
    calculate_transition_score,
)


# ---------------------------------------------------------
# Load ground truth
# ---------------------------------------------------------

metadata_path = Path(
    "samples/fragment_metadata.json"
)

metadata = json.loads(
    metadata_path.read_text()
)


# ---------------------------------------------------------
# Load storage
# ---------------------------------------------------------

storage_path = Path(
    "samples/fragmented_storage.bin"
)

data = storage_path.read_bytes()

block_size = metadata["fragment_size"]


# ---------------------------------------------------------
# Build storage blocks
# ---------------------------------------------------------

blocks = []

for block_id, offset in enumerate(
    range(0, len(data), block_size)
):

    block = data[
        offset:offset + block_size
    ]

    blocks.append({
        "block_id": block_id,
        "data": block,
    })


# ---------------------------------------------------------
# Map fragment ID → storage block ID
#
# This mapping is ONLY used for evaluation.
# The reconstruction algorithm itself does NOT receive it.
# ---------------------------------------------------------

fragment_to_block = {}

for storage_block in metadata["storage_blocks"]:

    if storage_block["block_type"] == "fragment":

        fragment_id = storage_block["fragment_id"]

        block_id = storage_block[
            "storage_block_id"
        ]

        fragment_to_block[
            fragment_id
        ] = block_id


# ---------------------------------------------------------
# Calculate every transition
# ---------------------------------------------------------

transitions = []

for left in blocks:

    for right in blocks:

        if (
            left["block_id"]
            == right["block_id"]
        ):
            continue

        score = calculate_transition_score(
            left["data"],
            right["data"],
        )

        transitions.append({
            "from": left["block_id"],
            "to": right["block_id"],
            "score": score["transition_score"],
        })


# ---------------------------------------------------------
# Evaluate the true JPEG transitions
# ---------------------------------------------------------

print("\n=== GROUND TRUTH TRANSITION EVALUATION ===\n")

correct_ranks = []

for fragment_id in range(
    metadata["fragment_count"] - 1
):

    next_fragment = fragment_id + 1

    true_from = fragment_to_block[
        fragment_id
    ]

    true_to = fragment_to_block[
        next_fragment
    ]

    candidates = [
        transition
        for transition in transitions
        if transition["from"] == true_from
    ]

    candidates.sort(
        key=lambda item:
        item["score"],
        reverse=True,
    )

    rank = next(
        (
            index + 1
            for index, candidate
            in enumerate(candidates)
            if candidate["to"] == true_to
        ),
        None,
    )

    correct_ranks.append(rank)

    print(
        f"Fragment {fragment_id:02d}"
        f" → "
        f"{next_fragment:02d}"
        f" | Storage block "
        f"{true_from:02d}"
        f" → "
        f"{true_to:02d}"
        f" | Rank: "
        f"{rank}"
    )


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

valid_ranks = [
    rank
    for rank in correct_ranks
    if rank is not None
]

print("\n=== SUMMARY ===")

print(
    "Transitions evaluated:",
    len(valid_ranks)
)

if valid_ranks:

    top1 = sum(
        1
        for rank in valid_ranks
        if rank == 1
    )

    top5 = sum(
        1
        for rank in valid_ranks
        if rank <= 5
    )

    print(
        "Top-1 accuracy:",
        round(
            top1 / len(valid_ranks) * 100,
            2
        ),
        "%"
    )

    print(
        "Top-5 accuracy:",
        round(
            top5 / len(valid_ranks) * 100,
            2
        ),
        "%"
    )

    print(
        "Average correct-transition rank:",
        round(
            sum(valid_ranks)
            / len(valid_ranks),
            2
        )
    )