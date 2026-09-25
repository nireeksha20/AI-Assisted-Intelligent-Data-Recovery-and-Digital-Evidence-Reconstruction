from .jpeg_anchors import extract_jpeg_anchors


BLOCK_SIZE = 4096


def get_anchor_positions(blocks):

    anchors = extract_jpeg_anchors(blocks)

    result = {}

    for block_id, anchor in anchors.items():

        structural_events = []

        for marker in anchor["markers"]:

            structural_events.append({
                "marker": marker["name"],
                "offset_in_block": marker["offset"],
            })

        if not structural_events:
            continue

        result[block_id] = {
            "block_id": block_id,
            "events": structural_events,
            "has_soi": anchor["has_soi"],
            "has_eoi": anchor["has_eoi"],
            "has_sos": anchor["has_sos"],
        }

    return result


def absolute_event_offset(
    block_position,
    offset_in_block,
):
    return (
        block_position * BLOCK_SIZE
        + offset_in_block
    )