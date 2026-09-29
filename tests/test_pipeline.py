"""End-to-end pipeline tests with fake gate and grader backends (no model, no network)."""

import json

import pytest
from PIL import Image

from cascade.costlog import CallLog
from cascade.pipeline import RunConfig, load_run, run_cascade, save_findings
from cascade.review import ReviewLog
from cascade.schema import Action, Evidence, Finding, GateRecord, ImageRecord, Measurements, NativeScale, Unified


def make_records(tmp_path, n=4, size=(64, 48), asset_class="steel_coating"):
    recs = []
    for i in range(n):
        p = tmp_path / f"img_{i}.jpg"
        Image.new("RGB", size, (i * 40 % 255, 100, 100)).save(p)
        recs.append(ImageRecord(image_id=f"img_{i}", path=str(p), sha256="0" * 64, width=size[0], height=size[1], asset_class=asset_class, captured_on="2026-09-01", source_dataset="fake", split="dev"))
    return recs


def fake_gate(img, image_id, *, backend, log, no_damage_min_conf):
    # img_0 clean and confident (not routed); img_1 unusable; others damaged
    idx = int(image_id.split("_")[-1])
    if idx == 0:
        out = dict(usable=True, damage_present=False, confidence=0.95, reason="clean", routed=False)
    elif idx == 1:
        out = dict(usable=False, damage_present=False, confidence=0.3, reason="blur", routed=True)
    else:
        out = dict(usable=True, damage_present=True, confidence=0.9, reason="rust", routed=True)
    log.record(stage="gate", model="fake-gate", image_id=image_id, input_tokens=10, output_tokens=5, seconds=0.01)
    return GateRecord(image_id=image_id, model="fake-gate", seconds=0.01, usd=0.0, **out)


def fake_grade(img, *, finding_id, image_id, asset_class, backend, rubric, metadata, exemplars, evidence, log):
    idx = int(image_id.split("_")[-1])
    level = "S4" if idx == 3 else "S2"
    log.record(stage="grade", model="fake-grader", image_id=image_id, input_tokens=100, output_tokens=50, seconds=0.02)
    return Finding(
        finding_id=finding_id,
        asset_class=asset_class,
        defect_type="corrosion",
        native_scale=NativeScale(standard=rubric["standard"], value=rubric["allowed_values"][-1], criteria_matched=[rubric["rows"][0]["criterion"]]),
        unified=Unified(level=level, uncertainty="+/-1", flags=[]),
        measurements=Measurements(area_cm2=None, crack_width_mm=None, delta_t_k=None, percent_area_rusted=12.0, section_loss_pct=None, confidence=0.8),
        action=Action(code="schedule", sla_days=90, basis="row 1"),
        justification="Fake finding for tests.",
        evidence=evidence,
        model="fake-grader",
    )


def test_run_cascade_routes_grades_and_exports(tmp_path):
    recs = make_records(tmp_path)
    out = tmp_path / "run"
    snapshots = []
    summary = run_cascade(recs, out, RunConfig(gate="none", grader="claude"), progress=lambda p: snapshots.append(p.as_dict()), gate_fn=fake_gate, grade_fn=fake_grade)
    assert summary["images"] == 4
    assert summary["routed_to_grader"] == 3  # img_0 skipped
    assert summary["unusable"] == 1
    assert summary["findings"] == 3
    assert summary["levels"]["U"] == 1 and summary["levels"]["S4"] == 1 and summary["levels"]["S2"] == 1
    for name in ("gate.jsonl", "findings.jsonl", "findings.json", "queue.csv", "summary.json", "calls.jsonl"):
        assert (out / name).exists(), name
    assert snapshots[-1]["stage"] == "done"
    assert snapshots[-1]["findings"] == 3
    ranked = load_run(out)["findings"]
    assert ranked[0].unified.level == "S4" and ranked[0].queue_rank == 1 and ranked[0].action.code == "escalate"
    assert ranked[-1].unified.level == "U" and ranked[-1].queue_score is None


def test_run_is_resumable_and_skips_done_images(tmp_path):
    recs = make_records(tmp_path)
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    calls_before = len((out / "calls.jsonl").read_text().splitlines())

    def exploding_gate(*a, **k):
        raise AssertionError("gate must not be called again")

    def exploding_grade(*a, **k):
        raise AssertionError("grader must not be called again")

    summary = run_cascade(recs, out, RunConfig(gate="none"), gate_fn=exploding_gate, grade_fn=exploding_grade)
    assert summary["findings"] == 3
    assert len((out / "calls.jsonl").read_text().splitlines()) == calls_before


