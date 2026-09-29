# 14. LA rain: which side of a building gets the most wind-driven rain (key: rain)

Status: built and measured on 2026-09-26. Every number below is copied from an artifact that
`scripts/build_la_rain.py` wrote under `eval/rain/`. Each table names its file. Pilot numbers from the research
run are **not** quoted, because the pilot used the wrong wind exponent, a 12 h storm gap and no QC. Labels follow
the site convention: **REAL** means measured, **MODELLED** means a model output, **SYNTHETIC** means a
unit-test fixture.

## 1. Question

The user's ask 4 had three parts:

1. What are the rain coverage patterns across LA County?
2. Which side of a building takes the most water because of the direction rain arrives from, and is there a
   correlation between rain and wind direction?
3. How could an AI model predict this in a way that generalises across the LA area?

## 2. Answer in one line

**In most of the LA basin, east- and south-east-facing walls get the most wind-driven rain.** At all 7 basin and San
Fernando Valley airport stations, the most-exposed wall is E or SE (`eval/rain/summary.json`: `n_basin_E_SE` 7 of
`n_basin` 7). The everyday wind blows mostly from the west or south-west, so a standard wind rose points at the
wrong wall. Outside the basin the answer changes:

- Santa Ana: S.
- Ontario: W, but only weakly concentrated.
- Palmdale: SW.
- Lancaster: W.

## 3. What we found

### 3.1 Rain coverage (NCEI 1991-2020 normals, REAL, `eval/rain/normals.json`)

Source: NCEI 1991-2020 annual precipitation normals at 64 LA-area stations, from a bounding-box search of the
NCEI Access Data Service [4].

- **Rain rises with elevation on the basin side of the mountains.** Spearman rho between elevation and annual
  normal:
  - basin side (south of 34.45 N): **0.759** (n = 54, p = 2.9e-11);
  - north of 34.45 N: 0.115 (n = 10, p = 0.75);
  - all stations pooled: 0.276 (n = 64, p = 0.027).
- **Median annual normal on the basin side:**
  - **13.48 in/yr** below 150 m (n = 22; range 11.77-17.73);
  - **27.63 in/yr** at 500 m and higher (n = 4; range 16.76-32.17);
  - ratio **2.05**. With n = 4 in the high band, read this as indicative.
- **North of 34.45 N (Antelope Valley side, rain shadow):** median **9.40 in/yr** (n = 10). The driest is Palmdale AP
  at 5.90 in; the band's maximum is 17.92 in.
- The 34.45 N split is a rough stand-in for the San Gabriel crest, not a surveyed line.
- **Season:** the median Dec-Feb share of the annual normal is **0.645** across the stations that report it.
- **Driving rain is even more concentrated in winter.** November to March carries 0.877-0.895 of the ISO driving-rain
  index at the basin and Orange County stations, 0.837 at ONT, 0.774 at PMD and 0.807 at WJF
  (`station_roses.json`, `novmar_share_of_driving_rain`).

### 3.2 Which wall gets wet (ISO 15927-3 airfield index, REAL, `eval/rain/station_roses.json`)

**Data.** IEM ASOS routine hourly observations [1] at 12 stations over water years 2006-2025. Water years that failed
QC were excluded (section 3.4), so each station uses 16-20 water years.

**Index.** `I_A` is the ISO 15927-3 method-1 airfield annual index in L/m2 per year. It is computed at 10 m on open
airfield terrain; C_T and W are not applied.

**Column meanings:**
- Rain dir: rain-weighted mean direction the wind blows from, in degrees, with Rbar (the mean resultant length).
- All-hours dir: the same for all non-calm hours.
- Storms: events of at least 5 mm, split by at least 6 dry hours.
- Rayleigh p: tests whether the per-storm rain-weighted directions are uniform.
- Rain-vs-dry p: a block permutation test (2,000 permutations) of whole rain episodes against fully dry local days.

