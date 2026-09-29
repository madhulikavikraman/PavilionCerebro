from PIL import Image

from cascade.pipeline import RunConfig
from cascade.schema import Action, Evidence, Finding, GateRecord, ImageRecord, Measurements, NativeScale, Unified, unassessable_finding
from cascade.surge import FEMA_CLASSES, run_surge, surge_counts, surge_records


def mk(fid, value, level, conf=0.7, rank=None):
    f = Finding(
        finding_id=fid,
        asset_class="building_disaster",
        defect_type="structural damage",
        native_scale=NativeScale(standard="FEMA-PDA", value=value, criteria_matched=["x"]),
        unified=Unified(level=level, uncertainty="+/-1", flags=[]),
        measurements=Measurements(area_cm2=None, crack_width_mm=None, delta_t_k=None, percent_area_rusted=None, section_loss_pct=None, confidence=conf),
        action=Action(code="prioritize", sla_days=7, basis="row"),
        justification="j",
        evidence=Evidence(image_ids=[fid.split("/")[0]], bbox=[0, 0, 1, 1], tile="full"),
    )
    f.queue_rank = rank
    return f


def test_surge_counts_cover_every_fema_class_and_u():
    findings = [mk("a/full", "Destroyed", "S4", 0.9, 1), mk("b/full", "Major", "S3", 0.6, 2), mk("c/full", "Undamaged", "S0", 0.8, 3)]
    findings.append(unassessable_finding(finding_id="d/full", asset_class="building_disaster", standard="FEMA-PDA", evidence=Evidence(image_ids=["d"]), reason="smoke"))
    c = surge_counts(findings)
    assert set(FEMA_CLASSES) <= set(c["by_fema_class"])
    assert c["by_fema_class"]["Destroyed"] == 1 and c["by_fema_class"]["Inaccessible"] == 0
    assert c["u_count"] == 1 and c["by_level"]["U"] == 1
    assert c["n_images"] == 4
    assert abs(c["mean_confidence"] - (0.9 + 0.6 + 0.8) / 3) < 1e-9  # U rows excluded
    assert [r["image_id"] for r in c["ranked"]][:3] == ["a", "b", "c"]


def test_surge_counts_empty():
    c = surge_counts([])
    assert c["n_findings"] == 0 and c["u_rate"] is None and c["mean_confidence"] is None


def test_run_surge_over_folder_writes_report(tmp_path):
    folder = tmp_path / "event"
    folder.mkdir()
    for i in range(3):
        Image.new("RGB", (40, 30), (200, 50 * i, 50)).save(folder / f"scene_{i}.jpg")

    def fake_gate(img, image_id, *, backend, log, no_damage_min_conf):
        log.record(stage="gate", model="fake", image_id=image_id, input_tokens=1, output_tokens=1, seconds=0.0)
        return GateRecord(image_id=image_id, usable=True, damage_present=True, confidence=0.9, reason="debris", routed=True, model="fake", seconds=0.0, usd=0.0)

    values = iter([("Destroyed", "S4"), ("Inaccessible", "U"), ("Affected", "S1")])

    def fake_grade(img, *, finding_id, image_id, asset_class, backend, rubric, metadata, exemplars, evidence, log):
        assert asset_class == "building_disaster" and rubric["standard"] == "FEMA-PDA"
        assert evidence.tile == "full"  # surge never tiles
        v, lvl = next(values)
        return mk(finding_id, v, lvl)

    counts = run_surge(tmp_path / "out", folder=folder, gate="none", grader="claude", gate_fn=fake_gate, grade_fn=fake_grade)
    assert counts["n_images"] == 3 and counts["u_count"] == 1
    assert counts["by_fema_class"]["Destroyed"] == 1
    assert counts["ranked"][0]["level"] == "S4" and counts["ranked"][0]["action"] == "escalate"
    assert (tmp_path / "out" / "surge_report.md").exists() and (tmp_path / "out" / "surge_counts.json").exists()
    text = (tmp_path / "out" / "surge_report.md").read_text(encoding="utf-8")
    assert "| Destroyed | 1 |" in text and "Unassessable (U): 1" in text


def test_surge_records_from_manifest_filters_asset_class(tmp_path):
    from cascade.ingest import write_manifest

    recs = [
        ImageRecord(image_id="b1", path="x", sha256="0" * 64, width=1, height=1, asset_class="building_disaster"),
        ImageRecord(image_id="s1", path="x", sha256="0" * 64, width=1, height=1, asset_class="steel_coating"),
    ]
    m = tmp_path / "m.jsonl"
    write_manifest(recs, m)
    assert [r.image_id for r in surge_records(manifest=m)] == ["b1"]
    assert RunConfig().tiles is False
