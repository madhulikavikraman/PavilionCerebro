"""Self-check: run every agent standalone on its real data, then the whole swarm.

  python scripts/selfcheck.py            # prints a summary, writes data/samples/metrics.json

Checks (non-zero exit if any fails):
  agent-0  wrapped cascade plumbing (fake grader, no model), opencv fallback accuracy on the replay sample
  agent-1  UPV + BMS through the one generic scorer; real low-UPV readings and the AC-1 output collapse flagged
  agent-2  SOH/RUL on NASA cells; cells flagged before their end-of-life crossing; RUL error
  agent-3  RP-1043 false alarms, detection, leave-one-severity-out diagnosis
  swarm    dashboard state updates every tick, a mitigation fires, disaster mode re-ranks
Every number the marketing site and the video quote comes from this file's output.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from agents.base import AgentReport  # noqa: E402
from agents.battery import BatteryAgent, evaluate_rul  # noqa: E402
from agents.hvac import HvacAgent, evaluate as evaluate_hvac  # noqa: E402
from agents.internal_sensor import InternalSensorAgent  # noqa: E402
from agents.structural_visual import CALIB_PATH, StructuralVisualAgent, _cascade  # noqa: E402
from coordinator.swarm import Swarm  # noqa: E402

OUT = ROOT / "data" / "samples" / "metrics.json"
results: dict = {}
failures: list = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' - ' + detail) if detail else ''}")
    if not ok:
        failures.append(name)


def agent0() -> None:
    print("agent-0 structural visual")
    gate, grade = _cascade()
    from cascade.schema import Action, Finding, Measurements, NativeScale, Unified

    def fake_grade(img, *, finding_id, image_id, asset_class, backend, rubric, metadata, exemplars=None, evidence=None, log=None):
        return Finding(finding_id=finding_id, asset_class=asset_class, defect_type="crack",
                       native_scale=NativeScale(standard=rubric["standard"], value=rubric["allowed_values"][-2], criteria_matched=[rubric["rows"][0]["criterion"]]),
                       unified=Unified(level="S3", uncertainty="+/-1", flags=[]),
                       measurements=Measurements(area_cm2=None, crack_width_mm=None, delta_t_k=None, percent_area_rusted=None, section_loss_pct=None, confidence=0.7),
                       action=Action(code="prioritize", sla_days=30, basis="plumbing test"), justification="fake grader for the wrapper plumbing test", evidence=evidence or {}, model="fake")

    real = grade.grade_image
    grade.grade_image = fake_grade
    try:
        a = StructuralVisualAgent(backend="none")  # cascade gate backend "none" + fake grader: no model, no network
        a._cache = {}
        a._cache_path = ROOT / "data" / "samples" / "cache" / "_selfcheck_plumbing.jsonl"
        img = sorted((ROOT / "data" / "samples" / "crack").glob("positive_*.jpg"))[0]
        reps = a.observe(("P1-parking", img))
        a._cache_path.unlink(missing_ok=True)
    finally:
        grade.grade_image = real
    r = reps[0]
    check("cascade wrapper: gate -> grade -> Finding -> AgentReport", isinstance(r, AgentReport) and r.evidence["cascade_level"] == "S3" and abs(r.evidence["frame_risk"] - 0.75) < 1e-9,
          f"S3 finding -> frame risk {r.evidence['frame_risk']}")

    a = StructuralVisualAgent(backend="opencv")
    rows = []
    for p in sorted((ROOT / "data" / "samples" / "crack").glob("*.jpg")):
        s = a.score_image(p)
        rows.append((p.name.startswith("positive"), s["risk"] >= 0.5))
    y, pr = np.array([r[0] for r in rows]), np.array([r[1] for r in rows])
    acc = float((y == pr).mean())
    calib = json.loads(CALIB_PATH.read_text())["meta"]
    check("opencv fallback on 60 replay images", acc >= 0.8, f"accuracy {acc:.1%}")
    check("opencv fallback on 1,600 held-out images", calib["accuracy"] >= 0.85, f"acc {calib['accuracy']:.1%}, precision {calib['precision']:.1%}, recall {calib['recall']:.1%}, Brier {calib['brier']}")
    results["agent0"] = {"replay_accuracy": round(acc, 4), "replay_n": len(rows), "replay_cracks_flagged": int((y & pr).sum()), "replay_cracks": int(y.sum()), "heldout": calib}


def agent1() -> None:
    print("agent-1 internal sensor (UPV + BMS, one scorer)")
    a = InternalSensorAgent()
    upv, bms = [], []
    for reps in a.stream():
        for r in reps:
            (upv if r.asset_id.startswith("upv") else bms).append(r)
    h = pd.DataFrame(a.upv_history)
    h["dev"] = (h["value"] - h["expected"]) / h["expected"]
    low = h[h["dev"] <= -0.20]
    flagged_low = int((low["risk"] >= 0.35).sum())
    low15 = h[h["dev"] <= -0.15]
    flagged15 = int((low15["risk"] >= 0.35).sum())
    check("UPV readings >=20% below expected are flagged", len(low) > 0 and flagged_low == len(low),
          f"{flagged_low}/{len(low)} flagged elevated or worse (at >=15% below: {flagged15}/{len(low15)}; misses are indirect-path readings)")
    normal_ish = h[h["dev"].abs() <= 0.02]
    upv_fa = float((normal_ish["risk"] >= 0.6).mean())
    check("UPV readings within 2% of expected rarely alarm", upv_fa <= 0.05, f"{upv_fa:.1%} reach high")
    # the AC-1 output collapse, visible in the raw data: weekday working-hour mean ~15-26 kW in July-Aug, ~5-7 kW 4-7 Sep 2018
    ep = [r for r in bms if "2018-09-04" <= r.evidence["source_time"][:10] <= "2018-09-07"]
    hit = [r for r in ep if r.risk_score >= 0.6 and r.evidence["channels"]["ac1_kw"]["risk"] >= 0.6]
    check("BMS: AC-1 output collapse (4-7 Sep 2018) flagged", len(hit) > 0, f"{len(hit)} high/critical reports with AC-1 as a driver")
    methods = {r.evidence["top_channel"]["baseline_method"] for r in bms}
    check("same scorer, provided vs inferred baselines", any("provided" in m for m in [upv[-1].evidence["worst_channel"]["baseline_method"]]) and any("inferred" in m for m in methods), ", ".join(sorted(methods)))
    results["agent1"] = {"upv_readings": len(h), "upv_low_readings": int(len(low)), "upv_low_flagged": flagged_low, "upv_low15_readings": int(len(low15)), "upv_low15_flagged": flagged15, "upv_near_expected_alarm_rate": round(upv_fa, 4),
                         "bms_reports": len(bms), "bms_ac1_event_reports_flagged": len(hit), "strength_fit_r2": round(a.strength["r2"], 3), "strength_fit_n": a.strength["n"]}


def agent2() -> None:
    print("agent-2 battery")
    a = BatteryAgent(start_cycle=1)
    first_flag, eol = {}, {}
    df = a.df
    for cell, g in df.groupby("cell"):
        b = g[g["capacity_ah"] <= 1.4]
        if not b.empty:
            eol[cell] = int(b["cycle"].min())
    for reps in a.stream():
        for r in reps:
            if r.risk_score >= 0.6 and r.asset_id not in first_flag:
                first_flag[r.asset_id] = r.evidence["cycle"]
    lead = {c: eol[c] - first_flag.get(c, 10 ** 6) for c in eol}
    ok = all(v > 0 for v in lead.values())
    check("every cell that reached EOL was flagged high before crossing it", ok, ", ".join(f"{c}: {v} cycles early" for c, v in lead.items()))
    rul = evaluate_rul()
    check("RUL projection error", rul["mae_cycles"] is not None and rul["mae_cycles"] < 15, f"MAE {rul['mae_cycles']} cycles over {rul['n']} checkpoints (10-40 cycles before EOL)")
    results["agent2"] = {"eol_cycles": eol, "first_high_cycle": first_flag, "lead_cycles": lead, "rul_mae_cycles": rul["mae_cycles"], "rul_points": rul["n"]}


def agent3() -> None:
    print("agent-3 hvac")
    e = evaluate_hvac()
    check("false alarms on held-out fault-free runs", e["false_alarm_rate_holdout_normal"] <= 0.05, f"{e['false_alarm_rate_holdout_normal']:.1%} of {e['n_holdout_normal_windows']} windows")
    check("diagnosis accuracy (leave-one-severity-out)", e["diagnosis_accuracy_detected"] >= 0.85, f"{e['diagnosis_accuracy_detected']:.1%} of {e['n_detected_windows']} detected windows")
    check("fault runs detected and diagnosed", e["fault_runs_detected_and_diagnosed"] >= 15, f"{e['fault_runs_detected_and_diagnosed']}/{e['fault_runs']} runs; severity exact {e['severity_exact']:.0%}, within one level {e['severity_within_one']:.0%}")
    results["agent3"] = {k: v for k, v in e.items() if k != "per_run"}
    results["agent3_per_run"] = e["per_run"]


def swarm() -> None:
    print("swarm / coordinator")
    s = Swarm(visual_backend="opencv")
    healths, ticks = [], []
    while not s.finished:
        s.step()
        snap = s.snapshot()
        healths.append(snap["health"]["building"])
        ticks.append(snap["tick"])
    check("dashboard state advances every tick", ticks == list(range(1, len(ticks) + 1)) and len(set(healths)) > 20, f"{len(ticks)} ticks, {s.coord.reports_ingested} reports fused, health {min(healths)}-{max(healths)}")
    mit = [e for e in s.coord.mitigation.log if e["type"] == "mitigation"]
    check("mitigation actions fire and are logged", len(mit) >= 3 and {"battery", "hvac", "structural_visual"} <= {e["subsystem"] for e in mit},
          "; ".join(f"t{e['tick']} {e['asset_id']}" for e in mit))
    # disaster mode: toggle at several points of a fresh run, time the re-triage
    s2 = Swarm(visual_backend="opencv")
    moved, ms = [], []
    while not s2.finished:
        s2.step()
        if s2.tick % 10 == 0:
            r = s2.coord.set_mode("disaster")
            moved.append(len(r["moved"]))
            ms.append(r["ms"])
            s2.coord.set_mode("normal")
    top_changes = sum(1 for m in moved if m > 0)
    check("disaster mode re-ranks visibly", top_changes >= len(moved) // 2, f"re-ranked at {top_changes}/{len(moved)} toggles, mean {np.mean(ms):.3f} ms")
    results["swarm"] = {"ticks": len(ticks), "reports_fused": s.coord.reports_ingested, "mitigations": [{k: e[k] for k in ("tick", "subsystem", "asset_id", "text")} for e in mit],
                        "rerank_ms_mean": round(float(np.mean(ms)), 4), "rerank_ms_max": round(float(np.max(ms)), 4), "rerank_toggles": len(ms), "rerank_toggles_changed_order": top_changes,
                        "health_min": min(healths), "health_max": max(healths)}


def main() -> int:
    t0 = time.time()
    for fn in (agent0, agent1, agent2, agent3, swarm):
        fn()
    a0, a1, a2, a3 = results["agent0"], results["agent1"], results["agent2"], results["agent3"]
    results["headline"] = {
        "subsystems_monitored": 4,
        "live_agents": 4,
        "roadmap_agents": 2,
        "public_datasets": 5,
        "real_fault_cases_flagged": a3["fault_runs_detected_and_diagnosed"] + len(a2["lead_cycles"]) + a1["upv_low_flagged"] + (1 if a1["bms_ac1_event_reports_flagged"] else 0),
        "real_fault_cases_breakdown": {"ashrae_fault_runs_detected_and_diagnosed": a3["fault_runs_detected_and_diagnosed"], "nasa_cells_flagged_before_eol": len(a2["lead_cycles"]),
                                       "umn_upv_low_readings_flagged": a1["upv_low_flagged"], "cu_bems_ac1_collapse_flagged": 1 if a1["bms_ac1_event_reports_flagged"] else 0},
        "rerank_ms_mean": results["swarm"]["rerank_ms_mean"],
        "hvac_false_alarm_rate": a3["false_alarm_rate_holdout_normal"],
        "hvac_diagnosis_accuracy": a3["diagnosis_accuracy_detected"],
        "crack_heldout_accuracy": a0["heldout"]["accuracy"],
        "battery_rul_mae_cycles": a2["rul_mae_cycles"],
    }
    results["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    OUT.write_text(json.dumps(results, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(f"\nheadline: {json.dumps(results['headline'], indent=1)}")
    print(f"wrote {OUT.relative_to(ROOT)} in {time.time() - t0:.1f}s; {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
