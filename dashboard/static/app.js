// Pavilion Cerebro dashboard client: renders coordinator snapshots streamed over SSE.
"use strict";

const BAND_ICON = { normal: "●", elevated: "▲", high: "◆", critical: "■" };
const BAND_LABEL = { normal: "Normal", elevated: "Elevated", high: "High", critical: "Critical" };
const BAND_COLOR = { normal: "#0ca30c", elevated: "#fab219", high: "#ec835a", critical: "#d03b3b" };
const SERIES = ["#3987e5", "#d95926", "#199e70", "#c98500"];
const SUBSYSTEM_LABEL = { structural_visual: "Structural visual", internal_sensor: "Internal sensors", battery: "Battery / fire", hvac: "HVAC chiller" };
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (v, d = 2) => (v === null || v === undefined || Number.isNaN(v) ? "--" : Number(v).toFixed(d));
const chip = (band, text) => `<span class="chip b-${band}"><i aria-hidden="true">${BAND_ICON[band]}</i>${esc(text ?? BAND_LABEL[band])}</span>`;
const bandOf = (r) => (r >= 0.8 ? "critical" : r >= 0.6 ? "high" : r >= 0.35 ? "elevated" : "normal");

const state = { evidence: {}, soh: {}, lastTick: -1, prevOrder: [], snapshot: null };

// ------------------------------------------------------------------ building map
const NODES = {
  "agent-3:CH-1": { x: 90, y: 50, label: "CH-1 chiller" },
  "agent-0:north-facade": { x: 30, y: 110, label: "N facade", anchor: "start", dx: 10 },
  "agent-1:bms-floor2-zone2": { x: 165, y: 185, label: "BMS L2 zone 2" },
  "agent-1:upv-L2-slab": { x: 95, y: 210, label: "UPV L2 slab" },
  "agent-0:stair-core": { x: 235, y: 160, label: "Stair core" },
  "agent-0:P1-parking": { x: 130, y: 285, label: "P1 parking" },
  "agent-2:B0005": { x: 60, y: 335, label: "B5" },
  "agent-2:B0006": { x: 100, y: 335, label: "B6" },
  "agent-2:B0007": { x: 140, y: 335, label: "B7" },
  "agent-2:B0018": { x: 180, y: 335, label: "B18" },
};
const HUB = { x: 338, y: 200 };

function drawBuilding() {
  const floors = [["ROOF", 40, 60], ["L4", 60, 110], ["L3", 110, 160], ["L2", 160, 210], ["L1", 210, 260], ["P1", 260, 310], ["B1", 310, 360]];
  let s = `<rect x="45" y="38" width="90" height="22" class="floor"/>`;
  for (const [n, y0, y1] of floors.slice(1)) s += `<rect x="30" y="${y0}" width="240" height="${y1 - y0}" class="floor"/><text x="262" y="${y0 + 12}" text-anchor="end" class="lbl-muted">${n}</text>`;
  s += `<text x="140" y="52" class="lbl-muted">ROOF PLANT</text>`;
  s += `<line x1="10" y1="260" x2="290" y2="260" class="ground"/><text x="12" y="256" class="lbl-muted">GRADE</text>`;
  s += `<rect x="222" y="60" width="26" height="250" fill="none" stroke="#33393e"/>`;
  s += `<text x="42" y="352" class="lbl-muted">BATTERY ROOM</text>`;
  // roadmap stubs: dashed, no data
  s += `<line x1="205" y1="62" x2="205" y2="358" class="stub"/><circle cx="205" cy="128" r="6" class="stub"/><text x="198" y="124" text-anchor="end" class="lbl-muted">plumbing (roadmap)</text>`;
  s += `<circle cx="150" cy="85" r="6" class="stub"/><text x="160" y="88" class="lbl-muted">fire/smoke (roadmap)</text>`;
  // coordinator hub
  s += `<g id="wires"></g>`;
  s += `<circle cx="${HUB.x}" cy="${HUB.y}" r="20" fill="#131618" stroke="#3987e5" stroke-width="1.5"/><circle cx="${HUB.x}" cy="${HUB.y}" r="5" fill="#3987e5"/>`;
  s += `<text x="${HUB.x}" y="${HUB.y + 34}" text-anchor="middle">COORDINATOR</text>`;
  s += `<g id="nodes"></g>`;
  $("#bldg").innerHTML = s;
  $("#bandLegend").innerHTML = Object.keys(BAND_LABEL).map((b) => chip(b)).join("") + `<span class="muted">dashed = roadmap agent</span>`;
}

