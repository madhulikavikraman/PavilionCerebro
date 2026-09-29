# 12. Exterior facade screening and interior wall testing

Status: built and measured on 2026-09-26. Key: `facade`. Pages: `app/site_pages/exterior_inspection.py` and `app/site_pages/interior_walls.py`.

## Question

The user asked (ASK 2): "our crack detection from the previous build is ready, mold it to have it done for the exterior inspection of the buildings, research for the data captured for interior testing of the walls and make a ML model for that."

We split this into two questions:

1. Can a small local model screen a whole facade photo for cracks fast enough to pick the tiles the existing VLM grader (`facade_ll11` rubric) should look at? Does it hold up on real facades it never saw?
2. What data does interior wall testing produce? For which method is there a real public dataset good enough to train and honestly test a model?

## What we found

**Exterior practice**

- NYC FISP (1 RCNY 103-04) rates each significant condition Safe, SWARMP or Unsafe. The rule says drones, high-resolution photography and non-destructive testing do not eliminate the close-up inspection requirement [1]. So the screen is triage for the inspector (QEWI) and never a filing.
- California has two relevant laws:
  - SB 721 (HSC 17973) [2] covers wood-supported exterior elevated elements.
  - SB 326 (Civ. 5551) [3] covers the same for condominiums.
  - Both target wood-supported members. Our screen was trained and tested only on concrete, masonry and render cracks, so these laws are out of its scope.
- San Francisco runs a facade program under SFEBC Chapter 5F [4].
- We found no City of LA periodic high-rise facade ordinance. That is absence of evidence, not proof.

**Facade image data (licences read at source)**

| Dataset | Content | Licence | Use here |
|---|---|---|---|
| Özgenel [5] | concrete crack tiles; filenames carry no source-photo ids | CC BY 4.0 | training only (it cannot be split without leakage) |
| SDNET2018 walls [6] | tiles with the source photo in each filename | CC BY 4.0 | train, validation and test split by source photo |
| BFDD [7] | real drone facade photos with pixel masks | CC BY 4.0 | out-of-domain (OOD) test |

- BFDD's archive has no README. The class order on its landing page, the thin shapes, and our own red overlay check (`eval/facade/bfdd_label_check.jpg`) all say that label value 1 means crack. That reading is inferred, not documented.
- Hugging Face crack checkpoints fall into three groups:
  - self-reported on unnamed or re-hosted data (for example dima806);
  - copyleft (AGPL YOLOv8 crack-seg);
  - lab-only.

  None is used or scored here.

**Interior wall testing**

The table on the interior page is written by `scripts/interior/write_methods_table.py` to `eval/interior/methods_table.json`.

- **Moisture meters** read on meter-specific scales [8].
- **IR thermography** gives thermograms and temperature differences, not moisture content [9][10].
- **RH probes** give time series [11][12].
- **Rebound hammer and UPV** give RN and Vp, paired with core or cube strength [13][14].
- **GPR, impact echo and sounding** produce radargrams, spectra and marked areas [10][15].
- **Mold sampling** is usually unnecessary when growth is visible [16].

Only rebound hammer and UPV have a large public labelled dataset:

- The Matthews et al. NDT databases (CC BY 4.0) [13] give 3,299 SonReb rows from 53 studies after cleaning, 544 of them in-situ from 14 studies.
- The BAM round-robin drilled cores (CC0) [14][17] are an external set that is not in that database.

## What we built

**A. Facade tile crack classifier** (`scripts/facade/*.py`, `src/cascade/facade/`)

- **Data.**
  - `download_data.py` fetches all three datasets and verifies the sha256 where the publisher gives one.
  - SDNET gives a Cloudflare 403 to a plain GET. A single open-ended curl range request works (observed 2026-09-26).
- **Manifest.** `build_manifest.py` builds the manifest.
  - SDNET walls: 72 source photos, shuffled with seed 0 and split 60/20/20 into 44 train, 14 val and 14 test photos.
  - Özgenel: train only.
  - BFDD: 224 px windows at native resolution with stride 224, the same geometry the website uses.
    - A window is crack if it has at least 20 label-1 pixels and no crack if it has 0. Windows with 1-19 pixels are dropped.
    - The group is the flight (10 flights).
- **Training.** `train_tilecls.py` runs on the RTX 4060.
  - timm `resnet18.a1_in1k`, 4 epochs, AdamW, class-weighted cross-entropy.
  - Augmentation runs batched on the GPU from a pre-decoded memmap (`cache_tiles.py`), because per-file JPEG reads starved the GPU on this shared laptop.
  - The checkpoint is chosen by validation AP.
  - An ablation with the same recipe trains on Özgenel only.
