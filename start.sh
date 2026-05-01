#!/usr/bin/env bash
# One-shot bootstrap: install deps, run tests, then launch the Flask server.
# Usage from repo root:  ./start.sh

set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$repo/urban-traffic-sim"

echo '==> Installing dependencies'
python -m pip install -r "$src/requirements.txt"

echo '==> Running tests'
python -m pytest "$src/tests"

echo '==> Starting server at http://127.0.0.1:5000/'
python "$src/app.py"
