from pathlib import Path

from core.jpeg_anchor_graph import build_anchor_graph


STORAGE_PATH = Path(
    "samples/fragmented_storage.bin"
)

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[
        offset:offset + BLOCK_SIZE
    ]


graph = build_anchor_graph(blocks)


print()
print("=" * 70)
print("JPEG ANCHOR COMPATIBILITY GRAPH")
print("=" * 70)

for block_id in sorted(graph):

    print()
    print(
        f"FROM BLOCK {block_id:02d}"
    )

    for edge in graph[block_id]:

        print(
            f"  → {edge['to']:02d} "
            f"| score={edge['score']}"
        )

        for reason in edge["reasons"]:
            print(
                f"      - {reason}"
            )