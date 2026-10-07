"""Deterministic demo feed. Replace this module with provider adapters in production."""
from .models import Asset, Event, Source, TimelinePoint, Alert


def source(name: str, kind: str, credibility: int) -> Source:
    return Source(name=name, kind=kind, credibility=credibility)


def timeline(rows):
    return [TimelinePoint(**row) for row in rows]


ASSETS = [
    Asset(symbol="BTC", name="Bitcoin", asset_type="crypto", price=67421.80,
          change_24h=-4.8, volume=48_200_000_000, volume_change=142,
          sentiment=24, sentiment_change=-38, mention_velocity=320, impact=92,
          status="Sentiment shock", sparkline=[72,73,71,74,72,68,65,61,56,53,49,48]),
    Asset(symbol="ETH", name="Ethereum", asset_type="crypto", price=3548.62,
          change_24h=-2.1, volume=21_800_000_000, volume_change=63,
          sentiment=41, sentiment_change=-17, mention_velocity=84, impact=68,
          status="Elevated", sparkline=[63,64,62,63,61,59,58,57,55,56,54,53]),
    Asset(symbol="SOL", name="Solana", asset_type="crypto", price=182.44,
          change_24h=3.7, volume=5_900_000_000, volume_change=91,
          sentiment=72, sentiment_change=14, mention_velocity=127, impact=73,
          status="Event active", sparkline=[45,47,46,49,52,54,57,55,59,62,65,68]),
    Asset(symbol="XRP", name="XRP", asset_type="crypto", price=0.5264,
          change_24h=-0.6, volume=1_700_000_000, volume_change=18,
          sentiment=53, sentiment_change=-3, mention_velocity=22, impact=34,
          status="Monitoring", sparkline=[52,51,52,53,53,52,51,52,51,50,51,51]),
    Asset(symbol="DOGE", name="Dogecoin", asset_type="crypto", price=0.1421,
          change_24h=8.9, volume=3_400_000_000, volume_change=218,
          sentiment=81, sentiment_change=29, mention_velocity=412, impact=78,
          status="Hype risk", sparkline=[35,36,39,38,43,47,54,57,61,68,72,76]),
    Asset(symbol="NVDA", name="NVIDIA", asset_type="equity", price=126.57,
          change_24h=2.4, volume=391_000_000, volume_change=47,
          sentiment=76, sentiment_change=11, mention_velocity=66, impact=71,
          status="Event active", sparkline=[57,58,57,59,61,60,63,65,66,67,69,71]),
    Asset(symbol="TSLA", name="Tesla", asset_type="equity", price=249.83,
          change_24h=-1.8, volume=112_000_000, volume_change=39,
          sentiment=38, sentiment_change=-12, mention_velocity=73, impact=57,
          status="Elevated", sparkline=[61,60,58,59,57,55,56,53,52,51,50,49]),
    Asset(symbol="AAPL", name="Apple", asset_type="equity", price=227.91,
          change_24h=0.8, volume=58_000_000, volume_change=9,
          sentiment=64, sentiment_change=4, mention_velocity=14, impact=29,
          status="Normal", sparkline=[50,51,50,52,53,52,53,54,54,55,56,56]),
    Asset(symbol="AMD", name="AMD", asset_type="equity", price=171.36,
          change_24h=1.3, volume=54_000_000, volume_change=31,
          sentiment=69, sentiment_change=8, mention_velocity=41, impact=48,
          status="Monitoring", sparkline=[49,50,52,51,53,54,55,54,56,57,59,60]),
]


BTC_TIMELINE = timeline([
    {"time":"10:00", "sentiment":61, "price_index":100.0, "mentions":48, "label":"Baseline stable"},
    {"time":"10:15", "sentiment":63, "price_index":100.2, "mentions":51},
    {"time":"10:30", "sentiment":62, "price_index":99.9, "mentions":55, "label":"Normal sentiment"},
    {"time":"10:45", "sentiment":48, "price_index":99.1, "mentions":118, "label":"Regulatory event detected", "severity":"event"},
    {"time":"11:00", "sentiment":24, "price_index":96.8, "mentions":232, "label":"Sentiment shock confirmed", "severity":"shock"},
    {"time":"11:15", "sentiment":27, "price_index":95.2, "mentions":214, "label":"Market impact peaks", "severity":"event"},
    {"time":"11:30", "sentiment":31, "price_index":95.7, "mentions":176},
    {"time":"11:45", "sentiment":35, "price_index":96.1, "mentions":131, "label":"Stabilization begins"},
]);


DOGE_TIMELINE = timeline([
    {"time":"09:30", "sentiment":52, "price_index":100.0, "mentions":34, "label":"Normal activity"},
    {"time":"09:45", "sentiment":55, "price_index":100.1, "mentions":38},
    {"time":"10:00", "sentiment":67, "price_index":102.3, "mentions":93, "label":"Viral claim appears", "severity":"event"},
    {"time":"10:15", "sentiment":81, "price_index":108.9, "mentions":174, "label":"Mention velocity +412%", "severity":"shock"},
    {"time":"10:30", "sentiment":79, "price_index":107.2, "mentions":161, "label":"No official confirmation", "severity":"event"},
    {"time":"10:45", "sentiment":71, "price_index":105.8, "mentions":129},
]);


