# 13. Common-area energy: code-bounded smart switching and a year-round LA plan

Key: `energy` (Ask 3). Written 2026-09-26. Page: `app/site_pages/energy.py`. Artifacts: `eval/energy/*.json`, `models/energy/m1_presence_hgb.joblib`.

## Question

The user asked: "get a ml model developed for Energy consumption smart switching for common areas and how we can build the mitigation for the needs year around needs."

We read this as three questions for a Los Angeles high-rise:

1. Can a model switch corridor, stairwell, lobby, garage, restroom and amenity-room lighting to save energy without breaking the fire and energy codes?
2. How good are occupancy and garage-load models on real public data, compared with the naive rules a building already uses?
3. What should a building manager do in each month of the year, given LA weather, daylight, tariffs and demand-response (DR) seasons?

## What we found

**Codes set hard limits, and they decide most of the design.**

- Title 24 Part 6 (2022) section 130.1 [8]:
  - Corridors and stairwells must cut lighting power by at least 50% when vacant, with sensors that cover every path of egress (130.1(c)6C).
  - Parking garages need a control step between 20% and 50% of design power, in zones of 500 W or less (130.1(c)7B).
  - Restrooms go fully off within 20 min (130.1(c)5).
  - Up to 0.1 W/ft2 may stay on continuously in areas designated as means of egress (Exception 3 to 130.1(c)1).
  - The 2025 code (in force from 2026-01-01) keeps these rules and adds demand-responsive lighting (at least a 15% cut for 4,000 W or more of general lighting) [9]. DR controls must respond to OpenADR 2.0b [15].
- ASHRAE 90.1-2019 [10]: partial-off of at least 50% within 20 min. Garages cut at least 50% after 10 min without activity, in zones of 3,600 ft2 or less.
- Life-safety floors [11][12]. These are the rules the AI must never cross:
  - Means of egress stay at 1 fc (11 lux) or more whenever the space is occupied (CFC 1008.2.1).
  - Stairways need 10 fc while in use (CFC 1008.2.1, NFPA 101 7.8.1.3 for new stairs). The first build spec missed this; the verifier added it.
  - Motion switches are allowed on egress routes only if they are fail-safe (lights ON when the sensor fails), hold for at least 15 min, and respond to any movement (NFPA 101 7.8.1.2.2).
  - Emergency lighting lasts 90 min (60 min for some existing buildings, CFC 1104.5.1).
  - UL 924 bypass relays force emergency lights on at loss of power whatever the controls do [37].
- HVAC:
  - Title 24 120.2(e)3 occupied-standby [14]: +2 F cooling and -2 F heating setpoints (0.5 F for multi-zone DDC). Ventilation may stay off only while the space is between the active setpoints, and the rule only covers spaces with occupant-sensor ventilation control.
  - Garage ventilation 120.6(c) [13]: on a CO-sensor failure, the fans return to design ventilation and an alarm is raised. We copy this fail-safe pattern for lighting.

**LA cost drivers.**

- LADWP TOU [16]: High Peak runs Mon-Fri 13:00-16:59. Low Peak runs 10:00-12:59 and 17:00-19:59. High season is June-September. The TOU page does not list holidays as Base, so we do not treat them as Base.
- A-2 Rate B base charges [17]. The 2026 adjustment factors [18] are left out because the page does not say which schedules they apply to, so our $ understate a real bill.
- LADWP DR [19]:
  - The season runs Jun 15 to Oct 15, with 4-hour events inside 13:00-21:00 and at most 20 events.
  - A participant must curtail at least 100 kW. Common-area lighting alone will not reach that, so it can only contribute to a building-level bid.
- SCE summer on-peak is 16:00-21:00 [20][21]. CAISO Flex Alerts usually run 16:00-21:00 [22].

**Data.** No public dataset records occupancy in high-rise corridors or stairs. The closest real data we found:

- **ROBOD** [3]: 5 rooms at NUS Singapore, 5-min data, presence plus recorded lighting kWh. CC BY 4.0.
  - It has no motion-sensor column.
  - How its ground truth was collected is not documented.
