FILE_SIGNATURES = {
    "PDF": {
        "header": b"%PDF",
        "footer": b"%%EOF",
        "extension": ".pdf",
        "mime_type": "application/pdf",
        "category": "document",
    },

    "JPEG": {
        "header": b"\xFF\xD8\xFF",
        "footer": b"\xFF\xD9",
        "extension": ".jpg",
        "mime_type": "image/jpeg",
        "category": "image",
    },

    "PNG": {
        "header": b"\x89PNG\r\n\x1a\n",
        "footer": b"\x49\x45\x4E\x44\xAE\x42\x60\x82",
        "extension": ".png",
        "mime_type": "image/png",
        "category": "image",
    },

    "GIF": {
        "header": b"GIF8",
        "footer": b"\x3B",
        "extension": ".gif",
        "mime_type": "image/gif",
        "category": "image",
    },

    "ZIP": {
        "header": b"PK\x03\x04",
        "extension": ".zip",
        "mime_type": "application/zip",
        "category": "archive",
    },

    "MP3_ID3": {
        "header": b"ID3",
        "extension": ".mp3",
        "mime_type": "audio/mpeg",
        "category": "audio",
    },

    "MP4": {
        "header": b"ftyp",
        "extension": ".mp4",
        "mime_type": "video/mp4",
        "category": "video",
    },

    "WAV": {
        "header": b"RIFF",
        "extension": ".wav",
        "mime_type": "audio/wav",
        "category": "audio",
    },

    "EXE": {
        "header": b"MZ",
        "extension": ".exe",
        "mime_type": "application/vnd.microsoft.portable-executable",
        "category": "executable",
    },
}