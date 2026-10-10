const state = {
  data: null,
  view: 'overview',
  asset: 'BTC',
  timeframe: '24H',
  unread: true,
  query: '',
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const formatCompact = (value) => new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(value);
const signed = (value, suffix = '%') => `${value > 0 ? '+' : ''}${value}${suffix}`;
const esc = (v) => String(v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const simTag = (e) => e.simulated ? '<span class="sim-tag">SIMULATED</span>' : '';
const tone = (value) => value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';

const icons = {
  logo: `<svg viewBox="0 0 32 32" fill="none"><path d="M3 18h6l3-9 5 16 4-12 3 5h5" stroke="currentColor" stroke-width="2"/><circle cx="27" cy="18" r="2" fill="currentColor"/></svg>`,
  overview: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>`,
  markets: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 18l5-6 4 3 7-9"/><path d="M15 6h5v5"/></svg>`,
  events: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 22a9 9 0 1 0-9-9"/><path d="M3 22l3-3M12 7v6l4 2"/></svg>`,
  sentiment: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 12h4l2-7 4 14 3-9 2 2h3"/></svg>`,
  hype: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v3M22 12h-3M12 22v-3M2 12h3"/></svg>`,
  alerts: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></svg>`,
  ai: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 3l2 5 5 2-5 2-2 5-2-5-5-2 5-2 2-5Z"/><path d="M19 15l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2Z"/></svg>`,
};

const navItems = [
  ['overview','Overview'], ['markets','Markets'], ['events','Events'], ['sentiment','Sentiment'],
  ['hype','Hype Radar'], ['alerts','Alerts'], ['ai','AI Analyst'],
];

function renderShell() {
  $('#sidebar').innerHTML = `
    <div class="brand"><div class="brand-mark">${icons.logo}</div><div class="brand-name">EventPulse AI<small>INTELLIGENCE SYSTEM</small></div></div>
    <div class="nav-group">Workspace</div>
    <nav>${navItems.map(([id,label]) => `<button class="nav-item ${state.view===id?'active':''}" data-view="${id}">${icons[id]}<span>${label}</span>${id==='alerts'?`<b class="badge">${state.data.alerts.length}</b>`:''}</button>`).join('')}</nav>
    <div class="system-card"><div class="status-line"><span><i class="status-dot"></i>BITGET LIVE</span><span>${state.data.meta.llm?'QWEN POWERED':'QWEN KEY NEEDED'}</span></div><strong>BITGET MARKET DATA</strong><p>${state.data.meta.live_assets} crypto assets live from Bitget<br>${state.data.meta.llm?'Qwen powers analysis':'Add BITGET_QWEN_API_KEY in Render for Qwen analysis'}</p></div>`;
  $('#topbar').innerHTML = `
    <div class="page-heading"><h1>${navItems.find(n=>n[0]===state.view)?.[1] || 'Overview'}</h1><p>BITGET MARKET DATA · ${new Date(state.data.meta.as_of).toISOString().replace('T',' · ').slice(0,19)} UTC</p></div>
    <div class="top-actions"><span class="feed-pill"><i class="status-dot"></i>BITGET LIVE</span><button class="ghost-button" id="inject" title="Inject a scripted breaking event (Ctrl+Shift+E)">⚡ INJECT EVENT</button><button class="icon-button" id="reset" title="Reset demo data" aria-label="Reset demo">↺</button><button class="icon-button" id="bell" aria-label="Alerts">${icons.alerts}${state.unread?'<i class="unread-dot"></i>':''}</button><button class="ask-button" id="open-ai">ASK EVENTPULSE <span>⌘ K</span></button></div>`;
}

function bindGlobalEvents() {
  document.addEventListener('click', event => {
    const nav = event.target.closest('[data-view]');
    if (nav) { state.view = nav.dataset.view; renderShell(); renderView(); return; }
    const detail = event.target.closest('[data-event]');
    if (detail) { if (detail.closest('#command')) closeAI(); openEvent(detail.dataset.event); }
    const asset = event.target.closest('[data-asset]');
    if (asset) { state.asset=asset.dataset.asset; state.view='sentiment'; renderShell(); renderSentiment(); showNotice(`${state.asset} intelligence context loaded`); }
    if (event.target.closest('#open-ai')) openAI();
    if (event.target.closest('#inject')) injectEvent();
    if (event.target.closest('#reset')) resetDemo();
    if (event.target.closest('#bell')) { state.unread=false; state.view='alerts'; renderShell(); renderView(); }
    if (event.target.id === 'detail-modal' || event.target.closest('.close-btn')) closeModal();
  });
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase()==='k') { event.preventDefault(); openAI(); }
    if ((event.metaKey || event.ctrlKey) && event.shiftKey && event.key.toLowerCase()==='e') { event.preventDefault(); injectEvent(); }
    if (event.key === 'Escape') { closeModal(); closeAI(); }
  });
}

