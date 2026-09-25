"""
Evidence-guided beam search for fragmented JPEG reconstruction.

Unlike a purely statistical ordering, this search feeds completed JPEG
entropy scans back into the search. A candidate transition receives strong
evidence when the bytes assembled so far can actually consume a progressive
DC scan and terminate at the next JPEG marker.

The search never reads simulator ground truth.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .fragment_transition import calculate_fragment_transition
from .jpeg_progressive_entropy import validate_first_dc_scan, validate_dc_scan_prefix
from .jpeg_stream_parser import parse_jpeg_stream


def _first_scan_evidence(data: bytes) -> Tuple[bool, bool]:
    result = validate_first_dc_scan(data)
    if result.get("status") == "incomplete_entropy":
        return False, False
    return bool(result.get("valid")), True

def _needs_entropy_check(data: bytes) -> bool:
    markers = parse_jpeg_stream(data)
    names = [m["name"] for m in markers]
    # Once a scan and a later DHT/EOI marker exist, at least one complete
    # entropy interval may be available for validation.
    if "SOS" not in names:
        return False
    return "DHT" in names[1:] or "EOI" in names


def search_evidence_guided(
    blocks: Dict[int, bytes],
    start_block: int,
    end_block: int,
    beam_width: int = 80,
    max_depth: int | None = None,
) -> List[dict]:
    if not blocks:
        return []

    if max_depth is None:
        max_depth = len(blocks)

    beam = [{
        "sequence": [start_block],
        "data": blocks[start_block],
        "score": 0.0,
        "completed_dc_scans": 0,
        "valid_dc_scans": 0,
        "invalid_dc_scans": 0,
    }]
    completed: List[dict] = []

    for _depth in range(1, max_depth):
        expanded = []

        for state in beam:
            current = state["sequence"][-1]

            for candidate in blocks:
                if candidate in state["sequence"]:
                    continue

                transition = calculate_fragment_transition(
                    current,
                    candidate,
                    blocks,
                )

                sequence = state["sequence"] + [candidate]
                candidate_data = state["data"] + blocks[candidate]
                score = state["score"] + transition["transition_score"]

                completed_dc = state["completed_dc_scans"]
                valid_dc = state["valid_dc_scans"]
                invalid_dc = state["invalid_dc_scans"]

                # Marker-bearing blocks are the only points where a
                # previously open entropy interval can become complete.
                boundary_hint = (
                    b"\xff\xc4" in blocks[candidate]
                    or b"\xff\xd9" in blocks[candidate]
                )

                if boundary_hint and len(sequence) <= 6:
                    evidence = validate_dc_scan_prefix(candidate_data, max_scans=3)
                    c = evidence["completed"]
                    v = evidence["valid"]
                    bad = evidence["invalid"]

                    if c > completed_dc:
                        newly_valid = v - valid_dc
                        newly_invalid = bad - invalid_dc
                        completed_dc = c
                        valid_dc = v
                        invalid_dc = bad

                        # Strong format-aware evidence. Three consecutive
                        # valid DC scans are substantially stronger than
                        # byte-distribution similarity.
                        score += 120.0 * newly_valid
                        score -= 160.0 * newly_invalid

                # An EOI block is terminal. A path containing it is never
                # expanded further.
                if candidate == end_block:
                    score += 25.0
                    if valid_dc > 0:
                        score += 35.0 * valid_dc
                    if invalid_dc:
                        score -= 45.0 * invalid_dc

                    completed.append({
                        "sequence": sequence,
                        "score": round(score, 5),
                        "completed_dc_scans": completed_dc,
                        "valid_dc_scans": valid_dc,
                        "invalid_dc_scans": invalid_dc,
                    })
                    continue

                expanded.append({
                    "sequence": sequence,
                    "data": candidate_data,
                    "score": score,
                    "completed_dc_scans": completed_dc,
                    "valid_dc_scans": valid_dc,
                    "invalid_dc_scans": invalid_dc,
                })

        if not expanded:
            break

        expanded.sort(
            key=lambda x: (
                x["score"],
                x["valid_dc_scans"],
                -x["invalid_dc_scans"],
            ),
            reverse=True,
        )
        beam = expanded[:beam_width]

    completed.sort(
        key=lambda x: (
            x["score"],
            x["valid_dc_scans"],
            -x["invalid_dc_scans"],
        ),
        reverse=True,
    )
    return completed
