#!/usr/bin/env bash
# Cheat Clip Pro backend helper for Termux + Ubuntu proot.
# Usage: bash ccp-server.sh start|stop|status|logs

set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PY="/tmp/ccp-backend-venv/bin/python"
PID_FILE="/tmp/cheat-clip-pro-backend.pid"
LOG_FILE="/tmp/cheat-clip-pro-backend.log"
HOST="0.0.0.0"
PORT="8000"

usage() {
  echo "Cheat Clip Pro backend"
  echo "Usage: bash ccp-server.sh {start|stop|status|logs}"
}

is_running() {
  [[ -s "$PID_FILE" ]] || return 1
  local pid
  pid="$(cat "$PID_FILE")"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  kill -0 "$pid" 2>/dev/null || return 1
  tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q 'uvicorn backend.main:app'
}

show_status() {
  if is_running; then
    echo "RUNNING: backend PID $(cat "$PID_FILE")"
    echo "Local API: http://127.0.0.1:$PORT"
    echo "Docs:      http://127.0.0.1:$PORT/docs"
    echo "Log:       $LOG_FILE"
  else
    echo "STOPPED: backend tidak sedang berjalan."
    rm -f "$PID_FILE"
  fi
}

start_server() {
  if [[ ! -d "$ROOT/backend" || ! -f "$ROOT/backend/main.py" ]]; then
    echo "ERROR: folder backend/main.py tidak ditemukan."
    echo "Lokasi script: $ROOT"
    exit 1
  fi
  if [[ ! -x "$PY" ]]; then
    echo "ERROR: virtualenv Python tidak ditemukan: $PY"
    echo "Periksa environment backend terlebih dahulu."
    exit 1
  fi

  if is_running; then
    echo "Backend sudah aktif."
    show_status
    exit 0
  fi
  rm -f "$PID_FILE"

  if ! "$PY" -c 'import uvicorn, fastapi' >/dev/null 2>&1; then
    echo "ERROR: uvicorn/FastAPI belum tersedia di virtualenv."
    echo "Periksa instalasi dependency backend sebelum menjalankan server."
    exit 1
  fi

  if ! "$PY" -c 'import httpx' >/dev/null 2>&1; then
    echo "Dependency httpx belum ada; memasang httpx..."
    "$PY" -m pip install httpx
  fi

  echo "Memeriksa import backend..."
  if ! (cd "$ROOT" && PYTHONPATH="$ROOT" "$PY" -c 'import backend.main') 2>"$LOG_FILE"; then
    echo "ERROR: backend gagal di-import. Detail:"
    tail -n 35 "$LOG_FILE"
    echo "Perbaiki dependency/konfigurasi yang disebutkan, lalu jalankan start lagi."
    exit 1
  fi

  if ! "$PY" -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('127.0.0.1',$PORT)); s.close()" >/dev/null 2>&1; then
    : # Port appears available.
  else
    echo "ERROR: port $PORT sudah dipakai proses lain."
    echo "Hentikan proses tersebut atau ubah PORT di script ini."
    exit 1
  fi

  echo "Menyalakan Cheat Clip Pro backend..."
  cd "$ROOT"
  nohup env PYTHONPATH="$ROOT" HOST="$HOST" PORT="$PORT" \
    "$PY" -m uvicorn backend.main:app --host "$HOST" --port "$PORT" \
    >>"$LOG_FILE" 2>&1 </dev/null &
  local pid=$!
  echo "$pid" > "$PID_FILE"
  sleep 2

  if kill -0 "$pid" 2>/dev/null; then
    echo "Backend berhasil dijalankan."
    show_status
  else
    echo "ERROR: backend berhenti saat startup. Log terakhir:"
    tail -n 50 "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
  fi
}

stop_server() {
  if ! is_running; then
    echo "Backend sudah berhenti."
    rm -f "$PID_FILE"
    exit 0
  fi
  local pid
  pid="$(cat "$PID_FILE")"
  kill "$pid"
  for _ in {1..10}; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 1
  done
  if kill -0 "$pid" 2>/dev/null; then
    echo "Server belum berhenti normal; mengirim SIGKILL..."
    kill -9 "$pid" 2>/dev/null || true
  fi
  rm -f "$PID_FILE"
  echo "Backend dihentikan."
}

case "${1:-}" in
  start)  start_server ;;
  stop)   stop_server ;;
  status) show_status ;;
  logs)
    if [[ -f "$LOG_FILE" ]]; then tail -n 60 -f "$LOG_FILE"; else echo "Log belum tersedia: $LOG_FILE"; fi
    ;;
  *) usage; exit 2 ;;
esac
