# backend/app/core/block_analyzer.py

import hashlib
import math


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of a byte sequence."""

    if not data:
        return 0.0

    frequency = [0] * 256

    for byte in data:
        frequency[byte] += 1

    entropy = 0.0
    length = len(data)

    for count in frequency:

        if count == 0:
            continue

        probability = count / length

        entropy -= probability * math.log2(probability)

    return round(entropy, 4)


def calculate_printable_ratio(data: bytes) -> float:
    """Calculate the proportion of printable ASCII bytes."""

    if not data:
        return 0.0

    printable = sum(
        1
        for byte in data
        if 32 <= byte <= 126
    )

    return round(printable / len(data), 4)


def analyze_block(data: bytes, block_id: int):

    trailing_zero_count = len(data) - len(
        data.rstrip(b"\x00")
    )

    return {
        "block_id": block_id,

        "size_bytes": len(data),

        "sha256": hashlib.sha256(data).hexdigest(),

        "entropy": calculate_entropy(data),

        "printable_ratio": calculate_printable_ratio(data),

        "starts_with_jpeg": data.startswith(
            b"\xFF\xD8\xFF"
        ),

        "contains_jpeg_header": (
            b"\xFF\xD8\xFF" in data
        ),

        "contains_jpeg_footer": (
            b"\xFF\xD9" in data
        ),

        "trailing_zero_bytes": trailing_zero_count,

        "likely_final_partial_block": (
            trailing_zero_count > 0
        ),
    }