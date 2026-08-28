#!/usr/bin/env python3
"""Assert an MCP server's stdio output is a valid handshake with the expected tools.

Parses rather than greps. The first version of this gate grepped for '"name":"aivis"'
and failed a perfectly good image, because json.dumps emits '"name": "aivis"' with a
space. A brittle assertion that fails on working software is worse than none — it
teaches you to ignore the gate.
"""
import json, sys

path = sys.argv[1] if len(sys.argv) > 1 else "out.jsonl"
want_tools = set(sys.argv[2:]) or {"check_ai_visibility", "build_recommendation_test"}

got = {}
for line in open(path):
    line = line.strip()
    if not line:
        continue
    got.update(json.loads(line).get("result", {}))   # non-JSON on stdout is a failure

info = got.get("serverInfo") or {}
if info.get("name") != "aivis":
    print(f"FAIL: serverInfo missing or wrong: {info!r}")
    sys.exit(1)
names = {t.get("name") for t in got.get("tools", [])}
missing = want_tools - names
if missing:
    print(f"FAIL: missing tools {sorted(missing)} (got {sorted(names)})")
    sys.exit(1)
print(f"ok: serves {len(names)} tools as {info}")