| Station | Region | WY used | Most exposed | I_A top | Least (I_A) | Max/min | Top-3 share | Rain dir (Rbar) | All-hours dir (Rbar) | Storms | Rayleigh p | Rain-vs-dry p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LAX | Coast & basin | 20 | E | 125.9 | N 30.8 | 4.1 | 0.547 (E+SE+NE) | 116 (0.41) | 252 (0.45) | 234 | 4.1e-17 | 5.0e-04 |
| SMO | Coast & basin | 19 | E | 79.8 | NW 15.4 | 5.2 | 0.535 (E+SE+S) | 100 (0.38) | 227 (0.41) | 226 | 2.2e-17 | 5.0e-04 |
| HHR | Coast & basin | 20 | E | 87.8 | N 9.4 | 9.4 | 0.596 (E+SE+S) | 127 (0.44) | 250 (0.61) | 227 | 2.6e-20 | 5.0e-04 |
| CQT | Coast & basin | 19 | E | 70.1 | NW 4.7 | 14.9 | 0.816 (E+SE+NE) | 97 (0.74) | 266 (0.34) | 235 | 6.9e-47 | 5.0e-04 |
| LGB | Coast & basin | 20 | SE | 99.5 | NW 32.0 | 3.1 | 0.557 (SE+S+E) | 134 (0.35) | 249 (0.30) | 234 | 3.7e-14 | 5.0e-04 |
| BUR | San Fernando Valley | 16 | SE | 208.2 | N 16.7 | 12.5 | 0.781 (SE+E+S) | 133 (0.61) | 159 (0.52) | 195 | 5.9e-40 | 5.0e-04 |
| VNY | San Fernando Valley | 20 | SE | 165.4 | W 17.4 | 9.5 | 0.735 (SE+S+E) | 135 (0.59) | 127 (0.30) | 243 | 1.1e-44 | 5.0e-04 |
| FUL | Orange County | 18 | SE | 65.6 | NW 10.6 | 6.2 | 0.585 (SE+E+S) | 120 (0.42) | 189 (0.46) | 203 | 1.4e-19 | 5.0e-04 |
| SNA | Orange County | 18 | S | 104.7 | N 14.6 | 7.2 | 0.646 (S+SE+SW) | 160 (0.43) | 208 (0.60) | 210 | 1.3e-20 | 5.0e-04 |
| ONT | Inland Empire | 17 | W | 72.9 | SE 19.6 | 3.7 | 0.498 (W+SW+NE) | 323 (0.16) | 255 (0.60) | 207 | 8.8e-05 | 5.0e-04 |
| PMD | Antelope Valley | 20 | SW | 75.6 | E 18.6 | 4.1 | 0.605 (SW+W+S) | 239 (0.35) | 239 (0.54) | 133 | 5.4e-16 | 5.0e-04 |
| WJF | Antelope Valley | 17 | W | 69.4 | SE 15.8 | 4.4 | 0.613 (W+SW+NW) | 260 (0.34) | 258 (0.64) | 118 | 3.6e-11 | 5.0e-04 |

**Exposure is lopsided.** The most-exposed wall gets 3.1 (LGB) to 14.9 (CQT) times the index of the least-exposed wall.
The top three walls carry 0.498 (ONT) to 0.816 (CQT) of the total.

**Rain arrives from a different side than the everyday wind** (`station_roses.json`: `sector_allhours_share` vs
`sector_rain_share`):

| Station | W+SW sectors | E+SE sectors | Mean wind speed |
|---|---|---|---|
| LAX | 0.651 of non-calm hours, 0.197 of rain | 0.185 of hours, 0.533 of rain | 4.09 m/s in rain hours, 3.18 m/s in dry hours |
| CQT | 0.604 of hours, 0.087 of rain | 0.255 of hours, 0.817 of rain | |
| HHR | 0.753 of hours, 0.243 of rain | 0.161 of hours, 0.604 of rain | |

**Heavy rain comes from the same direction** (`by_intensity`, rain-weighted mean direction, degrees):

| Station | <2.5 mm/h | 2.5-6 mm/h | >=6 mm/h |
|---|---|---|---|
| LAX | 119.8 | 115.1 | 111.3 |
| CQT | 98.5 | 98.6 | 93.0 |
| BUR | 139.6 | 127.5 | 132.5 |
| VNY | 137.3 | 129.6 | 137.8 |

**Year-to-year stability** (`top_facade_wy_counts`):
- BUR: SE in 16 of 16 QC-passed water years.
- CQT: E in 18 of 19.
- VNY: SE in 17 of 20.
- LAX varies more: E 9, SE 5, W 3, SW 3.
- For LAX storms, E is the storm-level top wall in 81 of 234 storms.

**Sensitivity** (`sensitivity`: all 20 water years without the QC exclusion, and WY2013-2025 only). The most-exposed
wall is unchanged at 11 of 12 stations. FUL flips between SE and E: SE and E are its two largest walls, at shares
0.22 and 0.21 on the page's heatmap.

