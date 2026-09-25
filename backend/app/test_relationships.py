from pathlib import Path

from core.fragment_relationship import (
    calculate_transition_score,
)


storage_path = Path(
    "samples/fragmented_storage.bin"
)

data = storage_path.read_bytes()

block_size = 4096

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


print("\nTesting fragment relationships...\n")


# Test every possible transition.

transitions = []

for left in blocks:

    for right in blocks:

        if (
            left["block_id"]
            == right["block_id"]
        ):
            continue

        result = calculate_transition_score(
            left["data"],
            right["data"],
        )

        transitions.append({
            "from": left["block_id"],
            "to": right["block_id"],
            **result,
        })


# Sort by strongest transition.

transitions.sort(
    key=lambda item:
        item["transition_score"],
    reverse=True,
)


print("Top 20 candidate transitions:\n")

for transition in transitions[:20]:

    print(
        f"Block "
        f"{transition['from']:02d}"
        f" -> "
        f"{transition['to']:02d}"
        f" | Score: "
        f"{transition['transition_score']:.4f}"
        f" | Boundary: "
        f"{transition['boundary_similarity']:.4f}"
        f" | Entropy: "
        f"{transition['entropy_compatibility']:.4f}"
        f" | Marker: "
        f"{transition['jpeg_marker_score']:.4f}"
    )