"""FR-21 demo UI for the inspection grading cascade.

Top-level tabs: Inspect run (dataset or upload, live counters, image grid, findings with evidence,
review, queue, surge, export) · Drop & grade (drag-and-drop inference) · Batch (several datasets in
one go) · Reports (stored per-run reports, compared visually) · Eval matrix (gate 2x2 and grading
confusion matrices against dataset labels) · Why this approach (sourced comparison with the
incumbents plus the numbers measured on the active run).

Run:  streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import altair as alt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from cascade.evalmetrics import eval_matrix  # noqa: E402
from cascade.exemplars import exemplar_provider  # noqa: E402
from cascade.export import finding_row  # noqa: E402
from cascade.ingest import ingest_folder, read_manifest, write_manifest  # noqa: E402
from cascade.pipeline import LEVELS, Progress, RunConfig, load_run, run_cascade, save_findings  # noqa: E402
from cascade.prioritize import SEVERITY_WEIGHT, consequence_for, urgency_for  # noqa: E402
from cascade.report import REPORT_FIELDS, run_metrics, write_run_report  # noqa: E402
from cascade.review import ReviewLog  # noqa: E402
from cascade.schema import Finding, ImageRecord  # noqa: E402
from cascade.surge import surge_counts, write_surge_report  # noqa: E402

RUNS = ROOT / "runs"
DEV_MANIFEST = ROOT / "data" / "dev" / "manifest.jsonl"
EVAL_MANIFEST = ROOT / "data" / "eval_v1" / "manifest.jsonl"
DEMO_DIR = ROOT / "data" / "demo"
DATASET_LABELS = {
    "mixed": "Mixed sample: all four asset classes",
    "corrosion_cs": "Steel coating: corrosion condition state (bridge steel)",
    "dacl10k": "Bridge elements: concrete defects (dacl10k)",
    "ir_solar": "PV thermal modules (InfraredSolarModules)",
    "rescuenet": "Post-disaster UAV (RescueNet), surge mode",
}
ASSET_CLASSES = ["bridge_element", "steel_coating", "pv_module", "building_disaster"]
ASSET_LABEL = {"bridge_element": "Bridge element (concrete)", "steel_coating": "Steel coating (corrosion)", "pv_module": "PV module (thermal)", "building_disaster": "Building (post-disaster)"}
ASSET_ICON = {"bridge_element": "\U0001F309", "steel_coating": "\U0001F529", "pv_module": "\u2600\ufe0f", "building_disaster": "\U0001F3DA\ufe0f"}
CSS = """
<style>
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@keyframes pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(220,38,38,.55); } 50% { box-shadow: 0 0 0 7px rgba(220,38,38,0); } }
div[data-testid="stImage"] { animation: fadeUp .45s ease both; }
div[data-testid="stImage"] img { border-radius: 10px; transition: transform .18s ease, box-shadow .18s ease; }
div[data-testid="stImage"] img:hover { transform: scale(1.03); box-shadow: 0 8px 24px rgba(0,0,0,.35); }
div[data-testid="stMetric"] { animation: fadeUp .4s ease both; border-radius: 10px; padding: 6px 10px; background: rgba(127,127,127,.07); }
.badge { display:inline-block; color:white; padding:1px 8px; border-radius:9px; font-weight:600; letter-spacing:.2px; transition: transform .15s ease; }
.badge:hover { transform: translateY(-1px); }
.badge-S4 { animation: pulse 1.6s ease-out infinite; }
.chip { display:inline-block; padding:2px 10px; margin:2px 4px 2px 0; border-radius:999px; background: rgba(59,130,246,.15); border:1px solid rgba(59,130,246,.35); font-size: .85em; }
button[kind="primary"] { transition: transform .12s ease, filter .12s ease; }
button[kind="primary"]:hover { transform: translateY(-1px); filter: brightness(1.08); }
div[data-testid="stMarkdownContainer"] table { animation: fadeUp .4s ease both; }
</style>
"""
LEVEL_COLOR = {"S0": "#7a7a7a", "S1": "#3b82f6", "S2": "#f59e0b", "S3": "#f97316", "S4": "#dc2626", "U": "#8b5cf6"}
LEVEL_MEANING = {
    "S0": "no defect found in the graded region",
    "S1": "minor; monitor at the next routine cycle",
    "S2": "moderate; schedule within the SLA",
    "S3": "severe; prioritize this cycle",
    "S4": "critical; same-day escalation, top of queue",
    "U": "unassessable: refusal, missing metadata or unusable image; never counted as S0",
}

st.set_page_config(page_title="Inspection grading cascade", layout="wide", page_icon="\U0001F50D")
st.markdown(CSS, unsafe_allow_html=True)


# ---------- helpers ----------


def list_manifests() -> dict:
    """label -> manifest path. Demo manifests first, then the dev set."""
    out = {}
    if DEMO_DIR.exists():
        for p in sorted(DEMO_DIR.glob("*/manifest.jsonl"), key=lambda q: (q.parent.name != "mixed", q.parent.name)):
            out[f"demo: {DATASET_LABELS.get(p.parent.name, p.parent.name)}"] = p
    if DEV_MANIFEST.exists():
        out["dev set (all four datasets, 50 images)"] = DEV_MANIFEST
    return out


def records_for(manifest: Path, dataset_filter, limit: int):
    recs = read_manifest(manifest)
    if dataset_filter:
        recs = [r for r in recs if r.source_dataset == dataset_filter]
    return recs[:limit] if limit else recs


def list_runs() -> list:
    if not RUNS.exists():
        return []
    return sorted([p.name for p in RUNS.iterdir() if p.is_dir() and not p.name.startswith("_") and (p / "gate.jsonl").exists()], reverse=True)


def draw_evidence(f: Finding, rec: ImageRecord) -> Image.Image:
    img = Image.open(rec.path).convert("RGB")
    if f.evidence.bbox and f.evidence.tile != "full":
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = f.evidence.bbox
        d.rectangle([x0, y0, x1, y1], outline=LEVEL_COLOR.get(f.unified.level, "#ffffff"), width=max(3, img.width // 300))
    if max(img.size) < 320:  # 24x40 thermal crops
        s = 320 / max(img.size)
        img = img.resize((int(img.width * s), int(img.height * s)), Image.NEAREST)
    return img


@st.cache_data(show_spinner=False)
def thumbnail(path: str, mtime: float, size: int = 320) -> Optional[Image.Image]:
    p = Path(path)
    if not p.exists():
        return None
    img = Image.open(p).convert("RGB")
    if max(img.size) < 160:
        s = 160 / max(img.size)
        img = img.resize((int(img.width * s), int(img.height * s)), Image.NEAREST)
    img.thumbnail((size, size))
    return img


def badge(level: str, text: str = "") -> str:
    color = LEVEL_COLOR.get(level, "#555")
    return f"<span class='badge badge-{level}' style='background:{color}'>{level}</span> {text}"


def gallery(records: List[ImageRecord], captions: Optional[Dict[str, str]] = None, levels: Optional[Dict[str, str]] = None, cols: int = 5, max_n: int = 30, key: str = "g"):
    """Thumbnail grid. `captions` and `levels` are keyed by image_id; a level renders as a colored badge."""
    if not records:
        st.info("No images.")
        return
    shown = records[:max_n]
    for start in range(0, len(shown), cols):
        row = st.columns(cols)
        for col, rec in zip(row, shown[start : start + cols]):
            with col:
                p = Path(rec.path)
                th = thumbnail(str(p), p.stat().st_mtime if p.exists() else 0.0)
                if th is None:
                    st.warning(f"{rec.image_id}: file missing")
                    continue
                st.image(th, width="stretch")
                lvl = (levels or {}).get(rec.image_id)
                cap = (captions or {}).get(rec.image_id, "")
                st.markdown((badge(lvl, "") if lvl else "") + f"<small>`{rec.image_id}`<br>{cap}</small>", unsafe_allow_html=True)
    if len(records) > max_n:
        st.caption(f"Showing {max_n} of {len(records)} images.")


def worst_levels(findings: List[Finding]) -> Dict[str, str]:
    order = {lvl: i for i, lvl in enumerate(["S0", "S1", "S2", "S3", "S4", "U"])}
    out: Dict[str, str] = {}
    for f in findings:
        for iid in f.evidence.image_ids:
            cur = out.get(iid)
            if cur is None or (f.unified.level != "U" and (cur == "U" or order[f.unified.level] > order[cur])):
                out[iid] = f.unified.level
    return out


def multipliers(f: Finding, rec) -> dict:
    return {
        "severity_weight": SEVERITY_WEIGHT.get(f.unified.level),
        "criticality": 1.0,
        "consequence": consequence_for(f),
        "urgency": urgency_for(rec.captured_on if rec else None, date.today()),
    }


def render_counters(box, p: Progress, cfg: RunConfig):
    with box.container():
        c = st.columns(7)
        c[0].metric("Images", p.images)
        c[1].metric("Gated", p.gated, help="stage A ran on this many images")
        c[2].metric("Routed", p.routed, help="sent to the heavy grader: damage, unusable, low-confidence clean, or forced asset class")
        c[3].metric("Graded", p.graded)
        c[4].metric("Findings", p.findings)
        c[5].metric("Cost USD", f"{p.usd:.3f}", help="API list price from the call log; local models cost $0")
        c[6].metric("Model seconds", f"{p.seconds_gate + p.seconds_grade:.0f}", help=f"gate {p.seconds_gate:.0f} s, grade {p.seconds_grade:.0f} s")
        st.caption(
            f"stage **{p.stage}** · image `{p.current_image}` · gate={cfg.gate} grader={cfg.grader} tiles={cfg.tiles} · levels: "
            + "  ".join(f"{k} {v}" for k, v in p.levels.items())
        )


def findings_df(findings) -> pd.DataFrame:
    cols = ["queue_rank", "queue_score", "image_id", "unified_level", "native_value", "standard", "defect_type", "action_code", "sla_days", "confidence", "flags", "review_status", "finding_id"]
    rows = [finding_row(f) for f in findings]
    return pd.DataFrame(rows)[cols] if rows else pd.DataFrame(columns=cols)


def load_records_for_run(out: Path) -> dict:
    """image_id -> ImageRecord from the run's own manifest, else the dev and eval manifests."""
    recs = []
    for mp in [out / "manifest.jsonl", DEV_MANIFEST, EVAL_MANIFEST]:
        if mp.exists():
            recs += read_manifest(mp)
    return {r.image_id: r for r in recs}


