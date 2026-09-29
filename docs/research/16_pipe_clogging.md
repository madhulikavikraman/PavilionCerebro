# 16. Pipe clogs in a tower: how to test for them, catch them early and prevent them

Module key `clog`. Page `app/site_pages/pipes.py`. Written 2026-09-26. Every number in the "Measured results"
section is generated from `eval/clog/*.json` by `scripts/clog_doc_tables.py`; the prose around it has no measured
numbers of its own.

Labels used throughout: **REAL** (measured data), **SIMULATED** (physics model output), **INJECTED** (a fault we put
into a simulation), **SYNTHETIC** (invented demo records), **RULE** (quoted from a code or regulation).

## 1. Question

The user asked (ask 6): "How can we test the pipe-clogging and prevention from the flow and hardware periodic
checking, with AI software research, and build some conclusions from that?"

We split it into four questions:

1. Can flow and pressure data from a tower's domestic-water riser show a partial clog, and where it is?
2. Does a short, human-approved active flow test beat passive monitoring? Does machine learning beat a plain rule?
3. On the drain side, which signal shows a blockage first, on real data?
4. How often should each piece of hardware be checked, and on what basis?

## 2. What we found (sources are numbered as in `src/cascade/building/clog/sources.json`)

**Physics.** A partial clog adds a local minor loss h = K v^2 / 2g on top of pipe friction; EPANET models both
(Hazen-Williams C for new cast-iron pipe is about 130-140) [5]. WNTR 1.5.0 runs EPANET from Python and lets us set a
per-pipe minor-loss K [4]. The loss scales with velocity squared, so a clog is nearly invisible when water barely
moves. In a residential riser at night that is most of the time.

**Code limits that shape the riser.** UPC-based section 608.2 limits static pressure at outlets to 80 psi and requires
a pressure regulator with a strainer where supply pressure is higher. The same section exempts regulators of
1-1/2 in (40 mm) and larger from the strainer requirement [10]. A strainer at a riser-size PRV is therefore a design
choice, not a code mandate. Where one is fitted, its differential pressure at a known flow is the most direct check.
California Plumbing Code equivalence was not verified.

**Drain capacity limits the active test.** A DN100 discharge stack carries about 4.0 L/s with square entries and
5.2 L/s with swept entries under EN 12056-2, as summarised by Lansing 2023 [11]. A supply test that discharges into a
stack must stay at or below that. Larger draws should go to a break tank.

**Flow-meter noise.** Clamp-on transit-time meters quote +-1% of reading from 0.5 to 12 m/s and +-0.0046 m/s below
that [12]. We model flow noise as max(1% of Q, 0.0046 m/s x pipe area). Pressure noise (sd 0.15 m per reading) is our
assumption.

**Real blockage data.** The Bellinge data set (Denmark, CC BY 4.0) is a 1.7 km2 municipal combined sewer [2]. Its
sensor readme logs that "the throttle pipe between sensor G71F04R and G71F06R was blocked" from 23 to 28 July 2020
[3]. We found no public building-drain data set with labelled blockages. Bellinge therefore tests the detector logic
on real data, not building-drain performance.

**Published methods.** A normal-behaviour level model plus a control-chart alarm is an established pattern for sewer
blockages (Rosin et al. 2022, abstract only) [13]. Active acoustic drain tests exist in the lab [14]. Transient tests
for partial blockages in pressurised pipes still lack large, complex, real systems [15]. Drain-camera AI is sold as
"assisted", with certified people confirming codes [16]. Clog analytics are sold for city sewers [17]. The building
supply devices we checked advertise leak checks, not clog tests [18, 19].

**Periodic checks in Los Angeles.**
- Backflow assemblies: tested at least annually by a tester licensed by LA County Public Health (LADWP Rule 16-D
  sections 9.1-9.2) [7].
- Grease interceptors at permitted food-service establishments: cleaned before fats, oils, grease (FOG) and solids
  reach 25% of the liquid depth. Hydromechanical grease traps are cleaned daily (LA Sanitation SSMP v3.0, 7.5.3)
  [8, 9].
- City sewers: cleaning frequency is set by each pipe's performance history. Any pipe with an overflow gets a CCTV
  inspection, usually within about 48 hours [8]. We adopt this as a team-proposed practice for building drains.
- In-building drains: we found no authoritative fixed interval for jetting or camera inspection.

**Demand data.** HSB Living Lab (Sweden, CC BY 4.0) gives 10-minute, fixture-level water use for real apartments
[1]. Its `value` column is m3 even though the data dictionary says litres; the total matches the stated volume
(computed in `hsb_stats`, see results). Timestamps are UTC. We convert them to Europe/Stockholm so the 03:00 test
lands at local night. Rows without an apartment are shared spaces; we drop them, so our demand is apartment-only.

## 3. What we built

All paths are in this repository.

