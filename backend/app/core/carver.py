# backend/app/core/carver.py

from pathlib import Path


def carve_files(data: bytes, findings: list, output_dir: str = "recovered"):
    """
    Extract recoverable artifacts from raw bytes.

    Only findings with:
        status = recoverable_candidate

    are carved.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    recovered = []
    counter = {}

    for finding in findings:

        if finding.get("status") != "recoverable_candidate":
            continue

        file_type = finding["file_type"]
        extension = finding["extension"]
        offset = finding["offset"]
        end_offset = finding.get("end_offset")

        if end_offset is None:
            continue

        # Make sure offsets are valid.
        if offset < 0 or end_offset <= offset:
            continue

        if end_offset > len(data):
            end_offset = len(data)

        # Extract the actual bytes.
        file_data = data[offset:end_offset]

        # Number files of the same type.
        counter[file_type] = counter.get(file_type, 0) + 1

        filename = (
            f"recovered_{file_type.lower()}_"
            f"{counter[file_type]}{extension}"
        )

        file_path = output_path / filename

        with open(file_path, "wb") as output_file:
            output_file.write(file_data)

        recovered.append({
            "filename": filename,
            "file_type": file_type,
            "path": str(file_path),
            "offset": offset,
            "end_offset": end_offset,
            "size_bytes": len(file_data),
        })

    return recovered