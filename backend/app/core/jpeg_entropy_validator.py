from .jpeg_analyzer import scan_jpeg_structure
from .jpeg_scan_parser import extract_scan_information


def validate_entropy_sequence(data: bytes):
    """
    Format-aware validation of a candidate JPEG fragment sequence.

    This is a structural validator, not a complete JPEG decoder.
    It checks whether the reconstructed byte stream has coherent
    JPEG markers and progressive scan structure.
    """

    if not data:
        return {
            "score": 0.0,
            "valid": False,
            "status": "empty",
            "reasons": [],
        }

    markers = scan_jpeg_structure(data)

    if not markers:
        return {
            "score": 0.0,
            "valid": False,
            "status": "no_jpeg_structure",
            "reasons": [],
        }

    score = 0.0
    reasons = []

    names = [marker["name"] for marker in markers]

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

    # ---------------------------------------------------------
    # 1. JPEG START
    # ---------------------------------------------------------

    if not data.startswith(b"\xFF\xD8\xFF"):
        return {
            "score": 0.0,
            "valid": False,
            "status": "invalid_start",
            "reasons": [
                "sequence does not start with JPEG SOI"
            ],
        }

    score += 20
    reasons.append("valid JPEG start")

    if len(soi_positions) == 1:
        score += 10
        reasons.append("single SOI")

    elif len(soi_positions) > 1:
        score -= 30
        reasons.append(
            f"multiple SOI markers: {len(soi_positions)}"
        )

    # ---------------------------------------------------------
    # 2. HEADER STRUCTURE
    # ---------------------------------------------------------

    if "DQT" in names:
        score += 10
        reasons.append("quantization table present")

    if any(name.startswith("SOF") for name in names):
        score += 15
        reasons.append("frame structure present")

    if "DHT" in names:
        score += 10
        reasons.append("Huffman table present")

    if "SOS" in names:
        score += 10
        reasons.append("scan structure present")

    # ---------------------------------------------------------
    # 3. PARSE SOS SCANS
    # ---------------------------------------------------------

    scans = extract_scan_information(data)

    valid_scans = [
        scan
        for scan in scans
        if scan.get("valid")
    ]

    invalid_scans = [
        scan
        for scan in scans
        if not scan.get("valid")
    ]

    if valid_scans:
        score += min(
            10.0,
            len(valid_scans) * 2.0
        )

        reasons.append(
            f"{len(valid_scans)} valid SOS scan(s)"
        )

    if invalid_scans:
        score -= min(
            10.0,
            len(invalid_scans) * 2.0
        )

        reasons.append(
            f"{len(invalid_scans)} invalid SOS scan(s)"
        )

    # ---------------------------------------------------------
    # 4. SOI / EOI
    # ---------------------------------------------------------

    if not eoi_positions:
        return {
            "score": round(
                max(score, 0.0),
                2
            ),
            "valid": False,
            "status": "missing_eoi",
            "marker_count": len(markers),
            "scan_count": len(valid_scans),
            "reasons": reasons + [
                "EOI missing"
            ],
        }

    if len(eoi_positions) == 1:
        score += 10
        reasons.append("single EOI")
    else:
        score -= 30
        reasons.append(
            f"multiple EOI markers: {len(eoi_positions)}"
        )

    # ---------------------------------------------------------
    # 5. MARKER ORDER
    # ---------------------------------------------------------

    if soi_positions[0] < eoi_positions[0]:
        score += 5
        reasons.append(
            "SOI occurs before EOI"
        )
    else:
        return {
            "score": 0.0,
            "valid": False,
            "status": "invalid_marker_order",
            "marker_count": len(markers),
            "scan_count": len(valid_scans),
            "reasons": reasons + [
                "EOI occurs before SOI"
            ],
        }

    # ---------------------------------------------------------
    # 6. EOI MUST BE AT THE END OF THE RECONSTRUCTED DATA
    # ---------------------------------------------------------

    eoi_position = eoi_positions[0]

    trailing = data[eoi_position + 2:]

    if trailing:

        if all(byte == 0 for byte in trailing):

            score += 5
            reasons.append(
                "zero padding follows EOI"
            )

        else:

            score -= 20
            reasons.append(
                "non-padding data follows EOI"
            )

    else:

        score += 5
        reasons.append(
            "EOI is at end of sequence"
        )

    score = max(
        0.0,
        min(score, 100.0)
    )

    return {
        "score": round(score, 2),
        "valid": score >= 70.0,
        "status": (
            "valid_candidate"
            if score >= 70.0
            else "structurally_incomplete"
        ),
        "marker_count": len(markers),
        "scan_count": len(valid_scans),
        "soi_position": soi_positions[0],
        "eoi_position": eoi_positions[0],
        "reasons": reasons,
    }