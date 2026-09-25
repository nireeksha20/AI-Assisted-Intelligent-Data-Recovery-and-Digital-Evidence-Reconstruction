from .jpeg_analyzer import scan_jpeg_structure
from .jpeg_scan_parser import extract_scan_information


def count_pattern(data: bytes, pattern: bytes) -> int:
    count = 0
    start = 0

    while True:
        position = data.find(pattern, start)

        if position == -1:
            break

        count += 1
        start = position + 1

    return count


def analyze_fragment(data: bytes, block_id: int):
    """
    Extract the JPEG-specific feature representation used by
    the JPEG role, transition, anchor and reconstruction engines.
    """

    markers = scan_jpeg_structure(data)

    marker_names = [
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

    scans = extract_scan_information(data)

    scan_parameters = []

    for scan in scans:
        if not scan.get("valid"):
            continue

        scan_parameters.append({
            "component_count": scan["component_count"],
            "components": scan["components"],
            "spectral_start": scan["spectral_start"],
            "spectral_end": scan["spectral_end"],
            "successive_high": scan["successive_high"],
            "successive_low": scan["successive_low"],
        })

    ff00_count = count_pattern(
        data,
        b"\xFF\x00"
    )

    restart_marker_count = sum(
        data.count(bytes([0xFF, marker]))
        for marker in range(0xD0, 0xD8)
    )

    starts_with_soi = data.startswith(
        b"\xFF\xD8\xFF"
    )

    starts_with_ff = data.startswith(
        b"\xFF"
    )

    ends_with_eoi = bool(
        eoi_positions
        and eoi_positions[-1] + 2 == len(data)
    )

    # Coarse JPEG role used by jpeg_transition.py.
    if (
        has_soi
        and soi_positions[0] == 0
        and not has_eoi
    ):
        role = "START"

    elif (
        has_soi
        and has_eoi
        and not valid_soi_eoi_order
    ):
        role = "SUSPICIOUS"

    elif has_eoi and not has_soi:
        role = "END_CANDIDATE"

    elif scans:
        role = "SCAN_TRANSITION"

    elif not marker_names:
        role = "DATA"

    else:
        role = "STRUCTURAL"

    return {
        "block_id": block_id,
        "size_bytes": len(data),

        "markers": marker_names,
        "marker_count": len(markers),

        "has_soi": has_soi,
        "has_eoi": has_eoi,

        "soi_positions": soi_positions,
        "eoi_positions": eoi_positions,

        "valid_soi_eoi_order": valid_soi_eoi_order,

        "ends_with_eoi": ends_with_eoi,

        "scan_count": len(scan_parameters),
        "scans": scan_parameters,

        "ff00_count": ff00_count,
        "restart_marker_count": restart_marker_count,

        "starts_with_soi": starts_with_soi,
        "starts_with_ff": starts_with_ff,

        "role": role,
    }