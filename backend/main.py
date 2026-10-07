from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import llm, simulator
from .engine import get_dashboard, answer_question
from .models import ChatRequest, ChatResponse
from .seed import EVENTS

app = FastAPI(title="EventPulse AI API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


@app.get("/api/health")
def health():
    return {"status": "operational", "mode": "seeded-demo", "version": "1.1.0", "llm_enabled": llm.enabled()}


@app.get("/api/dashboard")
def dashboard():
    return get_dashboard()


@app.get("/api/events")
def events(asset: str | None = None, min_impact: int = 0):
    rows = [event for event in EVENTS if event.impact_score >= min_impact]
    if asset:
        rows = [event for event in rows if asset.upper() in event.assets]
    return rows


@app.get("/api/events/{event_id}")
def event_detail(event_id: str):
    event = next((item for item in EVENTS if item.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return answer_question(request.question)


@app.post("/api/simulate")
def simulate():
    """Demo control: inject the next scripted breaking event (flagged simulated)."""
    return {"event": simulator.inject_next()}


@app.post("/api/reset")
def reset():
    """Demo control: restore the original seeded feed."""
    simulator.reset()
    return {"status": "reset"}


app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")


@app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
def spa(path: str):
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Unknown API route")
    return FileResponse(FRONTEND / "index.html")
