from pathlib import Path

from core.block_analyzer import analyze_block


storage_path = Path("samples/fragmented_storage.bin")

data = storage_path.read_bytes()

block_size = 4096

blocks = []

for block_id, offset in enumerate(
    range(0, len(data), block_size)
):

    block = data[offset:offset + block_size]

    analysis = analyze_block(
        block,
        block_id
    )

    analysis["offset"] = offset

    blocks.append(analysis)


print("\nTotal storage blocks:", len(blocks))

print("\nBlock analysis:\n")

for block in blocks:

    print(
        f"Block {block['block_id']:02d} | "
        f"Entropy: {block['entropy']:.4f} | "
        f"Printable: {block['printable_ratio']:.4f} | "
        f"JPEG header: {block['starts_with_jpeg']} | "
        f"JPEG footer: {block['contains_jpeg_footer']} | "
        f"Trailing zeros: {block['trailing_zero_bytes']}"
    )