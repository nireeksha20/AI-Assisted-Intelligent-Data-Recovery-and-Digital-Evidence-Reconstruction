from .jpeg_anchors import extract_jpeg_anchors
from .jpeg_anchor_graph import build_anchor_graph


def classify_structural_role(block_id, anchor):
    """
    Classify the reliability of structural evidence in a block.
    """

    # A strong JPEG start should contain SOI plus
    # meaningful JPEG scan/header structure.
    if anchor["has_soi"] and anchor["scans"]:
        return "START_ANCHOR"

    # SOI without a valid scan is suspicious/weak evidence.
    if anchor["has_soi"]:
        return "WEAK_STRUCTURAL"

    if anchor["has_eoi"] and not anchor["has_soi"]:
        return "END_ANCHOR"

    if anchor["has_sos"]:

        if anchor["scans"]:
            return "SCAN_ANCHOR"

        return "WEAK_SCAN_ANCHOR"

    if anchor["markers"]:
        return "WEAK_STRUCTURAL"

    return "ENTROPY"


def identify_jpeg_roles(blocks):

    anchors = extract_jpeg_anchors(blocks)

    roles = {
        "start": [],
        "scan_anchors": [],
        "end": [],
        "weak_structural": [],
        "entropy": [],
    }

    details = {}

    for block_id, anchor in anchors.items():

        role = classify_structural_role(
            block_id,
            anchor
        )

        details[block_id] = {
            "role": role,
            "markers": [
                marker["name"]
                for marker in anchor["markers"]
            ],
            "scan_count": len(anchor["scans"]),
        }

        if role == "START_ANCHOR":
            roles["start"].append(block_id)

        elif role == "SCAN_ANCHOR":
            roles["scan_anchors"].append(block_id)

        elif role == "END_ANCHOR":
            roles["end"].append(block_id)

        elif role == "WEAK_STRUCTURAL":
            roles["weak_structural"].append(block_id)

        else:
            roles["entropy"].append(block_id)

    return {
        "roles": roles,
        "details": details,
    }


def get_structural_order_candidates(blocks):

    anchor_graph = build_anchor_graph(blocks)

    candidates = []

    for left_id, edges in anchor_graph.items():

        for edge in edges:

            candidates.append({
                "from": left_id,
                "to": edge["to"],
                "score": edge["score"],
                "reasons": edge["reasons"],
            })

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return candidates