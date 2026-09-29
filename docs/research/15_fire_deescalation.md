# 15. Fire de-escalation plans with AI (ask 5)

Key `fire`. Written 2026-09-26. Page: `app/site_pages/fire_plan.py`. Code: `src/cascade/building/fire.py`,
`src/cascade/building/firesense.py`, rule table `src/cascade/building/fire_rules.json`. Artifacts: `eval/fire/`,
`models/fire/`, figures `docs/figures/fire_*.svg`.

Data labels used here: **SYNTHETIC** (our generated 32-floor tower and its fire layer), **SIMULATED** (firefighting-water
paths predicted on that tower's water graph), **REAL** (public laboratory sensor recordings). Nothing is INJECTED.

## Question

"How can we have fire de-escalation plans, with AI research about that, and draw something useful?"

Here de-escalation means the smallest response that is still safe: alert and relocate the fire floor and its neighbours
instead of evacuating a whole tower, with written triggers for widening the response, fast verified information for the
Fire Safety Director (FSD) and the fire department, and a controlled recovery. Two sub-questions:

1. Can software prepare a sourced, per-floor plan card from the building model that a human checks instead of inventing
   it under stress?
2. Can a machine-learning label on real multi-sensor data tell a real fire from a nuisance well enough to help the FSD,
   when tested on a room it has never seen?

## What we found (research, sources in brackets)

- **Code automation comes first and is not ours to touch.** A high-rise voice alarm must reach at least the alarming
  floor, the floor above and the floor below [6]; the LAFD high-rise sequence policy lists the automatic actions [1].
  The verifier corrected one claim: in the LAFD matrix, elevator recall is automatic only when an elevator lobby or
  hoistway detector activates (footnote g); manual pull stations, area smoke, duct detectors and waterflow do not recall
  elevators [1]. The firefighter's smoke control panel has "the highest priority of any control point" [10]. Each
  required stair has a standpipe hose connection at every floor landing [11], and high-rises have a supervised floor
  control valve on each floor [12].
- **People and LA rules.** LA Ordinance 180,648 makes the FSD call 911 (or designate someone), direct the evacuation and
  run annual drills that relocate occupants "to a predetermined floor or outside safe refuge area"; towers of 35 or more
  stories run a total-evacuation drill every three years [3]. NFPA's high-rise emergency action plan guide says limited
  evacuations (fire floor plus floors above and below) "have proved effective" and asks for a pre-incident building card
  [5]. NIST TN 1664 documents occupants confused by a stay-then-relocate message in a real 32-story office fire [14].
- **Fire-department tactics** (a California regional guideline, not an LAFD SOP): stage at least two floors below the
  fire, place equipment one floor below outside the attack stair, leave elevators at least two floors below, and use
  elevators only for fires above the sixth floor [31].
- **Smoke** can log stairwells and elevator shafts through stack effect [15].
- **First Interstate Bank, Los Angeles, 1988.** Fire started on floor 12 of a 62-story tower and burned floors 12 to 16;
  sprinklers were about 90 % installed but not in service and the standpipe had been shut off; a maintenance worker died
  after taking a service elevator to floor 12 to check the alarm; about 50 people were above the fire and five were
  rescued from the roof by helicopter [32][33]. Design rules we took: show impairments first, check alarms remotely and
  never by elevator, plan for upward spread.
- **Battery rooms.** In the 2019 Surprise, Arizona energy-storage explosion four firefighters were injured after a door
  was opened; the report recommends remote gas monitoring [34].
- **AI literature.** NIST P-Flash predicts flashover in simulations [17][18]; video and sensor-fusion detection exist
  [20][26]. Vorwerk et al. report a classification rate of up to 69 % (4 fire types) with no data from the target room
  [26] (related work only; their data are not the Mendeley files). An unlisted AI cannot replace listed detection; fire alarm control units
  are listed under UL 864 [38]. We follow the NIST AI RMF for governance [35].

**Therefore the AI role is read-only decision support.** In the design it may draft plan cards, attach evidence, draft
one message and assemble timelines; of these only the plan card is built (the page lists each phase's status: camera
verification, the message template, live shaft readings, the reset checklist and the timeline are not built, and the
sensor label did not transfer). It never silences, delays or resets an alarm, never commands the smoke control panel, sprinklers,
pumps, elevators, stair locks or HVAC, never chooses the evacuation scope, never sends anyone toward the fire, and never
treats a "nuisance-like" score as a reason to downgrade a code alarm.

## What we built

### Part A: deterministic plan card (SYNTHETIC building)

`plan_for_incident(building, fire_layer, zone_id, detections)` returns a `PlanCard` for any room, core, shaft or electrical
room of the synthetic tower. Every rule reads from `fire_rules.json` and shows its basis: a cited code or guideline
(URL), or the tag [team-proposed, validate]. Six of the 17 thresholds carry that tag (FIRE_RELOCATE_MIN_BELOW,
FIRE_RELOCATE_FLOORS, FIRE_SMOKE_WATCH_ABOVE, FIRE_SPREAD_ABOVE, ESS_NEAR_FLOORS, WATER_WATCH_MAX_HOPS; the second and
the last have no URL), and so do the stair choice, the E1 in-between fill and the E1 staging move:

| Card item | Rule | Basis |
|---|---|---|
| Alert floors | fire floor, floor above, floor below; any other alarming floor and its neighbours, with floors in between (E1) | IBC 907.5.2.2 [6]; LAFD [1]; in-between fill [team-proposed, validate] |
| FD staging | 2 floors below (exterior / ground below floor 3); when E1 widens the alert set over that floor, the first non-alerted floor below it (or exterior), tagged on the card | [31], not LAFD SOP; the E1 move [team-proposed, validate] |
| Attack stair and hose connection | the stair nearest the fire; standpipe at the landing 1 floor below | [31][11]; stair choice [team-proposed, validate] |
| Evacuation stair | the other stair | [team-proposed, validate]; FD designates on arrival |
| Relocation floors | 3 floors starting 3 below the fire, skipping staging, alert, impaired floors and floor 1; else outside | [team-proposed, validate]; example in [14] |
| FD elevator | Phase II, exit 2 floors below, only for fires above floor 6; otherwise "stairs expected" | [31] |
| Passenger elevators | Phase I recall expected only if a lobby or hoistway detector activates; verify on the panel | [1] (verifier correction) |
| Electrical | panel, circuits and the circuits feeding the fire zone, feeder path to SWB-1 (existing feeds graph); de-energize only on IC order | building model |
| Water | domestic riser and storm leader on the floor; sprinkler floor control valve; standpipes; where firefighting water migrates (existing water graph, max-product reach from the fire floor's rooms and core, 6 hops, score >= REACH_MIN) | [12][11]; graph weights [team-proposed, validate] |
| Smoke watch | shaft and core sensors 2 to 5 floors above the fire | [15]; band [team-proposed, validate] |
| Hazards | impairments on alert or relocation floors first; battery room (near if within 2 floors); water reaching an electrical room; roof landing | [32][33][34][2] |
| Occupants | design load = gross plate area / 150 sq ft per person (a code design figure, not a headcount); people needing help on alert floors | [37][3] |
| Decisions D0 to D5 | each owned by the FSD or the IC; AI role "evidence only" | [3][5][10][31] |
| Triggers E1 to E6 | alarm outside the alert set; alarm 2+ floors above; smoke in the evacuation stair; impairment; battery-room alarm; person needing help unaccounted | as listed in the rule table |
| Automatic sequence | A1 to A6 as "verify on the fire alarm panel" checkboxes | [1][6][8] |

Every line has `executes=False`; decision lines name the approver. The fire layer (not in the building model) is derived
from the tower geometry by `synthetic_fire_layer()` and stamped SYNTHETIC: Stair A and Stair B are 3 x 6 m enclosures in
the west and east offices, 12.0 m apart at their nearest points (checked against the 30 ft = 9.14 m separation summary
[7]; no code compliance claimed); two fire service access elevators; a low and a high passenger bank; the FCC and a
lithium-ion battery room on F01; three assistance entries; one sprinkler impairment on F23. The highest occupied floor
(F32) is at 124.0 m = 406.8 ft, which triggers the 75 ft and 120 ft items and not the 420 ft extra stair [7]. Design load
is 86 people per floor (1,200 m2 plate).

**Drawings** (SVG strings generated by code, no plotting library; copies in `docs/figures/`):
`fire_flowchart.svg` (phases 0 to 6, purple human-decision diamonds D1 to D5 and the escalation loop D4, teal dashed AI
boxes marked "evidence only", with every AI item that does not exist yet marked "not built"), `fire_section_F19.svg` (fire, alert, staging, relocation and smoke-watch bands; Stair A
evacuation arrow; Stair B attack line to the standpipe landing; FD elevator exit; smoke up the shaft; SIMULATED water
down; FCC, battery room and roof landing), `fire_swimlane.svg` (lanes: fire alarm system, Cerebro AI, FSD, wardens and
occupants, fire department; ordered steps, no clock times). The page redraws all three for the chosen zone.

### Part B: alarm verifier on REAL data

- Data: Mendeley "Indoor Fire Dataset with Distributed Multi-Sensor Nodes", EN54 test room v1 (doi
  10.17632/npk2zcm85h.1, sha256 65a568cf...) for training and the Industrial Hall (doi 10.17632/yghykzm4km.1, sha256
  b431b611...) as the unseen test room, both CC BY 4.0, contributor listed as "Pascal V", Otto von Guericke Universitat
  Magdeburg [24][25]. Hashes match the Mendeley API. A v2 of the EN54 record with revised labels exists; we use v1.
- Episodes (verifier corrections applied): EN54 runs split on a gap over 600 s **or** a label change give **20 episodes
  (13 fire, 7 nuisance)**; the Mendeley description says 12 and 6. Hall: id 13 (one row) merged into id 14 gives **31
  episodes (17 fire, 11 nuisance, 3 other: Ethanol and two CO releases carrying neither flag)**; `anomaly_label` ignored.
- Stage 1 (naive, team-defined proxy, not a listed detector): PM_Total rise over its 30-min rolling median (shifted one
  sample) above the q99.9 of **training** clean background, for 3 consecutive 10 s samples of one node.
- Stage 2: scikit-learn HistGradientBoosting (3 classes, max_iter 150, balanced weights) on 13 channels x (value, delta,
  6-sample slope) = 39 features. A trigger is labelled "fire-like evidence" when P(fire) >= 0.5 (fixed in advance)
  within 60 s, otherwise "nuisance-like, FSD to check". The label never removes the trigger.
- Baselines: the stage-1 trigger alone (every trigger called fire), a CO-rise trigger built the same way, and the ML
  alone without the gate (P(fire) >= 0.5 for 3 samples). Pre-registered ablation: deltas and slopes only (26 features).
- Metric definitions (fixed before the Hall run): latency from the label start, triggers up to 5 min early counted;
  clean background = at least 30 min before and 60 min after any episode, after a 30-min warm-up per sensor series and
  after gaps over 30 min; sensor-hours = samples x 10 s; episode intervals are exact Clopper-Pearson from the counts
  (`eval/fire/exact_intervals.json`), latency and background intervals are 1,000-sample bootstraps over episodes and over
  recording days.
- Protocol: within-site = leave-one-recording-day-out on EN54 (5 days; thresholds and model from the other days only).
  Then all settings were frozen (`eval/fire/frozen_config.json`, hash a08cb131d01d34be, 2026-09-26T21:14:08Z) and the
  Hall was scored once (`eval/fire/hall_runs.log`: run 1). Cross-site thresholds from all EN54 clean background: PM rise
  > 6.0 counts, CO rise > 1.10.

## Measured results

### Planner (SYNTHETIC, rule conformance, not accuracy)

`eval/fire/planner_checks.json`: **224 of 224** plan cards (every floor x office, core, shaft and electrical room of the
32-floor tower) pass all 12 rule checks. Escalated cards (fire in each floor's east office plus a second alarm on each
other floor): **992 of 992** pass the same checks plus three escalation checks (code minimum around every alarming
floor; staging on the first non-alerted floor at or below two under the fire; a staging move is tagged
[team-proposed, validate]); staging moves in 495 of them (`escalated_*` fields). `tests/test_building_fire.py` repeats
this on the 32-floor and a 10-floor tower and tests escalation, low floors, battery-room distance, JSON round trips and
the drawings.

### Verifier, held-out room (REAL, headline): train on EN54, test once on the Industrial Hall

From `eval/fire/sensor_eval.json` (block `hall/full`) and `exact_intervals.json`; n = 17 fire, 11 nuisance, 3 other
episodes; 365.9 clean-background sensor-hours over 4 days.

| Method | Fire caught | Nuisance called fire | Other called fire | Median min to alarm [95% CI] | Background alarms per 24 sensor-h [95% CI] (alarms) |
|---|---|---|---|---|---|
| PM trigger alone (baseline) | 17/17 [80%-100%] | 11/11 [72%-100%] | 2/3 [9%-99%] | 1.23 [-0.19, 7.33] | 6.69 [3.46, 10.92] (102) |
| CO trigger alone (baseline) | 13/17 [50%-93%] | 7/11 [31%-89%] | 3/3 [29%-100%] | 4.22 [-2.33, 19.95] | 0.00 [0.00, 0.00] (0) |
| ML alone, no gate | 16/17 [71%-100%] | 9/11 [48%-98%] | 3/3 [29%-100%] | -4.38 [-4.80, -2.78] | 139.33 [108.56, 168.40] (2124) |
| **Two-stage (ours)** | 17/17 [80%-100%] | **11/11 [72%-100%]** | 2/3 [9%-99%] | 1.23 [-0.19, 7.33] | 6.43 [2.95, 10.92] (98) |

Stage-2 AUROC over all 627 stage-1 triggers (303 from fire episodes, 324 from nuisance, other or clean background; near-
episode triggers excluded): **0.669 [0.51, 0.81]** (cluster bootstrap). The label called 296 of the 303 fire triggers and
292 of the 324 non-fire triggers fire-like. Ablation (deltas only, `hall/deltas`): AUROC 0.715 [0.58, 0.85]; two-stage
still 17/17 fire and 11/11 nuisance called fire; background 4.66 [1.37, 9.79] per 24 sensor-h (71 alarms).

Post-hoc check (defined after the run, `eval/fire/sensitivity_hall.json`): counting only triggers inside the labelled
window, the PM trigger and the two-stage label still alarm 17/17 fires and 11/11 nuisances; no episode was counted only
through the 5-minute early window. The early window only moves latency: for the PM trigger 14 of 30 first alarms (6 of
the 17 fires) land up to 5 minutes before the labelled start in the packed Hall schedule, and for the ML alone 22 of 28
(13 of the fires), which is why its median latency is negative (it alarms constantly, not early). Counts from
`sensitivity_hall.json` (`first_alarm_before_label_start`, computed from `eval/fire/episodes_hall_full.csv`); the 27
same-day gaps between Hall episodes are 7.9 to 74.7 minutes (median 39.0) (`episode_gaps_min`).

### Verifier, same room: leave-one-recording-day-out on EN54 (REAL)

Block `cv_en54/full`; n = 13 fire, 7 nuisance episodes; 570.3 clean-background sensor-hours over 5 days.

| Method | Fire caught | Nuisance called fire | Median min to alarm [95% CI] | Background alarms per 24 sensor-h [95% CI] (alarms) |
|---|---|---|---|---|
| PM trigger alone (baseline) | 13/13 [75%-100%] | 3/7 [10%-82%] | 2.01 [0.84, 3.10] | 0.76 [0.08, 1.63] (18) |
| CO trigger alone (baseline) | 12/13 [64%-100%] | 6/7 [42%-100%] | 7.59 [1.43, 15.48] | 0.55 [0.20, 1.15] (13) |
| ML alone, no gate | 13/13 [75%-100%] | 7/7 [59%-100%] | -3.78 [-4.48, 1.10] | 6.73 [2.54, 11.15] (160) |
| **Two-stage (ours)** | 13/13 [75%-100%] | 3/7 [10%-82%] | 2.01 [0.84, 3.10] | **0.04 [0.00, 0.18] (1)** |

Stage-2 AUROC 0.653 [0.49, 0.99] over 236 triggers (ablation: 0.833 [0.72, 0.99]). The research scratch figure of 0.955
(and 13/13 fire, 1/7 nuisance) came from episode-grouped CV with thresholds set on all background data; with the leak
removed and whole days held out we do not reproduce it, so it is not used anywhere.

## Conclusions

1. **The useful product is the plan card, not the classifier.** It is deterministic, shows its basis line by line (a
   citation or a [team-proposed, validate] tag), passes every rule check on 224 zones and 992 escalated cards, and turns the research into something an FSD can print, check and drill.
2. **The ML label did not transfer to a new room.** On the held-out hall it called 11 of 11 nuisance episodes fire-like,
   no better than the naive trigger, and separated triggers only weakly (AUROC 0.67). In the same room it removed most
   clean-background alarms (18 to 1) but still did not reduce nuisance episodes called fire (3/7 in both).
3. **The ML alone is unusable as an alarm source** (139 alarms per 24 sensor-hours in the hall). That supports the
   design rule: any AI label may add evidence for the FSD, never suppress, delay or downgrade a listed alarm.
4. The CO trigger raised no clean-background alarms in the hall but missed 4 of 17 fires; no single signal is enough,
   which is why listed multi-criteria detectors and human verification stay in charge.

## Limits

- The tower and fire layer are SYNTHETIC; no code compliance is claimed; the approved Emergency Plan of a real building
  (with its predetermined relocation floors) overrides the card.
- Relocation distance, smoke-watch band, battery-room distance, the stair choice, contiguous escalation fill, the staging
  move under E1 and the water-graph weights are [team-proposed, validate]. Staging and elevator rules come from a Sacramento regional guideline, not an LAFD SOP [31].
  The current LAFC 57.408 wording was not read (only the 2009 ordinance) [4].
- Sensor data are German laboratory rooms (the EN54 test room and a 10 x 22 x 8 m unventilated industrial hall, per the
  Mendeley description [25]), not a high-rise office. 13 + 17 fire
  episodes give wide intervals. The stage-1 trigger is a proxy, not a listed smoke detector. Hall episodes on the same day are 7.9 to 74.7
  minutes apart (median 39.0), so guard bands leave only 365.9 clean sensor-hours, and 165 (two-stage) and 183 (PM trigger) alarms fall in the guard
  bands near episodes (CO trigger 33, ML alone 611; `near_episode_alarms` in `sensor_eval.json`).
- The descriptive `by_scenario` field inside `sensor_eval.json` was first written with mangled keys (a key-formatting
  bug found after the run). `scripts/fire_summarize.py` rebuilt only that field from the saved episode lists and says so
  in `episodes_by_scenario_note`; no metric was re-scored. The same counts are in `eval/fire/episode_counts.json`.
- Nothing here has been reviewed by LAFD or an authority having jurisdiction. Part C (D-Fire images) was out of scope.

## How to rerun

Runtime env `C:\Users\HP\miniconda3\envs\origin_hack\python.exe`, from `E:\origin_hack`:

```
python scripts/fire_build_plans.py            # fire layer, 224 + 992 escalated rule checks, example cards, figures (~4 s)
python scripts/fire_sensor_eval.py --stage prep  # download/verify both CSVs into data/raw/fire, episodes, features (~25 s)
python scripts/fire_sensor_eval.py --stage cv    # EN54 leave-one-day-out, then freezes the settings (~3 min)
python scripts/fire_sensor_eval.py --stage hall --reason "<why>"  # single held-out run; refuses if settings changed (~1 min)
python scripts/fire_summarize.py              # post-hoc sensitivity, exact intervals, episode counts
python scripts/fire_make_fixtures.py          # small SYNTHETIC test fixtures (about 0.67 MB in total)
python -m pytest tests/test_building_fire.py tests/test_firesense.py tests/test_site_fire_plan.py -q
```

## Sources (accessed 2026-09-26)

[1] LAFD Policy for Fire Life Safety Sequence in High Rise Buildings. https://lafd.org/fire-prevention/fire-development-services/policy-fire-life-safety-sequence-high-rise-buildings
[2] LAFD Requirement No. 10, Emergency Helicopter Landing Facilities. https://lafd.org/sites/default/files/pdf_files/EHLF-Reg10.pdf
[3] LA Ordinance 180,648 (LAMC 57.33.19), 2009. https://cityclerk.lacity.org/onlinedocs/2008/08-2476_ord_180648.pdf
[4] LA City Fire Code 2023 section 408.1 (UpCodes). https://up.codes/s/emergency-planning-and-evacuation-requirements-for-high-rise-buildings
[5] NFPA, Emergency Action Plans for High-Rise Office Buildings (2014). https://content.nfpa.org/-/media/project/storefront/catalog/files/building-and-life-safety/highrise/emergencyactionplanhighrise.pdf?rev=9f5900973b264cc486ed9efa8643eb30
[6] IBC 2021 907.5.2.2 (UpCodes). https://up.codes/s/emergency-voice-alarm-communication-systems
[7] High-Rise Building Requirements Cheatsheet (IBC 2021), The Building Code Blog. https://www.buildingcode.blog/uploads/1/2/9/9/129929641/building_code_blog_-_high_rise_cheatsheet.pdf
[8] IBC 2021 909.20.5 (UpCodes). https://up.codes/s/stairway-and-ramp-pressurization-alternative
[10] IBC 2021 909.16 (UpCodes). https://up.codes/s/fire-fighter-s-smoke-control-panel
[11] IBC 2021 905.4 (UpCodes). https://up.codes/s/location-of-class-i-standpipe-hose-connections
[12] IBC 903.4.3 (UpCodes). https://up.codes/s/floor-control-valves
[13] NIST TN 1825, elevators for evacuation. https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.1825.pdf
[14] NIST TN 1664, occupant behavior in a high-rise office fire. https://www.nist.gov/system/files/documents/el/fire_research/TN1664.pdf
[15] NISTIR 89-4035, stack effect in building fires. https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir89-4035.pdf
[17] NIST news on P-Flash, June 2021. https://www.nist.gov/news-events/news/2021/06/how-ai-could-alert-firefighters-imminent-danger
[18] Tam et al. 2023, P-Flashv2. https://www.nist.gov/publications/real-time-flashover-prediction-model-multi-compartment-building-structures-using
[20] Cetin et al. 2013, video fire detection review (abstract only). https://www.sciencedirect.com/science/article/abs/pii/S1051200413001462
[24] V, Pascal (2023), Indoor Fire Dataset with Distributed Multi-Sensor Nodes (EN54 Test Room), Mendeley Data, V1, doi:10.17632/npk2zcm85h.1, CC BY 4.0. https://data.mendeley.com/datasets/npk2zcm85h/1
[25] V, Pascal (2024), Indoor Fire Dataset with Distributed Multi-Sensor Nodes (Industrial Hall), Mendeley Data, V1, doi:10.17632/yghykzm4km.1, CC BY 4.0. https://data.mendeley.com/datasets/yghykzm4km/1
[26] Vorwerk et al. 2024, Sensors 24(5):1428 (related work). https://pmc.ncbi.nlm.nih.gov/articles/PMC10934981/
[31] Sacramento Regional Fire, High Rise Fire guideline (reviewed 08/21/22). https://srfecc.ca.gov/files/bf8df60b1/High+Rise+Operations.pdf
[32] LAFD Historical Archive, First Interstate Bank fire executive summary. https://lafire.com/famous_fires/1988-0504_1stInterstateFire/ExSummary/LAFD-ExecutiveSummary.htm
[33] NIST, Interstate Bank Building Fire, Los Angeles 1988. https://www.nist.gov/el/interstate-bank-building-fire-los-angeles-1988
[34] UL FSRI, lithium-ion ESS explosion, Arizona. https://fsri.org/research-update/report-four-firefighters-injured-lithium-ion-battery-energy-storage-system
[35] NIST AI Risk Management Framework. https://www.nist.gov/itl/ai-risk-management-framework
[37] Jensen Hughes memo, IBC occupant load factors (2023-12-01). https://www.houstonpermittingcenter.org/media/9311/download?inline=
[38] Intertek, UL 864 overview. https://www.intertek.com/standards-updates/ul-864-control-and-accessories-for-fire-alarm-systems/
[40] Creative Commons Attribution 4.0. https://creativecommons.org/licenses/by/4.0/
