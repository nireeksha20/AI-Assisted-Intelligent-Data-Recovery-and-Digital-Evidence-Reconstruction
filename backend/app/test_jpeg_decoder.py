from pathlib import Path
from io import BytesIO

from PIL import Image


STORAGE_PATH = Path("samples/fragmented_storage.bin")
BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


def test_sequence(sequence):
    reconstructed = b"".join(blocks[block_id] for block_id in sequence)

    try:
        image = Image.open(BytesIO(reconstructed))

        # Force Pillow to actually decode the image.
        image.load()

        return {
            "valid": True,
            "format": image.format,
            "size": image.size,
            "mode": image.mode,
        }

    except Exception as error:
        return {
            "valid": False,
            "error": str(error),
        }


# Known correct beginning of the ground-truth sequence.
correct_sequence = [
    34, 24, 3, 16, 32
]

# Deliberately incorrect sequence.
wrong_sequence = [
    34, 24, 16, 3, 32
]


print("\n=== JPEG DECODER TEST ===\n")

print("Correct sequence:")
print(correct_sequence)

result = test_sequence(correct_sequence)
print(result)

print("\nWrong sequence:")
print(wrong_sequence)

result = test_sequence(wrong_sequence)
print(result)