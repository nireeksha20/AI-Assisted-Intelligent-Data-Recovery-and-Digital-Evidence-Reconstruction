from .jpeg_analyzer import scan_jpeg_structure


def analyze_fragment_state(data: bytes):

    markers = scan_jpeg_structure(data)

    names = [
        marker["name"]
        for marker in markers
    ]

    soi_positions = [
        marker["offset"]
        for marker in markers
        if marker["name"] == "SOI"
    ]

    eoi_positions = [
        marker["offset"]
        for marker in markers
        if marker["name"] == "EOI"
    ]

    has_soi = bool(soi_positions)
    has_eoi = bool(eoi_positions)

    valid_soi_eoi_order = True

    if has_soi and has_eoi:
        valid_soi_eoi_order = (
            soi_positions[0] < eoi_positions[0]
        )

    # --------------------------------------------------
    # Structural features
    # --------------------------------------------------

    has_sof = any(
        name.startswith("SOF")
        for name in names
    )

    has_dqt = "DQT" in names
    has_dht = "DHT" in names
    has_sos = "SOS" in names

    # --------------------------------------------------
    # Suspicion indicators
    # --------------------------------------------------

    suspicious = False
    suspicious_reasons = []

    if has_soi and has_eoi and not valid_soi_eoi_order:
        suspicious = True
        suspicious_reasons.append(
            "EOI occurs before SOI"
        )

    # SOI appearing away from the beginning of a
    # storage fragment is suspicious.
    if has_soi and soi_positions[0] != 0:
        suspicious = True
        suspicious_reasons.append(
            "SOI does not start fragment"
        )

    # EOI occurring far from the end is suspicious.
    if has_eoi:
        eoi_offset = eoi_positions[-1]

        if len(data) - eoi_offset > 32:
            suspicious_reasons.append(
                "EOI occurs well before fragment end"
            )

    # --------------------------------------------------
    # Role classification
    # --------------------------------------------------

    if (
        has_soi
        and soi_positions[0] == 0
        and not has_eoi
    ):
        role = "JPEG_START"

    elif (
        has_eoi
        and not has_soi
    ):
        role = "JPEG_END_CANDIDATE"

    elif (
        has_soi
        and has_eoi
        and not valid_soi_eoi_order
    ):
        role = "SUSPICIOUS_MARKER_BLOCK"

    elif has_dht and has_sos:
        role = "JPEG_SCAN_BOUNDARY"

    elif has_sof or has_dqt:
        role = "JPEG_HEADER_LIKE"

    else:
        role = "JPEG_DATA"

    return {
        "has_soi": has_soi,
        "has_eoi": has_eoi,
        "has_sof": has_sof,
        "has_dqt": has_dqt,
        "has_dht": has_dht,
        "has_sos": has_sos,

        "soi_positions": soi_positions,
        "eoi_positions": eoi_positions,

        "valid_soi_eoi_order": valid_soi_eoi_order,

        "marker_count": len(markers),
        "markers": names,

        "suspicious": suspicious,
        "suspicious_reasons": suspicious_reasons,

        "role": role,
    }