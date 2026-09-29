# Pavilion Cerebro business plan

> **Source of truth:** the pitch deck (`index_1.html`, NOVI-INFRA / Pavilion Cerebro) has the full narrative, market sizing, competitive table and valuation math, with sources linked in its footer. This document is a prose summary of that deck plus one reconciliation this README-style file is for: **what the pitch describes vs. what's actually built** in this repo, so nobody presents a claim the code doesn't back up.

## The pitch, in one paragraph

The market sells point tools for pieces of a building — a BMS for HVAC, sensors for structure, drone inspection, elevator IoT — and no single product covers the whole building or acts on what it finds. Pavilion Cerebro is that missing layer: one swarm of AI agents (the "senses"), one coordinator (the "brain") that fuses every agent's report into one risk-ranked picture and triggers a response. The technical thesis carries over unchanged from the README: one shared agent interface, so adding a subsystem is writing one more agent, not rebuilding the platform.

## The full vision: 11 building systems

The pitch names eleven systems a complete Pavilion Cerebro would watch. This repo builds **4 of them for real, on real data**, and stubs the rest as clearly-labeled roadmap items — nothing beyond the 4 is simulated with fake data.

| Code (pitch) | System | Status in this repo |
|---|---|---|
| STR | Structure & materials (cracks, rebar, strain, tilt) | **Built** — Agent 0 (crack imagery) + Agent 1's UPV channel (internal concrete strength) |
| PWR | Energy & batteries | **Built** — Agent 2 (battery SOH/RUL/fire risk); whole-building energy/demand-peak monitoring is future scope |
| HVAC | HVAC & mechanical | **Built** — Agent 3 (chiller fault detection & diagnosis) |
| H2O | Plumbing & water | Roadmap stub (agent-4) — no public dataset found yet; needs a field-data partnership |
| FIRE | Fire & life safety (sprinkler pressure, valve tamper, panel signals) | Not yet a stub — distinct from the visual smoke agent below; add if pursued |
| ELEC | Panels & switchgear (heat, current, power quality) | Not yet a stub |
| WIRE | Wiring in walls (arc-fault, insulation) | Not yet a stub |
| LIFT | Elevators (door cycles, motor, vibration) | Not yet a stub |
| ENV | Building envelope (moisture, façade, thermal) | Not yet a stub |
| AIR | Indoor air quality (CO₂, PM2.5, VOCs, radon) | Not yet a stub |
| CYBER | Cyber (BMS network exposure) | Not yet a stub |
| — | Fire/smoke **visual** (camera-based) | Roadmap stub (agent-5) — public datasets exist, not yet integrated. This is a different sensing approach from the pitch's FIRE (which reads sprinkler/panel sensors, not camera images) |
| — | Laser scan digital twin (LiDAR) | Roadmap stub (agent-6, hardware-dependent) — a sensing *modality* that would primarily feed the STR agent (see README for the design) |

Each new row is the same size of work: one loader, reusing the same `AgentReport` interface and, for numeric sensors, the same `agents/generic.py` scoring engine Agents 1–3 already share. None of this needs new coordinator or prioritization logic.

## Market (from the pitch; sources in its footer and repeated here)

- **TAM:** global smart building market, $121.6B (2026) → $204.4B (2032), 9.0%/yr (MarketsandMarkets).
- **SAM:** ~590,000 US commercial buildings that already run some automation, × ~$12,000/yr → **$7.1B/yr** (PNNL adoption study; EIA CBECS building count).
- **SOM:** 3,000 buildings by Year 5 (0.5% of SAM) → **$36M ARR**, at $1,000/building/month.
- Adjacent markets cited: predictive maintenance $13.9B → $23.8B (11.4%/yr); facility management software $3.8B → $9.6B (11.1%/yr); structural health monitoring $2.5B → $4.1B (10.4%/yr).

## Why the gap is real, not assumed

- **~10%** of US commercial buildings run any building automation at all today (PNNL) — most small/mid-size buildings run nothing.
- **~39,000** US fires a year start with electrical faults (NFPA, via FM) — a system that watches wiring/panels continuously addresses a named, sourced failure mode, not a hypothetical one.
- Regulatory tailwinds are real and dated, not assumed: Florida requires structural milestone inspections at 30 years then every 10 for 3+ story condos; NFPA 70B (2023) requires annual inspection of electrical equipment. Both create a recurring, mandated need for condition data — exactly what an always-on swarm produces as a byproduct.

## Customers (from the pitch)

Real estate owners/REITs, facility management firms, condo/HOA associations (Florida milestone inspections are a concrete forcing function), hospitals (downtime/fire/water are patient-safety issues), data centers (battery rooms + NFPA 70B), universities, government/public buildings, and insurers (State Farm already gives customers free electrical-fire sensors — a signal insurers will pay to prevent claims, not just price them).

## Valuation estimate (from the pitch — an internal estimate for discussion, not financial advice)

- **Today, pre-seed target:** $12M post-money, inside the $10–15M median 2025 SAFE cap range (Carta).
- **Year 5 target:** $162M–$292M, from $36M ARR × 4.5–8.1× (private SaaS median-to-top-quartile multiples, Aventis Advisors).
- **Comparables:** BrainBox AI (autonomous HVAC AI, 14,000+ buildings, acquired by Trane in 2025 after ~$82M raised, price undisclosed) and PassiveLogic (autonomous building platform, $74M Series C Sept 2025, $125M+ total raised, Johnson Controls as an investor).

## What this repo can honestly claim today vs. what the pitch claims

- The pitch's competitive-gap table, market sizing and valuation math are the deck's claims, sourced there — this repo doesn't independently re-derive them, and nobody should present them as measured by our own pipeline.
- What *is* measured by our own pipeline — real detection accuracy, false-alarm rates, lead time before failure, re-triage speed — is in `data/samples/metrics.json` and the README's "Self-check results" table. Keep these two kinds of numbers clearly separate in a pitch: **market/business numbers are sourced from external research; product numbers are measured from our own code.**
- Only 4 of the pitch's 11 systems are real, on real public data, today. Say that plainly rather than let "11 systems" imply 11 are built — the architecture supports it; the data and code for 7 of them don't exist yet.

## Existing team research

`docs/research/04_market_pain_size_regulation.md` and `docs/research/09_business_models_gtm.md` were written for the original infrastructure-inspection cascade (bridges, wind, solar, utilities), not for the building-swarm pivot — re-check any figure from there against the building market before reusing it in a Pavilion Cerebro pitch.
