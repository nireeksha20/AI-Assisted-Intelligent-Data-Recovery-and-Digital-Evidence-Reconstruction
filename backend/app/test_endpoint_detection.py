from pathlib import Path

from core.jpeg_analyzer import analyze_jpeg_block


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(
    range(0, len(data), BLOCK_SIZE)
):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


candidates = []

for block_id, block in blocks.items():

    features = analyze_jpeg_block(block)

    start_score = 0
    end_score = 0

    # START evidence
    if features["starts_with_soi"]:
        start_score += 50

    if features["has_soi"]:
        start_score += 20

    if features["has_dqt"]:
        start_score += 10

    if features["has_sof"]:
        start_score += 10

    if features["has_dht"]:
        start_score += 5

    if features["has_sos"]:
        start_score += 5

    # END evidence
    if features["has_eoi"]:
        end_score += 50

    if features["ends_with_eoi"]:
        end_score += 30

    candidates.append(
        {
            "block_id": block_id,
            "start_score": start_score,
            "end_score": end_score,
            "has_soi": features["has_soi"],
            "has_eoi": features["has_eoi"],
            "has_sof": features["has_sof"],
            "has_dqt": features["has_dqt"],
            "has_dht": features["has_dht"],
            "has_sos": features["has_sos"],
        }
    )


print("\n=== START CANDIDATES ===\n")

for item in sorted(
    candidates,
    key=lambda x: x["start_score"],
    reverse=True
):

    if item["start_score"] > 0:

        print(
            f"Block {item['block_id']:02d}"
            f" | Score: {item['start_score']:3d}"
            f" | SOI: {item['has_soi']}"
            f" | DQT: {item['has_dqt']}"
            f" | SOF: {item['has_sof']}"
            f" | DHT: {item['has_dht']}"
            f" | SOS: {item['has_sos']}"
        )


print("\n=== END CANDIDATES ===\n")

for item in sorted(
    candidates,
    key=lambda x: x["end_score"],
    reverse=True
):

    if item["end_score"] > 0:

        print(
            f"Block {item['block_id']:02d}"
            f" | Score: {item['end_score']:3d}"
            f" | EOI: {item['has_eoi']}"
            f" | Ends EOI: "
            f"{item['has_eoi'] and item['block_id'] == 9}"
        )