# backend/app/core/scanner.py

from .signatures import FILE_SIGNATURES


def scan_bytes(data: bytes):
    """
    Scan raw bytes for known file signatures
    and estimate whether each finding is valid.
    """

    findings = []

    for file_type, signature_info in FILE_SIGNATURES.items():

        header = signature_info["header"]
        footer = signature_info.get("footer")

        start = 0

        while True:

            offset = data.find(header, start)

            if offset == -1:
                break

            finding = {
                "file_type": file_type,
                "offset": offset,
                "extension": signature_info["extension"],
                "mime_type": signature_info["mime_type"],
                "confidence": "low",
                "status": "candidate",
            }

            # ------------------------------------------------
            # If this format has a footer, look for it.
            # ------------------------------------------------

            if footer:

                footer_offset = data.find(
                    footer,
                    offset + len(header)
                )

                if footer_offset != -1:

                    end_offset = footer_offset + len(footer)

                    finding["end_offset"] = end_offset
                    finding["size_bytes"] = end_offset - offset

                    finding["confidence"] = "high"
                    finding["status"] = "recoverable_candidate"

                else:

                    finding["confidence"] = "medium"
                    finding["status"] = "fragment_or_corrupted"

            # ------------------------------------------------
            # EXE needs more validation than just "MZ".
            # ------------------------------------------------

            elif file_type == "EXE":

                # PE executable normally contains "PE\0\0"
                # at a location pointed to by the PE header.
                #
                # We do not yet perform full PE parsing.
                # Therefore mark MZ-only findings as candidates.

                pe_marker = data.find(
                    b"PE\x00\x00",
                    offset + 2,
                    min(offset + 4096, len(data))
                )

                if pe_marker != -1:

                    finding["confidence"] = "medium"
                    finding["status"] = "possible_executable"

                else:

                    finding["confidence"] = "low"
                    finding["status"] = "possible_false_positive"

            findings.append(finding)

            start = offset + 1

    findings.sort(key=lambda item: item["offset"])

    return findings