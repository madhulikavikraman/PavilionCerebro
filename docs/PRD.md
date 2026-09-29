# Product Requirements Document

| Field | Value |
|---|---|
| Project | Origin Weekend Fall 2026, Prompt D (Infrastructure & Resilience) |
| Version | 1.0 (hackathon MVP scope; v1 roadmap in section 12) |
| Date | 2026-09-24 |
| Owner | Founding team |
| Status | Draft for team review; depends on D-001, D-002 and D-008 in `docs/decisions.md` |

**Citation key.** R01..R09 = notes in `docs/research/`. Labels: [Sourced: Rxx], [Inference], [Assumption], [Team-measured]. See `docs/decisions.md` D-011.

## 1. Summary

An imagery-agnostic inspection grading layer. Users drop in photos or video frames from any drone, ROV, handheld camera, thermal sensor or radiograph. A small local vision-language model (VLM) gates every image for "damage present and image usable". Flagged images are cropped and graded by a heavy VLM on the customer's own industry scale, with the verbatim criterion matched, a unified S0 to S4 severity, a confidence and evidence crop. Findings roll into a prioritized work queue that a qualified inspector reviews, overrides and exports. The same pipeline runs in surge mode after a disaster.

The hackathon MVP proves this on real public imagery for bridge elements (primary), PV thermal modules (secondary) and post-disaster UAV imagery (surge mode), with measured accuracy on a frozen held-out set.

## 2. Problem

See `docs/problem_statement.md`. In one sentence: capture is cheap and abundant, but grading is slow, inconsistent and never ranked by consequence, so failures are missed and repairs are reactive.

Evidence the MVP must answer to [Sourced: R04, R08]:

- AEP Ohio's 2025 drone pilot covered about 4 percent of its distribution system, produced 400,000 to 500,000 images, and one person spent over 500 hours reviewing them.
- FHWA found only 68 percent of bridge condition ratings fell within one point of the mean across 49 inspectors; a 2026 Indiana study found 30 percent of ratings matched the expected value.
- NTSB attributed the Fern Hollow Bridge collapse to failure to act on repeated inspection recommendations: a prioritization failure, not a detection failure.
- Solar equipment-driven power loss rose from 2.36 percent in 2021 to 5.08 percent in 2025, up to about $5,070 per MW per year.

## 3. Goals and non-goals

**Goals (MVP, by Sun 2026-09-27 23:59 PT)**

1. Grade real inspection imagery on native industry scales for three asset classes with no per-class training.
2. Show the cascade working end to end with live per-image cost and latency.
3. Report measured triage and grading accuracy on `eval_v1` with confidence intervals.
4. Produce a prioritized, exportable work queue with a human review step.

**Non-goals (MVP)**

- Flight planning, hardware, autonomy.
- Fine-tuned models (D-013).
- Integrations beyond CSV and JSON export.
- Any claim of field accuracy.

## 4. Users and personas [Sourced: R08 section 4; R02; R09]

| Persona | Organization | Job to be done | What they judge us on |
|---|---|---|---|
| Bridge inspection engineer (primary) | Consulting engineering firm under contract to a DOT or county; county bridge engineer | Enter element-level condition states into the state system within deadline, with CS3/CS4 photo documentation and a per-structure work list | Fewer hours per bridge, defensible ratings, integration with InspectX / AASHTOWare BrM, liability stays with the inspector |
| Drone service provider owner or chief pilot | Small or mid DSP flying bridges, solar, poles | Deliver "AI-ready, utility-grade" reports to win and keep contracts | Turnaround, price per asset, resellable output |
| Solar O&M lead (secondary) | Regional solar owner or independent O&M firm | Turn a thermal survey into an IEC-classed anomaly list and repair plan | False alarms (there is little patience for even small numbers), production loss quantified |
| Emergency or resilience coordinator (surge mode) | County, utility storm team, insurer CAT team | Triage thousands of post-event images to FEMA classes in hours | Speed, confidence flags, export in the formats responders use |

## 5. Competitive position [Sourced: R01, R02, R03]

