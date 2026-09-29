# Pavilion Cerebro

**A coordinated swarm of specialist AI agents for building structural health, damage detection and maintenance prediction.**

Instead of one narrow tool, Pavilion Cerebro runs one agent per building subsystem or data source. Every agent reports to a shared coordinator, which fuses their findings into a whole-building risk picture, ranks what needs attention first, and fires automated mitigation actions before small problems become expensive failures.

> **Technical thesis.** Pavilion Cerebro is one platform (one coordinator, one shared agent interface), not a bag of unrelated tools. Every agent, whether it watches cracks, internal sensor telemetry, batteries or HVAC, implements the same interface: it ingests its data, outputs a calibrated 0-1 risk score plus supporting evidence, and reports to the coordinator. That is what makes it a platform rather than a pile of point solutions. It is also why adding a new subsystem later means writing one more agent to the same interface, not rebuilding anything. The coordinator never imports an agent class.

This repo also contains the team's existing inspection grading cascade (`src/cascade/`, documented in [docs/cascade_README.md](docs/cascade_README.md)). Pavilion Cerebro wraps it as Agent 0 without changing any of its code.

---

## Quickstart (local; this is the working technical demo)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-cerebro.txt

python scripts/selfcheck.py          # every agent standalone on its real data + the full swarm; writes data/samples/metrics.json
python -m dashboard.server           # live dashboard at http://localhost:8765
```

The processed dataset samples are committed in `data/samples/` (2.4 MB), so the dashboard runs without downloading anything. To rebuild them from the original public sources: `python data/download_datasets.py && python data/prepare_samples.py` (~500 MB into the gitignored `data/raw/`).

Optional:

```bash
python -m playwright install chromium
python scripts/render_demo_video.py  # frame-rendered walkthrough -> site/assets/pavilion_cerebro_demo.mp4 (+ poster and stills)
python scripts/build_site.py         # copies measured metrics into the marketing site
```

Agent 0 backend: `CEREBRO_VISUAL_BACKEND=auto|claude|local|opencv` (default `auto`; see Agent 0 below).

---

## Architecture

```
 data sources (real, public)              agents (one BaseAgent interface)              coordinator
 ---------------------------              --------------------------------              -----------
 concrete crack images  ------------->  Agent 0  Structural Visual  --+
 UMN UPV + CU-BEMS BMS  ------------->  Agent 1  Internal Sensor    --+   AgentReport   fusion.py          whole-building health, concern list
 NASA Li-ion aging      ------------->  Agent 2  Battery / fire     --+--------------> prioritization.py  risk x consequence x time | disaster: severity
 ASHRAE RP-1043 chiller ------------->  Agent 3  HVAC FDD           --+               mitigation.py      threshold -> simulated action + log
                                        Agent 4  Plumbing   (roadmap stub)            swarm.py           replay clock, drives dashboard / video / self-check
                                        Agent 5  Fire/smoke (roadmap stub)
```

The standardized report (`agents/base.py`):

```python
AgentReport(agent_id, subsystem, risk_score: 0-1, confidence: 0-1, evidence: dict, timestamp,
            asset_id="", zone="", headline="", metrics={})
