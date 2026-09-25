from pathlib import Path

from core.fragment_association import split_into_blocks
from core.jpeg_stream_parser import parse_jpeg_stream


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    # For this test ONLY, use the known evaluation sequence.
    # Do not put this sequence into the reconstruction algorithm.
    sequence = [
        34, 24, 3, 16, 32, 7, 21, 30,
        8, 14, 5, 35, 33, 0, 19, 23,
        12, 13, 26, 22, 17, 28, 18, 11,
        10, 27, 2, 9
    ]

    reconstructed = b"".join(blocks[i] for i in sequence)

    markers = parse_jpeg_stream(reconstructed)

    print("=" * 90)
    print("CROSS-BLOCK JPEG STREAM PARSER")
    print("=" * 90)

    for marker in markers:
        print(
            f"{marker['name']:<6} "
            f"offset={marker['offset']:<8} "
            f"length={marker['segment_length']}"
        )

    print()
    print(f"Total markers detected: {len(markers)}")


if __name__ == "__main__":
    main()