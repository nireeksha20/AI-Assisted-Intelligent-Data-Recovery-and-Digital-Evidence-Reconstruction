from pathlib import Path

from core.jpeg_analyzer import analyze_jpeg_block
from core.jpeg_roles import classify_jpeg_block


storage_path = Path(
    "samples/fragmented_storage.bin"
)

data = storage_path.read_bytes()

BLOCK_SIZE = 4096


print("\n=== JPEG STRUCTURAL FEATURES ===\n")


for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):

    block = data[
        offset:offset + BLOCK_SIZE
    ]

    result = analyze_jpeg_block(block)

    roles = classify_jpeg_block(result)

    if result["marker_count"] > 0:

        print(
            f"Block {block_id:02d}"
            f" | Quality: {result['structural_quality']}"
            f" | Roles: {roles}"
            f" | SOI: {result['has_soi']}"
            f" | EOI: {result['has_eoi']}"
            f" | SOF: {result['has_sof']}"
            f" | DQT: {result['has_dqt']}"
            f" | DHT: {result['has_dht']}"
            f" | SOS: {result['has_sos']}"
            f" | Valid SOI→EOI: "
            f"{result['valid_soi_eoi_order']}"
        )