# EventPulse AI — 3-Minute Demo Script

## Before you go on (2 min)
- [ ] Run `run.bat` / `./run.sh`; confirm the dashboard loads. Click **↺ Reset**.
- [ ] Browser full-screen, zoom 100–110%, notifications off. Open `http://localhost:3000` on the **Overview** tab.
- [ ] Optional: set `ANTHROPIC_API_KEY` first so the analyst is Claude-backed (sidebar shows **CLAUDE ON**; otherwise **RULES**).
- [ ] Rehearse once through; the whole flow works offline, so bad venue Wi-Fi can't break it.

## The pitch (≈3:00)

**0:00 — Hook (20s)**
"When BTC drops 5%, three things could be true: real news moved it, a rumor moved it, or it's noise. Traders and analysts can't tell fast enough. EventPulse tells you which — and shows its evidence."

**0:20 — Act 1: a verified shock (40s)** *(Overview)*
Point at the top card and the chart. "A joint regulatory bulletin lands at 10:42. Bullish sentiment collapses from 62% to 24% — a **3.7σ shock** against its own baseline. Price −4.8%, volume +142%." Click the card: show **evidence 93**, the sources with credibility scores, and the factor breakdown. "Every score is explainable."

**1:00 — Act 2: hype vs reality (40s)** *(Hype Radar)*
"Now DOGE: +8.9%, sentiment 81%, mentions +412%. Looks just as dramatic — but **evidence is 31**. One viral thread, no official confirmation. The radar separates *crowded truth* from *unconfirmed signal*. That distinction is the product."

**1:40 — Act 3: live breaking event (50s)** *(press ⚡ Inject event)*
"Let's watch it work in real time." The dashboard re-scores, the new card flashes, the drawer opens: ETH exchange withdrawal pause, impact 94. "Official notice, news, and on-chain outflows all agree — high evidence, so it's credible." Press **Inject** again for the XRP spoofed-headline case: "Hype 94, evidence 12 — flagged immediately."

**2:30 — Act 4: ask anything (20s)** *(Ctrl+K)*
Ask: *"Which events are high impact but low confirmation?"* Click a citation chip — it opens the exact event. "Answers are grounded in the dashboard's data, cited, and never give trading advice."

**2:50 — Close (10s)**
"Real-time shock detection, hype-vs-evidence scoring, and cited explanations. Plug in live market, news, and social feeds and this runs on real data."

## Likely judge questions
**Is the data real?** No — it's a seeded demo feed, labelled DEMO FEED on screen, and injected events are tagged SIMULATED. The shock detector and Q&A grounding are real code; the architecture has a clean provider boundary (`seed.py`) to swap in live adapters.

**How is the shock computed?** Current sentiment vs. a rolling baseline, in standard deviations, with σ floored at 10 sentiment points so quiet periods don't trigger false alarms.

**How do you stop the AI from hallucinating?** The analyst only sees the current dashboard data, must answer from it, may only cite event IDs and source names that exist (anything else is dropped), and falls back to a deterministic engine on any failure. The UI shows which engine answered.

**Is this trading advice?** No. It reports observed activity and estimated impact, and says so in the UI and in the model's instructions.

**What's next?** Live adapters (exchange/market data, news APIs, social streams), real sentiment models, backtested impact weights, user-defined alert thresholds.

## If something goes wrong
- **Page blank / error state:** hit *Retry connection*; confirm the terminal shows the server running.
- **Demo state looks off:** click **↺ Reset**.
- **Analyst slow or erroring:** it auto-falls back to the rules engine within ~15s; ask a suggested question to stay on the happy path.
