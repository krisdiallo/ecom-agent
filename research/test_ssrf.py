#!/usr/bin/env python3
"""SSRF regression. aivis runs as an MCP server, so its hostname argument can come
from a model that was fed untrusted text — the classic confused-deputy setup. These
targets must never be fetched, and public ones must still work."""
import importlib.util, sys, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("aivis", os.path.join(HERE, "aivis.py"))
m = importlib.util.module_from_spec(spec)
sys.argv = ["aivis"]
try:
    spec.loader.exec_module(m)
except SystemExit:
    pass

MUST_BLOCK = [
    "http://169.254.169.254/latest/meta-data/",   # cloud metadata
    "http://127.0.0.1/", "http://localhost/", "http://[::1]/",
    "http://10.0.0.1/", "http://192.168.1.1/", "http://172.16.0.1/",
    "file:///etc/passwd", "gopher://x/", "ftp://x/",
    "http://0.0.0.0/",
]
MUST_ALLOW = ["https://example.com/", "http://example.com/robots.txt"]

fail = False
for u in MUST_BLOCK:
    try:
        m.guard_url(u)
        print(f"FAIL: should have blocked {u}")
        fail = True
    except m.BlockedTarget:
        pass
print(f"ok: {len(MUST_BLOCK)} internal/non-http targets blocked")

for u in MUST_ALLOW:
    try:
        m.guard_url(u)
    except m.BlockedTarget as e:
        print(f"FAIL: blocked a legitimate public target {u}: {e}")
        fail = True
print(f"ok: {len(MUST_ALLOW)} public targets allowed")

# get() must fail closed rather than raise
st, _, body = m.get("http://169.254.169.254/")
if st != 0 or body:
    print(f"FAIL: get() did not fail closed on a blocked target: {st}")
    fail = True
else:
    print("ok: get() fails closed on blocked targets")

sys.exit(1 if fail else 0)
