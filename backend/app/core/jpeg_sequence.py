from .jpeg_analyzer import scan_jpeg_structure


def validate_jpeg_sequence(data: bytes):
    """
    Strict whole-sequence JPEG validation.

    A sequence is considered valid only if:
    - it starts with JPEG SOI
    - it contains a valid JPEG structure
    - it contains EOI
    - EOI occurs in the final block
    - only zero padding follows EOI
    """

    if not data:
        return {
            "score": 0.0,
            "status": "empty",
            "valid": False,
            "marker_count": 0,
            "reasons": [],
        }

    markers = scan_jpeg_structure(data)

    if not markers:
        return {
            "score": 0.0,
            "status": "no_jpeg_structure",
            "valid": False,
            "marker_count": 0,
            "reasons": [],
        }

    reasons = []
    score = 0.0

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

    has_soi = bool(soi_positions)
    has_eoi = bool(eoi_positions)

    # --------------------------------------------------
    # 1. Sequence must start with JPEG SOI
    # --------------------------------------------------

    if not data.startswith(b"\xFF\xD8\xFF"):
        return {
            "score": 0.0,
            "status": "invalid_start",
            "valid": False,
            "marker_count": len(markers),
            "reasons": [
                "sequence does not start with JPEG SOI"
            ],
        }

    score += 30
    reasons.append("valid JPEG start")

    # --------------------------------------------------
    # 2. SOI
    # --------------------------------------------------

    if len(soi_positions) == 1:
        score += 10
        reasons.append("single SOI")

    elif len(soi_positions) > 1:
        score -= 40
        reasons.append(
            f"multiple SOI markers found: {len(soi_positions)}"
        )

    # --------------------------------------------------
    # 3. JPEG structural markers
    # --------------------------------------------------

    if any(name.startswith("SOF") for name in names):
        score += 15
        reasons.append("frame structure present")

    if "DQT" in names:
        score += 10
        reasons.append("quantization table present")

    if "DHT" in names:
        score += 10
        reasons.append("Huffman table present")

    if "SOS" in names:
        score += 10
        reasons.append("scan structure present")

    # --------------------------------------------------
    # 4. EOI must exist
    # --------------------------------------------------

    if not has_eoi:
        return {
            "score": round(max(score, 0.0), 2),
            "status": "missing_eoi",
            "valid": False,
            "marker_count": len(markers),
            "reasons": reasons + [
                "EOI missing"
            ],
        }

    # --------------------------------------------------
    # 5. Exactly one EOI
    # --------------------------------------------------

    if len(eoi_positions) == 1:
        score += 10
        reasons.append("single EOI")
    else:
        score -= 40
        reasons.append(
            f"multiple EOI markers found: {len(eoi_positions)}"
        )

    # --------------------------------------------------
    # 6. EOI must occur after SOI
    # --------------------------------------------------

    first_soi = soi_positions[0]
    first_eoi = eoi_positions[0]

    if first_eoi <= first_soi:
        return {
            "score": 0.0,
            "status": "invalid_marker_order",
            "valid": False,
            "marker_count": len(markers),
            "reasons": reasons + [
                "EOI occurs before SOI"
            ],
        }

    score += 5
    reasons.append("SOI occurs before EOI")

    # --------------------------------------------------
    # 7. EOI must be in the final storage block
    #
    # Our simulator uses 4096-byte blocks.
    # --------------------------------------------------

    BLOCK_SIZE = 4096

    eoi_block = first_eoi // BLOCK_SIZE
    final_block = (len(data) - 1) // BLOCK_SIZE

    if eoi_block != final_block:
        return {
            "score": 0.0,
            "status": "early_eoi",
            "valid": False,
            "marker_count": len(markers),
            "eoi_block": eoi_block,
            "final_block": final_block,
            "reasons": reasons + [
                f"EOI occurs in block {eoi_block}, "
                f"but sequence continues through block {final_block}"
            ],
        }

    score += 15
    reasons.append("EOI occurs in final block")

    # --------------------------------------------------
    # 8. Only zero padding may follow EOI
    # --------------------------------------------------

    eoi_marker_end = first_eoi + 2
    trailing_data = data[eoi_marker_end:]

    if trailing_data:

        if all(byte == 0 for byte in trailing_data):
            score += 10
            reasons.append("only zero padding follows EOI")

        else:
            return {
                "score": 0.0,
                "status": "data_after_eoi",
                "valid": False,
                "marker_count": len(markers),
                "eoi_block": eoi_block,
                "final_block": final_block,
                "reasons": reasons + [
                    "non-padding data follows EOI"
                ],
            }

    # --------------------------------------------------
    # 9. Final result
    # --------------------------------------------------

    score = max(0.0, min(score, 100.0))

    return {
        "score": round(score, 2),
        "status": "valid_candidate",
        "valid": True,
        "marker_count": len(markers),
        "soi_position": first_soi,
        "eoi_position": first_eoi,
        "eoi_block": eoi_block,
        "final_block": final_block,
        "reasons": reasons,
    }