def levels_chart(df: pd.DataFrame, x: str) -> alt.Chart:
    long = df.melt(id_vars=[x], value_vars=list(LEVELS), var_name="level", value_name="count")
    return (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=alt.X(f"{x}:N", title=None),
            y=alt.Y("count:Q", title="findings"),
            color=alt.Color("level:N", scale=alt.Scale(domain=list(LEVEL_COLOR), range=list(LEVEL_COLOR.values())), sort=list(LEVELS)),
            order=alt.Order("level:N"),
            tooltip=[x, "level", "count"],
        )
        .properties(height=260)
    )


def confusion_chart(labels: List[str], matrix: List[List[int]], title: str) -> alt.Chart:
    rows = [{"truth": t, "predicted": p, "count": matrix[i][j]} for i, t in enumerate(labels) for j, p in enumerate(labels)]
    df = pd.DataFrame(rows)
    base = alt.Chart(df).encode(
        x=alt.X("predicted:N", sort=labels, title="predicted (worst finding per image)"),
        y=alt.Y("truth:N", sort=labels, title="dataset truth"),
    )
    heat = base.mark_rect().encode(color=alt.Color("count:Q", scale=alt.Scale(scheme="blues"), legend=None), tooltip=["truth", "predicted", "count"])
    text = base.mark_text(fontSize=18, fontWeight="bold").encode(text="count:Q", color=alt.condition("datum.count > 0", alt.value("black"), alt.value("#999")))
    return (heat + text).properties(title=title, height=max(240, 70 * len(labels) + 80), width=max(300, 90 * len(labels) + 120))


