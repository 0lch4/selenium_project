#!/usr/bin/env bash
# Uruchamia Gitea i tworzy konto administratora używane przez testy.
set -euo pipefail
cd "$(dirname "$0")/.."

ADMIN_USER="${GITEA_ADMIN_USER:-admin}"
ADMIN_PASS="${GITEA_ADMIN_PASS:-Admin123!pass}"
ADMIN_EMAIL="${GITEA_ADMIN_EMAIL:-admin@example.com}"

docker compose up -d --wait

if docker compose exec -T -u git gitea gitea admin user list --admin | grep -qw "$ADMIN_USER"; then
  echo "Admin '$ADMIN_USER' już istnieje"
else
  docker compose exec -T -u git gitea gitea admin user create \
    --admin --username "$ADMIN_USER" --password "$ADMIN_PASS" \
    --email "$ADMIN_EMAIL" --must-change-password=false
fi

curl -fsS http://localhost:3000/api/v1/version && echo
