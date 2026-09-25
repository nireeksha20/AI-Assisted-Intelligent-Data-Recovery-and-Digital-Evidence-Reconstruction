from io import BytesIO
from PIL import Image


def validate_jpeg_bytes(data: bytes):
    result = {
        "valid": False,
        "format": None,
        "width": None,
        "height": None,
        "mode": None,
        "error": None,
    }

    try:
        image = Image.open(BytesIO(data))

        result["format"] = image.format
        result["width"] = image.width
        result["height"] = image.height
        result["mode"] = image.mode

        # Force complete decoding.
        image.load()

        result["valid"] = image.format == "JPEG"

    except Exception as exc:
        result["error"] = str(exc)

    return result