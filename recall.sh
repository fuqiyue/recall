#!/usr/bin/env bash
# Recall CLI launcher (Linux/macOS).
# Keep LF line endings; CRLF breaks the shebang. See .gitattributes.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    RECALL_PY=python3
elif command -v python >/dev/null 2>&1; then
    RECALL_PY=python
else
    echo "[ERROR] Python not found on PATH." >&2
    echo "        Install Python 3.8+: https://www.python.org/downloads/" >&2
    exit 127
fi

exec "$RECALL_PY" "$SCRIPT_DIR/scripts/recall.py" "$@"
