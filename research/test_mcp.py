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
    # offline by design: builds prompts, never queries anything
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
     "params": {"name": "build_recommendation_test",
                "arguments": {"brand": "Acme", "category": "wool socks"}}},
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
for want in ("check_ai_visibility", "build_recommendation_test"):
    if not any(t.get("name") == want for t in tools):
        print(f"FAIL: tools/list missing {want}"); fail = True
if not fail:
    print(f"ok: tools/list ({len(tools)} tools)")
if not by_id.get(3, {}).get("result", {}).get("isError"):
    print("FAIL: missing-arg call should report isError"); fail = True
else:
    print("ok: error handling")
rt = by_id.get(4, {}).get("result", {}).get("structuredContent") or {}
if len(rt.get("prompts") or []) != 10:
    print("FAIL: build_recommendation_test did not return 10 prompts"); fail = True
elif sum(1 for p in rt["prompts"] if p["type"] == "unprompted") != 8:
    print("FAIL: expected 8 unprompted prompts (brand-named ones measure recall, not "
          "recommendation, and must not be averaged in)"); fail = True
elif any(rt["brand"].lower() in p["prompt"].lower()
         for p in rt["prompts"] if p["type"] == "unprompted"):
    print("FAIL: an 'unprompted' prompt leaks the brand name, which would measure "
          "recall instead of recommendation"); fail = True
else:
    print("ok: recommendation protocol (10 prompts, 8 brand-free)")

sys.exit(1 if fail else 0)