function renderView() {
  const views = {overview:renderOverview,markets:renderMarkets,events:renderEvents,sentiment:renderSentiment,hype:renderHype,alerts:renderAlerts,ai:renderAnalyst};
  (views[state.view] || renderOverview)();
}

function impactClass(event) {
  if (event.evidence_score < 45) return 'warning';
  if (event.impact_score >= 85) return 'critical';
  return 'positive-card';
}

function eventCard(event) {
  return `<article class="event-card ${impactClass(event)} ${event.id===state.freshId?'fresh':''}" data-event="${event.id}">
    <div class="event-top"><span class="asset-tag">${event.assets.join(' · ')}</span><span class="category">${event.category}</span>${simTag(event)}<span class="age">${event.age}</span></div>
    <h3>${event.title}</h3>
    <div class="card-gauges">
      <div><div class="gauge-label"><span>HYPE</span><b>${event.hype_score}</b></div><div class="bar hype"><i style="width:${event.hype_score}%"></i></div></div>
      <div><div class="gauge-label"><span>EVIDENCE</span><b>${event.evidence_score}</b></div><div class="bar evidence ${event.evidence_score<45?'low':''}"><i style="width:${event.evidence_score}%"></i></div></div>
    </div>
    <div class="event-footer"><span class="verdict">${event.verdict}</span><div class="impact-ring" style="--score:${event.impact_score}"><span>${event.impact_score}</span></div></div>
  </article>`;
}

function linePath(values, width=700, height=210, pad=18, minValue=0, maxValue=100) {
  const dx = (width-pad*2)/(values.length-1);
  return values.map((v,i) => `${i?'L':'M'}${(pad+i*dx).toFixed(1)},${(height-pad-(v-minValue)/(maxValue-minValue)*(height-pad*2)).toFixed(1)}`).join(' ');
}

