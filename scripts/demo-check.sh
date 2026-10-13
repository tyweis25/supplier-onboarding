#!/bin/sh
# Usage: scripts/demo-check.sh
# Check health and supplier onboarding through the local tunnel on port 18080.

base=http://127.0.0.1:18080

curl --max-time 5 -sS "$base/health"
echo

for capability in BOOK UPGRADE_BIDDING; do
  curl --max-time 5 -sS -X POST "$base/onboarding/check" \
    -H 'Content-Type: application/json' \
    -d "{\"supplier_code\":\"AIR1\",\"capability\":\"$capability\"}"
  echo
done
