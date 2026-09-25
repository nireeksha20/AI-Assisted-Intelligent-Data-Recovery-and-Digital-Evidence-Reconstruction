import uuid
from dataclasses import dataclass
from heapq import nlargest

from .core.ingestion import blockize, storage_manifest
from .core.formats.plugins import REGISTRY, detect_formats
from .core.reconstruction import reconstruct_greedy
from .core.integrity import assess
from .core.prioritization import prioritize
from .ai import investigate

from .core.jpeg_fragment_features import analyze_fragment
from .core.jpeg_analyzer import scan_jpeg_structure
from .core.jpeg_block_likelihood import jpeg_entropy_likelihood
from .core.jpeg_roles import classify_jpeg_block
from .core.jpeg_anchor_graph import build_anchor_graph
from .core.jpeg_transition import transition_score
from .core.jpeg_sequence import validate_jpeg_sequence
from .core.jpeg_progressive_entropy import (
    validate_progressive_scans,
)


@dataclass
class ReconstructionCandidate:
    sequence: list[int]
    score: float


# ============================================================
# GENERIC RECONSTRUCTION
# ============================================================

def _reconstruct_with_existing_engine(member, plugin):
    """
    Preserve the original generic reconstruction engine.

    reconstruct_greedy() accepts only:
        reconstruct_greedy(fragments)

    and returns:
        list[int]
    """

    fragments = [
        {
            "fragment_id": block.id,
            "data": block.data,
        }
        for block in member
    ]

    sequence = reconstruct_greedy(fragments)

    if not sequence:
        return []

    block_map = {
        block.id: block
        for block in member
    }

    total_score = 0.0
    transitions = 0

    for left_id, right_id in zip(
        sequence,
        sequence[1:]
    ):
        left = block_map[left_id]
        right = block_map[right_id]

        try:
            result = plugin.transition_score(
                left.data,
                right.data
            )

            if isinstance(result, tuple):
                score = result[0]
            else:
                score = result

            total_score += float(score)
            transitions += 1

        except Exception:
            continue

    if transitions == 0:
        total_score = float(len(sequence))

    return [
        ReconstructionCandidate(
            sequence=sequence,
            score=total_score
        )
    ]


# ============================================================
# JPEG HELPERS
# ============================================================

def _jpeg_member(blocks):
    """
    Identify credible JPEG members.

    IMPORTANT:
    - JPEG byte stuffing is supporting evidence, not membership by itself.
    - Structural markers are accepted only when they are locally plausible.
    - Pure entropy fragments are accepted only when their byte-stuffing
      evidence is strong and they do not contain invalid FF events.
    - This deliberately rejects random/noise blocks that merely contain
      accidental JPEG-like marker bytes.
    """
    members = {}

    for block in blocks:
        features = analyze_fragment(block.data, block.id)
        likelihood = jpeg_entropy_likelihood(block.data)
        markers = scan_jpeg_structure(block.data)

        marker_names = {m["name"] for m in markers}

        # Strong boundaries.
        strong_start = features["starts_with_soi"]
        strong_end = (
            features["has_eoi"]
            and not features["has_soi"]
        )

        # A real SOS/scan inside a block is much stronger evidence than
        # an isolated accidental APP/DQT/SOF marker.
        valid_scan = (
            features["scan_count"] > 0
            and likelihood["stuffing_score"] >= 0.50
            and likelihood["invalid_ff_count"] <= 3
        )

        # Local structural marker: do not trust markers whose declared
        # segment crosses the block boundary unless the block also has
        # an independently strong scan/boundary signal.
        local_structural = any(
            marker["name"] in {
                "APP0",
                "APP1",
                "APP2",
                "DQT",
                "SOF0",
                "SOF1",
                "SOF2",
                "DHT",
                "SOS",
            }
            and not marker.get("crosses_block_boundary", False)
            for marker in markers
        ) and likelihood["invalid_ff_count"] <= 3

        # Pure entropy block.  Noise blocks in the simulator have invalid
        # FF events and therefore fail this test.
        entropy_only = (
            not marker_names
            and likelihood["jpeg_likelihood"] >= 0.90
            and likelihood["ff00_count"] >= 1
            and likelihood["invalid_ff_count"] == 0
        )

        if (
            strong_start
            or strong_end
            or valid_scan
            or local_structural
            or entropy_only
        ):
            members[block.id] = block.data

    return members