| Piece | File | Env | Label |
|---|---|---|---|
| Fetch/copy inputs, sha256 manifest, HSB properties | `scripts/fetch_clog_data.py` -> `eval/clog/data_manifest.json` | origin_hack | REAL |
| Code-plausible 32-floor riser: PRVs feed the low (F1-F11) and mid (F12-F22) zones, the booster feeds the top zone (F23-F32) directly, every outlet at or below 80 psi static | `src/cascade/building/clog/geometry.py`, `sim_riser.py` | either | SYNTHETIC design |
| Real apartment demand mapped onto the tower (the same HSB apartments on a different apartment-to-unit map for the train and test "buildings"; same riser geometry) | `clog/demand.py` | either | REAL demand |
| WNTR week-long simulations: clean weeks plus clogs with K drawn log-uniform over a continuous range, severity from contiguous K bands, on 6 riser segments and 2 PRV strainers | `scripts/clog_riser_sim.py`, `scripts/clog_sim_lib.py` (the only code that imports wntr/pyswmm; offline) -> `data/raw/clog/sims/*.npz`, `eval/clog/riser_scenarios.csv`, `sim_check.json` | cerebro_ml | SIMULATED + INJECTED |
| Nightly active test: a known flow per zone (4.0 and 2.5 L/s) at the zone-top test valve, proposed as a 60-120 s hold logged at 1 s (`ACTIVE_TEST_SECONDS`). The model solves the settled flow at one 10-minute EPANET step and does not simulate the transient. Feature = jump in segment head loss / jump in zone flow squared, minus the commissioning value from an earlier clean week | `clog/features.py` | either | SIMULATED |
| Detectors: z-score rule (no ML) vs gradient boosting (grade + locate), both passive and active, plus a BMS low-pressure alarm baseline and naive grading baselines (training-majority class, each constant class, random grade at training frequencies). Thresholds set on out-of-fold clean training nights. Evaluated per scenario with two-stage week-cluster bootstrap CIs, plus three out-of-distribution stress tests and one constant-offset cancellation check | `clog/detect.py`, `scripts/clog_riser_eval.py` -> `eval/clog/riser_metrics.json`, `models/clog/riser_act4.joblib` | origin_hack | SIMULATED |
| Known-volume drain-down test in a building drain: orifice openings from clean to nearly shut, level-sensor noise and quantisation, right-censoring when it never drains | `scripts/clog_drain_sim.py`, `scripts/clog_sim_lib.py`, `clog/drain.py` -> `eval/clog/drain_test.json` | cerebro_ml | SIMULATED + INJECTED |
| Bellinge July 2020 case study: normal-behaviour model of upstream depth (time-blocked out-of-fold residual threshold), paired rule "upstream above normal AND downstream starved", fixed-level threshold sweep, paired-rule parameter sweep | `scripts/clog_bellinge.py`, `clog/bellinge.py` -> `eval/clog/bellinge_case.json` | origin_hack | REAL |
| Risk-based check calendar: strainer dP at PRV stations, grease interceptor (25% rule) and traps, annual backflow test, drain camera after backups | `clog/schedule.py`, `clog/rules.json`, `scripts/clog_schedule.py` -> `eval/clog/schedule.json` | origin_hack | RULE + SYNTHETIC register |
| Page: SVG riser-and-stack sensor diagram, alarm-rate bars with CIs, drain curves, Bellinge chart, schedule, provenance, conclusions | `app/site_pages/pipes.py`, `clog/svg.py`, `clog/report.py` | origin_hack | all labelled |

**Safety rule, built into the page, the schedule and this design.** Cerebro proposes the nightly test and each check.
A facilities person approves the standing test schedule once, and the building management system (BMS) runs it with
its own low-pressure abort. Tests use domestic cold water only, never fire, sprinkler or standpipe piping. Every
schedule row carries "requires human approval". Cerebro never opens a valve itself.

## 4. Measured results

<!-- clog:results:start -->
_Generated by `scripts/clog_doc_tables.py` from `eval/clog/*.json`; do not edit by hand._
### Inputs (REAL) and their hashes

| dataset | kind | licence | bytes | sha256 (first 16) |
|---|---|---|---|---|
| HSB Living Lab fixture-level household water consumption (2019-2023) | REAL | CC BY 4.0 | 6244502 | ff766b30d05e65c2 |
| Bellinge sensor data, cleaned, G71F04R Level 1 (upstream of the throttle pipe) | REAL | CC BY 4.0 | 35716968 | 4c232b41baef6681 |
| Bellinge sensor data, cleaned, G71F06R Level inlet (downstream of the throttle pipe) | REAL | CC BY 4.0 | 531132816 | 72161dc962331693 |
| Bellinge sensor readme (2_Sensordata_v2.pdf) | REAL | CC BY 4.0 | 232723 | d714b4babb397d66 |
| LADWP Rule 16-D Protection of Public Water Supply | RULE | public regulation (quoted, not redistributed) | 97801 | bd4728549f7cf7d0 |
| LA Sanitation Sewer System Management Plan v3.0 (25 Jan 2019) | RULE | public document (quoted, not redistributed) | 3765901 | 8c233f3e5f9bbf46 |
| Section 608.2 Excessive Water Pressure (UPC-based Hawaii Plumbing Code 2021, UpCodes) | RULE | public code text (quoted, not redistributed) | 56107 | 9aa3990e6ec0bbd1 |
| Lansing 2023, CIB W062 symposium paper on single-stack drainage standards | RULE | conference paper (quoted, not redistributed) | 6922296 | 2cfaad33be07d601 |

HSB properties computed by `fetch_clog_data.py`: 652315 rows, 28 apartments, total `value` 3270.8 (m3), share of volume with no apartment (shared spaces, dropped) 39.3%, UTC span 2019-12-31 00:00:00 to 2023-01-31 14:10:00.

### Riser simulation (SIMULATED riser, INJECTED clogs, REAL demand)

1203 simulated weeks; engines {'EPANET': 1202, 'WNTRSimulator': 1}; weeks with non-converged steps 0; median 0.403 s per week; wall 206.1 s. HSB good weeks: train pool 47, test pool 24. Commissioning weeks {'train': '2020-01-06', 'test': '2021-11-15'}. Train weeks: 2020-01-13, 2020-01-27, 2020-02-17, 2020-03-02, 2020-05-04, 2020-05-11, 2020-06-01, 2020-09-21, 2020-10-12, 2020-10-19, 2020-11-23, 2020-12-07, 2021-01-18, 2021-02-01, 2021-09-27, 2021-10-25. Test weeks: 2022-03-21, 2022-04-25, 2022-05-02, 2022-05-09, 2022-05-16, 2022-08-22, 2022-10-24, 2023-01-23.

Engine cross-check (EPANET vs WNTRSimulator, max absolute pressure difference over all sensors and steps):

