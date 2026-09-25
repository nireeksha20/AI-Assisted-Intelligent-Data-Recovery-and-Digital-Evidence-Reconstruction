from pathlib import Path

from core.reconstructor import reconstruct_beam


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


print("\n=== BEAM SEARCH RECONSTRUCTION ===\n")

results = reconstruct_beam(
    blocks,
    beam_width=20,
    max_steps=28,
)

for rank, result in enumerate(
    results[:10],
    start=1
):

    print(
        f"{rank:02d}."
        f" Score: {result['score']:.2f}"
        f" | Length: {len(result['path'])}"
        f" | Path: {result['path']}"
    )