def _build_jpeg_features(member):
    return {
        block_id: analyze_fragment(
            data,
            block_id
        )
        for block_id, data in member.items()
    }


def _jpeg_transition(left_features, right_features):
    """
    Return the specialized JPEG transition score.
    """

    result = transition_score(
        left_features,
        right_features
    )

    if isinstance(result, dict):
        return float(result.get("score", 0.0))

    if isinstance(result, tuple):
        return float(result[0])

    return float(result)


def _candidate_sequence_score(
    sequence,
    features,
    graph,
):
    """
    Score an entire JPEG path using:

    1. pairwise JPEG transition quality
    2. progressive anchor evidence
    3. role ordering
    """

    if not sequence:
        return float("-inf")

    score = 0.0

    for left_id, right_id in zip(
        sequence,
        sequence[1:]
    ):
        score += _jpeg_transition(
            features[left_id],
            features[right_id]
        )

    # Reward paths that use the anchor graph consistently.
    for left_id, right_id in zip(
        sequence,
        sequence[1:]
    ):
        for edge in graph.get(left_id, []):
            if edge["to"] == right_id:
                score += edge["score"]
                break

    return score


def _beam_search_jpeg(
    member,
    features,
    graph,
    beam_width=40,
    top_k=5,
):
    """
    Beam search over JPEG fragment transitions.

    The search is constrained by:
      - one start block
      - one use of each fragment
      - no transition after an EOI block
      - JPEG transition score
      - progressive anchor evidence
    """

    ids = list(member.keys())

    starts = [
        block_id
        for block_id in ids
        if features[block_id]["starts_with_soi"]
    ]

    ends = {
        block_id
        for block_id in ids
        if features[block_id]["has_eoi"]
    }

    if not starts:
        return []

    # State:
    # (score, sequence, used)
    states = []

    for start_id in starts:
        states.append(
            (
                0.0,
                [start_id],
                {start_id},
            )
        )

    completed = []

    # We only need paths containing all detected JPEG members.
    target_size = len(ids)

    for _depth in range(
        max(1, target_size - 1)
    ):
        next_states = []

        for score, sequence, used in states:

            current = sequence[-1]

            # EOI must terminate a candidate.
            if current in ends:
                if len(sequence) == target_size:
                    completed.append(
                        (
                            score,
                            sequence
                        )
                    )
                continue

            for candidate_id in ids:

                if candidate_id in used:
                    continue

                transition = _jpeg_transition(
                    features[current],
                    features[candidate_id]
                )

                # Strongly reject obviously contradictory
                # transitions while retaining weaker candidates
                # for damaged data.
                if transition < -10:
                    continue

                new_score = score + transition

                # Add anchor-graph evidence.
                for edge in graph.get(current, []):
                    if edge["to"] == candidate_id:
                        new_score += edge["score"]
                        break

                next_states.append(
                    (
                        new_score,
                        sequence + [candidate_id],
                        used | {candidate_id},
                    )
                )

        if not next_states:
            break

        states = nlargest(
            max(1, beam_width),
            next_states,
            key=lambda item: item[0]
        )

    # Keep complete candidates.
    for score, sequence, used in states:
        if (
            len(sequence) == target_size
            and sequence[-1] in ends
        ):
            completed.append(
                (
                    score,
                    sequence
                )
            )

    # If no complete path was found, retain the best
    # paths ending in an EOI block.
    if not completed:
        for score, sequence, used in states:
            if sequence[-1] in ends:
                completed.append(
                    (
                        score,
                        sequence
                    )
                )

    # Deduplicate.
    unique = {}
    for score, sequence in completed:
        key = tuple(sequence)

        if (
            key not in unique
            or score > unique[key]
        ):
            unique[key] = score

    ranked = sorted(
        (
            ReconstructionCandidate(
                sequence=list(sequence),
                score=score
            )
            for sequence, score in unique.items()
        ),
        key=lambda candidate: candidate.score,
        reverse=True
    )

    return ranked[:top_k]