| clog pipe | K | EPANET s | WNTRSimulator s | max abs diff (m) |
|---|---|---|---|---|
| None | 0.0 | 0.388 | 2.92 | 0.00015 |
| P04 | 300.0 | 0.634 | 35.83 | 0.00734 |
| STR_L | 300.0 | 0.319 | 31.96 | 0.00735 |
| P30 | 30.0 | 1.142 | 4.12 | 0.00066 |

### Held-out test: alarm rate per night by true state

Held-out test (different unit map, 2022-23 weeks): 240 scenarios (1680 nights); scenarios per state {'clean': 48, 'mild': 62, 'moderate': 49, 'severe': 81}. Train: 480 scenarios (3360 nights). Threshold: 95th percentile of out-of-fold P(clog) or max-z on clean training nights (GroupKFold by week). CI: 95% two-stage cluster bootstrap (1000 resamples): the 8 test demand weeks with replacement, then scenarios within each drawn week (within true severity for macro-F1). Severity bands (K): {'mild': [1, 10], 'moderate': [10, 50], 'severe': [50, 300]}.

| detector | clean = false alarms | mild | moderate | severe |
|---|---|---|---|---|
| Active test 4.0 L/s, z-score rule (no ML) | 3.9% (1.2-6.9%) | 6.2% (3.0-11.3%) | 49.3% (32.9-63.7%) | 98.1% (93.2-100.0%) |
| Active test 4.0 L/s, gradient boosting | 0.6% (0.0-1.8%) | 3.2% (0.3-8.7%) | 30.0% (19.5-39.6%) | 95.1% (90.2-98.9%) |
| Active test 2.5 L/s, z-score rule (no ML) | 17.9% (12.5-23.5%) | 20.5% (15.6-25.2%) | 31.5% (25.9-37.9%) | 89.4% (82.7-94.6%) |
| Active test 2.5 L/s, gradient boosting | 24.7% (18.8-30.1%) | 27.9% (22.1-33.7%) | 38.5% (30.8-46.8%) | 87.1% (80.0-93.1%) |
| Passive 24 h, z-score rule (no ML) | 8.6% (4.8-12.8%) | 9.0% (5.2-13.5%) | 10.2% (5.5-15.5%) | 8.8% (5.4-12.4%) |
| Passive 24 h, gradient boosting | 4.5% (2.4-7.1%) | 3.0% (1.1-5.2%) | 3.8% (1.7-6.2%) | 4.6% (2.1-7.8%) |
| BMS low-pressure alarm at zone tops (baseline) | 1.8% (0.3-3.9%) | 2.1% (0.7-3.6%) | 1.7% (0.3-3.7%) | 1.8% (0.4-3.5%) |

### Held-out test: grading and locating

| detector | macro-F1 (95% CI) | QWK | locate moderate | locate severe | persistent alarm, clean weeks | persistent alarm, moderate weeks |
|---|---|---|---|---|---|---|
| Active test 4.0 L/s, z-score rule (no ML) | 0.492 (0.446-0.532) | 0.763 | 73.2% (61.3-83.9%) | 96.8% (89.6-100.0%) | 4.2% | 69.4% |
| Active test 4.0 L/s, gradient boosting | 0.584 (0.536-0.622) | 0.788 | 70.3% (57.9-81.2%) | 96.8% (89.6-100.0%) | 0.0% | 44.9% |
| Active test 2.5 L/s, z-score rule (no ML) | 0.392 (0.369-0.414) | 0.594 | 37.9% (28.6-46.2%) | 89.8% (82.1-95.8%) | 25.0% | 49.0% |
| Active test 2.5 L/s, gradient boosting | 0.398 (0.365-0.431) | 0.482 | 25.1% (16.0-34.0%) | 87.1% (79.9-93.9%) | 37.5% | 63.3% |
| Passive 24 h, z-score rule (no ML) | 0.124 (0.107-0.142) | 0.005 | - | - | 6.2% | 6.1% |
| Passive 24 h, gradient boosting | 0.222 (0.197-0.245) | 0.001 | - | - | 4.2% | 2.0% |
| BMS low-pressure alarm at zone tops (baseline) | - | - | - | - | 2.1% | 0.0% |
| Baseline: always 'mild' (training majority) | 0.103 | - | chance 12.5% | - | - | - |
| Baseline: always 'clean' | 0.083 | - | - | - | - | - |
| Baseline: always 'moderate' | 0.085 | - | - | - | - | - |
| Baseline: always 'severe' | 0.126 | - | - | - | - | - |
| Baseline: random grade at training class frequencies | 0.248 (0.226-0.268 over 1000 draws) | - | - | - | - | - |

Macro-F1 is scored on test nights; training class frequencies [0.2, 0.308, 0.225, 0.267] (clean, mild, moderate, severe), so the training majority class is 'mild'.

### Out-of-distribution stress tests (same thresholds)

