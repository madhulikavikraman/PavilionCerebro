"""Eval matrix against dataset labels, no model, no network."""

from cascade.evalmetrics import ORDINAL_LABELS, eval_matrix, predicted_ordinal, qwk, truth_ordinal
from cascade.schema import ImageRecord


def rec(i, ac, labels):
    return ImageRecord(image_id=f"i{i}", path=f"i{i}.jpg", sha256="0" * 64, width=10, height=10, asset_class=ac, labels=labels)


def finding(iid, value, level="S2"):
    return {"unified": {"level": level}, "native_scale": {"value": value}, "evidence": {"image_ids": [iid]}}


def test_truth_and_predicted_ordinals():
    assert truth_ordinal(rec(0, "steel_coating", {"grade_native": "Poor"})) == 2
    assert truth_ordinal(rec(0, "pv_module", {"grade_native": "CoA 3"})) == 2
    assert truth_ordinal(rec(0, "building_disaster", {"source_class": "Collapsed"})) == 2
    assert truth_ordinal(rec(0, "bridge_element", {"grade_source": "team-graded", "grade_native": 3})) == 2
    assert truth_ordinal(rec(0, "bridge_element", {"grade_source": "dataset", "grade_native": 3})) is None
    assert predicted_ordinal("steel_coating", [finding("a", "Fair"), finding("a", "Severe")]) == 3
    assert predicted_ordinal("building_disaster", [finding("a", "Major")]) == 1
    assert predicted_ordinal("building_disaster", [finding("a", "Inaccessible")]) is None
    assert predicted_ordinal("bridge_element", [finding("a", "CS3")]) == 2
    assert predicted_ordinal("pv_module", [finding("a", "CoA 2", level="U")]) is None


def test_qwk_perfect_and_worst():
    assert qwk([0, 1, 2, 3], [0, 1, 2, 3], 4) == 1.0
    assert qwk([0, 0, 3, 3], [3, 3, 0, 0], 4) < 0


def test_eval_matrix_counts_gate_and_grading():
    records = {
        "i0": rec(0, "steel_coating", {"damage_present": True, "grade_native": "Poor"}),
        "i1": rec(1, "steel_coating", {"damage_present": True, "grade_native": "Severe"}),
        "i2": rec(2, "steel_coating", {"damage_present": False, "grade_native": "Good"}),
        "i3": rec(3, "steel_coating", {}),  # unlabelled: never counted
    }
    gate = [{"image_id": "i0", "routed": True}, {"image_id": "i1", "routed": False}, {"image_id": "i2", "routed": True}, {"image_id": "i3", "routed": True}]
    findings = [finding("i0", "Poor"), finding("i2", "Fair")]
    m = eval_matrix(records, gate, findings)
    g = m["gate"]
    assert (g["tp"], g["fp"], g["fn"], g["tn"], g["unlabelled"]) == (1, 1, 1, 0, 1)
    assert g["misses"] == ["i1"] and g["recall"] == 0.5 and g["precision"] == 0.5
    sc = m["grading"]["steel_coating"]
    assert sc["labels"] == ORDINAL_LABELS["steel_coating"]
    assert sc["n_routed_with_truth"] == 2 and sc["n_assessed"] == 2 and sc["u_rate"] == 0
    assert sc["matrix"][2][2] == 1 and sc["matrix"][0][1] == 1  # Poor->Poor exact, Good->Fair over-graded
    assert sc["exact_match"] == 0.5 and sc["within_one_grade"] == 1.0 and sc["over_graded"] == 1


def test_eval_matrix_u_rate_when_no_finding():
    records = {"i0": rec(0, "pv_module", {"damage_present": True, "grade_native": "CoA 2"})}
    m = eval_matrix(records, [{"image_id": "i0", "routed": True}], [])
    pv = m["grading"]["pv_module"]
    assert pv["n_assessed"] == 0 and pv["u_rate"] == 1.0 and pv["u_images"] == ["i0"] and pv["exact_match"] is None
