import hashlib, math

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c/n) * math.log2(c/n) for c in counts if c)

def zero_ratio(data: bytes) -> float:
    return (data.count(0) / len(data)) if data else 1.0

def printable_ratio(data: bytes) -> float:
    return (sum(32 <= b < 127 or b in (9,10,13) for b in data) / len(data)) if data else 0.0

def clamp(v: float, lo=0.0, hi=1.0) -> float:
    return max(lo, min(hi, v))

def norm_distance(a: float, b: float, scale: float = 1.0) -> float:
    return clamp(1.0 - abs(a-b)/scale)
