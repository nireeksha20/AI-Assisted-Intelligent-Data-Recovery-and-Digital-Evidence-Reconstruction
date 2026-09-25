from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.jpeg_stream_parser import parse_jpeg_stream
from core.jpeg_scan_parser import extract_scan_information

BLOCK_SIZE = 4096

STORAGE_PATH = Path("samples/fragmented_storage.bin")

# Evaluation only — NEVER use this inside reconstruction logic.
GROUND_TRUTH_SEQUENCE = [
    34, 24, 3, 16, 32, 7, 21, 30,
    8, 14, 5, 35, 33, 0, 19, 23,
    12, 13, 26, 22, 17, 28, 18, 11,
    10, 27, 2, 9
]


def build_stream():
    storage = STORAGE_PATH.read_bytes()

    return b"".join(
        storage[
            block_id * BLOCK_SIZE:
            (block_id + 1) * BLOCK_SIZE
        ]
        for block_id in GROUND_TRUTH_SEQUENCE
    )


def main():
    data = build_stream()

    markers = parse_jpeg_stream(data)
    scans = extract_scan_information(data)

    print("=" * 90)
    print("JPEG SCAN + HUFFMAN TABLE USAGE")
    print("=" * 90)

    print(f"\nTotal scans: {len(scans)}")
    print()

    for index, scan in enumerate(scans, start=1):
        print("-" * 90)
        print(f"SCAN {index}")

        print(f"  SOS offset       : {scan.get('offset')}")
        print(f"  Components       : {scan.get('components')}")
        print(f"  Spectral start   : {scan.get('spectral_start')}")
        print(f"  Spectral end     : {scan.get('spectral_end')}")
        print(f"  Successive high  : {scan.get('successive_high')}")
        print(f"  Successive low   : {scan.get('successive_low')}")

        ss = scan.get("spectral_start")
        se = scan.get("spectral_end")
        ah = scan.get("successive_high")
        al = scan.get("successive_low")

        if ss == 0 and se == 0:
            scan_type = (
                "DC_INITIAL"
                if ah == 0
                else "DC_REFINEMENT"
            )
        elif ss > 0:
            scan_type = (
                "AC_INITIAL"
                if ah == 0
                else "AC_REFINEMENT"
            )
        else:
            scan_type = "UNKNOWN"

        print(f"  Scan type        : {scan_type}")

        print("  Component tables:")

        for component in scan.get("components", []):
            print(
                f"    Component {component.get('component_id')}: "
                f"DC table={component.get('dc_table')}, "
                f"AC table={component.get('ac_table')}"
            )

    print("\n" + "=" * 90)


if __name__ == "__main__":
    main()