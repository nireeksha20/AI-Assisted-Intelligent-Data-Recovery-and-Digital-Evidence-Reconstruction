from dataclasses import dataclass
from .utils import sha256, entropy, zero_ratio, printable_ratio


@dataclass
class Block:
    id: int
    offset: int
    data: bytes
    entropy: float
    zero_ratio: float
    printable_ratio: float


def blockize(data: bytes, block_size: int) -> list[Block]:
    """
    Split storage into non-overlapping fixed-size blocks.

    The slice MUST use the byte offset i * block_size.
    """
    return [
        Block(
            id=i,
            offset=i * block_size,
            data=data[i * block_size:(i + 1) * block_size],
            entropy=entropy(
                data[i * block_size:(i + 1) * block_size]
            ),
            zero_ratio=zero_ratio(
                data[i * block_size:(i + 1) * block_size]
            ),
            printable_ratio=printable_ratio(
                data[i * block_size:(i + 1) * block_size]
            ),
        )
        for i in range(
            (len(data) + block_size - 1) // block_size
        )
    ]


def storage_manifest(data: bytes, block_size: int) -> dict:
    blocks = blockize(data, block_size)

    return {
        "size_bytes": len(data),
        "block_size": block_size,
        "block_count": len(blocks),
        "sha256": sha256(data),
        "partial_last_block": bool(
            blocks
            and len(blocks[-1].data) != block_size
        ),
    }