**A few storms carry much of the index.** The top 10 % of storms carry 0.261 (WJF) to 0.486 (CQT) of the index summed
over storms of at least 5 mm (`top10pct_share_of_storm_index`).

### 3.3 Is there a correlation? (REAL)

Yes, at every station.

- **Storm directions are concentrated.** Per-storm rain-weighted directions are far from uniform, with Rayleigh p from
  8.8e-05 (ONT, the weakest, Rbar 0.16) to 6.9e-47 (CQT) (`summary.json`, `rayleigh_p_range`).
- **Rain wind differs from dry wind.** In the block permutation test, rain-episode wind differs from dry-day wind at
  every station. p = 5.0e-04 at all 12 (`perm_p_max`), which is the floor of a 2,000-permutation test.
- **Blocks respect storm structure.** The test permutes whole rain episodes and whole dry local days, so hours inside
  one storm are never treated as independent. This follows the verifier's request.

### 3.4 Data quality (REAL, `eval/rain/qa_station_wy.json`)

We compared IEM hourly rain with GHCN-Daily PRCP [4] for every station-day. Days use local standard time (UTC-8),
because GHCN-D first-order stations use the local-standard day.

- **Spike days.** A spike day is one where GHCN-D = 0 and the IEM day total exceeds 2.5 mm. These days were zeroed:
  39 across the 12 stations (LAX 13, CQT 13, LGB 4, HHR 3, WJF 3, SMO 1, SNA 1, ONT 1, others 0).
- **Water-year QC.** Station water years with an IEM/GHCN-D ratio outside 0.85-1.15 were excluded:

  | Station | Excluded water years |
  |---|---|
  | SMO | 2016 |
  | BUR | 2013, 2014, 2016, 2024 |
  | FUL | 2023, 2024 |
  | SNA | 2018, 2025 |
  | ONT | 2011, 2018, 2019 |
  | WJF | 2007, 2010, 2023 |

- **Aggregate ratio** over all water years: 0.929 (FUL) to 0.991 (LAX). Per-water-year ratios run from 0.43 (SNA) to
  1.04 (SMO).
- **The p01i 'M' rule is empirical.** Before 2012-01-18, 'M' mostly means no precipitation group was reported, so it
  is treated as 0; from that date on, 'M' means missing (NaN). This comes from the archive's own pattern, not from IEM
  documentation.
- **KCQT ends on 2024-05-20**, when the site moved; the replacement COOP station FHMC1 has no METAR [6].
- **Two data rules** are covered by unit tests: routine hourly observations only (minutes 40-59, ceil to the hour),
  and calm (0 kt) has no direction.

### 3.5 ERA5 against the airports (REAL vs reanalysis, `eval/rain/events_summary.json`)

We segmented events on ERA5 precipitation. An hour counts as wet at 0.1 mm or more; events are split by at least 6 dry
hours and kept at 5 mm or more.

- **Event counts.** 1,487 events were detected at the 12 stations and 1,332 were used. 145 were dropped because their
  water year failed QC, and 10 because ASOS coverage in the window was below 0.8.
- **Rain totals agree well.** ERA5 and ASOS event totals correlate at r = 0.796 (FUL) to 0.934 (CQT). The ERA5/ASOS sum
  ratio is 0.893 (LGB) to 1.483 (ONT).
- **False alarms.** 3.3 % (LAX) to 10.9 % (PMD) of ERA5 events had less than 1 mm at the airport.
- **ERA5 storm winds are more southerly than the airports measure.** ERA5 rain-weighted 10 m directions are 142.5-188.9
  degrees. The basin airports' rain directions are 97-135 degrees.
- **Wind direction barely changes with height in ERA5.** The median absolute difference between 10 m and 100 m is only
  1.4-5.8 degrees.
- **Consequence for the map.** Pure physics on ERA5 winds names S as the top wall in 18 of the 24 map cells
  (`grid_exposure.json`). Station-level ground truth is needed to correct this, which is the case for a learned
  corrector.

### 3.6 Can AI predict the wettest wall of a coming storm? (REAL held-out, `eval/rain/metrics.json`)

**Unit of evaluation.** One ERA5-segmented event at one station. False alarms count.

**Target.** The ASOS-measured ISO storm index per wall (L/m2), summed over the event window +/- 3 h.

