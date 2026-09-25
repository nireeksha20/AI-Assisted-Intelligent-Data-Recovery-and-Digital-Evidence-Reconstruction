from pathlib import Path
from io import BytesIO

from PIL import Image


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


GROUND_TRUTH = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18, 11,
    10, 27, 2, 9
]


reconstructed = b"".join(
    blocks[block_id]
    for block_id in GROUND_TRUTH
)

output_path = Path("samples/ground_truth_reconstructed.jpg")
output_path.write_bytes(reconstructed)


print("\n=== FULL JPEG RECONSTRUCTION TEST ===\n")

print("Fragments:", len(GROUND_TRUTH))
print("Reconstructed bytes:", len(reconstructed))
print("Output:", output_path)


try:
    image = Image.open(BytesIO(reconstructed))

    print("\nPillow opened the JPEG successfully.")

    print("Format:", image.format)
    print("Size:", image.size)
    print("Mode:", image.mode)

    image.load()

    print("JPEG decoded successfully.")
    print("VALID RECONSTRUCTION")

except Exception as error:

    print("\nJPEG validation failed:")
    print(error)