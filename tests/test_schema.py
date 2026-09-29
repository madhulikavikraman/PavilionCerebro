import json

from cascade.schema import Evidence, Finding, GateOutput, GraderOutput, unassessable_finding


def test_grader_output_schema_has_all_fields_required():
    schema = GraderOutput.model_json_schema()
    assert set(schema["required"]) == {"defect_type", "native_scale", "unified", "measurements", "action", "justification"}
    meas = schema["$defs"]["Measurements"]
    assert set(meas["required"]) == {"area_cm2", "crack_width_mm", "delta_t_k", "percent_area_rusted", "section_loss_pct", "confidence"}


def test_round_trip_contract():
    raw = {
        "defect_type": "corrosion",
        "native_scale": {"standard": "CorrosionCS", "value": "Poor", "criteria_matched": ["Rust with pitting"]},
        "unified": {"level": "S3", "uncertainty": "+/-1", "flags": ["section_loss"]},
        "measurements": {"area_cm2": None, "crack_width_mm": None, "delta_t_k": None, "percent_area_rusted": 35.0, "section_loss_pct": None, "confidence": 0.8},
        "action": {"code": "prioritize", "sla_days": 90, "basis": "CorrosionCS row Poor"},
        "justification": "Laminar rust across the flange.",
    }
    out = GraderOutput.model_validate_json(json.dumps(raw))
    f = Finding.from_grader(out, finding_id="img_0/full", asset_class="steel_coating", evidence=Evidence(image_ids=["img_0"]), model="test", usd=0.01, seconds=1.2)
    assert f.unified.level == "S3"
    assert f.review.status == "pending"
    assert Finding.model_validate_json(f.model_dump_json()).finding_id == "img_0/full"


def test_unassessable_is_u_not_s0():
    f = unassessable_finding(finding_id="x", asset_class="pv_module", standard="IEC-62446-3-CoA", evidence=Evidence(image_ids=["x"]), reason="blurred")
    assert f.unified.level == "U"
    assert "not_measurable" in f.unified.flags


def test_gate_output_bounds():
    GateOutput(usable=True, damage_present=False, confidence=0.5, reason="ok")
    try:
        GateOutput(usable=True, damage_present=False, confidence=1.5, reason="bad")
        assert False, "confidence above 1 must fail"
    except Exception:
        pass
