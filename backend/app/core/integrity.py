from .formats.plugins import REGISTRY
from .utils import clamp, sha256

def assess(data: bytes, plugin, sequence=None, expected_size=None):
    v=plugin.validate(data)
    completeness=1.0
    if expected_size:
        completeness=min(1.0,len(data)/expected_size)
    structural=v.score
    corruption=max(0.0,1-structural)
    recoverability=clamp(.55*structural+.30*completeness+.15*(1-corruption))
    return {
        "status": "recoverable" if recoverability>=.85 else "mostly_recoverable" if recoverability>=.65 else "partially_recoverable" if recoverability>=.4 else "unlikely_recoverable",
        "recoverability_percent": round(recoverability*100,2),
        "structural_integrity_percent": round(structural*100,2),
        "completeness_percent": round(completeness*100,2),
        "estimated_corruption_percent": round(corruption*100,2),
        "sha256": sha256(data),
        "validation": v.__dict__,
    }
