import json, os
from typing import Any
from .schemas import AIReport
from .config import get_settings

SYSTEM_PROMPT = """
You are EvidenceRecover AI, a digital-forensics decision-support assistant.
You are NOT the byte-reconstruction engine. The deterministic forensic engine is authoritative
for hashes, offsets, fragment membership, validation results, integrity measurements and scores.

Rules:
- Never invent timestamps, filenames, user identities, deleted content, causes or recovered facts.
- Only make claims supported by the supplied evidence.
- Clearly distinguish observed evidence, inference and limitation.
- If evidence is insufficient, say so.
- Explain why an artifact is prioritized using the supplied factors.
- Never claim that an artifact is fully recovered unless validation and integrity evidence support it.
Return JSON matching the requested schema.
"""

def fallback(context: dict) -> AIReport:
    arts=context.get("artifacts",[])
    if not arts:
        return AIReport(
            executive_summary="No validated artifact candidate was established from the supplied storage evidence.",
            key_findings=["The evidence set contains no candidate that passed the configured validation threshold."],
            artifact_assessments=[],
            recommended_actions=["Inspect fragment graph and lower-confidence candidates manually if appropriate."],
            limitations=["No validated artifact candidate is available."],
            confidence_explanation="Confidence is limited because no validated candidate was produced."
        )
    ordered=sorted(arts,key=lambda x:x.get("priority",{}).get("score",0),reverse=True)
    findings=[]
    assessments=[]
    for a in ordered[:5]:
        p=a.get("priority",{})
        i=a.get("integrity",{})
        findings.append(f"{a.get('format','UNKNOWN')} {a.get('artifact_id','')} has {a.get('recoverability',0)}% estimated recoverability and {p.get('level','LOW')} priority.")
        assessments.append({
            "artifact_id":a.get("artifact_id"),
            "assessment":a.get("integrity",{}).get("validation",{}).get("status","unknown"),
            "priority_reason":p.get("factors",{})
        })
    return AIReport(
        executive_summary=f"{len(arts)} artifact candidate(s) were produced. The highest-priority candidates should be reviewed first.",
        key_findings=findings,
        artifact_assessments=assessments,
        recommended_actions=[
            "Review the top reconstruction candidate and its validation evidence.",
            "Compare alternate reconstruction hypotheses when confidence is not near 100%.",
            "Preserve the original storage image and use hashes for evidence provenance."
        ],
        limitations=[
            "Recoverability is an evidence-derived estimate, not a guarantee.",
            "AI does not reconstruct bytes or replace forensic validation."
        ],
        confidence_explanation="This report is grounded in deterministic fragment, validation, integrity and prioritization outputs."
    )

def investigate(context: dict) -> AIReport:
    settings=get_settings()
    if not settings.ai_enabled or not settings.gemini_api_key:
        return fallback(context)
    try:
        from google import genai
        from google.genai import types
        client=genai.Client(api_key=settings.gemini_api_key)
        schema={
            "type":"object",
            "properties":{
                "executive_summary":{"type":"string"},
                "key_findings":{"type":"array","items":{"type":"string"}},
                "artifact_assessments":{"type":"array","items":{"type":"object"}},
                "recommended_actions":{"type":"array","items":{"type":"string"}},
                "limitations":{"type":"array","items":{"type":"string"}},
                "confidence_explanation":{"type":"string"}
            },
            "required":["executive_summary","key_findings","artifact_assessments","recommended_actions","limitations","confidence_explanation"]
        }
        prompt=SYSTEM_PROMPT+"\nEVIDENCE JSON:\n"+json.dumps(context,default=str)[:120000]
        response=client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.1
            )
        )
        return AIReport.model_validate_json(response.text)
    except Exception:
        return fallback(context)
