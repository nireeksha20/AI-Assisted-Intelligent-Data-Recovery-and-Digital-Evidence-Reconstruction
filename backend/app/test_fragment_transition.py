from pathlib import Path

from core.fragment_association import split_into_blocks
from core.fragment_transition import calculate_fragment_transition


def main():

    sample_path = Path("samples/fragmented_storage.bin")
    data = sample_path.read_bytes()

    blocks = split_into_blocks(data)

    source_block = 34

    results = []

    for candidate_block in blocks:

        if candidate_block == source_block:
            continue

        result = calculate_fragment_transition(
            source_block,
            candidate_block,
            blocks,
        )

        results.append(result)

    results.sort(
        key=lambda item: item["transition_score"],
        reverse=True,
    )

    print()
    print("=" * 70)
    print(f"FRAGMENT TRANSITION ANALYSIS: BLOCK {source_block}")
    print("=" * 70)

    print()

    for result in results[:10]:

        print(
            f"{result['left_block']:02d} -> "
            f"{result['right_block']:02d} | "
            f"score={result['transition_score']:.4f} | "
            f"boundary={result['boundary_similarity']:.4f} | "
            f"entropy={result['entropy_compatibility']:.4f} | "
            f"anchor={result['anchor_score']:.4f}"
        )

        for reason in result["reasons"]:
            print(f"    {reason}")


if __name__ == "__main__":
    main()