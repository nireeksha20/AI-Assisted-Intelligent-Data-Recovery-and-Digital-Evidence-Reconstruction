from pathlib import Path
from io import BytesIO

from PIL import Image

from core.reconstructor import reconstruct_beam
from core.jpeg_sequence import validate_jpeg_sequence


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


def build_sequence(sequence):
    return b"".join(
        blocks[block_id]
        for block_id in sequence
    )


def validate_sequence(sequence):
    reconstructed = build_sequence(sequence)

    # ------------------------------------------
    # Strict forensic validation
    # ------------------------------------------

    strict_result = validate_jpeg_sequence(
        reconstructed
    )

    # ------------------------------------------
    # Pillow decoder validation
    # Only run if strict validation passes
    # ------------------------------------------

    decoder_result = {
        "valid": False
    }

    if strict_result["valid"]:

        try:
            image = Image.open(
                BytesIO(reconstructed)
            )

            image.load()

            decoder_result = {
                "valid": True,
                "format": image.format,
                "size": image.size,
                "mode": image.mode,
            }

        except Exception as error:

            decoder_result = {
                "valid": False,
                "error": str(error),
            }

    return {
        "strict_valid": strict_result["valid"],
        "strict_status": strict_result["status"],
        "strict_score": strict_result["score"],
        "strict_reasons": strict_result["reasons"],
        "decoder": decoder_result,
    }


print("\n=== BEAM CANDIDATE VALIDATION ===\n")


# ------------------------------------------
# Validate ground truth
# ------------------------------------------

print("GROUND TRUTH")

ground_truth_result = validate_sequence(
    GROUND_TRUTH
)

print(
    f"Strict valid: "
    f"{ground_truth_result['strict_valid']}"
)

print(
    f"Status: "
    f"{ground_truth_result['strict_status']}"
)

print(
    f"Strict score: "
    f"{ground_truth_result['strict_score']}"
)

print(
    f"Decoder: "
    f"{ground_truth_result['decoder']}"
)

print(
    f"Path: "
    f"{GROUND_TRUTH}"
)


# ------------------------------------------
# Run beam search
# ------------------------------------------

print("\nTOP BEAM CANDIDATES\n")

results = reconstruct_beam(
    blocks,
    beam_width=20,
    max_steps=28
)


for rank, result in enumerate(
    results[:10],
    start=1
):

    validation = validate_sequence(
        result["path"]
    )

    print(
        f"{rank:02d}. "
        f"Beam Score: {result['score']:.2f} | "
        f"Strict: {validation['strict_valid']} | "
        f"Status: {validation['strict_status']} | "
        f"Strict Score: {validation['strict_score']}"
    )

    print(
        f"    Decoder: "
        f"{validation['decoder']}"
    )

    print(
        f"    Path: "
        f"{result['path']}"
    )