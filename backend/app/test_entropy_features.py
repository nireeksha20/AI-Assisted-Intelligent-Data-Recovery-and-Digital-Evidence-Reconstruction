from pathlib import Path

from core.block_analyzer import calculate_entropy


STORAGE_PATH = Path("samples/fragmented_storage.bin")

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


def count_pattern(data: bytes, pattern: bytes):
    count = 0
    start = 0

    while True:
        position = data.find(pattern, start)

        if position == -1:
            break

        count += 1
        start = position + 1

    return count


def analyze_entropy_features(data: bytes):

    restart_markers = sum(
        data.count(bytes([0xFF, marker]))
        for marker in range(0xD0, 0xD8)
    )

    stuffed_ff = count_pattern(data, b"\xFF\x00")

    return {
        "entropy": round(calculate_entropy(data), 4),
        "ff00_count": stuffed_ff,
        "restart_marker_count": restart_markers,
        "starts_with_ff": data.startswith(b"\xFF"),
        "ends_with_ff": data.endswith(b"\xFF"),
        "ends_with_ff00": data.endswith(b"\xFF\x00"),
        "first_16": data[:16].hex(" "),
        "last_16": data[-16:].hex(" "),
    }


print("\n=== JPEG ENTROPY FEATURES ===\n")

for block_id, block in blocks.items():

    features = analyze_entropy_features(block)

    print(
        f"Block {block_id:02d} | "
        f"Entropy={features['entropy']:.4f} | "
        f"FF00={features['ff00_count']:3d} | "
        f"RST={features['restart_marker_count']:2d} | "
        f"StartFF={features['starts_with_ff']} | "
        f"EndFF={features['ends_with_ff']} | "
        f"EndFF00={features['ends_with_ff00']}"
    )