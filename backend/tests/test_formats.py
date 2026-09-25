from app.core.formats.plugins import REGISTRY

def test_png_validator():
    p=REGISTRY["PNG"]
    # Signature-only data should be rejected, not crash.
    assert not p.validate(b"\x89PNG\r\n\x1a\n").valid

def test_pdf_detector():
    assert REGISTRY["PDF"].detect(b"%PDF-1.7") == 1.0

def test_exe_detector():
    assert REGISTRY["EXE"].detect(b"MZ"+b"\x00"*20) == 1.0

def test_wav_detector():
    assert REGISTRY["WAV"].detect(b"RIFF"+b"\x00\x00\x00\x00"+b"WAVE") == 1.0
