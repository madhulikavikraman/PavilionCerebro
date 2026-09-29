from PIL import Image

from cascade.exemplars import exemplar_provider, select_exemplars
from cascade.ingest import write_manifest
from cascade.schema import ImageRecord


def rec(iid, ac, grade, split="dev", source="dataset", path="x"):
    labels = {"grade_native": grade, "grade_source": source} if grade is not None else {}
    return ImageRecord(image_id=iid, path=path, sha256="0" * 64, width=8, height=8, asset_class=ac, split=split, labels=labels)


def test_select_spreads_across_grades_and_caps_at_five():
    recs = [rec(f"p{i}", "steel_coating", "Poor") for i in range(6)] + [rec("f1", "steel_coating", "Fair"), rec("s1", "steel_coating", "Severe")]
    chosen = select_exemplars(recs, "steel_coating", k=3)
    assert [r.labels["grade_native"] for r in chosen] == ["Fair", "Poor", "Severe"]
    assert len(select_exemplars(recs, "steel_coating", k=9)) == 5


def test_select_ignores_other_classes_eval_split_and_unlabelled():
    recs = [rec("a", "pv_module", "CoA 2"), rec("b", "steel_coating", "Poor", split="eval"), rec("c", "steel_coating", None), rec("d", "steel_coating", "Fair", source=None), rec("e", "steel_coating", "Severe")]
    chosen = select_exemplars(recs, "steel_coating", k=5)
    assert [r.image_id for r in chosen] == ["e"]
    assert select_exemplars(recs, "steel_coating", k=5, exclude_ids={"e"}) == []


def test_provider_loads_images_once(tmp_path):
    p = tmp_path / "ex.jpg"
    Image.new("RGB", (8, 8)).save(p)
    recs = [rec("a", "steel_coating", "Poor", path=str(p)), rec("b", "steel_coating", "Fair", path=str(p))]
    m = tmp_path / "dev.jsonl"
    write_manifest(recs, m)
    provide = exemplar_provider(m, k=2)
    ex = provide("steel_coating")
    assert [e.native_value for e in ex] == ["Fair", "Poor"]
    assert [e.image_id for e in ex] == ["b", "a"]
    assert provide("steel_coating") is ex
    assert provide("pv_module") == []
