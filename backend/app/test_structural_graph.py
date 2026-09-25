from pathlib import Path

from core.progressive_constraints import (
    extract_progressive_constraints,
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

features = extract_progressive_constraints(blocks)


STRUCTURAL_BLOCKS = [
    block_id
    for block_id, info in features.items()
    if info["scan_count"] > 0
]


def describe_transition(left_id, right_id):

    left = features[left_id]
    right = features[right_id]

    left_scan = left["scans"][-1]
    right_scan = right["scans"][0]

    score = 0
    reasons = []

    # Same spectral band
    if (
        left_scan["spectral_start"]
        == right_scan["spectral_start"]
        and
        left_scan["spectral_end"]
        == right_scan["spectral_end"]
    ):
        score += 1
        reasons.append("same spectral band")

    # Same components
    if (
        left_scan["components"]
        == right_scan["components"]
    ):
        score += 2
        reasons.append("same components")

    # DC progression
    if (
        left_scan["type"] == "DC_INITIAL"
        and
        right_scan["type"] == "DC_REFINEMENT"
        and
        right_scan["successive_high"]
        == left_scan["successive_low"]
    ):
        score += 5
        reasons.append(
            "valid DC initial → refinement"
        )

    elif (
        left_scan["type"] == "DC_REFINEMENT"
        and
        right_scan["type"] == "DC_REFINEMENT"
        and
        right_scan["successive_high"]
        == left_scan["successive_low"]
    ):
        score += 5
        reasons.append(
            "valid DC refinement continuation"
        )

    # AC progression
    if (
        left_scan["type"] == "AC_INITIAL"
        and
        right_scan["type"] == "AC_REFINEMENT"
    ):
        if (
            left_scan["components"]
            == right_scan["components"]
        ):
            score += 4
            reasons.append(
                "same-component AC refinement"
            )

        if (
            right_scan["successive_high"]
            == left_scan["successive_low"]
        ):
            score += 3
            reasons.append(
                "valid AC refinement level"
            )

    # New AC scan after DC scan
    if (
        left_scan["type"]
        in ("DC_INITIAL", "DC_REFINEMENT")
        and
        right_scan["type"]
        in ("AC_INITIAL", "AC_REFINEMENT")
    ):
        score += 2
        reasons.append(
            "DC → AC scan progression"
        )

    return score, reasons


print()
print("=== STRUCTURAL JPEG GRAPH ===")
print()

print(
    "Structural blocks:",
    STRUCTURAL_BLOCKS
)

print()

for left in STRUCTURAL_BLOCKS:

    candidates = []

    for right in STRUCTURAL_BLOCKS:

        if left == right:
            continue

        score, reasons = describe_transition(
            left,
            right
        )

        candidates.append(
            (
                score,
                right,
                reasons
            )
        )

    candidates.sort(
        key=lambda item: (
            item[0],
            -item[1]
        ),
        reverse=True
    )

    print(
        f"FROM BLOCK {left:02d}"
    )

    for score, right, reasons in candidates[:8]:

        print(
            f"  → {right:02d} | "
            f"score={score}"
        )

        for reason in reasons:
            print(
                f"      - {reason}"
            )

    print()