**Model.** One sklearn HistGradientBoostingRegressor per wall on log1p(target). Parameters: max_iter 300, learning rate
0.05, 15 leaf nodes, min leaf 10, L2 1.0, random_state 0.

**Baselines:**
- B0: station climatology.
- B1: ISO physics on the gridded 10 m wind, with no learning.
- B2: a per-station least-squares coefficient times gridded event rain.

**Bootstrap.** 95 % intervals resample storm clusters (event starts within 36 h across stations), 2,000 resamples. The
"gap" is baseline MAE minus model MAE; above 0 means the model is better.

**Temporal holdout** (train WY2016-2022, n_train = 926; test WY2023-2025, n = 406 events in 53 clusters; mean target
6.14 L/m2, mean wettest-wall target 16.50):

| Method | MAE | Wettest-wall MAE | Top-1 | Within 45 deg | Median Spearman | Gap vs model [95 % CI] |
|---|---|---|---|---|---|---|
| B0 station climatology | 5.70 | 12.75 | 0.428 | 0.730 | 0.714 | 2.36 [1.71, 3.16] |
| B1 ISO physics on ERA5 | 4.61 | 7.93 | 0.389 | 0.761 | 0.786 | 1.27 [0.77, 1.83] |
| B2 station coef x ERA5 rain | 4.20 | 8.18 | 0.425 | 0.696 | 0.738 | 0.86 [0.59, 1.16] |
| **HGB model** | **3.34** | 7.98 | 0.428 | **0.829** | **0.857** | - |

**Leave one station out** (12 folds, n = 1,332 events in 160 clusters; mean target 4.64):

| Method | MAE | Wettest-wall MAE | Top-1 | Within 45 deg | Median Spearman | Gap vs model [95 % CI] |
|---|---|---|---|---|---|---|
| B0 | 5.22 | 9.47 | 0.224 | 0.569 | 0.476 | 2.45 [2.16, 2.77] |
| B1 | 3.65 | 6.20 | 0.378 | 0.761 | 0.783 | 0.87 [0.70, 1.05] |
| B2 | 4.15 | 7.24 | 0.224 | 0.569 | 0.512 | 1.37 [1.19, 1.57] |
| **HGB model** | **2.77** | 6.20 | **0.396** | **0.771** | **0.799** | - |

**Leave station and period out** (train other stations WY2016-2022; test the held-out station WY2023-2025; n = 406 in
53 clusters):

| Method | MAE | Wettest-wall MAE | Top-1 | Within 45 deg | Median Spearman | Gap vs model [95 % CI] |
|---|---|---|---|---|---|---|
| B0 | 6.08 | 13.31 | 0.268 | 0.619 | 0.571 | 2.13 [1.64, 2.73] |
| B1 | 4.61 | 7.93 | **0.389** | 0.761 | 0.786 | 0.67 [0.23, 1.07] |
| B2 | 5.02 | 9.49 | 0.155 | 0.572 | 0.595 | 1.07 [0.79, 1.39] |
| HGB model | **3.94** | 9.27 | 0.344 | 0.761 | **0.809** | - |

**Real day-ahead forecasts.** The 10 m-only model was trained on ERA5 events up to WY2023 (n_train = 1,120). It was
tested on events segmented on real GFS day-1 forecasts from the Open-Meteo Previous Runs API [3], 2024-01-01 to
2025-09-30: n = 194 events in 25 clusters.

| Method | MAE | Wettest-wall MAE | Top-1 | Within 45 deg | Median Spearman | Gap vs model [95 % CI] |
|---|---|---|---|---|---|---|
| B0 | 5.38 | 10.97 | **0.400** | 0.722 | 0.738 | 1.74 [1.25, 2.21] |
| B1 (physics on GFS wind) | 4.51 | 8.22 | 0.256 | 0.667 | 0.675 | 0.87 [0.45, 1.37] |
| B2 (coef x GFS rain) | 3.85 | **7.44** | 0.394 | **0.733** | 0.738 | 0.21 [-0.53, 0.75] |
| HGB model (10 m) | **3.64** | 8.49 | 0.350 | 0.700 | **0.762** | - |

For reference, the same 10 m model on ERA5 events in the same period gives MAE 2.91 against B1 3.67 and B2 3.88, and
top-1 0.532 (n = 181). This suggests much of the drop on real forecasts comes from forecast error rather than the
model. The two event sets differ (181 against 194 events), so this is not a paired comparison.

**Reading the results:**

