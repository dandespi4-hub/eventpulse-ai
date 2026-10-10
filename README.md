# EventPulse AI

**Market intelligence that tells you whether a move is real or just noise.**
EventPulse connects detected events, abnormal sentiment shifts, social activity, and market reactions — and scores each one for *hype* versus *evidence*, so a verified regulatory shock is never confused with an unconfirmed viral rumor.

> Runs on a deterministic **seeded demo feed**. Everything on screen is labelled DEMO FEED, and injected events are tagged SIMULATED. It reports observed activity and estimated impact — not predictions or trading advice.

## Run it (60 seconds)

**Windows:** double-click `run.bat`  
**macOS / Linux:** `./run.sh`  
**Manual:** `pip install -r requirements.txt` then `python -m uvicorn backend.main:app --port 3000`

Open <http://localhost:3000>. Works fully offline (fonts fall back to system fonts).

### Optional: Bitget Qwen-backed analyst
Set `BITGET_QWEN_API_KEY` (see `.env.example`) before launching. The AI Analyst then uses Bitget-hosted Qwen `qwen3.8-max`, grounded strictly in the dashboard data, with citations you can click. If the key is missing or the call fails, it silently falls back to the rules engine, so the demo never breaks. The answer card shows whether Qwen produced the answer.

## Demo controls
| Control | What it does |
|---|---|
| **⚡ Inject event** (or `Ctrl+Shift+E`) | Fires a scripted breaking event (ETH exchange withdrawal pause → XRP spoofed headline → repeat). The dashboard re-scores live and opens the event drawer. |
| **↺ Reset** | Restores the original feed. |
| **Ask EventPulse** (or `Ctrl/⌘+K`) | Opens the analyst from anywhere. |

See **DEMO_SCRIPT.md** for a 3-minute walkthrough and judge Q&A.

## Architecture
- `backend/models.py` — typed domain models (Pydantic)
- `backend/seed.py` — deterministic demo data
- `backend/engine.py` — shock detection, impact scoring, grounded Q&A (rules)
- `backend/llm.py` — optional Bitget-hosted Qwen analyst, grounded in the same data, graceful fallback
- `backend/simulator.py` — scripted breaking-event injector
- `backend/main.py` — REST API + static frontend
- `frontend/` — dependency-free SPA with SVG charts
- `tests/smoke_test.py` — offline tests: `python -m tests.smoke_test`

The provider boundary is intentional: market, news, social, and sentiment adapters can replace `seed.py` without changing the UI contract.

## How scoring works
- **Sentiment shock** — deviation of current sentiment from its rolling baseline, in σ, with the baseline's σ floored at 10 sentiment points so quiet windows don't raise false alarms. |σ| > 3 = shock, ≥ 2 = significant, ≥ 1 = elevated.
- **Impact** — blend of sentiment shock, market movement, social activity, news coverage, and evidence strength (component scores are seeded in the demo).
- **Hype vs evidence** — mention velocity and source concentration vs. credibility of official, news, and market/on-chain sources.

## API
`GET /api/dashboard` · `GET /api/events[?asset=&min_impact=]` · `GET /api/events/{id}` · `POST /api/chat {question}` · `POST /api/simulate` · `POST /api/reset` · `GET /api/health`

## Known limits (be upfront with judges)
All market, news, and social data is seeded; impact and hype component scores are demo inputs, not computed from live feeds. The shock detector is real code running on the seeded sentiment history.