def run_with_progress(records: List[ImageRecord], out: Path, cfg: RunConfig, use_exemplars: bool, surge: bool) -> Optional[dict]:
    """Run the cascade with live counters in the current container. Returns the summary or None on error."""
    out.mkdir(parents=True, exist_ok=True)
    write_manifest(records, out / "manifest.jsonl")
    counters = st.empty()
    bar = st.progress(0.0, text="starting")
    log_box = st.empty()
    lines: List[str] = []
    n_total = max(1, len(records))

    def on_progress(p: Progress):
        render_counters(counters, p, cfg)
        done = min(n_total, p.gated if p.stage == "gate" else max(p.gated, p.graded))
        bar.progress(min(0.99, done / n_total), text=f"{p.stage} - {p.current_image} - {done}/{n_total} images - ${p.usd:.3f}")
        entry = f"{p.current_image} -> {p.stage}"
        if p.current_image and (not lines or lines[-1] != entry):
            lines.append(entry)
            log_box.code("\n".join(lines[-12:]))

    provider = exemplar_provider(DEV_MANIFEST, k=3) if use_exemplars and DEV_MANIFEST.exists() else None
    with st.spinner("Running. A cold local gate can take a minute; each heavy grade is 10 to 40 s."):
        try:
            summary = run_cascade(records, out, cfg, exemplars=provider, progress=on_progress)
            if surge:
                write_surge_report(surge_counts(load_run(out)["findings"]), summary, out)
            write_run_report(out, {r.image_id: r for r in records})
            bar.progress(1.0, text="done")
            st.toast(f"Run {out.name} finished: {summary['findings']} findings", icon="\u2705")
            st.success(f"Done: {summary['findings']} findings from {summary['images']} images, ${summary['usd_total']} total, routed {summary['routed_to_grader']} of {summary['gated']}. Report stored in runs/{out.name}/report.md.")
            return summary
        except Exception as e:  # partial outputs stay on disk; the run is resumable
            st.toast(f"Run {out.name} stopped", icon="\u26a0\ufe0f")
            st.error(f"Run stopped: {type(e).__name__}: {e}. Outputs so far are in runs/{out.name}; press Run again with the same name to resume.")
            return None


def gate_caption(g: dict) -> str:
    verdict = "unusable" if not g["usable"] else ("damage" if g["damage_present"] else "clean")
    routing = "routed" if g["routed"] else "not routed"
    forced = " (forced)" if "[forced:" in g.get("reason", "") else ""
    return f"gate: {verdict} {g['confidence']:.2f} · {routing}{forced}"


# ---------- sidebar ----------

st.sidebar.title("Inspection grading cascade")
st.sidebar.caption("gate → crop → grade → prioritize → review → export")
mode = st.sidebar.radio("Mode", ["Inspect", "Surge (disaster)"], horizontal=True, help="Surge: building damage only, whole frame, FEMA PDA counts and a surge report")
surge = mode.startswith("Surge")
source = st.sidebar.radio("Images", ["Dataset", "Upload"], horizontal=True)

manifests = list_manifests()
records: List[ImageRecord] = []
if source == "Dataset":
    if not manifests:
        st.sidebar.error("No manifests found. Run `python scripts/make_demo_manifests.py` first.")
    choice = st.sidebar.selectbox("Dataset", list(manifests) or ["none"])
    dataset_filter = None
    if choice in manifests and manifests[choice] == DEV_MANIFEST:
        pick = st.sidebar.selectbox("Filter dev set", ["all"] + list(DATASET_LABELS), format_func=lambda k: "all" if k == "all" else DATASET_LABELS[k])
        dataset_filter = None if pick == "all" else pick
    limit = st.sidebar.slider("Max images", 1, 50, 12)
    if choice in manifests:
        records = records_for(manifests[choice], dataset_filter, limit)
        if surge:
            records = [r for r in records if r.asset_class == "building_disaster"]
else:
    asset_class = "building_disaster" if surge else st.sidebar.selectbox("Asset class", ASSET_CLASSES)
    files = st.sidebar.file_uploader("JPEG / PNG", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="sidebar_upload")
    if files:
        up = RUNS / "_uploads" / time.strftime("%Y%m%d_%H%M%S")
        up.mkdir(parents=True, exist_ok=True)
        for fobj in files:
            (up / fobj.name).write_bytes(fobj.getbuffer())
        records = ingest_folder(up, asset_class=asset_class, source_dataset="upload", split="upload", id_prefix="up")
        write_manifest(records, up / "manifest.jsonl")
        st.sidebar.success(f"{len(records)} images ingested; hash, size and EXIF date recorded, missing metadata stays null")
if records:
    st.sidebar.caption(f"{len(records)} images selected · " + ", ".join(f"{k} {v}" for k, v in pd.Series([r.asset_class for r in records]).value_counts().items()))

st.sidebar.divider()
gate = st.sidebar.selectbox("Gate (stage A)", ["local", "claude", "none"], help="local = Qwen3-VL-4B via Ollama; claude = Haiku 4.5; none = route everything")
grader = st.sidebar.selectbox("Grader (stage C)", ["claude", "local", "none"], help="claude = " + os.getenv("GRADER_MODEL", "claude-opus-5") + "; local = Qwen3-VL-8B via Ollama; none = gate only")
tiles = st.sidebar.checkbox("Tile large images (FR-8)", value=False, disabled=surge, help="one grader call per 1568 px tile; surge mode always grades the whole frame")
use_exemplars = st.sidebar.checkbox("Few-shot exemplars from dev set (FR-13)", value=False, disabled=not DEV_MANIFEST.exists())
gate_min_conf = st.sidebar.slider("Route clean verdicts below confidence", 0.0, 1.0, 0.7, 0.05)
force_pv = st.sidebar.checkbox("Always grade PV thermal crops (skip gate verdict)", value=True, help="the local gate routed 0 of 12 thermal crops on the dev set; the gate still runs and its verdict is logged")
run_name = st.sidebar.text_input("Run name", value=f"ui_{time.strftime('%m%d_%H%M')}")
reviewer = st.sidebar.text_input("Reviewer name (for the review log)", value=os.getenv("USERNAME", "reviewer"))
run_clicked = st.sidebar.button("Run cascade", type="primary", disabled=not records, width="stretch")

st.sidebar.divider()
open_run = st.sidebar.selectbox("Or open a finished run", ["(none)"] + list_runs())

cfg = RunConfig(gate=gate, grader=grader, tiles=tiles and not surge, gate_min_conf=gate_min_conf, force_route_classes=("pv_module",) if force_pv else ())
active_run = st.session_state.get("active_run")
if open_run != "(none)" and not run_clicked:
    active_run = open_run
    st.session_state["active_run"] = open_run

tab_run, tab_drop, tab_batch, tab_reports, tab_eval, tab_why = st.tabs(["Inspect run", "Drop & grade", "Batch", "Reports", "Eval matrix", "Why this approach"])

# ---------- Inspect run ----------

