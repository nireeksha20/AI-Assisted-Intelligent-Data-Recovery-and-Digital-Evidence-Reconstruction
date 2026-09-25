from pathlib import Path

STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

# Evaluation-only known-good block sequence.
# Do NOT put this into reconstruction logic.
GROUND_TRUTH_SEQUENCE = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18, 11,
    10, 27, 2, 9
]

storage = STORAGE_PATH.read_bytes()

stream = b"".join(
    storage[block_id * BLOCK_SIZE:(block_id + 1) * BLOCK_SIZE]
    for block_id in GROUND_TRUTH_SEQUENCE
)

for target in [11756, 15871]:
    print("=" * 90)
    print(f"SUSPICIOUS MARKER AT OFFSET {target}")
    print("=" * 90)

    start = target - 32
    end = target + 32

    chunk = stream[start:end]

    print(f"Range: {start}..{end - 1}")
    print()

    for absolute_offset in range(start, end, 16):
        row = stream[absolute_offset:absolute_offset + 16]

        hex_bytes = " ".join(f"{b:02X}" for b in row)

        ascii_bytes = "".join(
            chr(b) if 32 <= b <= 126 else "."
            for b in row
        )

        print(
            f"{absolute_offset:6d}  "
            f"{hex_bytes:<47}  "
            f"{ascii_bytes}"
        )

    print()