from .jpeg_block_likelihood import jpeg_entropy_likelihood
from .jpeg_analyzer import scan_jpeg_structure


def classify_fragment_membership(data: bytes):
    """
    Classify a storage block as:
    - structural_jpeg
    - jpeg_entropy
    - noise_candidate
    - uncertain
    """

    likelihood = jpeg_entropy_likelihood(data)

    ff00 = likelihood["ff00_count"]
    invalid_ff = likelihood["invalid_ff_count"]
    jpeg_score = likelihood["jpeg_likelihood"]

    markers = scan_jpeg_structure(data)
    marker_names = [marker["name"] for marker in markers]

    has_soi = "SOI" in marker_names
    has_eoi = "EOI" in marker_names
    has_sos = "SOS" in marker_names
    has_dht = "DHT" in marker_names
    has_dqt = "DQT" in marker_names
    has_sof = any(name.startswith("SOF") for name in marker_names)

    # ---------------------------------------------------------
    # 1. Strong JPEG scan/structure evidence
    # ---------------------------------------------------------

    # SOS is a very strong indicator that this block contains
    # an actual JPEG scan boundary rather than random bytes.
    if has_sos:

        if has_soi:
            role = "jpeg_start"
        else:
            role = "jpeg_structural"

        return {
            "membership": "jpeg",
            "role": role,
            "score": round(max(jpeg_score, 0.50), 4),
            "ff00_count": ff00,
            "invalid_ff_count": invalid_ff,
        }

    # ---------------------------------------------------------
    # 2. JPEG end block
    # ---------------------------------------------------------

    if has_eoi:
        eoi_positions = [
            marker["offset"]
            for marker in markers
            if marker["name"] == "EOI"
        ]

        # Treat EOI as a genuine terminal marker only when it
        # occurs near the end of the block or is followed mostly
        # by zero/padding bytes.
        valid_terminal_eoi = False

        if eoi_positions:
            eoi_offset = eoi_positions[-1]
            trailing = data[eoi_offset + 2:]

            if not trailing:
                valid_terminal_eoi = True
            else:
                zero_ratio = trailing.count(0) / len(trailing)

                # EOI followed mostly by padding is plausible.
                if zero_ratio >= 0.90:
                    valid_terminal_eoi = True

        if valid_terminal_eoi:
            return {
                "membership": "jpeg",
                "role": "jpeg_end",
                "score": round(max(jpeg_score, 0.50), 4),
                "ff00_count": ff00,
                "invalid_ff_count": invalid_ff,
            }

    # ---------------------------------------------------------
    # 3. JPEG entropy-stream evidence
    # ---------------------------------------------------------

    if ff00 > 0 and invalid_ff == 0:
        return {
            "membership": "jpeg",
            "role": "jpeg_entropy",
            "score": round(jpeg_score, 4),
            "ff00_count": ff00,
            "invalid_ff_count": invalid_ff,
        }

    # ---------------------------------------------------------
    # 4. Strong noise evidence
    # ---------------------------------------------------------

    if ff00 == 0 and invalid_ff >= 3:
        return {
            "membership": "noise_candidate",
            "role": "noise",
            "score": round(jpeg_score, 4),
            "ff00_count": ff00,
            "invalid_ff_count": invalid_ff,
        }

    # ---------------------------------------------------------
    # 5. Ambiguous
    # ---------------------------------------------------------

    return {
        "membership": "uncertain",
        "role": "unknown",
        "score": round(jpeg_score, 4),
        "ff00_count": ff00,
        "invalid_ff_count": invalid_ff,
    }