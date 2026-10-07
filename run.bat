@echo off
REM EventPulse AI - one-click launcher (Windows)
cd /d "%~dp0"
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
REM Optional: enable the Claude-backed analyst for this session
REM set ANTHROPIC_API_KEY=your-key-here
echo.
echo EventPulse AI running at http://localhost:3000  (Ctrl+C to stop)
start "" http://localhost:3000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 3000
