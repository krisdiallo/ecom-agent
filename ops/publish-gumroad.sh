#!/usr/bin/env bash
# Publishes product #1 to Gumroad the moment a token exists.
# Requires: ops/.env with GUMROAD_TOKEN=...   Everything else is already built.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f ops/.env ] || { echo "BLOCKED: no ops/.env — see ops/SETUP-CHECKLIST.md"; exit 1; }
set -a; . ops/.env; set +a
: "${GUMROAD_TOKEN:?BLOCKED: GUMROAD_TOKEN unset}"

DIR=products/01-ecom-prompt-system
ZIP=/tmp/ecom-prompt-system.zip
rm -f "$ZIP"
( cd "$DIR" && zip -qr "$ZIP" . -x 'LISTING.md' )
echo "packaged: $(du -h "$ZIP" | cut -f1)"

NAME=$(sed -n 's/^## Title$//;t x;b;:x;n;p' "$DIR/LISTING.md" | head -1)
DESC=$(awk '/^## Description$/{f=1;next} f' "$DIR/LISTING.md")

curl -sS -X POST https://api.gumroad.com/v2/products \
  -H "Authorization: Bearer $GUMROAD_TOKEN" \
  -F "name=$NAME" \
  -F "price=2900" \
  -F "description=$DESC" \
  -F "custom_permalink=ecom-operator-prompt-system" \
  | tee ops/reports/gumroad-create-response.json
echo
echo "Next: upload $ZIP as the product file (Gumroad file upload is a separate step),"
echo "then flip published=true in the dashboard or via PUT /v2/products/:id."
