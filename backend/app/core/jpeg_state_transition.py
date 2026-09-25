ROLE_TRANSITIONS = {
    "JPEG_START": {
        "JPEG_DATA": 3.0,
        "JPEG_SCAN_BOUNDARY": 1.0,
        "JPEG_END_CANDIDATE": -5.0,
        "SUSPICIOUS_MARKER_BLOCK": -8.0,
        "JPEG_HEADER_LIKE": -2.0,
    },

    "JPEG_DATA": {
        "JPEG_DATA": 2.0,
        "JPEG_SCAN_BOUNDARY": 3.0,
        "JPEG_END_CANDIDATE": 4.0,
        "JPEG_HEADER_LIKE": -1.0,
        "SUSPICIOUS_MARKER_BLOCK": -6.0,
    },

    "JPEG_SCAN_BOUNDARY": {
        "JPEG_DATA": 3.0,
        "JPEG_SCAN_BOUNDARY": 2.0,
        "JPEG_END_CANDIDATE": 3.0,
        "JPEG_HEADER_LIKE": -2.0,
        "SUSPICIOUS_MARKER_BLOCK": -6.0,
    },

    "JPEG_HEADER_LIKE": {
        "JPEG_DATA": 1.0,
        "JPEG_SCAN_BOUNDARY": 1.0,
        "JPEG_END_CANDIDATE": -2.0,
        "SUSPICIOUS_MARKER_BLOCK": -6.0,
    },

    "JPEG_END_CANDIDATE": {
        "JPEG_DATA": -20.0,
        "JPEG_SCAN_BOUNDARY": -20.0,
        "JPEG_END_CANDIDATE": -20.0,
        "SUSPICIOUS_MARKER_BLOCK": -20.0,
        "JPEG_HEADER_LIKE": -20.0,
    },

    "SUSPICIOUS_MARKER_BLOCK": {
        "JPEG_DATA": -5.0,
        "JPEG_SCAN_BOUNDARY": -5.0,
        "JPEG_END_CANDIDATE": -5.0,
        "JPEG_HEADER_LIKE": -5.0,
        "SUSPICIOUS_MARKER_BLOCK": -10.0,
    },
}


def state_transition_score(
    left_state,
    right_state,
):
    left_role = left_state["role"]
    right_role = right_state["role"]

    return ROLE_TRANSITIONS.get(
        left_role,
        {}
    ).get(
        right_role,
        0.0
    )