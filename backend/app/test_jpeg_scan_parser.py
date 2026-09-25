from pathlib import Path

from core.jpeg_scan_parser import extract_scan_information


STORAGE_PATH = Path("samples/fragmented_storage.bin")

BLOCK_SIZE = 4096

data = STORAGE_PATH.read_bytes()

blocks = {}

for block_id, offset in enumerate(range(0, len(data), BLOCK_SIZE)):
    blocks[block_id] = data[offset:offset + BLOCK_SIZE]


SCAN_BLOCKS = [3, 8, 12, 16, 28, 30, 32, 34]


print("\n=== JPEG SCAN PARAMETER ANALYSIS ===\n")


for block_id in SCAN_BLOCKS:

    print(f"\nBLOCK {block_id:02d}")

    scans = extract_scan_information(blocks[block_id])

    if not scans:
        print("  No complete SOS segment found")
        continue

    for index, scan in enumerate(scans, start=1):

        print(f"  Scan {index}")

        if not scan["valid"]:
            print(f"    Invalid: {scan['reason']}")
            continue

        print(f"    Components: {scan['component_count']}")

        print(
            f"    Spectral selection: "
            f"{scan['spectral_start']} → {scan['spectral_end']}"
        )

        print(
            f"    Successive approximation: "
            f"Ah={scan['successive_high']}, "
            f"Al={scan['successive_low']}"
        )

        for component in scan["components"]:
            print(
                f"    Component {component['component_id']}: "
                f"DC={component['dc_table']} "
                f"AC={component['ac_table']}"
            )