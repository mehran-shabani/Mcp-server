#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/.devcontainer/logs"
mkdir -p "$LOG_DIR"

cd "$ROOT_DIR"

start_django() {
  if pgrep -f "manage.py runserver" >/dev/null; then
    echo "Django server already running"
  else
    echo "Starting Django development server..."
    nohup python manage.py runserver 0.0.0.0:8000 \
      >"$LOG_DIR/django.log" 2>&1 &
  fi
}

start_frontend() {
  if pgrep -f "npm run dev" >/dev/null; then
    echo "Vite dev server already running"
  else
    echo "Starting Vite development server..."
    cd "$ROOT_DIR/frontend"
    nohup npm run dev -- --host 0.0.0.0 --port 5173 \
      >"$LOG_DIR/frontend.log" 2>&1 &
  fi
}

start_django
start_frontend

cd "$ROOT_DIR"