- **Average error.** The model lowers the error per wall per storm against every baseline in the temporal,
  unseen-station and unseen-station-and-period tests. The cluster-bootstrap intervals exclude 0 in all three.
- **Wettest wall.** It does **not** reduce the error on each storm's wettest wall: 7.98 against B1 7.93 in the temporal
  test. In the station-and-period test, B1 names the wettest wall more often (0.389 against 0.344).
- **Day-ahead forecasts.** On real GFS forecasts, the model is **not clearly better** than B2 (gap CI -0.53 to 0.75).
  It names the wettest wall less often than B0 or B2.
- **Where it helps and where it does not.** Per station in the leave-one-station-out test (`loso.per_station`), the
  model names the wettest wall more often than B1 at 6 of 12 stations: LAX, SMO, HHR, CQT (0.500 against 0.300), LGB
  and FUL. It does so less often at the other 6: BUR (0.305 against 0.362), VNY, SNA, ONT (0.086 against 0.231), PMD
  and WJF.
- **Honest summary:** the model is a bias corrector on top of ISO physics that lowers average error. It is not a
  reliable predictor of which single wall a given storm will hit hardest. For planning, the measured station
  climatology in section 3.2 is the stronger product.

### 3.7 Map (MODELLED, `eval/rain/grid_exposure.json`)

- **Grid.** 24 ERA5 0.25-degree cells over lat 33.75-34.75 and lon -118.75 to -117.5. They include the 12 station
  cells. Two pairs of stations share a cell: LAX/SMO and CQT/HHR.
- **How each cell is modelled.** Events are segmented on the cell's ERA5 precipitation over WY2016-2025. The 10 m model
  runs on each event and the results are summed to an annual per-wall index.
- **Most-exposed wall across the 24 cells:**

  | Wall | Model (cells) | ERA5 physics alone (cells) |
  |---|---|---|
  | SE | 8 | 3 |
  | S | 7 | 18 |
  | E | 4 | 0 |
  | SW | 4 | 3 |
  | W | 1 | 0 |

- **Mountain cells.** 8 cells sit more than 50 m above the highest training station (774 m). They are flagged as
  outside the training range and possibly outside ISO scope (mountains with cliffs or gorges).
- **Expected skill** is the leave-one-station-out metric, not the temporal one.

## 4. What we built

| Path | What it does |
|---|---|
| `scripts/fetch_la_rain_data.py` | Paced, cached downloads into `data/raw/rain/`: IEM ASOS, IEM CA_ASOS metadata, ERA5 via the Open-Meteo archive (12 stations plus the 0.25-degree grid), GFS day-1 via Previous Runs, GHCN-Daily, NCEI normals. Writes `sources_manifest.json` (URL, parameters, access date, licence, sha256, rows) plus a slim copy in `eval/rain/`. 65 files. 24 of them (IEM and ERA5 station files) were copied from the research pilot cache, which downloaded them the same day with the same parameters; the manifest marks these. |
| `src/cascade/building/rainexposure.py` | ISO 15927-3 physics: `iso_hourly` with wind to the power 1 and rain to the power 8/9, any azimuth; `annual_index`; `spells` (96 h rule per orientation); `c_r`; `obstruction_factor`; `wall_index`. Also loading and QC (`load_asos_csv`, `qc_daily`, `qc_water_years`), circular statistics (`weighted_circmean`, `rayleigh`, `block_permutation_test`) and the building-layer API (`facade_exposure`, `exposure_rank`, `exposure_shares`, `wdr_iso_series`, `nearest_station`). Rule and threshold tables live in the module (`RULES`, `TERRAIN`, `OBSTRUCTION`), not in `src/cascade/rubrics`. |
| `src/cascade/building/rainmodel.py` | Event tables segmented on gridded or forecast rain; `FacadeModel` (8 HGB models); baselines B0/B1/B2; metrics; storm-cluster bootstrap; temporal and grouped evaluation. |
| `scripts/build_la_rain.py` | Parts qc, roses, events, model, map, normals, summary. Writes `eval/rain/*.json` and parquet, and `models/rain/hgb_era5_full.joblib` and `hgb_10m.joblib` (sklearn 1.9.1, 1.8-2.0 MB each). |
| `app/site_pages/rain_la.py` | The site page: one-line answer, a "What this means" box, pydeck map (station arrows REAL, grid cells MODELLED, normals REAL), rain rose next to the all-hours rose, per-wall bars, a water-year strip, an all-station x 8-wall heatmap, correlation statistics, model evaluation (bars plus tables and plain-language verdicts), and "Check your building" (station or coordinates, any wall azimuth, height, terrain, obstruction, and a four-wall inspection order). Engineers' expander and sources footer. Reads only `eval/rain/`. |
| `tests/test_rainexposure.py`, `tests/test_rainmodel.py`, `tests/test_site_rain_la.py`, `tests/fixtures/rain/` | Unit tests on SYNTHETIC fixtures, an artifact self-consistency test and an AppTest page check. |

