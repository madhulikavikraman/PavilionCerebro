"""Run report: metrics from a run folder and a stored report.md (fake backends, no network)."""

from cascade.pipeline import RunConfig, run_cascade
from cascade.report import REPORT_FIELDS, render_markdown, run_metrics, write_run_report
from test_pipeline import fake_gate, fake_grade, make_records


def test_run_metrics_and_report_files(tmp_path):
    recs = make_records(tmp_path, n=4)
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    m = run_metrics(out)
    assert all(k in m for k in REPORT_FIELDS)
    assert m["images"] == 4 and m["gated"] == 4 and m["routed"] == 3 and m["unusable"] == 1
    assert m["findings"] == 3 == sum(m[lvl] for lvl in ("S0", "S1", "S2", "S3", "S4", "U")) and m["S4"] == 1
    assert m["top_queue"][0]["level"] == "S4"  # S4 sorts first
    assert m["usd_total"] == 0.0 and m["models"] == ["fake-gate", "fake-grader"]
    p = write_run_report(out)
    assert p.name == "report.md" and (out / "report.json").exists()
    text = p.read_text(encoding="utf-8")
    assert "# Run report: run" in text and "| S0 | S1 | S2 | S3 | S4 | U |" in text and "Top of the work queue" in text


def test_report_includes_eval_matrix_when_labelled(tmp_path):
    recs = make_records(tmp_path, n=3)
    for r in recs:
        r.labels = {"damage_present": True, "grade_native": "Severe"}
    out = tmp_path / "run"
    run_cascade(recs, out, RunConfig(gate="none"), gate_fn=fake_gate, grade_fn=fake_grade)
    m = run_metrics(out, {r.image_id: r for r in recs})
    assert m["eval"]["gate"]["fn"] == 1  # img_0 is the clean confident gate verdict, so it is a miss
    md = render_markdown(m)
    assert "Grading matrix: steel_coating" in md and "truth \ predicted" in md


def test_run_metrics_on_empty_folder(tmp_path):
    out = tmp_path / "empty"
    out.mkdir()
    m = run_metrics(out)
    assert m["images"] == 0 and m["findings"] == 0 and m["usd_per_image"] is None and m["top_queue"] == []