with tab_run:
    if run_clicked and records:
        st.session_state["active_run"] = run_name
        active_run = run_name
        run_with_progress(records, RUNS / run_name, cfg, use_exemplars, surge)

    if not active_run:
        st.title("Inspection grading cascade")
        st.markdown(
            """
Pick a dataset or upload images on the left, choose the gate and grader backends, and press **Run cascade**.
Or drop images straight into **Drop & grade**, run several datasets under **Batch**, and compare stored runs under **Reports**.

**What happens per image**

1. **Gate** (small VLM): usable? damage present? Confidence and a one-line reason. Recall-first routing.
2. **Crop**: large images tiled at 1,568 px with overlap; tile coordinates are kept as evidence.
3. **Grade** (heavy VLM, schema-enforced): native scale value with the rubric criterion quoted verbatim, unified S0 to S4, measurements or `not_measurable`, action and justification. Refusals become U, never S0.
4. **Prioritize**: score = severity × criticality × consequence × urgency; any S4 goes to the top with same-day escalation.
5. **Review**: accept, override or mark U; every action is logged with the prior model value.
6. **Export**: queue CSV, findings JSON, bridge entry CSV, and a stored report.

Numbers shown here are measured from each run's call log. Accuracy claims live only in `eval/reports/` and the **Eval matrix** tab.
"""
        )
        with st.expander("60-second demo script"):
            st.markdown(
                """
1. Open the **mixed sample** (four asset classes) and press **Run cascade**. Counters tick: gated, routed, graded, cost, seconds.
2. Click one finding: evidence crop, native grade with the rubric criterion quoted verbatim, unified level, confidence, action.
3. Open the **Work queue**: any S4 at the top with same-day escalation; multipliers visible per row.
4. **Override** one grade as a reviewer; the log shows prior value and reviewer; the queue re-ranks; the agreement timeline updates.
5. Same pipeline, different rubric: PV thermal gives IEC classes, RescueNet gives FEMA classes and U counts (**Surge counts**).
6. **Export** the queue CSV and the stored report. End on **Eval matrix**: gate recall and within-one-grade accuracy with n.
"""
            )
        if records:
            classes = pd.Series([r.asset_class for r in records]).value_counts()
            st.subheader(f"Selected images ({len(records)})")
            st.markdown(" ".join(f"<span class='chip'>{ASSET_ICON.get(k, '')} {ASSET_LABEL.get(k, k)} · {v}</span>" for k, v in classes.items()), unsafe_allow_html=True)
            if len(classes) > 1:
                for ac in ASSET_CLASSES:
                    group = [r for r in records if r.asset_class == ac]
                    if group:
                        st.markdown(f"**{ASSET_ICON.get(ac, '')} {ASSET_LABEL.get(ac, ac)}** · {len(group)}")
                        gallery(group, captions={r.image_id: f"{r.width}x{r.height} · {r.source_dataset}" for r in group}, cols=6, key=f"preview_{ac}")
            else:
                gallery(records, captions={r.image_id: f"{r.asset_class} · {r.width}x{r.height}" for r in records}, key="preview")
    else:
        out = RUNS / active_run
        run = load_run(out)
        findings = run["findings"]
        gate_rows, calls, summary = run["gate"], run["calls"], run["summary"]
        imgs = load_records_for_run(out)
        recs = list(imgs.values())
        review_log = ReviewLog(out / "reviews.sqlite")
        lvl_by_img = worst_levels(findings)

        st.title(f"Run `{active_run}`")
        sub_over, sub_find, sub_queue, sub_surge, sub_export = st.tabs(["Overview", "Findings & review", "Work queue", "Surge counts", "Export"])

        with sub_over:
            p = Progress(
                images=summary.get("images", len(gate_rows)),
                gated=len(gate_rows),
                routed=sum(1 for g in gate_rows if g["routed"]),
                unusable=sum(1 for g in gate_rows if not g["usable"]),
                graded=len({f.evidence.image_ids[0] for f in findings if f.evidence.image_ids}),
                findings=len(findings),
                usd=round(sum(c["usd"] for c in calls), 4),
                seconds_gate=round(sum(c["seconds"] for c in calls if c["stage"] == "gate"), 1),
                seconds_grade=round(sum(c["seconds"] for c in calls if c["stage"] == "grade"), 1),
                stage="done",
            )
            for f in findings:
                p.levels[f.unified.level] = p.levels.get(f.unified.level, 0) + 1
            shown_cfg = RunConfig(**summary["config"]) if summary.get("config") else cfg
            render_counters(st.empty(), p, shown_cfg)
            st.markdown("  ".join(badge(lvl, LEVEL_MEANING[lvl]) + " &nbsp;" for lvl in LEVELS), unsafe_allow_html=True)

            st.subheader("Images: gate verdict and worst grade")
            gate_by_id = {g["image_id"]: g for g in gate_rows}
            ordered = [imgs[g["image_id"]] for g in gate_rows if g["image_id"] in imgs]
            gallery(ordered, captions={i: gate_caption(g) for i, g in gate_by_id.items()}, levels=lvl_by_img, key="overview")

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Gate decisions")
                if gate_rows:
                    st.dataframe(pd.DataFrame(gate_rows)[["image_id", "usable", "damage_present", "confidence", "routed", "seconds", "reason"]], width="stretch", hide_index=True, height=320)
                else:
                    st.info("No gate rows yet.")
            with c2:
                st.subheader("Cost and latency per call")
                if calls:
                    cdf = pd.DataFrame(calls)
                    agg = cdf.groupby(["stage", "model"]).agg(calls=("usd", "size"), usd=("usd", "sum"), median_s=("seconds", "median"), in_tok=("input_tokens", "sum"), out_tok=("output_tokens", "sum")).reset_index()
                    st.dataframe(agg, width="stretch", hide_index=True)
                    st.caption(f"USD per image: {summary.get('usd_per_image')} · API list prices from src/cascade/costlog.py; local models are $0")
                else:
                    st.info("No calls logged.")
            if summary:
                with st.expander("summary.json"):
                    st.json(summary)

        with sub_find:
            if not findings:
                st.info("No findings. Either nothing was routed or the grader was set to none.")
            else:
                df = findings_df(findings)
                st.dataframe(df, width="stretch", hide_index=True, height=260)
                fid = st.selectbox("Finding", df["finding_id"].tolist(), key="finding_pick")
                f = next(x for x in findings if x.finding_id == fid)
                rec = imgs.get(f.evidence.image_ids[0]) if f.evidence.image_ids else None
                c1, c2 = st.columns([1.1, 1])
                with c1:
                    if rec and Path(rec.path).exists():
                        st.image(draw_evidence(f, rec), caption=f"{rec.image_id} · {rec.width}x{rec.height} · tile {f.evidence.tile} · bbox {f.evidence.bbox}", width="stretch")
                        truth = rec.labels.get("grade_native") or rec.labels.get("source_class")
                        if truth:
                            st.caption(f"Dataset label, for eval only and never shown to the model: **{truth}** ({rec.labels.get('grade_source')})")
                    else:
                        st.warning("Source image not on disk for this run.")
                with c2:
                    st.markdown(f"### {f.native_scale.value} on {f.native_scale.standard} · " + badge(f.unified.level, f.unified.uncertainty), unsafe_allow_html=True)
                    st.caption(LEVEL_MEANING[f.unified.level])
                    sla = f", within {f.action.sla_days} days" if f.action.sla_days is not None else ""
                    st.markdown(f"**Defect:** {f.defect_type}  \n**Action:** {f.action.code}{sla}  \n**Basis:** {f.action.basis}")
                    st.markdown("**Criteria matched (verbatim from rubric):**")
                    for c in f.native_scale.criteria_matched or ["(none quoted)"]:
                        st.markdown(f"> {c}")
                    st.markdown(f"**Justification:** {f.justification}")
                    m = f.measurements
                    st.markdown(
                        f"**Measurements:** area {m.area_cm2} cm², crack {m.crack_width_mm} mm, ΔT {m.delta_t_k} K, rust {m.percent_area_rusted} %, section loss {m.section_loss_pct} % · confidence **{m.confidence:.2f}** · flags: {', '.join(f.unified.flags) or 'none'}"
                    )
                    reviewed = f" by {f.review.reviewer} at {f.review.reviewed_at} (prior {f.review.prior_level})" if f.review.reviewer else ""
                    st.caption(f"model {f.model} · ${f.usd:.4f} · {f.seconds:.1f} s · review: {f.review.status}{reviewed}")
                    st.markdown("**Reviewer decision (FR-18)**")
                    b1, b2, b3 = st.columns(3)
                    gradable = [lvl for lvl in LEVELS if lvl != "U"]
                    new_level = b2.selectbox("Override to", gradable, index=gradable.index(f.unified.level) if f.unified.level in gradable else 0, label_visibility="collapsed", key="override_level")
                    action = None
                    if b1.button("Accept", width="stretch", key="btn_accept"):
                        action = ("accepted", None)
                    if b2.button("Override", width="stretch", key="btn_override"):
                        action = ("overridden", new_level)
                    if b3.button("Mark U", width="stretch", key="btn_u"):
                        action = ("marked_u", None)
                    if action:
                        review_log.apply(active_run, f, action[0], reviewer, action[1])
                        save_findings(findings, out, recs)
                        write_run_report(out, imgs)
                        st.toast(f"{action[0]} by {reviewer}, prior {f.review.prior_level}", icon="\U0001F4DD")
                        st.rerun()
                agg = review_log.agreement(active_run)
                rate = f", agreement {agg['agreement_rate']:.0%}" if agg["agreement_rate"] is not None else ""
                st.caption(f"Review log: {agg['total']} decisions, accepted {agg['accepted']}, overridden {agg['overridden']}, marked U {agg['marked_u']}{rate} · persisted in reviews.sqlite")
                tl = review_log.timeline(active_run)
                if tl:
                    st.markdown("**Model vs reviewer agreement over time (FR-19)**")
                    tdf = pd.DataFrame(tl)
                    line = alt.Chart(tdf).mark_line(point=True, interpolate="monotone").encode(
                        x=alt.X("n:Q", title="decision #"), y=alt.Y("agreement_rate:Q", title="running agreement", scale=alt.Scale(domain=[0, 1])),
                        tooltip=["n", "reviewed_at", "finding_id", "action", "prior_level", "new_level", "reviewer"],
                    ).properties(height=200)
                    st.altair_chart(line, width="stretch")

        with sub_queue:
            st.markdown("`score = severity_weight[S] × criticality × consequence × urgency`. Any **S4** sorts first and is escalated same day. **U** is listed, never scored as S0. Criticality is 1 unless supplied per asset.")
            if findings:
                rows = []
                ranked = sorted(findings, key=lambda x: x.queue_rank or 10**9)
                for f in ranked:
                    rec = imgs.get(f.evidence.image_ids[0]) if f.evidence.image_ids else None
                    rows.append(
                        {
                            "rank": f.queue_rank,
                            "score": f.queue_score,
                            "level": f.unified.level,
                            "native": f.native_scale.value,
                            "image": f.evidence.image_ids[0] if f.evidence.image_ids else "",
                            "asset_class": f.asset_class,
                            "action": f.action.code,
                            "sla_days": f.action.sla_days,
                            **multipliers(f, rec),
                            "flags": ";".join(f.unified.flags),
                            "review": f.review.status,
                        }
                    )
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=400)
                st.subheader("Top of the queue, visually")
                top = [imgs[f.evidence.image_ids[0]] for f in ranked[:10] if f.evidence.image_ids and f.evidence.image_ids[0] in imgs]
                caps = {f.evidence.image_ids[0]: f"#{f.queue_rank} · {f.native_scale.value} · {f.action.code}" for f in ranked[:10] if f.evidence.image_ids}
                gallery(top, captions=caps, levels=lvl_by_img, key="queue")
            else:
                st.info("Empty queue.")

        with sub_surge:
            dis = [f for f in findings if f.asset_class == "building_disaster"]
            if not dis:
                st.info("No building_disaster findings in this run. Choose the RescueNet demo set or Surge mode.")
            else:
                counts = surge_counts(dis)
                c1, c2, c3 = st.columns(3)
                c1.metric("Images assessed", counts["n_images"])
                c2.metric("Unassessable (U)", counts["u_count"])
                c3.metric("Mean confidence", f"{counts['mean_confidence']:.2f}" if counts["mean_confidence"] is not None else "n/a")
                cc1, cc2 = st.columns(2)
                cc1.bar_chart(pd.Series(counts["by_fema_class"], name="FEMA PDA class"))
                cc2.bar_chart(pd.Series(counts["by_level"], name="unified level"))
                st.dataframe(pd.DataFrame(counts["ranked"]), width="stretch", hide_index=True)
                rp = out / "surge_report.md"
                if rp.exists():
                    st.download_button("Download surge_report.md", rp.read_bytes(), file_name="surge_report.md", key="dl_surge")

        with sub_export:
            for name in ["report.md", "report.json", "queue.csv", "findings.json", "bridge_entry.csv", "gate.jsonl", "calls.jsonl", "summary.json", "surge_counts.json", "surge_report.md"]:
                fp = out / name
                if fp.exists():
                    st.download_button(f"Download {name}", fp.read_bytes(), file_name=f"{active_run}_{name}", key=f"dl_{name}")
            st.caption("queue.csv columns are documented in src/cascade/export.py (QUEUE_COLUMNS). bridge_entry.csv carries element, condition state and quantity columns for SNBI-style entry (FR-17). report.md is the stored run report shown under Reports.")

