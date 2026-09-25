from pathlib import Path

from core.fragment_association import (
    analyze_storage_blocks,
    find_jpeg_candidates,
)


def main():

    sample_path = Path("samples/fragmented_storage.bin")
    data = sample_path.read_bytes()

    analysis = analyze_storage_blocks(data)

    candidates = find_jpeg_candidates(analysis)

    print()
    print("=" * 70)
    print("FRAGMENT ASSOCIATION ANALYSIS")
    print("=" * 70)

    print()
    print(f"Storage size : {len(data):,} bytes")
    print(f"Block count  : {len(analysis)}")

    print()
    print("JPEG STRUCTURAL CANDIDATES")
    print("-" * 70)

    for candidate in candidates:

        print(
            f"Block {candidate['block_id']:02d} | "
            f"score={candidate['evidence_score']:2d} | "
            f"entropy={candidate['entropy']:.4f} | "
            f"markers={candidate['markers']}"
        )


if __name__ == "__main__":
    main()