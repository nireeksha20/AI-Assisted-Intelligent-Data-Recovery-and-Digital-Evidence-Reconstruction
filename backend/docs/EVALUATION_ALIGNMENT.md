# CalmStacks Evaluation Alignment

The official rulebook evaluates:
- Technical Depth — 35%
- Innovation — 25%
- UI/UX — 20%
- Practical Impact — 20%

## Technical Depth — 35%
Backend evidence:
- format-plugin architecture
- graph-based fragment relationships
- beam-search reconstruction hypotheses
- format-aware validation
- integrity/corruption metrics
- SHA-256 evidence provenance
- deterministic prioritization
- grounded AI integration
- unified pipeline API
- legacy API compatibility
- test suite

## Innovation — 25%
The differentiator is not a generic recovery utility. The system models storage as an
evidence graph and combines multiple reconstruction hypotheses with integrity-aware
decision support. AI is used after evidence extraction to explain realistic recovery.

## UI/UX — 20%
The backend exposes a single pipeline contract that supports a dashboard showing:
storage overview, fragment graph, artifact candidates, integrity, recoverability, priority,
and AI investigation summary.

## Practical Impact — 20%
The workflow mirrors the investigator's sequence:
discover evidence -> associate fragments -> reconstruct candidates -> validate ->
estimate what can actually be restored -> prioritize review.

## Demo recommendation
1. Upload a deliberately fragmented storage image.
2. Show discovered fragments and artifact families.
3. Open the relationship graph.
4. Compare top reconstruction candidates.
5. Show integrity/recoverability.
6. Show deterministic priority factors.
7. Open the grounded AI investigation summary.
8. Demonstrate that the system reports uncertainty instead of fabricating recovery.
