from .utils import clamp

CATEGORY_VALUE={
    "DOCUMENT":.90,"DATABASE":.95,"IMAGE":.75,"VIDEO":.80,"AUDIO":.60,
    "ARCHIVE":.70,"EXECUTABLE":.65,"OTHER":.35
}

def prioritize(artifact):
    value=CATEGORY_VALUE.get(artifact.get("category","OTHER"),.35)
    recover=artifact.get("recoverability",0)/100
    integrity=artifact.get("integrity",{}).get("structural_integrity_percent",0)/100
    confidence=artifact.get("reconstruction_confidence",0)
    rarity=1.0 if artifact.get("fragment_count",0)<=5 else .75 if artifact.get("fragment_count",0)<=20 else .6
    score=100*(.30*value+.30*recover+.20*integrity+.15*confidence+.05*rarity)
    level="CRITICAL" if score>=85 else "HIGH" if score>=70 else "MEDIUM" if score>=50 else "LOW"
    return {"score":round(score,2),"level":level,"factors":{
        "investigative_value":round(value,3),
        "recoverability":round(recover,3),
        "integrity":round(integrity,3),
        "reconstruction_confidence":round(confidence,3),
        "rarity":round(rarity,3)
    }}