# ---------- Drop & grade ----------

with tab_drop:
    st.subheader("Drop images, get graded findings")
    st.caption("Drag files onto the box. They are hashed and ingested, then run through the cascade with the backends chosen in the sidebar. Each drop becomes its own stored run.")
    d1, d2 = st.columns([2, 1])
    drop_files = d1.file_uploader("Drop JPEG / PNG here", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="drop_upload")
    drop_class = d2.selectbox("Asset class", ASSET_CLASSES, index=ASSET_CLASSES.index("building_disaster") if surge else 0, key="drop_class")
    d2.markdown(f"Backends: gate `{gate}`, grader `{grader}`" + (", surge posture" if surge else ""))
    go = d2.button("Grade dropped images", type="primary", disabled=not drop_files, key="drop_go", width="stretch")
    if go and drop_files:
        name = f"drop_{time.strftime('%m%d_%H%M%S')}"
        out = RUNS / name
        up = out / "uploads"
        up.mkdir(parents=True, exist_ok=True)
        for fobj in drop_files:
            (up / fobj.name).write_bytes(fobj.getbuffer())
        drop_recs = ingest_folder(up, asset_class=drop_class, source_dataset="upload", split="upload", id_prefix="drop")
        st.session_state["drop_run"] = name
        run_with_progress(drop_recs, out, cfg, use_exemplars, surge or drop_class == "building_disaster")
    drop_run = st.session_state.get("drop_run")
    if drop_run and (RUNS / drop_run / "gate.jsonl").exists():
        out = RUNS / drop_run
        run = load_run(out)
        imgs = load_records_for_run(out)
        by_img: Dict[str, List[Finding]] = {}
        for f in run["findings"]:
            for iid in f.evidence.image_ids:
                by_img.setdefault(iid, []).append(f)
        st.markdown(f"**Run `{drop_run}`** · {len(run['gate'])} images · {len(run['findings'])} findings · ${sum(c['usd'] for c in run['calls']):.3f}")
        for g in run["gate"]:
            rec = imgs.get(g["image_id"])
            if not rec:
                continue
            c1, c2 = st.columns([1, 2])
            fs = sorted(by_img.get(rec.image_id, []), key=lambda x: x.queue_rank or 10**9)
            with c1:
                st.image(draw_evidence(fs[0], rec) if fs else thumbnail(rec.path, Path(rec.path).stat().st_mtime), width="stretch")
            with c2:
                st.markdown(f"**{rec.image_id}** · {gate_caption(g)}")
                st.caption(f"gate reason: {g['reason']}")
                if not fs:
                    st.write("Not graded (gate said clean, or grader set to none).")
                for f in fs:
                    st.markdown(badge(f.unified.level, f"**{f.native_scale.value}** on {f.native_scale.standard} · {f.defect_type} · action {f.action.code}" + (f" within {f.action.sla_days} d" if f.action.sla_days is not None else "")), unsafe_allow_html=True)
                    st.markdown(f"<small>{f.justification}</small>", unsafe_allow_html=True)
            st.divider()
        st.caption("Open this run under Inspect run (sidebar: open a finished run) to review, re-rank and export.")

