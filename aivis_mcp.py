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
    },
    {
        "name": "build_recommendation_test",
        "description": (
            "Generate the prompt set for testing whether AI assistants actually recommend "
            "a brand in its category, plus a scoring rubric. This tool does NOT query any "
            "assistant — it cannot, and any tool claiming a definitive 'AI ranking' is ahead "
            "of the evidence, because rankings are not public and vary by wording, location "
            "and session. What it does is remove the part that does not scale: writing "
            "varied, non-leading prompts and scoring the answers consistently. If you (the "
            "calling assistant) can search the web, run these yourself and report the results "
            "back to the user. Otherwise hand them to the user to run monthly."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand": {"type": "string", "description": "Brand name, e.g. 'Allbirds'."},
                "category": {"type": "string",
                             "description": "What they sell, in the words a buyer would use, "
                                            "e.g. 'merino wool sneakers'."},
                "market": {"type": "string",
                           "description": "Optional market/locale, e.g. 'UK'. Answers vary by "
                                          "location, so a result is only comparable within one."},
            },
            "required": ["brand", "category"],
        },
    },
]


def build_recommendation_test(args):
    brand = (args.get("brand") or "").strip()
    cat = (args.get("category") or "").strip()
    if not brand or not cat:
        raise ValueError("brand and category are required")
    mk = (args.get("market") or "").strip()
    loc = f" in the {mk}" if mk else ""

    # Deliberately varied in shape: a single phrasing is not a benchmark, and prompts
    # that name the brand test recall rather than recommendation. Only the last two
    # mention it, and they are scored separately for that reason.
    prompts = [
        f"What's the best {cat}{loc}?",
        f"Where should I buy {cat}{loc}?",
        f"Recommend a few brands for {cat}{loc}.",
        f"I'm shopping for {cat}{loc} — what are my options?",
        f"What's the most durable {cat} you'd recommend?",
        f"Best value {cat} under a typical budget{loc}?",
        f"Which {cat} brands do people actually rate?",
        f"Compare the top {cat} brands{loc}.",
        f"Is {brand} a good choice for {cat}?",
        f"How does {brand} compare to other {cat} brands?",
    ]
    return {
        "brand": brand, "category": cat, "market": mk or None,
        "prompts": [{"n": i + 1, "prompt": p,
                     "type": "unprompted" if i < 8 else "brand-named"}
                    for i, p in enumerate(prompts)],
        "scoring": {
            "mentioned": "Did the answer name the brand at all?",
            "position": "First, in the main list, or only an aside?",
            "accurate": "Was everything it said about the brand true? Log any invented claim "
                        "verbatim — a confident wrong fact is worse than being absent.",
            "sources": "Which pages did it cite? Those are the pages actually doing the work.",
            "competitors": "Which brands appeared instead? That gap is usually more actionable "
                           "than your own score.",
        },
        "method_notes": [
            "Prompts 1-8 never name the brand. Those measure recommendation. Prompts 9-10 do "
            "name it, and measure only recall and accuracy — do not average the two groups.",
            "Re-run monthly and compare the trend, not a single reading. One prompt is not a "
            "benchmark.",
            "Answers vary by location and session. Results are comparable only within one "
            "market and one assistant.",
            "This measures what assistants say, not why. The mechanical prerequisites — "
            "crawler access, readable facts, agent-commerce — are what check_ai_visibility "
            "covers.",
        ],
        "disclaimer": "No tool can tell you whether an assistant WILL recommend you. Rankings "
                      "are not public. This is a repeatable measurement protocol, not a score.",
    }


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


def protocol_text(r):
    mk = f" ({r['market']})" if r.get("market") else ""
    out = [f"Recommendation test for {r['brand']} — {r['category']}{mk}", "",
           "Run these and log the result for each. Prompts 1-8 never name the brand and "
           "measure recommendation; 9-10 name it and measure only recall and accuracy.", ""]
    for p in r["prompts"]:
        out.append(f"  {p['n']:>2}. [{p['type']}] {p['prompt']}")
    out += ["", "Score each answer on:"]
    for k, v in r["scoring"].items():
        out.append(f"  - {k}: {v}")
    out += ["", "Method:"] + [f"  - {n}" for n in r["method_notes"]]
    out += ["", r["disclaimer"]]
    return "\n".join(out)


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
        name = p.get("name")
        handlers = {"check_ai_visibility": (run_check, as_text),
                    "build_recommendation_test": (build_recommendation_test, protocol_text)}
        if name not in handlers:
            return {"jsonrpc": "2.0", "id": mid,
                    "error": {"code": -32602, "message": f"unknown tool {name!r}"}}
        fn, fmt = handlers[name]
        try:
            r = fn(p.get("arguments") or {})
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": f"{name} failed: {type(e).__name__}: {e}"}],
                "isError": True}}
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": fmt(r)}],
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
