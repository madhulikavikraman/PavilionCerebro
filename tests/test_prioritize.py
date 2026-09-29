from datetime import date

from cascade.prioritize import rank, score, urgency_for
from cascade.schema import Action, Evidence, Finding, Measurements, NativeScale, Unified


def mk(fid, level, asset="steel_coating", flags=None, image="img"):
    return Finding(
        finding_id=fid,
        asset_class=asset,
        defect_type="d",
        native_scale=NativeScale(standard="CorrosionCS", value="x", criteria_matched=[]),
        unified=Unified(level=level, uncertainty="+/-1", flags=flags or []),
        measurements=Measurements(area_cm2=None, crack_width_mm=None, delta_t_k=None, percent_area_rusted=None, section_loss_pct=None, confidence=0.5),
        action=Action(code="record", sla_days=None, basis="b"),
        justification="j",
        evidence=Evidence(image_ids=[image]),
    )


def test_s4_outranks_everything_regardless_of_criticality():
    low = mk("a", "S4", image="low")
    high = mk("b", "S3", image="high")
    ranked = rank([high, low], criticality_by_image={"low": 1.0, "high": 3.0})
    assert ranked[0].finding_id == "a"
    assert ranked[0].action.code == "escalate" and ranked[0].action.sla_days == 0


def test_u_listed_last_but_present():
    ranked = rank([mk("u", "U"), mk("s1", "S1")])
    assert [f.finding_id for f in ranked] == ["s1", "u"]
    assert ranked[1].queue_score is None


def test_section_loss_doubles_consequence():
    plain = score(mk("p", "S3"))
    flagged = score(mk("f", "S3", flags=["section_loss"]))
    assert flagged == 2 * plain


def test_urgency_caps_at_two():
    assert urgency_for("2026-01-01", today=date(2026, 9, 25)) == 2.0
    assert urgency_for("2026-09-25", today=date(2026, 9, 25)) == 1.0
    assert urgency_for(None) == 1.0
