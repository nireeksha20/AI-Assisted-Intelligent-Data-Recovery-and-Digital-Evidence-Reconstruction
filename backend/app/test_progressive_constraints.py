from pathlib import Path

from core.progressive_constraints import (
    extract_progressive_constraints,
    compare_structural_blocks,
)


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


features = extract_progressive_constraints(
    blocks
)


print()
print("=== PROGRESSIVE JPEG STRUCTURAL ANALYSIS ===")
print()


for block_id in sorted(features):

    info = features[block_id]

    if not info["scans"]:
        continue

    print(
        f"BLOCK {block_id:02d}"
    )

    print(
        f"  Role: {info['role']}"
    )

    for index, scan in enumerate(
        info["scans"],
        start=1
    ):

        print(
            f"  Scan {index}: "
            f"{scan['type']}"
        )

        print(
            f"    Components: "
            f"{scan['components']}"
        )

        print(
            f"    Spectral: "
            f"{scan['spectral_start']} "
            f"→ "
            f"{scan['spectral_end']}"
        )

        print(
            f"    Ah/Al: "
            f"{scan['successive_high']} "
            f"→ "
            f"{scan['successive_low']}"
        )

    print()


print()
print(
    "=== STRUCTURAL TRANSITION CHECKS ==="
)
print()


pairs = [
    (34, 3),
    (3, 16),
    (16, 32),
    (32, 30),
    (30, 8),
    (8, 12),
    (12, 28),
]


for left, right in pairs:

    result = compare_structural_blocks(
        features[left],
        features[right]
    )

    print(
        f"{left:02d} → {right:02d}"
    )

    print(
        f"  Score: "
        f"{result['score']}"
    )

    for reason in result["reasons"]:

        print(
            f"  - {reason}"
        )

    print()