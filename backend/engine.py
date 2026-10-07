"""Explainable analytics over normalized market, event, and sentiment records."""
import re
from statistics import mean, pstdev

from . import llm
from .models import ChatResponse
from .seed import ASSETS, EVENTS, ALERTS, SENTIMENT_HISTORY

# Sentiment is a 0-100 score. Even in a calm window it jitters by several points,
# so deviations are measured against max(observed sigma, this floor). Without a
# floor, a quiet baseline (sigma ~1.5) would make ordinary moves look like 10-sigma events.
NOISE_FLOOR = 10.0


def classify_shock(values: list[int]) -> dict:
    baseline, current = values[:-1], values[-1]
    avg = mean(baseline)
    sigma = max(pstdev(baseline), NOISE_FLOOR)
    z = max(-6.0, min(6.0, (current - avg) / sigma))
    absolute = abs(z)
    level = "Sentiment shock" if absolute > 3 else "Significant" if absolute >= 2 else "Elevated" if absolute >= 1 else "Normal"
    return {"baseline": round(avg, 1), "current": current, "z_score": round(z, 1), "level": level}


def market_mood() -> dict:
    weighted = round(sum(a.sentiment * max(a.volume, 1) for a in ASSETS) / sum(max(a.volume, 1) for a in ASSETS))
    # Headline mood is breadth (equal-weighted) so BTC's volume does not dominate it.
    breadth = round(sum(a.sentiment for a in ASSETS) / len(ASSETS))
    return {"score": breadth, "label": "Bullish" if breadth >= 60 else "Bearish" if breadth < 40 else "Mixed", "volume_weighted": weighted}


def get_dashboard() -> dict:
    shocks = {symbol: classify_shock(history) for symbol, history in SENTIMENT_HISTORY.items()}
    verified = sum(1 for e in EVENTS if e.evidence_score >= 70)
    source_names = {s.name for e in EVENTS for s in e.sources}
    return {
        "meta": {
            "mode": "DEMO FEED",
            "as_of": "2026-10-04T11:00:00Z",
            "coverage": f"{len(ASSETS)} assets · {len(source_names)} sources",
            "sources": len(source_names),
            "llm": llm.enabled(),
        },
        "mood": market_mood(),
        "stats": {
            "market_impact": round(sum(e.impact_score for e in EVENTS) / len(EVENTS)),
            "active_events": len(EVENTS),
            "verified_events": verified,
            "developing_events": len(EVENTS) - verified,
            "sentiment_shocks": sum(1 for s in shocks.values() if s["level"] in ("Significant", "Sentiment shock")),
            "high_risk": sum(1 for a in ASSETS if a.impact >= 75),
        },
        "assets": ASSETS,
        "events": sorted(EVENTS, key=lambda event: event.impact_score, reverse=True),
        "alerts": ALERTS,
        "shocks": shocks,
        "methodology": {
            "shock": f"Deviation from a rolling sentiment baseline, normalized by the baseline's standard deviation (floored at {NOISE_FLOOR:.0f} points to avoid false alarms in quiet windows).",
            "impact": "Weighted blend of sentiment shock, market movement, social activity, coverage, and evidence.",
            "hype": "Mention velocity, intensity, influencer concentration, and weak source support.",
            "evidence": "Credible sources, official statements, independent confirmation, and observable market/on-chain data.",
        },
    }


# ---------------------------------------------------------------- grounded Q&A

def _find_asset(q: str):
    for asset in ASSETS:
        for token in (asset.symbol.lower(), asset.name.lower()):
            if re.search(rf"\b{re.escape(token)}\b", q):
                return asset
    return None


def _event_for(symbol: str):
    mine = sorted((e for e in EVENTS if symbol in e.assets), key=lambda e: (e.assets[0] != symbol, -e.impact_score))
    return mine[0] if mine else None


def _asset_answer(asset) -> tuple[str, list[str]]:
    event = _event_for(asset.symbol)
    if event and event.assets[0] == asset.symbol:
        direction = "down" if event.price_change < 0 else "up"
        tail = (
            "No credible confirmation appears in the dataset, so this is observed activity, not a validated signal."
            if event.evidence_score < 50
            else f"Supporting sources: {', '.join(s.name for s in event.sources[:3])}."
        )
        answer = (
            f"{asset.symbol} is {direction} {abs(event.price_change)}% after “{event.title}”. "
            f"Sentiment moved {event.sentiment_before}% → {event.sentiment_after}% ({event.shock_score:+.1f}σ), "
            f"volume {event.volume_change:+d}% and mentions {event.mention_change:+d}%. "
            f"Evidence is {event.evidence_score}/100 against a hype score of {event.hype_score}/100 — {event.verdict.lower()}. {tail}"
        )
        return answer, [event.id, *[s.name for s in event.sources[:2]]]
    if event:
        answer = (
            f"{asset.symbol} is {asset.change_24h:+.1f}% over 24h with sentiment at {asset.sentiment}% ({asset.sentiment_change:+d} pts), "
            f"status “{asset.status}”. It is linked to “{event.title}” (impact {event.impact_score}/100, evidence {event.evidence_score}/100)."
        )
        return answer, [event.id]
    answer = (
        f"No active event is attached to {asset.symbol}. It is {asset.change_24h:+.1f}% over 24h, sentiment is {asset.sentiment}% "
        f"({asset.sentiment_change:+d} pts), mention velocity {asset.mention_velocity:+d}%, status “{asset.status}”."
    )
    return answer, []