- **UCI 357** [1] (CC BY 4.0). Its "test1" file comes before the training period, so only test2 is a forward-in-time test.
- **UCI 864** [7]: the only candidate with real PIR readings next to ground truth. CC BY 4.0.
- **BDG2** [4]: 20 usable parking-garage meters. Licence is CC BY-SA, version ambiguous.
- **Weather and climate**:
  - NOAA 1991-2020 normals for Downtown USC and LAX [23].
  - NOAA GML solar equations for daylight [24].
  - Open-Meteo 2025 reanalysis [25][26]. We request it with `timezone=GMT` and convert in pandas, because the `America/Los_Angeles` option applies one fixed UTC-7 offset all year.

**Expected size of savings from the literature.**

- LBNL's meta-analysis puts average occupancy-control savings at 24% (38% with multiple strategies) [27].
- PNNL garage retrofits ranged from 76% extra savings to almost none, depending on commissioning [28].
- Occupancy-based HVAC may not pay back in offices [29].
- Pre-cooling can cut chiller power by 80-100% during 14:00-17:00 [30].

**Design conclusion.** ML should not be the thing that switches common-area lights off:

- Code-required motion sensors, hold timers and floors do the switching.
- The ML can only add light: it can extend a hold that is already active.
- ML also forecasts load for tariff and DR planning.
- Every change is a proposal that a named person approves.

## What we built

All code is in `src/cascade/building/energy/`, run by `scripts/train_energy_models.py`.

| Module | What it does |
|---|---|
| `common_area_rules.json`, `rules.py` | Rule table per zone type with code basis and tags (PUBLIC / PUBLIC, secondary / team-proposed, validate). It holds the life-safety floors: 1 fc egress, 10 fc stair in use, a fail-safe hold of at least 15 min, sensor fault means full ON, 90-min emergency lighting, UL 924 outside AI control, and 0.1 W/ft2 egress. It also holds zone rules (corridor, stairwell, lobby, garage, restroom, amenity), DR, HVAC standby and garage ventilation. It lives in the energy package, not `src/cascade/rubrics/`, so it does not change the grading fingerprint. |
| `policy.py` | Deterministic lighting state machine: level = max(code floor, target). **Sensor+ML (recommended)** lets M1 only extend an active hold. It cannot switch a zone on or off. A sensor fault gives full ON, and DR trims skip egress zones. A proposal is checked against the code bounds before it exists. The append-only `ProposalLog` allows only pending_approval -> approved / rejected by a named reviewer. |
| `occupancy.py` | **M1** presence-now classifier (HistGradientBoosting on CO2, CO2 slope, sound, VOC, RH, temperature, Wi-Fi count, time). Lighting, lux, plug, fan, HVAC and occupant count are excluded as leakage. **M2** 1-h-ahead presence forecaster in an oracle variant (uses true presence at t) and a deployable variant (uses the M1 probability, out-of-fold on training days). Also the UCI 357 leakage check and UCI 864 PIR miss and false-trigger rates. |
| `forecast.py` | **M3** day-ahead garage load forecaster (issued 00:00 local, all lags of 24 h or more) on BDG2 parking meters. Baselines are lag-24 and lag-168, with a weather ablation: oracle same-hour temperature, 24-h-lagged temperature, no weather. There is an optional Chronos-Bolt zero-shot comparator. |
| `simulate.py` | **(A) REAL replay** on ROBOD held-out days: policy kWh = sum(recorded 5-min lighting kWh x level). A policy can only remove recorded use, so savings are "recoverable kWh vs as-operated". Motion-sensor misses are INJECTED at the UCI 864 rate. **(B) SEMI-SYNTHETIC tower year** for 2025 in America/Los_Angeles: an assumed inventory, times ROBOD test-day blocks of (true presence, M1 probability) resampled jointly so ML errors carry over, times hypothetical DR days picked from 2025 reanalysis heat. |
| `inventory.py` | Common-area zones for the synthetic tower, with [ASSUMPTION] W, ft2 and design fc. The shared tower has no such zones and its `Building.tz` is UTC. |
| `tariff.py` | LADWP A-2 Rate B periods and charges, SCE windows, LADWP DR, Flex Alert. |
| `calendar_la.py` | 12-month LA calendar: NOAA normals, GML day length and sunset, LADWP / SCE / DR seasons, federal holidays, DST, 2025 reanalysis temperature, month actions, weekday mode heatmap and the seasonal plan. All hour windows and thresholds in the text are read from the tariff and rule tables. |
| `data.py` | Downloads with a sha256 manifest (ROBOD by GET, because the presigned S3 URL refuses HEAD), loaders, NOAA parsing of padded strings, and Open-Meteo GMT -> local conversion. |