# ---------- Batch ----------

with tab_batch:
    st.subheader("Batch: several datasets in one go")
    st.caption("Each selected dataset becomes its own run (resumable, stored, reported). Runs execute one after another with live counters; compare them under Reports afterwards.")
    b1, b2 = st.columns([2, 1])
    picks = b1.multiselect("Datasets", list(manifests), default=[], key="batch_picks")
    per = b2.slider("Max images per dataset", 1, 50, 10, key="batch_limit")
    prefix = b2.text_input("Run name prefix", value=f"batch_{time.strftime('%m%d_%H%M')}", key="batch_prefix")
    est_imgs = sum(len(records_for(manifests[k], None, per)) for k in picks) if picks else 0
    b2.markdown(f"About **{est_imgs}** images · gate `{gate}`, grader `{grader}`")
    if b1.button("Run batch", type="primary", disabled=not picks, key="batch_go"):
        status = st.empty()
        rows = []
        for k in picks:
            recs_k = records_for(manifests[k], None, per)
            slug = manifests[k].parent.name if manifests[k] != DEV_MANIFEST else "dev"
            name = f"{prefix}_{slug}"
            rows.append({"run": name, "dataset": k, "images": len(recs_k), "status": "running"})
            status.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            with st.expander(f"{name} ({len(recs_k)} images)", expanded=True):
                summ = run_with_progress(recs_k, RUNS / name, cfg, use_exemplars, surge)
            rows[-1]["status"] = "done" if summ else "stopped"
            if summ:
                rows[-1].update(findings=summ["findings"], usd=summ["usd_total"], routed=summ["routed_to_grader"])
            status.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        st.session_state["batch_runs"] = [r["run"] for r in rows]
        st.success("Batch finished. See Reports for the comparison.")
    if st.session_state.get("batch_runs"):
        st.markdown("Last batch: " + ", ".join(f"`{r}`" for r in st.session_state["batch_runs"]))

# ---------- Reports ----------

