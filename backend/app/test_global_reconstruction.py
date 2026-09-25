from pathlib import Path

from core.global_reconstructor import reconstruct_global


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


print()
print("=== GLOBAL RECONSTRUCTION TEST ===")
print()

beam = reconstruct_global(
    blocks,
    beam_width=50
)

print(
    f"Candidate paths: {len(beam)}"
)

print()


for index, candidate in enumerate(
    beam[:10],
    start=1
):

    path = candidate["path"]

    matches = sum(
        predicted == actual
        for predicted, actual in zip(
            path,
            GROUND_TRUTH
        )
    )

    print(
        f"#{index}"
    )

    print(
        f"Score: {candidate['score']:.4f}"
    )

    print(
        f"Prefix matches: "
        f"{matches}/{len(GROUND_TRUTH)}"
    )

    print(
        "Path:"
    )

    print(
        " → ".join(
            f"{block:02d}"
            for block in path
        )
    )

    print()