from .jpeg_analyzer import scan_jpeg_structure
from .jpeg_scan_parser import extract_scan_information


STRUCTURAL_MARKERS = {
    "SOI",
    "APP0",
    "APP1",
    "APP2",
    "DQT",
    "SOF0",
    "SOF1",
    "SOF2",
    "DHT",
    "SOS",
    "EOI",
}


def extract_jpeg_anchors(blocks):
    anchors = {}

    for block_id, data in blocks.items():

        markers = scan_jpeg_structure(data)
        scans = extract_scan_information(data)

        structural_markers = []

        for marker in markers:

            if marker["name"] in STRUCTURAL_MARKERS:

                structural_markers.append({
                    "name": marker["name"],
                    "offset": marker["offset"],
                    "segment_length": marker.get(
                        "segment_length"
                    ),
                })

        anchors[block_id] = {
            "block_id": block_id,

            "markers": structural_markers,

            "scans": scans,

            "has_soi": any(
                marker["name"] == "SOI"
                for marker in markers
            ),

            "has_eoi": any(
                marker["name"] == "EOI"
                for marker in markers
            ),

            "has_sos": any(
                marker["name"] == "SOS"
                for marker in markers
            ),
        }

    return anchors