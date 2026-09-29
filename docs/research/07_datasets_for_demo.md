# 07 - Public Datasets for the Damage-Detection / Grading Demo

Research note for Origin Weekend Fall 2026 (Prompt D). Written 2026-09-24 (Thu evening, LA).
Angle: which PUBLIC, DOWNLOADABLE image datasets can the team pull within hours to build the
small-VLM triage -> heavy-VLM detection + grading pipeline, and how to build a real held-out eval set.

Method: 10 web searches (the session's shared search budget then ran out) plus ~90 direct page fetches of
dataset landing pages, GitHub READMEs, figshare/Zenodo/HuggingFace JSON APIs, Europe PMC full text and arXiv/ar5iv.
Every number below carries a source URL (numbered [n] -> Sources section). Where a page could not be reached
(Kaggle and Roboflow Universe return 403 to non-browser fetchers; SINTEF's LIACi portal is a JS app) I say so.
Things I could not verify are marked "not found" or "Inference:". No interviews, surveys or testimonials are cited.

---

## Summary

- **Grading (severity) labels are rare in public data.** Of ~40 datasets checked, only six carry an ordinal severity/condition label:
  Corrosion Condition State (AASHTO Good/Fair/Poor/Severe) [12], xBD (4-level Joint Damage Scale) [31][33], RescueNet (No/Medium/Major/Total destruction) [35][36],
  ELPV (defect probability 0-1) [8], IDID insulators (good / flashover / broken) [67], and CAL FIRE DINS structure status for the 2025 LA fires [41].
  Everything else is detection/segmentation/classification of damage TYPE only. That gap is exactly where the product's "grading + prioritization" layer adds value.
- **Licensing is the trap.** Most academic sets are non-commercial (dacl10k CC BY-NC 4.0 [4][5]; CODEBRIM "other-nc" [7]; DTU Nordtank CC BY-NC 3.0 [13]; InsPLAD CC BY-NC [22][23][24];
  xBD CC BY-NC-SA 4.0 [33]; ELPV CC BY-NC-SA 4.0 [8]; GDXray research-only, no redistribution [28][29]). Commercial-OK options exist for every core asset class:
  SDNET2018 CC BY 4.0 [9], Ozgenel crack sets CC BY 4.0 [10][11], InfraredSolarModules MIT [1], Corrosion Condition State CC0 [12], COCO-Bridge 2021+ CC0 [14],
  TTPLA Apache-2.0 [25], UPID MIT [27], FloodNet CDLA-Permissive [37], SegCODEBRIM MIT [15], CAL FIRE DINS CC BY [41], Vantor/Maxar Open Data CC BY-NC 4.0 (imagery, NC) [40].
- **Recommended demo stack (3-day window):** (1) Corrosion Condition State - 440 images, CC0, 333 MB, the only true AASHTO grading set [12];
  (2) dacl10k validation split (975 of 9,920 real German bridge-inspection images, 19 classes, 5.29 GB total; NC license is fine for a demo) [4][5][6];
  (3) InfraredSolarModules - 20,000 thermal module crops, 12 anomaly classes, MIT, parquet mirror on HF [1][2]; (4) RescueNet - 4,494 UAV images with 4 building-damage levels [35][36].
  Optional: the Feb-2026 Scientific Data wind-turbine-blade set (1,065 images, 6 classes, VOC XML, CC BY-NC-ND 4.0) [17] and InsPLAD's fault-classification zip for power lines [22].
- **A real LA hook exists:** CAL FIRE's Palisades and Eaton Fire structure-status layers (CC BY, photos attached for damaged/destroyed structures) [41][42] plus Vantor (ex-Maxar) Open Data
  imagery of the same fires dated 9 Jan 2025 (CC BY-NC 4.0) [40]. Pairing these gives graded ground truth for a genuine post-disaster prioritization demo.
- **Wind turbine data is smaller than it looks.** DTU Nordtank is one turbine, 2017-2018, no counts or labels on the landing page [13]; labels come from third parties [18][19].
  Blade30 (1,302 images / 30 blades, direct Drive links) has no license statement [20]. The 2026 Sci Data set is the cleanest (1,568 boxes, 6 classes) but ND-licensed [17].
- **Thin verticals:** telecom towers (only RF100 "cell-towers", 1,008 images, 2 detection classes [30]), underwater pipelines (RF100 "underwater-pipes", 7,971 images, 1 class, no damage [30][38]),
  weld X-ray with severity (none found; GDXray welds = 98 images, RIAWELC download path not visible [28][29][3]). Position these as later verticals, not demo content.
- **Eval plan:** freeze a 180-image stratified held-out set from official test/val splits (40 corrosion / 60 dacl10k / 40 IR solar / 40 RescueNet), convert masks to image-level labels,
  team-label a 1-4 severity where the source lacks one (report inter-annotator kappa), and report precision/recall/F1, within-one-grade accuracy and quadratic-weighted kappa with bootstrap CIs.
  n=180 gives roughly +/-5 to +/-7 points of 95% CI; say so on the slide rather than claiming more.

---

## Detailed findings

### 0. License quick reference (commercial use?)

| Dataset | License | Commercial OK? | Source |
|---|---|---|---|
| InfraredSolarModules (Raptor Maps) | MIT | Yes | [1] |
| SDNET2018 | CC BY 4.0 | Yes | [9] |
| Concrete Crack Images for Classification / Segmentation (Ozgenel) | CC BY 4.0 | Yes | [10][11] |
| Corrosion Condition State (Bianchi & Hebdon) | CC0 (figshare API); code repo MIT | Yes | [12][16] |
| COCO-Bridge 2021+ | CC0 | Yes | [14] |
| SegCODEBRIM | MIT | Yes | [15] |
| TTPLA | Apache-2.0 | Yes | [25] |
| UPID (unified insulators) | MIT | Yes | [27] |
| FloodNet | CDLA-Permissive | Yes | [37] |
| CAL FIRE DINS structure status (Palisades/Eaton) | CC BY | Yes | [41][42] |
| HF "Solar-Panel-Thermal-Drone-UAV-Images" | Apache-2.0 | Yes (labels unclear) | [39] |
| DTU thermography WTB (2023), DTU Riso video (2024) | CC BY 4.0 | Yes | [21][44] |
| dacl10k | CC BY-NC 4.0 (official); HF mirror mislabels CC BY 4.0 | No | [4][5][54] |
| CODEBRIM | "other-nc" (non-commercial/educational) | No | [7] |
| DTU Nordtank drone images; YOLO-annotated derivative | CC BY-NC 3.0 | No | [13][19] |
| InsPLAD | CC BY-NC 3.0 (GitHub LICENSE, Mendeley) / CC BY-NC-SA 4.0 (project page) | No | [22][23][24][65] |
| xBD / xView2 | CC BY-NC-SA 4.0 | No | [33] |
| ELPV | Images CC BY-NC-SA 4.0; code Apache-2.0 | No (contact maintainers) | [8] |
| RescueNet | CONFLICT: GitHub README says CC BY-NC-ND; Sci Data paper says CC BY 4.0 | Verify | [35][36] |
| LIACi | CONFLICT: abstract summary says CC BY; earlier project text says "noncommercial" | Verify | [45][46][47] |
| GDXray+ | Research/educational only; redistribution and commercial use prohibited | No | [28][29] |
| DeepCrack | "RESTRICTED to non-commercial research and educational purposes" | No | [49] |
| Vantor (Maxar) Open Data imagery | CC BY-NC 4.0 | No | [40] |
| 2026 Sci Data WTB multiclass set | CC BY-NC-ND 4.0 | No (no derivatives) | [17] |
| Blade30, CPLID, CRACK500, RIAWELC, SUIM, IDID | Not stated on fetched pages | Unknown | [20][26][48][3][50][67] |

Inference: for the hackathon demo any of these is fine; for the pitch, say plainly that production training data will come from customer inspections, and that the public sets are used only for evaluation/bootstrapping.

### 1. Wind turbine blades

**DTU - Drone inspection images of wind turbine ("Nordtank")** - https://data.mendeley.com/datasets/hd96prn3nc/2 [13]
- Content: drone photos of a single Nordtank turbine at DTU Roskilde, years 2017 and 2018; version 2 published 26 Sep 2018; license CC BY NC 3.0 [13].
- Image count, resolution and labels are NOT on the landing page [13]; the Mendeley file API returned an empty list to our fetcher. The associated paper is Shihavuddin et al., Energies 2019 [43] (abstract has no counts).
  A 2026 Scientific Data review table lists that paper's data as 458 images at 4000x3000 with 4 defect types [17] - treat as indicative.
- Third-party labels: (a) imadgohar/DTU-annotations - bounding boxes, 70:15:15 split, test set in original HR and 1024-px slices, "Crack" class re-annotated for extreme aspect ratio; format not stated; license not stated [18].
  (b) "YOLO Annotated Wind Turbine Surface Damage" (Mendeley t6fwpc735s, 14 Sep 2021) - YOLO txt, 586x371 px, 2 classes "Dirt" and "Damage", re-annotated from the DTU set with makesense.ai, CC BY NC 3.0 [19]. A Kaggle copy exists (ajifoster3) but Kaggle returned 403 to the fetcher.
- Severity: none.

**Multiclass Dataset for Intelligent Detection of Wind Turbine Blade Defects Using Drone Imagery** (Scientific Data, Feb 2026) [17]
- 1,065 UAV blade images standardized to 1024x1024, 1,568 annotated instances, PASCAL VOC XML boxes; figshare DOI 10.6084/m9.figshare.30210175; CC BY-NC-ND 4.0 [17].
- Classes (instances): Surface_injure 394, Hide_craze 345, Craze 259, Corrosion 254, Crack 224, Thunderstrike 92 [17]. Severity: none.
- Caveat: ND license forbids redistributing derivatives; fine for internal evaluation.

**Blade30** - https://github.com/cong-yang/Blade30 [20]
- 1,302 real drone images covering 30 full blades, on- and offshore; per-image blade masks plus JSON "ground truth of defects and contaminations"; direct OneDrive and two Google Drive links in README [20]. Search snippets give ~5400x3600 px per image [51].
- License: none in README [20]. Defect/contamination class names not visible in fetched pages. Severity: none.

**DTU Wind Turbine Blade Damage Inspection Dataset using Thermography** (Mendeley jmm33c6dny v2, 3 May 2023, CC BY 4.0) - passive thermography of a fatigue-tested composite blade with embedded defects; counts not on landing page [21].
**2024 DTU Riso WTB inspection video dataset** (Mendeley 6nzbdvjn87, 22 Jan 2024, CC BY 4.0) - 29 videos (DJI Mavic 2) + frames + blade masks; for blade identification, not damage [44].
**HF**: ybli/yolo-wind-turbine-blade-falling-and-crack - 1 detection class, license unspecified [52]. Roboflow Universe search pages returned 403.

Inference: no public WTB set carries severity grades; the demo must have the heavy VLM assign a grade (e.g., a 1-5 scale with "repair within X months" semantics) and the team must hand-label the held-out set to measure it.

### 2. Solar PV (thermal / EL)

**InfraredSolarModules (Raptor Maps)** - https://github.com/RaptorMaps/InfraredSolarModules [1]
- 20,000 IR module crops at 24x40 px; 12 classes; JSON metadata; zip `2020-02-14_InfraredSolarModules.zip` in the repo; MIT license; ICLR 2020 AI for Earth Sciences workshop [1].
- Class counts: Cell 1,877; Cell-Multi 1,288; Cracking 941; Hot-Spot 251; Hot-Spot-Multi 247; Shadowing 1,056; Diode 1,499; Diode-Multi 175; Vegetation 1,639; Soiling 205; Offline-Module 828; No-Anomaly 10,000 [1].
- HF parquet mirror `tester202405/InfraredSolarModules`: 16,000 train / 4,000 test rows, same 12 labels [2].
- Severity: none explicit. Inference: anomaly class maps naturally to a severity table (Offline-Module / Diode-Multi = high; Hot-Spot = medium; Soiling / Shadowing = low, operational). The 24x40 resolution is a stress test for VLMs; upscale or tile before prompting.

**ELPV** - https://github.com/zae-bayern/elpv-dataset [8]
- 2,624 EL cell images, 300x300 8-bit grayscale, from 44 modules; label = defect probability in [0,1] plus mono/poly type; `pip install elpv-dataset`; images CC BY-NC-SA 4.0, code Apache-2.0 [8]. Only public PV set with a graded label.

**PVEL-AD** - https://github.com/binyisu/PVEL-AD [53]
- 36,543 EL images, 12 defect types, 40,358 ground-truth boxes; access only by hand-signed request form from an institutional e-mail, sent to the authors [53]. Not feasible inside a 3-day window.

**HF Manishsahu53/Solar-Panel-Thermal-Drone-UAV-Images** - Apache-2.0, size tag 10K<n<100K, DJI-drone thermal images of a plant in India, three zips; README gives no count, resolution or label format; annotations appear absent (tools for temperature extraction / hotspot detection are linked instead) [39]. Good for full-frame demo footage, not for scoring.
**Kaggle "Photovoltaic system thermography"** (marcosgabriel) exists but the page returned 403; details not verified.
**RF100 solar-panels-taxvb**: 161 images, 5 classes [30] - too small.

### 3. Concrete / bridge damage

**dacl10k** - toolkit https://github.com/phiyodr/dacl10k-toolkit [4]; catalog https://datasetninja.com/dacl10k [5]; paper arXiv 2309.00460 [6]
- 9,920 images from real German bridge inspections: train 6,935 / val 975 / test-dev 1,012 / test-challenge 998 [4]; average size 1,950x1,581 px; full download 5.29 GB, sample 404 MB [5].
- 19 classes: 13 damages (Crack, Alligator Crack, Wetspot, Efflorescence, Rust, Rockpocket, Hollowareas, Cavity, Spalling, Graffiti, Weathering, Restformwork, Exposed Rebars) + 6 components (Bearing, Expansion Joint, Drainage, Protective Equipment, Joint Tape, Washouts/Concrete corrosion) per toolkit [4]; the arXiv abstract says "12 damage classes" [6] - minor discrepancy between sources.
- Polygon annotations in modified labelme JSON [4]; top object counts: rust 14,720, spalling 9,884, cavity 9,271, weathering 4,634, efflorescence 3,965 [5]. Best benchmark mIoU 0.42 [6].
- Hosted on AWS S3 (`dacl10k.s3.eu-central-1.amazonaws.com`) and RWTH GigaMove [4]. License CC BY-NC 4.0 [4][5]. HF mirror `Voxel51/dacl10k` (8,922 images) is tagged CC BY 4.0 [54] - conflicts with the official license; treat official as controlling.
- Severity: none, but dacl's commercial product page markets DIN 1076 / VDI 6200 conformity [55] - Inference: the class taxonomy is designed to feed German condition grading.

**CODEBRIM** - https://zenodo.org/records/2620293 [7]; stats from ar5iv of CVPR 2019 paper [56]
- 1,590 high-res images from 30 bridges (larger side typically >4,000 px), 5,354 defect boxes (multi-label), 2,506 background boxes; classes: cracks 2,507, spallation 1,898, efflorescence 833, exposed bars 1,507, corrosion stains 1,559 [56].
- Files: original images 8.3 GB; cropped 7.9 GB; classification 7.9 GB; balanced 12.2 GB; license "other-nc" [7]. Published 1 Apr 2019 [7].
- **SegCODEBRIM** (Zenodo 10071534, Nov 2023): crack segmentation masks derived from CODEBRIM, 916.6 MB, MIT [15].

**SDNET2018** - https://digitalcommons.usu.edu/all_datasets/48/ [9]; Data in Brief paper [57]
- 56,092 sub-images at 256x256 from 230 originals (16 MP Nikon, 4068x3456): bridge decks 13,620 (2,025 cracked / 11,595 uncracked), walls 18,138 (3,851 / 14,287), pavements 24,334 (2,608 / 21,726) [57]; 503.8 MB zip; CC BY 4.0; DOI 10.15142/T3TD19 [9].

**Concrete Crack Images for Classification** (Ozgenel, Mendeley 5y9wdsg2zt v2, 23 Jul 2019): 40,000 images, 227x227, 20,000 per class, CC BY 4.0 [10]. **Concrete Crack Segmentation Dataset** (Mendeley jwsn7tfbrp, 3 Apr 2019): 458 hi-res images with binary masks, CC BY 4.0 [11].

**CRACK500** (pavement) - repo https://github.com/fyangneil/pavement-crack-detection [48]; stats from ar5iv 1901.06340 [58]
- 500 phone images ~2,000x1,500 px, pixel masks, cropped to 3,368 patches (train 1,896 / val 348 / test 1,124) [58]; Google Drive / OneDrive / Baidu links in repo; license not stated [48].
- Same paper documents GAPs384 (384 images 1920x1080), Cracktree200 (206 images 800x600), CFD (118 images 480x320), AEL (58 images) [58]. HF mirror `xcll/crack500_and_deepcrack` [59].

**DeepCrack** - https://github.com/yhlleo/DeepCrack [49]: manually annotated binary masks, `dataset/DeepCrack.zip` in repo; use restricted to non-commercial research [49]; image count not found in fetched pages.

**COCO-Bridge 2021+** (Virginia Tech, figshare 16624495, 7 Oct 2021): 1,470 annotated images, 4 structural-detail classes (bearings, cover plate terminations, gusset plate connections, out-of-plane stiffeners), bboxes in CSV/TXT/XML, 1,321 train / 136 test, 679.4 MB, CC0 [14]. Components, not damage - useful for "which element is this?" context.

**Not found / not usable:** CUBIT - no verifiable page found. "Bridge defect dataset" (Zenodo 20202242, May 2026) is Restricted with 0 downloads [60].

### 4. Corrosion / steel

**Corrosion Condition State Semantic Segmentation Dataset** (Bianchi & Hebdon, Virginia Tech) - figshare API record [12]; code https://github.com/beric7/corrosion_cs_classification [16]
- 440 finely annotated images (396 train / 44 test) from VDOT bridge inspection reports, labeled per AASHTO / BIRM corrosion condition states: Good, Fair, Poor, Severe [12]; 512x512 working resolution, labelme JSON -> masks [16].
- Files: Corrosion Condition State Classification.zip 333.4 MB + annotation guidelines PDF; published 13 Dec 2021; license CC0 [12]. Baseline DeepLabV3+ F1 86.67; trained weights at DOI 10.7294/16628668.v1 [12][16].
- **This is the single most valuable public set for the "grading" story**: real inspector-defined ordinal grades on real bridge steel.

**RF100 corrosion-bi3q3**: 1,249 images (840 train / 105 test / 304 valid), 3 classes [30]; HF mirror `LibreYOLO/corrosion-bi3q3` lists classes slippage / corrosion / crack, CC BY 4.0 [61]. RF100 download needs a Roboflow API key [62].
**HF imaadd05/steel-bridge-corrosion-pointer**: 514 field images with pixel masks, license unknown [61].
**"NEA corrosion"**: not found.

### 5. Underwater structures / hulls

**LIACi** (SINTEF) - project page [46]; paper DOI 10.1109/JOE.2022.3219129 [45][47]
- 1,893 pixel-annotated images from real underwater ship inspections; 10 categories incl. defects, corrosion, paint peel, marine growth, sea chest gratings, overboard valves, propeller, anodes, bilge keel, hull [45]. Project page lists 9 segmentation classes [46].
- Hosting: https://liaci.sintef.cloud (JavaScript app; returned "Loading..." to the fetcher) and data.sintef.no (Google-account registration required) [46]. License conflict: the abstract summary reports CC BY [45]; earlier project text says available "for noncommercial use" [47]. Verify at download.
- Severity: none, but "paint peel / corrosion / defect / marine growth" classes support a fouling-and-coating condition score (Inference).

**SUIM** - 1,525 train + 110 test images, 8 classes (wrecks/ruins, robots, reefs, etc.), pixel masks, Google Drive; license not stated [50][63]. Scene understanding, not damage.
**RF100 underwater-pipes-4ng4t**: 7,971 images, 1 class (pipe) [30]; HF mirror `LibreYOLO/underwater-pipes-4ng4t` CC BY 4.0 [38]. Detection only, no damage labels.
**Marine-growth synthetic segmentation (2025 paper)**: 1,038x2 rendered images, commissioned, no public link [64]. Underwater pipeline DAMAGE sets: not found.

### 6. Power lines / insulators / towers

**InsPLAD** - README [22]; Mendeley https://data.mendeley.com/datasets/5n3fjgvfyz/1 [23]; project page [24]
- 10,607 high-res UAV images, 28,933 annotated instances, 17 asset classes; 6 defects across 5 assets (4 corrosion, 1 broken component, 1 bird's nest) [22]; three zips: InsPLAD-det (detection), supervised_fault_classification, unsupervised_anomaly_detection [22]; published 5 Nov 2023 [23].
- License: CC BY-NC 3.0 in GitHub LICENSE and on Mendeley [23][65]; project page says CC BY-NC-SA 4.0 [24] - non-commercial either way. Asset-class names and per-defect counts were not in fetched pages.

**CPLID** - https://github.com/InsulatorData/InsulatorDataSet [26]: 600 normal UAV insulator images + 248 SYNTHETIC defective (missing shell) images, VOC2007 XML; IEEE DataPort copy 390.1 MB (login) [66]; license not stated. Synthetic defects weaken the demo's credibility - say so if used.
**IDID (IEEE DataPort competition, created Aug 2021, updated Apr 2025)**: classes good / flashover-damaged / broken insulator shell + insulator string; bbox CSV; train 2.26 GB, test 697.6 MB; login required; license not stated [67]. Three-state condition = a grading-like label.
**UPID** - merges CPLID + Tomaszewski set, COCO labels, Google Drive, MIT [27].
**TTPLA** - 1,100 images at 3,840x2,160, 8,987 instances of towers and lines, COCO pixel labels, Apache-2.0 [25][68]. No defects.
**HF**: `UPNAdroneLab/powerline_towers` (~1K images, txt labels, CC BY-NC-SA 4.0) [69]; `docmhvr/powerline-components-and-faults` (bbox, license unspecified) [70]; `silera/broken-insulators-synthetic-detection` (200+ synthetic, CC BY 4.0) [71]; Dataset Ninja "Insulator-Defect Detection" 2K images, 3 classes broken / pollution-flashover / insulator [72].

### 7. Weld radiographs / X-ray NDT

**GDXray+** - https://domingomery.ing.uc.cl/material/gdxray/ [28]; catalog [29]
- 20,966 X-ray images in 5 groups; Welds group = 98 images in 3 series from BAM Berlin; W0001/W0002 carry boxes for 641 defects plus binary GT; W0003 = 67 digitized round-robin radiographs [29]; Dropbox download on author site [28].
- Terms: free for research/education only; redistribution and commercial use prohibited [28][29]. Severity: none.

**RIAWELC** - https://github.com/stefyste/RIAWELC [3]: 24,407 PNG radiographic crops at 224x224, 4 classes (lack of penetration, porosity, cracks, no defect), "released freely"; no license file, no download link visible in README and no GitHub Releases [3][73]. Expect to e-mail the authors - risky for a 3-day window.
**HF visual weld sets** (not X-ray): `l985215117/welding-defect-object-detection` 2,028 images, 3 classes, CC0 [74]. No public weld X-ray set with severity found.

### 8. Disaster building damage

**xBD / xView2** - https://xview2.org/ (registration) [31]; paper arXiv 1911.09296 [32]; TorchGeo table [33]; baseline repo [34]
- 850,736 building polygons over 45,362 km2 of pre/post satellite imagery with ordinal damage labels [32]; 4 levels: 1 no damage, 2 minor, 3 major, 4 destroyed (0 = no building) [34]; PNG + JSON, 1024x1024 at 0.8 m (Maxar) [33][34]; ~10 GB compressed / 11 GB uncompressed [34]; CC BY-NC-SA 4.0 [33].
- Image-count sources disagree: 22,068 images [75] vs TorchGeo "3,732 samples" (likely one tier only) [33]. HF mirrors exist (e.g., `kshitijrajsharma/xview2-xbd`, tagged cc-by-nc-sa-4.0) [76].

**RescueNet** (Hurricane Michael, UAV) - GitHub README [35]; Scientific Data paper full text [36]
- 4,494 images at 3000x4000 (train 3,595 / val 449 / test 450); 11 classes incl. Building No Damage / Minor(Medium) / Major / Total Destruction, Road-Clear / Road-Blocked [35][36]; building polygon counts: no damage 4,011, medium 3,119, major 1,693, total destruction 2,080 [36]; figshare DOI 10.6084/m9.figshare.c.6647354.v1 and Dropbox [35][36].
- License conflict: README says CC BY-NC-ND [35]; paper says CC BY 4.0 [36].

**FloodNet** (Hurricane Harvey, UAV) - 2,343 images, 10 classes incl. Building Flooded / Non-Flooded, Road Flooded / Non-Flooded; CDLA-Permissive; Dropbox; 60/20/20 split [37].
**Post-hurricane satellite damage (Cao & Choe, Harvey)** - IEEE DataPort [77]: train 5,000 damaged + 5,000 undamaged; val 1,000 + 1,000; balanced test 1,000 + 1,000; unbalanced test 8,000 + 1,000; JPEG; 63 MB; login; license not stated. Kaggle mirror (kmader) blocked to fetcher.
**ISBDA** - only the MSNet abstract was reachable; no download or counts verified [78].
**2025 LA fires** - Vantor (ex-Maxar) Open Data confirms Palisades and Eaton imagery dated 9 Jan 2025, CC BY-NC 4.0, via discover.vantor.com [40]. CAL FIRE publishes "Palisades Fire Structure Status Map" and "Eaton Fire Structure Status Map" on data.ca.gov (CC BY; created 24 Jan 2025; updated 25 Sep 2026; photos "may only be available for damaged and destroyed structures"; contact dins.CALFIRE@fire.ca.gov) [41][42]. Damage-category values were not in the fetched page (Inference: DINS normally uses No Damage / Affected / Minor / Major / Destroyed - verify in the ArcGIS layer).

### 9. Telecom towers

- Only RF100 `cell-towers`: 1,008 images (705 / 101 / 202), 2 classes, detection only [30]. HF `tccx18/Towerdataset` is a LiDAR point-cloud corridor set (661 scenes) [79]. No public telecom-tower DEFECT imagery found. Inference: treat telecom as a "same model, new vertical" claim backed by the power-line results, not by data.

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| InfraredSolarModules image count / size / classes | 20,000 images, 24x40 px, 12 classes, MIT | https://github.com/RaptorMaps/InfraredSolarModules | 2020-02-14 |
| InfraredSolarModules No-Anomaly count | 10,000 of 20,000 | https://github.com/RaptorMaps/InfraredSolarModules | 2020-02-14 |
| HF mirror of InfraredSolarModules split | 16,000 train / 4,000 test | https://huggingface.co/api/datasets/tester202405/InfraredSolarModules | 2024-05-21 |
| ELPV size / label | 2,624 cells, 300x300, defect probability 0-1, CC BY-NC-SA 4.0 | https://github.com/zae-bayern/elpv-dataset | fetched 2026-09-24 |
| PVEL-AD size / access | 36,543 EL images, 40,358 boxes, 12 defects; signed request form | https://github.com/binyisu/PVEL-AD | fetched 2026-09-24 |
| dacl10k splits | 6,935 / 975 / 1,012 / 998 = 9,920 | https://github.com/phiyodr/dacl10k-toolkit | fetched 2026-09-24 |
| dacl10k size / resolution / license | 5.29 GB; avg 1,950x1,581; CC BY-NC 4.0 | https://datasetninja.com/dacl10k | fetched 2026-09-24 |
| dacl10k benchmark mIoU | 0.42 | https://arxiv.org/abs/2309.00460 | 2023-09 |
| CODEBRIM images / boxes | 1,590 images, 5,354 defect boxes, 2,506 background boxes, 30 bridges | https://ar5iv.labs.arxiv.org/html/1904.08486 | 2019-04 |
| CODEBRIM class counts | cracks 2,507; spallation 1,898; efflorescence 833; exposed bars 1,507; corrosion stains 1,559 | https://ar5iv.labs.arxiv.org/html/1904.08486 | 2019-04 |
| CODEBRIM download sizes | 8.3 / 7.9 / 7.9 / 12.2 GB; license other-nc | https://zenodo.org/api/records/2620293 | 2019-04-01 |
| SegCODEBRIM | 916.6 MB, MIT | https://zenodo.org/records/10071534 | 2023-11-04 |
| SDNET2018 total and per-subset | 56,092 imgs; decks 2,025/11,595; walls 3,851/14,287; pavements 2,608/21,726 | https://pmc.ncbi.nlm.nih.gov/articles/PMC6247444/ | 2018-11 |
| SDNET2018 zip / license | 503.8 MB, CC BY 4.0 | https://digitalcommons.usu.edu/all_datasets/48/ | 2018-05-17 |
| Ozgenel classification set | 40,000 imgs, 227x227, CC BY 4.0 | https://data.mendeley.com/datasets/5y9wdsg2zt/2 | 2019-07-23 |
| Ozgenel segmentation set | 458 hi-res imgs + masks, CC BY 4.0 | https://data.mendeley.com/datasets/jwsn7tfbrp/1 | 2019-04-03 |
| CRACK500 | 500 imgs ~2000x1500; 1,896 / 348 / 1,124 patches | https://ar5iv.labs.arxiv.org/html/1901.06340 | 2019-01 |
| Corrosion Condition State images / classes | 440 imgs (396/44); Good/Fair/Poor/Severe; CC0; 333.4 MB | https://api.figshare.com/v2/articles/16624663 | 2021-12-13 |
| Corrosion CS baseline F1 | 86.67 (DeepLabV3+) | https://api.figshare.com/v2/articles/16624663 | 2021-12-13 |
| COCO-Bridge 2021+ | 1,470 imgs, 4 classes, 679.4 MB, CC0 | https://api.figshare.com/v2/articles/16624495 | 2021-10-07 |
| RF100 corrosion-bi3q3 | 1,249 imgs, 3 classes | https://raw.githubusercontent.com/roboflow/roboflow-100-benchmark/main/metadata/datasets_stats.csv | fetched 2026-09-24 |
| RF100 underwater-pipes-4ng4t | 7,971 imgs, 1 class | same as above | fetched 2026-09-24 |
| RF100 cell-towers | 1,008 imgs, 2 classes | same as above | fetched 2026-09-24 |
| RF100 solar-panels-taxvb | 161 imgs, 5 classes | same as above | fetched 2026-09-24 |
| RF100 total | 224,714 images, API key required | https://raw.githubusercontent.com/roboflow/roboflow-100-benchmark/main/README.md | fetched 2026-09-24 |
| LIACi | 1,893 imgs, 10 classes | https://www.sintef.no/en/projects/2021/liaci/ | project 2021-2023 |
| SUIM | 1,525 train + 110 test, 8 classes | https://irvlab.cs.umn.edu/resources/suim-dataset | fetched 2026-09-24 |
| InsPLAD | 10,607 imgs, 28,933 instances, 17 assets, 6 defects | https://raw.githubusercontent.com/andreluizbvs/InsPLAD/main/README.md | 2023-11-05 |
| InsPLAD license (Mendeley) | CC BY NC 3.0 | https://data.mendeley.com/datasets/5n3fjgvfyz/1 | 2023-11-05 |
| CPLID | 600 normal + 248 synthetic defective, VOC | https://github.com/InsulatorData/InsulatorDataSet | 2018 paper |
| CPLID IEEE DataPort size | 390.1 MB | https://ieee-dataport.org/open-access/insulator-data-set-chinese-power-line-insulator-dataset-cplid | updated 2026-02-17 |
| IDID sizes | train 2.26 GB, test 697.6 MB; good/flashover/broken | https://ieee-dataport.org/competitions/insulator-defect-detection | updated 2025-04-27 |
| TTPLA | 1,100 imgs, 3840x2160, 8,987 instances, Apache-2.0 | https://arxiv.org/abs/2010.10032 ; https://github.com/R3ab/ttpla_dataset | 2020 |
| GDXray+ total / welds | 20,966 imgs; welds 98 imgs in 3 series; 641 defect boxes | https://datasetninja.com/gdxray | fetched 2026-09-24 |
| GDXray terms | research/education only; no redistribution or commercial use | https://domingomery.ing.uc.cl/material/gdxray/ | fetched 2026-09-24 |
| RIAWELC | 24,407 imgs, 224x224 PNG, 4 classes | https://github.com/stefyste/RIAWELC | 2022-10 |
| xBD polygons / area | 850,736 polygons; 45,362 km2 | https://arxiv.org/abs/1911.09296 | 2019-11 |
| xBD license / tile | CC BY-NC-SA 4.0; 1024x1024; 0.8 m | https://docs.torchgeo.org/en/stable/api/datasets.html | fetched 2026-09-24 |
| xBD download size | ~10 GB compressed / 11 GB uncompressed | https://github.com/DIUx-xView/xView2_baseline | fetched 2026-09-24 |
| RescueNet images / resolution / splits | 4,494 imgs; 3000x4000; 3,595/449/450 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10733412/fullTextXML | 2023-12 |
| RescueNet damage polygons | 4,011 / 3,119 / 1,693 / 2,080 | same as above | 2023-12 |
| FloodNet | 2,343 imgs, 10 classes, CDLA-Permissive | https://github.com/BinaLab/FloodNet-Supervised_v1.0 | 2021 |
| Harvey satellite damage (Cao & Choe) | 5k+5k train; 1k+1k val; 1k+1k / 8k+1k test; 63 MB | https://ieee-dataport.org/open-access/detecting-damaged-buildings-post-hurricane-satellite-imagery-based-customized | 2018-12-13 |
| Vantor Open Data LA fires | Palisades + Eaton imagery 9 Jan 2025; CC BY-NC 4.0 | https://vantor.com/company/open-data-program | 2025-01-09 |
| CAL FIRE Palisades structure status | CC BY; created 2025-01-24; updated 2026-09-25; photos for damaged/destroyed | https://data.ca.gov/dataset/palisades-fire-structure-status-map | 2026-09-25 |
| 2026 WTB multiclass set | 1,065 imgs 1024x1024; 1,568 boxes; 6 classes; VOC XML; CC BY-NC-ND 4.0; figshare 10.6084/m9.figshare.30210175 | https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12996307/fullTextXML | 2026-02 |
| 2026 WTB class counts | Surface_injure 394; Hide_craze 345; Craze 259; Corrosion 254; Crack 224; Thunderstrike 92 | same as above | 2026-02 |
| Blade30 | 1,302 imgs, 30 blades; direct Drive/OneDrive links; no license | https://github.com/cong-yang/Blade30 | 2023 |
| DTU Nordtank license | CC BY NC 3.0; v2 2018-09-26 | https://data.mendeley.com/datasets/hd96prn3nc/2 | 2018-09-26 |
| YOLO-annotated WTB derivative | 586x371; 2 classes; CC BY NC 3.0 | https://data.mendeley.com/datasets/t6fwpc735s/1 | 2021-09-14 |
| DTU thermography WTB set | CC BY 4.0 | https://data.mendeley.com/datasets/jmm33c6dny/2 | 2023-05-03 |
| DTU Riso video set | 29 videos, CC BY 4.0 | https://data.mendeley.com/datasets/6nzbdvjn87/1 | 2024-01-22 |
| HF solar thermal drone set | Apache-2.0; 10K<n<100K; labels unclear | https://huggingface.co/api/datasets/Manishsahu53/Solar-Panel-Thermal-Drone-UAV-Images | 2026-09-06 |
| HF Voxel51/dacl10k mirror | 8,922 imgs; tagged CC BY 4.0 (conflicts with official NC) | https://huggingface.co/api/datasets/Voxel51/dacl10k | 2024-05-06 |

---

## Recommendation: the 3-4 datasets to actually use, and why

Selection criteria: (a) downloadable in minutes without a request form, (b) real (not synthetic) inspection imagery, (c) carries or can be mapped to a severity grade, (d) covers a distinct asset class the pitch names, (e) license at least allows a research demo.

1. **Corrosion Condition State (steel bridges) - use as the flagship grading demo.** 333 MB, CC0, 440 images with AASHTO Good/Fair/Poor/Severe masks [12]. Convert masks to an image-level "worst condition state present" label and a % area per state. This is the one place where the heavy VLM's grade can be compared to an inspector's grade with zero hand labeling.
2. **dacl10k (concrete bridges) - use the 975-image validation split only** (avoid the 5.29 GB full pull if bandwidth is tight; the S3 dev-phase zip contains train+val [4]). 13 damage types on real inspection photos; polygon labels give damage presence and extent per class [4][5]. Non-commercial license is acceptable for a hackathon demo; note it on the data slide.
3. **InfraredSolarModules (PV thermal) - use the HF parquet mirror for speed** [2]. 12 anomaly classes incl. a 10,000-image No-Anomaly class = ideal for measuring the small-VLM triage stage's false-negative rate on "no damage" vs "damage" [1]. MIT.
4. **RescueNet (disaster, UAV) - use the 450-image test split** for the "rapidly prioritize recovery" half of Prompt D: 4 building damage levels + Road-Blocked [35][36]. UAV imagery matches the drone story better than xBD's satellite tiles, and no registration is needed (figshare/Dropbox). Verify license text inside the download because sources conflict [35][36].

Stretch (only if the four above are done by Saturday noon): the Feb-2026 WTB set (1,065 images, VOC XML, direct figshare) to show wind blades [17]; InsPLAD `supervised_fault_classification.zip` for power-line corroded/broken/bird-nest crops [22]; CAL FIRE DINS + Vantor imagery for a one-slide LA-fire prioritization example [40][41][42].

Skip for the demo: PVEL-AD (request form) [53], RIAWELC (no visible download) [3], CPLID (synthetic defects) [26], GDXray welds (98 images, no redistribution) [29], Kaggle-only sets (login), Roboflow Universe sets (API key + unknown per-dataset licenses) [62].

## Held-out evaluation set plan (so the deck reports MEASURED numbers)

Goal: one frozen `eval_v1` of ~180 images with ground truth, never used for prompt iteration, that supports three metric families: triage, detection, grading.

1. **Sampling (stratified, from official test/val splits only)**
   - Corrosion CS: all 44 official test images; if fewer than 10 per state, top up from train images that were not used for prompt development. Target 40. [12]
   - dacl10k val split: 60 images stratified by presence of Crack, Spalling, Rust, Exposed Rebars, Efflorescence, and 10 with no damage class (components only). [4]
   - InfraredSolarModules HF test split: 40 images = 15 No-Anomaly + 25 spread over the 11 anomaly classes (at least 2 each). [2]
   - RescueNet test split: 40 images, 10 per building damage level; crop 1024-px tiles centered on a labeled building so each tile has one dominant grade. [36]
2. **Ground truth derivation (script, not hand work)**
   - `damage_present` = any damage-class pixel/box in the tile (bool).
   - `classes_present` = set of damage classes (from polygons / JSON label).
   - `grade` = the native ordinal label where it exists: Corrosion CS state (1-4), RescueNet building level (1-4), IR-solar class mapped to a 3-tier severity table you define BEFORE looking at results. For dacl10k there is no grade: two teammates independently assign 1-4 using a written rubric (class + area fraction); keep both labels, report Cohen's kappa, and use the adjudicated label. Label these rows "team-graded" in the report.
3. **Freeze**: commit `eval_v1/manifest.jsonl` (file hash, source dataset, split, labels) before the first end-to-end run; keep a separate 50-image `dev` set for prompt tuning.
4. **Metrics to report (with n and 95% bootstrap CIs)**
   - Stage 1 (small VLM triage): precision, recall, F1 for `damage_present`; recall is the headline because a miss is a skipped inspection; also % of images routed to the heavy model and cost per 1,000 images.
   - Stage 2 (heavy VLM): per-class precision/recall and macro-F1 on `classes_present`.
   - Grading: exact-match accuracy, within-one-grade accuracy, mean absolute error on the 1-4 scale, quadratic-weighted kappa vs ground truth; confusion matrix per asset class.
   - Ops: median latency per image and $ per image at both stages (measured from API usage logs).
5. **Honesty guardrails**: n=180 total (about 40 per class) gives roughly +/-5 to +/-7 percentage points of 95% CI on an accuracy near 80-90% (Inference from the binomial approximation). Put "n=" on the slide; do not extrapolate to field performance; state that public sets are not customer imagery.

## Implications for our product / edge

- **Grading, not detection, is the white space in public data.** Nearly every public set stops at "what defect is this"; inspectors are paid to answer "how bad and what first". Only six public sets have ordinal grades [12][33][36][8][67][41]. Our differentiator is the grading + prioritization layer expressed in the customer's own scheme (AASHTO condition states for bridges [12]; DIN 1076-style classes that dacl targets [55]; xBD/DINS-style 4-5 level damage scales for disasters [34][41]). Demo this with Corrosion CS and RescueNet where real graded ground truth exists.
- **Cross-asset generality is demonstrable in 3 days.** A VLM pipeline can be shown on steel, concrete, PV thermal and post-disaster UAV imagery with zero per-asset training, which per-asset CNN products cannot claim without retraining. The datasets above make that a measured claim, not a slide claim.
- **The triage stage has a clean, measurable justification.** InfraredSolarModules is 50% No-Anomaly [1]; dacl10k images average 1,950x1,581 px [5]; RescueNet images are 3000x4000 [36]. Report the fraction of images the small model filters out and the resulting cost per image - a concrete unit-economics argument.
- **Licensing shapes the business-model narrative.** Because most quality sets are NC, the startup cannot ship a model trained on them commercially; the story must be "customers bring imagery, we bring grading rubrics + evaluation harness + workflow", with commercially licensed sets (SDNET2018 [9], InfraredSolarModules [1], Corrosion CS [12], COCO-Bridge [14], TTPLA [25]) used for bootstrapping. Say this before a judge asks.
- **Local, timely proof point**: CAL FIRE's DINS layers for Palisades/Eaton (CC BY, photos attached, still updated Sep 2026) [41][42] + Vantor imagery of the same fires [40] let the team show "prioritize recovery" on a disaster the judges lived through, with public ground truth.
- **Thin verticals to defer**: telecom towers (detection-only, 1,008 images) [30], underwater pipeline damage (none found), weld X-ray with severity (none found). List them as roadmap, backed by the power-line and hull results (InsPLAD [22], LIACi [45]) rather than data we do not have.

## Open questions / gaps

1. LIACi license: CC BY (abstract summary [45]) vs "noncommercial use" (earlier project text [47]); the download portal is a JS app requiring Google login [46] - confirm before using in the deck.
2. RescueNet license: CC BY-NC-ND on GitHub [35] vs CC BY 4.0 in the Scientific Data paper [36].
3. dacl10k: official CC BY-NC 4.0 [4][5] vs HF mirror tagged CC BY 4.0 [54]; also 12 vs 13 damage classes between abstract [6] and toolkit [4].
4. InsPLAD license variant (CC BY-NC 3.0 [23][65] vs CC BY-NC-SA 4.0 [24]); asset-class names and per-defect counts not retrieved.
5. Blade30 has no license statement [20]; class list not retrieved; ~5400x3600 resolution only from a search snippet [51].
6. DTU Nordtank image count and resolution are not on the landing page [13]; the Mendeley files API returned nothing; the 2019 paper abstract has no counts [43].
7. RIAWELC: no visible download link or license file [3][73]; likely e-mail-the-authors.
8. Kaggle (ajifoster3 WTB; marcosgabriel PV thermography; kmader hurricane) and Roboflow Universe pages all returned 403; details unverified; Roboflow needs an API key [62].
9. Corrosion CS: per-state image counts not retrieved (zip is 333 MB; count on download) [12].
10. DeepCrack image count not found in fetched pages [49]. ISBDA download not found [78]. CUBIT and "NEA corrosion" not found.
11. xBD image count conflict: 22,068 [75] vs 3,732 samples in TorchGeo [33].
12. CAL FIRE DINS damage-category schema not in the fetched catalog page [41]; check the ArcGIS layer fields.
13. IEC 62446-3 thermal-abnormality classes as a PV grading rubric: not fetched in this session; verify the standard's class definitions before citing it on a slide.
14. HF solar-thermal drone set: image count, format (radiometric JPEG?) and presence of labels unknown [39].

## Sources

1. https://github.com/RaptorMaps/InfraredSolarModules - Raptor Maps IR module dataset README (20k images, 12 classes, MIT).
2. https://huggingface.co/api/datasets/tester202405/InfraredSolarModules - HF parquet mirror metadata (16k/4k split).
3. https://github.com/stefyste/RIAWELC - RIAWELC weld radiograph dataset README.
4. https://github.com/phiyodr/dacl10k-toolkit - dacl10k toolkit: splits, classes, download hosts, CC BY-NC 4.0.
5. https://datasetninja.com/dacl10k - dacl10k catalog entry: size 5.29 GB, resolution, object counts, license.
6. https://arxiv.org/abs/2309.00460 - dacl10k paper abstract (WACV 2024).
7. https://zenodo.org/api/records/2620293 - CODEBRIM Zenodo record (files, sizes, other-nc license).
8. https://github.com/zae-bayern/elpv-dataset - ELPV EL cell dataset README.
9. https://digitalcommons.usu.edu/all_datasets/48/ - SDNET2018 repository page (CC BY 4.0, 503.8 MB).
10. https://data.mendeley.com/datasets/5y9wdsg2zt/2 - Concrete Crack Images for Classification (Ozgenel).
11. https://data.mendeley.com/datasets/jwsn7tfbrp/1 - Concrete Crack Segmentation Dataset (458 images).
12. https://api.figshare.com/v2/articles/16624663 - Corrosion Condition State dataset figshare metadata (CC0, 440 images, 333.4 MB).
13. https://data.mendeley.com/datasets/hd96prn3nc/2 - DTU Drone inspection images of wind turbine (Nordtank), CC BY NC 3.0.
14. https://api.figshare.com/v2/articles/16624495 - COCO-Bridge 2021+ figshare metadata (CC0, 1,470 images).
15. https://zenodo.org/records/10071534 - SegCODEBRIM (MIT, 916.6 MB).
16. https://github.com/beric7/corrosion_cs_classification - Corrosion CS code repo (classes, labelme format, weights DOI).
17. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12996307/fullTextXML - Scientific Data 2026 multiclass WTB defect dataset full text (counts, VOC, figshare DOI, CC BY-NC-ND).
18. https://github.com/imadgohar/DTU-annotations - third-party bounding-box annotations for the DTU set.
19. https://data.mendeley.com/datasets/t6fwpc735s/1 - YOLO Annotated Wind Turbine Surface Damage (586x371, 2 classes, CC BY NC 3.0).
20. https://github.com/cong-yang/Blade30 - Blade30 README (1,302 images, Drive/OneDrive links).
21. https://data.mendeley.com/datasets/jmm33c6dny/2 - DTU WTB damage inspection dataset using thermography (CC BY 4.0).
22. https://raw.githubusercontent.com/andreluizbvs/InsPLAD/main/README.md - InsPLAD README (10,607 images, 28,933 instances, zips).
23. https://data.mendeley.com/datasets/5n3fjgvfyz/1 - InsPLAD Mendeley record (CC BY NC 3.0, 2023-11-05).
24. https://andreluizbvs.github.io/InsPLAD/ - InsPLAD project page (states CC BY-NC-SA 4.0).
25. https://github.com/R3ab/ttpla_dataset - TTPLA repo (Apache-2.0, COCO labels).
26. https://github.com/InsulatorData/InsulatorDataSet - CPLID (600 normal + 248 synthetic defective, VOC).
27. https://github.com/heitorcfelix/public-insulator-datasets - UPID unified insulator dataset (MIT, COCO).
28. https://domingomery.ing.uc.cl/material/gdxray/ - GDXray+ official page (terms, Dropbox link).
29. https://datasetninja.com/gdxray - GDXray+ catalog entry (20,966 images; welds 98 images / 3 series / 641 boxes).
30. https://raw.githubusercontent.com/roboflow/roboflow-100-benchmark/main/metadata/datasets_stats.csv - RF100 per-dataset counts (corrosion, solar, underwater pipes, cell towers).
31. https://xview2.org/ - xView2 challenge site (registration for xBD download).
32. https://arxiv.org/abs/1911.09296 - xBD paper abstract (850,736 polygons, 45,362 km2).
33. https://docs.torchgeo.org/en/stable/api/datasets.html - TorchGeo dataset table (xBD: CC-BY-NC-SA-4.0, 1024 px, 0.8 m).
34. https://github.com/DIUx-xView/xView2_baseline - xView2 baseline README (damage levels 0-4, ~10 GB).
35. https://github.com/BinaLab/RescueNet-A-High-Resolution-Post-Disaster-UAV-Dataset-for-Semantic-Segmentation/blob/main/README.md - RescueNet README (classes, CC BY-NC-ND, links).
36. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10733412/fullTextXML - RescueNet Scientific Data full text (3000x4000, splits, damage polygon counts, CC BY 4.0).
37. https://github.com/BinaLab/FloodNet-Supervised_v1.0 - FloodNet (2,343 images, 10 classes, CDLA-Permissive).
38. https://huggingface.co/api/datasets?search=underwater&limit=40 - HF search: underwater-pipes mirror (7,971 images, CC BY 4.0) and others.
39. https://huggingface.co/api/datasets/Manishsahu53/Solar-Panel-Thermal-Drone-UAV-Images - HF thermal PV drone images metadata (Apache-2.0).
40. https://vantor.com/company/open-data-program - Vantor (ex-Maxar) Open Data: Palisades/Eaton imagery 9 Jan 2025, CC BY-NC 4.0.
41. https://data.ca.gov/dataset/palisades-fire-structure-status-map - CAL FIRE Palisades Fire structure status (CC BY, photos for damaged/destroyed).
42. https://data.ca.gov/dataset?q=DINS+damage+inspection - data.ca.gov listing incl. Eaton Fire structure status map (CC BY).
43. https://api.semanticscholar.org/graph/v1/paper/DOI:10.3390/en12040676?fields=title,abstract,year,venue - Shihavuddin et al. 2019 Energies abstract (DTU Nordtank paper).
44. https://data.mendeley.com/datasets/6nzbdvjn87/1 - 2024 DTU Riso WTB inspection video dataset (CC BY 4.0).
45. https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/JOE.2022.3219129?fields=title,abstract,year,venue,externalIds - LIACi paper abstract (1,893 images, 10 classes; CC BY per summary).
46. https://www.sintef.no/en/projects/2021/liaci/ - LIACi project page (liaci.sintef.cloud, data.sintef.no, Google login).
47. https://www.sintef.no/en/publications/publication/2071613/ - LIACi publication record (DOI, handle).
48. https://github.com/fyangneil/pavement-crack-detection - CRACK500 / FPHB repo (download links).
49. https://github.com/yhlleo/DeepCrack - DeepCrack repo (non-commercial restriction, dataset zip).
50. https://irvlab.cs.umn.edu/resources/suim-dataset - SUIM dataset page.
51. https://www.sciencedirect.com/science/article/abs/pii/S0045790624005421 - paper using Blade30 (search snippet: 1,302 images ~5400x3600).
52. https://huggingface.co/api/datasets?search=wind%20turbine&limit=20 - HF search for WTB datasets.
53. https://github.com/binyisu/PVEL-AD - PVEL-AD README (36,543 images; request form).
54. https://huggingface.co/api/datasets/Voxel51/dacl10k - HF dacl10k mirror metadata (8,922 images, tagged CC BY 4.0).
55. https://dacl.ai/ - dacl commercial page (DIN 1076 / VDI 6200 conformity claim).
56. https://ar5iv.labs.arxiv.org/html/1904.08486 - CODEBRIM CVPR 2019 paper (1,590 images, 5,354 boxes, class counts).
57. https://pmc.ncbi.nlm.nih.gov/articles/PMC6247444/ - SDNET2018 Data in Brief (per-subset counts, camera).
58. https://ar5iv.labs.arxiv.org/html/1901.06340 - FPHB paper (CRACK500, GAPs384, Cracktree200, CFD, AEL stats).
59. https://huggingface.co/api/datasets?search=crack500&limit=10 - HF CRACK500/DeepCrack mirrors.
60. https://zenodo.org/records/20202242 - "Bridge defect dataset" (restricted, May 2026).
61. https://huggingface.co/api/datasets?search=corrosion&limit=20 - HF corrosion datasets (RF100 mirrors, steel-bridge-corrosion-pointer).
62. https://raw.githubusercontent.com/roboflow/roboflow-100-benchmark/main/README.md - RF100 README (224,714 images; API key; per-dataset licenses not stated).
63. https://arxiv.org/abs/2004.01241 - SUIM paper abstract.
64. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11751705/fullTextXML - marine-growth synthetic segmentation paper (no public data).
65. https://github.com/andreluizbvs/InsPLAD/blob/main/LICENSE - InsPLAD LICENSE file (CC BY-NC 3.0).
66. https://ieee-dataport.org/open-access/insulator-data-set-chinese-power-line-insulator-dataset-cplid - CPLID on IEEE DataPort (390.1 MB).
67. https://ieee-dataport.org/competitions/insulator-defect-detection - IDID insulator defect competition dataset (classes, sizes).
68. https://arxiv.org/abs/2010.10032 - TTPLA paper abstract (1,100 images, 8,987 instances).
69. https://huggingface.co/api/datasets/UPNAdroneLab/powerline_towers - HF powerline towers (CC BY-NC-SA 4.0).
70. https://huggingface.co/api/datasets/docmhvr/powerline-components-and-faults - HF powerline components and faults (bbox).
71. https://huggingface.co/api/datasets?search=insulator&limit=20 - HF insulator datasets.
72. https://datasetninja.com/ - Dataset Ninja catalog (Insulator-Defect Detection 2K images; RDD2022 47K; others).
73. https://github.com/stefyste/RIAWELC/releases - RIAWELC releases page (empty).
74. https://huggingface.co/api/datasets?search=weld&limit=30 - HF weld datasets (visual, not X-ray).
75. https://hyper.ai/en/datasets/13272 - xBD listing (22,068 images 1024x1024; via search snippet).
76. https://huggingface.co/api/datasets?search=xbd&limit=20 - HF xBD mirrors and license tags.
77. https://ieee-dataport.org/open-access/detecting-damaged-buildings-post-hurricane-satellite-imagery-based-customized - Cao & Choe Harvey damage dataset (counts, 63 MB).
78. https://arxiv.org/abs/2006.16479 - MSNet / ISBDA paper abstract.
79. https://huggingface.co/api/datasets?search=tower&limit=40 - HF tower datasets (LiDAR corridor set; powerline towers).