The page shows:

- KPI tiles
- The policy comparison on real rooms, with under-lit share
- A sensor-degradation what-if
- The model card with every baseline and a day-bootstrap CI
- The garage profile and a forecast example
- The year-round calendar heatmap and month table
- "What the building manager does each season"
- The pending-approval queue
- An engineers expander
- Sources and licences

## Measured results

Every number below is copied from `eval/energy/*.json`, written by the run of `scripts/train_energy_models.py` at 2026-09-26T22:25:15Z (manifest runtime 397 s) plus the Chronos step. Labels: **REAL** = public measured data; **INJECTED** = errors added on purpose at a measured rate; **SIMULATED** = hypothetical events; **SEMI-SYNTHETIC** = assumed building built around real traces.

### M1: is the space occupied now? (REAL, ROBOD, per room: first 70% of days train, last 30% test)

Metric: F1 for the occupied class at a fixed 0.5 threshold. Baselines are fitted on the training days only:
- majority class
- 48-bin schedule (weekday/weekend x hour)
- 168-bin hour-of-week schedule

The CI is a 95% bootstrap over whole test days (1,000 resamples) of the F1 difference, model minus best baseline.

| Room | Test days | n test (5-min) | Occupied (positives, prevalence) | M1 F1 | M1 AUC | Best baseline | Baseline F1 | 95% CI of difference | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 Lecture | 9 | 2,592 | 55 (2.1%) | 0.072 | 0.734 | schedule_168 | 0.065 | -0.012 to +0.075 | no clear difference |
| 2 Lecture | 9 | 2,592 | 555 (21.4%) | 0.580 | 0.846 | schedule_168 | 0.491 | +0.018 to +0.156 | model better |
| 3 Office | 9 | 2,592 | 789 (30.4%) | 0.803 | 0.952 | schedule_48 | 0.793 | -0.013 to +0.028 | no clear difference |
| 4 Office | 15 | 4,320 | 2,522 (58.4%) | 0.911 | 0.924 | schedule_168 | 0.910 | -0.011 to +0.013 | no clear difference |
| 5 Library | 15 | 4,320 | 1,535 (35.5%) | 0.818 | 0.906 | schedule_48 | 0.819 | -0.043 to +0.033 | no clear difference |

- M1 beats the best schedule by a clear margin only in Room 2. In the other four rooms it ties within noise, and in Room 5 its point estimate is lower.
- Room 1 was occupied only 2.1% of test time, so every score there is unstable.
- Without Wi-Fi, M1's F1 is 0.057 / 0.404 / 0.796 / 0.910 / 0.773 for Rooms 1-5. Wi-Fi device count carries much of the signal in the lecture rooms.
- Leave-one-room-out (train on four rooms, test on all days of the fifth; the schedules are pooled from the four training rooms):

| Test room | M1 | Best pooled schedule |
|---|---|---|
| 1 | 0.649 | 0.507 |
| 2 | 0.710 | 0.672 |
| 3 | 0.778 | 0.826 |
| 4 | 0.785 | 0.756 |
| 5 | 0.650 | 0.906 |

M1 wins in 3 of 5 rooms and loses badly on the library (Room 5). It does not transfer reliably to a new space type.

### M2: will the space be occupied in 1 hour? (REAL, ROBOD, same split)

The **deployable** variant uses the M1 probability now. The **oracle** variant uses true presence now, which no deployed system has.

| Room | Deployable F1 | Best deployable baseline | 95% CI | Verdict | Oracle F1 | Persistence (oracle) F1 | 95% CI | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.086 | schedule_168 0.065 | -0.001 to +0.084 | no clear difference | 0.138 | 0.582 | -0.567 to +0.000 | no clear difference |
| 2 | 0.517 | schedule_168 0.491 | -0.054 to +0.106 | no clear difference | 0.740 | 0.814 | -0.149 to -0.033 | baseline better |
| 3 | 0.793 | schedule_48 0.793 | -0.019 to +0.021 | no clear difference | 0.815 | 0.853 | -0.167 to +0.034 | no clear difference |
| 4 | 0.918 | schedule_48 0.923 | -0.015 to +0.003 | no clear difference | 0.931 | 0.941 | -0.086 to +0.030 | no clear difference |
| 5 | 0.661 | schedule_48 0.819 | -0.281 to -0.063 | baseline better | 0.889 | 0.884 | -0.066 to +0.045 | no clear difference |

