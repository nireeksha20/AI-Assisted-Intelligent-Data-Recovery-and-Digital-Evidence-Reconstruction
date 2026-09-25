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


def analyze_path(path, name):

    sequence = b"".join(
        blocks[block_id]
        for block_id in path
    )

    markers = scan_jpeg_structure(
        sequence
    )

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    print(
        "Path:",
        " → ".join(
            f"{block_id:02d}"
            for block_id in path
        )
    )

    print(
        "Sequence size:",
        len(sequence)
    )

    print()

    for marker in markers:

        offset = marker["offset"]

        block_position = offset // BLOCK_SIZE
        offset_inside_block = offset % BLOCK_SIZE

        print(
            f"{marker['name']:4s} | "
            f"absolute={offset:6d} | "
            f"path_position={block_position:2d} | "
            f"inside_block={offset_inside_block:4d}"
        )


analyze_path(
    GROUND_TRUTH,
    "GROUND TRUTH"
)

analyze_path(
    SHORTCUT,
    "SHORTCUT"
)