# Implementation Plan

| Field | Value |
|---|---|
| Project | Origin Weekend Fall 2026, Prompt D (Infrastructure & Resilience) |
| Version | 1.0 |
| Date | 2026-09-24 (Thursday evening) |
| Owner | Founding team |
| Status | Active. Update `docs/progress.md` at every checkpoint. |

All times Pacific. Event facts come from the Origin Weekend onboarding packet (Google Doc) and are marked [Event]. Research citations R01..R09 as in `docs/decisions.md`. Team roles are placeholders until the team roster is final [Assumption].

## 1. Deadlines and event calendar [Event]

| When | What | Where |
|---|---|---|
| Thu 2026-09-24 23:00 | Team registration form due | Google Form linked in the packet |
| Fri 2026-09-25 12:30 to 15:00 | Virtual mentorship hours (one session per team; sign up for one slot) | Virtual |
| Fri 2026-09-25 18:30 / 19:00 / 19:30 / 20:00 | Replit 101, Replit demo, open tech support, pizza | EEB 132 |
| Sat 2026-09-26 10:00 to 12:00 | Second mentor slot available | Virtual |
| Sun 2026-09-27 23:59 | Devpost submission due. No exceptions. | Devpost |
| Mon 2026-09-28 12:00 | Individual check-out form due, every member | Google Form |
| Mon 2026-09-28 17:15 | Team check-in for the pitch | Ginsburg Auditorium (GCS) |
| Mon 2026-09-28 18:00 | Final pitch showcase: 3 minutes plus 2 minutes Q&A for the 10 to 15 finalists | GCS |
| Mon 2026-09-28 21:00 | Winners announced | GCS |

Other event facts that shape the plan [Event]: not judged on visual polish; a demo may be working code, a dashboard, video, market analysis or customer testimonials; embed a 30-second video or screenshots in the deck to avoid day-of failures; submissions must reference sources and may not contain fabricated performance claims or survey results; team size 2 to 6; a Replit promo gives one month of Core and $20 credits; the SHIP fund ($15k) closes 2026-10-02.

## 2. Workstreams and owners

| Stream | Scope | Owner |
|---|---|---|
| A. Data and eval | Downloads, `eval_v1` freeze, ground-truth scripts, team grading, metrics report | TBD |
| B. Pipeline | Gate, crop, grade, prioritize, export | TBD |
| C. UI and demo | Streamlit app, demo script, video | TBD |
| D. Customer discovery | Outreach, interviews, honest funnel log | TBD (non-engineer if available) |
| E. Deck, Devpost, pitch | Six slides, description, video upload, rehearsal | TBD |

Checkpoints: Fri 09:00, Fri 18:00, Sat 12:00 (cut-line review, D-009), Sat 20:00, Sun 14:00 (eval freeze for the deck), Sun 20:00 (submission dry run).

## 3. Hour-by-hour plan

### Thursday 2026-09-24 (evening) — done or in flight

- Research notes R01 to R09, problem statement, decision log, PRD, this plan. Done.
- Submit the team registration form before 23:00 [Event]. **Owner: TBD. Verify tonight.**
- Create the Devpost account for every member and join the hackathon [Event].

### Friday 2026-09-25

| Time | Stream | Task | Done when |
|---|---|---|---|
| 09:00 | All | Sync: confirm D-001, D-002, D-008; assign owners; agree cut lines | `docs/decisions.md` statuses updated |
| 09:30 | B | Done Thursday night: repo skeleton (section 4), conda env `origin_hack` (Python 3.13, `environment.yml`), Ollama installed, `qwen3-vl:4b-instruct` and `qwen3-vl:8b-instruct` pulled, Anthropic SDK key in `.env`, `claude-api` skill consulted before writing API code | `python -m cascade.run --help` runs |
| 09:30 | A | Download Corrosion Condition State (333 MB, figshare), dacl10k validation split, InfraredSolarModules HF parquet, RescueNet test split (R07). Record license text found inside each download | `data/raw/*` present; `docs/progress.md` lists licenses |
| 10:00 | D | Send the 90-word outreach template (R08 section 5.2) to the 22 targets in R08 section 5.1; sign up for one mentor slot [Event] | Outreach count logged |
| 11:00 | A | Write the class-to-severity mapping tables for IR solar and the dacl10k team-grading rubric **before** any model output is seen (D-007) | Tables committed under `eval/rubrics/` |
| 12:00 | A | Build `eval_v1/manifest.jsonl` (about 180 images, stratified per D-007) and `dev/` (50 images); freeze | Manifest hash recorded in `docs/progress.md` |
| 12:00 | B | Gate stage (FR-5, FR-6) on the IR-solar dev set; JSON schema validation; routing fraction printed | Dev recall printed |
| 14:00 | B | Rubric files: `bridge_mbei.json`, `bridge_nbi.json`, `corrosion_cs.json`, `pv_iec62446_3.json`, `disaster_fema.json`, using rows from R05 | Second teammate reviews against R05 |
| 15:00 | B | Grade stage (FR-10 to FR-12) on corrosion dev images with Sonnet 5 structured outputs; U handling when GSD missing | 10 findings inspected by hand |
| 16:00 | C | Streamlit skeleton: pick dataset, run, stage counters, findings table with crops | Runs on 10 images end to end |
| 18:00 | All | Checkpoint. Optional: Replit 101 at EEB 132 [Event] if someone wants to host the UI there | `docs/progress.md` updated |
| Evening | B | Tiling (FR-8) for dacl10k; prioritization score and export (FR-15, FR-17) | Queue CSV produced on dev set |

