from app.core.formats.plugins import REGISTRY
from app.core.ingestion import blockize
from app.core.utils import entropy
from app.pipeline import analyze_storage

def test_plugins_present():
    assert set(REGISTRY) >= {"JPEG","PNG","GIF","PDF","ZIP","MP3","MP4","WAV","EXE"}

def test_blockize():
    b=blockize(b"abcdef"*100,64)
    assert len(b)>0 and b[0].id==0 and b[0].offset==0

def test_entropy():
    assert entropy(b"\x00"*100)==0
    assert entropy(bytes(range(256)))>7

def test_pipeline_runs():
    result=analyze_storage(b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n%%EOF\n",16,10,2,False)
    assert "metrics" in result
    assert "artifacts" in result
