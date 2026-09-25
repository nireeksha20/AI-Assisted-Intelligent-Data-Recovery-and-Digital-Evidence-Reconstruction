from pathlib import Path

from core.fragment_association import split_into_blocks
from core.reconstruction_search import search_paths


def main():

    sample_path = Path(
        "samples/fragmented_storage.bin"
    )

    data = sample_path.read_bytes()

    blocks = split_into_blocks(data)

    start_block = 34
    end_block = 9

    results = search_paths(
        blocks=blocks,
        start_block=start_block,
        end_block=end_block,
        max_depth=28,
        beam_width=10,
    )

    print()
    print("=" * 70)
    print("GLOBAL JPEG RECONSTRUCTION SEARCH")
    print("=" * 70)

    print()
    print(f"Start block : {start_block}")
    print(f"End block   : {end_block}")
    print(f"Paths found : {len(results)}")

    print()

    for index, result in enumerate(
        results[:5],
        start=1,
    ):

        print(
            f"Path {index}: "
            f"score={result['score']:.4f}"
        )

        print(
            "  "
            + " → ".join(
                f"{block:02d}"
                for block in result["sequence"]
            )
        )


if __name__ == "__main__":
    main()