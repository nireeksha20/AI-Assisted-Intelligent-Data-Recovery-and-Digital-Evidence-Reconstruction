def scan_compatibility(left, right):
    """
    Compare progressive JPEG scan parameters.

    Returns a score in [-1, 1].
    """

    if not left["scans"] or not right["scans"]:
        return 0.0

    left_scan = left["scans"][-1]
    right_scan = right["scans"][0]

    score = 0.0

    # Same component count is useful evidence.
    if (
        left_scan["component_count"]
        == right_scan["component_count"]
    ):
        score += 0.15

    # Progressive DC refinement:
    #
    # Previous:
    # Ah -> Al
    #
    # Next refinement should normally begin
    # from the previous Al value.
    if (
        left_scan["spectral_start"] == 0
        and right_scan["spectral_start"] == 0
    ):

        if (
            right_scan["successive_high"]
            == left_scan["successive_low"]
        ):
            score += 0.60

        elif (
            right_scan["successive_high"]
            < left_scan["successive_low"]
        ):
            score += 0.20

    # Same AC spectral band is evidence that
    # the scans belong to the same progressive region.
    if (
        left_scan["spectral_start"]
        == right_scan["spectral_start"]
        and
        left_scan["spectral_end"]
        == right_scan["spectral_end"]
    ):
        score += 0.15

    # Component continuity.
    left_components = {
        component["component_id"]
        for component in left_scan["components"]
    }

    right_components = {
        component["component_id"]
        for component in right_scan["components"]
    }

    if left_components & right_components:
        score += 0.10

    return max(-1.0, min(score, 1.0))


def role_compatibility(left_role, right_role):

    table = {
        "START": {
            "DATA": 4.0,
            "SCAN_TRANSITION": 1.0,
            "END_CANDIDATE": -8.0,
            "SUSPICIOUS": -10.0,
            "STRUCTURAL": -2.0,
        },

        "DATA": {
            "DATA": 3.0,
            "SCAN_TRANSITION": 3.0,
            "END_CANDIDATE": 4.0,
            "SUSPICIOUS": -8.0,
            "STRUCTURAL": -1.0,
        },

        "SCAN_TRANSITION": {
            "DATA": 3.0,
            "SCAN_TRANSITION": 2.0,
            "END_CANDIDATE": 3.0,
            "SUSPICIOUS": -8.0,
            "STRUCTURAL": -1.0,
        },

        "STRUCTURAL": {
            "DATA": 1.0,
            "SCAN_TRANSITION": 1.0,
            "END_CANDIDATE": -2.0,
            "SUSPICIOUS": -8.0,
            "STRUCTURAL": 0.0,
        },

        "END_CANDIDATE": {
            "DATA": -20.0,
            "SCAN_TRANSITION": -20.0,
            "END_CANDIDATE": -20.0,
            "SUSPICIOUS": -20.0,
            "STRUCTURAL": -20.0,
        },

        "SUSPICIOUS": {
            "DATA": -8.0,
            "SCAN_TRANSITION": -8.0,
            "END_CANDIDATE": -8.0,
            "SUSPICIOUS": -10.0,
            "STRUCTURAL": -8.0,
        },
    }

    return table.get(
        left_role,
        {}
    ).get(
        right_role,
        0.0
    )


def transition_score(left, right):

    score = 0.0
    reasons = []

    # --------------------------------------------------
    # 1. Role compatibility
    # --------------------------------------------------

    role_score = role_compatibility(
        left["role"],
        right["role"]
    )

    score += role_score

    if role_score > 0:
        reasons.append(
            f"{left['role']} → {right['role']} is structurally plausible"
        )

    elif role_score < 0:
        reasons.append(
            f"{left['role']} → {right['role']} is suspicious"
        )

    # --------------------------------------------------
    # 2. Scan compatibility
    # --------------------------------------------------

    scan_score = scan_compatibility(
        left,
        right
    )

    score += scan_score * 8.0

    if scan_score > 0:
        reasons.append(
            "progressive JPEG scan parameters are compatible"
        )

    # --------------------------------------------------
    # 3. Structural contradictions
    # --------------------------------------------------

    if right["has_soi"]:
        score -= 10.0
        reasons.append(
            "candidate contains another SOI"
        )

    if (
        right["has_eoi"]
        and right["role"] != "END_CANDIDATE"
    ):
        score -= 5.0

    # --------------------------------------------------
    # 4. Suspicious block penalty
    # --------------------------------------------------

    if right["role"] == "SUSPICIOUS":
        score -= 15.0
        reasons.append(
            "candidate has contradictory JPEG markers"
        )

    # --------------------------------------------------
    # 5. Entropy evidence
    # --------------------------------------------------

    # FF00 is supporting evidence only.
    if (
        left["ff00_count"] > 0
        and right["ff00_count"] > 0
    ):
        score += 0.5
        reasons.append(
            "both fragments contain JPEG byte-stuffing evidence"
        )

    return {
        "score": round(score, 4),
        "role_score": round(role_score, 4),
        "scan_score": round(scan_score, 4),
        "reasons": reasons,
    }