function renderBuilding(snap) {
  const byKey = Object.fromEntries(snap.concerns.map((c) => [c.key, c]));
  let wires = "", nodes = "";
  for (const [key, n] of Object.entries(NODES)) {
    const c = byKey[key];
    const band = c ? c.band : "normal";
    const col = c ? BAND_COLOR[band] : "#33393e";
    const hot = c && c.band !== "normal" ? "hot" : "";
    const mx = 300;
    wires += `<path d="M${n.x},${n.y} C${mx},${n.y} ${mx},${HUB.y} ${HUB.x - 20},${HUB.y}" stroke="${col}" class="wire ${hot}"/>`;
    if (band === "critical") nodes += `<circle cx="${n.x}" cy="${n.y}" r="7" stroke="${col}" class="pulse"/>`;
    nodes += `<circle cx="${n.x}" cy="${n.y}" r="${key.startsWith("agent-2") ? 6 : 7}" fill="${col}" class="node"><title>${esc(key)} ${c ? fmt(c.risk) : "waiting"}</title></circle>`;
    const anchor = n.anchor || "middle";
    const tx = n.x + (n.dx || 0);
    nodes += `<text x="${tx}" y="${n.y - 11}" text-anchor="${anchor}">${esc(n.label)}</text>`;
    if (c && c.state && c.state !== "MONITORING" && c.state !== "WORK ORDER OPEN" && !key.startsWith("agent-2")) {
      const w = c.state.length * 4.6 + 8;
      const x = Math.min(Math.max(n.x - w / 2, 2), 290 - w);
      nodes += `<g class="state-tag"><rect x="${x}" y="${n.y + 9}" width="${w}" height="11" rx="2"/><text x="${x + 4}" y="${n.y + 17}">${esc(c.state)}</text></g>`;
    }
  }
  const acted = snap.concerns.filter((c) => c.agent_id === "agent-2" && c.state !== "MONITORING" && c.state !== "WORK ORDER OPEN");
  if (acted.length) {
    const t = `${acted.map((c) => c.asset_id.replace("B00", "B")).join(", ")}: ${acted[0].state}`;
    const w = t.length * 4.6 + 8;
    nodes += `<g class="state-tag"><rect x="40" y="365" width="${w}" height="11" rx="2"/><text x="44" y="373">${esc(t)}</text></g>`;
  }
  $("#wires").innerHTML = wires;
  $("#nodes").innerHTML = nodes;
}