**Verifier corrections applied** (from the research verification):

- **Wind exponent.** Speed enters to the power 1, not 8/9. A unit test pins it against Blocken & Carmeliet 2010 eq. 5.
  The pinned value for a 5 m/s east wind with 2 mm/h rain on the E wall is (2/9) x 5 x 2^(8/9) = 2.0575. The
  verifier's note wrote 2.069, an arithmetic slip; the formula is the same.
- **QC** covers all 20 water years with GHCN-D day matching, spike zeroing and water-year exclusion.
- **Storms are segmented on ERA5** (or GFS) precipitation in training and at inference alike, so false alarms count.
  No "oracle timing" figure is published.
- **Bootstrap** resamples storm clusters, and every table reports n events and n clusters.
- **Baselines and weak spots are reported.** B0 is included, the wettest-wall MAE is reported, and the
  leave-station-and-period-out test is added.
- **The forecast-lead test** starts at 2024-01-01, the start of the Previous Runs archive.
- **ISO spells** use the 96 h per-orientation rule.
- **Footer attribution** follows the verifier's wording.

## 5. Conclusions

1. **Which side.** In the LA basin and San Fernando Valley, plan facade inspection and sealing on the east and south-east
   walls first:
   - E at LAX, SMO, HHR and CQT;
   - SE at LGB, BUR and VNY (and at FUL in Orange County).

   Elsewhere: Santa Ana S, Antelope Valley SW/W, Ontario W (weak). The everyday wind rose (W/SW at the coast) points at
   the wrong wall.
2. **Correlation.** Storm rain arrives from a concentrated direction at all 12 stations (Rayleigh), and that direction
   differs from dry-weather wind at all 12 (block permutation, p at the test floor). Heavy rain (6 mm/h and above)
   keeps the same direction.
3. **Coverage.** On the coastal side, rain roughly doubles from the lowlands to 500 m and above (median 13.48 against
   27.63 in/yr, n = 22 and 4). Behind the crest is a rain shadow (median 9.40 in/yr, n = 10). At the basin and valley
   stations, 0.887-0.895 of the driving-rain index falls from November to March.
4. **AI.** A gradient-boosted corrector on ERA5 features beats three naive baselines on average error in held-out years
   and at unseen stations. It does not improve on the wettest wall, and on real day-ahead GFS forecasts it is not
   clearly better than the simplest rain-scaling baseline. It is worth running as a storm-level advisory, labelled
   modest. The measured climatology is the dependable product.
5. **Advisory only.** The AI proposes an inspection order; a person approves any work order. Nothing here actuates
   equipment.

## 6. Limits

- **Airports, not buildings.** All measurements come from airport sites at 10 m on open terrain; none come from a
  building.
- **ASOS wind differs from ISO's assumption.** ASOS wind is a 2-minute average reported to 10 degrees, with calm at 2 kt
  or less [7], while ISO assumes hourly means. At CQT, 0.267 of rain falls in calm hours and has no direction.
- **C_T and W not applied.** The topography factor and wall factor (ISO Figure 1, not read [8]) are set to 1. Values
  are relative exposure, not litres on a wall; on-building catch ratios need site calibration [9].
- **Upper floors and urban effects are not resolved.** Winds above 100 m, street canyons and tower effects are outside
  the data. The literature finds top corners and side edges of the windward face wettest [10]; the page shows this as
  text only.
- **ERA5 resolution.** ERA5 is 0.25 degrees and two station pairs share cells. ERA5 storm winds are more southerly than
  ASOS.
- **Short forecast test.** The forecast-lead test covers 21 months, 194 events and 25 clusters, so its intervals are
  wide.
- **Map cells are MODELLED.** Mountain cells are outside the training range.
- **Spell index not computed.** The ISO 3-year-return spell index is not computed; only per-water-year spell maxima are
  shown.
