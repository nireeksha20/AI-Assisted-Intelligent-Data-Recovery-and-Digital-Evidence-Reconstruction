from .jpeg_analyzer import scan_jpeg_structure


def find_entropy_regions(data: bytes):
    """
    Identify approximate entropy-coded regions following SOS markers.

    This is deliberately conservative:
    it tracks FF byte-stuffing and restart markers so that
    FF bytes inside compressed JPEG data are not blindly treated
    as structural markers.
    """

    markers = scan_jpeg_structure(data)

    regions = []

    for index, marker in enumerate(markers):

        if marker["name"] != "SOS":
            continue

        sos_offset = marker["offset"]

        # SOS structure:
        # FF DA
        # length(2)
        # scan header...
        #
        # Entropy data begins after the complete SOS segment.

        if sos_offset + 4 > len(data):
            continue

        segment_length = int.from_bytes(
            data[sos_offset + 2:sos_offset + 4],
            byteorder="big"
        )

        entropy_start = sos_offset + 2 + segment_length

        if entropy_start >= len(data):
            continue

        entropy_end = len(data)

        i = entropy_start

        while i < len(data) - 1:

            if data[i] != 0xFF:
                i += 1
                continue

            next_byte = data[i + 1]

            # JPEG byte stuffing:
            # FF 00 represents a literal FF data byte.
            if next_byte == 0x00:
                i += 2
                continue

            # Restart markers belong to entropy-coded data.
            if 0xD0 <= next_byte <= 0xD7:
                i += 2
                continue

            # Any other FF xx is treated as the next marker.
            entropy_end = i
            break

            i += 1

        regions.append({
            "sos_offset": sos_offset,
            "entropy_start": entropy_start,
            "entropy_end": entropy_end,
            "entropy_size": max(0, entropy_end - entropy_start),
        })

    return regions