from .signatures import FILE_SIGNATURES
from .format_registry import FORMAT_REGISTRY


def detect_formats(data: bytes):
    """
    Detect known file formats inside a binary/storage image.

    Returns a list of candidate artifacts with:
    - format
    - offset
    - extension
    - MIME type
    - category
    - confidence
    - status
    """

    findings = []

    for file_type, signature in FILE_SIGNATURES.items():
        header = signature["header"]

        start = 0

        while True:
            offset = data.find(header, start)

            if offset == -1:
                break

            registry_info = FORMAT_REGISTRY.get(file_type, {})

            finding = {
                "format": file_type,
                "offset": offset,
                "extension": signature.get(
                    "extension",
                    registry_info.get("extensions", [""])[0]
                ),
                "mime_type": signature.get(
                    "mime_type",
                    registry_info.get("mime_type")
                ),
                "category": registry_info.get(
                    "category",
                    "unknown"
                ),
                "confidence": "medium",
                "status": "candidate",
            }

            findings.append(finding)

            start = offset + 1

    findings.sort(key=lambda item: item["offset"])

    return findings