from pathlib import Path

from core.jpeg_analyzer import scan_jpeg_structure


STORAGE_PATH = Path(
    "samples/fragmented_storage.bin"
)

BLOCK_SIZE = 4096

GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18,
    11, 10, 27, 2, 9
]


SHORTCUT = [
    34, 3, 16, 32, 30, 8, 12, 28, 9
]


data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


def build_sequence(path):
    return b"".join(
        blocks[block_id]
        for block_id in path
    )


def analyze(path, name):

    sequence = build_sequence(path)

    markers = scan_jpeg_structure(
        sequence
    )

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    print(
        "Size:",
        len(sequence)
    )

    print()

    for index, marker in enumerate(
        markers
    ):

        print(
            f"{index:02d} | "
            f"offset={marker['offset']:6d} | "
            f"{marker['marker']} | "
            f"{marker['name']}"
        )

        if "segment_length" in marker:

            print(
                f"     segment_length="
                f"{marker['segment_length']}"
            )

            print(
                f"     crosses_boundary="
                f"{marker.get('crosses_block_boundary')}"
            )


analyze(
    GROUND_TRUTH,
    "FULL GROUND TRUTH"
)

analyze(
    SHORTCUT,
    "SHORTCUT"
)