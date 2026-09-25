from pathlib import Path

from core.jpeg_entropy_parser import find_entropy_regions


STORAGE_PATH = Path("samples/fragmented_storage.bin")

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


SCAN_BLOCKS = [3, 8, 12, 16, 28, 30, 32, 34]


print("\n=== JPEG ENTROPY REGION ANALYSIS ===\n")


for block_id in SCAN_BLOCKS:

    print(f"\nBLOCK {block_id:02d}")

    regions = find_entropy_regions(blocks[block_id])

    if not regions:
        print("  No complete entropy region detected")
        continue

    for index, region in enumerate(regions, start=1):

        print(f"  Region {index}")

        print(
            f"    SOS offset: "
            f"{region['sos_offset']}"
        )

        print(
            f"    Entropy start: "
            f"{region['entropy_start']}"
        )

        print(
            f"    Entropy end: "
            f"{region['entropy_end']}"
        )

        print(
            f"    Entropy bytes: "
            f"{region['entropy_size']}"
        )