- **Open-Meteo licence.** The free tier is non-commercial; commercial use needs a paid plan [3].
- **No live "next storm" panel.** The site runs offline, so the page does not call the live forecast API.

## 7. How to rerun

```
set HF_HOME=E:\hf_cache & set TMP=E:\tmp & set TEMP=E:\tmp & set PYTHONIOENCODING=utf-8 & set OMP_NUM_THREADS=4
C:\Users\HP\miniconda3\envs\origin_hack\python.exe scripts\fetch_la_rain_data.py --steps meta,iem,era5,ghcnd,normals,prev
C:\Users\HP\miniconda3\envs\origin_hack\python.exe scripts\fetch_la_rain_data.py --steps grid --grid-pause 150
C:\Users\HP\miniconda3\envs\origin_hack\python.exe scripts\build_la_rain.py            (all parts; 11 min on a shared laptop CPU on 2026-09-26)
C:\Users\HP\miniconda3\envs\origin_hack\python.exe -m pytest tests\test_rainexposure.py tests\test_rainmodel.py tests\test_site_rain_la.py -q
C:\Users\HP\miniconda3\envs\origin_hack\python.exe -m streamlit run app\site_pages\rain_la.py
```

Downloads are skipped when cached. The build is deterministic (random_state 0, bootstrap and permutation seed 0): a full
rerun on 2026-09-26 reproduced `metrics.json` and `station_roses.json` exactly.

## 8. Sources (all accessed 2026-09-26)

1. Iowa Environmental Mesonet, ASOS request API. https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py
   Station metadata: https://mesonet.agron.iastate.edu/geojson/network/CA_ASOS.geojson
   Licence: public domain (https://mesonet.agron.iastate.edu/disclaimer.php).
   Precipitation note ("conservative over time when summed"): https://mesonet.agron.iastate.edu/ASOS/precipnote.phtml
2. Open-Meteo Historical Weather API (ERA5). https://open-meteo.com/en/docs/historical-weather-api ; endpoint
   https://archive-api.open-meteo.com/v1/archive . ERA5: Hersbach et al. 2023, Copernicus Climate Change Service /
   ECMWF, https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels (DOI 10.24381/cds.adbb2d47; CDS page
   not opened).
3. Open-Meteo Previous Runs API. https://open-meteo.com/en/docs/previous-runs-api ; endpoint
   https://previous-runs-api.open-meteo.com/v1/forecast . Terms: CC BY 4.0, free tier non-commercial,
   https://open-meteo.com/en/terms . "Weather data by Open-Meteo.com".
4. NOAA NCEI Access Data Service: daily-summaries (GHCN-Daily PRCP) and normals-annualseasonal-1991-2020.
   https://www.ncei.noaa.gov/access/services/data/v1 ; station search
   https://www.ncei.noaa.gov/access/services/search/v1/data . US federal data.
5. Blocken B, Carmeliet J (2010). Overview of three state-of-the-art wind-driven rain assessment models and comparison
   based on model theory. Building and Environment. Source of the ISO 15927-3 method 1 formulas (eq. 3, 5-9), Table 1
   roughness and Table 2 obstruction. Preprint:
   http://www.urbanphysics.net/2010_BAE_BB_JC_2010_WDRcomp_review__Preprint.pdf
6. NWS Service Change Notice 24-47, Downtown Los Angeles observing site move (KCQT to FHMC1, 2024-05-20).
   https://www.weather.gov/media/notification/pdf_2023_24/scn24-47_downtown_los_angeles_observing_site_move.pdf
7. NWS, ASOS wind sensor (2-minute average, 10-degree direction, calm at 2 kt or less).
   https://www.weather.gov/asos/WindSensor.html
8. ISO 15927-3:2009, Hygrothermal performance of buildings, Part 3: driving rain index from hourly wind and rain data.
   https://www.iso.org/standard/44281.html (paywalled; HTTP 403; not read).
9. Blocken B, Carmeliet J (2010), as [5]: measured catch coefficients on buildings of 0.02-0.26 s/m.
10. Blocken B, Carmeliet J (2004). A review of wind-driven rain research in building science. J Wind Eng Ind Aerodyn
    92:1079-1130. Preprint: https://urbanphysics.net/2004_JWEIA_WDRreview_preprint.pdf
11. scikit-learn, BSD-3-Clause. https://github.com/scikit-learn/scikit-learn/blob/main/COPYING