- **Export.** `export_onnx.py` writes ONNX opset 17.
  - The fp32 file has max |logit diff| 7.5e-6 against PyTorch.
  - The shipped `models/facade/tilecls_resnet18_v1.onnx` stores weights as fp16 with Casts, so compute stays fp32. It is 22.4 MB, with max |p diff| 0.0025.
- **Evaluation.** `eval_tilecls.py` runs in the app env.
  - Baselines: constant guess, the repo heuristic `cascade.measure.crack_mask` (fraction of pixels flagged), and the ablation.
  - The threshold is chosen on the validation photos only. The rule is the highest threshold with validation recall ≥ 0.90, which gives p = 0.2050.
  - 95% CIs come from 1,000 bootstrap resamples of whole photos or flights.
  - These metrics are scored from the PyTorch checkpoint's predictions. `onnx_rescore.py` re-scores the same rows with the shipped ONNX file the website runs (results below).
- **Runtime.**
  - `heatmap.py` handles the onnxruntime session, window scoring, overlay, and the top-K review list.
    - With side-by-side windows (the default) every window is eligible, including edge-flush windows that overlap a neighbour, because they also cover pixels no other window does. An earlier version applied NMS at IoU 0.3 here, which capped a 640x512 frame at 6 of its 9 squares and could hide a cracked edge row.
    - With half-overlapping windows NMS at IoU 0.3 still applies, and the page shows how many distinct squares are available.
  - `review.py` glues tiles to `cascade.grade.grade_image(asset_class="facade_element")`. It calls the grader only when `ANTHROPIC_API_KEY` is set (the repo `.env` sets it on the team laptop) and the page sends crops only after the user ticks a confirmation box; without a key it shows a notice.
  - Grader accuracy on facade photos is unmeasured. `cascade.evalmetrics.TRUTH_SOURCE["facade_element"]` records that no public labelled set of FISP Safe / SWARMP / Unsafe photos exists, and the page prints that next to the grader button and the graded table.
  - It also glues tiles to `cascade.measure.measure_crack`, which gives mm only with a scale.
  - Review notes always start as "pending human review".
- **Samples.** `make_samples.py` bundles 3 BFDD test frames (CC BY 4.0) chosen by a fixed rule: the 90th, 50th and 10th percentiles of labelled crack area. Their labelled-crack overlays are bundled with them.

**B. Interior strength estimator** (`scripts/interior/*.py`, `src/cascade/interior/`)

- **Model.** A SonReb power law, ln fc = a + b ln RN + c ln Vp, fitted by least squares.
  - Challenger: HistGradientBoosting on (RN, Vp).
  - Single-instrument fallbacks: RN-only on the rebound database and Vp-only on the UPV database.
- **Per-building calibration.** Shift the prediction by the mean log residual of k cores.
- **Intervals.** Split-conformal 90% on |ln residual|.
  - The quantile is always set on studies other than the one being scored.
  - A separate quantile table applies after k-core calibration.
- **Field readings.** `readings.py` defines the pydantic `FieldReading` schema, and `data/interior/field_readings_template.csv` is the CSV template.
  - Rebound and UPV rows go to the estimator.
  - Moisture and RH rows are graded by rules from `interior_water.json` and `WOOD_MC_MAX`. A reading with no rubric row becomes U, never "dry".

## Measured results (copied from artifacts)

All data is REAL. There are no synthetic rows in any evaluation.

### A. Facade screen

Source: `eval/facade/tilecls_v1.json`. The threshold comes from SDNET validation (14 photos, n=3,522).

**SDNET2018 walls, held-out source photos (in-domain)**

n=3,529 tiles (787 crack, 2,742 no crack), 14 photos.

| Model | AUROC [95% CI] | AP [95% CI] | Precision | Recall | F1 | Tiles skipped |
|---|---|---|---|---|---|---|
| Constant guess | 0.500 | 0.223 | n/a | 0.000 | 0.000 | 100% |
| Repo heuristic `crack_mask` | 0.642 [0.594, 0.713] | 0.361 [0.304, 0.446] | 0.223 | 1.000 | 0.365 | 0% |
| ResNet-18, Özgenel only | 0.749 [0.688, 0.825] | 0.497 [0.415, 0.606] | 0.329 | 0.784 | 0.464 | 46.9% |
| **ResNet-18, Özgenel + SDNET (shipped)** | **0.918 [0.890, 0.946]** | **0.852 [0.822, 0.884]** | 0.592 | 0.839 | 0.694 | 68.4% |

**BFDD drone facades (OOD)**