def _validate_jpeg_candidate(
    sequence,
    member,
    features,
):
    reconstructed = b"".join(
        member[block_id]
        for block_id in sequence
    )

    sequence_validation = validate_jpeg_sequence(
        reconstructed
    )

    try:
        progressive_validation = validate_progressive_scans(
            reconstructed
        )
    except Exception as exc:
        progressive_validation = {
            "valid": False,
            "score": 0.0,
            "status": "validator_error",
            "error": str(exc),
        }

    return (
        reconstructed,
        sequence_validation,
        progressive_validation,
    )


def _reconstruct_jpeg(
    blocks,
    beam_width=40,
    top_k=5,
):
    """
    Complete specialized JPEG reconstruction path.
    """

    member = _jpeg_member(blocks)

    if not member:
        return [], [], 0

    features = _build_jpeg_features(
        member
    )

    # Build the specialized progressive JPEG
    # anchor graph.
    graph = build_anchor_graph(
        member
    )

    candidates = _beam_search_jpeg(
        member,
        features,
        graph,
        beam_width=beam_width,
        top_k=max(top_k, 10),
    )

    validated = []

    for candidate in candidates:

        (
            reconstructed,
            sequence_validation,
            progressive_validation,
        ) = _validate_jpeg_candidate(
            candidate.sequence,
            member,
            features,
        )

        whole_valid = bool(
            sequence_validation.get(
                "valid",
                False
            )
        )

        progressive_valid = bool(
            progressive_validation.get(
                "valid",
                False
            )
        )

        sequence_score = float(
            sequence_validation.get(
                "score",
                0.0
            )
        )

        progressive_score = float(
            progressive_validation.get(
                "score",
                0.0
            )
        )

        # Candidate ranking:
        #
        # Whole-sequence validity dominates.
        # Progressive validation is secondary.
        # Transition score is tertiary.
        #
        # This prevents a merely syntactically plausible
        # ordering from beating a structurally correct one.

        ranking_score = candidate.score

        if whole_valid:
            ranking_score += 1000.0
        else:
            ranking_score -= 500.0

        ranking_score += (
            sequence_score * 10.0
        )

        if progressive_valid:
            ranking_score += 300.0

        ranking_score += (
            progressive_score * 5.0
        )

        validated.append({
            "candidate": candidate,
            "reconstructed": reconstructed,
            "sequence_validation": sequence_validation,
            "progressive_validation": progressive_validation,
            "ranking_score": ranking_score,
        })

    validated.sort(
        key=lambda item: item["ranking_score"],
        reverse=True
    )

    return (
        validated[:top_k],
        graph,
        len(member),
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def analyze_storage(
    data: bytes,
    block_size=4096,
    beam_width=40,
    top_k=5,
    run_ai=True
):

    manifest = storage_manifest(
        data,
        block_size
    )

    blocks = blockize(
        data,
        block_size
    )

    fragment_rows = []
    detected_counts = {}

    # ========================================================
    # 1. FRAGMENT DISCOVERY
    # ========================================================

    for block in blocks:

        matches = detect_formats(
            block.data
        )

        roles = []
        types = []

        for plugin, _score in matches:

            types.append(
                plugin.name
            )

            try:
                analysis = plugin.analyze_fragment(
                    block.data
                )

                if analysis:
                    roles.append(
                        analysis.role
                    )

                detected_counts[
                    plugin.name
                ] = (
                    detected_counts.get(
                        plugin.name,
                        0
                    ) + 1
                )

            except Exception:
                continue

        fragment_rows.append({
            "block_id": block.id,
            "offset": block.offset,
            "size": len(block.data),
            "entropy": round(
                block.entropy,
                4
            ),
            "zero_ratio": round(
                block.zero_ratio,
                4
            ),
            "printable_ratio": round(
                block.printable_ratio,
                4
            ),
            "signatures": [
                plugin.name
                for plugin, _score in matches
            ],
            "roles": roles,
            "artifact_types": types,
        })

    artifacts = []
    edges = []

    # ========================================================
    # 2. SPECIALIZED JPEG RECONSTRUCTION
    # ========================================================

    jpeg_results = []
    jpeg_graph = {}
    jpeg_member_count = 0

    jpeg_plugin = REGISTRY.get(
        "JPEG"
    )

    if jpeg_plugin is not None:

        (
            jpeg_results,
            jpeg_graph,
            jpeg_member_count,
        ) = _reconstruct_jpeg(
            blocks,
            beam_width=beam_width,
            top_k=max(top_k, 10),
        )

        # Convert specialized graph into API graph edges.
        for source, graph_edges in jpeg_graph.items():

            for edge in graph_edges:

                edges.append({
                    "source": source,
                    "target": edge["to"],
                    "score": round(
                        float(
                            edge["score"]
                        ),
                        4
                    ),
                    "signals": {
                        "type": "jpeg_progressive_anchor",
                        "reasons": edge.get(
                            "reasons",
                            []
                        ),
                    },
                })

        # ====================================================
        # 3. JPEG CANDIDATES
        # ====================================================

        for rank, result in enumerate(
            jpeg_results[:top_k],
            1
        ):

            candidate = result["candidate"]

            reconstructed = result[
                "reconstructed"
            ]

            sequence_validation = result[
                "sequence_validation"
            ]

            progressive_validation = result[
                "progressive_validation"
            ]

            integrity = assess(
                reconstructed,
                jpeg_plugin,
                candidate.sequence
            )

            sequence_valid = bool(
                sequence_validation.get(
                    "valid",
                    False
                )
            )

            progressive_valid = bool(
                progressive_validation.get(
                    "valid",
                    False
                )
            )

            # Specialized confidence.
            #
            # Transition quality is normalized against
            # the number of transitions. Validation then
            # contributes strongly.
            transition_count = max(
                1,
                len(candidate.sequence) - 1
            )

            transition_confidence = (
                candidate.score /
                transition_count
            )

            transition_confidence = max(
                0.0,
                min(
                    1.0,
                    transition_confidence /
                    10.0
                )
            )

            validation_confidence = (
                sequence_validation.get(
                    "score",
                    0.0
                ) / 100.0
            )

            progressive_confidence = (
                progressive_validation.get(
                    "score",
                    0.0
                ) / 100.0
            )

            confidence = (
                0.20 * transition_confidence
                + 0.55 * validation_confidence
                + 0.25 * progressive_confidence
            )

            if sequence_valid:
                confidence = max(
                    confidence,
                    0.90
                )

            confidence = max(
                0.0,
                min(
                    1.0,
                    confidence
                )
            )

            artifact = {
                "artifact_id":
                    f"ART-{len(artifacts)+1:03d}",

                "format":
                    "JPEG",

                "category":
                    jpeg_plugin.category,

                "fragment_ids":
                    candidate.sequence,

                "fragment_count":
                    len(candidate.sequence),

                "start_block":
                    candidate.sequence[0],

                "end_block":
                    candidate.sequence[-1],

                "reconstruction_confidence":
                    round(
                        confidence,
                        4
                    ),

                "validation":
                    integrity["validation"],

                "integrity":
                    integrity,

                "recoverability":
                    integrity[
                        "recoverability_percent"
                    ],

                "jpeg_validation":
                    sequence_validation,

                "progressive_validation":
                    progressive_validation,

                "candidate_rank":
                    rank,

                "candidate_score":
                    round(
                        candidate.score,
                        4
                    ),

                "validated":
                    sequence_valid,

                "progressive_validated":
                    progressive_valid,

                "priority": {},
            }

            artifact["priority"] = prioritize(
                artifact
            )

            artifacts.append(
                artifact
            )

    # ========================================================
    # 4. GENERIC FORMAT RECONSTRUCTION
    # ========================================================

    for plugin in REGISTRY.values():

        # JPEG is already handled by the specialized engine.
        if plugin.name == "JPEG":
            continue

        member = []

        for block in blocks:

            try:
                detection = float(
                    plugin.detect(block.data)
                )
            except Exception:
                detection = 0.0

            try:
                analysis = plugin.analyze_fragment(
                    block.data
                )
            except Exception:
                analysis = None

            # Generic reconstruction must have actual format evidence.
            # Do not treat a weak incidental byte match as membership.
            if analysis is not None:
                confidence = float(
                    getattr(
                        analysis,
                        "confidence",
                        0.0
                    )
                )

                if (
                    detection >= 0.25
                    or confidence >= 0.85
                ):
                    member.append(block)

        if not member:
            continue

        candidates = (
            _reconstruct_with_existing_engine(
                member,
                plugin
            )
        )

        for candidate in candidates[:top_k]:

            reconstructed = b"".join(
                next(
                    block.data
                    for block in blocks
                    if block.id == block_id
                )
                for block_id in candidate.sequence
            )

            integrity = assess(
                reconstructed,
                plugin,
                candidate.sequence
            )

            confidence = (
                candidate.score /
                max(
                    1,
                    len(candidate.sequence)
                )
            )

            confidence = min(
                1.0,
                max(
                    0.0,
                    confidence
                )
            )

            artifact = {
                "artifact_id":
                    f"ART-{len(artifacts)+1:03d}",

                "format":
                    plugin.name,

                "category":
                    plugin.category,

                "fragment_ids":
                    candidate.sequence,

                "fragment_count":
                    len(candidate.sequence),

                "start_block":
                    candidate.sequence[0],

                "end_block":
                    candidate.sequence[-1],

                "reconstruction_confidence":
                    round(
                        confidence,
                        4
                    ),

                "validation":
                    integrity["validation"],

                "integrity":
                    integrity,

                "recoverability":
                    integrity[
                        "recoverability_percent"
                    ],

                "priority": {},
            }

            artifact["priority"] = prioritize(
                artifact
            )

            artifacts.append(
                artifact
            )

    # ========================================================
    # 5. DEDUPLICATE HYPOTHESES
    # ========================================================

    unique = []
    seen = set()

    for artifact in sorted(
        artifacts,
        key=lambda item:
            item["priority"].get(
                "score",
                0
            ),
        reverse=True
    ):

        key = (
            artifact["format"],
            tuple(
                artifact["fragment_ids"]
            )
        )

        if key not in seen:
            seen.add(key)
            unique.append(
                artifact
            )

    artifacts = unique[:30]

    # ========================================================
    # 6. METRICS
    # ========================================================

    metrics = {
        "detected_format_counts":
            detected_counts,

        "artifact_candidate_count":
            len(artifacts),

        "recoverable_count":
            sum(
                a["recoverability"] >= 65
                for a in artifacts
            ),

        "high_priority_count":
            sum(
                a["priority"].get(
                    "level"
                ) in (
                    "CRITICAL",
                    "HIGH"
                )
                for a in artifacts
            ),

        "graph_edge_count":
            len(edges),

        "block_entropy_mean":
            round(
                sum(
                    block.entropy
                    for block in blocks
                ) / len(blocks),
                4
            )
            if blocks
            else 0,

        "jpeg_candidate_block_count":
            jpeg_member_count,

        "jpeg_valid_candidate_count":
            sum(
                1
                for result in jpeg_results
                if result[
                    "sequence_validation"
                ].get(
                    "valid",
                    False
                )
            ),
    }

    # ========================================================
    # 7. AI DECISION SUPPORT
    # ========================================================

    context = {
        "storage": manifest,
        "fragments": fragment_rows,
        "artifacts": artifacts,
        "metrics": metrics,
    }

    ai_report = (
        investigate(context)
        if run_ai
        else None
    )

    # ========================================================
    # 8. FINAL RESPONSE
    # ========================================================

    return {
        "case_id":
            str(uuid.uuid4()),

        "storage":
            manifest,

        "fragments":
            fragment_rows,

        "artifacts":
            artifacts,

        "edges":
            edges[:1000],

        "metrics":
            metrics,

        "ai_report":
            ai_report.model_dump()
            if ai_report
            else None,

        "pipeline_version":
            "2.1",

        "stages": [
            {
                "name":
                    "ingestion",
                "status":
                    "complete",
            },
            {
                "name":
                    "fragment_discovery",
                "status":
                    "complete",
            },
            {
                "name":
                    "relationship_graph",
                "status":
                    "complete",
            },
            {
                "name":
                    "reconstruction",
                "status":
                    "complete",
            },
            {
                "name":
                    "integrity_assessment",
                "status":
                    "complete",
            },
            {
                "name":
                    "classification_prioritization",
                "status":
                    "complete",
            },
            {
                "name":
                    "ai_decision_support",
                "status":
                    "complete"
                    if ai_report
                    else "skipped",
            },
        ],
    }