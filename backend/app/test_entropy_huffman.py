from pathlib import Path

from core.jpeg_huffman import (
    BitReader,
    decode_huffman_symbol,
    parse_dht_segment,
)
from core.jpeg_stream_parser import parse_jpeg_stream


STORAGE_PATH = Path("samples/fragmented_storage.bin")

BLOCK_SIZE = 4096

GROUND_TRUTH_SEQUENCE = [
    34, 24, 3, 16, 32, 7, 21, 30, 8, 14,
    5, 35, 33, 0, 19, 23, 12, 13, 26, 22,
    17, 28, 18, 11, 10, 27, 2, 9,
]


def build_reconstructed_bytes(sequence):
    storage = STORAGE_PATH.read_bytes()

    return b"".join(
        storage[block_id * BLOCK_SIZE:(block_id + 1) * BLOCK_SIZE]
        for block_id in sequence
    )


def extract_dht_segments(data):
    """
    Extract actual FF C4 DHT segments from the reconstructed JPEG.
    """
    segments = []

    i = 0

    while i < len(data) - 3:

        if data[i:i + 2] != b"\xFF\xC4":
            i += 1
            continue

        length = int.from_bytes(
            data[i + 2:i + 4],
            "big"
        )

        end = i + 2 + length

        if end > len(data):
            break

        segments.append(data[i:end])

        i = end

    return segments

def extract_entropy_until_marker(data, start):
    """
    Extract entropy bytes starting at `start` until the next
    non-stuffed JPEG marker.

    Returns:
        entropy_bytes,
        marker_bytes,
        marker_offset
    """

    i = start

    while i < len(data) - 1:

        if data[i] != 0xFF:
            i += 1
            continue

        next_byte = data[i + 1]

        # Byte stuffing: FF 00 is entropy data.
        if next_byte == 0x00:
            i += 2
            continue

        # Restart markers remain inside entropy-coded data.
        if 0xD0 <= next_byte <= 0xD7:
            i += 2
            continue

        # Any other FF xx terminates the entropy region.
        return (
            data[start:i],
            data[i:i + 2],
            i,
        )

    return (
        data[start:],
        None,
        len(data),
    )


def main():

    print("\n=== HUFFMAN ENTROPY EXPERIMENT ===\n")

    data = build_reconstructed_bytes(
        GROUND_TRUTH_SEQUENCE
    )

    print("Reconstructed size:", len(data))

    # ---------------------------------------------------------
    # Parse JPEG markers
    # ---------------------------------------------------------

    markers = parse_jpeg_stream(data)

    print("Markers:", len(markers))

    # ---------------------------------------------------------
    # Parse DHT tables
    # ---------------------------------------------------------

    dht_segments = extract_dht_segments(data)

    print("DHT segments:", len(dht_segments))

    all_tables = []

    for index, segment in enumerate(dht_segments, start=1):

        try:
            tables = parse_dht_segment(segment)

            print(
                f"DHT {index}: "
                f"length={len(segment)}, "
                f"tables={len(tables)}"
            )

            all_tables.extend(tables)

        except Exception as exc:

            print(
                f"DHT {index}: ERROR - {exc}"
            )

    print(
        "Total Huffman tables:",
        len(all_tables)
    )

    for table in all_tables:

        table_type = (
            "DC"
            if table.table_class == 0
            else "AC"
        )

        print(
            f"  {table_type}{table.table_id}: "
            f"{len(table.codes)} codes"
        )

    # ---------------------------------------------------------
    # Basic entropy experiment
    # ---------------------------------------------------------

    print("\n=== BITSTREAM EXPERIMENT ===")

    # Use the first SOS as the beginning of an entropy stream.

    sos = next(
        (
            marker
            for marker in markers
            if marker["name"] == "SOS"
        ),
        None
    )

    if sos is None:

        print("No SOS found.")

        return

    sos_offset = sos["offset"]

    segment_length = int.from_bytes(
        data[sos_offset + 2:sos_offset + 4],
        "big"
    )

    entropy_start = (
        sos_offset + 2 + segment_length
    )

    print(
        "First SOS:",
        sos_offset
    )

    print(
        "Entropy start:",
        entropy_start
    )

    # Take a limited prefix so this experiment does not
    # attempt to fully decode the progressive JPEG.

    entropy_data = data[
        entropy_start:
        min(entropy_start + 512, len(data))
    ]

    print(
        "Entropy bytes tested:",
        len(entropy_data)
    )

    # Find a DC Huffman table.

    dc_tables = [
        table
        for table in all_tables
        if table.table_class == 0
    ]

    if not dc_tables:

        print("No DC Huffman table found.")

        return

    table = dc_tables[0]

    reader = BitReader(entropy_data)

    decoded = 0

    errors = 0

    for _ in range(100):

        try:

            symbol = decode_huffman_symbol(
                reader,
                table
            )

            decoded += 1

        except EOFError as exc:

            print(
                "Entropy boundary reached:",
                exc
            )

            break

        except ValueError as exc:

            errors += 1

            print(
                "Huffman decode error:",
                exc
            )

            break

    print("\n=== RESULT ===")

    print(
        "Symbols decoded:",
        decoded
    )

    print(
        "Errors:",
        errors
    )

        # ---------------------------------------------------------
    # CROSS-BLOCK ENTROPY EXPERIMENT
    # ---------------------------------------------------------

    print("\n=== CROSS-BLOCK ENTROPY EXPERIMENT ===")

    prefix_sequence = [34, 24, 3]

    prefix_data = build_reconstructed_bytes(
        prefix_sequence
    )

    prefix_markers = parse_jpeg_stream(
        prefix_data
    )

    first_sos = next(
        marker
        for marker in prefix_markers
        if marker["name"] == "SOS"
    )

    first_sos_offset = first_sos["offset"]

    first_sos_length = int.from_bytes(
        prefix_data[
            first_sos_offset + 2:
            first_sos_offset + 4
        ],
        "big"
    )

    first_entropy_start = (
        first_sos_offset
        + 2
        + first_sos_length
    )

    entropy_data, terminating_marker, marker_offset = (
        extract_entropy_until_marker(
            prefix_data,
            first_entropy_start
        )
    )

    print(
        "Prefix:",
        " → ".join(map(str, prefix_sequence))
    )

    print(
        "Entropy start:",
        first_entropy_start
    )

    print(
        "Entropy length:",
        len(entropy_data)
    )

    print(
        "Terminating marker:",
        terminating_marker.hex()
        if terminating_marker
        else None
    )

    print(
        "Marker offset:",
        marker_offset
    )

    reader = BitReader(entropy_data)

    decoded = 0

    decode_errors = 0

    while True:

        try:

            decode_huffman_symbol(
                reader,
                table
            )

            decoded += 1

        except EOFError as exc:

            print(
                "Reader stopped:",
                exc
            )

            break

        except ValueError as exc:

            decode_errors += 1

            print(
                "Huffman error:",
                exc
            )

            break

    print(
        "Symbols decoded:",
        decoded
    )

    print(
        "Decode errors:",
        decode_errors
    )


if __name__ == "__main__":
    main()