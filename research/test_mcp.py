#!/usr/bin/env python3
"""Smoke-test the MCP server over real stdio. It is easy for a stray print in
aivis.py to pollute the JSON-RPC stream and break every client silently."""
import json, subprocess, sys, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
     "params": {"name": "check_ai_visibility", "arguments": {}}},
]
p = subprocess.run([sys.executable, os.path.join(HERE, "aivis_mcp.py")],
                   input="\n".join(json.dumps(m) for m in msgs),
                   capture_output=True, text=True, timeout=120)
fail = False
lines = [l for l in p.stdout.splitlines() if l.strip()]
for l in lines:
    try:
        json.loads(l)
    except Exception:
        print(f"FAIL: non-JSON on stdout (would break every MCP client): {l[:80]!r}")
        fail = True
by_id = {}
for l in lines:
    try:
        d = json.loads(l)
        if d.get("id") is not None:
            by_id[d["id"]] = d
    except Exception:
        pass
if "serverInfo" not in by_id.get(1, {}).get("result", {}):
    print("FAIL: initialize did not return serverInfo"); fail = True
else:
    print("ok: initialize")
tools = by_id.get(2, {}).get("result", {}).get("tools", [])
if not any(t.get("name") == "check_ai_visibility" for t in tools):
    print("FAIL: tools/list missing check_ai_visibility"); fail = True
else:
    print("ok: tools/list")
if not by_id.get(3, {}).get("result", {}).get("isError"):
    print("FAIL: missing-arg call should report isError"); fail = True
else:
    print("ok: error handling")
sys.exit(1 if fail else 0)
