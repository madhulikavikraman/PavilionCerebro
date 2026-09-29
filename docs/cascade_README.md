# Inspection grading cascade

Origin Weekend Fall 2026, Prompt D (Infrastructure & Resilience). An imagery-agnostic
inspection grading layer: a small local vision-language model gates every frame, a heavy
model grades flagged frames on the industry-native scale with the rubric criterion quoted
verbatim, findings roll into a consequence-weighted work queue, and a qualified inspector
reviews, overrides and exports. The same pipeline runs in surge mode after a disaster.

Documents: `docs/problem_statement.md`, `docs/PRD.md`, `docs/decisions.md`,
`docs/implementation_plan.md`, `docs/progress.md`. Research notes in `docs/research/`.

## Setup (conda, not venv)

```powershell
conda env create -f environment.yml        # Python 3.13, installs the package with dev + ui extras
conda activate origin_hack
copy .env.example .env                     # then fill ANTHROPIC_API_KEY
ollama pull qwen3-vl:4b-instruct           # local gate
ollama pull qwen3-vl:8b-instruct           # optional local grader
```

If the env already exists: `conda activate origin_hack; pip install -e .[dev,ui]`.

Datasets (public, licenses noted in `docs/progress.md`): `python scripts/download_data.py`,
then `python eval/build_eval.py` to build the frozen `data/eval_v1` and `data/dev` manifests,
then `python scripts/make_demo_manifests.py` for the small demo sets used by the app.

## Run

```powershell
# gate only, no API cost
python -m cascade.run --manifest data/dev/manifest.jsonl --out runs/gate_dev --grader none

# full cascade on 10 images with dev-set exemplars in the grader prompt
python -m cascade.run --manifest data/demo/corrosion_cs/manifest.jsonl --out runs/demo_corr --exemplars data/dev/manifest.jsonl

# surge mode over a folder of post-event UAV images (FEMA PDA rubric)
python -m cascade.surge --folder data/raw/rescuenet/images --out runs/surge01 --limit 40

# score a run against the frozen eval set (bootstrap CIs)
python eval/run_eval.py --manifest data/eval_v1/manifest.jsonl --run runs/eval_v1_run1 --name eval_v1_run1

# demo UI
streamlit run app/streamlit_app.py   # tabs: Inspect run, Drop & grade, Batch, Reports, Eval matrix, Why this approach

# tests (no model, no network)
pytest -q
```

Backends: `--gate local|claude|none`, `--grader claude|local|none`. Model ids come from `.env`.
Runs are resumable: rerun with the same `--out` to continue after an interruption.

## Layout

```
src/cascade/
  schema.py      finding contract (PRD appendix A), pydantic
  ingest.py      folder or manifest -> ImageRecord rows (hash, size, EXIF date, sidecar metadata)
  gate.py        stage A: usable? damage? local Qwen3-VL via Ollama or Claude Haiku
  crop.py        stage B: 1568 px overlapping tiles, model-ready resizing
  grade.py       stage C: rubric-driven grading, schema-enforced (Claude parse / Ollama format)
  exemplars.py   FR-13: few-shot exemplars from the dev set
  rubrics/       standard rows per asset class (MBEI, NBI, corrosion CS, IEC 62446-3, FEMA PDA)
  prioritize.py  stage D: severity x criticality x consequence x urgency; S4 always first
  review.py      stage E: SQLite review log with prior model value
  export.py      queue CSV, findings JSON, bridge entry CSV (element, CS, quantity)
  pipeline.py    run_cascade(): resumable loop with live progress, shared by CLI, surge and UI
  surge.py       FR-20: FEMA triage over a folder, counts per class, U count, ranked list
  run.py         CLI
app/streamlit_app.py   FR-21 demo UI
eval/                  build_eval.py (freeze), run_eval.py (metrics + CIs), rubrics/, reports/
tests/                 unit and pipeline tests with fake backends
```

## Outputs per run (`runs/<id>/`)

| File | Content |
|---|---|
| `gate.jsonl` | one row per image: usable, damage_present, confidence, reason, routed, seconds |
| `findings.jsonl` / `findings.json` | finding contract rows; JSON is ranked |
| `queue.csv` | ranked work queue (columns in `export.QUEUE_COLUMNS`) |
| `bridge_entry.csv` | element, condition state, quantity columns for SNBI-style entry |
| `calls.jsonl` | tokens, dollars and seconds per model call |
| `summary.json` | counts, levels, routing fraction, cost per image |
| `reviews.sqlite` | reviewer decisions with prior model value |
| `surge_counts.json`, `surge_report.md` | surge mode only |

## Honesty rules

Every number in the deck is labelled Sourced, Team-measured, Inference or Assumption
(`docs/decisions.md` D-011). Accuracy claims come only from `eval/reports/` on the frozen
`eval_v1` set with n and confidence intervals. One image proves plumbing, not accuracy.
