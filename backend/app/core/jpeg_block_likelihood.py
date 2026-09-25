from .fragment_analyzer import calculate_entropy


def count_ff00(data: bytes):
    return data.count(b"\xff\x00")


def count_invalid_ff(data: bytes):
    """
    In JPEG entropy-coded data, an FF byte is normally followed
    by 00 (byte stuffing), or by a legitimate restart/marker
    boundary.

    Random noise tends to contain many arbitrary FFxx pairs.
    """

    invalid = 0

    for i in range(len(data) - 1):

        if data[i] != 0xFF:
            continue

        nxt = data[i + 1]

        # JPEG byte stuffing
        if nxt == 0x00:
            continue

        # Restart markers
        if 0xD0 <= nxt <= 0xD7:
            continue

        # Repeated FF can be marker padding
        if nxt == 0xFF:
            continue

        invalid += 1

    return invalid


def jpeg_entropy_likelihood(data: bytes):
    """
    Estimate whether a block resembles JPEG entropy-coded data.

    This is NOT a reconstruction decision.
    It is only a ranking signal.
    """

    ff00 = count_ff00(data)
    invalid_ff = count_invalid_ff(data)

    total_ff_events = ff00 + invalid_ff

    if total_ff_events == 0:
        stuffing_score = 0.5
    else:
        stuffing_score = ff00 / total_ff_events

    entropy = calculate_entropy(data)

    # JPEG compressed data is normally high entropy.
    entropy_score = min(entropy / 8.0, 1.0)

    likelihood = (
        0.70 * stuffing_score
        + 0.30 * entropy_score
    )

    return {
        "ff00_count": ff00,
        "invalid_ff_count": invalid_ff,
        "stuffing_score": round(stuffing_score, 4),
        "entropy": round(entropy, 4),
        "entropy_score": round(entropy_score, 4),
        "jpeg_likelihood": round(likelihood, 4),
    }