- Capture is owned by Skydio ($4.4B valuation), Zeitview, Percepto, ROV makers and Gecko Robotics. We do not compete on capture; we ingest anyone's imagery.
- Analytics incumbents are single-vertical and closed-vocabulary: SkySpecs and Clobotics on blades, Raptor Maps and Sitemark on solar, Buzz Solutions and Sharper Shape on grid. None found publishes grading definitions or the rationale per finding, none spans asset classes in one engine, and all are quote-only enterprise pricing except Scopito.
- Bridges have no dominant AI-grading vendor. Skydio's DOT case studies stop at 3D twins.
- Disaster triage products (ICEYE, Nearmap, Vexcel) serve insurers with building-level classes from overhead imagery; none grades engineered infrastructure and overhead imagery under-reports damage by at least 20 percent versus drones.

**Our edge, in order of defensibility [Inference]:** (1) standards-cited grading with the clause next to each finding; (2) one engine across asset classes and modalities via the VLM cascade; (3) an audit trail of human decisions against model output; (4) transparent per-asset pricing for the long tail; (5) surge mode on the same engine.

## 6. Functional requirements

Priority: P0 must ship for the demo; P1 ship if on schedule; P2 roadmap.

### 6.1 Ingest

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-1 | Accept a folder or upload of JPEG/PNG images; record filename, hash, dimensions, EXIF where present | P0 | 100 images ingested to a run manifest without error |
| FR-2 | Attach optional per-image metadata: asset id, asset class, GSD (mm per px), irradiance (W/m2), capture date | P0 | Missing values stored as null, never defaulted |
| FR-3 | Normalize 8-bit thermal images to a fixed grayscale plus pseudo-color and pass temperature statistics as text when radiometric data exists | P1 | Verified on one radiometric sample or explicitly skipped for the demo |
| FR-4 | Video frame extraction at a fixed interval | P2 | |

### 6.2 Gate (stage A)

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-5 | For every image return `{damage_present: bool, usable: bool, confidence: float, reason: string}` from a local small VLM with a JSON schema | P0 | Runs on the IR-solar dev set; output validates against schema 100 percent |
| FR-6 | Recall-first threshold tuned on the dev set only; log the fraction routed to the heavy stage | P0 | Threshold and routing fraction printed in the eval report |
| FR-7 | Cloud fallback (Haiku 4.5) selectable by flag | P1 | Same schema, same tests |

### 6.3 Crop (stage B)

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-8 | Tile images above 1,568 px on the long side into overlapping tiles; carry tile coordinates | P0 | dacl10k images (avg 1,950x1,581) tile without loss of coverage |
| FR-9 | Zero-shot detector (Grounding DINO or OWLv2) proposes boxes drawn onto crops for the grader | P1 | Boxes rendered; grader accuracy compared with and without on dev set |

### 6.4 Grade (stage C)

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-10 | Per flagged crop, return the finding contract in the appendix, schema-enforced | P0 | 100 percent schema-valid on eval_v1 |
| FR-11 | Rubric files per asset class containing the standard's own table rows and thresholds: MBEI element condition states and NBI 0 to 9 for bridges; IEC TS 62446-3 Annex C rows for PV; FEMA PDA matrix for disaster | P0 | Rubrics reviewed against R05 by a second teammate |
| FR-12 | `criteria_matched` must quote the rubric row verbatim; if no measurement supports a threshold, the finding is U or carries `not_measurable` | P0 | Spot check 20 findings |
| FR-13 | Few-shot exemplars (2 to 5 per class) retrieved from the dev set and included in the prompt | P1 | Toggle on/off compared on dev set |
| FR-14 | Second grader (local Qwen3-VL-8B) for disagreement-based escalation | P2 | |

### 6.5 Prioritize (stage D)

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-15 | Deterministic queue score (section 8) with S4 always at the top and same-day action | P0 | Unit test: any S4 outranks any S3 regardless of criticality |
| FR-16 | Per-asset-class consequence lever exposed in the score: production loss for PV, load posting or closure risk for bridges, occupancy for buildings | P1 | Visible in the queue table |
| FR-17 | Export queue as CSV and JSON; bridge export includes MBEI element, CS and quantity columns ready for SNBI-style entry | P0 | File opens in a spreadsheet; columns documented |

### 6.6 Review (stage E)

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-18 | Reviewer can accept, override grade, or mark U per finding; every action logged with timestamp and prior model value | P0 (table form) / P1 (full UI) | Review log persists across restarts |
| FR-19 | Show model-versus-reviewer agreement over time as the audit metric | P2 | |

