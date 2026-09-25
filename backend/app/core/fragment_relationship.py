# backend/app/core/fragment_relationship.py

import math


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy."""

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

    return entropy


def boundary_similarity(
    left: bytes,
    right: bytes,
    window: int = 64,
) -> float:
    """
    Compare the tail of one fragment with the beginning
    of another.

    This is only one weak signal.
    """

    if not left or not right:
        return 0.0

    left_tail = left[-window:]
    right_head = right[:window]

    length = min(
        len(left_tail),
        len(right_head)
    )

    matches = sum(
        1
        for i in range(length)
        if left_tail[i] == right_head[i]
    )

    return matches / length


def entropy_compatibility(
    left: bytes,
    right: bytes,
) -> float:
    """
    Measure whether two fragments have similar entropy.

    Returns a value between 0 and 1.
    """

    left_entropy = calculate_entropy(left)
    right_entropy = calculate_entropy(right)

    difference = abs(
        left_entropy - right_entropy
    )

    # Maximum possible entropy difference for a byte
    # sequence is approximately 8 bits.
    score = 1 - min(difference / 8.0, 1.0)

    return score


def jpeg_marker_score(
    left: bytes,
    right: bytes,
) -> float:
    """
    Basic JPEG structural compatibility.

    This does NOT claim that marker presence proves
    fragment ordering.
    """

    score = 0.5

    # A fragment beginning with JPEG SOI should normally
    # be the beginning of the file, not a continuation.
    if right.startswith(b"\xFF\xD8\xFF"):
        score -= 0.4

    # A fragment ending with EOI should normally be the
    # final fragment.
    if left.endswith(b"\xFF\xD9"):
        score -= 0.4

    return max(0.0, min(score, 1.0))


def calculate_transition_score(
    left: bytes,
    right: bytes,
) -> dict:
    """
    Calculate a multi-signal transition score.

    The score estimates how compatible `right` is as the
    fragment immediately following `left`.
    """

    boundary = boundary_similarity(
        left,
        right
    )

    entropy = entropy_compatibility(
        left,
        right
    )

    marker = jpeg_marker_score(
        left,
        right
    )

    # Initial baseline weighting.
    #
    # Boundary similarity receives the largest weight,
    # while entropy and structural compatibility provide
    # supporting evidence.
    score = (
        0.50 * boundary
        + 0.25 * entropy
        + 0.25 * marker
    )

    return {
        "boundary_similarity": round(
            boundary,
            4
        ),

        "entropy_compatibility": round(
            entropy,
            4
        ),

        "jpeg_marker_score": round(
            marker,
            4
        ),

        "transition_score": round(
            score,
            4
        ),
    }