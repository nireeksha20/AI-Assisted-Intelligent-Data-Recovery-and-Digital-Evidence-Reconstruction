from .block_analyzer import calculate_entropy
from .jpeg_analyzer import scan_jpeg_structure


BLOCK_SIZE = 4096


def split_into_blocks(data: bytes, block_size: int = BLOCK_SIZE):
    """
    Split storage into fixed-size blocks.
    """

    blocks = {}

    for block_id, offset in enumerate(range(0, len(data), block_size)):
        block = data[offset:offset + block_size]
        blocks[block_id] = block

    return blocks


def analyze_block(block_id: int, data: bytes):
    """
    Extract basic forensic features from one block.
    """

    markers = scan_jpeg_structure(data)

    marker_names = [
        marker["name"]
        for marker in markers
    ]

    return {
        "block_id": block_id,
        "size_bytes": len(data),
        "entropy": round(calculate_entropy(data), 4),
        "has_soi": "SOI" in marker_names,
        "has_eoi": "EOI" in marker_names,
        "has_sos": "SOS" in marker_names,
        "has_dht": "DHT" in marker_names,
        "has_dqt": "DQT" in marker_names,
        "has_sof": any(
            name.startswith("SOF")
            for name in marker_names
        ),
        "markers": marker_names,
    }


def analyze_storage_blocks(data: bytes):
    """
    Analyze every storage block independently.
    """

    blocks = split_into_blocks(data)

    analysis = {}

    for block_id, block_data in blocks.items():
        analysis[block_id] = analyze_block(
            block_id,
            block_data
        )

    return analysis


def find_jpeg_candidates(block_analysis):
    """
    Identify blocks that contain evidence of JPEG structure.
    """

    candidates = []

    for block_id, info in block_analysis.items():

        evidence_score = 0

        if info["has_soi"]:
            evidence_score += 5

        if info["has_sos"]:
            evidence_score += 3

        if info["has_dht"]:
            evidence_score += 2

        if info["has_dqt"]:
            evidence_score += 2

        if info["has_sof"]:
            evidence_score += 2

        if info["has_eoi"]:
            evidence_score += 5

        if evidence_score > 0:

            candidates.append({
                "block_id": block_id,
                "evidence_score": evidence_score,
                "entropy": info["entropy"],
                "markers": info["markers"],
            })

    candidates.sort(
        key=lambda item: item["evidence_score"],
        reverse=True
    )

    return candidates