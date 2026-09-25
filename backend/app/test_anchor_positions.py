from pathlib import Path

from core.jpeg_anchor_positions import (
    get_anchor_positions,
    absolute_event_offset,
)


STORAGE_PATH = Path(
    "samples/fragmented_storage.bin"
)

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


anchors = get_anchor_positions(blocks)


print()
print("=" * 70)
print("JPEG ANCHOR POSITION MODEL")
print("=" * 70)

for block_id in sorted(anchors):

    anchor = anchors[block_id]

    print()
    print(
        f"BLOCK {block_id:02d}"
    )

    for event in anchor["events"]:

        print(
            f"  {event['marker']:4s} "
            f"inside_block="
            f"{event['offset_in_block']:4d}"
        )

        print(
            f"       "
            f"position 0 → "
            f"absolute="
            f"{absolute_event_offset(0, event['offset_in_block'])}"
        )

        print(
            f"       "
            f"position 1 → "
            f"absolute="
            f"{absolute_event_offset(1, event['offset_in_block'])}"
        )

        print(
            f"       "
            f"position 2 → "
            f"absolute="
            f"{absolute_event_offset(2, event['offset_in_block'])}"
        )