function sentimentChart(event) {
  const width=700, height=210, pad=18;
  const values=event.timeline.map(p=>p.sentiment);
  const price=event.timeline.map(p=>Math.max(0,Math.min(100,(p.price_index-92)*8)));
  const path=linePath(values,width,height,pad);
  const area=`${path} L${width-pad},${height-pad} L${pad},${height-pad} Z`;
  const points=event.timeline.map((p,i)=>{
    const x=pad+i*(width-pad*2)/(values.length-1), y=height-pad-p.sentiment/100*(height-pad*2);
    return `<circle class="chart-point ${p.severity==='shock'?'shock':''}" cx="${x}" cy="${y}" r="${p.severity==='shock'?5:3}"/><text class="chart-label" x="${x}" y="${height+3}" text-anchor="middle">${p.time}</text>${p.severity!=='normal'?`<line class="event-marker" x1="${x}" y1="${pad}" x2="${x}" y2="${height-pad}"/>`:''}`;
  }).join('');
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height+12}" preserveAspectRatio="none" aria-label="Sentiment timeline">
    <defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#50e3c2" stop-opacity=".22"/><stop offset="1" stop-color="#50e3c2" stop-opacity="0"/></linearGradient></defs>
    ${[25,50,75].map(v=>`<line class="chart-grid" x1="${pad}" y1="${height-pad-v/100*(height-pad*2)}" x2="${width-pad}" y2="${height-pad-v/100*(height-pad*2)}"/>`).join('')}
    <path class="chart-area" d="${area}"/><path class="chart-price" d="${linePath(price,width,height,pad)}"/><path class="chart-line" d="${path}"/>${points}
  </svg>`;
}

function statusClass(status) {
  return status.includes('shock') ? 'danger' : status.includes('Hype') || status.includes('Elevated') ? 'warn' : status.includes('active') ? 'live' : '';
}

function sparkline(asset) {
  return `<svg class="spark" viewBox="0 0 70 24"><path d="${linePath(asset.sparkline,70,24,2,30,80)}" fill="none" stroke="${asset.change_24h>=0?'#50e3c2':'#ff626a'}" stroke-width="1.4"/></svg>`;
}

function marketTable(assets=state.data.assets) {
  return `<div class="panel"><div class="panel-head"><h3>Market impact matrix</h3><span class="eyebrow">Observed · 24H</span></div><div style="overflow:auto"><table class="market-table"><thead><tr><th>Asset</th><th>Price / trend</th><th>Volume</th><th>Sentiment</th><th>Mentions</th><th>Impact</th><th>Status</th></tr></thead><tbody>
    ${assets.map(a=>`<tr data-asset="${a.symbol}"><td><div class="asset-cell"><span class="coin">${a.symbol.slice(0,2)}</span><div><strong>${a.symbol}</strong><small>${a.name}</small></div></div></td><td class="${tone(a.change_24h)}">${signed(a.change_24h)} ${sparkline(a)}</td><td>$${formatCompact(a.volume)} <small class="${tone(a.volume_change)}">${signed(a.volume_change)}</small></td><td>${a.sentiment}% <small class="${tone(a.sentiment_change)}">${signed(a.sentiment_change,' pts')}</small></td><td class="${a.mention_velocity>200?'warning-text':''}">${signed(a.mention_velocity)}</td><td><strong>${a.impact}</strong></td><td><span class="status ${statusClass(a.status)}">${a.status}</span></td></tr>`).join('')}
    </tbody></table></div></div>`;
}

function hypeRadar() {
  const events=state.data.events;
  return `<div class="panel"><div class="panel-head"><h3>Hype radar</h3><span class="eyebrow">Evidence →</span></div><div class="radar-wrap"><div class="quadrant"><span class="quad-label tl">Unconfirmed signal</span><span class="quad-label tr">Crowded truth</span><span class="quad-label bl">Low attention</span><span class="quad-label br">Quiet evidence</span><span class="axis-y">HYPE ↑</span><span class="axis-x">EVIDENCE →</span>${events.map((e,i)=>{let b=e.hype_score;for(let j=0;j<i;j++){const o=events[j],ob=o._by??o.hype_score;if(Math.abs(o.evidence_score-e.evidence_score)<7&&Math.abs(ob-b)<9)b=ob+9}e._by=b;return `<button class="bubble ${e.evidence_score<50?'risk':'verified'}" style="left:${e.evidence_score}%;bottom:${Math.min(b,94)}%" data-event="${e.id}" title="${esc(e.title)}">${e.assets[0]}</button>`}).join('')}</div></div></div>`;
}

function renderOverview() {
  const {mood,stats,events}=state.data;
  const focus=events[0];
  $('#content').innerHTML=`<div class="reveal">
    <section class="hero-strip">
      <div class="metric primary"><span class="eyebrow">Market mood</span><div class="metric-value">${mood.score}% <small>${mood.label}</small></div><div class="metric-note">Broad sentiment across monitored assets</div><div class="mini-bars">${[12,16,20,17,24,28,23,30,26,32].map(v=>`<i style="height:${v}px"></i>`).join('')}</div></div>
      <div class="metric"><span class="eyebrow">Market impact</span><div class="metric-value">${stats.market_impact}<small>/100</small></div><div class="metric-note positive">High observed activity</div></div>
      <div class="metric"><span class="eyebrow">Active events</span><div class="metric-value">${String(stats.active_events).padStart(2,'0')}</div><div class="metric-note">${stats.verified_events} verified · ${stats.developing_events} developing</div></div>
      <div class="metric"><span class="eyebrow">Sentiment shocks</span><div class="metric-value negative">${String(stats.sentiment_shocks).padStart(2,'0')}</div><div class="metric-note negative">Requires attention</div></div>
    </section>
    <section class="section"><div class="section-head"><div class="section-title"><h2>Live events</h2><span class="count">${events.length}</span></div><button class="link-btn" data-view="events">VIEW ALL EVENTS →</button></div><div class="event-grid">${events.slice(0,3).map(eventCard).join('')}</div></section>
    <section class="section analysis-grid"><div class="panel"><div class="panel-head"><h3>Sentiment shock monitor · ${focus.assets[0]}</h3><span class="eyebrow">15-MIN BUCKETS</span></div><div class="chart-wrap"><div class="chart-summary"><strong>${focus.sentiment_after}%</strong><span class="shock">${focus.shock_score}σ · SENTIMENT SHOCK</span></div>${sentimentChart(focus)}</div><div class="chart-legend"><span><i></i>Sentiment</span><span><i class="price"></i>Price index</span><span class="negative">Vertical markers indicate detected events</span></div></div>${hypeRadar()}</section>
    <section class="section">${marketTable()}</section>
  </div>`;
}

function renderMarkets() {
  $('#content').innerHTML=`<div class="reveal"><div class="section-head"><div><span class="eyebrow">Cross-asset monitor</span><h2 style="font-size:22px;margin:7px 0 0">Markets under observation</h2></div><span class="feed-pill"><i class="status-dot"></i>9 ASSETS LIVE</span></div>${marketTable()}</div>`;
}

function renderEvents() {
  const events=state.data.events;
  $('#content').innerHTML=`<div class="reveal page-grid"><div class="page-card"><span class="eyebrow">Detection stream</span><h2>Active market events</h2><p>Events are extracted, clustered, and scored against price, volume, sentiment, social activity, and source evidence.</p><div class="event-list">${events.map(e=>`<div class="event-row" data-event="${e.id}"><span class="asset-tag">${e.assets[0]}</span><div><h3>${e.title}</h3><p>${e.category} · ${e.confidence}% confidence · ${e.age}</p></div><span class="status ${impactClass(e)==='critical'?'danger':impactClass(e)==='warning'?'warn':'live'}">${e.importance}</span><span class="score-big">${e.impact_score}</span></div>`).join('')}</div></div><div><div class="page-card"><span class="eyebrow">Scoring model</span><h2>Explainable by design</h2>${Object.entries(state.data.methodology).map(([k,v])=>`<div class="method-box"><strong>${k.toUpperCase()}</strong><p>${v}</p></div>`).join('')}</div></div></div>`;
}

function renderSentiment() {
  const events=state.data.events;
  const selected=events.find(e=>e.assets.includes(state.asset)) || events[0];
  $('#content').innerHTML=`<div class="reveal"><div class="section-head"><div><span class="eyebrow">Anomaly detection</span><h2 style="font-size:22px;margin:7px 0 0">Sentiment shock monitor</h2></div><div class="tabs">${events.map(e=>`<button data-sentiment-asset="${e.assets[0]}" class="${selected.assets[0]===e.assets[0]?'active':''}">${e.assets[0]}</button>`).join('')}</div></div><div class="analysis-grid"><div class="panel"><div class="panel-head"><h3>${selected.assets[0]} rolling sentiment</h3><span class="status ${Math.abs(selected.shock_score)>3?'danger':'warn'}">${Math.abs(selected.shock_score)>3?'SHOCK':'ELEVATED'}</span></div><div class="chart-wrap"><div class="chart-summary"><strong>${selected.sentiment_after}%</strong><span class="${selected.shock_score<0?'negative':'positive'}">${selected.shock_score>0?'+':''}${selected.shock_score}σ from baseline</span></div>${sentimentChart(selected)}</div></div><div class="page-card"><span class="eyebrow">Current read</span><h2>${selected.dominant_emotion} dominates</h2><p>Emotion distribution derived from the event's associated news and social corpus.</p>${Object.entries(selected.emotions).map(([name,val])=>`<div class="factor-row"><span>${name}</span><div class="bar"><i style="width:${val}%;background:${name==='Fear'||name==='Pessimism'?'var(--red)':name==='Uncertainty'?'var(--amber)':'var(--cyan)'}"></i></div><b>${val}</b></div>`).join('')}<div class="method-box"><strong>DETECTION RULE</strong><p>&lt;1σ normal · 1–2σ elevated · 2–3σ significant · &gt;3σ sentiment shock</p></div></div></div></div>`;
  $$('[data-sentiment-asset]').forEach(btn=>btn.addEventListener('click',()=>{state.asset=btn.dataset.sentimentAsset;renderSentiment()}));
}

