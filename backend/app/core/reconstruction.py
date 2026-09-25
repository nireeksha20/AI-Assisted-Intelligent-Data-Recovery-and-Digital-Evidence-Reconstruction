# backend/app/core/reconstruction.py

import hashlib


def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def byte_similarity(left: bytes, right: bytes, window: int = 32) -> float:
    """
    Compare the end of one fragment with the beginning
    of another fragment.

    Returns a score between 0 and 1.
    """

    if not left or not right:
        return 0.0

    left_tail = left[-window:]
    right_head = right[:window]

    length = min(len(left_tail), len(right_head))

    if length == 0:
        return 0.0

    matches = sum(
        1
        for i in range(length)
        if left_tail[i] == right_head[i]
    )

    return matches / length


def calculate_transition_score(
    left: bytes,
    right: bytes,
) -> float:
    """
    Calculate how compatible two fragments are.

    This is our first reconstruction heuristic.
    """

    similarity = byte_similarity(left, right)

    return round(similarity * 100, 2)


def build_transition_matrix(fragments: list[dict]) -> list[dict]:
    """
    Calculate pairwise transition scores.
    """

    transitions = []

    for left in fragments:

        for right in fragments:

            if left["fragment_id"] == right["fragment_id"]:
                continue

            score = calculate_transition_score(
                left["data"],
                right["data"],
            )

            transitions.append({
                "from": left["fragment_id"],
                "to": right["fragment_id"],
                "score": score,
            })

    return transitions


def reconstruct_greedy(fragments: list[dict]) -> list[int]:
    """
    Build an ordering using the strongest available
    transition at each step.

    This is a baseline algorithm, not the final AI
    reconstruction engine.
    """

    if not fragments:
        return []

    unused = {
        fragment["fragment_id"]
        for fragment in fragments
    }

    fragment_map = {
        fragment["fragment_id"]: fragment
        for fragment in fragments
    }

    # Start with the fragment containing a known file header.
    start_fragment = None

    for fragment in fragments:

        data = fragment["data"]

        if (
            data.startswith(b"%PDF")
            or data.startswith(b"\xFF\xD8\xFF")
            or data.startswith(b"\x89PNG\r\n\x1a\n")
        ):
            start_fragment = fragment["fragment_id"]
            break

    # If no obvious start exists, use the first fragment.
    if start_fragment is None:
        start_fragment = fragments[0]["fragment_id"]

    order = [start_fragment]
    unused.remove(start_fragment)

    current = start_fragment

    while unused:

        best_fragment = None
        best_score = -1

        for candidate in unused:

            score = calculate_transition_score(
                fragment_map[current]["data"],
                fragment_map[candidate]["data"],
            )

            if score > best_score:
                best_score = score
                best_fragment = candidate

        if best_fragment is None:
            break

        order.append(best_fragment)
        unused.remove(best_fragment)

        current = best_fragment

    return order