def test_grader_none_is_gate_only(tmp_path):
    recs = make_records(tmp_path)
    out = tmp_path / "run"
    summary = run_cascade(recs, out, RunConfig(gate="none", grader="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    assert summary["routed_to_grader"] == 3 and summary["findings"] == 0
    assert not any(json.loads(line)["stage"] == "grade" for line in (out / "calls.jsonl").read_text().splitlines())


def test_tiles_produce_one_finding_per_tile(tmp_path):
    recs = make_records(tmp_path, n=3, size=(2000, 1600))
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none", tiles=True), gate_fn=fake_gate, grade_fn=fake_grade)
    findings = load_run(out)["findings"]
    img2 = [f for f in findings if f.evidence.image_ids == ["img_2"]]
    assert len(img2) > 1
    assert all(f.evidence.tile.startswith("t") for f in img2)
    assert all(len(f.evidence.bbox) == 4 for f in img2)


def test_exemplars_exclude_self_and_are_cached(tmp_path):
    from cascade.grade import Exemplar

    recs = make_records(tmp_path)
    seen = []
    calls = []

    def provider(asset_class):
        calls.append(asset_class)
        return [Exemplar(image=Image.new("RGB", (8, 8)), native_value="Poor", image_id="img_2"), Exemplar(image=Image.new("RGB", (8, 8)), native_value="Fair", image_id="other")]

    def grade_capture(img, **kw):
        seen.append((kw["image_id"], [e.image_id for e in (kw["exemplars"] or [])]))
        return fake_grade(img, **kw)

    run_cascade(recs, tmp_path / "run", RunConfig(gate="none"), exemplars=provider, gate_fn=fake_gate, grade_fn=grade_capture)
    assert calls == ["steel_coating"]  # loaded once per asset class
    by_img = dict(seen)
    assert by_img["img_2"] == ["other"]
    assert by_img["img_3"] == ["img_2", "other"]


def test_review_then_save_findings_reranks_and_persists(tmp_path):
    recs = make_records(tmp_path)
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    findings = load_run(out)["findings"]
    top = findings[0]
    assert top.unified.level == "S4"
    log = ReviewLog(out / "reviews.sqlite")
    log.apply("run", top, "overridden", "alice", "S1")
    ranked = save_findings(findings, out, recs)
    assert ranked[0].finding_id != top.finding_id
    reloaded = load_run(out)["findings"]
    changed = next(f for f in reloaded if f.finding_id == top.finding_id)
    assert changed.unified.level == "S1" and changed.review.prior_level == "S4" and changed.review.reviewer == "alice"
    assert ReviewLog(out / "reviews.sqlite").agreement("run")["overridden"] == 1


def test_bridge_csv_written_for_bridge_class(tmp_path):
    recs = make_records(tmp_path, asset_class="bridge_element")
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    csv_text = (out / "bridge_entry.csv").read_text(encoding="utf-8")
    header = csv_text.splitlines()[0].split(",")
    for col in ("element", "condition_state", "quantity", "unit", "criteria_matched"):
        assert col in header
    assert len(csv_text.splitlines()) == 1 + 3


def test_unknown_backend_raises():
    from cascade.gate import run_gate

    with pytest.raises(ValueError):
        run_gate(Image.new("RGB", (8, 8)), "x", backend="bogus", log=CallLog())


def test_force_route_overrides_clean_gate_verdict_for_listed_class(tmp_path):
    recs = make_records(tmp_path, n=2, asset_class="pv_module")
    out = tmp_path / "run"
    summary = run_cascade(recs, out, RunConfig(gate="none", grader="claude"), gate_fn=fake_gate, grade_fn=fake_grade)
    run = load_run(out)
    g0 = next(g for g in run["gate"] if g["image_id"] == "img_0")
    assert g0["routed"] is True and g0["damage_present"] is False  # verdict kept, routing overridden
    assert "[forced: asset class pv_module]" in g0["reason"]
    assert summary["routed_to_grader"] == 2
    assert {f.evidence.image_ids[0] for f in run["findings"]} == {"img_0", "img_1"}


def test_force_route_disabled_keeps_gate_routing(tmp_path):
    recs = make_records(tmp_path, n=2, asset_class="pv_module")
    out = tmp_path / "run"
    summary = run_cascade(recs, out, RunConfig(gate="none", grader="claude", force_route_classes=()), gate_fn=fake_gate, grade_fn=fake_grade)
    g0 = next(g for g in load_run(out)["gate"] if g["image_id"] == "img_0")
    assert g0["routed"] is False and "[forced" not in g0["reason"]
    assert summary["routed_to_grader"] == 1


def test_review_timeline_running_agreement(tmp_path):
    recs = make_records(tmp_path, n=4)
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    findings = load_run(out)["findings"]
    log = ReviewLog(out / "reviews.sqlite")
    log.apply("run", findings[0], "accepted", "r1")
    log.apply("run", findings[1], "overridden", "r1", "S1")
    log.apply("run", findings[2], "accepted", "r2")
    tl = log.timeline("run")
    assert [r["n"] for r in tl] == [1, 2, 3]
    assert [round(r["agreement_rate"], 2) for r in tl] == [1.0, 0.5, 0.67]
    assert tl[1]["new_level"] == "S1" and tl[2]["reviewer"] == "r2"