function renderHype() {
  $('#content').innerHTML=`<div class="reveal"><div class="section-head"><div><span class="eyebrow">Narrative verification</span><h2 style="font-size:22px;margin:7px 0 0">Hype vs reality engine</h2></div></div><div class="analysis-grid">${hypeRadar()}<div class="page-card"><span class="eyebrow">Priority review</span><h2>DOGE confirmation gap</h2><p>Social momentum is materially outpacing credible confirmation.</p><div class="detail-score-row" style="grid-template-columns:1fr 1fr"><div class="detail-score"><small>Hype</small><strong class="warning-text">89</strong></div><div class="detail-score"><small>Evidence</small><strong class="negative">31</strong></div></div><div class="alert-card warning"><span class="eyebrow">HIGH HYPE / LOW CONFIRMATION</span><h3>Payment integration claim is unverified</h3><p>Social concentration is high and no official source has confirmed the narrative.</p></div></div></div><section class="section"><div class="event-grid">${state.data.events.slice().sort((a,b)=>(b.hype_score-b.evidence_score)-(a.hype_score-a.evidence_score)).slice(0,3).map(eventCard).join('')}</div></section></div>`;
}

function renderAlerts() {
  $('#content').innerHTML=`<div class="reveal page-grid"><div><div class="section-head"><div><span class="eyebrow">Triggered intelligence</span><h2 style="font-size:22px;margin:7px 0 0">Alert stream</h2></div><span class="count">${state.data.alerts.length} ACTIVE</span></div>${state.data.alerts.map(a=>`<article class="alert-card ${a.severity==='positive'?'positive-card':a.severity}"><span class="eyebrow">${a.kind}</span><h3>${a.asset} · ${a.title}</h3><p>${a.message}</p><div class="alert-meta"><span>Impact ${a.impact}/100</span><span>${a.timestamp}</span></div></article>`).join('')}</div><div class="page-card"><span class="eyebrow">Alert controls</span><h2>Signal thresholds</h2><p>Alerts report detected conditions. They do not represent guaranteed trading signals.</p>${[['Shock threshold','> 3σ'],['Impact threshold','> 70'],['Mention velocity','> 100%'],['Evidence risk','< 40']].map(([a,b])=>`<div class="method-box"><strong>${a.toUpperCase()}</strong><p>${b}</p></div>`).join('')}</div></div>`;
}

