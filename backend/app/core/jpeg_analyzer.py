# backend/app/core/jpeg_analyzer.py


JPEG_MARKER_NAMES = {
    0xD8: "SOI",
    0xD9: "EOI",
    0xDA: "SOS",
    0xDB: "DQT",
    0xC0: "SOF0",
    0xC1: "SOF1",
    0xC2: "SOF2",
    0xC4: "DHT",
    0xE0: "APP0",
    0xE1: "APP1",
    0xE2: "APP2",
    0xFE: "COM",
}


# JPEG markers that contain a 2-byte length field.
LENGTH_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC4,
    0xDB,
    0xDA,
    0xE0,
    0xE1,
    0xE2,
    0xFE,
}


def scan_jpeg_structure(data: bytes):
    """
    Scan a byte sequence for plausible JPEG markers.
    """

    markers = []

    i = 0

    while i < len(data) - 1:

        # JPEG marker begins with FF.
        if data[i] != 0xFF:
            i += 1
            continue

        # Skip repeated FF fill bytes.
        j = i + 1

        while j < len(data) and data[j] == 0xFF:
            j += 1

        if j >= len(data):
            break

        marker_byte = data[j]

        # FF 00 is byte stuffing inside JPEG data.
        if marker_byte == 0x00:
            i = j + 1
            continue

        marker_name = JPEG_MARKER_NAMES.get(marker_byte)

        # Ignore unknown markers.
        if marker_name is None:
            i = j + 1
            continue

        marker_info = {
            "offset": i,
            "marker": f"FF{marker_byte:02X}",
            "name": marker_name,
        }

        # SOI and EOI have no length field.
        if marker_byte in (0xD8, 0xD9):

            markers.append(marker_info)

            i = j + 1

            continue

        # Markers containing a length field.
        if marker_byte in LENGTH_MARKERS:

            # Need two bytes for the length.
            if j + 2 >= len(data):
                break

            length = int.from_bytes(
                data[j + 1:j + 3],
                byteorder="big"
            )

            marker_info["segment_length"] = length

            # JPEG segment length must be >= 2.
            if length < 2:

                marker_info["valid_length"] = False

                markers.append(marker_info)

                i = j + 1

                continue

            marker_info["valid_length"] = True

            segment_end = j + 1 + length

            marker_info["crosses_block_boundary"] = segment_end > len(data)

            markers.append(marker_info)

            i = j + 1

            continue

        markers.append(marker_info)

        i = j + 1

    return markers


def calculate_structural_quality(markers, data_length):
    """
    Estimate how structurally plausible the JPEG evidence
    inside one storage block is.

    This is a forensic heuristic, not a complete JPEG validator.
    """

    if not markers:
        return 0.0

    score = 0.0
    maximum = 0.0

    has_soi = any(
        marker["name"] == "SOI"
        for marker in markers
    )

    has_eoi = any(
        marker["name"] == "EOI"
        for marker in markers
    )

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

    # --------------------------------------------------
    # 1. Segment validity
    # --------------------------------------------------

    for marker in markers:

        if marker["name"] in ("SOI", "EOI"):

            score += 1.0
            maximum += 1.0

        elif marker.get("valid_length"):
            maximum += 1.0
            score += 1.0

    # --------------------------------------------------
    # 2. SOI / EOI ordering
    # --------------------------------------------------

    if has_soi and has_eoi:

        maximum += 2.0

        if soi_positions[0] < eoi_positions[-1]:

            score += 2.0

        else:

            # Strong penalty for impossible ordering.
            score -= 2.0

    # --------------------------------------------------
    # 3. Genuine JPEG start
    # --------------------------------------------------

    if has_soi and soi_positions[0] == 0:

        maximum += 1.0
        score += 1.0

    # --------------------------------------------------
    # 4. Clamp and normalize
    # --------------------------------------------------

    if maximum <= 0:
        return 0.0

    normalized = score / maximum

    return round(
        max(0.0, min(normalized, 1.0)),
        4
    )


def analyze_jpeg_block(data: bytes):
    """
    Extract structural JPEG features from one storage block.
    """

    markers = scan_jpeg_structure(data)

    structural_quality = calculate_structural_quality(
    markers,
    len(data)
    )

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

    has_soi = len(soi_positions) > 0

    has_eoi = len(eoi_positions) > 0

    # A normal JPEG should encounter SOI before EOI.
    valid_soi_eoi_order = False

    if has_soi and has_eoi:

        valid_soi_eoi_order = (
            soi_positions[0] < eoi_positions[-1]
        )

    return {
    "size_bytes": len(data),

    "marker_count": len(markers),

    "markers": markers,

    "structural_quality": structural_quality,

    "has_soi": has_soi,

    "has_eoi": has_eoi,

    "has_sos": "SOS" in names,

    "has_dqt": "DQT" in names,

    "has_dht": "DHT" in names,

    "has_sof": any(
        name.startswith("SOF")
        for name in names
    ),

    "soi_positions": soi_positions,

    "eoi_positions": eoi_positions,

    "valid_soi_eoi_order": valid_soi_eoi_order,

    "starts_with_soi": (
        len(soi_positions) > 0
        and soi_positions[0] == 0
    ),

    "ends_with_eoi": (
        len(eoi_positions) > 0
        and eoi_positions[-1] >= len(data) - 2
    ),
}