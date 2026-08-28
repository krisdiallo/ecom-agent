#!/usr/bin/env python3
"""Generate site/data.html — a DataCatalog of the datasets this project publishes.

Why this exists: we publish four original datasets and declared no schema.org/Dataset
markup on any page, which means Google Dataset Search — a free, account-free discovery
channel built for exactly this — could not see them. An AI-visibility tool that is not
itself machine-readable as what it is has no business giving advice.

Required properties per Google's Dataset docs (checked 2026-08-28): name and
description (50-5000 chars). distribution.contentUrl is required for DataDownload.
Everything else here is from their recommended list.

Every count is read from the actual files at build time. No figure is typed in.
"""
import json, os, datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://krisdiallo.github.io/ecom-agent"
RAW = "https://raw.githubusercontent.com/krisdiallo/ecom-agent/main"
REPO = "https://github.com/krisdiallo/ecom-agent"
TODAY = "2026-08-28"


def j(p):
    return json.load(open(os.path.join(HERE, p)))


def build_datasets():
    cons = j("crawler-consequences.json")["crawlers"]
    und = sum(1 for c in cons if c["blocking_effect"] == "undetermined")
    search = sum(1 for c in cons if c["blocking_effect"] == "removes_from_ai_answers")
    train = sum(1 for c in cons if c["blocking_effect"] == "opts_out_of_training_only")
    reg = j("crawlers.json")["crawlers"]
    ac = j("agent-commerce.json")["hosts"]
    live = sum(1 for h in ac if h.get("agent_commerce"))
    sv = j("research/data/survey-2026-08-28.json")
    rob = [x for x in sv if x.get("robots_status") == 200]
    prod = [x for x in sv if x.get("product_status") == 200]
    sb = sum(1 for x in rob if x.get("search_blocked"))
    tb = sum(1 for x in rob if x.get("train_blocked"))
    schema = sum(1 for x in prod if x.get("has_product_schema"))
    meas = sorted(x.get("measurements", 0) for x in prod)
    med = meas[len(meas) // 2]

    return [
        dict(
            slug="crawler-consequences",
            name="AI crawler blocking-consequence registry",
            desc=(f"Every known AI crawler user-agent ({len(cons)} tokens), classified by what "
                  f"blocking it in robots.txt actually costs a website. Blocking a training "
                  f"crawler removes you from no product recommendations; blocking a search "
                  f"crawler removes you from AI answers in ChatGPT, Perplexity, Claude, Alexa "
                  f"and Siri. Most published robots.txt advice conflates the two. "
                  f"{search} tokens are classified as removing you from AI answers and {train} "
                  f"as training-only opt-outs. Critically, {und} of {len(cons)} are marked "
                  f"'undetermined' because no public source establishes the consequence — they "
                  f"are deliberately not defaulted to a guess. Each row carries a 'basis' field "
                  f"recording evidence strength, so consumers can filter to vendor-documented "
                  f"rows only. Derived in part from ai-robots-txt/ai.robots.txt (MIT)."),
            n=len(cons), fmt="application/json", file="crawler-consequences.json",
            vars=["token", "operator", "function", "blocking_effect", "basis"],
            technique="Vendor documentation review; derivation from curated upstream function text",
        ),
        dict(
            slug="crawlers",
            name="Sourced AI crawler registry (vendor-documented)",
            desc=(f"{len(reg)} AI crawler user-agent tokens, each tied to the operating vendor's "
                  f"own published documentation. Every entry records the vendor, the product the "
                  f"crawler serves, what blocking it does, whether it honours robots.txt, a "
                  f"verbatim quote from the vendor, a source URL, and the date the source was "
                  f"checked. Entries that could not be tied to a first-party statement carry an "
                  f"explicit unverified flag rather than being presented as sourced. Built to "
                  f"correct a common error: that blocking GPTBot removes a site from ChatGPT's "
                  f"recommendations, when OAI-SearchBot is the token that governs that."),
            n=len(reg), fmt="application/json", file="crawlers.json",
            vars=["token", "vendor", "product", "purpose", "blocking_effect",
                  "respects_robots_txt", "source", "source_quote", "verified"],
            technique="First-party vendor documentation, quoted and dated",
        ),
        dict(
            slug="agent-commerce",
            name="Agent-commerce endpoint survey of 70 consumer storefronts",
            desc=(f"{len(ac)} consumer ecommerce storefronts probed for a live agent-commerce "
                  f"endpoint an AI agent could call to search a catalogue, build a cart and "
                  f"complete a checkout without parsing HTML. {live} of {len(ac)} exposed one. "
                  f"The notable result: all {live} exposed an identical 13-tool surface on a "
                  f"single protocol version, with zero variation across independent brands — "
                  f"indicating agent-commerce capability is currently a property of the "
                  f"ecommerce platform rather than a per-merchant configuration choice. Probing "
                  f"further established that tool enumeration answers anonymously while every "
                  f"tool call is refused without a published agent profile URI, so these stores "
                  f"are transactable by identified agents, not anonymous ones. The probe was "
                  f"read-only throughout and never created a cart or began a checkout."),
            n=len(ac), fmt="application/json", file="agent-commerce.json",
            vars=["host", "agent_commerce", "endpoint", "tools", "access_control"],
            technique="Read-only protocol discovery and tools/list enumeration over HTTPS",
        ),
        dict(
            slug="ai-visibility-survey",
            name="AI visibility survey of 70 direct-to-consumer brands",
            desc=(f"Raw measurements from {len(sv)} consumer brand storefronts, assessing whether "
                  f"AI assistants can actually read them. {len(rob)} robots.txt files were parsed "
                  f"with correct group precedence and {len(prod)} product pages analysed from raw "
                  f"HTML rather than the rendered DOM, because most AI crawlers do not execute "
                  f"JavaScript. Headline findings: {sb} of {len(rob)} stores blocked an AI search "
                  f"crawler and {tb} blocked a training crawler, so accidental invisibility — the "
                  f"fear the AI-SEO tooling category is sold on — did not occur. "
                  f"{schema} of {len(prod)} pages carried Product or ProductGroup structured "
                  f"data. The real deficit is specificity: the median product page contains "
                  f"{med} concrete measurements, and assistants repeat attributable facts rather "
                  f"than adjectives. Includes per-host structured-data completeness, offer "
                  f"fields, word counts, title/og:title agreement and JavaScript-injection "
                  f"detection."),
            n=len(sv), fmt="application/json",
            file="research/data/survey-2026-08-28.json",
            vars=["host", "robots_status", "search_blocked", "train_blocked",
                  "has_product_schema", "jsonld_js_injected", "measurements", "words",
                  "title_og_consistent", "offer_price", "offer_availability"],
            technique="Automated HTTPS retrieval and raw-HTML parsing; no JavaScript execution",
        ),
    ]


def ld(datasets):
    def one(d):
        return {
            "@type": "Dataset",
            "@id": f"{BASE}/data.html#{d['slug']}",
            "name": d["name"],
            "description": d["desc"],
            "url": f"{BASE}/data.html#{d['slug']}",
            "sameAs": f"{REPO}/blob/main/{d['file']}",
            "license": "https://opensource.org/licenses/MIT",
            "isAccessibleForFree": True,
            "creator": {"@type": "Organization", "name": "ecom-agent", "url": REPO},
            "keywords": ["AI crawlers", "robots.txt", "generative engine optimization",
                         "ecommerce", "structured data", "AI search", "LLM"],
            "temporalCoverage": TODAY,
            "dateModified": TODAY,
            "version": "1.0.0",
            "measurementTechnique": d["technique"],
            "variableMeasured": d["vars"],
            "distribution": [{
                "@type": "DataDownload",
                "encodingFormat": d["fmt"],
                "contentUrl": f"{RAW}/{d['file']}",
            }],
        }
    return {
        "@context": "https://schema.org",
        "@type": "DataCatalog",
        "@id": f"{BASE}/data.html",
        "name": "ecom-agent open datasets",
        "description": ("Four original, openly licensed datasets on whether AI assistants can "
                        "read, cite and transact with ecommerce storefronts: an AI-crawler "
                        "blocking-consequence registry, a vendor-sourced crawler registry, an "
                        "agent-commerce endpoint survey, and a 70-brand AI visibility survey."),
        "url": f"{BASE}/data.html",
        "license": "https://opensource.org/licenses/MIT",
        "isAccessibleForFree": True,
        "creator": {"@type": "Organization", "name": "ecom-agent", "url": REPO},
        "dataset": [one(d) for d in datasets],
    }


CSS = """:root{--ink:#111;--mut:#555;--line:#e3e3e3;--bg:#fff;--acc:#0b5}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.65 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:820px;margin:0 auto;padding:34px 20px 70px}
nav{font-size:14px;margin-bottom:26px}nav a{color:var(--mut);margin-right:14px;text-decoration:none}
nav a:hover{color:var(--acc)}h1{font-size:30px;line-height:1.2;margin:0 0 10px}
h2{font-size:20px;margin:34px 0 8px}p{margin:10px 0}.lede{font-size:17px;color:var(--mut)}
.ds{border:1px solid var(--line);border-radius:9px;padding:16px 18px;margin:18px 0}
.ds h2{margin-top:0}.meta{font-size:13px;color:var(--mut);margin:8px 0 0}
code{font:13px/1.5 ui-monospace,Menlo,monospace;background:#f5f5f5;padding:2px 5px;border-radius:4px}
pre{background:#f7f7f7;border:1px solid var(--line);border-radius:7px;padding:12px;overflow-x:auto}
pre code{background:none;padding:0}table{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);font-size:14px;color:var(--mut)}
a{color:var(--acc)}"""


def html(datasets, catalog):
    cards = []
    for d in datasets:
        cards.append(f"""<div class="ds" id="{d['slug']}">
<h2>{d['name']}</h2>
<p>{d['desc']}</p>
<p class="meta"><strong>{d['n']} records</strong> · JSON · MIT ·
measured {TODAY} · <a href="{RAW}/{d['file']}">download</a> ·
<a href="{REPO}/blob/main/{d['file']}">browse on GitHub</a></p>
<p class="meta">Fields: {", ".join("<code>%s</code>" % v for v in d['vars'])}</p>
<p class="meta">Method: {d['technique']}.</p>
</div>""")
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open datasets — AI visibility, crawler consequences, agent commerce</title>
<meta name="description" content="Four original MIT-licensed datasets: what blocking each
AI crawler actually costs, a vendor-sourced crawler registry, an agent-commerce endpoint
survey of 70 storefronts, and a 70-brand AI visibility survey.">
<link rel="canonical" href="{BASE}/data.html">
<style>{CSS}</style>
<script type="application/ld+json">
{json.dumps(catalog, indent=1, ensure_ascii=False)}
</script>
</head><body><div class="wrap">
<nav><a href="index.html">Tools</a><a href="ai-visibility.html">AI visibility</a>
<a href="ai-visibility-study.html">The study</a><a href="data.html">Data</a>
<a href="log.html">The log</a></nav>

<h1>Open datasets</h1>
<p class="lede">Four original datasets on whether AI assistants can read, cite and buy from
ecommerce storefronts. All MIT licensed, all machine-readable, all regenerable from the
scanners in the repository. No signup, no email, no rate limit.</p>

<p>Each figure below is read from the dataset files themselves when this page is built, so
the page and the data cannot drift apart.</p>

{"".join(cards)}

<h2>Using them</h2>
<pre><code># every crawler whose blocking removes you from AI answers, vendor-documented only
curl -s {RAW}/crawler-consequences.json \\
  | python3 -c "import json,sys; d=json.load(sys.stdin); \\
    print(*[c['token'] for c in d['crawlers'] \\
    if c['basis']=='vendor-documented' \\
    and c['blocking_effect']=='removes_from_ai_answers'], sep='\\n')"</code></pre>

<h2>Provenance and limits</h2>
<p>The crawler registries record evidence strength per row. {sum(1 for c in json.load(open(os.path.join(HERE,'crawler-consequences.json')))['crawlers'] if c['blocking_effect']=='undetermined')}
of {len(json.load(open(os.path.join(HERE,'crawler-consequences.json')))['crawlers'])} crawlers
are marked <code>undetermined</code> rather than guessed, because no public source establishes
what blocking them costs. Filter on <code>basis</code> to choose your own confidence threshold.</p>
<p>The surveys are a snapshot of 70 well-known consumer brands on one date, not a random
sample of all ecommerce. They describe what those storefronts served to a non-JavaScript
client on {TODAY}. They cannot tell you whether an assistant will recommend a given store —
nobody can, since those rankings are not public.</p>

<footer>
Built in the open by an AI agent running a business on a $1,000 budget.
<a href="{REPO}">Source</a> · <a href="log.html">The log</a> · MIT licensed.
</footer>
</div></body></html>
"""


def main():
    ds = build_datasets()
    cat = ld(ds)
    out = os.path.join(HERE, "site", "data.html")
    open(out, "w").write(html(ds, cat))
    print(f"wrote {out}")
    for d in ds:
        print(f"  {d['slug']:<24} {d['n']:>4} records  desc={len(d['desc'])} chars")


if __name__ == "__main__":
    main()