// ------------------------------------------------------------------ small charts
function sparkline(values, { h = 34, max = 1, threshold = 0.8 } = {}) {
  const w = 240;
  if (!values || values.length < 2) return `<svg class="spark" viewBox="0 0 ${w} ${h}"></svg>`;
  const n = values.length;
  const x = (i) => (i / (n - 1)) * (w - 4) + 2;
  const y = (v) => h - 3 - (Math.min(v, max) / max) * (h - 6);
  const d = values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("");
  const last = values[n - 1];
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" data-values="${values.map((v) => v.toFixed(3)).join(",")}">
    <line x1="0" x2="${w}" y1="${y(threshold)}" y2="${y(threshold)}" stroke="#d03b3b" stroke-width="1" opacity=".5"/>
    <path d="${d}" fill="none" stroke="#b7bec3" stroke-width="1.5" vector-effect="non-scaling-stroke"/>
    <circle cx="${x(n - 1)}" cy="${y(last)}" r="2.5" fill="${BAND_COLOR[bandOf(last)]}"/></svg>`;
}

function sohChart() {
  const w = 360, h = 150, pl = 30, pr = 44, pt = 8, pb = 18;
  const cells = Object.keys(state.soh).sort();
  const all = cells.flatMap((c) => state.soh[c]);
  if (!all.length) return `<svg class="chart" viewBox="0 0 ${w} ${h}"></svg>`;
  const x0 = Math.min(...all.map((p) => p.cycle)), x1 = Math.max(x0 + 10, ...all.map((p) => p.cycle));
  const yMin = 55, yMax = 100;
  const X = (c) => pl + ((c - x0) / (x1 - x0)) * (w - pl - pr);
  const Y = (v) => pt + (1 - (Math.max(yMin, Math.min(yMax, v)) - yMin) / (yMax - yMin)) * (h - pt - pb);
  let s = "";
  for (const v of [60, 70, 80, 90, 100]) s += `<line x1="${pl}" x2="${w - pr}" y1="${Y(v)}" y2="${Y(v)}" stroke="#262b2f"/><text x="${pl - 4}" y="${Y(v) + 3}" text-anchor="end">${v}</text>`;
  s += `<line x1="${pl}" x2="${w - pr}" y1="${Y(70)}" y2="${Y(70)}" stroke="#d03b3b" opacity=".7"/><text x="${w - pr + 3}" y="${Y(70) + 3}" fill="#d03b3b">EOL 70%</text>`;
  s += `<text x="${pl}" y="${h - 4}">cycle ${x0}</text><text x="${w - pr}" y="${h - 4}" text-anchor="end">${x1}</text>`;
  cells.forEach((c, i) => {
    const pts = state.soh[c];
    const d = pts.map((p, j) => `${j ? "L" : "M"}${X(p.cycle).toFixed(1)},${Y(p.soh).toFixed(1)}`).join("");
    s += `<path d="${d}" fill="none" stroke="${SERIES[i]}" stroke-width="2" stroke-linejoin="round"/>`;
    const last = pts[pts.length - 1];
    s += `<circle cx="${X(last.cycle)}" cy="${Y(last.soh)}" r="3" fill="${SERIES[i]}" stroke="#131618" stroke-width="2"/>`;
  });
  // direct labels at line ends, nudged apart
  const ends = cells.map((c, i) => ({ c, i, y: Y(state.soh[c][state.soh[c].length - 1].soh) })).sort((a, b) => a.y - b.y);
  for (let k = 1; k < ends.length; k++) if (ends[k].y - ends[k - 1].y < 11) ends[k].y = ends[k - 1].y + 11;
  for (const e of ends) s += `<text x="${w - pr + 3}" y="${e.y + 3}" fill="#b7bec3">${e.c}</text>`;
  return `<svg class="chart soh" viewBox="0 0 ${w} ${h}" data-x0="${x0}" data-x1="${x1}" data-pl="${pl}" data-pr="${pr}">${s}<line class="xhair" y1="${pt}" y2="${h - pb}" stroke="#7d868c" opacity="0"/></svg>`;
}

// ------------------------------------------------------------------ agent cards
function card(agent, inner, anyCritical) {
  return `<article class="agent ${anyCritical ? "is-critical" : ""}" id="card-${agent.agent_id}">
    <div class="a-head"><div><div class="a-id">${esc(agent.agent_id.toUpperCase())} / ${esc(agent.subsystem)}</div><div class="a-name">${esc(agent.name)}</div>
    <div class="a-src">${esc(agent.data_source)}</div></div><div class="a-status ${agent.status === "live" ? "live" : ""}">${esc(agent.status)}</div></div>${inner}</article>`;
}

function renderAgent0(agent, byKey) {
  const zones = [["P1-parking", "P1 parking, col line C"], ["north-facade", "North facade L2-4"], ["stair-core", "Stair core B"]];
  const ev = state.evidence["agent-0"] || {};
  const box = ev.bbox_227 && ev.frame_risk >= 0.5 ? ev.bbox_227 : null;
  const scale = 128 / 227;
  const boxHtml = box ? `<div class="box" style="left:${box[0] * scale}px;top:${box[1] * scale}px;width:${Math.max(6, (box[2] - box[0]) * scale)}px;height:${Math.max(6, (box[3] - box[1]) * scale)}px"></div>` : "";
  const rows = zones.map(([k, label]) => {
    const c = byKey[`agent-0:${k}`];
    const r = c ? c.risk : 0;
    const b = c ? c.band : "normal";
    return `<div class="zone"><span>${label}</span><span>${c ? chip(b, fmt(r)) : '<span class="muted">waiting</span>'}</span><div class="bar"><span style="width:${r * 100}%;background:${BAND_COLOR[b]}"></span></div></div>`;
  }).join("");
  const backend = agent.backend === "opencv" ? "opencv fallback (no Ollama / API key found)" : `inspection cascade (${agent.backend})`;
  return `<div class="row"><div class="frame">${ev.frame ? `<img src="/img/${esc(ev.frame)}" alt="current inspection frame">` : ""}${boxHtml}<div class="scan"></div></div><div class="zones">${rows}</div></div>
    <div class="headline">${ev.frame ? `Frame ${esc(ev.frame)}: crack probability <b class="mono">${fmt(ev.frame_risk)}</b>` : "Waiting for first frame"}</div>
    <div class="muted small">Scoring backend: ${esc(backend)}</div>`;
}

function renderAgent1(agent, byKey) {
  const u = byKey["agent-1:upv-L2-slab"], b = byKey["agent-1:bms-floor2-zone2"];
  const um = u ? u.metrics : {}, bm = b ? b.metrics : {};
  return `<div class="split">
    <div class="sub-block"><h3>UPV / material health ${u ? chip(u.band, fmt(u.risk)) : ""}</h3>
      <div class="big">${um.upv_mps ? Math.round(um.upv_mps).toLocaleString() : "--"}<span class="small muted"> m/s</span></div>
      <dl class="kv"><dt>expected</dt><dd>${um.expected_mps ? Math.round(um.expected_mps).toLocaleString() : "--"}</dd>
      <dt>test path</dt><dd>${esc(um.config || "--")}</dd>
      <dt>est. strength</dt><dd>${um.est_strength_mpa == null ? "direct only" : fmt(um.est_strength_mpa, 1) + " MPa"}</dd><dt>vs expected</dt><dd>${um.strength_deficit_pct == null ? "--" : (um.strength_deficit_pct > 0 ? "+" : "") + fmt(um.strength_deficit_pct, 1) + "%"}</dd>
      <dt>age</dt><dd>${esc(um.age || "--")}</dd></dl>${sparkline(u ? u.history : [])}
      <div class="muted small">baseline: provided (maturity metadata)</div></div>
    <div class="sub-block"><h3>BMS telemetry ${b ? chip(b.band, fmt(b.risk)) : ""}</h3>
      <div class="big">${fmt(bm.temp_c, 1)}<span class="small muted"> degC</span></div>
      <dl class="kv"><dt>RH</dt><dd>${fmt(bm.rh_pct, 1)}%</dd><dt>zone AC</dt><dd>${fmt(bm.ac_total_kw, 1)} kW</dd><dt>AC-1</dt><dd>${fmt(bm.ac1_kw, 1)} kW</dd>
      <dt>2018</dt><dd>${esc(bm.source_time || "--")}</dd></dl>${sparkline(b ? b.history : [])}
      <div class="muted small">baseline: inferred from data (seasonal)</div></div></div>
    <div class="headline">${esc((b && b.band !== "normal" ? b.headline : u ? u.headline : "") || "")}</div>
    <div class="muted small">One scoring function, both sources: only the loaders differ.</div>`;
}

function renderAgent2(agent, byKey) {
  const cells = ["B0005", "B0006", "B0007", "B0018"];
  const rows = cells.map((c, i) => {
    const k = byKey[`agent-2:${c}`];
    const m = k ? k.metrics : {};
    return `<tr><td><span class="sw" style="background:${SERIES[i]}"></span>${c}</td><td>${fmt(m.soh_pct, 1)}%</td><td>${m.rul_cycles === null || m.rul_cycles === undefined ? "--" : m.rul_cycles}</td>
      <td>${fmt(m.temp_max_c, 1)}</td><td>${m.impedance_growth_pct !== undefined ? "+" + fmt(m.impedance_growth_pct, 0) + "%" : "--"}</td><td>${k ? chip(k.band, fmt(k.risk)) : ""}</td></tr>`;
  }).join("");
  return `<div>${sohChart()}</div>
    <table class="cells"><thead><tr><th>Cell</th><th>SOH</th><th>RUL (cyc)</th><th>Tmax degC</th><th>Impedance</th><th>Fire risk</th></tr></thead><tbody>${rows}</tbody></table>
    <div class="muted small">State of health vs 2.0 Ah rated; EOL = 30% fade (1.4 Ah), the dataset's own criterion.</div>`;
}