### 6.7 Surge mode

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-20 | Batch run over a folder with FEMA PDA rubric, output a map-free ranked list and counts per class with confidence and U counts | P0 | Runs on 40 RescueNet tiles in the eval; counts shown |

### 6.8 Demo UI

| ID | Requirement | Priority | Acceptance |
|---|---|---|---|
| FR-21 | Single-page app: choose dataset or upload, run, watch stage counters, per-image cost and latency, findings table with crops, queue, export, review buttons | P0 | 60-second walkthrough recorded without errors |

## 7. Grading specification [Sourced: R05]

The unified scale is defined by action semantics so it is comparable across industries.

| Level | Meaning | Queue action |
|---|---|---|
| S0 | No finding | Record; baseline for change detection |
| S1 | Cosmetic or minor | Log; monitor at routine cadence |
| S2 | Moderate | Schedule in next campaign |
| S3 | Major | Engineering review within weeks; consider derate, posting or restriction |
| S4 | Critical or safety | Same-day escalation; stop, isolate, close or red-tag |
| U | Not assessable | Re-image or other NDT; never default to S0 |

MVP native mappings:

| Native scale | S0 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|
| Bridge NBI component 0 to 9 | 9, 8 | 7, 6 | 5 | 4, 3 (flag `load_posting_review` at 3) | 2, 1, 0 |
| Bridge MBEI element CS | CS1 | CS2 | CS3 | CS4 | CS4 with instability indicators |
| Steel coating ISO 4628-3 / ASTM D610 | Ri0 / 10 | Ri1 / 9 to 8 | Ri2 to Ri3 / 7 to 5 | Ri4 to Ri5 / 4 to 0, flag `section_loss` | only if section loss compromises structure |
| Corrosion Condition State dataset labels (these are MBEI CS1 to CS4 for steel corrosion) | Good (CS1) | Fair (CS2) | Poor (CS3) | Severe (CS4), flag `load_posting_review` | Severe with instability indicators |
| PV IEC TS 62446-3 CoA | CoA 1 | (none) | CoA 2 module or substring, dT 2 to 7 K | CoA 2 hot cell 10 to 40 K; string or inverter outage | CoA 3: over 40 K cell, broken glass, arc |
| Disaster FEMA PDA | undamaged | Affected | Minor | Major | Destroyed; Inaccessible maps to U |

The Corrosion Condition State row is our own mapping of the dataset's four labels onto S-levels and must be fixed before eval [Assumption]. The full multi-industry table (wind, hull, waterfront, weld RT, poles, insulators) is in R05 and ships as roadmap rubrics.

Uncertainty is reported as +/-1 level following EPRI's guidance on blade categories.

## 8. Prioritization model [Assumption: weights are ours; the levers are sourced from R05]

```
score = severity_weight[S] * criticality * consequence * urgency
severity_weight = {S1: 1, S2: 3, S3: 9, S4: 27}; U is listed separately, never scored as S0
criticality   = 1 to 3, user-supplied per asset (e.g. daily traffic band, customers served, MW)
consequence   = per asset class: PV = estimated production loss; bridge = 2 if load_posting_review flag else 1; building = occupancy class
urgency       = 1 + (days since finding / 30), capped at 2
rule          = any S4 sorts above every non-S4 regardless of score and gets action "escalate", sla_days = 0
```

Weights and multipliers are printed in the UI so a reviewer can see why an item ranks where it does.

## 9. Non-functional requirements

| Area | Requirement | Basis |
|---|---|---|
| Cost | Show measured dollars per image per stage in the UI. Expected order of magnitude: about $10 per 1,000 1080p frames heavy-only on Sonnet 5, about $3 with a local gate at 30 percent pass-through | [Sourced: R06] |
| Latency | Show measured median seconds per image per stage | [Team-measured] |
| Privacy | Gate stage runs locally so only flagged frames leave the machine; a fully local mode exists for customers who cannot use a public API | [Sourced: R06, R09] |
| Honesty | Every accuracy figure carries n and a CI; U and confidence are always visible | D-007 |
| Robustness | Resolution normalization and tiling because resolution changes caused 82.6 percent label flips in a field deployment | [Sourced: R03] |
| Licenses | Non-commercial datasets are demo-only and labeled on the data slide | [Sourced: R07] |