function renderAnalyst() {
  $('#content').innerHTML=`<div class="reveal page-grid"><div class="page-card" style="min-height:500px"><span class="eyebrow">Grounded market Q&A</span><h2>Ask EventPulse AI</h2><p>Answers are generated from the current event, sentiment, market, social, and evidence datasets.</p><div class="ai-message" id="inline-answer">The highest-impact current event affects BTC: a verified regulatory bulletin coincides with a 3.7σ negative sentiment shock and a 4.8% price decline. Ask a focused question to investigate.</div><form class="command-head" id="inline-form" style="margin-top:15px;border:1px solid var(--line)"><span>›</span><input id="inline-input" placeholder="Why is BTC falling?" autocomplete="off"><button class="ask-button">ANALYZE</button></form></div><div class="page-card"><span class="eyebrow">Suggested investigations</span><h2>Start with the evidence</h2><div class="suggestions">${['Why is BTC falling?','What caused the biggest sentiment shock today?','Is the DOGE rally driven by hype?','What events are affecting NVDA?','Show high impact events with low confirmation.'].map(q=>`<button class="suggestion inline-suggestion">${q}</button>`).join('')}</div></div></div>`;
  $('#inline-form').addEventListener('submit',e=>{e.preventDefault();runInlineAI($('#inline-input').value)});
  $$('.inline-suggestion').forEach(b=>b.addEventListener('click',()=>runInlineAI(b.textContent)));
}

