from typing import List, Dict


MARKER_NAMES = {
    0xC0: "SOF0",
    0xC1: "SOF1",
    0xC2: "SOF2",
    0xC4: "DHT",
    0xDB: "DQT",
    0xDA: "SOS",
    0xDD: "DRI",
    0xD8: "SOI",
    0xD9: "EOI",
    0xE0: "APP0",
    0xE1: "APP1",
    0xE2: "APP2",
    0xFE: "COM",
}


NO_LENGTH_MARKERS = {
    0xD8,  # SOI
    0xD9,  # EOI
}


def parse_jpeg_stream(data: bytes) -> List[Dict]:
    """
    Context-aware JPEG marker parser.

    Important:
    After SOS, bytes are entropy-coded data.
    FF00 is byte stuffing and must not be treated as a marker.
    """

    markers = []

    i = 0
    length = len(data)

    in_entropy = False

    while i < length - 1:

        # Outside entropy data, look for FF marker introducer.
        if not in_entropy:

            if data[i] != 0xFF:
                i += 1
                continue

            j = i + 1

            while j < length and data[j] == 0xFF:
                j += 1

            if j >= length:
                break

            marker = data[j]

            if marker == 0x00:
                i = j + 1
                continue

            name = MARKER_NAMES.get(marker)

            if name is None:
                i = j + 1
                continue

            offset = i

            if marker in NO_LENGTH_MARKERS:

                markers.append({
                    "name": name,
                    "offset": offset,
                    "marker": marker,
                    "segment_length": None,
                })

                i = j + 1

                if marker == 0xD9:
                    break

                continue

            if j + 2 >= length:
                break

            segment_length = int.from_bytes(
                data[j + 1:j + 3],
                "big"
            )

            end = j + 1 + segment_length

            if end > length:
                break

            markers.append({
                "name": name,
                "offset": offset,
                "marker": marker,
                "segment_length": segment_length,
                "end_offset": end,
            })

            i = end

            # SOS begins entropy-coded data.
            if marker == 0xDA:
                in_entropy = True

            continue

        # ---------------------------------------------------------
        # ENTROPY-CODED MODE
        # ---------------------------------------------------------

        if data[i] != 0xFF:
            i += 1
            continue

        j = i + 1

        # JPEG permits repeated FF fill bytes.
        while j < length and data[j] == 0xFF:
            j += 1

        if j >= length:
            break

        marker = data[j]

        # FF00 = literal FF byte in entropy data.
        if marker == 0x00:
            i = j + 1
            continue

        # Restart markers remain inside entropy data.
        if 0xD0 <= marker <= 0xD7:

            markers.append({
                "name": f"RST{marker - 0xD0}",
                "offset": i,
                "marker": marker,
                "segment_length": None,
            })

            i = j + 1
            continue

        # Any other marker terminates the entropy-coded segment.
        name = MARKER_NAMES.get(marker)

        if name is None:
            i = j + 1
            continue

        offset = i

        if marker in NO_LENGTH_MARKERS:

            markers.append({
                "name": name,
                "offset": offset,
                "marker": marker,
                "segment_length": None,
            })

            i = j + 1

            if marker == 0xD9:
                break

            # EOI ends everything.
            in_entropy = False
            continue

        if j + 2 >= length:
            break

        segment_length = int.from_bytes(
            data[j + 1:j + 3],
            "big"
        )

        end = j + 1 + segment_length

        if end > length:
            break

        markers.append({
            "name": name,
            "offset": offset,
            "marker": marker,
            "segment_length": segment_length,
            "end_offset": end,
        })

        i = end

        # After the next SOS, entropy mode starts again.
        if marker == 0xDA:
            in_entropy = True
        else:
            in_entropy = False

    return markers