- The deployable M2 is never clearly better than a schedule, and it is clearly worse in Room 5.
- Oracle persistence has the higher point estimate in 4 of 5 rooms, which matches the research scratch run.
- **M2 is not used for switching.** At most it is a planning input.

### M3: garage load for tomorrow (REAL, BDG2 parking meters, train 2016 / test 2017)

The forecast is issued at 00:00 local for the next 24 h. The test set is 20 meters and 174,258 meter-hours. Three meters were skipped for coverage below 0.8: Panther_parking_Jody 0.759, Bear_parking_Bridget 0.67 and Hog_parking_Joan 0.0. Two of the 20 are US/Pacific (Bear site). Metric: CV(RMSE), lower is better [38].

| Forecaster | Median CV(RMSE) | Median NMBE | Meters beating lag-168 | Meters beating lag-24 | Meters beating best naive |
|---|---|---|---|---|---|
| lag-168 (same hour last week) | 0.119 | 0.0003 | - | - | - |
| lag-24 (same hour yesterday) | 0.096 | 0.00004 | - | - | - |
| HGB, oracle weather (observed same-hour temperature) | 0.091 | 0.0007 | 19 | 16 | 16 |
| HGB, 24 h-lagged temperature | 0.093 | -0.0026 | 19 | 15 | 15 |
| **HGB, no weather (headline, deployable)** | **0.091** | -0.0015 | 19 | 15 | 15 |
| Chronos-Bolt-small zero-shot (Apache-2.0, 512 h context, no training on these meters) | 0.074 | - | - | - | 19 |

- Against the best naive baseline, the headline HGB loses on 5 meters:

| Meter | HGB CV(RMSE) | Best naive CV(RMSE) |
|---|---|---|
| Panther_parking_Mellissa | 0.092 | 0.089 |
| Panther_parking_Stanley | 0.040 | 0.033 |
| Fox_parking_Tommie | 0.078 | 0.044 |
| Hog_parking_Jean | 0.253 | 0.229 |
| Hog_parking_Shannon | 0.241 | 0.227 |

- Weather adds almost nothing: 0.091 with oracle weather against 0.091 without.
- **The zero-shot foundation model beats our trained HGB on 18 of 20 meters** (median 0.074 vs 0.091). We did not check whether BDG2 was in its pretraining data.
- The median night/day load ratio is 1.047, so garages draw about as much at night as by day. These are whole-garage meters, not lighting circuits, so this is an inference.

### Supporting checks (REAL)

**UCI 357 leakage check.** Only test2 (n = 9,752) is forward in time.

| Model | F1 on test2 |
|---|---|
| Majority | 0.000 |
| Schedule_48 | 0.845 |
| Logistic regression, no Light | 0.669 |
| HGB, no Light | 0.772 |
| Logistic regression, with Light (leaky) | 0.983 |
| HGB, with Light (leaky) | 0.957 |

A model that sees the controlled lights looks excellent. Without them, both models lose to a schedule. This is why lighting and lux are banned from M1. Test1 (n = 2,665) comes before the training days and is reported only for completeness.

**UCI 864 PIR rates**, used to INJECT an imperfect motion sensor. We count 5-min windows with at least 8 samples at 30 s, where either S6 or S7 fires.
- Miss rate: 0.0052 over 192 fully occupied windows.
- False-trigger rate: 0.0106 over 846 vacant windows.

### Policy replay on real rooms (REAL + INJECTED, ROBOD held-out days, all 5 rooms pooled)

Recorded lighting on the test days was 375.2 kWh. Of that, 135.3 kWh (36.1%) was used while the room was empty. $ are LADWP A-2B base energy charges, with ROBOD clock times mapped onto LADWP periods as if local.

