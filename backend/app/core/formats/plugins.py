from .base import FormatPlugin, FragmentAnalysis, ValidationResult
from ..utils import clamp, norm_distance
import io, struct, zlib, zipfile

def _has(data: bytes, x: bytes) -> bool:
    return data.find(x) >= 0

class JPEGPlugin(FormatPlugin):
    name, category = "JPEG", "IMAGE"
    def detect(self, d):
        return 1.0 if d.startswith(b"\xff\xd8\xff") else (0.35 if b"\xff\xd8\xff" in d[:64] else 0.0)
    def analyze_fragment(self,d):
        if d.startswith(b"\xff\xd8\xff"): return FragmentAnalysis(self.name,"START",1.0)
        if b"\xff\xd9" in d: return FragmentAnalysis(self.name,"END_OR_DATA",0.85)
        if b"\xff\xda" in d: return FragmentAnalysis(self.name,"SCAN_BOUNDARY",0.9)
        if any(x in d for x in (b"\xff\xdb",b"\xff\xc4",b"\xff\xc0",b"\xff\xc2")):
            return FragmentAnalysis(self.name,"STRUCTURAL",0.88)
        if d and sum(32 <= b < 127 for b in d)/len(d) < .35:
            return FragmentAnalysis(self.name,"ENTROPY",0.62,{"entropy": min(1.0, _entropy(d)/8)})
        return None
    def transition_score(self,l,r):
        # JPEG fragment adjacency is dominated by marker continuity and entropy similarity.
        end = 1.0 if b"\xff\xd9" not in l else 0.0
        start = 0.0 if r.startswith(b"\xff\xd8") else 1.0
        marker = 0.85 if any(x in l[-16:] for x in (b"\xff\xda",b"\xff\xc4",b"\xff\xdb")) else 0.55
        e = norm_distance(_entropy(l),_entropy(r),8)
        score = clamp(.35*end + .25*start + .20*marker + .20*e)
        return score, {"marker_continuity":marker,"entropy_continuity":e,"boundary_validity":end}
    def validate(self,d):
        reasons=[]
        if not d.startswith(b"\xff\xd8\xff"): return ValidationResult(False,0.05,"invalid",["missing JPEG SOI"])
        if b"\xff\xd9" not in d: reasons.append("missing EOI")
        else: reasons.append("EOI present")
        try:
            from PIL import Image
            im=Image.open(io.BytesIO(d)); im.verify()
            im=Image.open(io.BytesIO(d)); im.load()
            reasons += [f"decoder accepted {im.width}x{im.height}", f"mode={im.mode}"]
            return ValidationResult(True, .95 if b"\xff\xd9" in d else .65, "decoder_valid", reasons, {"width":im.width,"height":im.height,"mode":im.mode})
        except Exception as e:
            return ValidationResult(False,.35,"decoder_rejected",reasons+[str(e)])

class PNGPlugin(FormatPlugin):
    name, category = "PNG", "IMAGE"
    sig=b"\x89PNG\r\n\x1a\n"
    def detect(self,d): return 1.0 if d.startswith(self.sig) else (.4 if self.sig in d[:64] else 0)
    def analyze_fragment(self,d):
        if d.startswith(self.sig): return FragmentAnalysis(self.name,"START",1.0)
        if b"IEND" in d: return FragmentAnalysis(self.name,"END",.95)
        if b"IDAT" in d: return FragmentAnalysis(self.name,"DATA",.9)
        if any(x in d for x in (b"IHDR",b"PLTE",b"tEXt")): return FragmentAnalysis(self.name,"STRUCTURAL",.85)
        return None
    def transition_score(self,l,r):
        if l[-4:] in (b"IEND",): return 0.0, {"end_boundary":0.0}
        crc = 1.0 if len(r)>=8 else .2
        return .65*crc + .35*(1.0 if b"IDAT" in l or b"IDAT" in r else .5), {"chunk_continuity":crc}
    def validate(self,d):
        if not d.startswith(self.sig): return ValidationResult(False,.0,"invalid",["missing PNG signature"])
        pos=8; chunks=0; reasons=[]
        try:
            while pos+12<=len(d):
                n=struct.unpack(">I",d[pos:pos+4])[0]
                typ=d[pos+4:pos+8]
                end=pos+12+n
                if end>len(d): return ValidationResult(False,.35,"truncated",[f"truncated {typ.decode(errors='ignore')} chunk"])
                payload=d[pos+8:pos+8+n]; stored=struct.unpack(">I",d[pos+8+n:end])[0]
                calc=zlib.crc32(typ+payload)&0xffffffff
                if calc!=stored: return ValidationResult(False,.55,"crc_mismatch",[f"CRC mismatch in {typ!r}"])
                chunks+=1; pos=end
                if typ==b"IEND":
                    return ValidationResult(True,.98,"valid",["signature valid","all CRCs valid","IEND present"],{"chunks":chunks})
            return ValidationResult(False,.45,"missing_iend",["IEND not reached"])
        except Exception as e: return ValidationResult(False,.2,"parse_error",[str(e)])

