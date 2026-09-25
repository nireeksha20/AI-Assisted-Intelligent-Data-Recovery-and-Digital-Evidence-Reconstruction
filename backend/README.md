# AI-Assisted Intelligent Data Recovery & Digital Evidence Reconstruction

Advanced FastAPI backend for the CalmStacks 24H Hackathon challenge.

## Architecture

Storage image -> forensic ingestion -> fragment features -> artifact discovery ->
fragment relationship graph -> format-aware reconstruction -> integrity assessment ->
classification -> deterministic prioritization -> grounded AI investigator report.

The AI layer is intentionally downstream of deterministic forensic evidence. It explains,
summarizes and recommends actions; it does not invent bytes or decide fragment order.

## Supported artifact families

Detection / structural analysis plugins:
- JPEG
- PNG
- GIF
- PDF
- ZIP
- MP3
- MP4 / ISO-BMFF
- WAV
- Windows PE/EXE

The reconstruction engine is format-agnostic and asks each format plugin for:
1. fragment role analysis
2. pairwise compatibility
3. reconstructed-stream validation
4. integrity evidence

This means adding a format does not require rewriting the search engine.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Main API

- `POST /api/v1/ingest`
- `POST /api/v1/analyze`
- `POST /api/v1/reconstruct`
- `POST /api/v1/classify`
- `POST /api/v1/prioritize`
- `POST /api/v1/ai/investigate`
- `POST /api/v1/pipeline/analyze`
- legacy-compatible `/analyze`, `/reconstruct`, `/recover`

The unified pipeline endpoint is the recommended frontend integration point.

## AI

Set:

```env
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash
```

If no key is configured, the backend uses a deterministic grounded fallback so the
demo remains functional without an external model.

## Forensic safety model

The backend reads the uploaded bytes as evidence. It never executes recovered files.
It computes SHA-256 hashes, preserves byte offsets, records provenance, and reports
unrecoverable/uncertain regions instead of fabricating data.

## Clean-slate hackathon note

This package is a newly generated implementation. For a clean-slate event submission,
use it only if it is created/committed during the permitted hackathon development period.
Do not copy a pre-event repository into the submission as a substitute for event-time
development. AI assistance is permitted by the event rules, but the team remains
responsible for the submitted implementation.
