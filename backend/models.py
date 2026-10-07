from typing import Literal
from pydantic import BaseModel, Field


AssetType = Literal["crypto", "equity"]
SentimentLabel = Literal["bullish", "bearish", "neutral"]


class Source(BaseModel):
    name: str
    kind: Literal["official", "news", "social", "market"]
    credibility: int = Field(ge=0, le=100)
    url: str | None = None


class Asset(BaseModel):
    symbol: str
    name: str
    asset_type: AssetType
    price: float
    change_24h: float
    volume: float
    volume_change: float
    sentiment: int
    sentiment_change: int
    mention_velocity: int
    impact: int
    status: str
    sparkline: list[float]


class TimelinePoint(BaseModel):
    time: str
    sentiment: int
    price_index: float
    mentions: int
    label: str | None = None
    severity: Literal["normal", "event", "shock"] = "normal"


class Event(BaseModel):
    id: str
    title: str
    timestamp: str
    age: str
    assets: list[str]
    category: str
    importance: Literal["Critical", "High", "Medium", "Low"]
    confidence: int
    summary: str
    sentiment_before: int
    sentiment_after: int
    shock_score: float
    dominant_emotion: str
    emotions: dict[str, int]
    price_change: float
    volume_change: int
    mention_change: int
    volatility: float
    hype_score: int
    evidence_score: int
    impact_score: int
    factors: dict[str, int]
    verdict: str
    sources: list[Source]
    explanation: str
    timeline: list[TimelinePoint]
    simulated: bool = False


class Alert(BaseModel):
    id: str
    kind: str
    title: str
    message: str
    asset: str
    impact: int
    timestamp: str
    severity: Literal["critical", "warning", "info", "positive"]


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    suggested_questions: list[str]
    mode: Literal["rules", "llm"] = "rules"
