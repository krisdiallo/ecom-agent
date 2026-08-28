#!/usr/bin/env python3
"""
aivis-mcp — the AI visibility checker as an MCP server.

Lets any MCP client (Claude Code, Claude Desktop, Cursor, …) check whether AI
assistants can read and transact with a store.

    {
      "mcpServers": {
        "aivis": { "command": "python3", "args": ["/path/to/aivis_mcp.py"] }
      }
    }

Stdio JSON-RPC, standard library only — no pip install, no build step, same as the
CLI it wraps. It shells nothing out: it imports aivis.py directly, so the CLI, the
web tool, the study and this server all share one verified implementation.

Read-only against the sites it inspects. The agent-commerce probe calls only
tools/list, which enumerates capabilities; it never creates a cart or a checkout.

MIT. https://github.com/krisdiallo/ecom-agent
"""
import importlib.util
import io as _io
import json
import os
import sys
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("aivis", os.path.join(HERE, "aivis.py"))
aivis = importlib.util.module_from_spec(_spec)
_argv = sys.argv
sys.argv = ["aivis"]           # aivis.py parses args only under __main__, but be safe
try:
    _spec.loader.exec_module(aivis)
except SystemExit:
    pass
finally:
    sys.argv = _argv

PROTOCOL = "2025-06-18"
TOOLS = [
    {
        "name": "check_ai_visibility",
        "description": (
            "Check whether AI assistants can find, read and transact with an ecommerce "
            "store. Three checks: (1) robots.txt, distinguishing crawlers whose blocking "
            "removes you from AI answers (OAI-SearchBot, PerplexityBot, Claude-SearchBot, "
            "Amzn-SearchBot, Applebot) from training-only crawlers where blocking costs "
            "nothing (GPTBot, ClaudeBot, Google-Extended); (2) product page RAW HTML — not "
            "the rendered DOM, because most AI crawlers do not run JavaScript — covering "
            "structured data, offer completeness and how many concrete measurements the "
            "page gives; (3) the agent-commerce layer (Universal Commerce Protocol / MCP), "
            "which decides whether an agent can actually buy rather than merely describe. "
            "Read-only: nothing is created, purchased or uploaded."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "store": {"type": "string",
                          "description": "Store domain, e.g. 'allbirds.com'."},
                "url": {"type": "string",
                        "description": "Optional specific product page URL to check."},
                "pages": {"type": "integer", "minimum": 1, "maximum": 25, "default": 1,
                          "description": "Sample N product pages to see whether a problem "
                                         "is systemic rather than a one-off."},
            },
            "required": ["store"],
        },
    }
]


def run_check(args):
    store = (args.get("store") or "").strip()
    if not store:
        raise ValueError("store is required")
    host = aivis.re.sub(r"^https?://", "", store).strip("/").split("/")[0]
    aivis.paint(False)
    rep = aivis.R(quiet=True)
    # aivis writes progress to stdout; stdout is the JSON-RPC channel here, so capture it.
    buf = _io.StringIO()
    with contextlib.redirect_stdout(buf):
        aivis.check_robots(host, rep)
        pages = int(args.get("pages") or 1)
        if pages > 1 and not args.get("url"):
            aivis.check_catalogue(host, rep, min(pages, 25))
        else:
            aivis.check_product(host, rep, args.get("url"))
        aivis.check_agent_commerce(host, rep)
    return {"host": host, "critical": rep.bad, "warnings": rep.warn,
            "passed": rep.ok, "findings": rep.findings}


def as_text(r):
    lines = [f"AI visibility for {r['host']}",
             f"{r['critical']} critical · {r['warnings']} to review · {r['passed']} passed", ""]
    mark = {"bad": "FAIL", "warn": "WARN", "ok": "OK", "note": "note"}
    for f in r["findings"]:
        lines.append(f"[{mark.get(f['level'], f['level'])}] {f['title']}")
        if f.get("detail"):
            lines.append(f"    {f['detail']}")
    lines += ["", "This cannot tell you whether an assistant WILL recommend the store — "
                  "nobody can; rankings are not public and vary by wording. It checks "
                  "whether the store is readable and transactable at all."]
    return "\n".join(lines)


def handle(msg):
    m, mid = msg.get("method"), msg.get("id")
    if m == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "aivis", "version": aivis.__version__}}}
    if m in ("notifications/initialized", "notifications/cancelled"):
        return None
    if m == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if m == "tools/call":
        p = msg.get("params") or {}
        if p.get("name") != "check_ai_visibility":
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"unknown tool {p.get('name')!r}"}}
        try:
            r = run_check(p.get("arguments") or {})
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"check failed: {type(e).__name__}: {e}"}],
                "isError": True}}
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": as_text(r)}],
            "structuredContent": r}}
    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": f"method not found: {m}"}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        try:
            out = handle(msg)
        except Exception as e:
            out = {"jsonrpc": "2.0", "id": msg.get("id"),
                   "error": {"code": -32603, "message": str(e)}}
        if out is not None:
            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, BrokenPipeError):
        pass