| Policy | Room rule: kWh | Room rule: % saved vs recorded | Room rule: occupied time under-lit | Corridor rule (50% setback): % saved |
|---|---|---|---|---|
| As operated (recorded) | 375.2 ($19.03) | 0 | 0 | 0 |
| Fixed schedule 07-22 | 310.6 | 17.22% | 6.56% | 8.61% |
| Motion sensor + 15 min hold (INJECTED misses) | 252.7 ($13.28) | 32.66% | 0.0073% | 16.33% |
| **Sensor + ML, extend-only (recommended)** | 271.3 ($14.24) | 27.69% | 0.0055% | 13.84% |
| Sensor + ML union (ML may also switch on) | 309.9 | 17.42% | 0.0018% | 8.71% |
| Ideal sensor = true presence + hold (upper bound; under-lit 0 by construction) | 247.2 | 34.12% | 0 | 17.06% |
| ML only (unsafe counterfactual) | 294.6 | 21.50% | 6.14% | 10.75% |

- With ML-only switching, the share of occupied time left under-lit (room rule) was:

| Room | Under-lit share |
|---|---|
| 1 | 0.145 |
| 2 | 0.236 |
| 3 | 0.037 |
| 4 | 0.025 |
| 5 | 0.067 |

- The hypothetical 24/7-at-p95-power case is kept only as a labelled hypothetical. It is far above what the rooms really used: for example Room 4 would use 890.1 kWh against 201.2 recorded.

### Tower year (SEMI-SYNTHETIC + INJECTED + SIMULATED; not measured in any real building)

The tower is 32 floors with 168 common-area zones and 66,880 W of assumed design lighting. The year is 2025 on a local clock at 5-min steps.

| Policy | Annual kWh | Total $ (A-2B base) | Summer high-peak kW | Occupied time under-lit | Stair minutes < 10 fc while in use | Egress < 1 fc |
|---|---|---|---|---|---|---|
| Always on (pre-controls) | 585,869 | 36,072.65 | 66.88 | 0 | 0 | 0 |
| Fixed schedule 07-22 | 445,665 | 30,786.51 | 66.88 | 6.97% | 0 | 0 |
| Motion sensor + 15 min hold | 386,841 | 27,328.45 | 62.49 | 0.0079% | 420 | 0 |
| **Sensor + ML, extend-only (recommended)** | 405,980 | 28,444.53 | 64.10 | 0.0054% | 400 | 0 |
| Sensor + ML union | 438,251 | 30,375.22 | 66.85 | 0.0024% | 235 | 0 |
| ML only (unsafe counterfactual) | 424,636 | 29,831.32 | 66.83 | 3.80% | 101,965 | 0 |

- **Recommended policy against always-on:**
  - 179,889 kWh/yr saved (30.7%)
  - $7,628/yr saved (base charges only)
  - Summer high-peak demand cut by 2.77 kW
- **Against the fixed schedule:** 39,685 kWh (8.9%) and $2,342 saved.
- **Sensor-only saves more** (34.0% vs always-on). The ML extension costs 19,139 kWh ($1,116) a year, and in return removes a small part of the under-lit time.
- **What if the sensors degrade?** Stair minutes below 10 fc while in use, by policy:

| Miss rate | Motion sensor | Sensor + ML | Union |
|---|---|---|---|
| 0.1 | 8,425 | 7,570 | 4,040 |
| 0.3 | 32,515 | 27,175 | 13,760 |

  Sensor health matters more than the ML: commissioning and fault detection are the real safety levers.
- **Demand response:** on 10 SIMULATED DR days (the hottest 2025 weekdays of the DR season, 13:00-17:00), trimming restrooms and amenity rooms by 15% sheds 1.48 kW on average (max 1.67 kW). LADWP's program needs at least 100 kW, so this is only a contribution to a building-level bid.
- **Life safety:** the 1 fc egress floor was never breached, in any deployable policy (0 violations).

### Year-round LA calendar (REAL normals + computed solar + tariff tables)

