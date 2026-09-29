# Documentation Index and Technical Notes

| Field | Value |
|---|---|
| Project | Origin Weekend Fall 2026, Prompt D (Infrastructure & Resilience) |
| Version | 1.0 |
| Date | 2026-09-24 |
| Owner | Founding team |
| Status | Living index. Add a row whenever a document is created or its status changes. |

## 1. Document map

| Path | Purpose | Status | Read it when |
|---|---|---|---|
| `problem.md` | The prompt exactly as given by the organizers. Never edited. | Frozen | Quoting the prompt on Devpost or slide 1 |
| `docs/problem_statement.md` | Our detailed, sourced statement of the problem, who has it, why now, and what we build | v1.0 | Writing slides 1 and 2, onboarding a teammate |
| `docs/decisions.md` | Decision log D-001 to D-013 with options, rationale, status and revisit triggers | v1.0, two decisions Proposed | Before any design or scope debate |
| `docs/PRD.md` | Product requirements: personas, functional requirements FR-1 to FR-21, grading spec, prioritization model, metrics, finding contract | v1.0 | Before building any pipeline stage or UI element |
| `docs/implementation_plan.md` | Hour-by-hour plan Thursday to Monday, workstreams, repo layout, demo script, Q&A drills, risk register | v1.0 | Every checkpoint |
| `docs/progress.md` | Running log of what is done, status board per workstream, blockers, gaps | Live | Start and end of every work session |
| `docs/changelog.md` | Dated history of document and product changes | Live | Before committing a change that alters behavior or a decision |
| `docs/documentation.md` | This file: index, conventions, technical notes, glossary | v1.0 | Looking for anything |
| `docs/research/00_research_brief.md` | Synthesis of R01 to R09: verdicts on hypotheses, numbers safe for slides, numbers to avoid, gaps | v1.0 | Writing the deck |
| `docs/research/01_competitors_wind_solar.md` | R01: wind blade and solar PV inspection vendors, prices, claims, gaps | Done 2026-09-24 | Competitive slide, pricing anchors |
| `docs/research/02_competitors_bridges_powerlines_telecom.md` | R02: bridge, grid and telecom inspection vendors, regulation, white space | Done | Wedge rationale |
| `docs/research/03_competitors_underwater_industrial_disaster.md` | R03: subsea, NDT radiography, disaster assessment players and standards | Done | Roadmap and surge-mode slides |
| `docs/research/04_market_pain_size_regulation.md` | R04: cost of manual inspection, failure costs, asset counts, regulation, bottom-up SAM | Done | Problem and business-model slides |
| `docs/research/05_damage_grading_standards.md` | R05: per-industry taxonomies and thresholds, unified S0 to S4 schema, JSON contract | Done | Writing rubric files and the grading spec |
| `docs/research/06_vlm_tech_landscape_2026.md` | R06: model options, prices, structured outputs, cascade evidence, risks | Done | Building the pipeline |
| `docs/research/07_datasets_for_demo.md` | R07: about 40 datasets checked, licenses, recommended four, eval plan | Done | Downloading data, building eval_v1 |
| `docs/research/08_customer_voice_and_discovery.md` | R08: RFP language, practitioner quotes, personas, 22-target LA discovery plan, script | Done | Outreach and interviews |
| `docs/research/09_business_models_gtm.md` | R09: pricing benchmarks, funding calibration, channels, grant programs | Done | Business-model slide |
| `docs/discovery/` | Interview notes and the outreach funnel (to be created Friday) | Not started | Logging customer conversations |

## 2. Conventions (from `docs/decisions.md` D-011)

- **Citation key.** R01 to R09 refer to the nine research notes by number prefix.
- **Evidence labels.** `[Sourced: Rxx]` traceable to a research note; `[Team-measured]` our own eval output; `[Inference]` our reasoning from sources; `[Assumption]` a planning guess; `[Event]` a fact from the Origin Weekend onboarding packet.
- **No unlabeled numbers.** A number, quote, company fact or price without a label does not go into a doc or slide. Missing numbers are written as TBD and logged under gaps in `docs/progress.md`.
- **Hackathon rules that bind the docs.** No fabricated performance claims, survey results, or stage-of-development claims; sources must be referenced; the demo must be the team's own work.
- **Dates and times.** Absolute dates, YYYY-MM-DD; times Pacific.
- **Versioning.** Docs carry a version in their header table; changes are logged in `docs/changelog.md`.

## 3. Technical notes

### 3.1 Data flow

```
images + optional metadata sidecar
  -> ingest.py        run manifest (hash, dims, EXIF, asset_class, gsd, irradiance)
  -> gate.py          local small VLM: {usable, damage_present, confidence, reason}
        |-- not usable      -> finding U (not_measurable), never S0
        |-- no damage       -> finding S0 (record)
        `-- damage          -> crop.py
  -> crop.py          tiles above 1,568 px long side; optional zero-shot boxes
  -> grade.py         heavy VLM + rubric rows + exemplars -> finding contract JSON
  -> prioritize.py    score; S4 rule; per-class consequence lever
  -> review.py        accept / override / mark U, logged with prior model value
  -> export.py        CSV and JSON; bridge columns for SNBI-style entry
