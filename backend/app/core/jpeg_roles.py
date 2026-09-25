def classify_jpeg_block(features):

    roles = []

    if features["starts_with_soi"]:

        roles.append("START_CANDIDATE")

    if features["ends_with_eoi"]:

        roles.append("END_CANDIDATE")

    if features["has_sof"]:

        roles.append("FRAME_STRUCTURE")

    if features["has_dqt"]:

        roles.append("QUANTIZATION_TABLE")

    if features["has_dht"]:

        roles.append("HUFFMAN_TABLE")

    if features["has_sos"]:

        roles.append("SCAN_STRUCTURE")

    if (
        features["has_soi"]
        and features["has_eoi"]
        and not features["valid_soi_eoi_order"]
    ):

        roles.append("STRUCTURALLY_SUSPICIOUS")

    return roles