from pathlib import Path

from core.jpeg_entropy_validator import (
    validate_entropy_sequence,
)


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


def build_sequence(path):
    return b"".join(
        blocks[block_id]
        for block_id in path
    )


TESTS = {
    "FULL GROUND TRUTH": GROUND_TRUTH,

    "SHORT PREFIX": [
        34, 24, 3, 16
    ],

    "FALSE SHORTCUT": [
        34, 3, 16, 32, 30, 8, 12, 28, 9
    ],

    "WRONG START": [
        20, 15, 6, 25, 26, 22, 17, 9
    ],

    "TRUE PREFIX WITH EARLY EOI": [
        34, 24, 3, 9
    ],
}


print()
print("=== JPEG ENTROPY VALIDATOR ===")
print()

for name, path in TESTS.items():

    sequence = build_sequence(path)

    result = validate_entropy_sequence(
        sequence
    )

    print(name)

    print(
        "Path:",
        " → ".join(
            f"{x:02d}"
            for x in path
        )
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "Valid:",
        result["valid"]
    )

    print(
        "Status:",
        result["status"]
    )

    print(
        "Markers:",
        result.get("marker_count")
    )

    print(
        "Scans:",
        result.get("scan_count")
    )

    for reason in result["reasons"]:
        print(
            " -",
            reason
        )

    print()