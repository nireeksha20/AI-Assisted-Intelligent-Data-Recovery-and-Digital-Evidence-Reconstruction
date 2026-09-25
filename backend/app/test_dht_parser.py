from pathlib import Path

from core.fragment_association import split_into_blocks
from core.jpeg_stream_parser import parse_jpeg_stream
from core.jpeg_huffman import parse_dht_segment


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    # Evaluation-only sequence.
    sequence = [
        34, 24, 3, 16, 32, 7, 21, 30,
        8, 14, 5, 35, 33, 0, 19, 23,
        12, 13, 26, 22, 17, 28, 18, 11,
        10, 27, 2, 9
    ]

    reconstructed = b"".join(
        blocks[block_id]
        for block_id in sequence
    )

    markers = parse_jpeg_stream(reconstructed)

    print("=" * 90)
    print("JPEG HUFFMAN TABLE ANALYSIS")
    print("=" * 90)

    dht_count = 0

    for marker in markers:

        if marker["name"] != "DHT":
            continue

        start = marker["offset"]
        end = marker["end_offset"]

        segment = reconstructed[start:end]

        try:
            tables = parse_dht_segment(segment)

            print(
                f"\nDHT @ {start}"
                f" | length={marker['segment_length']}"
                f" | tables={len(tables)}"
            )

            for table in tables:
                print(
                    f"    class={table.table_class}"
                    f" id={table.table_id}"
                    f" codes={len(table.codes)}"
                )

            dht_count += len(tables)

        except Exception as exc:
            print(
                f"\nDHT @ {start}"
                f" | PARSE ERROR: {exc}"
            )

    print()
    print("=" * 90)
    print(f"TOTAL HUFFMAN TABLES: {dht_count}")
    print("=" * 90)


if __name__ == "__main__":
    main()