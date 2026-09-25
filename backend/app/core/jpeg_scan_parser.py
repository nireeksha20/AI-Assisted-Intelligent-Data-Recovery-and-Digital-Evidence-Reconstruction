from .jpeg_analyzer import scan_jpeg_structure


def parse_sos(data: bytes, marker):
    """
    Parse the SOS (Start of Scan) segment beginning at marker['offset'].

    JPEG layout:

        FF DA
        LL LL
        Ns
        Cs TdTa   <- one pair per component
        Ss
        Se
        AhAl
    """

    offset = marker["offset"]

    if offset + 4 > len(data):
        return None

    # Verify SOS marker.
    if data[offset] != 0xFF or data[offset + 1] != 0xDA:
        return None

    segment_length = int.from_bytes(
        data[offset + 2:offset + 4],
        byteorder="big"
    )

    segment_end = offset + 2 + segment_length

    if segment_end > len(data):
        return {
            "valid": False,
            "reason": "SOS segment crosses fragment boundary"
        }

    if segment_length < 2:
        return {
            "valid": False,
            "reason": "invalid SOS segment length"
        }

    ns_offset = offset + 4

    if ns_offset >= len(data):
        return None

    component_count = data[ns_offset]

    expected_length = 2 + 1 + (2 * component_count) + 3

    if segment_length != expected_length:
        return {
            "valid": False,
            "reason": "unexpected SOS segment length",
            "segment_length": segment_length,
            "expected_length": expected_length,
        }

    components = []

    cursor = ns_offset + 1

    for _ in range(component_count):
        component_id = data[cursor]
        table_selector = data[cursor + 1]

        dc_table = table_selector >> 4
        ac_table = table_selector & 0x0F

        components.append({
            "component_id": component_id,
            "dc_table": dc_table,
            "ac_table": ac_table,
        })

        cursor += 2

    spectral_start = data[cursor]
    spectral_end = data[cursor + 1]

    approximation = data[cursor + 2]

    ah = approximation >> 4
    al = approximation & 0x0F

    return {
        "valid": True,
        "offset": offset,
        "segment_length": segment_length,
        "component_count": component_count,
        "components": components,
        "spectral_start": spectral_start,
        "spectral_end": spectral_end,
        "successive_high": ah,
        "successive_low": al,
    }


def extract_scan_information(data: bytes):
    markers = scan_jpeg_structure(data)

    scans = []

    for marker in markers:
        if marker["name"] != "SOS":
            continue

        scan = parse_sos(data, marker)

        if scan is not None:
            scans.append(scan)

    return scans