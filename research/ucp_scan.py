#!/usr/bin/env python3
"""
Measure the agent-commerce layer across the same sample as the main survey.

Found 2026-08-28: Shopify stores are serving /llms.txt "Agent Instructions" that
advertise the Universal Commerce Protocol — a live MCP endpoint an AI agent can call
to search the catalogue, build a cart and complete a checkout. This is a machine-readable
commerce API that bypasses HTML parsing entirely, and the original survey missed it
because it only looked at robots.txt and rendered markup.

Read-only. Only ever calls tools/list, which enumerates capabilities. It never creates
a cart, never starts a checkout, and never sends anything that could place an order.
"""
import json, re, sys, time, urllib.request, urllib.error, gzip, io

UA = ("Mozilla/5.0 (compatible; ecom-agent-research/1.0; "
      "+https://github.com/krisdiallo/ecom-agent) agent-commerce survey")


def get(url, timeout=15, data=None, ctype=None):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if ctype:
        h["Content-Type"] = ctype
    req = urllib.request.Request(url, headers=h, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
            return r.status, r.headers.get("Content-Type", ""), raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, "", ""
    except Exception:
        return 0, "", ""


def probe(host):
    out = {"host": host}

    st, ct, body = get(f"https://{host}/llms.txt")
    # A 200 that serves HTML is a soft-404, not an llms.txt.
    real = st == 200 and "html" not in ct.lower() and not re.match(r"\s*<", body or "")
    out["llms_txt"] = bool(real)
    if real:
        out["llms_agent_instructions"] = bool(re.search(r"agent instructions", body, re.I))
        out["llms_mentions_ucp"] = "ucp" in body.lower()
        out["llms_mentions_shop_skill"] = "shop.app/SKILL.md" in body
        out["llms_bytes"] = len(body)

    st, ct, body = get(f"https://{host}/.well-known/ucp")
    if st == 200 and body.strip().startswith("{"):
        try:
            j = json.loads(body)
            u = j.get("ucp", j)
            out["ucp"] = True
            out["ucp_version"] = u.get("version")
            svc = (u.get("services") or {}).get("dev.ucp.shopping") or []
            eps = [s.get("endpoint") for s in svc if s.get("transport") == "mcp"]
            out["ucp_mcp_endpoint"] = eps[0] if eps else None
        except Exception:
            out["ucp"] = False
    else:
        out["ucp"] = False

    ep = out.get("ucp_mcp_endpoint") or f"https://{host}/api/ucp/mcp"
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
    st, ct, body = get(ep, data=payload, ctype="application/json", timeout=20)
    if st == 200 and body.strip().startswith("{"):
        try:
            tools = json.loads(body).get("result", {}).get("tools", [])
            out["mcp_live"] = True
            out["mcp_tools"] = sorted(t.get("name") for t in tools if t.get("name"))
        except Exception:
            out["mcp_live"] = False
    else:
        out["mcp_live"] = False
        out["mcp_status"] = st
    return out


if __name__ == "__main__":
    hosts = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
    res = []
    for i, h in enumerate(hosts, 1):
        r = probe(h)
        res.append(r)
        print(f"[{i}/{len(hosts)}] {h:<30} llms={r['llms_txt']!s:<5} "
              f"ucp={r['ucp']!s:<5} mcp={r['mcp_live']!s:<5} "
              f"tools={len(r.get('mcp_tools') or [])}", flush=True)
        json.dump(res, open(sys.argv[2], "w"), indent=1)
        time.sleep(2.0)
    live = [r for r in res if r.get("mcp_live")]
    print(f"\n{len(live)}/{len(res)} hosts expose a live agent-commerce MCP endpoint")