EVENTS = [
    Event(
        id="evt-btc-reg-1042", title="Digital asset custody rules tighten in joint regulator statement",
        timestamp="2026-10-04T10:42:00Z", age="18m ago", assets=["BTC", "ETH"],
        category="Regulation", importance="Critical", confidence=91,
        summary="A joint regulatory bulletin introduces stricter capital and custody requirements for institutions holding digital assets.",
        sentiment_before=62, sentiment_after=24, shock_score=-3.7, dominant_emotion="Fear",
        emotions={"Fear":61,"Uncertainty":22,"Anger":8,"Pessimism":6,"Optimism":3},
        price_change=-4.8, volume_change=142, mention_change=320, volatility=6.4,
        hype_score=58, evidence_score=93, impact_score=92,
        factors={"Sentiment shock":96,"Market movement":88,"Social activity":90,"News coverage":86,"Evidence strength":93},
        verdict="High-confidence event-driven reaction",
        sources=[source("Joint regulator bulletin","official",98), source("Global Markets Wire","news",91), source("Digital Assets Desk","news",86), source("Exchange order-book data","market",94)],
        explanation="BTC sentiment shifted sharply negative after a verified regulatory bulletin at 10:42 UTC. Bullish sentiment fell from 62% to 24%, a 3.7σ deviation from its rolling baseline. Negative discussion increased 3.2× while fear became the dominant emotion. BTC declined 4.8% and trading volume rose 142% in the same window. Multiple independent reports and market evidence support a high-confidence event-driven reaction rather than normal noise.",
        timeline=BTC_TIMELINE,
    ),
    Event(
        id="evt-doge-viral-1002", title="Unverified payment integration rumor accelerates across social channels",
        timestamp="2026-10-04T10:02:00Z", age="58m ago", assets=["DOGE"],
        category="Viral narrative", importance="High", confidence=64,
        summary="A viral post claims a major payment platform will integrate DOGE, but no company statement or credible independent report has appeared.",
        sentiment_before=52, sentiment_after=81, shock_score=3.2, dominant_emotion="Excitement",
        emotions={"Excitement":68,"Optimism":17,"Uncertainty":10,"Fear":3,"Anger":2},
        price_change=8.9, volume_change=218, mention_change=412, volatility=9.7,
        hype_score=89, evidence_score=31, impact_score=78,
        factors={"Sentiment shock":86,"Market movement":77,"Social activity":98,"News coverage":38,"Evidence strength":31},
        verdict="High hype / low confirmation",
        sources=[source("Viral social thread","social",29), source("Crypto community reposts","social",34), source("Spot market data","market",92)],
        explanation="DOGE discussion accelerated 4.1× after an unverified payment-integration claim circulated. Sentiment reached 81% bullish and price rose 8.9%, but activity is concentrated around a small group of social accounts. No official announcement or credible independent confirmation is available. The observed move is therefore classified as high hype with low evidence; this is not a prediction of reversal.",
        timeline=DOGE_TIMELINE,
    ),
    Event(
        id="evt-nvda-orders-0935", title="NVIDIA supplier commentary signals sustained accelerator demand",
        timestamp="2026-10-04T09:35:00Z", age="1h 25m", assets=["NVDA", "AMD"],
        category="Corporate", importance="High", confidence=87,
        summary="Independent supply-chain commentary points to continued data-center accelerator orders into the next quarter.",
        sentiment_before=65, sentiment_after=76, shock_score=1.8, dominant_emotion="Optimism",
        emotions={"Optimism":54,"Excitement":27,"Uncertainty":12,"Fear":5,"Pessimism":2},
        price_change=2.4, volume_change=47, mention_change=66, volatility=2.8,
        hype_score=52, evidence_score=84, impact_score=71,
        factors={"Sentiment shock":52,"Market movement":63,"Social activity":58,"News coverage":76,"Evidence strength":84},
        verdict="Evidence-led positive repricing",
        sources=[source("Supplier earnings call","official",89), source("Semiconductor Ledger","news",87), source("Options flow data","market",90)],
        explanation="NVDA sentiment improved by 11 points following corroborated supplier commentary about accelerator demand. Price gained 2.4% on 47% higher volume. The 1.8σ shift is elevated but not an extreme shock. Credible supply-chain reporting and market participation suggest an evidence-led positive repricing.",
        timeline=timeline([
            {"time":"09:15","sentiment":64,"price_index":100,"mentions":41},
            {"time":"09:30","sentiment":65,"price_index":100.2,"mentions":43},
            {"time":"09:45","sentiment":71,"price_index":101.1,"mentions":59,"label":"Supplier comments indexed","severity":"event"},
            {"time":"10:00","sentiment":76,"price_index":102.4,"mentions":72,"label":"Positive repricing","severity":"event"},
            {"time":"10:15","sentiment":74,"price_index":102.2,"mentions":65},
        ]),
    ),
    Event(
        id="evt-sol-validator-0850", title="Solana validator upgrade clears final network vote",
        timestamp="2026-10-04T08:50:00Z", age="2h 10m", assets=["SOL"],
        category="Protocol upgrade", importance="High", confidence=94,
        summary="Validators approved a throughput-focused network upgrade after completion of the public test phase.",
        sentiment_before=58, sentiment_after=72, shock_score=2.1, dominant_emotion="Optimism",
        emotions={"Optimism":59,"Excitement":25,"Uncertainty":9,"Fear":4,"Pessimism":3},
        price_change=3.7, volume_change=91, mention_change=127, volatility=4.2,
        hype_score=61, evidence_score=96, impact_score=73,
        factors={"Sentiment shock":68,"Market movement":70,"Social activity":72,"News coverage":63,"Evidence strength":96},
        verdict="Strong fundamental confirmation",
        sources=[source("Solana governance record","official",99), source("Validator telemetry","market",97), source("Chain Bulletin","news",84)],
        explanation="SOL sentiment rose 14 points after the validator vote was recorded on-chain. A 3.7% price increase, 91% higher volume, and broad validator participation confirm meaningful market attention. The 2.1σ move is significant and supported by direct protocol evidence.",
        timeline=timeline([
            {"time":"08:30","sentiment":57,"price_index":100,"mentions":31},
            {"time":"08:45","sentiment":58,"price_index":100.1,"mentions":34},
            {"time":"09:00","sentiment":66,"price_index":101.8,"mentions":59,"label":"Vote finalized","severity":"event"},
            {"time":"09:15","sentiment":72,"price_index":103.7,"mentions":77,"label":"Significant shift","severity":"shock"},
            {"time":"09:30","sentiment":70,"price_index":103.3,"mentions":68},
        ]),
    ),
    Event(
        id="evt-tsla-recall-0812", title="Tesla issues limited software recall notice",
        timestamp="2026-10-04T08:12:00Z", age="2h 48m", assets=["TSLA"],
        category="Corporate", importance="Medium", confidence=89,
        summary="A formal notice covers a limited vehicle cohort and identifies an over-the-air software remedy.",
        sentiment_before=50, sentiment_after=38, shock_score=-1.6, dominant_emotion="Uncertainty",
        emotions={"Uncertainty":47,"Fear":24,"Pessimism":18,"Anger":7,"Optimism":4},
        price_change=-1.8, volume_change=39, mention_change=73, volatility=3.1,
        hype_score=66, evidence_score=88, impact_score=57,
        factors={"Sentiment shock":48,"Market movement":46,"Social activity":61,"News coverage":69,"Evidence strength":88},
        verdict="Confirmed event / moderate impact",
        sources=[source("Safety regulator filing","official",98), source("Tesla service notice","official",96), source("Automotive Press","news",82)],
        explanation="TSLA sentiment weakened after a confirmed software recall notice. The reaction is elevated rather than extreme: sentiment declined 12 points and shares fell 1.8% on 39% higher volume. Official documentation confirms the event, while the limited scope supports a moderate—not systemic—impact classification.",
        timeline=timeline([
            {"time":"08:00","sentiment":51,"price_index":100,"mentions":29},
            {"time":"08:15","sentiment":50,"price_index":99.9,"mentions":31},
            {"time":"08:30","sentiment":42,"price_index":98.8,"mentions":48,"label":"Recall notice detected","severity":"event"},
            {"time":"08:45","sentiment":38,"price_index":98.2,"mentions":53,"label":"Reaction elevated","severity":"event"},
            {"time":"09:00","sentiment":40,"price_index":98.4,"mentions":46},
        ]),
    ),
]


