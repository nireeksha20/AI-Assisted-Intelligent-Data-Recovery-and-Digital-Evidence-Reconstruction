from .fragment_analyzer import calculate_entropy
import math


def byte_distribution(data: bytes):
    counts = [0] * 256

    if not data:
        return counts

    for byte in data:
        counts[byte] += 1

    total = len(data)

    return [count / total for count in counts]


def distribution_similarity(left: bytes, right: bytes):
    """
    Cosine similarity between byte-frequency distributions.
    Used as a statistical compatibility signal between fragments.
    """

    left_dist = byte_distribution(left)
    right_dist = byte_distribution(right)

    dot = sum(
        left_dist[i] * right_dist[i]
        for i in range(256)
    )

    left_norm = math.sqrt(
        sum(value * value for value in left_dist)
    )

    right_norm = math.sqrt(
        sum(value * value for value in right_dist)
    )

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def entropy_compatibility(left: bytes, right: bytes):
    left_entropy = calculate_entropy(left)
    right_entropy = calculate_entropy(right)

    difference = abs(left_entropy - right_entropy)

    return 1.0 - min(difference / 8.0, 1.0)


def calculate_transition_score(left: bytes, right: bytes):
    """
    Statistical fragment compatibility.

    Distribution similarity is the primary signal.
    Entropy compatibility is the secondary signal.

    This replaces the previous boundary-byte comparison,
    which is unreliable for shuffled fixed-size fragments.
    """

    distribution = distribution_similarity(left, right)
    entropy = entropy_compatibility(left, right)

    score = (
        0.70 * distribution
        + 0.30 * entropy
    )

    return {
        "distribution_similarity": round(distribution, 4),
        "entropy_compatibility": round(entropy, 4),
        "transition_score": round(score, 4),
    }


def calculate_fragment_transition(
    left_id,
    right_id,
    blocks,
    anchor_graph=None,
):
    left = blocks[left_id]
    right = blocks[right_id]

    statistical = calculate_transition_score(left, right)

    anchor_score = 0.0
    anchor_reasons = []

    if anchor_graph is not None:
        for candidate in anchor_graph.get(left_id, []):
            if candidate["to"] == right_id:
                anchor_score = candidate["score"]
                anchor_reasons = candidate["reasons"]
                break

    normalized_anchor = min(anchor_score / 10.0, 1.0)

    combined_score = (
        0.70 * statistical["transition_score"]
        + 0.30 * normalized_anchor
    )

    return {
        "left_block": left_id,
        "right_block": right_id,
        "distribution_similarity":
            statistical["distribution_similarity"],
        "entropy_compatibility":
            statistical["entropy_compatibility"],
        "statistical_score":
            statistical["transition_score"],
        "anchor_score":
            round(normalized_anchor, 4),
        "transition_score":
            round(combined_score, 4),
        "reasons":
            anchor_reasons,
    }