- **Climate:** annual CDD65 is 1,295.6 at Downtown USC against 720.4 at LAX. The monthly normals sum to the NOAA annual normals of 1,295.7 and 720.4, and a test checks this. 952 of 1,296 USC CDD65 fall in June-September. August is the hottest month (300.7).
- **Daylight:** day length runs from 9.9 h (Dec) to 14.41 h (Jun) on the 15th of each month. The GML equations give 14.43 h on Jun 21 and 9.88 h on Dec 21.
- **Calendar year 2027:**
  - DST changes on 2027-03-14 and 2027-11-07.
  - LADWP DR days per month: 16 (Jun), 31 (Jul), 31 (Aug), 30 (Sep), 15 (Oct).
- **Seasonal plan** (on the page, generated from these rows):
  - Winter: sunset-anchored garage and perimeter lighting, holiday setbacks.
  - Spring: re-anchor schedules after DST, April commissioning audit, May DR enrolment.
  - Summer: weekday 13:00-17:00 kW cap at $10.00/kW (vs $4.75/kW in winter), lobby pre-cooling proposals, DR playbook (15% on non-egress only), Flex Alert 16:00-21:00.
  - Autumn: DR readiness to Oct 15, DST re-anchor, year review.

## Conclusions

1. **Let code-compliant sensors do the switching and keep ML out of the off-decision.** ML-only switching left 2.5-23.6% of occupied time under-lit in real rooms. In the tower it left stairs under 10 fc for 101,965 minutes a year.
2. **The recommended policy (sensor + ML, extend-only) never went below the 1 fc egress floor (0 violations, by design), but it did not always hold the 10 fc stair-in-use level.** In the semi-synthetic tower, stairs were below 10 fc while in use for 400 minutes a year with sensor + ML and 420 with sensor-only, each time an injected sensor miss left the stair at its setback level (`eval/energy/tower_year.json`). A stair design fix is proposed on the page. It recovers 27.7% of recorded lighting energy in the real-room replay (room rule), and 30.7% of always-on energy in the semi-synthetic tower. It saves less than sensor-only (32.7% / 34.0%): that is the price of a small safety margin. A building manager could reasonably choose sensor-only. Both are shown.
3. **The ML models mostly tie simple baselines.**
   - M1 is clearly better than a schedule in 1 of 5 rooms.
   - The deployable M2 is never clearly better, and is clearly worse in 1 room.
   - M3 beats the better naive forecast on 15 of 20 garage meters, with a median CV(RMSE) of 0.091 vs 0.096.
   - A zero-shot Chronos-Bolt model does better still (0.074, and beats the best naive baseline on 19 of 20 meters), so a foundation model is the better choice for garage load forecasting if torch is available.
4. **We expect most of the money to be in the calendar, not the classifier (hypothesis, not measured: the calendar actions and HVAC were not simulated; only a 2.8 kW peak cut and a 1.5 kW DR trim are quantified).** Summer weekday 13:00-17:00 demand ($10.00/kW), DR readiness (Jun 15-Oct 15), sunset-anchored garage schedules, DST re-anchoring and sensor commissioning are rule-based actions that the page turns into approvable proposals.
5. **Sensor health is the biggest safety lever.** At a 10% miss rate, stair under-lighting rises about 20-fold for the sensor policy (420 -> 8,425 minutes). Fault detection and commissioning deserve the effort before more ML.

## Limits

- **ROBOD** is 5 university rooms in tropical Singapore (29-47 days each), not high-rise corridors, stairs or garages.
  - How its ground truth was collected is not documented.
  - The room-to-zone mapping in the tower is an [ASSUMPTION].
- **The replay can only remove recorded use.** It cannot add light that was off, so under-lit comparisons are relative to the occupied level, not to measured lux.
- **Motion-sensor misses** are injected independently per 5-min step at a rate from one 4-day lab dataset. Real corridor sensors fail in correlated ways (coverage gaps, bad commissioning [28]).
- **The tower year is SEMI-SYNTHETIC:**
  - Inventory, W/ft2 and design fc are assumptions.
  - Each garage level is one control zone. The code requires zones of 500 W or less (T24) and 3,600 ft2 or less (90.1), so real garage savings would differ.
  - DST hour shifts are ignored.
  - HVAC is not simulated.
  - The Open-Meteo year is the UTC 2025 year shown in local time (2024-12-31 16:00 to 2025-12-31 15:00 PST).
  - The DR days are hypothetical.
