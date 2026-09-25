"""
High-level forensic recovery orchestration.

This module is deliberately deterministic and evidence-oriented. It combines:
1. signature detection,
2. block-level JPEG membership analysis,
3. progressive JPEG structural constraints,
4. statistical transition evidence,
5. beam-search candidate generation,
6. format-aware validation.

No ground-truth metadata is used by the production pipeline.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ..core.artifact_pipeline import analyze_artifacts
from ..core.carver import carve_files
from ..core.fragment_association import split_into_blocks
from ..core.fragment_membership import classify_fragment_membership
from ..core.jpeg_progressive_entropy import validate_progressive_scans
from ..core.jpeg_sequence import validate_jpeg_sequence
from ..core.forensic_search import search_evidence_guided
from ..core.reconstruction_validator import validate_jpeg_bytes
from ..core.scanner import scan_bytes


def analyze_storage(data: bytes, block_size: int = 4096) -> dict[str, Any]:
    findings = scan_bytes(data)
    artifacts = analyze_artifacts(data)

    blocks = split_into_blocks(data, block_size)
    jpeg_blocks = []
    for block_id, block in blocks.items():
        membership = classify_fragment_membership(block)
        if membership.get("role") != "noise_candidate":
            jpeg_blocks.append(membership)

    return {
        "storage": {
            "size_bytes": len(data),
            "block_size": block_size,
            "block_count": len(blocks),
        },
        "signatures": findings,
        "signature_count": len(findings),
        "artifacts": [asdict(a) for a in artifacts],
        "jpeg_candidate_blocks": jpeg_blocks,
    }


def recover_contiguous(data: bytes, output_dir: str = "recovered") -> dict[str, Any]:
    findings = scan_bytes(data)
    recovered = carve_files(data, findings, output_dir=output_dir)
    return {
        "detected": len(findings),
        "recovered": len(recovered),
        "findings": findings,
        "recovered_files": recovered,
    }


def reconstruct_jpeg(
    data: bytes,
    block_size: int = 4096,
    beam_width: int = 80,
    top_k: int = 10,
) -> dict[str, Any]:
    blocks = split_into_blocks(data, block_size)

    # Candidate membership is computed first so the search space is
    # restricted to blocks that contain positive JPEG evidence.
    membership = {
        block_id: classify_fragment_membership(block)
        for block_id, block in blocks.items()
    }

    candidate_ids = [
        block_id
        for block_id, info in membership.items()
        if info.get("membership") == "jpeg"
    ]

    candidate_blocks = {
        block_id: blocks[block_id]
        for block_id in candidate_ids
    }

    start_candidates = [
        block_id for block_id in candidate_ids
        if membership[block_id].get("role") == "jpeg_start"
    ]
    end_candidates = [
        block_id for block_id in candidate_ids
        if membership[block_id].get("role") == "jpeg_end"
    ]

    if not start_candidates:
        return {
            "status": "no_jpeg_start",
            "candidate_block_count": len(candidate_ids),
            "candidates": [],
        }

    ranked = []
    for start in start_candidates:
        for end in end_candidates:
            paths = search_evidence_guided(
                candidate_blocks,
                start_block=start,
                end_block=end,
                max_depth=len(candidate_blocks),
                beam_width=beam_width,
            )
            ranked.extend(paths)

    ranked.sort(key=lambda item: item["score"], reverse=True)

    # Format-aware validation is deliberately applied after candidate
    # generation. This avoids running a full parser for every beam state.
    results = []
    seen = set()

    for candidate in ranked:
        sequence = tuple(candidate["sequence"])
        if sequence in seen:
            continue
        seen.add(sequence)

        reconstructed = b"".join(
            candidate_blocks[block_id] for block_id in sequence
        )

        structural = validate_jpeg_sequence(reconstructed)
        decoder = validate_jpeg_bytes(reconstructed)
        entropy = validate_progressive_scans(reconstructed)

        # Candidate ranking is evidence aggregation, not a single heuristic.
        final_score = float(candidate["score"])
        final_score += structural.get("score", 0.0) * 0.20
        if decoder.get("valid"):
            final_score += 100.0
        valid_dc = sum(
            1 for scan in entropy.get("scans", [])
            if scan.get("valid")
            and scan.get("scan", {}).get("spectral_start") == 0
            and scan.get("scan", {}).get("spectral_end") == 0
        )
        invalid_dc = sum(
            1 for scan in entropy.get("scans", [])
            if not scan.get("valid")
            and scan.get("scan", {}).get("spectral_start") == 0
            and scan.get("scan", {}).get("spectral_end") == 0
        )
        final_score += 35.0 * valid_dc
        final_score -= 70.0 * invalid_dc

        results.append({
            "sequence": list(sequence),
            "search_score": round(candidate["score"], 4),
            "final_score": round(final_score, 4),
            "structural_validation": structural,
            "decoder_validation": decoder,
            "progressive_entropy": entropy,
            "reconstructed_size_bytes": len(reconstructed),
        })

        if len(results) >= max(top_k * 5, top_k):
            break

    results.sort(key=lambda item: item["final_score"], reverse=True)

    return {
        "status": "reconstruction_candidates_generated",
        "block_size": block_size,
        "candidate_block_count": len(candidate_ids),
        "start_candidates": start_candidates,
        "end_candidates": end_candidates,
        "top_candidates": results[:top_k],
    }
