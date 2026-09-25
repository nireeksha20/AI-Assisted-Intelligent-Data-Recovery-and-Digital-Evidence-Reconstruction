from pathlib import Path

from core.jpeg_analyzer import scan_jpeg_structure


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


def marker_summary(data):
    markers = scan_jpeg_structure(data)

    return [
        (
            marker["name"],
            marker["offset"]
        )
        for marker in markers
    ]


def test_transition(left_id, right_id):

    left = blocks[left_id]
    right = blocks[right_id]

    combined = left + right

    markers = scan_jpeg_structure(combined)

    print(
        f"\n{left_id:02d} → {right_id:02d}"
    )

    print(
        f"Left markers : {marker_summary(left)}"
    )

    print(
        f"Right markers: {marker_summary(right)}"
    )

    print(
        f"Combined markers: "
        f"{[(m['name'], m['offset']) for m in markers]}"
    )


print("\n=== JPEG TRANSITION ANALYSIS ===")


# Known correct transitions
correct_pairs = [
    (34, 24),
    (24, 3),
    (3, 16),
    (16, 32),
    (32, 7),
    (7, 21),
    (21, 30),
    (30, 8),
]


print("\n--- CORRECT TRANSITIONS ---")

for left, right in correct_pairs:
    test_transition(left, right)


print("\n--- INCORRECT TRANSITIONS ---")

wrong_pairs = [
    (34, 3),
    (34, 16),
    (24, 16),
    (3, 24),
    (16, 3),
    (32, 3),
    (30, 16),
]

for left, right in wrong_pairs:
    test_transition(left, right)