with tab_reports:
    st.subheader("Stored run reports")
    all_runs = list_runs()
    if not all_runs:
        st.info("No runs yet.")
    else:
        metrics = []
        for r in all_runs:
            try:
                metrics.append(run_metrics(RUNS / r))
            except Exception as e:  # a half-written run must not break the page
                metrics.append({"run": r, "error": f"{type(e).__name__}: {e}"})
        mdf = pd.DataFrame(metrics)
        show_cols = [c for c in ["run", "mode", "gate", "grader", "images", "routed", "findings", *LEVELS, "usd_total", "usd_per_image", "seconds_gate", "seconds_grade", "reviews"] if c in mdf.columns]
        st.table(mdf[show_cols].set_index("run"))
        default = st.session_state.get("batch_runs") or ([active_run] if active_run else all_runs[:3])
        compare = st.multiselect("Compare runs", all_runs, default=[r for r in default if r in all_runs], key="cmp_runs")
        if compare and all(lvl in mdf.columns for lvl in LEVELS):
            sub = mdf[mdf["run"].isin(compare)].fillna(0)
            c1, c2 = st.columns(2)
            c1.altair_chart(levels_chart(sub[["run"] + list(LEVELS)], "run"), width="stretch")
            cost = sub[["run", "usd_per_image", "seconds_gate", "seconds_grade", "images"]].copy()
            cost["seconds_per_image"] = (cost["seconds_gate"] + cost["seconds_grade"]) / cost["images"].replace(0, pd.NA)
            cost = cost.astype({"usd_per_image": float, "seconds_per_image": float})
            with c2:
                k1, k2 = st.columns(2)
                for col, (metric, title) in zip((k1, k2), (("usd_per_image", "USD per image"), ("seconds_per_image", "model seconds per image"))):
                    col.altair_chart(
                        alt.Chart(cost).mark_bar(color="#3b82f6").encode(x=alt.X("run:N", title=None), y=alt.Y(f"{metric}:Q", title=title), tooltip=["run", metric]).properties(height=240),
                        width="stretch",
                    )
        st.divider()
        pick = st.selectbox("Open a report", all_runs, index=all_runs.index(active_run) if active_run in all_runs else 0, key="report_pick")
        rp = RUNS / pick / "report.md"
        cA, cB = st.columns([1, 3])
        if cA.button("Generate / refresh report.md", key="report_gen"):
            write_run_report(RUNS / pick, load_records_for_run(RUNS / pick))
            st.rerun()
        if rp.exists():
            cB.download_button("Download report.md", rp.read_bytes(), file_name=f"{pick}_report.md", key="report_dl")
            st.markdown(rp.read_text(encoding="utf-8"))
            rr = load_run(RUNS / pick)
            ranked = sorted(rr["findings"], key=lambda x: x.queue_rank or 10**9)[:10]
            imgs_r = load_records_for_run(RUNS / pick)
            top = [imgs_r[f.evidence.image_ids[0]] for f in ranked if f.evidence.image_ids and f.evidence.image_ids[0] in imgs_r]
            if top:
                st.markdown("**Top findings, visually**")
                gallery(top, captions={f.evidence.image_ids[0]: f"#{f.queue_rank} · {f.native_scale.value} · {f.action.code}" for f in ranked if f.evidence.image_ids}, levels=worst_levels(rr["findings"]), key="report_gallery")
        else:
            st.info("No report stored for this run yet. Press Generate.")

# ---------- Eval matrix ----------

with tab_eval:
    st.subheader("Eval matrix: gate and grading against dataset labels")
    st.caption("Truth comes from the datasets' own labels and the class-to-severity maps frozen before any model output (D-007). Images without a label are listed, not guessed. Confidence intervals are in eval/reports/; this tab shows counts.")
    all_runs = list_runs()
    if not all_runs:
        st.info("No runs yet.")
    else:
        pick = st.selectbox("Run", all_runs, index=all_runs.index(active_run) if active_run in all_runs else 0, key="eval_pick")
        rr = load_run(RUNS / pick)
        imgs_e = load_records_for_run(RUNS / pick)
        em = eval_matrix(imgs_e, rr["gate"], [f.model_dump() for f in rr["findings"]])
        g = em["gate"]
        st.markdown("#### Gate (stage A): damage present vs routed")
        if g["n"] == 0:
            st.info("No image in this run carries a damage_present label (uploads never do).")
        else:
            c1, c2, c3 = st.columns([1, 1, 2])
            c1.metric("Recall (headline)", f"{100 * g['recall']:.1f}%" if g["recall"] is not None else "n/a", help="damaged images that were routed; recall-first by design")
            c1.metric("Precision", f"{100 * g['precision']:.1f}%" if g["precision"] is not None else "n/a")
            c2.altair_chart(confusion_chart(["clean", "damaged"], [[g["tn"], g["fp"]], [g["fn"], g["tp"]]], f"gate, n={g['n']}"), width="content")
            if em["per_dataset"]:
                pdf = pd.DataFrame([{"dataset": ds, **d} for ds, d in em["per_dataset"].items()])
                c3.dataframe(pdf[["dataset", "n", "tp", "fp", "fn", "tn", "recall", "precision"]], width="stretch", hide_index=True)
            if g["misses"]:
                st.markdown("**Missed damaged images** (routed = no):")
                gallery([imgs_e[i] for i in g["misses"] if i in imgs_e], captions={i: "missed by gate" for i in g["misses"]}, key="eval_misses", max_n=10)
        sc1, sc2 = st.columns([1, 3])
        if sc1.button("Score with bootstrap CIs", key="eval_score", help="runs eval/run_eval.py on this run's manifest; writes eval/reports/<run>.md and .json, no model calls"):
            mp = RUNS / pick / "manifest.jsonl"
            if not mp.exists():
                mp = DEV_MANIFEST
            with st.spinner("bootstrapping 1000 resamples"):
                proc = subprocess.run([sys.executable, str(ROOT / "eval" / "run_eval.py"), "--manifest", str(mp), "--run", str(RUNS / pick), "--name", pick], capture_output=True, text=True, cwd=str(ROOT))
            if proc.returncode == 0:
                st.toast(f"eval/reports/{pick}.md written", icon="\U0001F4CA")
                st.rerun()
            else:
                st.error(proc.stderr[-1500:] or proc.stdout[-1500:])
        sc2.caption("The scored report carries n and 95% bootstrap CIs per metric; the matrices below are raw counts.")
        st.markdown("#### Grading (stage C): worst finding per image vs truth")
        if not em["grading"]:
            st.info("No routed image with a grade label in this run. Use a demo or dev dataset with the grader on.")
        for ac, gr in em["grading"].items():
            st.markdown(f"**{ac}** · truth: {gr['truth_source']}")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.altair_chart(confusion_chart(gr["labels"], gr["matrix"], f"{ac}: n assessed {gr['n_assessed']} of {gr['n_routed_with_truth']}"), width="content")
            with c2:
                if gr["n_assessed"]:
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Exact match", f"{100 * gr['exact_match']:.0f}%")
                    m2.metric("Within one grade", f"{100 * gr['within_one_grade']:.0f}%", help="the PRD's headline grading metric; FHWA found 68% of human ratings within one point")
                    m3.metric("Weighted kappa", f"{gr['qwk']:.2f}")
                    m1.metric("MAE (grades)", f"{gr['mae']:.2f}")
                    m2.metric("Over-graded", gr["over_graded"])
                    m3.metric("Under-graded", gr["under_graded"], help="under-grading is the costly direction for safety")
                st.metric("U rate", f"{100 * gr['u_rate']:.0f}%" if gr["u_rate"] is not None else "n/a", help="routed images with truth that produced no gradable finding")
                if gr["pairs"]:
                    with st.expander("Per-image truth vs predicted"):
                        st.dataframe(pd.DataFrame(gr["pairs"]), width="stretch", hide_index=True)
                if gr["u_images"]:
                    st.caption("U images: " + ", ".join(gr["u_images"][:20]))
        st.divider()
        st.markdown("#### Scored eval reports (eval/reports)")
        reports = sorted((ROOT / "eval" / "reports").glob("*.md"), key=lambda q: q.stat().st_mtime, reverse=True)
        if not reports:
            st.info("No scored report yet. Press Score with bootstrap CIs above, or run eval/run_eval.py.")
        else:
            rp = st.selectbox("Report", reports, format_func=lambda q: q.name, index=next((i for i, q in enumerate(reports) if q.stem == pick), 0), key="eval_report_pick")
            st.markdown(rp.read_text(encoding="utf-8"))

