#!/usr/bin/env bash
set -euo pipefail

# CTMSN deployment setup script for Ubuntu 24.04
# Usage: sudo bash deploy/setup.sh <domain> <email>

DOMAIN="${1:?Usage: setup.sh <domain> <email>}"
EMAIL="${2:?Usage: setup.sh <domain> <email>}"

echo "=== CTMSN Setup ==="
echo "Domain: $DOMAIN"
echo "Email:  $EMAIL"
echo ""

# --- 1. Install Docker (if not installed) ---
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    apt-get update
    apt-get install -y ca-certificates curl
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    echo "Docker installed."
else
    echo "Docker already installed."
fi

# --- 2. Create .env if not exists ---
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    SECRET=$(openssl rand -hex 32)
    sed "s|<generate: openssl rand -hex 32>|${SECRET}|" .env.example > .env
    echo ".env created."
fi

# --- 3. Get SSL certificate (standalone mode, before starting the stack) ---
echo "Obtaining SSL certificate via certbot standalone..."

# Determine compose project name (directory name, lowercased)
PROJECT_NAME=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]')
VOLUME_NAME="${PROJECT_NAME}_certbot-conf"

docker volume create "$VOLUME_NAME" 2>/dev/null || true
docker run --rm \
    -p 80:80 \
    -v "${VOLUME_NAME}:/etc/letsencrypt" \
    certbot/certbot certonly \
    --standalone \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN"

# --- 4. Update nginx.conf with actual domain ---
echo "Configuring nginx for domain: $DOMAIN"
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" deploy/nginx.conf

# --- 5. Build and start all services ---
echo "Building and starting all services..."
docker compose up -d --build

# --- 6. Setup cert renewal cron ---
PROJECT_DIR="$(pwd)"
CRON_CMD="0 3 * * * cd ${PROJECT_DIR} && bash deploy/renew-certs.sh >> /var/log/ctmsn-certbot.log 2>&1"
(crontab -l 2>/dev/null | grep -v "renew-certs.sh"; echo "$CRON_CMD") | crontab -

echo ""
echo "=== Setup Complete ==="
echo "Site: https://$DOMAIN"
echo ""
echo "To create a teacher account:"
echo "  docker compose exec api python -c \\"
echo "    \"from ctmsn_api.database import SessionLocal; \\"
echo "    from ctmsn_api.models import User, UserRole; \\"
echo "    from passlib.context import CryptContext; \\"
echo "    pwd_ctx = CryptContext(schemes=['bcrypt']); \\"
echo "    db = SessionLocal(); \\"
echo "    db.add(User(username='teacher', hashed_password=pwd_ctx.hash('CHANGE_ME'), role=UserRole.TEACHER)); \\"
echo "    db.commit(); \\"
echo "    print('Done')\""
