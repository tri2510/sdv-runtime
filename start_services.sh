#!/bin/sh

# Minimal startup script for the ptrace-only runtime.
# Keeps the syncer running and tails to keep the container alive.

SYNCER_SERVER_URL=${SYNCER_SERVER_URL:-"https://kit.digitalauto.tech"}
export KUKSA_DISABLED=${KUKSA_DISABLED:-1}

printf 'Runtime: syncer=%s (KUKSA_DISABLED=%s)\n' "$SYNCER_SERVER_URL" "$KUKSA_DISABLED"

python3 /home/dev/ws/kuksa-syncer/syncer.py &

# Keep the container alive (syncer runs in background)
tail -f /dev/null
