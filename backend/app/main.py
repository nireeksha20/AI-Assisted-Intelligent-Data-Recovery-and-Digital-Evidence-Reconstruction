from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .pipeline import analyze_storage


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-assisted forensic data recovery and digital evidence reconstruction"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online"
    }


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "ai_enabled": settings.ai_enabled,
        "gemini_configured": bool(settings.gemini_api_key)
    }


async def _read(file: UploadFile):
    data = await file.read()

    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            413,
            "Uploaded evidence exceeds configured size limit."
        )

    return data


# ============================================================
# MAIN END-TO-END PIPELINE
# ============================================================

@app.post("/api/v1/pipeline/analyze")
async def pipeline(
    file: UploadFile = File(...),
    block_size: int = Query(4096, ge=512, le=1048576),
    beam_width: int = Query(40, ge=5, le=300),
    top_k: int = Query(5, ge=1, le=20),
    run_ai: bool = True
):
    return analyze_storage(
        await _read(file),
        block_size,
        beam_width,
        top_k,
        run_ai
    )


# ============================================================
# INDIVIDUAL ANALYSIS API
# ============================================================

@app.post("/api/v1/analyze")
async def analyze(
    file: UploadFile = File(...),
    block_size: int = Query(4096, ge=512, le=1048576)
):
    return analyze_storage(
        await _read(file),
        block_size,
        30,
        3,
        False
    )


# ============================================================
# RECONSTRUCTION API
# ============================================================

@app.post("/api/v1/reconstruct")
async def reconstruct(
    file: UploadFile = File(...),
    block_size: int = Query(4096, ge=512, le=1048576),
    beam_width: int = Query(80, ge=5, le=300),
    top_k: int = Query(10, ge=1, le=20)
):
    result = analyze_storage(
        await _read(file),
        block_size,
        beam_width,
        top_k,
        False
    )

    return {
        "status": "reconstruction_candidates_generated",
        "block_size": block_size,
        "candidate_block_count": len(result["fragments"]),
        "top_candidates": result["artifacts"][:top_k],
        "graph_edges": result["edges"]
    }


# ============================================================
# CLASSIFICATION API
# ============================================================

@app.post("/api/v1/classify")
async def classify(
    file: UploadFile = File(...)
):
    result = analyze_storage(
        await _read(file),
        settings.default_block_size,
        20,
        3,
        False
    )

    return {
        "artifacts": result["artifacts"],
        "metrics": result["metrics"]
    }


# ============================================================
# PRIORITIZATION API
# ============================================================

@app.post("/api/v1/prioritize")
async def prioritize(
    file: UploadFile = File(...)
):
    result = analyze_storage(
        await _read(file),
        settings.default_block_size,
        20,
        5,
        False
    )

    return {
        "artifacts": sorted(
            result["artifacts"],
            key=lambda x: x["priority"]["score"],
            reverse=True
        )
    }


# ============================================================
# AI INVESTIGATION API
# ============================================================

@app.post("/api/v1/ai/investigate")
async def ai_investigate(
    file: UploadFile = File(...),
    block_size: int = Query(4096, ge=512, le=1048576)
):
    result = analyze_storage(
        await _read(file),
        block_size,
        40,
        5,
        True
    )

    return {
        "case_id": result["case_id"],
        "ai_report": result["ai_report"],
        "evidence": result["metrics"]
    }


# ============================================================
# COMPATIBILITY ROUTES
# Keeps your previous frontend/backend contract working.
# ============================================================

@app.post("/analyze")
async def legacy_analyze(
    file: UploadFile = File(...)
):
    return await analyze(file)


@app.post("/reconstruct")
async def legacy_reconstruct(
    file: UploadFile = File(...),
    block_size: int = Query(4096, ge=512, le=1048576),
    beam_width: int = Query(80, ge=5, le=300),
    top_k: int = Query(10, ge=1, le=20)
):
    return await reconstruct(
        file,
        block_size,
        beam_width,
        top_k
    )


@app.post("/recover")
async def recover(
    file: UploadFile = File(...)
):
    data = await _read(file)

    # Conventional contiguous carving is retained
    # as a conservative baseline.
    findings = []

    signatures = {
        "JPEG": b"\xff\xd8\xff",
        "PNG": b"\x89PNG\r\n\x1a\n",
        "PDF": b"%PDF-",
        "ZIP": b"PK\x03\x04",
        "GIF": b"GIF89a",
        "WAV": b"RIFF",
        "EXE": b"MZ"
    }

    for name, prefix in signatures.items():
        pos = 0

        while True:
            pos = data.find(prefix, pos)

            if pos < 0:
                break

            findings.append({
                "file_type": name,
                "offset": pos,
                "status": "signature_detected"
            })

            pos += 1

    return {
        "detected": len(findings),
        "recovered": 0,
        "findings": findings,
        "note": (
            "Use /api/v1/pipeline/analyze "
            "for fragmented reconstruction."
        )
    }