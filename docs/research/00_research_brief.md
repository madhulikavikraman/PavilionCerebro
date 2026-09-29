# 00 - Research Brief: What the Nine Notes Say, and What to Put on the Slides

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | 2026-09-24 |
| Inputs | R01 to R09 in this folder (about 3,450 lines, all web-sourced on 2026-09-24) |
| Purpose | One page the deck can be written from, with every number traceable |

## 1. Ten findings that matter

1. **Capture is commoditized; analysis is the bottleneck.** Drone capture is 5 to 10x cheaper than rope access and 4 to 8x cheaper than helicopter patrol; analytics is already sold as a separate $100 to $300 per turbine line item (R04). AEP Ohio's 2025 pilot produced 400,000 to 500,000 images and one person spent over 500 hours reviewing them (R08).
2. **Grading is inconsistent and it costs money.** FHWA: only 68 percent of bridge condition ratings within one point of the mean across 49 inspectors; 2026 Indiana study: 30 percent matched expected; manual crack-area measurements vary from 18 percent to over 100 percent (R08). EPRI: no standard blade damage categorization; agreement on any category was rare; recommend a one-category uncertainty (R05).
3. **The worst failures were prioritization failures.** NTSB on Fern Hollow: failure to act on repeated inspection recommendations. The I-40 Hernando de Soto fracture was visible in 2019 drone footage and acted on in 2021 (R08).
4. **Incumbents are single-vertical, closed-vocabulary and quote-only.** SkySpecs, Clobotics, Cornis on blades; Raptor Maps, Sitemark, Above on solar; Buzz, Sharper Shape, Hepta on grid; none publishes grading definitions or per-finding rationale; only Scopito publishes prices (R01, R02, R09).
5. **Bridges have no dominant AI-grading vendor and the most codified scales.** Skydio's DOT case studies stop at 3D twins (R02). MBEI condition states have numeric thresholds; SNBI element-level data is due 2028-03-15; routine inspections at most every 24 months (R02, R04, R05).
6. **The cascade architecture is validated in the 2025-2026 literature.** A cheap pre-filter cut VLM calls 240x in a deployed system; a detector plus constrained model gave a 4 percent hallucination rate versus 65 percent zero-shot; frontier VLMs are weak at localizing small defects, GPT-4o scored 74.9 percent on MMAD (R02, R06).
7. **Only six public datasets carry a severity label; one is a bridge set with real inspector grades** (Corrosion Condition State, CC0). Most quality sets are non-commercial, so the business is rubrics, evaluation and workflow, not a trained model (R07).
8. **Buyers buy compliance plus a work list.** Bridge RFPs require entry into the state system by deadline, CS3/CS4 photo documentation and a per-structure maintenance list; one county fines $100 per day for late entry (R08). Utilities evaluate safety prequalification first and price last (R09).
9. **Avoided-failure economics beat inspection savings.** Solar: 5.08 percent average loss, up to $5,070 per MW per year; wind: $30k minor repair versus $500k structural; bridges: $467B repair backlog across 624,167 bridges with 41,677 poor; Duke's 2024 storms cost about $2.8B (R04).
10. **Disaster triage is government-endorsed but under-served for infrastructure.** FEMA's July 2025 PDA guide invites analytics on imagery; insurers already get building-level classes in 24 to 48 hours; nobody grades poles, spans, piers or blades post-event (R03).

## 2. Verdicts on the problem-statement hypotheses

| Hypothesis | Verdict | Evidence |
|---|---|---|
| H1 Single-vertical, closed-model tools | Supported | Blade-only and solar-only vendors; closed-vocabulary CNN detectors on grid (R01, R02) |
| H2 Detection without industry-native grading | Supported | "Severity ratings" without published definitions; no vendor ships MBEI condition states with clauses (R01, R02); public datasets stop at defect type (R07) |
| H3 No consequence-aware prioritization | Partially supported | SkySpecs and Raptor Maps frame findings in AEP or dollars; Noteworthy claims faster storm assessment; no cross-asset consequence-ranked queue found (R01, R02) |
| H4 Enterprise-only economics | Supported | All analytics incumbents quote-only except Scopito; DSPs and sub-100 MW owners left with AI-less generic tools (R01, R09) |
| H5 Poor fit for thermal, radiographic, underwater | Partially supported | Solar vendors handle thermal well within solar; radiography ADR is on-prem manufacturing software; underwater AI is a thin bolt-on; nobody spans modalities (R01, R03) |
| H6 Nothing built for the disaster surge | Refined | Insurers have 24 to 48 hour building products (ICEYE, Nearmap, Vexcel); none grades engineered infrastructure (R03) |

## 3. Numbers safe for slides (each with its note)

| Number | Use on slide | Source |
|---|---|---|
| 400,000 to 500,000 images; 500+ hours of one person's review (AEP Ohio, 2025) | Problem | R08 |
| 68 percent of ratings within +/-1 (FHWA, 49 inspectors); 30 percent matched (Indiana 2026) | Problem | R08 |
| 624,167 US bridges; 41,677 poor; $467B to repair | Problem, market | R04 |
| Routine inspection at most every 24 months; SNBI element data due 2028-03-15 | Why now | R02, R04 |
| 5.08 percent solar loss; up to $5,070 per MW per year | Problem, solar | R04 |
| $30k minor blade repair vs about $500k structural | Value at stake | R04 |
| Duke Energy 2024 storms about $2.8B net of insurance | Disaster | R04 |
| LA fires: 18,189+ structures damaged or destroyed | Disaster, local | R03 |
| Scopito EUR 160 / 80 per turbine; $100 to $300 analytics add-on; about $313 per pole implied | Pricing anchors | R01, R04, R09 |
| About $10 per 1,000 frames heavy-only; about $3 with local gate at 30 percent pass-through (Sonnet 5, Sept 2026 prices) | Unit economics | R06 |
| 4 percent vs 65 percent hallucination, hybrid vs zero-shot (arXiv 2605.26533) | Feasibility | R02, R06 |
| Buzz Solutions $20M Series A on three utility logos (2026-08-04) | Traction calibration | R09 |

## 4. Numbers to avoid

- Vendor accuracy claims (Clobotics over 95 percent recall, Buzz "90 percent plus", Sharper Shape "over 95 percent", Aramco ADR 90 to 95 percent): unaudited marketing (R01, R02, R03).
- Analyst market sizes ($15.5B drone inspection, $32B AI vision inspection): service revenue or manufacturing QC, not our software layer (R04). Use the bottom-up SAM framing in R04 section 7 instead, labeled Inference.
- The 100 percent result on 30 images in the RAG-VLM blade paper: too small to mean anything (R01, R06).
- Aggregator funding figures where sources conflict (Zeitview pilot count, SkySpecs round letter, Percepto rounds) (R09).
- Any accuracy for our own pipeline until `eval_v1` has run (D-007).

## 5. Gaps to close by interviews (R08 section 5)

- Willingness to pay per bridge element set or per report from a consulting firm or county engineer.
- Which state system the LA-area targets use (InspectX, AASHTOWare BrM, HSIS) for the export column format.
- Whether solar DSPs would pay under the $100 per turbine or per-MW analytics floor for standards-cited output.
- The trust threshold: what accuracy, audit trail and liability posture a reviewer needs before using a pre-filled grade (R08 script Q8).
