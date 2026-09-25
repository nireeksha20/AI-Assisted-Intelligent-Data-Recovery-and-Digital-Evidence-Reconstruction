import hashlib
import math


def calculate_entropy(data: bytes) -> float:

    if not data:
        return 0.0

    frequency = [0] * 256

    for byte in data:
        frequency[byte] += 1

    length = len(data)
    entropy = 0.0

    for count in frequency:

        if count == 0:
            continue

        probability = count / length
        entropy -= probability * math.log2(probability)

    return entropy


def analyze_fragment(data: bytes, fragment_id: int):

    sha256 = hashlib.sha256(data).hexdigest()

    return {
        "fragment_id": fragment_id,
        "size_bytes": len(data),
        "sha256": sha256,
        "entropy": round(calculate_entropy(data), 4),
        "starts_with_pdf": data.startswith(b"%PDF"),
        "starts_with_jpeg": data.startswith(b"\xFF\xD8\xFF"),
        "starts_with_png": data.startswith(b"\x89PNG\r\n\x1a\n"),
        "ends_with_pdf": data.endswith(b"%%EOF"),
        "ends_with_jpeg": data.endswith(b"\xFF\xD9"),
        "ends_with_png": data.endswith(
            b"\x49\x45\x4E\x44\xAE\x42\x60\x82"
        ),
    }