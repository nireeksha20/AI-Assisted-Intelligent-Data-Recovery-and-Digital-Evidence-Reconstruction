from pathlib import Path


STORAGE_PATH = Path("samples/fragmented_storage.bin")

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


print("\n=== FRAGMENT BOUNDARY ANALYSIS ===\n")


for block_id in range(len(blocks)):

    block = blocks[block_id]

    first_bytes = block[:16]

    print(
        f"Block {block_id:02d} | "
        f"First 16 bytes: {first_bytes.hex(' ')}"
    )