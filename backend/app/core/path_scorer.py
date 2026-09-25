from .jpeg_fragment_features import analyze_fragment
from .jpeg_transition import transition_score


def path_score(path, blocks, features):
    if not path:
        return float("-inf")

    score = 0.0

    # --------------------------------------------------
    # 1. START
    # --------------------------------------------------

    first = features[path[0]]

    if first["role"] == "START":
        score += 50.0
    else:
        score -= 50.0

    # --------------------------------------------------
    # 2. TRANSITIONS
    # --------------------------------------------------

    for left_id, right_id in zip(
        path,
        path[1:]
    ):
        left = blocks[left_id]
        right = blocks[right_id]

        transition = transition_score(
            features[left_id],
            features[right_id]
        )

        score += transition["score"]

    # --------------------------------------------------
    # 3. EOI POSITION
    # --------------------------------------------------

    eoi_positions = []

    for block_id in path:

        feature = features[block_id]

        if feature["has_eoi"]:
            eoi_positions.append(
                path.index(block_id)
            )

    if eoi_positions:

        last_eoi = eoi_positions[-1]

        # EOI should normally occur near the
        # end of the reconstructed sequence.

        distance_from_end = (
            len(path) - 1 - last_eoi
        )

        if distance_from_end == 0:
            score += 40.0

        else:
            score -= (
                distance_from_end * 10.0
            )

    # --------------------------------------------------
    # 4. Suspicious blocks
    # --------------------------------------------------

    for block_id in path:

        if features[block_id]["role"] == "SUSPICIOUS":
            score -= 25.0

    # --------------------------------------------------
    # 5. Duplicate SOI
    # --------------------------------------------------

    soi_count = sum(
        features[block_id]["has_soi"]
        for block_id in path
    )

    if soi_count == 1:
        score += 20.0

    elif soi_count > 1:
        score -= 40.0 * (soi_count - 1)

    return score