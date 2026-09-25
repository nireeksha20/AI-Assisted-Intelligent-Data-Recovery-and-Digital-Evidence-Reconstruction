from .jpeg_analyzer import analyze_jpeg_block


def statistical_transition_score(left, right):
    """
    Lightweight statistical compatibility score.

    This is deliberately treated as weak evidence.
    It must not be interpreted as proof of adjacency.
    """

    import math
    from collections import Counter

    def entropy(data):
        counts = Counter(data)
        n = len(data)

        if n == 0:
            return 0.0

        return -sum(
            (count / n) * math.log2(count / n)
            for count in counts.values()
        )

    def distribution_similarity(a, b):
        ca = Counter(a)
        cb = Counter(b)

        total_a = len(a)
        total_b = len(b)

        if total_a == 0 or total_b == 0:
            return 0.0

        difference = 0.0

        for value in range(256):
            p = ca[value] / total_a
            q = cb[value] / total_b
            difference += abs(p - q)

        return 1.0 - difference / 2.0

    left_entropy = entropy(left)
    right_entropy = entropy(right)

    entropy_difference = abs(
        left_entropy - right_entropy
    )

    entropy_score = max(
        0.0,
        1.0 - entropy_difference / 8.0
    )

    distribution_score = distribution_similarity(
        left,
        right
    )

    # Weak score.
    return (
        0.30 * entropy_score
        + 0.70 * distribution_score
    )


def start_score(features):
    """
    Estimate how strongly a block resembles the
    beginning of a JPEG.
    """

    score = 0.0

    if features["starts_with_soi"]:
        score += 50

    if features["has_soi"]:
        score += 20

    if features["has_dqt"]:
        score += 10

    if features["has_sof"]:
        score += 10

    if features["has_dht"]:
        score += 5

    if features["has_sos"]:
        score += 5

    return score


def end_score(features):
    """
    Estimate how strongly a block resembles the
    end of a JPEG.
    """

    score = 0.0

    if features["has_eoi"]:
        score += 30

    if features["ends_with_eoi"]:
        score += 30

    return score


def suspicious_penalty(features):
    """
    Penalize blocks with structurally suspicious
    JPEG marker ordering.
    """

    if (
        features["has_soi"]
        and features["has_eoi"]
        and not features["valid_soi_eoi_order"]
    ):
        return 40.0

    return 0.0


def build_block_features(blocks):
    """
    Analyze every storage block once.
    """

    features = {}

    for block_id, data in blocks.items():

        result = analyze_jpeg_block(data)

        features[block_id] = result

    return features


def reconstruct_beam(
    blocks,
    beam_width=20,
    max_steps=None,
):
    """
    Reconstruct a fragmented JPEG using beam search.

    Returns ranked candidate paths.

    Ground-truth metadata is NOT used.
    """

    if not blocks:
        return []

    if max_steps is None:
        max_steps = len(blocks)

    features = build_block_features(blocks)

    # -------------------------------------------------
    # Find starting candidates
    # -------------------------------------------------

    starts = []

    for block_id, block_features in features.items():

        score = start_score(block_features)

        if score > 0:

            starts.append(
                (
                    score,
                    block_id
                )
            )

    starts.sort(reverse=True)

    starts = starts[:beam_width]

    # -------------------------------------------------
    # Initial beam
    # -------------------------------------------------

    beam = []

    for score, block_id in starts:

        beam.append(
            {
                "path": [block_id],
                "score": score,
            }
        )

    # -------------------------------------------------
    # Expand paths
    # -------------------------------------------------

    for step in range(1, max_steps):

        candidates = []

        for state in beam:

            path = state["path"]
            current = path[-1]

            for candidate in blocks:

                if candidate in path:
                    continue

                transition = statistical_transition_score(
                    blocks[current],
                    blocks[candidate]
                )

                candidate_features = features[candidate]

                score = (
                    state["score"]
                    + transition * 10.0
                )

                # Penalize suspicious blocks.
                score -= suspicious_penalty(
                    candidate_features
                )

                # Reward reaching a possible end.
                if candidate_features["has_eoi"]:

                    score += end_score(
                        candidate_features
                    )

                candidates.append(
                    {
                        "path": path + [candidate],
                        "score": score,
                    }
                )

        if not candidates:
            break

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        # Remove duplicate paths.
        unique = []

        seen = set()

        for candidate in candidates:

            path_tuple = tuple(candidate["path"])

            if path_tuple in seen:
                continue

            seen.add(path_tuple)
            unique.append(candidate)

            if len(unique) >= beam_width:
                break

        beam = unique

        # If every path has reached an EOI,
        # we can stop early.
        if all(
            features[state["path"][-1]]["has_eoi"]
            for state in beam
        ):
            break

    return beam