| condition | detector | false alarms (95% CI) | moderate | severe |
|---|---|---|---|---|
| Held-out test (different unit map, 2022-23 weeks) | Active test 4.0 L/s, z-score rule (no ML) | 3.9% (1.2-6.9%) | 49.3% | 98.1% |
| Held-out test (different unit map, 2022-23 weeks) | Active test 4.0 L/s, gradient boosting | 0.6% (0.0-1.8%) | 30.0% | 95.1% |
| Held-out test (different unit map, 2022-23 weeks) | Active test 2.5 L/s, z-score rule (no ML) | 17.9% (12.5-23.5%) | 31.5% | 89.4% |
| Held-out test (different unit map, 2022-23 weeks) | Passive 24 h, z-score rule (no ML) | 8.6% (4.8-12.8%) | 10.2% | 8.8% |
| Held-out test (different unit map, 2022-23 weeks) | Passive 24 h, gradient boosting | 4.5% (2.4-7.1%) | 3.8% | 4.6% |
| Held-out test (different unit map, 2022-23 weeks) | BMS low-pressure alarm at zone tops (baseline) | 1.8% (0.3-3.9%) | 1.7% | 1.8% |
| Stress: sensor noise x2 | Active test 4.0 L/s, z-score rule (no ML) | 54.2% (47.3-60.7%) | 73.8% | 98.9% |
| Stress: sensor noise x2 | Active test 4.0 L/s, gradient boosting | 23.8% (17.3-30.7%) | 49.6% | 96.3% |
| Stress: sensor noise x2 | Active test 2.5 L/s, z-score rule (no ML) | 79.8% (71.7-87.2%) | 84.5% | 97.0% |
| Stress: sensor noise x2 | Passive 24 h, z-score rule (no ML) | 59.5% (54.2-64.3%) | 67.6% | 65.4% |
| Stress: sensor noise x2 | Passive 24 h, gradient boosting | 22.6% (18.1-28.0%) | 25.9% | 24.0% |
| Stress: sensor noise x2 | BMS low-pressure alarm at zone tops (baseline) | 6.0% (3.3-8.9%) | 6.4% | 6.3% |
| Check: constant +0.3 m offset on one pressure sensor (cancels in the active test) | Active test 4.0 L/s, z-score rule (no ML) | 3.9% (1.2-6.9%) | 49.3% | 98.1% |
| Check: constant +0.3 m offset on one pressure sensor (cancels in the active test) | Active test 4.0 L/s, gradient boosting | 0.6% (0.0-1.8%) | 30.0% | 95.1% |
| Check: constant +0.3 m offset on one pressure sensor (cancels in the active test) | Active test 2.5 L/s, z-score rule (no ML) | 17.9% (12.5-23.5%) | 31.5% | 89.4% |
| Check: constant +0.3 m offset on one pressure sensor (cancels in the active test) | Passive 24 h, z-score rule (no ML) | 67.0% (52.1-79.8%) | 60.9% | 61.9% |
| Check: constant +0.3 m offset on one pressure sensor (cancels in the active test) | Passive 24 h, gradient boosting | 13.7% (6.0-22.9%) | 14.3% | 14.1% |
| Check: constant +0.3 m offset on one pressure sensor (cancels in the active test) | BMS low-pressure alarm at zone tops (baseline) | 1.5% (0.3-3.0%) | 1.5% | 1.8% |
| Stress: pipes aged since commissioning (C 130 -> 110) | Active test 4.0 L/s, z-score rule (no ML) | 5.1% (1.8-8.9%) | 60.3% | 100.0% |
| Stress: pipes aged since commissioning (C 130 -> 110) | Active test 4.0 L/s, gradient boosting | 2.1% (0.0-4.8%) | 36.4% | 98.4% |
| Stress: pipes aged since commissioning (C 130 -> 110) | Active test 2.5 L/s, z-score rule (no ML) | 23.8% (18.5-29.8%) | 36.4% | 91.4% |
| Stress: pipes aged since commissioning (C 130 -> 110) | Passive 24 h, z-score rule (no ML) | 6.5% (3.3-10.1%) | 7.0% | 7.6% |
| Stress: pipes aged since commissioning (C 130 -> 110) | Passive 24 h, gradient boosting | 0.9% (0.0-2.4%) | 1.7% | 4.2% |
| Stress: pipes aged since commissioning (C 130 -> 110) | BMS low-pressure alarm at zone tops (baseline) | 1.2% (0.0-3.0%) | 0.9% | 1.4% |
| Stress: LA-like busier tower (demand x2.5) | Active test 4.0 L/s, z-score rule (no ML) | 4.5% (1.8-7.7%) | 53.9% | 98.1% |
| Stress: LA-like busier tower (demand x2.5) | Active test 4.0 L/s, gradient boosting | 4.5% (2.1-7.4%) | 39.9% | 95.6% |
| Stress: LA-like busier tower (demand x2.5) | Active test 2.5 L/s, z-score rule (no ML) | 11.0% (6.8-15.5%) | 23.0% | 87.1% |
| Stress: LA-like busier tower (demand x2.5) | Passive 24 h, z-score rule (no ML) | 5.4% (2.4-8.6%) | 6.4% | 8.8% |
| Stress: LA-like busier tower (demand x2.5) | Passive 24 h, gradient boosting | 13.1% (6.5-20.5%) | 12.0% | 8.3% |
| Stress: LA-like busier tower (demand x2.5) | BMS low-pressure alarm at zone tops (baseline) | 2.4% (0.6-4.5%) | 4.4% | 4.2% |

### Commissioning sensitivity (test building reference redrawn with new noise)

| detector | true state | median | min | max | draws |
|---|---|---|---|---|---|
| Active test 4.0 L/s, z-score rule (no ML) | clean | 5.8% | 2.4% | 9.5% | 20 |
| Active test 4.0 L/s, z-score rule (no ML) | moderate | 53.9% | 48.1% | 57.7% | 20 |
| Active test 4.0 L/s, z-score rule (no ML) | severe | 97.9% | 97.9% | 98.1% | 20 |
| Active test 4.0 L/s, gradient boosting | clean | 3.6% | 0.6% | 7.1% | 20 |
| Active test 4.0 L/s, gradient boosting | moderate | 37.5% | 30.0% | 41.7% | 20 |
| Active test 4.0 L/s, gradient boosting | severe | 95.3% | 94.4% | 96.5% | 20 |
| Active test 2.5 L/s, z-score rule (no ML) | clean | 9.8% | 5.7% | 14.0% | 20 |
| Active test 2.5 L/s, z-score rule (no ML) | moderate | 21.0% | 14.3% | 27.7% | 20 |
| Active test 2.5 L/s, z-score rule (no ML) | severe | 88.0% | 84.5% | 91.2% | 20 |
| Active test 2.5 L/s, gradient boosting | clean | 11.6% | 5.1% | 21.4% | 20 |
| Active test 2.5 L/s, gradient boosting | moderate | 21.3% | 11.7% | 27.1% | 20 |
| Active test 2.5 L/s, gradient boosting | severe | 83.6% | 78.5% | 86.1% | 20 |

