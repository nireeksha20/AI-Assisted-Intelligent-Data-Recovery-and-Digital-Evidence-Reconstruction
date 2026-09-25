from pathlib import Path

from core.jpeg_analyzer import analyze_jpeg_block


storage_path = Path(
    "samples/fragmented_storage.bin"
)

data = storage_path.read_bytes()

block_size = 4096


print("\nJPEG structural analysis:\n")


for block_id, offset in enumerate(
    range(0, len(data), block_size)
):

    block = data[
        offset:offset + block_size
    ]

    result = analyze_jpeg_block(block)

    if result["marker_count"] > 0:

        print(
            f"\nBlock {block_id}"
        )

        print(
            "Marker count:",
            result["marker_count"]
        )

        print(
            "SOI:",
            result["has_soi"]
        )

        print(
            "SOS:",
            result["has_sos"]
        )

        print(
            "DQT:",
            result["has_dqt"]
        )

        print(
            "DHT:",
            result["has_dht"]
        )

        print(
            "EOI:",
            result["has_eoi"]
        )

        print(
            "Markers:",
            result["markers"]
        )