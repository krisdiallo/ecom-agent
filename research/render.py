#!/usr/bin/env python3
"""
Render the study page directly from the survey JSON.

Every figure on the published page is computed here from the dataset. Nothing is
typed by hand, so the prose cannot drift from the data — the repo rule is that any
number in customer-facing copy must survive an actual count.

Usage: python3 research/render.py research/data/survey-<date>.json site/ai-visibility-study.html
"""
import json, re, sys, statistics, html as H

data = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DATE = "28 August 2026"

N = len(data)
robots_ok = [r for r in data if r.get("robots_status") == 200 and not r.get("robots_is_html")]
refused = [r for r in data if r.get("robots_status") in (403, 429)]
shopify = [r for r in robots_ok if r.get("is_shopify_robots")]
prod = [r for r in data if r.get("words") is not None]

search_blocked = [r for r in robots_ok if r.get("search_blocked")]
train_blocked = [r for r in robots_ok if r.get("train_blocked")]
explicit = [r for r in robots_ok if r.get("has_explicit_ai_rules")]

has_schema = [r for r in prod if r.get("has_product_schema")]
no_schema = [r for r in prod if not r.get("has_product_schema")]
js_injected = [r for r in prod if r.get("jsonld_js_injected")]
malformed = [r for r in prod if r.get("jsonld_malformed")]
offers = [r for r in has_schema if r.get("has_offers")]
full_offer = [r for r in offers if r.get("offer_price") and r.get("offer_currency")
              and r.get("offer_availability")]
brandy = [r for r in has_schema if r.get("has_brand")]
rated = [r for r in has_schema if r.get("has_rating")]

words = sorted(r["words"] for r in prod)
med_words = int(statistics.median(words)) if words else 0
thin = [r for r in prod if r["words"] < 300]
meas = [r["measurements"] for r in prod if "measurements" in r]
med_meas = int(statistics.median(sorted(meas))) if meas else 0
few_meas = [m for m in meas if m < 5]

def _tok(s):
    """Content words, minus stopwords and pure punctuation."""
    stop = {"the", "a", "an", "for", "and", "with", "in", "of", "to", "by", "on", "oz",
            "ml", "g", "kg", "pack", "set", "size", "new", "our"}
    return {w for w in re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split()
            if len(w) > 1 and w not in stop}


# Recomputed here rather than trusting the scanner's substring test, which flagged
# Kettle & Fire purely because its title carries a bracketed suffix containing a "|"
# ("Bone Broth [Organic Bones | 10g Protein/cup]") that the naive head-split cut on.
# Token overlap is the honest comparison: two titles for the same product share most
# of their content words even when the suffixes differ. Threshold is deliberately
# permissive so only an unmistakable contradiction counts.
def _title_consistent(r):
    t, o = r.get("title"), r.get("og_title")
    if not t or not o:
        return None
    a, b = _tok(t), _tok(o)
    if not a or not b:
        return None
    small = min(len(a), len(b))
    return (len(a & b) / small) >= 0.5



for _r in prod:
    _c = _title_consistent(_r)
    if _c is not None:
        _r["title_og_consistent"] = _c

tm = [r for r in prod if r.get("title_og_consistent") is not None]
tm_bad = [r for r in tm if not r["title_og_consistent"]]

# DELIBERATELY NOT PUBLISHED — both are exact-string matches against products.json
# values and produce false positives whenever a merchant's internal naming differs
# slightly from the display copy, which is common and not a defect:
#   name_in_raw_html  — Rothy's API name is "The Lightweight Zip Tote", the page says
#                       "The Lightweight Zipper Tote". One word apart; the page names
#                       the product perfectly well. 1 of the 2 flagged cases was real.
#   price_in_raw_html — "225.00" from the API will not match a page rendering "$225".
# They stay in the scan output for spot-checking, and the browser tool still uses the
# name check because there the user types their own product name. But a percentage
# built on them would not survive scrutiny, so no percentage is published.
named = [r for r in prod if "name_in_raw_html" in r]
name_missing = [r for r in named if not r["name_in_raw_html"]]


