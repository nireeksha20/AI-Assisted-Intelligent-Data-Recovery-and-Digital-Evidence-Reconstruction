from .jpeg_scan_parser import extract_scan_information


def classify_scan(scan):
    ss = scan["spectral_start"]
    se = scan["spectral_end"]
    ah = scan["successive_high"]

    if ss == 0 and se == 0:
        if ah == 0:
            return "DC_INITIAL"
        return "DC_REFINEMENT"

    if ss > 0:
        if ah == 0:
            return "AC_INITIAL"
        return "AC_REFINEMENT"

    return "UNKNOWN"


def scan_transition_score(left_scan, right_scan):
    left_type = classify_scan(left_scan)
    right_type = classify_scan(right_scan)

    score = 0.0
    reasons = []

    # DC initial → DC refinement
    if left_type == "DC_INITIAL" and right_type == "DC_REFINEMENT":
        if left_scan["successive_low"] == right_scan["successive_high"]:
            score += 10.0
            reasons.append(
                "DC refinement successive approximation matches previous DC scan"
            )

    # DC refinement → DC refinement
    if left_type == "DC_REFINEMENT" and right_type == "DC_REFINEMENT":
        if left_scan["successive_low"] == right_scan["successive_high"]:
            score += 10.0
            reasons.append(
                "DC refinement levels continue correctly"
            )

    # AC initial → AC refinement
    if left_type == "AC_INITIAL" and right_type == "AC_REFINEMENT":
        if left_scan["components"] == right_scan["components"]:
            score += 8.0
            reasons.append(
                "AC refinement targets the same component"
            )

        if left_scan["successive_low"] == right_scan["successive_high"]:
            score += 10.0
            reasons.append(
                "AC refinement successive approximation matches previous AC scan"
            )

        if (
            left_scan["spectral_start"]
            == right_scan["spectral_start"]
            and
            left_scan["spectral_end"]
            == right_scan["spectral_end"]
        ):
            score += 5.0
            reasons.append(
                "AC refinement covers the same spectral band"
            )

    # AC refinement → AC refinement
    if left_type == "AC_REFINEMENT" and right_type == "AC_REFINEMENT":
        if left_scan["components"] == right_scan["components"]:
            score += 8.0
            reasons.append(
                "AC refinement continues on the same component"
            )

        if left_scan["successive_low"] == right_scan["successive_high"]:
            score += 10.0
            reasons.append(
                "AC refinement levels continue correctly"
            )

    return {
        "left_type": left_type,
        "right_type": right_type,
        "score": score,
        "reasons": reasons,
    }