n=7,454 windows (6,485 crack, 969 no crack), 10 flights. The crack prevalence is 0.870, so AP starts at 0.870 for a constant guess.

| Model | AUROC [95% CI] | AP [95% CI] | Precision | Recall | F1 | Tiles skipped |
|---|---|---|---|---|---|---|
| Constant guess | 0.500 | 0.870 | n/a | 0.000 | 0.000 | 100% |
| Repo heuristic `crack_mask` | 0.445 [0.400, 0.504] | 0.850 [0.776, 0.920] | 0.870 | 1.000 | 0.930 | 0% |
| ResNet-18, Özgenel only | 0.656 [0.599, 0.719] | 0.925 [0.876, 0.962] | 0.886 | 0.971 | 0.927 | 4.7% |
| **ResNet-18, Özgenel + SDNET (shipped)** | **0.906 [0.881, 0.914]** | **0.984 [0.974, 0.989]** | 0.940 | 0.932 | 0.936 | 13.8% |

Where it loses or is weak:

- On SDNET only 59.2% of flagged tiles are cracks, and 16.1% of cracked tiles are missed at the validation threshold. Validation recall was 0.90; test recall is 0.839.
- On BFDD the screen skips only 13.8% of windows, because most windows contain cracks.
- The repo heuristic scores below the constant guess on drone photos.
- The Özgenel-only ablation is far weaker in both domains. Close-range Özgenel tiles alone do not transfer.

**Shipped ONNX file vs PyTorch checkpoint (same rows, same threshold)**

Source: `eval/facade/onnx_rescore.json`. The tables above are scored from PyTorch checkpoint predictions (training env, fp16 autocast). The website runs `models/facade/tilecls_resnet18_v1.onnx` in onnxruntime on CPU, so `scripts/facade/onnx_rescore.py` re-scored every validation and test row with that file at the card threshold p = 0.2050.

| Set | n | Source | AUROC | AP | Precision | Recall | Tiles skipped |
|---|---|---|---|---|---|---|---|
| SDNET validation photos | 3,522 | PyTorch checkpoint | 0.937 | 0.888 | 0.607 | 0.901 | 64.4% |
| SDNET validation photos | 3,522 | shipped ONNX | 0.937 | 0.888 | 0.607 | 0.900 | 64.4% |
| SDNET test photos | 3,529 | PyTorch checkpoint | 0.918 | 0.852 | 0.592 | 0.839 | 68.4% |
| SDNET test photos | 3,529 | shipped ONNX | 0.918 | 0.852 | 0.593 | 0.837 | 68.5% |
| BFDD drone windows (OOD) | 7,454 | PyTorch checkpoint | 0.906 | 0.984 | 0.940 | 0.932 | 13.8% |
| BFDD drone windows (OOD) | 7,454 | shipped ONNX | 0.906 | 0.984 | 0.940 | 0.932 | 13.8% |

- SDNET validation photos: max |p diff| 0.0144, mean 0.00062; 4 of 3,522 tiles change side of the threshold.
- SDNET test photos: max |p diff| 0.0126, mean 0.00062; 5 of 3,529 tiles change side of the threshold.
- BFDD drone windows (OOD): max |p diff| 0.0048, mean 0.00034; 4 of 7,454 tiles change side of the threshold.
- The threshold the ONNX validation scores would pick is 0.2040; the page keeps the card threshold.

Latency:

- onnxruntime CPU in the app env: 30.95 ms per tile (4 threads, 256 tiles), measured while the laptop was shared with other heavy jobs.
- PyTorch GPU fp16: 0.368 ms per tile.
- A 640x512 BFDD frame is 9 windows.

### B. Interior strength

Source: `eval/interior/ndt_strength_v1.json`. The split is leave-one-study-out (LOSO) over 53 studies.

| Model | MAE all rows (n=3,299) | MAE in-situ rows (n=544, 14 studies) | In-situ per-study macro MAE |
|---|---|---|---|
| Training mean | 10.93 | 14.37 | 12.99 |
| RN-only power law (fitted on SonReb rows) | 8.71 | 12.23 | 9.54 |
| Vp-only power law (fitted on SonReb rows) | 9.49 | 10.06 | 10.07 |
| **SonReb power law (shipped)** | **7.98** | **9.65** (MAPE 46.8%) | 8.56 |
| HGB (RN, Vp) challenger | 8.86 | 10.48 | 9.26 |

All values are in MPa. The challenger lost to the power law, so the power law ships.

**Calibration with k same-study specimens**

These are labelled specimens from the same study, mostly lab cubes, standing in for cores. Each study gets 20 draws. Pooled MAE in MPa:

| Rows | Studies | k=0 | k=1 | k=3 | k=5 |
|---|---|---|---|---|---|
| All | 52 | 7.99 | 6.67 | 5.53 | 5.13 |
| In-situ | 12 | 9.79 | 6.68 | 5.47 | 4.97 |

**Conformal 90% intervals**

The quantile comes from inner GroupKFold on training studies only, and coverage is measured on the held-out study.

| | Row coverage | In-situ row coverage | Median width factor |
|---|---|---|---|
| No cores (k=0) | 0.890 | 0.879 | ×/÷ 1.97 |
| After 3-core calibration | 0.890 | 0.888 | ×/÷ 1.55 |

**Leakage contrast (HGB on RN, Vp)**

- Random 5-fold rows: R² 0.638.
- 5-fold GroupKFold by study: R² 0.349.
- Matthews et al. report R² 0.947 for SonReb (TPE-CatBoost) from 10-fold k-fold CV with no grouping by study stated (Section 4.1.3) [18]. That figure is comparable only with random-row numbers.

**External test: BAM cores (n=20)**

- NDT was measured in labs on the cores. The Original Schmidt "R" file is used for rebound.
- Core strength is multiplied by 0.968. That is the database's own fc,cyl/fc,core factor over 56 rows of ~100x200 mm cores.

| | MAE (MPa) | Notes |
|---|---|---|
| Global model | 9.92 | R² −1.96; it underpredicts every core |
| Training-mean baseline | 22.94 | |
| k=3-calibrated | 4.43 | scored on the other 17 cores, 20 draws; interval coverage 1.00 |

- The 20 cores span only 40.3 to 61.6 MPa, and the model underpredicts them systematically. That combination gives the negative R², and it is exactly the case where calibration against a few cores helps.
- The k=0 interval covered all 20 cores.
- Per lab-pair MAE ranges from 7.83 to 12.95 MPa.

**Single-instrument fallbacks (LOSO)**

| Fallback | Rows / studies | MAE | Mean-baseline MAE | In-situ rows / studies | In-situ MAE | In-situ mean-baseline MAE |
|---|---|---|---|---|---|---|
| RN-only on the rebound database | 10,428 / 85 | 14.03 | 21.43 | 3,042 / 23 | 14.47 | 22.50 |
| Vp-only on the UPV database | 6,103 / 88 | 9.62 | 11.50 | 1,328 / 25 | 8.61 | 11.14 |

These are the laws a user gets with only one reading. They differ from the RN-only and Vp-only baseline rows in the LOSO table above, which are fitted on SonReb rows; the page shows the fallback's own error next to a one-instrument estimate.

**Moisture.** No ML model is shipped. Moisture readings are rule-graded, and only some have a rule: RH spot readings below 60 %RH and leak sensors (EPA-based rows of `interior_water.json`) and wood moisture content (USDA FPL `WOOD_MC_MAX`). Pin or pinless readings on gypsum, concrete or plaster return U (cannot be graded) until a dry-reference rule exists (integration request to the rubric owner).

## Conclusions

1. **The facade screen is useful triage.**
   - On unseen SDNET photos it clearly beats the repo heuristic and the Özgenel-only model.
   - On real drone facades it ranks windows well (AUROC 0.906) with recall 0.932 at the validation threshold.
   - Its precision on SDNET (0.592) means inspectors will dismiss false alarms.
   - It is positioned as "look here first", never as a finding.
2. **In-domain training photos matter.** Adding in-domain SDNET training photos lifted held-out AUROC from 0.749 to 0.918 with the same architecture (model size was not varied).
3. **Rebound + UPV strength needs cores.**
   - Across held-out studies the typical miss on real structures is 9.65 MPa.
   - Three same-study specimens cut it to about 5.5 MPa.
   - The BAM external set shows the same pattern: 9.92 MPa uncalibrated, 4.43 MPa with 3 cores.
   - The product therefore always asks for cores before any decision.
4. **Split design dominates reported accuracy.** The same model loses about half its R² when whole studies are held out.

## Limits

- **Facade screen**
  - It was trained on close-range concrete tiles. Drone performance is only what one BFDD team's 10 flights measure.
  - There is no GSD rescaling. Window size is in pixels.
  - BFDD's value-to-class map is inferred.
- **Grader and width measurement**
  - Grader accuracy on facades is unmeasured: no public labelled FISP set exists. The tests never call the API. On a machine whose `.env` holds a key the button works, so the page labels the class a suggestion and asks for confirmation before sending crops.
  - Crack width uses the heuristic mask, which has no measured error on facades.