- **Costs** use LADWP A-2 Rate B base charges only. Adjustment factors are excluded, so real bills are higher. Demand savings are a coincident-peak estimate. SCE customers would need SCE prices, which we did not model.
- **Sources:** NFPA 101 and CFC values come from secondary sources [11][12]. Nothing here certifies code compliance; an engineer and the AHJ must confirm settings.
- **BDG2** meters are whole-garage loads from 2016-2017, mostly outside California. The licence is CC BY-SA (version ambiguous).
- **Chronos** was run as a zero-shot comparator only. Contamination of its pretraining data with BDG2 was not checked.
- **No actuation.** Proposals are pending until a named human approves them. The page keeps decisions for the browser session only; the production path is the append-only `ProposalLog`.

## How to rerun

Set these environment variables first: `PYTHONIOENCODING=utf-8`, `OMP_NUM_THREADS=4`, `TMP=E:\tmp`, `TEMP=E:\tmp`. Raw downloads go to `data/raw/energy/` (git-ignored), with sha256 values in `data/raw/energy/manifest.json`.

```
# origin_hack env (Python 3.13, no torch): downloads anything missing, trains, evaluates, writes eval/energy + models/energy
C:\Users\HP\miniconda3\envs\origin_hack\python.exe scripts/train_energy_models.py            # add --offline to forbid downloads
# optional zero-shot comparator (torch env, reuses the M3 test cache written above)
E:\conda_envs\cerebro_ml\python.exe scripts/train_energy_models.py chronos
# tests (no network, no data/raw: fixtures under tests/fixtures/energy)
C:\Users\HP\miniconda3\envs\origin_hack\python.exe -m pytest tests/test_energy_calendar.py tests/test_energy_forecast.py tests/test_energy_occupancy.py tests/test_energy_policy.py tests/test_energy_tariff.py tests/test_site_energy.py -q
# page on its own
C:\Users\HP\miniconda3\envs\origin_hack\python.exe -m streamlit run app/site_pages/energy.py
```

The seeds are fixed (HGB `random_state=0`, tower `seed=0`, bootstrap seeds in code). The BDG2 load and the M3 fits take most of the runtime; the manifest records the runtime of the last run.

## Sources

All accessed 2026-09-26.