class GIFPlugin(FormatPlugin):
    name, category="GIF","IMAGE"
    def detect(self,d): return 1.0 if d.startswith((b"GIF87a",b"GIF89a")) else 0
    def analyze_fragment(self,d):
        if d.startswith((b"GIF87a",b"GIF89a")): return FragmentAnalysis(self.name,"START",1)
        if b"\x3b" in d: return FragmentAnalysis(self.name,"END_OR_DATA",.75)
        if b"\x2c" in d: return FragmentAnalysis(self.name,"IMAGE_DATA",.8)
        return None
    def transition_score(self,l,r): return .65, {"format_continuity":.65}
    def validate(self,d):
        if not self.detect(d): return ValidationResult(False,.05,"invalid",["missing GIF header"])
        if d.endswith(b"\x3b") or b"\x3b" in d[-8:]: return ValidationResult(True,.9,"valid",["GIF trailer present"])
        return ValidationResult(False,.55,"incomplete",["GIF trailer not found"])

class PDFPlugin(FormatPlugin):
    name, category="PDF","DOCUMENT"
    def detect(self,d): return 1.0 if d.startswith(b"%PDF-") else (.45 if b"%PDF-" in d[:128] else 0)
    def analyze_fragment(self,d):
        if d.startswith(b"%PDF-"): return FragmentAnalysis(self.name,"START",1)
        if b"%%EOF" in d: return FragmentAnalysis(self.name,"END",.98)
        if b"obj" in d or b"xref" in d or b"trailer" in d: return FragmentAnalysis(self.name,"STRUCTURAL",.82)
        return None
    def transition_score(self,l,r):
        eof=0.0 if b"%%EOF" in l[-64:] else 1.0
        structure=1.0 if (b"obj" in l or b"stream" in l or b"xref" in l or b"obj" in r) else .55
        return clamp(.55*eof+.45*structure), {"eof_continuity":eof,"pdf_structure":structure}
    def validate(self,d):
        if not d.startswith(b"%PDF-"): return ValidationResult(False,.05,"invalid",["missing PDF header"])
        eof=b"%%EOF" in d[-2048:]
        objs=d.count(b" obj"); xref=d.count(b"xref"); trailer=d.count(b"trailer")
        score=.55 + .15*min(1,objs/3)+.10*min(1,xref)+.10*min(1,trailer)+.10*eof
        return ValidationResult(score>=.75,score,"valid" if score>=.75 else "incomplete",
                                [f"objects={objs}",f"xref_sections={xref}",f"trailers={trailer}",f"EOF={eof}"])

class ZIPPlugin(FormatPlugin):
    name, category="ZIP","ARCHIVE"
    def detect(self,d): return 1.0 if d.startswith(b"PK\x03\x04") else (.7 if b"PK\x03\x04" in d[:256] else 0)
    def analyze_fragment(self,d):
        if d.startswith(b"PK\x03\x04"): return FragmentAnalysis(self.name,"LOCAL_HEADER",.98)
        if b"PK\x01\x02" in d: return FragmentAnalysis(self.name,"CENTRAL_DIRECTORY",.95)
        if b"PK\x05\x06" in d: return FragmentAnalysis(self.name,"END",1)
        return None
    def transition_score(self,l,r):
        return .8, {"zip_structure":.8}
    def validate(self,d):
        try:
            with zipfile.ZipFile(io.BytesIO(d)) as z:
                bad=z.testzip()
                names=z.namelist()
                return ValidationResult(bad is None,.98 if bad is None else .55,
                    "valid" if bad is None else "crc_error",
                    [f"entries={len(names)}",f"first_bad={bad}"],{"entries":names[:50]})
        except Exception as e:
            return ValidationResult(False,.25,"invalid_or_incomplete",[str(e)])

class WAVPlugin(FormatPlugin):
    name, category="WAV","AUDIO"
    def detect(self,d): return 1.0 if d.startswith(b"RIFF") and d[8:12]==b"WAVE" else 0
    def analyze_fragment(self,d):
        if self.detect(d): return FragmentAnalysis(self.name,"START",1)
        if b"fmt " in d: return FragmentAnalysis(self.name,"FORMAT_CHUNK",.9)
        if b"data" in d: return FragmentAnalysis(self.name,"DATA_CHUNK",.9)
        return None
    def transition_score(self,l,r): return .7, {"riff_continuity":.7}
    def validate(self,d):
        if not self.detect(d): return ValidationResult(False,.05,"invalid",["missing RIFF/WAVE"])
        size=struct.unpack("<I",d[4:8])[0] if len(d)>=8 else 0
        return ValidationResult(True if size+8<=len(d) else False,.9 if size+8<=len(d) else .55,
            "valid" if size+8<=len(d) else "truncated",[f"RIFF_declared_size={size}"])

