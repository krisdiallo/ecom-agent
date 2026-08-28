#!/usr/bin/env bash
# Render the study from the dataset, wire it into nav + sitemap, sync docs/, ping IndexNow.
# Idempotent: re-running will not duplicate nav links or sitemap entries.
set -euo pipefail
cd "$(dirname "$0")/.."

DATA="${1:-research/data/survey-2026-08-28.json}"
PAGE="site/ai-visibility-study.html"

python3 research/render.py "$DATA" "$PAGE"

# The dataset catalogue carries the schema.org/Dataset markup that makes these files
# discoverable through Google Dataset Search. Regenerated from the data files, so its
# figures cannot drift from the datasets they describe.
python3 research/build_data_page.py

# nav link to the data catalogue on every page that doesn't already carry one
for f in site/index.html site/log.html site/free-prompts.html site/brief-builder.html \
         site/ai-visibility.html site/ai-visibility-study.html; do
  grep -q '"data.html"' "$f" || \
    perl -0pi -e 's{(  <a href="ai-visibility-study\.html">The study</a>\n)}{$1  <a href="data.html">Data</a>\n}' "$f"
done
grep -q 'data\.html' site/board.html || \
  perl -0pi -e "s{(\+'<a href=\"ai-visibility-study\.html\">The study</a>')}{\$1\n      +'<a href=\"data.html\">Data</a>'}" site/board.html

grep -q 'data\.html' site/sitemap.xml || \
  perl -0pi -e 's{(  <url><loc>https://krisdiallo\.github\.io/ecom-agent/board\.html</loc>)}{  <url><loc>https://krisdiallo.github.io/ecom-agent/data.html</loc><lastmod>2026-08-28</lastmod><priority>0.9</priority></url>\n$1}' site/sitemap.xml

# nav link on every page that doesn't already carry one
for f in site/index.html site/log.html site/free-prompts.html site/brief-builder.html site/ai-visibility.html; do
  grep -q 'ai-visibility-study.html' "$f" || \
    perl -0pi -e 's{(  <a href="ai-visibility\.html"[^>]*>AI visibility</a>\n)}{$1  <a href="ai-visibility-study.html">The study</a>\n}' "$f"
done
grep -q 'ai-visibility-study.html' site/board.html || \
  perl -0pi -e "s{(\+'<a href=\"ai-visibility\.html\">AI visibility</a>')}{\$1\n      +'<a href=\"ai-visibility-study.html\">The study</a>'}" site/board.html

# sitemap
grep -q 'ai-visibility-study.html' site/sitemap.xml || \
  perl -0pi -e 's{(  <url><loc>https://krisdiallo\.github\.io/ecom-agent/board\.html</loc>)}{  <url><loc>https://krisdiallo.github.io/ecom-agent/ai-visibility-study.html</loc><lastmod>2026-08-28</lastmod><priority>0.9</priority></url>\n$1}' site/sitemap.xml

cp site/*.html site/sitemap.xml site/robots.txt docs/
echo "nav links:"; grep -c 'ai-visibility-study' site/*.html | grep -v ':0' || true
echo "rendered + wired."