function renderAgent3(agent, byKey) {
  const c = byKey["agent-3:CH-1"];
  const ev = state.evidence["agent-3"] || {};
  const m = c ? c.metrics : {};
  const ratio = m.d2_ratio || 0;
  const diag = (ev.diagnosis || []).map((d) => `<div class="d"><span>${esc(d.fault)}</span><span class="mono">${fmt(d.match)}</span><div class="bar"><span style="width:${Math.max(0, d.match) * 100}%"></span></div></div>`).join("");
  return `<div class="row" style="justify-content:space-between"><div><div class="muted small">Deviation from fault-free baseline</div><div class="big">${fmt(ratio, 2)}<span class="small muted"> x threshold</span></div></div>
      <div>${c ? chip(c.band, m.severity && m.severity !== "-" ? m.severity : fmt(c.risk)) : ""}</div></div>
    <div class="meter"><span style="width:${Math.min(100, (ratio / 3) * 100)}%;background:${BAND_COLOR[c ? c.band : "normal"]}"></span><i style="left:33.3%" title="alarm threshold"></i></div>
    <div class="muted small">threshold = 99th pct of fault-free runs (bar marker)</div>
    <div class="diag"><div class="muted small">${ev.detected ? "Diagnosis (signature match, cosine)" : "Nearest fault signatures (below alarm threshold, not a diagnosis)"}</div>${diag}</div>
    <div class="headline">${esc(c ? c.headline : "")}</div>
    <div class="truth">Replaying <b class="mono">${esc(ev.run || "--")}</b>. Ground truth: ${esc(ev.ground_truth || "--")}. The model never saw this run. ${m.kW ? `kW ${fmt(m.kW, 0)}, COP ${fmt(m.COP, 2)}` : ""}</div>`;
}

