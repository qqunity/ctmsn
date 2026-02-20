#!/usr/bin/env bash
set -euo pipefail

# Renew Let's Encrypt certificates and reload nginx
# Intended to be called from cron (see setup.sh)

cd "$(dirname "$0")/.."

docker compose run --rm certbot renew --quiet
docker compose exec nginx nginx -s reload

echo "[$(date)] Certificate renewal completed."
