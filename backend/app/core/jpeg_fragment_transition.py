from .jpeg_scan_parser import extract_scan_information
from .jpeg_scan_transition import scan_transition_score


def get_fragment_scans(data: bytes):
    return extract_scan_information(data)


def fragment_scan_transition_score(left_data: bytes, right_data: bytes):
    left_scans = get_fragment_scans(left_data)
    right_scans = get_fragment_scans(right_data)

    if not left_scans or not right_scans:
        return {
            "score": 0.0,
            "reasons": [],
            "left_scan_count": len(left_scans),
            "right_scan_count": len(right_scans),
        }

    # The last scan in the left fragment and
    # first scan in the right fragment are the
    # relevant boundary scans.
    left_scan = left_scans[-1]
    right_scan = right_scans[0]

    result = scan_transition_score(left_scan, right_scan)

    return {
        "score": result["score"],
        "reasons": result["reasons"],
        "left_type": result["left_type"],
        "right_type": result["right_type"],
        "left_scan_count": len(left_scans),
        "right_scan_count": len(right_scans),
    }