from pathlib import Path


STORAGE_PATH = Path("samples/fragmented_storage.bin")

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


def find_positions(data: bytes, pattern: bytes):
    positions = []
    start = 0

    while True:
        position = data.find(pattern, start)

        if position == -1:
            break

        positions.append(position)
        start = position + 1

    return positions


for block_id in [3, 16, 32, 34]:

    block = blocks[block_id]

    positions = find_positions(block, b"\xFF\x00")

    print(f"\nBLOCK {block_id:02d}")
    print(f"FF00 count: {len(positions)}")

    if positions:
        print(f"First 20 positions: {positions[:20]}")
        print(f"Last 20 positions:  {positions[-20:]}")