### Saturday 2026-09-26

| Time | Stream | Task | Done when |
|---|---|---|---|
| 09:00 | A | Two teammates grade dacl10k eval images independently with the rubric; compute Cohen's kappa; adjudicate | Kappa in `docs/progress.md` |
| 09:00 | B | Grade stage on dacl10k and IR solar; few-shot exemplars from dev set (FR-13) | Dev-set comparison with and without exemplars |
| 10:00 | D | Interviews (aim for three by Saturday night); log verbatim notes and consent to quote per R08 section 5.4 | Notes in `docs/discovery/` |
| 12:00 | All | **Cut-line review** per D-009 | Decisions logged |
| 13:00 | B | Surge mode (FR-20) on RescueNet dev tiles with FEMA rubric; counts per class, U counts | Runs on 10 tiles |
| 14:00 | C | Review actions (FR-18) with persistent log; cost and latency counters; export button | Restart-safe |
| 16:00 | A | First full `eval_v1` run through the whole cascade; metrics report with bootstrap CIs (`eval/run_eval.py`) | `eval/reports/eval_v1_run1.md` |
| 18:00 | B, A | Fix systematic failures found in run 1 using the **dev** set only; note every change in `docs/changelog.md` | |
| 20:00 | All | Checkpoint; E drafts slides 1, 2, 4, 5 from the research brief and interview notes | Draft deck |
| Stretch | B | Zero-shot detector (FR-9) on dev set; keep only if it improves grader accuracy | Comparison logged |

### Sunday 2026-09-27

| Time | Stream | Task | Done when |
|---|---|---|---|
| 09:00 | A | Final `eval_v1` run, frozen. No more prompt changes after this | `eval/reports/eval_v1_final.md` |
| 10:00 | C | Demo script (section 6) rehearsed twice; record the 30 to 60 second video with the real app | `demo/demo.mp4` |
| 11:00 | D | Last interviews; finalize the funnel: sent, replied, interviewed, quotable | Funnel table in the deck |
| 12:00 | E | Slides 3 and 6 with measured numbers and screenshots; every number labeled per D-011 | Deck v1 |
| 14:00 | All | Deck review against the rubric: problem and customer insight, solution and business model, execution and communication | Deck v2 |
| 16:00 | E | Export deck PDF; write the "What did you build?" description; prepare demo link (Replit or a public video and repo) | Assets ready |
| 18:00 | E | Devpost dry run: team code, exact prompt question, PDF, demo link, video, description, all members added [Event] | Checklist complete |
| 20:00 | All | Submit. Do not wait for 23:59 | Confirmation screenshot saved |
| 21:00 | All | Update `docs/progress.md` and `docs/changelog.md`; write the pitch script | |

### Monday 2026-09-28

| Time | Task |
|---|---|
| 09:00 | Every member submits the individual check-out form (due 12:00) [Event] |
| 10:00 | Three-minute pitch rehearsal, five runs, with Q&A drills from section 7 |
| 17:15 | Team check-in at GCS; laptop, charger, offline copy of video and deck |
| 18:00 | Showcase |

## 4. Repository layout [Assumption]

```
origin_hack/
  problem.md                  # the prompt as given; never edited
  docs/                       # this folder
  data/                       # gitignored
    raw/<dataset>/
    eval_v1/manifest.jsonl    # frozen; hash recorded in progress.md
    dev/manifest.jsonl
  src/cascade/                # package name avoids shadowing the stdlib `inspect` module
    schema.py                 # pydantic models of the finding contract (PRD appendix A)
    costlog.py                # per-call tokens, dollars, seconds
    ingest.py                 # folder/upload to run manifest; EXIF; metadata sidecar
    gate.py                   # stage A: local small VLM via Ollama, JSON schema; Claude fallback
    crop.py                   # stage B: tiling; optional zero-shot detector
    grade.py                  # stage C: heavy VLM with rubric + exemplars, structured outputs
    rubrics/*.json            # standard rows and thresholds per asset class (from R05)
    prioritize.py             # stage D: deterministic score, S4 rule
    review.py                 # stage E: SQLite review log
    export.py                 # CSV/JSON; bridge columns for SNBI-style entry
    run.py                    # CLI: python -m cascade.run --manifest ... --out runs/<id> --gate local --grader claude|local|none
  eval/
    build_eval.py             # stratified sampling, ground-truth derivation, freeze
    rubrics/                  # class-to-severity tables, team-grading rubric
    run_eval.py               # metrics, bootstrap CIs, markdown report
    reports/
  app/streamlit_app.py
  scripts/download_*.py
  tests/
  demo/                       # video, screenshots
```

