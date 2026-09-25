from pathlib import Path

from core.jpeg_fragment_state import analyze_fragment_state


STORAGE_PATH = Path(
    "samples/fragmented_storage.bin"
)

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

print("\n=== JPEG FRAGMENT STATES ===\n")

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):

    block = data[
        offset:offset + BLOCK_SIZE
    ]

    state = analyze_fragment_state(
        block
    )

    print(
        f"Block {block_id:02d} | "
        f"Role: {state['role']:<24} | "
        f"Markers: {state['markers']}"
    )