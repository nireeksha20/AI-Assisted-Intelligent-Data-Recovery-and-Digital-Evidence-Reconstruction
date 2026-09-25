from pathlib import Path
from core.fragment_association import split_into_blocks
from core.reconstruction_search import search_paths
from core.reconstruction_validator import validate_jpeg_bytes


STORAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "fragmented_storage.bin"
)

OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "samples"
    / "reconstruction_candidates"
)


def main():
    data = STORAGE_PATH.read_bytes()
    blocks = split_into_blocks(data)

    paths = search_paths(
        blocks,
        start_block=34,
        end_block=9,
        max_depth=36,
        beam_width=50,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("JPEG CANDIDATE VALIDATION")
    print("=" * 70)

    valid_count = 0

    for index, path in enumerate(paths, start=1):

        sequence = path["sequence"]

        reconstructed = b"".join(
            blocks[block_id]
            for block_id in sequence
        )

        validation = validate_jpeg_bytes(reconstructed)

        print()
        print(f"Candidate {index}")
        print("-" * 70)
        print("Sequence:")
        print(" → ".join(f"{x:02d}" for x in sequence))
        print(f"Search score : {path['score']:.4f}")
        print(f"Valid JPEG   : {validation['valid']}")

        if validation["valid"]:
            valid_count += 1

            print(
                f"Image        : "
                f"{validation['width']}x{validation['height']}"
            )
            print(f"Mode         : {validation['mode']}")

            output_path = (
                OUTPUT_DIR / f"recovered_candidate_{index}.jpg"
            )

            output_path.write_bytes(reconstructed)

            print(f"Saved        : {output_path}")

        else:
            print(f"Error        : {validation['error']}")

    print()
    print("=" * 70)
    print(f"VALID CANDIDATES: {valid_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()