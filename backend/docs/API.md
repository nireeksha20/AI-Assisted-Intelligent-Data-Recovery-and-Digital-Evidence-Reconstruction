# API Contract

## Recommended endpoint

`POST /api/v1/pipeline/analyze`

Multipart:
- `file`: storage/evidence image
- `block_size`: default 4096
- `beam_width`: default 40
- `top_k`: default 5
- `run_ai`: default true

The response includes:
- case id
- storage manifest
- block-level evidence
- artifact candidates
- relationship edges
- integrity/recoverability
- priority
- AI report
- per-stage pipeline status

## Frontend integration

The frontend should use the pipeline endpoint for the main workflow. It can then render
`fragments`, `edges`, `artifacts`, `metrics` and `ai_report` without knowing the internal
reconstruction implementation.
