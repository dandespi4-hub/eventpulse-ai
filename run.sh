#!/usr/bin/env bash
# EventPulse AI - one-command launcher (macOS / Linux)
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
# Optional: export ANTHROPIC_API_KEY=your-key-here   (enables the Claude-backed analyst)
echo "EventPulse AI running at http://localhost:3000  (Ctrl+C to stop)"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 3000
