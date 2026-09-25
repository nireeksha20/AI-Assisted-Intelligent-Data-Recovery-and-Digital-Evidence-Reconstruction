from pathlib import Path

from core.fragment_association import split_into_blocks
from core.jpeg_block_likelihood import jpeg_entropy_likelihood


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)


def main():

    data = STORAGE_PATH.read_bytes()

    blocks = split_into_blocks(data)

    results = []

    for block_id, block_data in blocks.items():

        score = jpeg_entropy_likelihood(block_data)

        results.append({
            "block_id": block_id,
            **score,
        })

    results.sort(
        key=lambda item: item["jpeg_likelihood"],
        reverse=True,
    )

    print("=" * 70)
    print("JPEG BLOCK LIKELIHOOD")
    print("=" * 70)

    for item in results:

        print(
            f"Block {item['block_id']:02d} | "
            f"JPEG={item['jpeg_likelihood']:.4f} | "
            f"FF00={item['ff00_count']:3d} | "
            f"invalidFF={item['invalid_ff_count']:3d} | "
            f"entropy={item['entropy']:.4f}"
        )


if __name__ == "__main__":
    main()