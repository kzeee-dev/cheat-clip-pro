#!/data/data/com.termux/files/usr/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=================================="
echo "       CHEAT CLIP PRO"
echo "=================================="

if curl -fsS --max-time 2 http://127.0.0.1:8000/docs -o /dev/null; then
    echo "Backend sudah aktif di port 8000."
    echo "Buka: http://127.0.0.1:8000/docs"
    exit 0
fi

echo "Menjalankan backend melalui Ubuntu..."

exec proot-distro login ubuntu -- bash -lc "cd '$ROOT_DIR' && node scripts/start-backend.js"