## 10. Evaluation and success metrics

Protocol: `docs/decisions.md` D-007 and R07.

| Metric | Target for the demo [Assumption] | Why |
|---|---|---|
| Gate recall on `damage_present` | at least 0.95 on eval_v1 with CI shown | A miss is a skipped inspection |
| Gate routing fraction | reported, no target | Drives the cost story |
| Grader macro-F1 on classes present | reported, no target | Literature ceiling is modest: GPT-4o 74.9 percent on MMAD (R06) |
| Grading within-one-grade accuracy (corrosion, RescueNet) | reported, no target | EPRI's own +/-1 tolerance |
| Schema validity | 100 percent | Product contract |
| Cost and latency per image | reported | Unit economics |

Success for the hackathon means the numbers exist, are honest, and the story survives Q&A.

## 11. Data and licensing

See `docs/decisions.md` D-006. Commercial bootstrapping is limited to permissively licensed sets (Corrosion Condition State CC0, InfraredSolarModules MIT, SDNET2018 CC BY 4.0, COCO-Bridge CC0, TTPLA Apache-2.0) [Sourced: R07].

## 12. Roadmap after the weekend [Inference]

1. Wind blades (EPRI five-category and IEA Task 46 erosion levels), poles and insulators, hull and waterfront, weld radiography: rubrics already mapped in R05.
2. Radiometric thermal and 16-bit radiograph preprocessing (R06).
3. Multi-vendor grader abstraction and disagreement escalation.
4. Exports to InspectX and AASHTOWare BrM, CMMS.
5. Asset registry with baselines for change detection and true post-event triage.
6. Compliance: SOC 2 roadmap, self-hosted option (R09).

## 13. Business model hypothesis

See `docs/decisions.md` D-008. Per-asset pricing, free gate-only tier, consultants and DSPs first, utilities and DOTs via programs and grants.

## 14. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hallucinated defects or memorized answers regardless of image (R06) | Grounded crops, schema-enforced criteria quotes, U state, human review, report our own error rate |
| Mid-scale grades are the hardest (xBD Major F1 0.0094) (R05) | Show within-one-grade accuracy and confidence; never claim exact-match dominance |
| Thermal domain gap (R06) | Demo on 8-bit modules; radiometric handling is roadmap |
| Model availability and pricing: Haiku 4.5 may retire after 2026-10-15 (R06) | Vendor-agnostic schema and prompt template |
| Judges ask "why not focus?" | One beachhead (D-001), engine generality shown as next steps |
| Judges ask for customers | Honest funnel from the discovery plan in R08 section 5 |

## 15. Open questions

1. D-001 and D-002 confirmation at the Friday sync.
2. Willingness to pay from at least three interviews.
3. Whether the zero-shot detector improves grader accuracy on the dev set enough to keep.

## Appendix A. Finding contract (v0) [Sourced: R05]

```json
{
  "asset_class": "bridge_element | steel_coating | pv_module | building_disaster",
  "defect_type": "<native taxonomy term>",
  "native_scale": {
    "standard": "NBI-0-9 | MBEI-CS | ISO-4628-3 | IEC-62446-3-CoA | FEMA-PDA | CorrosionCS",
    "value": "<code>",
    "criteria_matched": ["<verbatim threshold matched>"]
  },
  "unified": {
    "level": "S0|S1|S2|S3|S4|U",
    "uncertainty": "+/-1",
    "flags": ["fire_shock_pathway", "load_posting_review", "section_loss", "not_measurable"]
  },
  "measurements": {
    "area_cm2": null, "crack_width_mm": null, "delta_t_k": null,
    "percent_area_rusted": null, "section_loss_pct": null, "confidence": 0.0
  },
  "action": {"code": "record|monitor|schedule|prioritize|escalate", "sla_days": null, "basis": "<standard clause>"},
  "evidence": {"image_ids": [], "bbox": [], "tile": null, "gsd_mm_per_px": null, "irradiance_wm2": null},
  "review": {"status": "pending|accepted|overridden|marked_u", "reviewer": null, "reviewed_at": null, "prior_level": null}
}
```