const citeHtml = (list) => list.map(c => state.data.events.some(e => e.id === c) ? `<button class="citation link" data-event="${esc(c)}">${esc(c)}</button>` : `<span class="citation">${esc(c)}</span>`).join('');
const modeTag = (m) => `<span class="mode-tag ${m}">${m === 'llm' ? 'QWEN · GROUNDED IN BITGET + EVENTPULSE DATA' : 'RULES ENGINE · QWEN KEY NEEDED'}</span>`;
async function runInlineAI(question) {
  if (!question.trim()) return;
  const box=$('#inline-answer'); box.innerHTML='<span class="thinking">ANALYZING EVENT GRAPH…</span>';
  try { const result=await askAI(question); box.innerHTML=`${esc(result.answer)}<div class="citation-list">${citeHtml(result.citations)}</div>${modeTag(result.mode)}`; }
  catch { box.textContent='The analyst service is temporarily unavailable.'; }
}

function openEvent(eventId) {
  const e=state.data.events.find(item=>item.id===eventId);
  if (!e) return;
  const modal=$('#detail-modal');
  modal.innerHTML=`<article class="detail-drawer" role="dialog" aria-modal="true" aria-label="Event detail">
    <header class="detail-hero"><div class="detail-head"><span class="asset-tag">${e.assets.join(' · ')}</span><span class="category">${e.category}</span>${simTag(e)}<span class="status ${e.impact_score>85?'danger':'live'}">${e.importance.toUpperCase()}</span><button class="close-btn" aria-label="Close">×</button></div><h2>${e.title}</h2><p>${e.summary}</p></header>
    <div class="detail-body">
      <div class="detail-score-row"><div class="detail-score"><small>Impact</small><strong>${e.impact_score}<small>/100</small></strong></div><div class="detail-score"><small>Confidence</small><strong>${e.confidence}%</strong></div><div class="detail-score"><small>Hype</small><strong class="warning-text">${e.hype_score}</strong></div><div class="detail-score"><small>Evidence</small><strong class="${e.evidence_score<45?'negative':'positive'}">${e.evidence_score}</strong></div></div>
      <section class="detail-section"><h3>AI event explanation</h3><div class="explanation">${e.explanation}</div></section>
      <section class="detail-section"><h3>Observed reaction</h3><div class="detail-score-row"><div class="detail-score"><small>Sentiment</small><strong class="${tone(e.sentiment_after-e.sentiment_before)}">${e.sentiment_before} → ${e.sentiment_after}%</strong></div><div class="detail-score"><small>Shock</small><strong class="${tone(e.shock_score)}">${e.shock_score>0?'+':''}${e.shock_score}σ</strong></div><div class="detail-score"><small>Price</small><strong class="${tone(e.price_change)}">${signed(e.price_change)}</strong></div><div class="detail-score"><small>Volume</small><strong class="positive">${signed(e.volume_change)}</strong></div></div></section>
      <section class="detail-section"><h3>Impact score factors</h3>${Object.entries(e.factors).map(([name,val])=>`<div class="factor-row"><span>${name}</span><div class="bar"><i style="width:${val}%"></i></div><b>${val}</b></div>`).join('')}</section>
      <section class="detail-section"><h3>Event progression</h3><div class="timeline">${e.timeline.filter(p=>p.label).map(p=>`<div class="timeline-item ${p.severity}"><span>${p.time}</span><strong>${p.label}</strong></div>`).join('')}</div></section>
      <section class="detail-section"><h3>Evidence &amp; sources</h3><div class="source-list">${e.sources.map(s=>`<div class="source"><span class="coin">${s.kind.slice(0,2).toUpperCase()}</span><div><strong>${s.name}</strong><small>${s.kind} source</small></div><span class="cred">${s.credibility}</span></div>`).join('')}</div></section>
      <section class="detail-section"><div class="alert-card ${e.evidence_score<45?'warning':'positive-card'}"><span class="eyebrow">SYSTEM VERDICT</span><h3>${e.verdict}</h3><p>Observed evidence is assessed at ${e.evidence_score}/100. This classification provides context and is not a forecast or trading recommendation.</p></div></section>
    </div></article>`;
  modal.classList.add('open'); modal.setAttribute('aria-hidden','false');
}

