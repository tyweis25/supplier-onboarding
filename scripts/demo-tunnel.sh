#!/bin/sh
# Usage: scripts/demo-tunnel.sh [namespace]
# Forward svc/supplier-onboarding to http://127.0.0.1:18080.
# Namespace defaults to qa.

NS="${1:-qa}"
while true; do
  kubectl port-forward -n "$NS" --address 127.0.0.1 svc/supplier-onboarding 18080:80
  echo "tunnel dropped, reconnecting"
  sleep 1
done
