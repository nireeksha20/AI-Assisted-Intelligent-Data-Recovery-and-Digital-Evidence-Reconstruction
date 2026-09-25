# backend/app/core/fragment_extractor.py

from pathlib import Path
import hashlib


def extract_blocks(
    storage_path: str,
    block_size: int = 4096,
):
    """
    Split a raw storage image into fixed-size blocks.

    Each block receives:
    - block ID
    - storage offset
    - size
    - SHA-256 hash
    - basic file-signature information
    """

    storage = Path(storage_path)
    data = storage.read_bytes()

    blocks = []

    for block_id, offset in enumerate(
        range(0, len(data), block_size)
    ):

        block = data[offset:offset + block_size]

        blocks.append({
            "block_id": block_id,
            "offset": offset,
            "size_bytes": len(block),
            "sha256": hashlib.sha256(block).hexdigest(),

            "starts_with_jpeg": block.startswith(
                b"\xFF\xD8\xFF"
            ),

            "ends_with_jpeg": block.endswith(
                b"\xFF\xD9"
            ),

            "contains_jpeg_header": (
                b"\xFF\xD8\xFF" in block
            ),

            "contains_jpeg_footer": (
                b"\xFF\xD9" in block
            ),
        })

    return blocks