from .fragment_transition import calculate_fragment_transition
from .jpeg_anchor_graph import build_anchor_graph


def search_paths(
    blocks,
    start_block,
    end_block=None,
    max_depth=36,
    beam_width=200,
    min_depth=20,
):
    """
    Beam-search JPEG fragment reconstruction.

    Rules:
    - start_block must be first
    - end_block (EOI) must be the LAST block
    - EOI cannot appear in the middle of a candidate
    - reconstruction may finish at any depth between
      min_depth and max_depth
    """

    anchor_graph = build_anchor_graph(blocks)

    paths = [
        {
            "sequence": [start_block],
            "score": 0.0,
        }
    ]

    completed = []

    for depth in range(1, max_depth):

        candidates = []

        for path in paths:

            current = path["sequence"][-1]

            for next_block in blocks:

                if next_block in path["sequence"]:
                    continue

                # --------------------------------------------------
                # EOI can ONLY be the final block.
                # --------------------------------------------------
                if (
                    end_block is not None
                    and next_block == end_block
                ):
                    new_depth = len(path["sequence"]) + 1

                    if new_depth < min_depth:
                        continue

                transition = calculate_fragment_transition(
                    current,
                    next_block,
                    blocks,
                    anchor_graph=anchor_graph,
                )

                new_score = (
                    path["score"]
                    + transition["transition_score"]
                )

                new_sequence = (
                    path["sequence"] + [next_block]
                )

                # --------------------------------------------------
                # If this is EOI, COMPLETE the path immediately.
                # Never expand it further.
                # --------------------------------------------------
                if (
                    end_block is not None
                    and next_block == end_block
                ):
                    completed.append(
                        {
                            "sequence": new_sequence,
                            "score": new_score,
                        }
                    )
                    continue

                candidates.append(
                    {
                        "sequence": new_sequence,
                        "score": new_score,
                    }
                )

        if not candidates:
            break

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        paths = candidates[:beam_width]

        # Keep completed candidates under control.
        completed.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        completed = completed[:200]

    completed.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return completed[:100]