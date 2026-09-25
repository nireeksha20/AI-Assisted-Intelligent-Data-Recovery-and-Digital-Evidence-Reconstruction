# Technical Architecture

## Why this architecture matches the challenge

### 1. Intelligent fragment reconstruction
Fragments are converted into feature-bearing blocks. Every supported format exposes a
format-specific transition function. A beam-search engine explores multiple hypotheses
instead of trusting one greedy next-block decision.

### 2. Data integrity and corruption assessment
Every candidate is passed through a format validator. Integrity combines validation score,
completeness evidence and corruption estimate. Hashes are retained for provenance.

### 3. Classification and prioritization
Artifact family and category are separated from recovery confidence. Priority is a
deterministic weighted score with transparent factors. This avoids letting a generative
model make opaque forensic decisions.

### 4. Investigative decision support
The AI layer receives structured evidence only. Gemini is used to summarize findings,
explain priority, identify limitations and recommend review actions. A deterministic
fallback keeps the product usable if the external model is unavailable.

## Reconstruction scoring

The generic engine combines:
- format compatibility
- marker / structural continuity
- entropy continuity
- artifact role compatibility
- explicit start/end constraints

The architecture deliberately keeps statistical transition scores as one signal rather
than treating them as ground truth. This addresses the failure mode where a syntactically
valid but incorrectly ordered JPEG can still be decoded by a permissive decoder.

## Evidence graph

Nodes are storage blocks. Edges represent plausible adjacency. Edge metadata contains
the contributing signals. The frontend can render this graph to explain why a fragment
was associated with an artifact.

## Realistic recovery model

The system reports:
- recoverable
- mostly recoverable
- partially recoverable
- unlikely recoverable

It never claims to recover bytes that are absent from the supplied evidence.