const RENDER = { "agent-0": renderAgent0, "agent-1": renderAgent1, "agent-2": renderAgent2, "agent-3": renderAgent3 };

function renderAgents(snap) {
  const byKey = Object.fromEntries(snap.concerns.map((c) => [c.key, c]));
  $("#agents").innerHTML = snap.agents.map((a) => {
    const crit = snap.concerns.some((c) => c.agent_id === a.agent_id && c.band === "critical");
    return card(a, RENDER[a.agent_id](a, byKey), crit);
  }).join("");
  $("#roadmap").innerHTML = snap.roadmap.map((r) => `<div class="stub-card"><div class="row" style="justify-content:space-between"><span class="a-id">${esc(r.agent_id.toUpperCase())}</span><span class="tag">ROADMAP / ${esc(r.status.toUpperCase())}</span></div>
    <div class="a-name">${esc(r.name)}</div><div class="small">${esc(r.status)}: ${esc(r.note)}</div><div class="muted small">Same BaseAgent interface. ${r.agent_id === "agent-6" ? "Design only; no hardware to run it on, no data faked." : "No detection logic yet, no data faked."}</div></div>`).join("");
}

// ------------------------------------------------------------------ health, queue, feed
function renderHealth(snap) {
  const h = snap.health;
  $("#health").textContent = fmt(h.building, 1);
  const band = h.building >= 75 ? "normal" : h.building >= 55 ? "elevated" : h.building >= 35 ? "high" : "critical";
  $("#healthBand").outerHTML = `<div id="healthBand">${chip(band)}</div>`;
  $("#subs").innerHTML = Object.entries(SUBSYSTEM_LABEL).map(([k, label]) => {
    const v = h.subsystems[k];
    const b = v === undefined ? "normal" : bandOf(1 - v / 100);
    return `<div class="sub-tile"><div class="small muted">${label}</div><div class="row" style="justify-content:space-between"><span class="v">${v === undefined ? "--" : fmt(v, 0)}</span>${v === undefined ? "" : chip(b)}</div></div>`;
  }).join("");
}