function closeModal(){const modal=$('#detail-modal');modal.classList.remove('open');modal.setAttribute('aria-hidden','true')}

function openAI() {
  const command=$('#command');
  command.innerHTML=`<div class="command-box"><form class="command-head" id="ai-form"><span>EP/AI</span><input id="ai-input" placeholder="Ask about an asset, event, shock, or narrative…" autocomplete="off"><button class="ask-button">ASK</button></form><div class="command-body" id="ai-body"><span class="eyebrow">QUICK INVESTIGATIONS</span><div class="suggestions">${['Why is BTC falling?','What caused the biggest sentiment shock today?','Is the DOGE rally driven by hype?','What events are affecting NVDA?'].map(q=>`<button class="suggestion command-suggestion">${q}</button>`).join('')}</div></div></div>`;
  command.classList.add('open');command.setAttribute('aria-hidden','false');
  $('#ai-input').focus();
  $('#ai-form').addEventListener('submit',ev=>{ev.preventDefault();runCommandAI($('#ai-input').value)});
  $$('.command-suggestion').forEach(b=>b.addEventListener('click',()=>runCommandAI(b.textContent)));
  command.addEventListener('click',ev=>{if(ev.target===command)closeAI()},{once:true});
}

function closeAI(){const command=$('#command');command.classList.remove('open');command.setAttribute('aria-hidden','true')}
async function askAI(question){return api('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})})}
async function runCommandAI(question){
  if(!question.trim())return;
  const body=$('#ai-body');body.innerHTML=`<span class="thinking">CONNECTING EVENTS · SENTIMENT · MARKET DATA…</span>`;
  try{const result=await askAI(question);body.innerHTML=`<span class="eyebrow">EVENTPULSE ANALYSIS</span><div class="ai-message" style="margin-top:10px">${esc(result.answer)}<div class="citation-list">${citeHtml(result.citations)}</div>${modeTag(result.mode)}</div><div class="suggestions">${result.suggested_questions.map(q=>`<button class="suggestion command-suggestion">${esc(q)}</button>`).join('')}</div>`;$$('.command-suggestion',body).forEach(b=>b.addEventListener('click',()=>runCommandAI(b.textContent)))}catch{body.innerHTML='<div class="ai-message negative">Analyst service unavailable. The dashboard data remains accessible.</div>'}
}

let noticeTimer;
function showNotice(message, ms = 2200){const el=$('#notice');el.textContent=message;el.classList.remove('hidden');clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>el.classList.add('hidden'),ms)}

async function refresh(){ state.data = await api('/api/dashboard'); renderShell(); renderView(); }

async function injectEvent() {
  if (state.busy) return;
  state.busy = true;
  try {
    const { event } = await api('/api/simulate', { method: 'POST' });
    state.unread = true; state.view = 'overview'; state.asset = event.assets[0]; state.freshId = event.id;
    closeModal(); closeAI();
    await refresh();
    showNotice(`⚡ BREAKING · ${event.assets[0]} · ${event.title}`, 4500);
    setTimeout(() => openEvent(event.id), 900);
  } catch { showNotice('Simulation unavailable — is the backend running?', 3500); }
  finally { state.busy = false; }
}

async function resetDemo() {
  if (state.busy) return;
  state.busy = true;
  try { await api('/api/reset', { method: 'POST' }); state.view = 'overview'; state.asset = 'BTC'; state.freshId = null; closeModal(); await refresh(); showNotice('Demo data reset', 1800); }
  catch { showNotice('Reset failed', 2500); }
  finally { state.busy = false; }
}

async function api(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}

async function init() {
  try {
    state.data = await api('/api/dashboard');
    renderShell();
    renderView();
    bindGlobalEvents();
  } catch (error) {
    $('#content').innerHTML = `<div class="error-state"><strong>Intelligence feed unavailable</strong><p>${error.message}</p><button onclick="location.reload()">Retry connection</button></div>`;
  }
}

document.addEventListener('DOMContentLoaded', init);