def _suggestions() -> list[str]:
    lead = max(EVENTS, key=lambda e: e.impact_score)
    risk = min(EVENTS, key=lambda e: e.evidence_score)
    return [f"Why is {lead.assets[0]} moving?", f"Is the {risk.assets[0]} move driven by hype?", "Which asset has the strongest bullish sentiment?"]


def _rules_answer(question: str) -> ChatResponse:
    q = question.lower().strip()
    asset = _find_asset(q)

    if re.search(r"\b(biggest|largest|strongest|most extreme)\b", q) and ("shock" in q) and not asset:
        event = max(EVENTS, key=lambda e: abs(e.shock_score))
        answer = (
            f"{event.assets[0]} has the largest detected sentiment shock: {event.shock_score:+.1f}σ. Bullish sentiment moved from "
            f"{event.sentiment_before}% to {event.sentiment_after}% after “{event.title}”. Impact is {event.impact_score}/100 with {event.confidence}% confidence."
        )
        citations = [event.id, *[s.name for s in event.sources[:2]]]
    elif re.search(r"\b(strongest|most|highest)\b", q) and ("bullish" in q or "sentiment" in q) and not asset:
        top = max(ASSETS, key=lambda a: a.sentiment)
        event = _event_for(top.symbol)
        if event and event.evidence_score < 50:
            note = f"Its narrative carries hype {event.hype_score}/100 against evidence {event.evidence_score}/100, so this is observed sentiment, not a validated trading signal."
        elif event:
            note = f"It is backed by evidence of {event.evidence_score}/100 for “{event.title}”."
        else:
            note = "No specific event is driving it in the dataset."
        answer = f"{top.symbol} has the strongest bullish sentiment at {top.sentiment}%. {note}"
        citations = [f"asset:{top.symbol}", *([event.id] if event else [])]
    elif not asset and (("high impact" in q and "low confirmation" in q) or any(w in q for w in ("low evidence", "unconfirmed", "unverified", "rumor", "rumour", "low confirmation"))):
        matches = [e for e in EVENTS if e.impact_score >= 70 and e.evidence_score < 50] or [min(EVENTS, key=lambda e: e.evidence_score)]
        parts = [f"{e.title} ({', '.join(e.assets)}): impact {e.impact_score}, hype {e.hype_score}, evidence {e.evidence_score}" for e in matches]
        answer = f"{len(matches)} event{'s' if len(matches) != 1 else ''} match: " + "; ".join(parts) + ". The market move is observable, but the claimed catalyst is not confirmed."
        citations = [e.id for e in matches]
    elif not asset and "hype" in q:
        event = max(EVENTS, key=lambda e: e.hype_score)
        answer = f"The highest hype is around “{event.title}” ({', '.join(event.assets)}): hype {event.hype_score}/100 versus evidence {event.evidence_score}/100 — {event.verdict.lower()}."
        citations = [event.id]
    elif asset:
        answer, citations = _asset_answer(asset)
    elif any(w in q for w in ("summary", "summarize", "overview", "what happened", "what's happening", "whats happening", "latest", "brief")):
        top = sorted(EVENTS, key=lambda e: e.impact_score, reverse=True)[:3]
        answer = "Top events by impact: " + " ".join(f"{i}) {e.assets[0]} — {e.title} (impact {e.impact_score}, evidence {e.evidence_score})." for i, e in enumerate(top, 1))
        citations = [e.id for e in top]
    else:
        leader = max(EVENTS, key=lambda e: e.impact_score)
        answer = (
            f"The highest-impact active event affects {', '.join(leader.assets)}: “{leader.title}”. Impact is {leader.impact_score}/100 with {leader.confidence}% confidence. "
            "Ask about a specific asset, the largest shock, bullish sentiment, or high-impact low-confirmation events for a focused readout."
        )
        citations = [leader.id]
    return ChatResponse(answer=answer, citations=citations, suggested_questions=_suggestions(), mode="rules")


def answer_question(question: str) -> ChatResponse:
    result = llm.ask(question, ASSETS, EVENTS, ALERTS)
    if result:
        if len(result["suggested_questions"]) < 3:
            result["suggested_questions"] = _suggestions()
        return ChatResponse(**result, mode="llm")
    return _rules_answer(question)