class MP3Plugin(FormatPlugin):
    name, category="MP3","AUDIO"
    def detect(self,d): return 1.0 if d.startswith(b"ID3") or (len(d)>=2 and d[0]==0xff and (d[1]&0xe0)==0xe0) else 0
    def analyze_fragment(self,d):
        if d.startswith(b"ID3"): return FragmentAnalysis(self.name,"ID3_HEADER",1)
        if len(d)>=2 and d[0]==0xff and (d[1]&0xe0)==0xe0: return FragmentAnalysis(self.name,"AUDIO_FRAME",.85)
        return None
    def transition_score(self,l,r): return .68, {"mpeg_frame_continuity":.68}
    def validate(self,d):
        if not self.detect(d): return ValidationResult(False,.05,"invalid",["no MP3 signature"])
        frames=0
        for i in range(len(d)-1):
            if d[i]==0xff and (d[i+1]&0xe0)==0xe0: frames+=1
        return ValidationResult(frames>0,.75 if frames>4 else .45,"valid" if frames>0 else "incomplete",[f"frame_sync_candidates={frames}"])

class MP4Plugin(FormatPlugin):
    name, category="MP4","VIDEO"
    def detect(self,d): return 1.0 if len(d)>=12 and d[4:8]==b"ftyp" else (.5 if b"ftyp" in d[:64] else 0)
    def analyze_fragment(self,d):
        if len(d)>=12 and d[4:8]==b"ftyp": return FragmentAnalysis(self.name,"FTYP",1)
        if b"moov" in d: return FragmentAnalysis(self.name,"MOOV",.95)
        if b"mdat" in d: return FragmentAnalysis(self.name,"MDAT",.9)
        return None
    def transition_score(self,l,r): return .74, {"box_continuity":.74}
    def validate(self,d):
        if len(d)<12 or d[4:8]!=b"ftyp": return ValidationResult(False,.1,"invalid",["missing ftyp"])
        boxes=0; pos=0
        try:
            while pos+8<=len(d):
                size=struct.unpack(">I",d[pos:pos+4])[0]
                typ=d[pos+4:pos+8]
                if size==0: break
                if size<8 or pos+size>len(d): break
                boxes+=1; pos+=size
            has_moov=b"moov" in d; has_mdat=b"mdat" in d
            score=.5+.15*min(1,boxes/4)+.175*has_moov+.175*has_mdat
            return ValidationResult(score>=.8,score,"valid" if score>=.8 else "partial",[f"boxes={boxes}",f"moov={has_moov}",f"mdat={has_mdat}"])
        except Exception as e: return ValidationResult(False,.2,"parse_error",[str(e)])

class EXEPlugin(FormatPlugin):
    name, category="EXE","EXECUTABLE"
    def detect(self,d): return 1.0 if d.startswith(b"MZ") else (.2 if b"MZ" in d[:64] else 0)
    def analyze_fragment(self,d):
        if d.startswith(b"MZ"): return FragmentAnalysis(self.name,"DOS_HEADER",1)
        if b"PE\x00\x00" in d: return FragmentAnalysis(self.name,"PE_HEADER",.98)
        return None
    def transition_score(self,l,r): return .6, {"pe_continuity":.6}
    def validate(self,d):
        if not d.startswith(b"MZ"): return ValidationResult(False,.05,"invalid",["missing MZ"])
        pe=False
        if len(d)>=0x40:
            off=struct.unpack_from("<I",d,0x3c)[0]
            pe=off+4<=len(d) and d[off:off+4]==b"PE\x00\x00"
        return ValidationResult(pe,.95 if pe else .35,"valid" if pe else "partial",["PE header present" if pe else "PE header not found"])

def _entropy(d): 
    if not d: return 0.0
    from collections import Counter
    import math
    c=Counter(d); n=len(d)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

PLUGINS=[JPEGPlugin(),PNGPlugin(),GIFPlugin(),PDFPlugin(),ZIPPlugin(),WAVPlugin(),MP3Plugin(),MP4Plugin(),EXEPlugin()]
REGISTRY={p.name:p for p in PLUGINS}

def detect_formats(data: bytes, threshold=.25):
    out=[]
    for p in PLUGINS:
        s=p.detect(data)
        if s>=threshold: out.append((p,s))
    return sorted(out,key=lambda x:x[1],reverse=True)