### Moderate-or-severe clogs flagged, by location (held-out test)

| location | Active test 4.0 L/s, z-score rule (no ML) | Active test 4.0 L/s, gradient boosting | Active test 2.5 L/s, gradient boosting | scenarios |
|---|---|---|---|---|
| Low zone riser F1-F6 | 81.0% | 76.2% | 83.3% | 18 |
| Low zone riser F6-F11 | 73.9% | 66.4% | 73.9% | 17 |
| Mid zone riser F12-F17 | 86.5% | 79.4% | 73.8% | 18 |
| Mid zone riser F17-F22 | 89.9% | 78.2% | 74.8% | 17 |
| High zone riser F23-F28 | 77.8% | 73.0% | 78.6% | 18 |
| High zone riser F28-F32 | 71.4% | 64.8% | 63.7% | 13 |
| Strainer at low-zone PRV (F1) | 90.8% | 77.6% | 44.9% | 14 |
| Strainer at mid-zone PRV (F12) | 63.8% | 44.8% | 47.6% | 15 |

### Drain-down test (SIMULATED drain, INJECTED orifice clogs)

Test 2.5 L/s for 60 s; level noise sd 0.005 m, logging step 0.01 m (assumptions). Evaluation draws are level-noise redraws over 3 deterministic SWMM runs per opening (base flows [0.02, 0.05, 0.1] L/s). Commissioning drain-down 89.5 s. Thresholds (p95 of clean calibration draws): {'drain_down_ratio_p95_clean': 1.2402234636871508, 'peak_ratio_p95_clean': 1.0, 'grading_bands': {'watch': 1.2, 'urgent': 2.0}}.

| opening | drain-down median (s) | never drained (share) | flagged by drain-down | flagged by peak level | graded urgent | draws |
|---|---|---|---|---|---|---|
| 1.0 | 87.5 | 0.0% | 8.3% | 0.0% | 0.0% | 60 |
| 0.8 | 82.0 | 0.0% | 8.3% | 0.0% | 0.0% | 60 |
| 0.6 | 81.0 | 0.0% | 0.0% | 0.0% | 0.0% | 60 |
| 0.5 | 90.0 | 0.0% | 8.3% | 1.7% | 0.0% | 60 |
| 0.4 | 91.5 | 0.0% | 11.7% | 0.0% | 0.0% | 60 |
| 0.3 | 98.5 | 0.0% | 30.0% | 1.7% | 0.0% | 60 |
| 0.25 | 121.5 | 0.0% | 71.7% | 0.0% | 0.0% | 60 |
| 0.2 | 178.0 | 0.0% | 100.0% | 20.0% | 48.3% | 60 |
| 0.15 | 251.0 | 0.0% | 100.0% | 86.7% | 95.0% | 60 |
| 0.12 | 357.5 | 0.0% | 100.0% | 100.0% | 100.0% | 60 |
| 0.1 | 477.0 | 0.0% | 100.0% | 100.0% | 100.0% | 60 |
| 0.08 | 766.0 | 33.3% | 100.0% | 100.0% | 100.0% | 60 |

### Bellinge July 2020 blockage (REAL, one event)

REAL (Bellinge sensor data, CC BY 4.0) - municipal combined sewer, 1 documented event, case study. Train ['2020-01-01', '2020-06-30'], held-out ['2020-07-01', '2020-10-11'] (3.38 months), documented event ['2020-07-23', '2020-07-28']. Onset 2020-07-23 18:30:00 (first 5-min step in the documented window where upstream depth exceeds its previous-24-h median by more than 0.10 m). Normal model: HistGradientBoostingRegressor(max_iter=300), out-of-fold training MAE 0.0131 m, held-out MAE (event excluded) 0.0086 m; threshold basis: quantile of the 30-min median residual on time-blocked (calendar-month) out-of-fold training residuals.

| detector | first attributable alarm (local) | minutes after onset | other held-out episodes | training-month episodes | episodes in event window before onset |
|---|---|---|---|---|---|
| paired rule | 2020-07-23 19:40:00 | 70.0 | 0 | 0 | 0 |
| upstream residual only | 2020-07-23 18:50:00 | 20.0 | 0 | 8 | 0 |
| downstream drop only | 2020-07-23 19:40:00 | 70.0 | 73 | 24 | 1 (first 2020-07-23 02:15:00), not attributable |
| fixed level > 1.000 m (1.0 m) | 2020-07-23 19:05:00 | 35.0 | 3 | 22 | 0 |
| fixed level > 1.102 m (train p99) | 2020-07-23 19:10:00 | 40.0 | 3 | 19 | 0 |
| fixed level > 1.131 m (train p99.5) | 2020-07-23 19:15:00 | 45.0 | 3 | 15 | 0 |
| fixed level > 1.151 m (train p99.9) | 2020-07-25 19:05:00 | 2915.0 | 2 | 6 | 0 |

An episode inside the documented dates counts as a detection only if it starts no more than 60 min before the visible onset; earlier ones are added to the other held-out episodes.

Parameter sweep of the paired rule: 45 of 45 settings detected the event; first alarms 2020-07-23 19:15:00 to 2020-07-23 21:20:00; other held-out episodes 0-0.

### Proposed check calendar (as of 2026-09-26; SYNTHETIC demo asset register; strainer and drain-down readings SIMULATED)