# ---------- Why this approach ----------

with tab_why:
    st.subheader("How this differs from the incumbents")
    st.caption("Incumbent facts are from the team's web research of 2026-09-24 (docs/research/R01, R02, R06, R08, R09). No head-to-head benchmark has been run; the right-hand column is measured from the run selected in the sidebar, or blank.")
    live = run_metrics(RUNS / active_run, load_records_for_run(RUNS / active_run)) if active_run and (RUNS / active_run / "gate.jsonl").exists() else None

    def measured(fn, default="not measured yet"):
        try:
            return fn() if live else default
        except Exception:
            return default

    rows = [
        ("Asset coverage", "Single-vertical: SkySpecs, Clobotics, Cornis on blades; Raptor Maps, Sitemark, Above on solar; Buzz, Sharper Shape, Hepta on grid (R01, R02)",
         "One engine, four asset classes: bridge steel coating, bridge concrete elements, PV thermal modules, post-disaster buildings; rubrics are data, not code",
         measured(lambda: ", ".join(live["asset_classes"]) or "none graded")),
        ("Grading vocabulary", "\"Severity ratings\" with no published definitions; none ships MBEI condition states with clauses (R01, R02)",
         "Native scale first (MBEI CS1 to CS4, IEC TS 62446-3 CoA, FEMA PDA), the rubric row quoted verbatim in every finding, unified S0 to S4 overlay",
         measured(lambda: f"{live['findings']} findings, each with quoted criteria")),
        ("Rationale per finding", "No per-finding rationale published by any incumbent (R01, R02, R09)",
         "Justification, measurements or not_measurable, confidence, +/-1 uncertainty, evidence crop with bbox",
         measured(lambda: f"{live['graded_images']} images with evidence crops")),
        ("Unassessable state", "Not exposed; a refusal or bad image silently becomes 'no finding'",
         "Explicit U: refusals, missing GSD and unusable frames are U, never S0, and are listed in the queue",
         measured(lambda: f"U = {live['U']} of {live['findings']}")),
        ("Hallucination control", "Zero-shot VLM grading: 65% hallucination in the 2026 hybrid study; frontier VLMs weak at small defects (R02, R06)",
         "Cascade: cheap gate, crop, then schema-enforced grade constrained to rubric values; hybrid pipelines reached 4% in the same study",
         measured(lambda: f"routed {live['routed']} of {live['gated']} ({100 * live['routed'] / max(1, live['gated']):.0f}%)")),
        ("Prioritization", "Findings framed in AEP or dollars inside one vertical; no cross-asset consequence-ranked queue found (R01, R02)",
         "Deterministic queue: severity × criticality × consequence × urgency; any S4 same-day; multipliers shown per row",
         measured(lambda: f"S4 = {live['S4']}, S3 = {live['S3']}")),
        ("Human sign-off", "Not published",
         "Mandatory accept / override / mark U with the prior model value logged; agreement rate measured per run",
         measured(lambda: f"{live['reviews']} reviewer decisions logged")),
        ("Unit cost", "Quote-only pricing except Scopito (EUR 160 / 80 per turbine); $100 to $300 analytics add-on per turbine (R01, R04, R09)",
         "About $10 per 1,000 frames heavy-only, about $3 with a local gate at 30% pass-through (R06 estimate, Sonnet 5 Sept 2026 prices)",
         measured(lambda: f"${live['usd_per_image']:.4f} per image = ${1000 * live['usd_per_image']:.2f} per 1,000" if live["usd_per_image"] is not None else "no priced calls")),
        ("Compliance output", "RFPs require state-system entry by deadline, CS3/CS4 photo documentation, a per-structure list; one county fines $100 per day late (R08)",
         "bridge_entry.csv (element, condition state, quantity) and queue.csv per run; evidence crops per finding",
         measured(lambda: "bridge_entry.csv written" if (RUNS / active_run / "bridge_entry.csv").exists() else "no bridge findings in this run")),
        ("Disaster surge", "Insurers deliver building-level classes in 24 to 48 h (ICEYE, Nearmap, Vexcel); nobody grades engineered infrastructure post-event (R03)",
         "Surge posture on the same engine: whole-frame FEMA PDA counts and a report; infrastructure surge is roadmap, not demo",
         measured(lambda: "surge run" if live["mode"] == "surge" else "inspect run")),
        ("Consistency baseline", "Human inspectors: 68% of ratings within one point across 49 inspectors (FHWA); 30% matched expected (Indiana 2026) (R08)",
         "Within-one-grade and weighted kappa reported per asset class with n and CI, against frozen label maps",
         measured(lambda: "; ".join(f"{ac}: within-1 {100 * gr['within_one_grade']:.0f}% (n={gr['n_assessed']})" for ac, gr in live.get("eval", {}).get("grading", {}).items() if gr["n_assessed"]) or "no labelled grades in this run")),
    ]
    head = ["Capability", "Incumbents (as researched)", "This cascade", f"Measured on `{active_run}`" if active_run else "Measured (no run open)"]
    table = ["| " + " | ".join(head) + " |", "|---|---|---|---|"]
    table += ["| **" + r[0] + "** | " + " | ".join(str(x).replace("|", "/") for x in r[1:]) + " |" for r in rows]
    st.markdown(chr(10).join(table))
    st.markdown(
        """
**What is deliberately not claimed.** No field accuracy: all numbers come from public datasets. No trained model: the business is rubrics,
evaluation and workflow (R07). No comparison benchmark against any named vendor exists yet. The R06 cost figures are estimates from
list prices; the measured column is the only number from this codebase.
"""
    )
