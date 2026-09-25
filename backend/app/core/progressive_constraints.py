from .jpeg_fragment_features import analyze_fragment


def scan_signature(scan):
    """
    Create a compact representation of a progressive JPEG scan.
    """

    components = tuple(
        component["component_id"]
        for component in scan["components"]
    )

    return {
        "component_count": scan["component_count"],
        "components": components,
        "spectral_start": scan["spectral_start"],
        "spectral_end": scan["spectral_end"],
        "successive_high": scan["successive_high"],
        "successive_low": scan["successive_low"],
    }


def classify_scan(scan):
    """
    Classify the progressive JPEG scan.
    """

    ss = scan["spectral_start"]
    se = scan["spectral_end"]
    ah = scan["successive_high"]
    al = scan["successive_low"]

    # DC scan
    if ss == 0 and se == 0:

        if ah == 0:
            return "DC_INITIAL"

        return "DC_REFINEMENT"

    # AC scan
    if ss > 0:

        if ah == 0:
            return "AC_INITIAL"

        return "AC_REFINEMENT"

    return "UNKNOWN"


def extract_progressive_constraints(blocks):
    """
    Analyze all blocks and extract progressive JPEG
    scan information.

    This function does NOT use ground-truth metadata.
    """

    results = {}

    for block_id, data in blocks.items():

        features = analyze_fragment(
            data,
            block_id
        )

        scans = []

        for scan in features["scans"]:

            scan_info = scan_signature(
                scan
            )

            scan_info["type"] = classify_scan(
                scan
            )

            scans.append(scan_info)

        results[block_id] = {
            "block_id": block_id,
            "role": features["role"],
            "markers": features["markers"],
            "scan_count": len(scans),
            "scans": scans,
            "has_soi": features["has_soi"],
            "has_eoi": features["has_eoi"],
        }

    return results


def scan_transition_score(left_scan, right_scan):
    """
    Estimate whether two progressive JPEG scans
    form a plausible progression.

    This is structural evidence, not byte similarity.
    """

    score = 0.0
    reasons = []

    left_type = left_scan["type"]
    right_type = right_scan["type"]

    # --------------------------------------------------------
    # DC progressive refinement
    # --------------------------------------------------------

    if (
        left_type == "DC_INITIAL"
        and right_type == "DC_REFINEMENT"
    ):

        if (
            right_scan["successive_high"]
            == left_scan["successive_low"]
        ):
            score += 5.0
            reasons.append(
                "DC refinement matches previous Al"
            )

    elif (
        left_type == "DC_REFINEMENT"
        and right_type == "DC_REFINEMENT"
    ):

        if (
            right_scan["successive_high"]
            == left_scan["successive_low"]
        ):
            score += 5.0
            reasons.append(
                "DC refinement levels continue"
            )

    # --------------------------------------------------------
    # AC progression
    # --------------------------------------------------------

    if (
        left_type == "AC_INITIAL"
        and right_type == "AC_REFINEMENT"
    ):

        if (
            left_scan["components"]
            == right_scan["components"]
        ):

            score += 4.0
            reasons.append(
                "AC refinement uses same component"
            )

        if (
            right_scan["successive_high"]
            == left_scan["successive_low"]
        ):

            score += 3.0
            reasons.append(
                "AC refinement level continues"
            )

    # --------------------------------------------------------
    # Same spectral band
    # --------------------------------------------------------

    if (
        left_scan["spectral_start"]
        == right_scan["spectral_start"]
        and
        left_scan["spectral_end"]
        == right_scan["spectral_end"]
    ):

        score += 1.0
        reasons.append(
            "same spectral band"
        )

    return {
        "score": score,
        "reasons": reasons,
    }


def compare_structural_blocks(
    left_features,
    right_features
):

    """
    Compare the last scan in the left block
    with the first scan in the right block.
    """

    if (
        not left_features["scans"]
        or not right_features["scans"]
    ):

        return {
            "score": 0.0,
            "reasons": [
                "one or both blocks contain no SOS scan"
            ],
        }

    left_scan = (
        left_features["scans"][-1]
    )

    right_scan = (
        right_features["scans"][0]
    )

    return scan_transition_score(
        left_scan,
        right_scan
    )