- **Strength model**
  - The database mixes lab cubes and in-situ tests from many countries.
  - The calibration experiment uses lab specimens as a stand-in for cores.
  - The BAM NDT was measured on cores in labs, not on the structure.
  - The power law is extrapolated outside the fitted RN and Vp ranges; the page flags this.
- **Latency** was measured on a laptop shared with other heavy jobs.

## How to rerun

Set the environment first: `HF_HOME=E:\hf_cache`, `TORCH_HOME=E:\torch_cache`, `TMP=TEMP=E:\tmp`, `PYTHONIOENCODING=utf-8`, `OMP_NUM_THREADS=4`.

App env (`C:\Users\HP\miniconda3\envs\origin_hack\python.exe`):

```
python scripts/facade/download_data.py --only ozgenel,bfdd,sdnet
python scripts/facade/build_manifest.py
python scripts/facade/cache_tiles.py
```

Training env (`E:\conda_envs\cerebro_ml\python.exe`):

```
python scripts/facade/train_tilecls.py --tag resnet18_ozg_sdnet --train-sets ozgenel,sdnet_walls
python scripts/facade/train_tilecls.py --tag resnet18_ozg_only --train-sets ozgenel
python scripts/facade/export_onnx.py --tag resnet18_ozg_sdnet
```

App env:

```
python scripts/facade/eval_tilecls.py
python scripts/facade/onnx_rescore.py
python scripts/facade/make_samples.py
python scripts/facade/write_sources.py
python scripts/interior/download_ndt.py
python scripts/interior/ndt_strength.py
python scripts/interior/write_methods_table.py
python -m pytest tests/test_facade_heatmap.py tests/test_interior_ndt.py tests/test_site_exterior_inspection.py tests/test_site_interior_walls.py -q
```

## Sources (accessed 2026-09-26)

1. NYC 1 RCNY 103-04 (FISP rule). https://www.nyc.gov/assets/buildings/rules/1_RCNY_103-04.pdf
2. California HSC 17973 (SB 721). https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=HSC&sectionNum=17973
3. California Civil Code 5551 (SB 326). https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=5551
4. SF DBI Facade Inspection and Maintenance Program. https://www.sf.gov/reports--june-2024--dbi-facade-inspection-and-maintenance-program
5. Özgenel, Concrete Crack Images for Classification, Mendeley 5y9wdsg2zt v2, CC BY 4.0. https://data.mendeley.com/datasets/5y9wdsg2zt/2
6. SDNET2018, Utah State University, CC BY 4.0. https://digitalcommons.usu.edu/all_datasets/48/
7. BFDD RGB-IR facade defect dataset, Mendeley 9ych7czvyg v1, CC BY 4.0. https://data.mendeley.com/datasets/9ych7czvyg/1
8. Protimeter, pin vs pinless meters. https://blog.protimeter.com/blog/comparing-pinless-moisture-meters-vs.-pin-moisture-meters
9. IRT and other techniques for wall moisture (Sensors, PMC9101659). https://pmc.ncbi.nlm.nih.gov/articles/PMC9101659/
10. IRT and GPR for moisture detection (Sensors, PMC7696806). https://pmc.ncbi.nlm.nih.gov/articles/PMC7696806/
11. Mikkonen and Vinha, timber-framed wall hygrothermal measurements, Zenodo 17778563, CC BY 4.0. https://zenodo.org/records/17778563
12. EPA, A brief guide to mold, moisture and your home. https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home
13. Matthews, Allaix, Wijte, Vullings, NDT concrete strength databases, Zenodo 15392443, CC BY 4.0. https://zenodo.org/records/15392443
14. Gebauer et al., BAM round-robin NDT data set, Harvard Dataverse doi:10.7910/DVN/AFCITK, CC0 1.0. https://doi.org/10.7910/DVN/AFCITK
15. FHWA SHRP2 R06A, NDT for concrete bridge decks. https://www.fhwa.dot.gov/goshrp2/Solutions/Construction/R06A/Nondestructive_Testing_for_Concrete_Bridge_Decks
16. EPA, Mold testing or sampling. https://www.epa.gov/mold/mold-testing-or-sampling
17. Gebauer et al. 2023, Data in Brief (PMC10196957). https://pmc.ncbi.nlm.nih.gov/articles/PMC10196957/
18. Matthews et al. 2026, NDT&E International 158, 103549 (TNO full text, CC BY 4.0). https://publications.tno.nl/publication/34645091/4b25FibC/matthews-2026-advancing.pdf
19. timm/resnet18.a1_in1k, Apache-2.0 tag. https://huggingface.co/timm/resnet18.a1_in1k
