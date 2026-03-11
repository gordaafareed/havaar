#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "  // havaar"
echo ""

if ! command -v python3 &> /dev/null; then
  echo "  [error] python3 not found. install from https://python.org"
  exit 1
fi

if [ ! -f "$ROOT_DIR/.env" ]; then
  echo "  [setup] no .env found — copying from .env.example"
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "  [setup] edit .env with your Twilio credentials then run this again"
  open "$ROOT_DIR/.env" 2>/dev/null || xdg-open "$ROOT_DIR/.env" 2>/dev/null || echo "  open .env in a text editor"
  exit 0
fi

if [ ! -d "$ROOT_DIR/.venv" ]; then
  echo "  [setup] creating virtual environment..."
  python3 -m venv "$ROOT_DIR/.venv"
fi

source "$ROOT_DIR/.venv/bin/activate"

echo "  [setup] installing dependencies..."
pip install -q -r "$ROOT_DIR/requirements.txt"

if ! command -v cloudflared &> /dev/null; then
  echo ""
  echo "  [setup] cloudflared not found. installing..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install cloudflared 2>/dev/null || {
      echo "  [error] brew not found. install cloudflared manually:"
      echo "  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
      exit 1
    }
  else
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 \
      -o /usr/local/bin/cloudflared
    chmod +x /usr/local/bin/cloudflared
  fi
fi

PORT=$(grep -E "^PORT=" "$ROOT_DIR/.env" | cut -d= -f2 | tr -d '[:space:]')
PORT=${PORT:-5050}

echo "  [tunnel] starting cloudflare tunnel..."
cloudflared tunnel --url "http://localhost:$PORT" --no-autoupdate > /tmp/havaar-tunnel.log 2>&1 &
TUNNEL_PID=$!

echo "  [tunnel] waiting for public url..."
TUNNEL_URL=""
for i in $(seq 1 20); do
  TUNNEL_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/havaar-tunnel.log 2>/dev/null | head -1)
  if [ -n "$TUNNEL_URL" ]; then
    break
  fi
  sleep 1
done

if [ -z "$TUNNEL_URL" ]; then
  echo "  [error] could not get tunnel url. check /tmp/havaar-tunnel.log"
  kill $TUNNEL_PID 2>/dev/null
  exit 1
fi

echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │  dashboard  → http://localhost:$PORT          │"
echo "  │  public url → $TUNNEL_URL  │"
echo "  └─────────────────────────────────────────────┘"
echo ""
echo "  set this as your twilio webhook:"
echo "  $TUNNEL_URL/twilio/incoming"
echo ""

trap "kill $TUNNEL_PID 2>/dev/null; echo '  [stopped]'" EXIT

cd "$ROOT_DIR"
python3 -m server.app