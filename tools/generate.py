#!/usr/bin/env python3
"""Generate an original, warm four-variation Clink sound pack."""
import base64
import hashlib
import io
import json
import math
import os
import pathlib
import random
import struct
import wave

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOUNDS = ROOT / "Sounds"
NAME = "v8-calido"
RATE = 44100

def sample(seed):
    rng = random.Random(seed)
    count = int(RATE * 0.090)
    data = []
    low = 0.0
    for i in range(count):
        t = i / RATE
        low = 0.86 * low + 0.14 * rng.uniform(-1, 1)
        attack = min(1.0, t / 0.0015)
        body = math.sin(2 * math.pi * (165 + 7 * seed) * t) * math.exp(-t * 66)
        tap = low * math.exp(-t * 110)
        texture = rng.uniform(-1, 1) * math.exp(-t * 280)
        value = (0.50 * body + 0.24 * tap + 0.09 * texture) * attack
        data.append(max(-0.72, min(0.72, value)))
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(b"".join(struct.pack("<h", round(x * 32767)) for x in data))
    return base64.b64encode(out.getvalue()).decode("ascii")

def main():
    SOUNDS.mkdir(exist_ok=True)
    names = [f"v8-calido-{i}" for i in range(1, 5)]
    pack = {
        "pack": {
            "id": NAME,
            "name": "V8 Cálido",
            "blurb": "Original warm, short and soft mechanical key taps.",
            "sampleNames": names,
            "fileExtension": "wav",
            "gain": 0.75,
            "source": "bundled"
        },
        "samples": [sample(i) for i in range(1, 5)]
    }
    path = SOUNDS / f"{NAME}.clinkpack"
    raw = (json.dumps(pack, ensure_ascii=False, indent=2) + "\n").encode()
    path.write_bytes(raw)
    version = "v8-calido-" + hashlib.sha256(raw).hexdigest()[:16]
    repo = os.environ.get("GITHUB_REPOSITORY", "JacsNN/clink-v8-calido")
    manifest = {
        "version": version,
        "sounds": [{
            "id": NAME,
            "name": "V8 Cálido",
            "version": version,
            "asset": {
                "path": path.name,
                "url": f"https://github.com/{repo}/releases/download/{version}/{path.name}",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byteCount": len(raw)
            },
            "platform": "android"
        }]
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    for encoded in pack["samples"]:
        with wave.open(io.BytesIO(base64.b64decode(encoded)), "rb") as w:
            assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 44100)
            assert w.getnframes() <= RATE // 2
    assert len(pack["samples"]) <= 4
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["sounds"][0]["asset"]["sha256"]
    print(f"Validated {len(pack['samples'])} original samples; release {version}")

if __name__ == "__main__":
    main()
