from pathlib import Path

from core.jpeg_sequence import validate_jpeg_sequence


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


def build_sequence(block_ids):
    return b"".join(blocks[block_id] for block_id in block_ids)


def test(block_ids):
    data = build_sequence(block_ids)

    result = validate_jpeg_sequence(data)

    print(
        f"{block_ids}"
        f" | Valid: {result['valid']}"
        f" | Status: {result['status']}"
        f" | Score: {result['score']}"
        f" | Markers: {result['marker_count']}"
    )

    if result.get("reasons"):
        print(
            f"    Reasons: {'; '.join(result['reasons'])}"
        )


print("\n=== STRICT JPEG SEQUENCE VALIDATOR ===\n")


# Start only
test([34])

# Correct beginning, but early EOI
test([34, 24, 3, 9])

# Correct beginning without EOI
test([34, 24, 3])

# Correct full reconstruction
GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18, 11,
    10, 27, 2, 9
]

test(GROUND_TRUTH)

# Wrong ordering containing the EOI block early
test([
    34, 3, 9, 24, 20, 15, 29, 4,
    1, 6, 25, 26, 22, 17, 11, 18,
    10, 2, 28, 13, 8, 21, 5, 14,
    23, 33, 0, 12
])