Manifest rows (`data/eval_v1/manifest.jsonl`), one JSON object per line, dates as YYYY-MM-DD:

```json
{"file": "corrosion/img_0001.jpg", "sha256": "<hex>", "source_dataset": "corrosion_cs", "split": "test",
 "asset_class": "steel_coating", "damage_present": true, "classes_present": ["corrosion"],
 "grade_native": "Poor", "grade_source": "dataset|team-graded", "frozen_on": "2026-09-25"}
```

## 5. Pipeline build notes

- **Gate prompt** asks two questions and nothing else: is the image usable (blur, exposure, occlusion) and is there visible damage of any kind. Output schema `{usable, damage_present, confidence, reason}`. Tune the threshold for recall on the dev set only (D-007).
- **Grade prompt** contains: the rubric rows for the asset class verbatim; the finding contract schema; 2 to 5 exemplar crops with their native labels from the dev set; the crop with tile coordinates; available metadata (GSD, irradiance). Instruction: quote the criterion matched; if a threshold needs a measurement you cannot make, return U with `not_measurable`.
- **Structured outputs**: Claude structured outputs are GA on Sonnet 5 via a JSON schema in the request's output configuration (R06); Ollama constrains local models with its `format` option (R06). Coordinates from Claude are absolute pixels of the resized image, so normalize once (R06). Confirm parameter names by loading the `claude-api` skill before coding.
- **Image sizing**: keep crops at or under 1,568 px on the long side; a 1000x1000 image costs about 1,296 input tokens (R06).
- **Cost and latency logging**: record tokens, dollars and wall time per call per stage to `runs/<id>/calls.jsonl`; the UI reads it live.
- **Prioritization**: implement PRD section 8 exactly; print the multipliers next to each row.

## 6. Demo script (60 seconds, recorded and live)

1. Open the app on the corrosion dataset folder (10 images). Say: "Real steel bridge photos with inspector-assigned condition states."
2. Press run. Stage counters tick: 10 gated locally, 6 flagged, 6 graded. Cost and latency shown.
3. Click one finding: crop, native grade "Poor" with the criterion quoted, S3, confidence, action "prioritize".
4. Switch to the queue: S4 item at the top with "escalate, same day"; multipliers visible.
5. Override one grade as a reviewer; the log shows prior value and reviewer.
6. Switch dataset to PV thermal: same pipeline, IEC class output. Then RescueNet: FEMA classes and U count.
7. Export CSV. End on the eval report: gate recall, within-one-grade accuracy, n and CI.

## 7. Q&A drills

- "Why not focus on one thing?" One beachhead, bridge consultants (D-001); the engine is what generalizes.
- "Inspectors must rate bridges themselves." Yes; we pre-fill and log their decision (D-012).
- "How accurate?" Only our measured numbers with n and CI; literature quoted as feasibility only (D-007).
- "Who pays?" Consultants and DSPs per asset; free gate tier; utilities via programs (D-008).
- "Why now?" VLM cascade economics (R06), SNBI 2028 and Part 108 timing (R02, R04).
- "What about Raptor Maps or SkySpecs?" Single-vertical, unpublished grading definitions, enterprise-only pricing (R01).

## 8. Risk register

| Risk | Signal | Response |
|---|---|---|
| Downloads slow or blocked | Not on disk by Fri 12:00 | Use HF mirrors; reduce dacl10k to 200 images |
| Local model too slow on team laptops | Gate over 5 s per image | Switch gate to Haiku 4.5 (FR-7); note cost |
| Grader accuracy poor on corrosion | Within-one-grade under 0.6 on dev | Add exemplars; simplify to a three-level mapping; report honestly |
| No interview replies | Zero by Sat 10:00 | Walk-in targets in R08 section 5.1; log the funnel anyway |
| Team behind at Sat 12:00 | Any P0 not started | Apply cut lines in D-009 order |
| API key or billing issue | Errors | Fully local mode (D-005 fallback) |

## 9. Definition of done for the Devpost entry [Event]

- All members on the Devpost project; team code correct; exact prompt question included.
- Six-slide deck as PDF following the required outline: Problem and Customer; Customer Insights; Solution/MVP; Value Prop and Differentiation; Business Model Hypothesis; Next Steps.
- Demo link (app or public repo plus video) and a 30 to 60 second video showing what was built.
- "What did you build?" description written.
- Every number in the deck labeled per D-011; sources referenced.
