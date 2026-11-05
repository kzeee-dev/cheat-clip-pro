#!/data/data/com.termux/files/usr/bin/bash

echo "=================================="
echo "       CHEAT CLIP PRO"
echo "=================================="

FOUND=0

for FILE in /proc/[0-9]*/cmdline; do
    [ -r "$FILE" ] || continue

    CMD=$(tr '\0' ' ' < "$FILE" 2>/dev/null) || continue

    case "$CMD" in
        *"python -m uvicorn backend.main:app"*"--port 8000"*)
            PID=${FILE#/proc/}
            PID=${PID%/cmdline}

            echo "Menghentikan backend PID: $PID"

            if kill -TERM "$PID" 2>/dev/null; then
                FOUND=1
            fi
            ;;
    esac
done

if [ "$FOUND" -eq 0 ]; then
    echo "Backend tidak ditemukan."
else
    echo "Perintah penghentian sudah dikirim."
fi
