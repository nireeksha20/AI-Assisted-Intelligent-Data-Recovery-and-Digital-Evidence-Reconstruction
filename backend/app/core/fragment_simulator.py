# backend/app/core/fragment_simulator.py

from pathlib import Path
import hashlib
import json
import random


def create_fragmented_storage(
    file_path: str,
    output_path: str = "samples/fragmented_storage.bin",
    metadata_path: str = "samples/fragment_metadata.json",
    fragment_size: int = 4096,
    noise_blocks: int = 8,
    seed: int = 42,
):
    """
    Create a controlled damaged-storage image.

    The original file is divided into fixed-size fragments.
    The fragments are shuffled and placed into fixed-size
    storage blocks together with unrelated noise blocks.

    Metadata is generated only as ground truth for evaluating
    reconstruction accuracy. The recovery algorithm must not
    depend on it.
    """

    source = Path(file_path)
    data = source.read_bytes()

    random.seed(seed)

    # ---------------------------------------------------------
    # 1. Split original file into fixed-size fragments
    # ---------------------------------------------------------

    fragments = [
        data[i:i + fragment_size]
        for i in range(0, len(data), fragment_size)
    ]

    fragment_records = []

    for fragment_id, fragment in enumerate(fragments):

        fragment_records.append({
            "fragment_id": fragment_id,
            "original_order": fragment_id,
            "size_bytes": len(fragment),
            "sha256": hashlib.sha256(fragment).hexdigest(),
        })

    # ---------------------------------------------------------
    # 2. Create unrelated noise blocks
    # ---------------------------------------------------------

    noise = []

    for noise_id in range(noise_blocks):

        noise_data = bytes(
            random.randint(0, 255)
            for _ in range(fragment_size)
        )

        noise.append({
            "block_type": "noise",
            "noise_id": noise_id,
            "data": noise_data,
        })

    # ---------------------------------------------------------
    # 3. Convert fragments into storage blocks
    # ---------------------------------------------------------

    storage_blocks = []

    for fragment_id, fragment in enumerate(fragments):

        # Every fragment occupies exactly one storage block.
        block = fragment.ljust(
            fragment_size,
            b"\x00"
        )

        storage_blocks.append({
            "block_type": "fragment",
            "fragment_id": fragment_id,
            "data": block,
        })

    # Add unrelated blocks.
    storage_blocks.extend(noise)

    # ---------------------------------------------------------
    # 4. Shuffle everything
    # ---------------------------------------------------------

    random.shuffle(storage_blocks)

    # ---------------------------------------------------------
    # 5. Write storage image
    # ---------------------------------------------------------

    storage = bytearray()

    block_records = []

    for storage_block_id, block in enumerate(storage_blocks):

        storage.extend(block["data"])

        block_records.append({
            "storage_block_id": storage_block_id,
            "block_type": block["block_type"],
            "fragment_id": block.get("fragment_id"),
            "offset": storage_block_id * fragment_size,
            "size_bytes": fragment_size,
        })

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(storage)

    # ---------------------------------------------------------
    # 6. Save ground-truth metadata
    # ---------------------------------------------------------

    metadata = {
        "original_file": str(source),
        "original_size_bytes": len(data),
        "fragment_count": len(fragments),
        "fragment_size": fragment_size,
        "noise_blocks": noise_blocks,
        "storage_block_count": len(storage_blocks),
        "storage_size_bytes": len(storage),
        "original_order": [
            record["fragment_id"]
            for record in fragment_records
        ],
        "fragments": fragment_records,
        "storage_blocks": block_records,
        "storage_file": str(output),
    }

    Path(metadata_path).write_text(
        json.dumps(metadata, indent=2)
    )

    return metadata