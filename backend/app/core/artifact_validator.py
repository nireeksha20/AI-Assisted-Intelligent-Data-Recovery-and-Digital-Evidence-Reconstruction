from .artifact import Artifact


def validate_artifact(artifact: Artifact, data: bytes):
    """
    Perform format-specific structural validation
    on a detected artifact.
    """

    offset = artifact.offset

    if offset < 0 or offset >= len(data):
        artifact.confidence = 0.0
        artifact.status = "invalid_offset"
        artifact.evidence.append("Artifact offset is outside storage")
        return artifact

    if artifact.format == "EXE":
        return validate_exe(artifact, data)

    if artifact.format == "JPEG":
        return validate_jpeg(artifact, data)

    return validate_generic(artifact, data)


def validate_exe(artifact: Artifact, data: bytes):
    """
    Validate a possible Windows PE executable.
    """

    offset = artifact.offset

    if data[offset:offset + 2] != b"MZ":
        artifact.confidence = 0.0
        artifact.status = "invalid"
        artifact.evidence.append("MZ signature missing")
        return artifact

    pe_offset_location = offset + 0x3C

    if pe_offset_location + 4 > len(data):
        artifact.confidence = 0.20
        artifact.status = "fragment_or_corrupted"
        artifact.evidence.append(
            "PE header location is outside available data"
        )
        return artifact

    pe_offset = int.from_bytes(
        data[pe_offset_location:pe_offset_location + 4],
        byteorder="little"
    )

    pe_location = offset + pe_offset

    if pe_location + 4 <= len(data) and data[pe_location:pe_location + 4] == b"PE\x00\x00":
        artifact.confidence = 0.95
        artifact.status = "validated_candidate"
        artifact.evidence.append("Valid PE signature found")
    else:
        artifact.confidence = 0.15
        artifact.status = "possible_false_positive"
        artifact.evidence.append(
            "MZ signature found but PE signature was not validated"
        )

    return artifact


def validate_jpeg(artifact: Artifact, data: bytes):
    """
    Basic JPEG structural validation.

    Deep JPEG reconstruction will be handled
    by the existing JPEG analysis modules later.
    """

    if data[artifact.offset:artifact.offset + 3] != b"\xFF\xD8\xFF":
        artifact.confidence = 0.0
        artifact.status = "invalid"
        artifact.evidence.append("JPEG SOI signature missing")
        return artifact

    artifact.confidence = 0.75
    artifact.status = "validated_candidate"
    artifact.evidence.append("JPEG SOI signature confirmed")

    return artifact


def validate_generic(artifact: Artifact, data: bytes):
    """
    Generic fallback validation.
    """

    artifact.confidence = max(
        artifact.confidence,
        0.30
    )

    artifact.status = "candidate"
    artifact.evidence.append(
        "Format detected by registered file signature"
    )

    return artifact