| next check | status | asset | why | who | rules | input |
|---|---|---|---|---|---|---|
| 2026-05-12 | overdue | SB-B: Stack B base cleanout (serves F2-F16) | Base 365 d / risk x4.00 = 91 d (consequence x1.36 (15 floors drain or feed through it); history x2 (1 backup(s) in 12 months); nightly drain-down test ratio 1.99 (watch band)) | Drain contractor (CCTV camera, jetting if needed) | CAMERA_BASE_INTERVAL, PERFORMANCE_HISTORY, DRAIN_RATIO_BANDS | SIMULATED drain-down test (partial clog, orifice opening 0.2) |
| 2026-09-27 | due within 7 days | GT-1: Grease trap under ground-floor bar sink | Grease traps are cleaned and visually inspected daily. | Kitchen staff (daily clean and visual inspection) | GREASE_TRAP_DAILY | SYNTHETIC |
| 2026-09-27 | due within 7 days | BD-1: Building drain main cleanout | Backup on 2026-09-25: camera inspection within 48 hours. | Drain contractor (CCTV camera, jetting if needed) | CAMERA_BASE_INTERVAL, PERFORMANCE_HISTORY, CCTV_48H_AFTER_OVERFLOW | SYNTHETIC backup ticket |
| 2026-10-03 | due within 7 days | STR-M: Strainer at mid-zone PRV station (F12) | Nightly flow test alarmed on 4 of 7 nights on this strainer, meeting the work-order rule of at least 2 alarms in 3 consecutive nights (extra head loss about 1.08 m at 4 L/s): inspect within 7 days. | Building engineer (isolate the PRV station, open and clean the strainer) | UPC_608_2_PRV_80PSI, STRAINER_BASE_INTERVAL, PERSISTENCE_2_OF_3 | SIMULATED nightly-test readings (test scenario 511, true K 34) |
| 2026-10-06 | due within 30 days | GI-1: Grease interceptor, ground-floor restaurant (FSE permit on file) | FOG + solids 19% rising 3.3 points/week; projected to reach 25% on 2026-10-09; pump out 3 days before. | Licensed grease hauler, logged in the FSE cleaning logbook | FOG_25PCT, FOG_PROGRAM | SYNTHETIC |
| 2026-10-09 | due within 30 days | SB-A: Stack A base cleanout (serves F2-F32) | Base 365 d / risk x2.82 = 130 d (consequence x2.82 (31 floors drain or feed through it)) | Drain contractor (CCTV camera, jetting if needed) | CAMERA_BASE_INTERVAL, PERFORMANCE_HISTORY, DRAIN_RATIO_BANDS | SIMULATED drain-down test (clean drain, opening 1.0) |
| 2026-10-20 | due within 30 days | BF-1: Reduced-pressure backflow assembly, domestic water service | Annual test: last tested 2025-10-20; regulatory maximum 365 days. | Certified Backflow Prevention Assembly Tester licensed by LA County Department of Public Health | BACKFLOW_ANNUAL | SYNTHETIC |
| 2026-10-28 | scheduled | STR-L: Strainer at low-zone PRV station (F1) | No persistent nightly-test alarm (alarmed on 0 of 7 nights); base interval 180 days from 2026-05-01. | Building engineer (isolate the PRV station, open and clean the strainer) | UPC_608_2_PRV_80PSI, STRAINER_BASE_INTERVAL, PERSISTENCE_2_OF_3 | SIMULATED nightly-test readings (test scenario 482, true K 0) |

### Conclusions as computed for the page (`report.conclusions`)

- **Earliest supply-side signal** [SIMULATED] A short nightly flow test at a known flow is the signal that worked. On held-out simulated weeks the 4.0 L/s test flagged 98% of severe-clog nights and 49% of moderate-clog nights at 4% false alarms per clean night. In our simulation (10-minute readings, assumed pressure noise sd 0.15 m, apartment-only demand) passive 24-hour monitoring and a BMS low-pressure alarm did no better than their own false-alarm rate (severe: 5% and 2%): everyday flows are too small to make a clog's head loss stand out. In the stress test 'Stress: LA-like busier tower (demand x2.5)' passive (gradient boosting) flagged 8% of severe nights at 13% false alarms.
- **What machine learning adds** [SIMULATED] Detection: the plain z-score rule and gradient boosting caught moderate clogs at rates whose 95% CIs overlap (49% vs 30%, at 3.9% vs 0.6% false alarms per clean night). Grading into clean / mild / moderate / severe: gradient boosting scored higher (macro-F1 0.58 vs 0.49). Naive grading baselines: always 'mild' (the training majority) 0.10; always 'clean' 0.08, always 'moderate' 0.08, always 'severe' 0.13; a random grade drawn with the training class frequencies 0.25. Locating a moderate clog to one of 8 places: the z-score rule's largest-deviation segment and the gradient-boosting localiser were about the same (73% vs 70%, overlapping 95% CIs; chance 12%). No method flagged mild clogs (K below 10) much more often than clean weeks (at most 3 percentage points above its own false-alarm rate).
- **Test flow** [SIMULATED] Head loss grows with flow squared, so the stack-safe 2.5 L/s test is weaker: 31% of moderate clogs at 18% false alarms, against 49% at 4% for 4.0 L/s. A draw above 4.0 L/s should go to a break tank, not into a DN100 stack.
- **What breaks it (stress tests)** [SIMULATED] For the 4.0 L/s test, twice the sensor noise pushed its false alarms from 4% to 54% per clean night; pipes aged since commissioning barely moved its false alarms (4% to 5% per clean night), while the 2.5 L/s test went from 18% to 24%. A constant offset on one pressure sensor cancels in the test's before/after jump by construction (false alarms 4%, identical to 4% without it), so that row checks the algebra rather than stressing the detector; a drifting offset was not tested. The passive z-score rule, which has no such cancellation, jumped to 67%. Redrawing the one-week commissioning reference 20 times moved the 4.0 L/s false-alarm rate between 2% and 10%. So: recommission after pipe or sensor work; a longer commissioning window may help but was not tested.
- **Earliest drain-side signal** [SIMULATED] In the simulated drain, drain-down time after a known 150 L discharge flagged at least 90% of tests once the clog left 20% of the pipe open; peak level needed 12% open. At 50% open the model drain behaved like a clean one (flagged 8% vs 8% for a clean drain), so in this model the test cannot see a clog that leaves half the pipe open.
- **Real blockage (Bellinge, July 2020)** [REAL] On the one documented real blockage, the paired rule (upstream above normal AND downstream starved) alarmed 70 minutes after the visible onset with 0 other alarm episodes in 3.4 held-out months and 0 in the training months. The upstream level checked against its learned normal alone (residual only) alarmed 20 minutes after onset with 0 other held-out episodes and 8 in the training months (out-of-fold). The fastest fixed high-level alarm (1.0 m) was 35 minutes after onset but raised 3 other held-out episodes and 22 in the training months. 45 of 45 paired-rule settings caught it, with 0 other held-out episodes. The learned-normal signals won on false alarms. One event in a municipal combined sewer: a case study, not an accuracy.
- **Where to put sensors** [SIMULATED + design] Supply: a clamp-on flow meter on each zone header; pressure at the booster, at each PRV station's strainer inlet and outlet, and at the header, middle and top floor of every zone; one test valve at each zone top. With this layout the 4.0 L/s test flagged 64%-91% of moderate-or-severe clog nights at each location (lowest: Strainer at mid-zone PRV (F12); highest: Strainer at low-zone PRV (F1); simulated, per night). Drains: a level sensor at each stack base and main cleanout (for the drain-down test), a FOG probe at the grease interceptor, and a downstream partner gauge where a pair is possible.
- **How often to check** [rules + SYNTHETIC register] Regulatory maximums first: backflow assemblies every 365 days by an LA County-licensed tester; grease interceptors before FOG and solids reach 25% of the liquid depth; grease traps daily. Supply risers: the nightly test, with a work order only after 2 alarms in 3 nights. Everything else: a base interval shortened by consequence, backups and test results, as LA Sanitation does for city sewers. In the demo register, 4 of 8 checks fall due within 7 days of 2026-09-26.
<!-- clog:results:end -->