ALERTS = [
    Alert(id="a1", kind="SENTIMENT SHOCK", title="BTC negative sentiment accelerated", message="Bullish sentiment fell 38 points in 15 minutes. Potential cause: regulatory bulletin.", asset="BTC", impact=92, timestamp="10:52 UTC", severity="critical"),
    Alert(id="a2", kind="HYPE RISK", title="DOGE rally lacks confirmation", message="Mention velocity rose 412%, while evidence remains limited to social sources.", asset="DOGE", impact=78, timestamp="10:21 UTC", severity="warning"),
    Alert(id="a3", kind="MAJOR EVENT", title="SOL validator upgrade confirmed", message="On-chain governance data confirms the network upgrade vote.", asset="SOL", impact=73, timestamp="09:02 UTC", severity="positive"),
    Alert(id="a4", kind="MARKET IMPACT", title="NVDA volume expansion", message="Price gained 2.4% alongside 47% higher trading volume.", asset="NVDA", impact=71, timestamp="09:58 UTC", severity="info"),
]


SENTIMENT_HISTORY = {
    asset.symbol: [max(10, min(90, asset.sentiment + offset)) for offset in (-3, 1, 0, 2, -1, 1, -2, 0)]
    for asset in ASSETS
}
SENTIMENT_HISTORY["BTC"] = [61, 63, 62, 60, 61, 59, 62, 24]
SENTIMENT_HISTORY["DOGE"] = [48, 50, 49, 47, 51, 50, 48, 81]
