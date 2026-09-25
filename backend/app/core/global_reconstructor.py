from collections import Counter
import math


# ============================================================
# BASIC STATISTICS
# ============================================================

def entropy(data):
    if not data:
        return 0.0

    counts = Counter(data)
    n = len(data)

    return -sum(
        (count / n) * math.log2(count / n)
        for count in counts.values()
    )


def distribution_similarity(a, b):
    if not a or not b:
        return 0.0

    ca = Counter(a)
    cb = Counter(b)

    difference = 0.0

    for value in range(256):
        p = ca[value] / len(a)
        q = cb[value] / len(b)

        difference += abs(p - q)

    return 1.0 - difference / 2.0


def transition_score(left, right):

    entropy_score = max(
        0.0,
        1.0 - abs(
            entropy(left) - entropy(right)
        ) / 8.0
    )

    distribution_score = (
        distribution_similarity(left, right)
    )

    return (
        0.30 * entropy_score
        + 0.70 * distribution_score
    )


# ============================================================
# PRECOMPUTE ALL PAIRWISE TRANSITIONS
# ============================================================

def build_transition_matrix(blocks):

    matrix = {}

    block_ids = list(blocks.keys())

    for left_id in block_ids:

        matrix[left_id] = {}

        for right_id in block_ids:

            if left_id == right_id:
                continue

            matrix[left_id][right_id] = (
                transition_score(
                    blocks[left_id],
                    blocks[right_id]
                )
            )

    return matrix


# ============================================================
# START / END INFORMATION
# ============================================================

def start_score(block):

    score = 0.0

    # JPEG SOI
    if block.startswith(b"\xFF\xD8\xFF"):
        score += 2.0

    return score


def contains_eoi(block):

    return b"\xFF\xD9" in block


# ============================================================
# GLOBAL RECONSTRUCTION
# ============================================================

def reconstruct_global(
    blocks,
    beam_width=30
):

    if not blocks:
        return []

    print(
        "Building transition matrix..."
    )

    transition_matrix = (
        build_transition_matrix(blocks)
    )

    print(
        "Transition matrix ready."
    )

    # --------------------------------------------------------
    # Find possible starting blocks
    # --------------------------------------------------------

    starts = []

    for block_id, block in blocks.items():

        score = start_score(block)

        if score > 0:

            starts.append(
                (
                    score,
                    block_id
                )
            )

    starts.sort(
        reverse=True
    )

    if not starts:
        return []

    print(
        "Start candidates:",
        [block_id for _, block_id in starts]
    )

    # --------------------------------------------------------
    # Initial beam
    # --------------------------------------------------------

    beam = []

    for score, block_id in starts:

        beam.append({
            "path": [block_id],
            "score": score,
        })

    # --------------------------------------------------------
    # Expand beam
    # --------------------------------------------------------

    target_length = len(blocks)

    for step in range(
        1,
        target_length
    ):

        candidates = []

        for state in beam:

            path = state["path"]

            current = path[-1]

            used = set(path)

            for candidate_id in blocks:

                if candidate_id in used:
                    continue

                transition = (
                    transition_matrix[current]
                    [candidate_id]
                )

                new_score = (
                    state["score"]
                    + transition
                )

                # ------------------------------------------------
                # EOI constraint
                # ------------------------------------------------

                if contains_eoi(
                    blocks[candidate_id]
                ):

                    remaining = (
                        target_length
                        - len(path)
                        - 1
                    )

                    if remaining == 0:

                        # EOI at the end
                        new_score += 5.0

                    else:

                        # Penalize premature EOI
                        new_score -= (
                            remaining * 0.5
                        )

                candidates.append({

                    "path":
                        path + [candidate_id],

                    "score":
                        new_score,
                })

        if not candidates:
            break

        candidates.sort(
            key=lambda item:
                item["score"],
            reverse=True
        )

        beam = candidates[
            :beam_width
        ]

        # --------------------------------------------------------
        # Progress
        # --------------------------------------------------------

        print(
            f"Step {step:02d} | "
            f"Beam paths: {len(beam)} | "
            f"Best score: "
            f"{beam[0]['score']:.4f}"
        )

    return beam