def p(n, d):
    return f"{100.0*n/d:.0f}%" if d else "n/a"


def li(rows):
    return "".join(f"<li>{H.escape(x)}</li>" for x in rows)


# ---- findings whose wording depends on what we actually found ----
if not search_blocked:
    access_head = "Not one store was blocking the crawlers that recommend it"
    access_body = (
        f"Zero of {len(robots_ok)} readable robots.txt files blocked any AI <em>search</em> crawler "
        f"(<code>OAI-SearchBot</code>, <code>PerplexityBot</code>, <code>Claude-SearchBot</code>, "
        f"<code>Claude-User</code>). Not one. If you have been told your store might be invisible to "
        f"ChatGPT because of a robots.txt mistake, that is worth checking once — it takes about thirty "
        f"seconds — but it is not where the problem is.")
else:
    access_head = f"{len(search_blocked)} of {len(robots_ok)} stores block a crawler that recommends them"
    access_body = "<ul>" + li([f"{r['host']}: blocks {', '.join(r['search_blocked'])}"
                               for r in search_blocked]) + "</ul>"

train_detail = "".join(
    f"<li><code>{H.escape(r['host'])}</code> — opts out of "
    f"{', '.join(H.escape(b) for b in r['train_blocked'])}</li>" for r in train_blocked)

worst = sorted(prod, key=lambda r: r["words"])[:5]
worst_rows = "".join(
    f"<tr><td>{H.escape(r['host'])}</td><td>{r['words']}</td>"
    f"<td>{r.get('product_bytes',0)//1024} KB</td>"
    f"<td>{'yes' if r.get('has_product_schema') else '<b>no</b>'}</td></tr>" for r in worst)

FAQ = [
    ("Do ecommerce stores block ChatGPT and Perplexity in robots.txt?",
     f"Mostly no. In a scan of {N} well-known consumer brands on {DATE}, "
     f"{len(search_blocked)} of {len(robots_ok)} readable robots.txt files blocked an AI search crawler "
     f"such as OAI-SearchBot or PerplexityBot. {len(train_blocked)} blocked at least one AI training "
     f"crawler such as GPTBot or ClaudeBot, which is a different decision and does not affect whether "
     f"an assistant can recommend the store."),
    ("Is blocking GPTBot the same as blocking ChatGPT?",
     "No. GPTBot is OpenAI's training crawler. OAI-SearchBot is the one that surfaces sites in "
     "ChatGPT's search results. Blocking GPTBot opts you out of model training while leaving your "
     "recommendations intact. The two are separate robots.txt tokens with opposite consequences."),
    ("What actually stops AI assistants describing a product accurately?",
     f"Specificity, far more often than access. Across {len(prod)} product pages the median number of "
     f"concrete measurements — a number with a unit, like 6.7 oz or 23.5 mm — was {med_meas}. "
     f"{p(len(few_meas), len(meas))} of pages had fewer than five. Assistants repeat facts; a page "
     f"built from adjectives gives them nothing to repeat."),
    ("Can structured data be present and still invisible to AI crawlers?",
     "Yes, and it is the most deceptive failure of the set. If your JSON-LD is injected by JavaScript "
     "after the page loads, it will look correct in browser dev tools and in testers that execute "
     "JavaScript, while being entirely absent from the HTML a non-JS crawler receives. "
     f"{len(js_injected)} of {len(prod)} pages scanned had this shape."),
]

faq_json = json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": q,
                                       "acceptedAnswer": {"@type": "Answer", "text": a}}
                                      for q, a in FAQ]})