function renderQueue(snap) {
  const tbody = $("#queue");
  const first = {};
  tbody.querySelectorAll("tr").forEach((tr) => (first[tr.dataset.key] = tr.getBoundingClientRect().top));
  const disaster = snap.mode === "disaster";
  $("#prioHead").textContent = disaster ? "Severity" : "Priority";
  $("#rankRule").textContent = disaster ? "triage by severity band, then risk" : "risk x consequence x time";
  tbody.innerHTML = snap.concerns.map((c) => {
    const act = c.state !== "MONITORING";
    return `<tr data-key="${esc(c.key)}"><td class="rk">${c.rank}</td><td class="asset"><b>${esc(c.asset_id)}</b><span>${esc(SUBSYSTEM_LABEL[c.subsystem])} / ${esc(c.zone)}</span></td>
      <td>${chip(c.band, fmt(c.risk))}</td><td class="mono">${disaster ? esc(BAND_LABEL[c.band]) : fmt(c.priority, 3) + `<div class="muted small nw">c ${fmt(c.consequence, 2)} &middot; t ${fmt(c.freshness * c.persistence, 2)}</div>`}</td>
      <td class="st ${act ? "act" : ""}">${esc(c.state)}</td></tr>`;
  }).join("");
  // FLIP: slide rows from their previous position so re-ranking is visible
  tbody.querySelectorAll("tr").forEach((tr) => {
    const k = tr.dataset.key;
    if (first[k] === undefined) return;
    const dy = first[k] - tr.getBoundingClientRect().top;
    if (Math.abs(dy) > 2) {
      tr.classList.add("moved");
      tr.animate([{ transform: `translateY(${dy}px)` }, { transform: "translateY(0)" }], { duration: 650, easing: "cubic-bezier(.2,.7,.2,1)" });
      setTimeout(() => tr.classList.remove("moved"), 1200);
    }
  });
  const rr = snap.last_rerank;
  $("#rerank").textContent = rr ? `last re-triage: ${rr.moved.length} concerns moved in ${rr.ms.toFixed(2)} ms (${rr.mode} mode)` : "";
}

function renderFeed(snap) {
  const icon = { mitigation: "ACTION", advisory: "WORK ORDER", rearm: "RE-ARMED", mode: "MODE", report: "REPORT" };
  $("#feed").innerHTML = snap.feed.slice(0, 60).map((e) => {
    const t = (e.time || "").replace("T", " ");
    const band = e.band || (e.risk !== undefined ? bandOf(e.risk) : "normal");
    return `<li class="${e.type}"><div class="meta"><span>${esc(t)}</span><span>${icon[e.type] || e.type}</span>${e.asset_id ? `<span>${esc(e.agent_id)} / ${esc(e.asset_id)}</span>` : ""}
      ${e.type === "report" ? chip(band, fmt(e.risk)) : ""}${e.type === "mitigation" ? '<span class="simtag">SIMULATED ACTION</span>' : ""}</div>${esc(e.text)}</li>`;
  }).join("");
}

// ------------------------------------------------------------------ main loop
function absorb(snap) {
  if (snap.tick < state.lastTick) { state.soh = {}; state.evidence = {}; }
  state.lastTick = snap.tick;
  for (const a of snap.agents) {
    for (const r of a.latest || []) {
      if (a.agent_id === "agent-0" || a.agent_id === "agent-3") state.evidence[a.agent_id] = r.evidence;
    }
    if (a.soh_series) state.soh = Object.fromEntries(Object.entries(a.soh_series).map(([c, pts]) => [c, pts.map(([cycle, soh]) => ({ cycle, soh }))]));
  }
}