1. UCI ML Repository, Occupancy Detection (Candanedo). CC BY 4.0. https://archive.ics.uci.edu/dataset/357/occupancy+detection
2. Candanedo & Feldheim 2016, Energy and Buildings 112 (citation only). https://doi.org/10.1016/j.enbuild.2015.11.071
3. ROBOD, Room-level Occupancy and Building Operation Dataset, figshare 19234530 (Tekler et al. 2022). CC BY 4.0. https://figshare.com/articles/dataset/ROBOD_Room-level_Occupancy_and_Building_Operation_Dataset/19234530 (file: https://ndownloader.figshare.com/files/36228765)
4. Building Data Genome Project 2. CC BY-SA, version ambiguous: the LICENSE header says 4.0 but the body is the 3.0 legal code. https://github.com/buds-lab/building-data-genome-project-2
5. CU-BEMS (not used; scope cut). https://doi.org/10.6084/m9.figshare.11726517
6. LBNL Building 59 (not used; scope cut). https://datadryad.org/dataset/doi:10.7941/D1N33Q
7. UCI Room Occupancy Estimation (864). CC BY 4.0. https://archive.ics.uci.edu/dataset/864/room+occupancy+estimation
8. Energy Code Ace, 2022 Title 24 Part 6 section 130.1. https://energycodeace.com/content/section-1301-mandatory-indoor-lighting-controls-nonresident
9. inside.lighting, "California Tightens Title 24 Lighting Code Again" (2025-08-26; secondary). https://inside.lighting/news/25-08/california-tightens-title-24-lighting-code-again
10. PNNL-SA-153216, ASHRAE 90.1-2019 lighting training (DOE BECP, May 2020). https://www.oregon.gov/bcd/codes-stand/Documents/90.1-2019-Lighting-training.pdf
11. CSE Magazine, "Ten things to know about emergency illumination" (2017; secondary for NFPA 101). https://www.csemag.com/articles/ten-things-to-know-about-emergency-illumination/
12. GoCodebook, California Fire Code 1008 (2025 ed.; secondary). https://gocodebook.com/us/california/california-fire-code/means-of-egress/signs-illumination-and-path-marking/egress-illumination-and-emergency-lighting
13. CEC Enclosed Parking Garages fact sheet (2022 code). https://www.energy.ca.gov/sites/default/files/2023-09/2022_CEC-Enclosed_Parking_Garages_ADA.pdf
14. Energy Code Ace, 2022 section 120.2. https://energycodeace.com/content/section-1202-required-controls-for-space-conditioning-syste
15. CEC Demand Responsive Lighting Control certification (OpenADR 2.0b). https://www.energy.ca.gov/rules-and-regulations/building-energy-efficiency/manufacturer-certification-building-equipment/dr-controls-lighting
16. LADWP Commercial Electric Rates (TOU periods). https://www.ladwp.com/account/understanding-your-rates/commercial-electric-rates
17. LADWP Standard Commercial/Industrial Rates (A-2 Rate B). https://www.ladwp.com/account/customer-service/electric-rates/standard-commercial-industrial-rates
18. LADWP Commercial Adjustment Billing Factors (2026). https://www.ladwp.com/account/customer-service/electric-rates/commercial-adjustment-billing-factors
19. LADWP Demand Response Program. https://www.ladwp.com/commercial-services/programs-and-rebates-commercial/demand-response-program
20. SCE Business Time-of-Use Rate Plans. https://www.sce.com/business/rates-financing/rate-plans/business-time-of-use-rate-plans
21. SCE Summary of Available Rate Options (PDF). https://www.sce.com/sites/default/files/custom-files/Summary%20of%20Available%20Residential%20and%20Nonresidential%20Rate%20Options.pdf
22. Flex Alert. https://www.flexalert.org/what-is-flex-alert
23. NOAA NCEI 1991-2020 normals API (USW00093134, USW00023174). https://www.ncei.noaa.gov/access/services/data/v1?dataset=normals-monthly-1991-2020&stations=USW00093134,USW00023174&dataTypes=MLY-CLDD-NORMAL,MLY-HTDD-NORMAL,MLY-TAVG-NORMAL&includeStationName=true&format=csv
24. NOAA GML General Solar Position Calculations. https://gml.noaa.gov/grad/solcalc/solareqns.PDF
25. Open-Meteo Terms (CC BY 4.0; free tier non-commercial). https://open-meteo.com/en/terms
26. Open-Meteo Historical Weather API (requested with timezone=GMT). https://archive-api.open-meteo.com/v1/archive?latitude=34.0511&longitude=-118.2353&start_date=2025-01-01&end_date=2025-12-31&hourly=temperature_2m,shortwave_radiation&timezone=GMT
27. LBNL-5095E, Williams et al., "A Meta-Analysis of Energy Savings from Lighting Controls in Commercial Buildings". https://eta-publications.lbl.gov/sites/default/files/a_meta-analysis_of_energy_savings_from_lighting_controls_in_commercial_buildings_lbnl-5095e.pdf
28. PNNL-21923, "Use of Occupancy Sensors in LED Parking Lot and Garage Applications" (2012). https://www.pnnl.gov/main/publications/external/technical_reports/pnnl-21923.pdf
29. Pang et al. 2023, occupancy-based HVAC controls in energy codes (PNNL). https://www.pnnl.gov/publications/adopting-occupancy-based-hvac-controls-commercial-building-energy-codes-analysis-cost
30. Xu, Haves, Piette, Braun 2004, "Peak Demand Reduction from Pre-Cooling with Zone Temperature Reset" (LBNL). https://bies.lbl.gov/publications/peak-demand-reduction-pre-cooling
31. Hugging Face, amazon/chronos-bolt-small (Apache-2.0). https://huggingface.co/amazon/chronos-bolt-small
37. Functional Devices, UL 924 shunt/bypass relays (vendor source). https://blog.functionaldevices.com/product-guidance/shunt-bypass-ul-924-emergency-lighting-relays
38. Garrett & New (ORNL), ASHRAE Guideline 14 metrics (CV(RMSE), NMBE). https://www.osti.gov/servlets/purl/1266021

The numbering follows the research note `energy_switching.json`. Numbers 32-36, 39 and 40 there are model and code pages that this build did not use.
