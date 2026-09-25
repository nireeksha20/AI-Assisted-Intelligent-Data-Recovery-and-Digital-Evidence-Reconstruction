from .jpeg_anchors import extract_jpeg_anchors


def classify_scan(scan):
    ss = scan["spectral_start"]
    se = scan["spectral_end"]
    ah = scan["successive_high"]
    al = scan["successive_low"]

    if ss == 0 and se == 0:
        if ah == 0:
            return "DC_INITIAL"
        return "DC_REFINEMENT"

    if ss > 0:
        if ah == 0:
            return "AC_INITIAL"
        return "AC_REFINEMENT"

    return "UNKNOWN"


def progressive_compatibility(left_scan, right_scan):
    score = 0.0
    reasons = []

    left_type = classify_scan(left_scan)
    right_type = classify_scan(right_scan)

    left_components = tuple(
        component["component_id"]
        for component in left_scan["components"]
    )

    right_components = tuple(
        component["component_id"]
        for component in right_scan["components"]
    )

    # ---------------------------------------------------------
    # 1. DC INITIAL → DC REFINEMENT
    # ---------------------------------------------------------
    if (
        left_type == "DC_INITIAL"
        and right_type == "DC_REFINEMENT"
        and left_scan["successive_low"] == right_scan["successive_high"]
    ):
        score += 5.0
        reasons.append("valid DC initial → refinement")

    # ---------------------------------------------------------
    # 2. DC REFINEMENT → DC REFINEMENT
    # ---------------------------------------------------------
    if (
        left_type == "DC_REFINEMENT"
        and right_type == "DC_REFINEMENT"
        and left_scan["successive_low"] == right_scan["successive_high"]
    ):
        score += 5.0
        reasons.append("valid DC refinement continuation")

    # ---------------------------------------------------------
    # 3. AC INITIAL → AC REFINEMENT
    # ---------------------------------------------------------
    if (
        left_type == "AC_INITIAL"
        and right_type == "AC_REFINEMENT"
    ):
        if left_components == right_components:
            score += 4.0
            reasons.append("same AC component")

        if (
            left_scan["successive_low"]
            == right_scan["successive_high"]
        ):
            score += 3.0
            reasons.append("valid AC refinement level")

    # ---------------------------------------------------------
    # 4. AC REFINEMENT → AC REFINEMENT
    # ---------------------------------------------------------
    if (
        left_type == "AC_REFINEMENT"
        and right_type == "AC_REFINEMENT"
    ):
        if left_components == right_components:
            score += 4.0
            reasons.append("same AC component")

        if (
            left_scan["successive_low"]
            == right_scan["successive_high"]
        ):
            score += 3.0
            reasons.append("valid AC refinement continuation")

    # ---------------------------------------------------------
    # 5. AC INITIAL → AC INITIAL
    #
    # Progressive JPEGs can encode different components
    # using separate initial AC scans over the same band.
    # ---------------------------------------------------------
    if (
        left_type == "AC_INITIAL"
        and right_type == "AC_INITIAL"
    ):
        if (
            left_scan["spectral_start"]
            == right_scan["spectral_start"]
            and
            left_scan["spectral_end"]
            == right_scan["spectral_end"]
        ):
            score += 3.0
            reasons.append(
                "compatible AC initial scans over same spectral band"
            )

        if left_components != right_components:
            score += 1.0
            reasons.append(
                "different AC components"
            )

    # ---------------------------------------------------------
    # 6. Same spectral band
    # ---------------------------------------------------------
    if (
        left_scan["spectral_start"]
        == right_scan["spectral_start"]
        and
        left_scan["spectral_end"]
        == right_scan["spectral_end"]
    ):
        score += 1.0
        reasons.append("same spectral band")

    # ---------------------------------------------------------
    # 7. Same component set
    # ---------------------------------------------------------
    if left_components == right_components:
        score += 1.0
        reasons.append("same components")

    return score, reasons


def build_anchor_graph(blocks):

    anchors = extract_jpeg_anchors(blocks)

    structural_ids = [
        block_id
        for block_id, anchor in anchors.items()
        if (
            anchor["has_soi"]
            or anchor["has_eoi"]
            or anchor["has_sos"]
            or anchor["markers"]
        )
    ]

    graph = {}

    for left_id in structural_ids:

        graph[left_id] = []

        left_scans = anchors[left_id]["scans"]

        for right_id in structural_ids:

            if left_id == right_id:
                continue

            right_scans = anchors[right_id]["scans"]

            if not left_scans or not right_scans:
                continue

            score, reasons = progressive_compatibility(
                left_scans[-1],
                right_scans[0],
            )

            graph[left_id].append({
                "to": right_id,
                "score": score,
                "reasons": reasons,
            })

        graph[left_id].sort(
            key=lambda item: item["score"],
            reverse=True,
        )

    return graph