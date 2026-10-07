"""Scripted 'breaking event' injector for live demos.

Mutates the seeded in-memory feed in place (so every module sharing the lists
sees the change). Injected events are flagged `simulated=True` and the UI says so.
"""
import copy

from .engine import classify_shock
from .models import Alert, Event, TimelinePoint
from .seed import ALERTS, ASSETS, EVENTS, SENTIMENT_HISTORY, source

_ORIGINAL = {
    "assets": copy.deepcopy(ASSETS),
    "events": copy.deepcopy(EVENTS),
    "alerts": copy.deepcopy(ALERTS),
    "history": copy.deepcopy(SENTIMENT_HISTORY),
}
_cursor = 0


def _timeline(sentiments, prices, mentions, labels):
    times = ["09:45", "10:00", "10:15", "10:30", "10:45", "11:00"]
    rows = []
    for t, s, p, m, (label, sev) in zip(times, sentiments, prices, mentions, labels):
        rows.append(TimelinePoint(time=t, sentiment=s, price_index=p, mentions=m, label=label, severity=sev or "normal"))
    return rows


SCENARIOS = [
    {
        "symbol": "ETH",
        "patch": dict(price=3321.40, change_24h=-6.4, volume_change=188, sentiment=9, sentiment_change=-32,
                      mention_velocity=356, impact=94, status="Sentiment shock",
                      sparkline=[63, 62, 61, 59, 58, 57, 55, 56, 54, 49, 43, 37]),
        "event": dict(
            id="evt-eth-halt-sim", title="Major exchange pauses ETH withdrawals pending security review",
            timestamp="2026-10-04T10:58:00Z", age="just now", assets=["ETH"], category="Exchange risk",
            importance="Critical", confidence=82,
            summary="An exchange status notice pauses ETH withdrawals while a security review is carried out; on-chain outflows are accelerating.",
            sentiment_before=41, sentiment_after=9, dominant_emotion="Fear",
            emotions={"Fear":66,"Uncertainty":19,"Anger":8,"Pessimism":5,"Optimism":2},
            price_change=-6.4, volume_change=188, mention_change=356, volatility=7.9,
            hype_score=63, evidence_score=78, impact_score=94,
            factors={"Sentiment shock":97,"Market movement":91,"Social activity":92,"News coverage":71,"Evidence strength":78},
            verdict="Credible exchange-risk event / contagion watch",
            sources=[source("Exchange status notice","official",88), source("Global Markets Wire","news",91), source("On-chain withdrawal flow","market",93)],
            explanation="ETH sentiment collapsed after an exchange status notice paused withdrawals. Bullish sentiment fell from 41% to 9% while mentions rose 3.6×. Price declined 6.4% on 188% higher volume, and on-chain outflow data corroborates the notice. Official and independent sources agree on the facts; what remains unconfirmed is the scope of the security review, so the system rates evidence as strong but incomplete.",
            timeline=_timeline([41,40,41,39,22,9], [100,100.1,99.9,99.2,96.9,93.6], [84,88,86,121,284,356],
                               [("Baseline stable",None),(None,None),(None,None),("Status notice detected","event"),("Outflows accelerate","event"),("Sentiment shock confirmed","shock")]),
        ),
        "alert": dict(id="sim-eth", kind="SENTIMENT SHOCK", title="ETH sentiment collapsed after withdrawal pause",
                      message="Bullish sentiment fell 32 points in 30 minutes. Cause: exchange withdrawal pause, corroborated by on-chain outflows.",
                      asset="ETH", impact=94, timestamp="11:00 UTC", severity="critical"),
    },
    {
        "symbol": "XRP",
        "patch": dict(price=0.5590, change_24h=5.6, volume_change=164, sentiment=84, sentiment_change=31,
                      mention_velocity=540, impact=82, status="Hype risk",
                      sparkline=[52, 51, 52, 53, 53, 52, 51, 52, 58, 66, 74, 80]),
        "event": dict(
            id="evt-xrp-spoof-sim", title="Fabricated 'ETF approved' headline spreads from a spoofed news account",
            timestamp="2026-10-04T10:55:00Z", age="just now", assets=["XRP"], category="Misinformation",
            importance="High", confidence=74,
            summary="A screenshot of an 'ETF approval' headline is circulating widely, but no matching statement exists from the named regulator or any verified outlet.",
            sentiment_before=53, sentiment_after=84, dominant_emotion="Excitement",
            emotions={"Excitement":71,"Optimism":15,"Uncertainty":9,"Fear":3,"Anger":2},
            price_change=5.6, volume_change=164, mention_change=540, volatility=8.8,
            hype_score=94, evidence_score=12, impact_score=82,
            factors={"Sentiment shock":88,"Market movement":74,"Social activity":99,"News coverage":18,"Evidence strength":12},
            verdict="High hype / no credible confirmation",
            sources=[source("Spoofed news account","social",8), source("Reposted screenshots","social",21), source("Spot market data","market",90)],
            explanation="XRP discussion accelerated 6.4× after a screenshot of an 'ETF approved' headline began circulating. Sentiment jumped from 53% to 84% and price rose 5.6%, but the claim traces to a single unverified account and no regulator filing or credible outlet reports it. The system classifies the move as high hype with very low evidence; this describes observed activity and is not a prediction of reversal.",
            timeline=_timeline([53,52,54,55,70,84], [100,100,100.1,100.2,103.4,105.6], [22,24,23,40,150,141],
                               [("Normal activity",None),(None,None),(None,None),("Screenshot appears","event"),("Mention velocity +540%","shock"),("No official confirmation","event")]),
        ),
        "alert": dict(id="sim-xrp", kind="HYPE RISK", title="XRP rally rests on an unverified headline",
                      message="Mentions up 540% with evidence at 12/100: no regulator filing or verified outlet matches the claim.",
                      asset="XRP", impact=82, timestamp="11:00 UTC", severity="warning"),
    },
]


def inject_next() -> Event:
    """Apply the next scripted scenario and return the new event."""
    global _cursor
    sc = SCENARIOS[_cursor % len(SCENARIOS)]
    _cursor += 1
    sym = sc["symbol"]

    idx = next(i for i, a in enumerate(ASSETS) if a.symbol == sym)
    ASSETS[idx] = ASSETS[idx].model_copy(update=sc["patch"])
    SENTIMENT_HISTORY[sym] = SENTIMENT_HISTORY[sym][:-1] + [sc["patch"]["sentiment"]]

    shock = classify_shock(SENTIMENT_HISTORY[sym])["z_score"]
    event = Event(**sc["event"], shock_score=shock, simulated=True)
    EVENTS[:] = [e for e in EVENTS if e.id != event.id]
    EVENTS.insert(0, event)
    ALERTS[:] = [a for a in ALERTS if a.id != sc["alert"]["id"]]
    ALERTS.insert(0, Alert(**sc["alert"]))
    return event


def reset() -> None:
    global _cursor
    _cursor = 0
    ASSETS[:] = copy.deepcopy(_ORIGINAL["assets"])
    EVENTS[:] = copy.deepcopy(_ORIGINAL["events"])
    ALERTS[:] = copy.deepcopy(_ORIGINAL["alerts"])
    SENTIMENT_HISTORY.clear()
    SENTIMENT_HISTORY.update(copy.deepcopy(_ORIGINAL["history"]))