## 5. Conclusions

These follow from the tables above. The page computes the same statements from the same artifacts
(`report.conclusions`), so a rerun that changes a number changes the wording.

1. **Which signal catches a supply clog earliest: test at a known flow, do not just listen.** In our simulation the
   nightly active test was the only supply-side signal clearly above its own false-alarm rate. Passive 24-hour
   features and a BMS low-pressure alarm stayed near their false-alarm rate, even in the busier-tower stress test.
   This holds under our assumptions: 10-minute readings, 0.15 m pressure noise, and apartment-only demand. Faster
   logging or a busier real tower could change it.
2. **Machine learning helps with grading, not with detection.** With the 4.0 L/s test, the plain z-score rule
   flagged more moderate-clog nights than gradient boosting in point estimate (at a higher false-alarm rate), but the
   week-cluster 95% intervals overlap, so neither is clearly better at detection. The rule's largest-deviation
   segment and the gradient-boosting localiser located moderate clogs about equally well (overlapping intervals).
   Gradient boosting scored higher at grading severity. With the 2.5 L/s test the two were close on grading and both had high false-alarm
   rates on the test map. Mild clogs were not clearly separable from clean weeks by any method. The active-test
   methods beat every naive grading baseline in section 4 (the training-majority class is "mild", not "clean", and a
   random grade drawn at the training class frequencies is the strongest naive baseline). The passive detectors
   scored below that random baseline and had no ordinal skill (QWK near zero). Where two methods' 95% intervals
   overlap (for example, locating moderate clogs) we call them about the same.
3. **Test flow matters.** Head loss grows with flow squared, so the lower, stack-safe test flow was clearly weaker. A
   draw above the DN100 stack limit should go to a break tank rather than into the stack.
4. **What breaks it.** Doubled sensor noise raised false alarms sharply for every active and passive detector.
   Pipes aged since commissioning moved the 4.0 L/s test's false alarms only a little, and the 2.5 L/s test's more.
   A constant sensor offset cancels in the before/after jump of the active test, but it wrecks the passive z-score
   rule. The single-week commissioning reference is itself noisy: redrawing it moves the false-alarm rate. So
   recommission after any pipe or sensor work.
5. **Where to put sensors.** Supply side: a clamp-on flow meter on each zone header; pressure at the booster, at each
   PRV station's strainer inlet and outlet, and at the header, middle and top floor of every zone; and one test valve
   at each zone top. With that layout the 4.0 L/s test flagged moderate-or-severe clog nights at every location,
   at the per-night rates in the by-location table (simulated). Drain side: a level sensor at each stack base and main cleanout for the drain-down test, a FOG
   probe at the grease interceptor, and a downstream partner gauge wherever a pair is possible.
6. **Drains.** In the simulated drain, drain-down time after a known discharge flagged clogs before peak level did. A
   clog leaving half the pipe open was indistinguishable from clean in this model. On the one real blockage
   (Bellinge), the two signals built on a learned normal level (residual only, and the paired rule) alarmed the same
   evening as the visible onset with no other held-out alarm episodes. The fixed high-level thresholds alarmed in the
   same window (except the strictest one, which was days late) but raised other held-out alarms. The paired rule
   also had no alarm episodes in the training months; the residual-only detector had some (out-of-fold). A
   downstream-drop-only rule fires almost every night, so an episode it started before the visible onset is not
   credited as a detection. This is one event in a municipal sewer: a case study, not an accuracy.
7. **How often to check.** Regulatory maximums come first: backflow annually by a licensed tester, grease
   interceptors before the 25% FOG-plus-solids limit, grease traps daily. Supply risers get the nightly test, with a
   work order after 2 alarms in 3 nights. Everything else runs on a base interval shortened by consequence, backups
   and test results, as LA Sanitation does for city sewers. The calendar is advisory, and a person approves each
   row.

## 6. Limits