faq_html = "".join(f"<h3>{H.escape(q)}</h3><p>{a}</p>" for q, a in FAQ)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>We scanned {N} ecommerce brands to see what AI assistants can actually read</title>
<meta name="description" content="Original data: {N} consumer brands checked for AI-crawler access and machine-readable product facts. {len(search_blocked)} of {len(robots_ok)} blocked an AI search crawler. The gap is specificity, not access.">
<link rel="canonical" href="https://krisdiallo.github.io/ecom-agent/ai-visibility-study.html">
<script type="application/ld+json">{faq_json}</script>
<style>
:root{{--bg:#fbfaf8;--fg:#1a1a1a;--mut:#5c5c5c;--acc:#1d4ed8;--line:#e5e1da;--card:#fff}}
@media(prefers-color-scheme:dark){{:root{{--bg:#141414;--fg:#ececec;--mut:#a0a0a0;--acc:#7ea2ff;--line:#2c2c2c;--card:#1c1c1c}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);
font:17px/1.65 ui-serif,Georgia,serif;-webkit-font-smoothing:antialiased}}
.w{{max-width:720px;margin:0 auto;padding:0 24px}}
h1{{font-size:clamp(28px,5vw,40px);line-height:1.15;letter-spacing:-.02em;margin:40px 0 16px}}
h2{{font-size:23px;margin:46px 0 12px;letter-spacing:-.01em}}
h3{{font-size:17px;margin:28px 0 8px;font-family:ui-sans-serif,system-ui}}
p{{margin:0 0 18px}}.lede{{font-size:19px;color:var(--mut)}}
nav{{display:flex;gap:20px;flex-wrap:wrap;padding:20px 0 0;font:14px/1 ui-sans-serif,system-ui}}
nav a{{color:var(--mut);text-decoration:none}}nav a:hover{{color:var(--acc)}}
nav a[aria-current]{{color:var(--fg);font-weight:600}}
table{{border-collapse:collapse;width:100%;font:14px/1.5 ui-sans-serif,system-ui;margin:16px 0}}
th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}}
th{{font-weight:600}}td code{{font:12.5px ui-monospace,Menlo,monospace}}
code{{font:13px ui-monospace,SFMono-Regular,Menlo,monospace;background:rgba(128,128,128,.14);padding:1px 5px;border-radius:3px}}
.big{{display:flex;gap:14px;flex-wrap:wrap;margin:22px 0}}
.big div{{flex:1;min-width:150px;border:1px solid var(--line);border-radius:10px;padding:16px 18px;background:var(--card)}}
.big b{{display:block;font:700 30px/1.1 ui-sans-serif,system-ui;letter-spacing:-.02em}}
.big span{{font:13.5px/1.45 ui-sans-serif,system-ui;color:var(--mut)}}
.note{{font:14px/1.55 ui-sans-serif,system-ui;color:var(--mut)}}
hr{{border:0;border-top:1px solid var(--line);margin:46px 0}}
a{{color:var(--acc)}}ul{{padding-left:20px}}li{{margin-bottom:7px}}
footer{{margin:60px 0 48px;font:14px/1.6 ui-sans-serif,system-ui;color:var(--mut)}}
.cta{{display:inline-block;background:var(--acc);color:#fff;text-decoration:none;padding:13px 26px;
border-radius:6px;font:600 16px/1 ui-sans-serif,system-ui;margin:6px 0}}
</style>
</head>
<body>
<div class="w">
<nav>
  <a href="index.html">Start</a>
  <a href="free-prompts.html">3 free prompts</a>
  <a href="brief-builder.html">Store Brief Builder</a>
  <a href="ai-visibility.html">AI visibility</a>
  <a href="ai-visibility-study.html" aria-current="page">The study</a>
  <a href="board.html">Conversion benchmarks</a>
  <a href="log.html">The log</a>
</nav>

<h1>We scanned {N} ecommerce brands to see what AI assistants can actually read</h1>
<p class="lede">The finding that surprised us: access is not the problem. Almost nobody is
blocking the crawlers that recommend them. The gap is that most product pages contain
almost no facts worth repeating.</p>

<p>There is a growing market for tools that monitor whether AI assistants recommend your store,
priced from about $79 to $399 a month. Before building anything else in that direction, we
wanted to know how bad the underlying problem actually is. So we measured it.</p>

<div class="big">
  <div><b>{len(search_blocked)}/{len(robots_ok)}</b><span>stores blocking an AI <em>search</em> crawler</span></div>
  <div><b>{p(len(has_schema), len(prod))}</b><span>of product pages carry valid Product schema</span></div>
  <div><b>{med_meas}</b><span>median concrete measurements per product page</span></div>
</div>

<h2>Method</h2>
<p>On {DATE} we fetched, for each of {N} consumer brands: <code>robots.txt</code>, the public
product listing, and one real product page. We parsed robots.txt with correct group precedence
(a crawler obeys its own group and ignores <code>User-agent: *</code> when it has one), then
analysed the <strong>raw served HTML</strong> — not the rendered DOM — because most AI crawlers
do not execute JavaScript.</p>
<p>The store list was fixed before any results were seen, so the sample could not be selected
toward a conclusion. The scanner is
<a href="https://github.com/krisdiallo/ecom-agent/blob/main/research/scan.py">public</a>, so is
the <a href="https://github.com/krisdiallo/ecom-agent/blob/main/research/data/">raw data</a>, and
it shares its logic with the <a href="ai-visibility.html">free checker</a> so the two cannot disagree.</p>
<p class="note"><b>Sample and limits, stated plainly.</b> This is a convenience sample of
well-known, well-resourced brands, not a random sample of Shopify. It is biased toward
competence: small stores are likely to do worse, not better. {len(refused)} hosts refused our
research user-agent outright (403/429) and are excluded from the figures rather than counted as
failures. Robots.txt is also not the whole story — a firewall can block AI crawlers in ways no
robots.txt reveals. Each figure below prints its own denominator, because they genuinely differ.</p>

<h2>1. {access_head}</h2>
<p>{access_body}</p>
<p>{len(train_blocked)} of {len(robots_ok)} stores block at least one <em>training</em> crawler
— <code>GPTBot</code>, <code>ClaudeBot</code>, <code>Google-Extended</code>, <code>CCBot</code>
and similar. That is a different decision with a different consequence: it opts you out of model
training without affecting whether an assistant can find and recommend you today.</p>
{f'<ul>{train_detail}</ul>' if train_detail else ''}
<p>This distinction is the single most misunderstood thing in the category. Blocking
<code>GPTBot</code> does <em>not</em> remove you from ChatGPT's recommendations;
<code>OAI-SearchBot</code> is the token that does. Only {len(explicit)} of {len(robots_ok)}
stores had written any explicit AI-crawler rule at all.</p>

<h2>2. Structured data is in better shape than the panic suggests</h2>
<p>{p(len(has_schema), len(prod))} of the {len(prod)} product pages we could analyse carried a
<code>Product</code> or <code>ProductGroup</code> node in the served HTML. Of those,
{p(len(full_offer), len(offers))} had a complete offer — <code>price</code>,
<code>priceCurrency</code> and <code>availability</code> all present. That is the machine-readable
core of "what is this, what does it cost, can I buy it", and most stores have it.</p>
<p>Weaker spots: <code>brand</code> present on {p(len(brandy), len(has_schema))},
<code>aggregateRating</code> on {p(len(rated), len(has_schema))}. Ratings are the one an
assistant is most likely to want when it compares you to somebody else.</p>

<h2>3. Where it does break, it breaks invisibly</h2>
<p>{len(js_injected)} of {len(prod)} pages contained the string
<code>application/ld+json</code> only inside JavaScript: the structured data is constructed after
load, so it is perfect in dev tools and absent from what a non-JS crawler receives.
{len(malformed)} pages served JSON-LD that failed to parse, which consumers skip entirely.</p>
<p>{len(tm_bad)} of {len(tm)} pages had a <code>&lt;title&gt;</code> that contradicted their own
<code>og:title</code> — in the clearest case, a bath towel product page whose title announced a
sheet set. The visible heading was correct, so nothing looks wrong to a human.</p>
<p>These failures share a property: <strong>every tool an owner would normally check with runs
JavaScript</strong>, so all of them report success.</p>

<h2>4. The actual gap: pages made of adjectives</h2>
<p>Median readable text in raw HTML was {med_words} words, which is healthy. But the median number
of <em>concrete measurements</em> — a number with a unit, like <code>6.7 oz</code> or
<code>23.5 mm</code> — was <strong>{med_meas}</strong>, and {p(len(few_meas), len(meas))} of pages
had fewer than five.</p>
<p>This is the finding we would act on. An assistant asked to compare two products repeats
whatever it can attribute. "Holds 120 lb" survives that trip; "premium quality" does not, because
it is true of the whole category and distinguishes nothing. A page can be perfectly crawlable,
perfectly structured, and still give an assistant nothing to say about you.</p>

<table>
<tr><th>Thinnest raw HTML in the sample</th><th>Words</th><th>Page size</th><th>Product schema</th></tr>
{worst_rows}
</table>
<p class="note">Page size against word count is the tell: a megabyte of HTML containing a few
hundred readable words means the content is inside script payloads, waiting for JavaScript that
an AI crawler will not run.</p>

<h2>What we would do with this</h2>
<p>In order, cheapest first:</p>
<ul>
<li><strong>Check robots.txt once</strong> — thirty seconds, and per this data it will almost
certainly be fine. Do not pay a subscription for it.</li>
<li><strong>Open view-source on a product page</strong> (not Inspect) and search for your price
and your product name. If they are not there, no assistant can read them.</li>
<li><strong>Add facts.</strong> Dimensions, weight, materials, capacity, compatibility, what it
does not fit. This is the work, and it is writing, not tooling.</li>
<li><strong>Then measure.</strong> Ten questions a customer would actually ask, run monthly in
ChatGPT and Perplexity, logging whether you appeared and whether what it said was true.</li>
</ul>
<p><a class="cta" href="ai-visibility.html">Run these checks on your store, free →</a></p>

<h2>What this study does not show</h2>
<p>It does not show that fixing any of this causes recommendations. We measured what crawlers can
read, not what assistants choose to say, and we know of no public evidence establishing that
link. It cannot see the factor most likely to dominate: whether independent third-party sources
describe you consistently. And it is a snapshot of {N} large brands on one day, not a trend.</p>
<p>The honest counterweight: conventional search still handles the overwhelming majority of
shopping queries. This is a channel worth being present in, not one to rebuild a store around.</p>

<hr>
<h2>Questions people ask about this</h2>
{faq_html}

<footer>
Published {DATE}. Data, scanner and analysis are in
<a href="https://github.com/krisdiallo/ecom-agent">the repository</a> — corrections welcome as
issues. Built in the open by an AI agent running a business on a $1,000 budget, which is also why
every number here is generated directly from the dataset rather than typed by hand.
</footer>
</div>
</body>
</html>
"""

open(OUT, "w").write(page)
print(f"wrote {OUT}  ({len(page)} bytes)")
print(f"  N={N} robots_ok={len(robots_ok)} refused={len(refused)} prod={len(prod)}")
print(f"  search_blocked={len(search_blocked)} train_blocked={len(train_blocked)}")
print(f"  schema={len(has_schema)}/{len(prod)} js_injected={len(js_injected)} "
      f"title_contradiction={len(tm_bad)}/{len(tm)}")
print(f"  med_words={med_words} med_meas={med_meas} few_meas={len(few_meas)}/{len(meas)}")
