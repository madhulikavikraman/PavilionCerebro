import csv

from cascade.export import QUEUE_COLUMNS, write_findings_json, write_queue_csv
from cascade.prioritize import rank
from cascade.review import ReviewLog
from cascade.schema import Action, Evidence, Finding, Measurements, NativeScale, Unified


def mk(fid, level):
    return Finding(
        finding_id=fid,
        asset_class="bridge_element",
        defect_type="spall",
        native_scale=NativeScale(standard="MBEI-CS", value="CS3", criteria_matched=["Spall greater than 1 in deep"]),
        unified=Unified(level=level, uncertainty="+/-1", flags=[]),
        measurements=Measurements(area_cm2=None, crack_width_mm=None, delta_t_k=None, percent_area_rusted=None, section_loss_pct=None, confidence=0.7),
        action=Action(code="schedule", sla_days=180, basis="MBEI CS3"),
        justification="Deep spall with exposed aggregate.",
        evidence=Evidence(image_ids=["b1"], bbox=[0, 0, 10, 10], tile="full"),
    )


def test_queue_csv_and_review_log(tmp_path):
    ranked = rank([mk("b1/full", "S2"), mk("b2/full", "S4")])
    rows = write_queue_csv(ranked, tmp_path / "queue.csv")
    write_findings_json(ranked, tmp_path / "findings.json")
    with (tmp_path / "queue.csv").open(encoding="utf-8") as fh:
        got = list(csv.DictReader(fh))
    assert [r["queue_rank"] for r in got] == ["1", "2"]
    assert set(got[0].keys()) == set(QUEUE_COLUMNS)
    assert got[0]["unified_level"] == "S4" and got[0]["action_code"] == "escalate"

    log = ReviewLog(tmp_path / "reviews.sqlite")
    f = log.apply("run1", ranked[1], "overridden", "inspector", new_level="S3")
    assert f.unified.level == "S3" and f.review.prior_level == "S2"
    log.apply("run1", ranked[0], "accepted", "inspector")
    agg = log.agreement("run1")
    assert agg["total"] == 2 and agg["agreement_rate"] == 0.5