```

`BaseAgent` has two methods an agent must write: `observations()` (the source-specific loader, which yields real readings in arrival order) and `observe(obs)` (one reading in, reports out). Everything else is shared.

---

## The agents

### Agent 0: Structural Visual (existing pipeline, wrapped)

`agents/structural_visual.py` wraps the existing cascade: it calls `cascade.gate.run_gate` and `cascade.grade.grade_image` and translates their `GateRecord`/`Finding` into an `AgentReport` (unified level S0-S4 → risk 0.05/0.25/0.5/0.75/0.95; U → 0.5 at low confidence). **No cascade code was changed.** Its outputs were already structured pydantic objects, so no adapter change was needed inside it. The existing 42 cascade tests still pass.

**Correction to the build brief:** the brief described the existing pipeline as classical OpenCV edge/contour detection. It isn't. It is a vision-language-model cascade: a local Qwen3-VL gate via Ollama, and Claude or local grading against industry rubrics. That cascade needs either Ollama or an `ANTHROPIC_API_KEY`, and neither was available on the build machine. So Pavilion Cerebro adds an **offline fallback backend** (`opencv`): classical crack features (black-hat morphology, connected-component length and elongation, edge density) with a logistic calibration. It is new code, not part of the original cascade, and every report names the backend that produced it.

| Backend | When `auto` picks it | What runs |
|---|---|---|
| `claude` | `ANTHROPIC_API_KEY` set | cascade gate + grader on Claude (MBEI concrete rubric) |
| `local` | Ollama answers on `OLLAMA_URL` | cascade gate + grader on local Qwen3-VL |
| `opencv` | neither | offline fallback, measured below |

Data: Concrete Crack Images for Classification (Özgenel, CC BY 4.0; 227 px patches, Hugging Face mirror `mohammadnajeeb/concrete_crack_images`, test split). The fallback's calibration was fitted on 1,600 images from the first half of that split and **evaluated on 1,600 disjoint images**: accuracy **92.9%**, precision 93.3%, recall 92.4%, Brier 0.053. Reliability is close to the diagonal (for example, predictions in 0.8-1.0 average 0.98 and are 96.9% cracks). The 60-image replay sample (disjoint from calibration) scores 98.3%. The cascade path is exercised in the self-check with a fake grader (plumbing only, no model), and cascade results are cached per image hash so a replay never re-bills an API.

### Agent 1: Internal Sensor Intelligence (UPV + BMS, one scorer)

`agents/generic.py` is the concrete proof that **the agent infers from whatever numeric data it gets**. `assess(history, SeriesSpec)` scores any labeled series with generic statistics:

- **level:** z-score of the latest reading(s) against a baseline;
- **drift:** trend over a window, in units of scale;
- **crossing:** fraction of recent readings outside the normal range;
- **missing data:** a sensor that goes quiet is itself a finding.

Whatever metadata exists is used. Anything missing is **inferred from the data itself**: a seasonal period from autocorrelation (daily or weekly, preferring the weekly multiple when it correlates better), a rolling or seasonal median baseline, robust (MAD, floored at half the SD) scale, and a percentile normal range. Multi-channel assets use one shared `corroborated()` rule: one channel alone can reach "high", and "critical" needs a second channel to agree.

`agents/internal_sensor.py` then contains only two loaders:

| Source | What the loader supplies | Baseline |
|---|---|---|
| **UPV**: *Dataset on compressive strength, UPV and rebound hammer properties of UHPC with maturing age*, Durrani & Haroon, UMN DRUM, [doi:10.13020/h3m2-1h76](https://doi.org/10.13020/h3m2-1h76), CC0. 1,130 readings, direct/semi-direct/indirect paths at 54 and 250 kHz, 1-28 days | expected UPV per reading (leave-one-out median of same age, fiber content and configuration); per-configuration spread (IQR, floored at 2% of expected, a team assumption) | **provided** |
| **BMS**: CU-BEMS, a real 7-storey office building's energy management system in Bangkok (Chulalongkorn University, figshare 11726517, CC BY 4.0). Floor 2 zone 2, 15-min, Jul-Sep 2018: zone temperature, humidity, 14 AC units' power, plug load | nothing | **inferred** (weekly seasonal for AC power, daily for temperature/humidity) |

Lower UPV than expected for the concrete's age and mix means a less dense, weaker material; that is the standard NDT relationship (ASTM C597). Strength is estimated from direct-path UPV with an exponential fit on the dataset's own 108 paired measurements (MPa = 0.253·e^(0.00125·UPV), R² = 0.85). The fit is only applied to direct-path readings.

**Dataset substitution (disclosed):** the brief named the IEEE DataPort Honeywell BMS dataset (Stamatescu et al., 2019; "HVAC Air Handling Units: One-year Data from Medium-to-Large Size Academic Building"). DataPort serves it only to paid subscribers, so it could not be fetched. LBNL Building 59 (Dryad) was the next choice, but Dryad's download API required authentication. CU-BEMS is an openly licensed dataset from a real building management system and plays the same role: telemetry that has nothing to do with concrete.

Measured (self-check):

- all **10/10** UPV readings ≥20% below expected are flagged; at ≥15% below it is 14/17, and the three misses are indirect surface-path readings, the noisiest configuration;
- readings within 2% of expected reach "high" 0.2% of the time;
- in the BMS data the agent independently finds the **AC-1 output collapse of 4-7 Sep 2018**. AC-1's weekday working-hour mean falls from 15-26 kW to about 5-7 kW while zone temperature rises, and 16 high/critical reports cite AC-1. It also flags two Thai substitution holidays (AC off on a weekday) as statistical anomalies. That is correct behaviour for a detector with no calendar, and worth saying out loud.

### Agent 2: Battery & Electrical Fire Risk

NASA Ames PCoE Li-ion Battery Aging Dataset (cells B0005, B0006, B0007, B0018; 2.0 Ah rated, end-of-life at 30% fade to 1.4 Ah). Per discharge cycle, the agent tracks:

- **state of health:** capacity ÷ 2.0 Ah;
- **remaining useful life:** a Theil-Sen trend over the last 80 cycles, projected to 1.4 Ah;
- **discharge temperature rise and Re+Rct impedance growth,** both scored by the same generic engine as Agent 1.

The fire-risk score combines these **precursor indicators** (fade toward or past EOL, impedance growth, abnormal self-heating). The weights are assumptions and are written in the code. The NASA cells never went into thermal runaway, so the score is a "pull this cell for inspection" triage signal, not a runaway predictor.

Measured: the three cells that reached EOL (at cycles 97, 109, 125) were each flagged high **32-43 cycles before** the crossing. RUL error is **8.4 cycles MAE** over 12 checkpoints, taken 10-40 cycles before EOL. *Caveat:* the 80-cycle trend window was chosen by comparing five windows (20/30/50/80/all) on these same four cells, so that error is optimistic.

### Agent 3: HVAC Fault Detection & Diagnosis

ASHRAE RP-1043 (90-ton centrifugal water-cooled chiller; figshare 28435232, CC0), using 4,050 steady-state 5-minute windows from 12 fault-free runs and 7 faults × 4 severity levels. The method:

1. **Fault-free reference:** each of 23 sensor features is regressed (quadratic) on the operating point, using 8 fault-free runs.
2. **Detection:** Mahalanobis distance of the residuals, with the alarm threshold at the 99th percentile of fault-free data.
3. **Diagnosis:** cosine match to each fault's mean whitened residual signature.
4. **Severity (SL1-SL4):** residual magnitude interpolated between the other levels.

Signatures are always built **leaving out the severity level being scored**, and the dashboard replays a held-out fault-free run and then a refrigerant leak through SL1 to SL4. The model has never seen any run the dashboard shows.

Measured:

- **1.5%** false alarms on 400 windows from 4 held-out fault-free runs;
- **96.9%** diagnosis accuracy on 2,034 detected windows;
- severity exact 82.5%, within one level 98.6%;
- 20 of 28 fault runs detected and correctly diagnosed.

The misses are low-severity refrigerant leak/overcharge, condenser fouling and excess oil at SL1, which the literature also finds hard. A 10% refrigerant undercharge shows a detectable signature in only 3% of windows.

---

## Coordinator: the core

`coordinator/fusion.py` keeps the latest report per (agent, asset), computes whole-building health (0-100 from the consequence-weighted worst and mean asset risk) and per-subsystem health, and maintains an incident feed.

**Prioritization** (`coordinator/prioritization.py`) generalizes the cascade's *severity × criticality × consequence × urgency* rule across subsystem types:

```
priority = risk_score × consequence(subsystem, asset) × time_factor
time_factor = freshness (evidence decays after a 3 h grace, 4 h half-life, when an agent stops reporting)
            × persistence (an open concern escalates 1.0 → 2.0 over 24 h, the cascade's urgency_for rule)
```

Consequence weights are team assumptions, listed so they can be argued with: battery 1.0 (fire, life safety), load-bearing slab 0.85, structural visual 0.8, chiller 0.55, office comfort/energy (BMS zone) 0.4. This is why, at replay tick 40, battery cell B0018 at risk 0.64 ranks above a P1 parking crack at risk 0.76.

**Disaster / incident mode** switches ranking to pure triage by severity: severity band first, then raw risk, with no cost or consequence weighting. In the self-check the order changed at 15/15 toggles, with a mean re-triage time of **0.05 ms**.

**Self-healing layer** (`coordinator/mitigation.py`). **These actions are simulated: log entries and dashboard state changes, with no real building-control integration.**

| Trigger | Action |
|---|---|
| battery critical | "throttled charge rate to 50% and paged facilities team" |
| HVAC critical | "shut down affected chiller loop and switched to backup" |
| UPV or structural-visual critical | "flagged zone for structural inspection and restricted access" |
| BMS critical | priority HVAC work order and comfort-alarm mode |

- **Critical** means risk ≥ 0.8 on 2 consecutive reports, and the action fires once per episode.
- **High** means risk ≥ 0.6 on 3 consecutive reports, which opens an advisory work order.
- **Re-arm** needs 8 consecutive reports below 0.5, so a daily comfort cycle cannot re-fire an action.

In the 150-tick replay, actions fire for the BMS zone (t11), the UPV slab (t23), P1 parking (t42), battery cells (t62-t117) and chiller CH-1 (t104).

---

## Dashboard (local prototype)

`python -m dashboard.server` uses the standard library only. A background thread steps the swarm once per interval (one replay hour per tick) and streams each coordinator snapshot to the browser over Server-Sent Events, so values tick as the real datasets replay. The page shows:

- a building cross-section with agent nodes wired to the coordinator hub, plus dashed roadmap nodes;
- the whole-building health score;
- one live card per agent: the crack frame with its detection box, UPV and BMS readouts, battery SOH curves and RUL, and chiller diagnosis;
- the ranked queue, which animates rows when the ranking changes;
- the incident feed, where mitigation actions are tagged SIMULATED;
- pause, 1x/2x/4x, restart and the disaster-mode toggle.

The visual identity is new, since the existing Streamlit UI had none to reuse: dark industrial, IBM Plex Sans and Mono, and status colors that always come with an icon and a label.

## Demo video

`scripts/render_demo_video.py` produces a frame-rendered walkthrough (77.8 s, 1280×720, 2.3 MB), not a screen recording. The real swarm runs headless and every coordinator snapshot is recorded. The real dashboard page is then loaded in headless Chromium in static mode, each snapshot is injected and screenshotted, and Pillow composes the shots:

1. title, with the caption *"Simulated monitoring feed - detection logic and readings are from real public datasets, replayed live."*;
2. the building;
3. each agent's live detection;
4. the coordinator filling in;
5. a triggered mitigation;
6. the disaster-mode toggle;
7. an end card with measured metrics.

The caption stays on screen throughout.

## Three levels, for three audiences

The live dashboard is an expert's bird's-eye view: everything ticking at once, no pauses, built for someone who already knows what "risk score" or "diagnosis confidence" means. Explaining that live, in real time, to a client or a layperson doesn't work — so there are three levels now, slow to fast:

1. **`site/walkthrough/`** — a self-paced, plain-English walkthrough for anyone who isn't an engineer. One real screenshot of the real dashboard, one plain-English idea, per screen, advanced by hand (Next/Back, no autoplay, no jargon). Built by `scripts/capture_walkthrough.py`, which reuses the demo video's own recording and screenshot machinery (`scripts/render_demo_video.py`'s `record()` and `Shooter`) — every image is a real screenshot of a real run, not a mockup, and each agent's screenshot is the moment that agent's own risk score peaked in that run (found automatically, not hand-picked). Regenerate after any change with `python scripts/capture_walkthrough.py`. Open `site/walkthrough/index.html` directly, or serve `site/` and go to `/walkthrough/`.
2. **`python -m dashboard.server`** — the live, ticking, expert view described above. Use this once someone already understands the pitch and wants to see the real system running.
3. **`site/index.html`** — the marketing/pitch site (below), plus the demo video, for someone deciding whether to look closer at all.

## Marketing site (Deliverable 2, deploys to Replit)

`site/` is a static site (HTML/CSS/JS, the same visual identity, SVG flow diagram, embedded demo video, a metrics strip filled from `site/assets/metrics.json`). It does not run or depend on the Python pipeline. To publish it on Replit:

1. Create a Replit project and upload the **contents** of `site/`, or import this repo and use `site/` as the root. It includes a `.replit` (Python static server for preview, and a `[deployment]` block with `deploymentTarget = "static"`).
2. Press Run to preview, then Deploy as a static deployment. If Replit's template generates its own `.replit`, keep its `modules` line; the only requirement is that `index.html` is served.
3. If the dashboard is ever deployed somewhere reachable, set `DASHBOARD_URL` in `site/main.js` so the secondary call to action links to it. Until then it points to local run instructions.

Re-run `python scripts/selfcheck.py && python scripts/build_site.py` before uploading so the numbers on the site match the code. `site/walkthrough/` (see "Three levels" above) ships inside `site/` and goes to Replit along with it automatically.

---

## What is real, what is simulated, what is future scope

We present this split as a credibility asset.

| Real | Simulated | Future scope |
|---|---|---|
| The existing inspection cascade (wrapped, unchanged), plus the offline OpenCV fallback, measured on held-out images | **The building.** Five datasets from different places are mapped onto one fictional building and replayed on a shared clock | **Plumbing / water damage agent.** No public dataset exists; needs a field-data partnership (roadmap stub in the UI) |
| UMN DRUM UHPC UPV dataset (CC0) | **Mitigation actions.** Log entries and UI state only, no building control | **Fire / smoke visual agent.** Public image datasets exist but are not yet integrated (roadmap stub) |
| CU-BEMS BMS telemetry (CC BY 4.0), substituted for the paywalled IEEE DataPort set | **The crack camera sweep.** Real images and scores, but the assignment of images to zones is scripted | Real control integration (BACnet, BMS vendor APIs); a site-specific consequence model |
| NASA PCoE Li-ion aging data | | **Laser scan digital twin agent.** Needs a real LiDAR/laser scanner; not simulated with fabricated scan data (roadmap stub, hardware-dependent) |
| ASHRAE RP-1043 chiller data (CC0) | | |
| All detection, fusion, prioritization and mitigation-trigger logic, and every metric quoted here | | |

### Roadmap agent: laser scan digital twin (hardware-dependent, not built)

Mentioned verbally, not simulated with fake data, because it depends on hardware we don't have: a LiDAR/laser scanner (fixed-mounted on a critical zone, or on a drone/robot payload — e.g. Skydio 3D Scan, or a wall-crawler in the style of Gecko Robotics' TOKA). This is established practice elsewhere (TxDOT rescans bridges by drone LiDAR every two years for change tracking; MnDOT/Collins report 70-80% of defects visible on the digital twin before a field inspection), so the gap is hardware access, not feasibility.

Design, if built: a laser scan is registered against a baseline point cloud (ICP, via Open3D or PDAL) and reduced to a scalar — max or 95th-percentile deviation in a zone, or a deformation rate in mm/month. That number feeds `agents/generic.py` exactly like UPV or BMS does; no new report shape or coordinator logic is needed. Scans are **triggered reactively**, not run on a fixed calendar: when another agent's risk score in a zone crosses a threshold (e.g. Agent 1's UPV reading drifting, or Agent 0 flagging a crack), the coordinator requests a scan from this agent, the same "cheap continuous sensor gates an expensive inspection" pattern real structural-health-monitoring systems already use. A genuinely *predictive* scheduler — forecasting drift before a threshold is crossed — is a further-out, more speculative extension of this, not the current design.

## Self-check results (`python scripts/selfcheck.py`, 15/15 pass)

| Check | Result |
|---|---|
| Cascade wrapper plumbing (gate → grade → Finding → AgentReport) | pass (fake grader, no model) |
| Crack fallback, 1,600 held-out images | 92.9% accuracy, Brier 0.053 |
| UPV ≥20% below expected flagged | 10/10 (≥15%: 14/17) |
| UPV within 2% of expected reaching "high" | 0.2% |
| BMS AC-1 collapse (4-7 Sep 2018) flagged | 16 high/critical reports |
| Same scorer, provided vs inferred baselines | yes |
| Battery cells flagged before EOL | 3/3, 32-43 cycles early |
| Battery RUL MAE | 8.4 cycles (window chosen on the same cells) |
| Chiller false alarms, held-out fault-free runs | 1.5% |
| Chiller diagnosis, leave-one-severity-out | 96.9% |
| Chiller fault runs detected and diagnosed | 20/28 |
| Dashboard state advances every tick | 150 ticks, 1,008 reports fused |
| Mitigation fires and logs | yes (structural, battery, HVAC, UPV, BMS) |
| Disaster mode re-ranks | 15/15 toggles, 0.05 ms mean |

"34 real fault cases flagged" on the site is: 20 ASHRAE fault runs, 3 NASA cells before EOL, 10 low-UPV readings, and 1 CU-BEMS AC-unit collapse.

## Business plan

See [BUSINESS_PLAN.md](BUSINESS_PLAN.md) for the business case. It is kept separate from the technical README on purpose. In summary, Pavilion Cerebro sells one platform per building, and each subsystem agent is an add-on on the same interface, so expansion revenue comes from adding agents rather than new products. The team's go-to-market research is in `docs/research/09_business_models_gtm.md` and `docs/research/04_market_pain_size_regulation.md`.

## Repo structure

```
agents/          base.py (BaseAgent, AgentReport), generic.py (the any-series scorer),
                 structural_visual.py (wraps src/cascade), internal_sensor.py, battery.py, hvac.py
coordinator/     fusion.py, prioritization.py, mitigation.py, swarm.py (runtime + roadmap stubs)
dashboard/       server.py (stdlib HTTP + SSE), static/ (index.html, app.js, style.css)
data/            samples/ (committed, real, 2.4 MB), prepare_samples.py, download_datasets.py,
                 synthetic.py (fallback generator, marks anything it writes as SYNTHETIC)
scripts/         selfcheck.py, render_demo_video.py, build_site.py
site/            marketing website for Replit (static); site/walkthrough/ is the layperson walkthrough
assets/fonts/    IBM Plex (OFL) for the video renderer
src/cascade/     the existing inspection cascade (unchanged); see docs/cascade_README.md
```

Environment note: developed and verified on macOS with the system Python 3.9 in a local `.venv`. The cascade's own `pyproject.toml` asks for Python ≥3.11 (its conda setup is in `environment.yml`), but its tests also pass on 3.9, and Pavilion Cerebro imports it from `src/` without installing it.

## Credits

This repo's history was squashed to a single commit for a clean personal copy, so git's own contributor graph doesn't reflect who built what. For the record:

- **AthArvA-188** wrote the original inspection cascade (`src/cascade/`, `app/streamlit_app.py`) that Agent 0 wraps unchanged, and built a separate parallel "smart building" module set (numeric forecasting, facade/interior NDT, energy, rain, fire, clog) documented in `docs/FINDINGS_2026-09-26.md` and `docs/research/11-16_*.md`, not otherwise part of this build.
- **Leena Rajan Katkar** built the `index_1.html` pitch deck this README and `BUSINESS_PLAN.md` summarize.
- **Madhulika Vikraman** built the Pavilion Cerebro agents, coordinator, dashboard, marketing site, and layperson walkthrough (`agents/`, `coordinator/`, `dashboard/`, `site/`), with Claude (Anthropic) as a coding assistant throughout.
