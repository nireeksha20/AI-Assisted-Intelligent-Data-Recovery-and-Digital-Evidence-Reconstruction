from .jpeg_anchors import extract_jpeg_anchors
from .jpeg_anchor_graph import build_anchor_graph
from .fragment_transition import calculate_fragment_transition


def get_strong_anchors(blocks):
    """
    Return reliable JPEG structural anchors.

    Weak marker-only blocks are excluded.
    """

    anchors = extract_jpeg_anchors(blocks)

    strong = {}

    for block_id, info in anchors.items():

        # Strong JPEG start:
        # SOI + successfully parsed scan.
        if info["has_soi"] and info["scans"]:
            strong[block_id] = "START"

        # Strong scan anchor:
        elif info["has_sos"] and info["scans"]:
            strong[block_id] = "SCAN"

        # Strong end:
        elif info["has_eoi"] and not info["has_soi"]:
            strong[block_id] = "END"

    return strong


def get_anchor_scan_types(blocks):
    """
    Extract the semantic scan type of every strong scan anchor.
    """

    anchors = extract_jpeg_anchors(blocks)

    result = {}

    for block_id, info in anchors.items():

        if not info["scans"]:
            continue

        scan = info["scans"][0]

        ss = scan["spectral_start"]
        se = scan["spectral_end"]
        ah = scan["successive_high"]

        if ss == 0 and se == 0:

            if ah == 0:
                scan_type = "DC_INITIAL"
            else:
                scan_type = "DC_REFINEMENT"

        elif ss > 0:

            if ah == 0:
                scan_type = "AC_INITIAL"
            else:
                scan_type = "AC_REFINEMENT"

        else:
            scan_type = "UNKNOWN"

        result[block_id] = scan_type

    return result


def get_valid_anchor_edges(blocks):
    """
    Return structural anchor relationships supported by
    progressive JPEG compatibility.
    """

    graph = build_anchor_graph(blocks)

    edges = []

    for left_id, candidates in graph.items():

        for candidate in candidates:

            # Only retain meaningful structural relationships.
            if candidate["score"] >= 4.0:

                edges.append({
                    "from": left_id,
                    "to": candidate["to"],
                    "score": candidate["score"],
                    "reasons": candidate["reasons"],
                })

    edges.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return edges


def score_fragment_between_anchors(
    left_anchor,
    right_anchor,
    fragment_id,
    blocks,
    anchor_graph
):
    """
    Score an entropy fragment as a possible member of the
    interval between two structural anchors.

    This is deliberately only a candidate score.
    """

    left_to_fragment = calculate_fragment_transition(
        left_anchor,
        fragment_id,
        blocks,
        anchor_graph=anchor_graph
    )

    fragment_to_right = calculate_fragment_transition(
        fragment_id,
        right_anchor,
        blocks,
        anchor_graph=anchor_graph
    )

    score = (
        left_to_fragment["statistical_score"]
        + right_to_right_score(fragment_to_right)
    ) / 2.0

    return {
        "fragment": fragment_id,
        "score": round(score, 4),
        "left_score": left_to_fragment["statistical_score"],
        "right_score": fragment_to_right["statistical_score"],
    }


def right_to_right_score(transition):
    """
    Extract the statistical transition component.
    Kept separate so the scoring logic is explicit.
    """

    return transition["statistical_score"]