- The riser, the clogs, the geometry and the pressure noise are simulated. K bands are not calibrated to any measured
  blockage state. Train and test share the simulator and riser geometry; the test "building" is the same HSB
  apartments on a different apartment-to-unit map. Only that map, the weeks, clog draws and noise differ.
- CIs use a two-stage bootstrap over the test demand weeks and the scenarios within them. With only a handful of
  test weeks (listed in section 4) the intervals are coarse, and they do not cover variation in riser geometry,
  which was never varied.
- The constant-offset row checks that a constant offset cancels in the active test (its active-test rows equal the
  base run by construction). A drifting sensor offset was not tested.
- The active test is proposed as a 60-120 s hold, but EPANET solves only the settled flow at one 10-minute step; the
  transient after the valve opens is not simulated.
- Weeks where EPANET fails fall back to WNTR's own solver. Which weeks fall back can differ between reruns (see
  engine counts in section 4); the engine cross-check bounds the pressure difference between the two solvers.
- HSB demand is Swedish apartment use without shared facilities. The busier-tower stress test stands in for an LA
  tower; it is not LA data.
- Thresholds were set for a 5% false-alarm target on training nights but did not transfer exactly to the new
  building; see the clean-night rates in the tables.
- The drain model has one geometry. The per-event drain classifier, the WEUSEDTO disaggregation and a clog-ramp
  detection-delay experiment were descoped and not run.
- Bellinge: one event; a municipal combined-sewer throttle pipe, not a building drain. The paired-rule parameters were
  chosen after the event was known; the sweep shows how sensitive the result is to them. The G71F04R scaling change
  in 2020 covers the whole analysed window. Rain is not used (the rain gauges are CC BY-NC 4.0). See `caveats` in
  `bellinge_case.json`.
- The demo asset register (dates, backups, FOG readings) is SYNTHETIC.

## 7. How to rerun

```bash
# Git Bash, from the repo root; about 12-15 minutes on a laptop CPU.
bash scripts/clog_run_all.sh > data/raw/clog/run_all.log 2>&1
C:/Users/HP/miniconda3/envs/origin_hack/python.exe scripts/clog_make_fixture.py   # refresh tests/fixtures/clog/
C:/Users/HP/miniconda3/envs/origin_hack/python.exe scripts/clog_doc_tables.py     # refresh section 4
C:/Users/HP/miniconda3/envs/origin_hack/python.exe -m pytest tests/test_clog_*.py tests/test_site_pipes.py -q
E:/conda_envs/cerebro_ml/python.exe -m pytest tests/test_clog_sims.py -q          # WNTR/pyswmm checks
```

Raw inputs live in `data/raw/clog/` (git-ignored). `fetch_clog_data.py` copies them from the research scratch folder
or downloads them, and records their sha256 in `eval/clog/data_manifest.json`.

## Sources (accessed 2026-09-26)

1. HSB Living Lab fixture-level household water consumption (2019-2023), Zenodo 22076411, CC BY 4.0. https://zenodo.org/records/22076411
2. Pedersen et al. 2021, The Bellinge data set, Earth System Science Data 13:4779, CC BY 4.0. https://essd.copernicus.org/articles/13/4779/2021/
3. Dataset for Bellinge (DTU collection 5029124), 2_cleaned_data and 2_Sensordata_v2.pdf, CC BY 4.0. https://doi.org/10.11583/DTU.c.5029124
4. WNTR 1.5.0, US EPA Water Network Tool for Resilience, Revised BSD. https://usepa.github.io/WNTR/
5. EPANET 2.2 manual, ch. 3 The Network Model. https://epanet-manual.readthedocs.io/en/latest/3_network_model.html
6. pyswmm 2.1.0 / swmm-toolkit 0.17.0. https://pypi.org/project/pyswmm/
7. LADWP Rule 16-D Protection of Public Water Supply, 9.1-9.2. https://www.ladwp.com/sites/default/files/2025-04/LADWP%20Rule%2016-D%20REVISED%20July_15_2015.pdf
8. LA Sanitation Sewer System Management Plan v3.0 (25 Jan 2019). https://planning.lacity.gov/eir/Sunset_Wilcox/deir/deir_reference_docs/water-supply/LASAN%20-%20Sewer%20System%20Management%20Plan%20Hyperion%20Sanitary%20Sewer%20System,%20January%202019.pdf
9. LA Sanitation and Environment, FOG program. https://sanitation.lacity.gov/programs/fats-oils-and-grease-fog
10. Section 608.2 Excessive Water Pressure (Hawaii Plumbing Code 2021, UPC-based, UpCodes). https://up.codes/s/excessive-water-pressure
11. Lansing 2023, single-stack drainage design standards review, CIB W062 symposium. https://www.irbnet.de/daten/iconda/CIB_DC39171.pdf
12. AW-Lake CUTT clamp-on ultrasonic flow meter (vendor page). https://aw-lake.com/product/clamp-on-ultrasonic-flow-meter/
13. Rosin, Kapelan, Keedwell, Romano 2022, J. Hydroinformatics 24(2) (abstract only). https://doi.org/10.2166/hydro.2022.036
14. Kelly et al. 2024, The Reflected Wave Technique for blockages in sewers and drains, Buildings 14(10):3138 (abstract only). https://doi.org/10.3390/buildings14103138
15. Brunone et al. 2023, Detection of partial blockages in pressurized pipes by transient tests: a review, Fluids 8(1):19 (abstract only). https://doi.org/10.3390/fluids8010019
16. NASSCO, PACP codes and automated defect recognition. https://nassco.org/resource/pacp%EF%B8%8F-codes-and-automated-defect-recognition/
17. SmartCover Systems, system cleaning. https://smartcoversystems.com/system-cleaning/
18. Phyn technology page. https://phyn.com/pages/technology
19. Flo by Moen Smart Water Monitor. https://shop.moen.com/pages/flo-smart-water-monitor