function render(snap) {
  state.snapshot = snap;
  absorb(snap);
  document.body.classList.toggle("disaster", snap.mode === "disaster");
  $("#disaster").checked = snap.mode === "disaster";
  $("#modeText").textContent = snap.mode === "disaster" ? "ON: triage by severity only" : "Normal: risk x consequence x time";
  $("#simtime").textContent = (snap.sim_time || "--").replace("T", " ") + " replay";
  $("#progress").style.width = `${Math.min(100, (snap.tick / snap.scenario_ticks) * 100)}%`;
  $("#tickinfo").textContent = `tick ${snap.tick}/${snap.scenario_ticks} - ${snap.reports_ingested} reports fused${snap.finished ? " - replay complete, restarting" : ""}`;
  if (snap.control) {
    $("#pause").textContent = snap.control.paused ? "Resume" : "Pause";
    document.querySelectorAll("#speed button").forEach((b) => b.classList.toggle("on", Number(b.dataset.speed) === snap.control.speed));
  }
  renderHealth(snap);
  renderBuilding(snap);
  renderAgents(snap);
  renderQueue(snap);
  renderFeed(snap);
}

async function control(body) {
  const r = await fetch("/api/control", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json();
}

function wire() {
  $("#disaster").addEventListener("change", (e) => control({ action: "mode", mode: e.target.checked ? "disaster" : "normal" }));
  $("#pause").addEventListener("click", () => control({ action: state.snapshot?.control?.paused ? "resume" : "pause" }));
  $("#restart").addEventListener("click", () => control({ action: "restart" }));
  document.querySelectorAll("#speed button").forEach((b) => b.addEventListener("click", () => control({ action: "speed", speed: Number(b.dataset.speed) })));
  // hover layer: sparkline values and SOH crosshair
  const tip = $("#tip");
  document.addEventListener("mousemove", (e) => {
    const spark = e.target.closest && e.target.closest("svg.spark");
    const soh = e.target.closest && e.target.closest("svg.soh");
    let text = "";
    if (spark && spark.dataset.values) {
      const vals = spark.dataset.values.split(",").map(Number);
      const rect = spark.getBoundingClientRect();
      const i = Math.round(((e.clientX - rect.left) / rect.width) * (vals.length - 1));
      const v = vals[Math.max(0, Math.min(vals.length - 1, i))];
      text = `risk ${v.toFixed(2)} (${BAND_LABEL[bandOf(v)]}), ${vals.length - 1 - i} ticks ago`;
    } else if (soh) {
      const rect = soh.getBoundingClientRect();
      const vb = soh.viewBox.baseVal;
      const px = ((e.clientX - rect.left) / rect.width) * vb.width;
      const { x0, x1, pl, pr } = Object.fromEntries(Object.entries(soh.dataset).map(([k, v]) => [k, Number(v)]));
      const cyc = Math.round(x0 + ((px - pl) / (vb.width - pl - pr)) * (x1 - x0));
      const parts = Object.keys(state.soh).sort().map((c) => {
        const p = state.soh[c].reduce((best, q) => (Math.abs(q.cycle - cyc) < Math.abs(best.cycle - cyc) ? q : best), state.soh[c][0]);
        return `${c} ${p.soh.toFixed(1)}%`;
      });
      const xh = soh.querySelector(".xhair");
      if (xh) { xh.setAttribute("x1", px); xh.setAttribute("x2", px); xh.setAttribute("opacity", 0.8); }
      text = `cycle ${cyc}: ` + parts.join("  ");
    }
    if (text) { tip.textContent = text; tip.style.left = e.clientX + 12 + "px"; tip.style.top = e.clientY + 12 + "px"; tip.style.opacity = 1; }
    else tip.style.opacity = 0;
  });
}

function connect() {
  const es = new EventSource("/api/events");
  es.onmessage = (m) => render(JSON.parse(m.data));
  es.onerror = () => { es.close(); setTimeout(connect, 1500); };
}

drawBuilding();
wire();
// ?static=1: no live stream; snapshots are injected by scripts/render_demo_video.py via window.cerebroRender
if (new URLSearchParams(location.search).get("static")) window.cerebroRender = render;
else connect();