```

### 3.2 Finding contract

Defined in `docs/PRD.md` appendix A and derived from R05. The contract is the product: native scale first, unified level second, verbatim criterion, measurements, action with basis, evidence, review status.

### 3.3 Rubric files

One JSON file per asset class under `src/inspect/rubrics/`, each row copied from the standard as documented in R05: MBEI element condition states with numeric thresholds, NBI 0 to 9 component scale, ISO 4628-3 / ASTM D610 rust-area grades, IEC TS 62446-3 Annex C thermal patterns and dT bands, FEMA PDA damage matrix. Rows are quoted into the grader prompt and referenced by `criteria_matched`.

### 3.4 Evaluation artifacts

`data/eval_v1/manifest.jsonl` (frozen, hash recorded in `docs/progress.md`), `data/dev/manifest.jsonl`, `eval/rubrics/` (class-to-severity tables and team-grading rubric written before any results), `eval/reports/*.md` (metrics with n and bootstrap CIs). Protocol in `docs/decisions.md` D-007. Manifest row shape is shown in `docs/implementation_plan.md` section 4.

### 3.5 Model and cost facts used in the docs [Sourced: R06]

| Item | Value |
|---|---|
| Gate model | Qwen3-VL-4B via Ollama, Apache-2.0, 3.3 GB pull |
| Cloud gate fallback | Claude Haiku 4.5, $1 in / $5 out per million tokens; retirement not sooner than 2026-10-15 |
| Grader | Claude Sonnet 5, $2 in / $10 out per million tokens; structured outputs GA |
| Local grader fallback | Qwen3-VL-8B via Ollama, 6.1 GB |
| Image tokens (Claude) | ceil(w/28) x ceil(h/28); 1000x1000 = 1,296 tokens; standard tier max 1,568 px long side |
| Order-of-magnitude cost | about $10 per 1,000 1080p frames heavy-only on Sonnet 5; about $3 with a local gate at 30 percent pass-through; Batch API halves Claude figures |
| Structured output mechanics | Claude: JSON schema in the request's output configuration; Ollama: `format` option. Confirm exact parameter names by loading the `claude-api` skill before coding. |

### 3.6 Code map (as built 2026-09-24)

| Path | What it does | How to run |
|---|---|---|
| `src/cascade/` | The pipeline package (stages A to E, schema, cost log) | `python -m cascade.run --manifest data/dev/manifest.jsonl --out runs/dev01 --gate local --grader none` |
| `src/cascade/rubrics/*.json` | Standard rows and thresholds per asset class, quoted into the grader prompt | edited by hand; reviewed against R05 |
| `eval/build_eval.py` | Builds and freezes `data/eval_v1/manifest.jsonl` and `data/dev/manifest.jsonl`, downloading images as needed | `python eval/build_eval.py --download` |
| `eval/run_eval.py` | Scores a run folder against a manifest, writes `eval/reports/<name>.md` | `python eval/run_eval.py --manifest data/eval_v1/manifest.jsonl --run runs/x --name x` |
| `eval/rubrics/` | Class-to-severity maps and the team-grading rubric, fixed before any model output | read by the two scripts above |
| `scripts/download_data.py` | Fetches the corrosion and IR solar sources into `data/raw/` | `python scripts/download_data.py corrosion_cs ir_solar` |
| `tests/` | Unit tests for schema, routing, tiling, prioritization, export and review log | `python -m pytest -q` |
| `.env.example` | Model ids and Ollama URL; copy to `.env` | |

All commands run from the repo root inside the conda environment: `conda env create -f environment.yml` once, then `conda activate origin_hack` (or prefix commands with `conda run -n origin_hack`). Ollama must be running for `--gate local` and `--grader local`; use the `-instruct` model tags (see `.env.example`).

## 4. Glossary

| Term | Meaning |
|---|---|
| AASHTO MBEI | Manual for Bridge Element Inspection; defines element condition states CS1 (good) to CS4 (severe) with numeric thresholds |
| ADR | Automated defect recognition, used for radiography software |
| ATC-20 | Post-earthquake building safety evaluation: Inspected (green), Restricted Use (yellow), Unsafe (red) |
| BVLOS / Part 108 | Beyond visual line of sight drone operations; the FAA rule pending as of September 2026 |
| CoA | Class of Abnormality in IEC TS 62446-3: CoA 1 none, CoA 2 thermal abnormality, CoA 3 safety-relevant |
| CS1 to CS4 | MBEI element condition states |
| DINS | CAL FIRE Damage Inspection program; structure status classes Affected 1 to 9 percent, Minor 10 to 25, Major 26 to 50, Destroyed over 50 |
| DSP | Drone service provider |
| EPRI five-category scale | De facto wind blade damage severity, Cat 1 cosmetic to Cat 5 stop turbine; not a formal standard |
| FEMA PDA | Preliminary Damage Assessment classes: Affected, Minor, Major, Destroyed, Inaccessible |
| GSD | Ground sample distance, mm or cm per pixel; required for width and area thresholds |
| IEA Wind Task 46 | Leading-edge erosion classification Levels 0 to 5 with area thresholds |
| NBI / NBIS / SNBI | National Bridge Inventory; National Bridge Inspection Standards (23 CFR 650, routine interval at most 24 months); Specifications for the NBI (element-level data due 2028-03-15) |
| NDT | Non-destructive testing |
| O&M | Operations and maintenance |
| ROV | Remotely operated underwater vehicle |
| S0 to S4, U | Our unified action-based severity scale and the not-assessable state |
| VLM | Vision-language model |
| xBD / xView2 | Satellite building-damage dataset and challenge with a 4-level Joint Damage Scale |
