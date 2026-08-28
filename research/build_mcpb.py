#!/usr/bin/env python3
"""Build the .mcpb bundle: a zip of manifest.json + the server and its one import.

Deliberately trivial — no toolchain, no packaging deps — because the whole point of
this project is that the checker is a single stdlib-only file.

The build is REPRODUCIBLE. A plain zipfile.write() stamps each entry with the file's
mtime, so every rebuild produced different bytes and the sha256 that server.json pins
was meaningless — the publish gate caught exactly that. Fixed timestamps and fixed
permissions mean anyone can rebuild from source and confirm, byte for byte, that the
artifact in the release is the code in the repo.
"""
import hashlib, json, os, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "aivis.mcpb")
EPOCH = (1980, 1, 1, 0, 0, 0)   # earliest value the zip format can represent
os.makedirs(os.path.dirname(OUT), exist_ok=True)

man = json.load(open(os.path.join(ROOT, "mcpb", "manifest.json")))
src = open(os.path.join(ROOT, "aivis.py")).read()
ver = src.split('__version__ = "')[1].split('"')[0]
if man["version"] != ver:
    man["version"] = ver
    json.dump(man, open(os.path.join(ROOT, "mcpb", "manifest.json"), "w"), indent=2)
    print(f"manifest version synced to aivis {ver}")


def add(z, arcname, data):
    zi = zipfile.ZipInfo(arcname, date_time=EPOCH)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.external_attr = 0o644 << 16
    z.writestr(zi, data)


with zipfile.ZipFile(OUT, "w") as z:
    add(z, "manifest.json", json.dumps(man, indent=2))
    for f in ("aivis_mcp.py", "aivis.py"):
        add(z, f"server/{f}", open(os.path.join(ROOT, f), "rb").read())
    add(z, "LICENSE", open(os.path.join(ROOT, "LICENSE"), "rb").read())

sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
open(os.path.join(ROOT, "dist", "aivis.mcpb.sha256"), "w").write(sha + "\n")
print(f"built {OUT}")
print(f"  size    {os.path.getsize(OUT)} bytes")
print(f"  sha256  {sha}")
print(f"  version {man['version']}")
