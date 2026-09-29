# Research 03 — Adjacent-segment competitors: underwater/subsea inspection AI, industrial NDT (X-ray/radiography/thermal) AI, and disaster damage assessment

Prepared 2026-09-24 (Thursday) for the Origin Weekend Fall 2026 team (Prompt D). Bracketed numbers like [12] refer to the numbered Sources list at the end; the Key Numbers table repeats the full URL next to each figure. Statements labelled "Inference:" are our reasoning, not sourced facts. Where a figure could not be sourced it is marked "not found". No interviews, testimonials or surveys are quoted anywhere in this document because none were conducted.

Research method: 20 web searches (the session's search budget then ran out) plus ~60 page fetches and text extraction from 6 PDFs (FEMA PDA Guide + pocket guide, two FEMA PDA reports, two arXiv papers, one NDT.net paper). Several vendor pages (Skydio blog, CNBC, MDPI, Verisk Geomni, EEI, Duke Energy) returned 403/404 and are cited only via search summaries where noted.

---

## Summary

- **Underwater inspection is a hardware-led market where AI is a thin bolt-on.** ROV makers (Deep Trekker, Blueye, Subsea Tech, Greensea IQ) sell $8.5k–$300k vehicles [4][7][8]; only Notilo Plus/Delair Marine sells a standalone AI hull-report product, priced "from €1,000/inspection", with published accuracies of 83% (fouling 0–3) and 90% (coating defects) trained on a 25,000-image set [11]. Consolidation is under way: Kraken Robotics agreed to buy Covelya (Sonardyne, EIVA, Voyis, etc.) for $615M on 2026-03-03 [16].
- **Class societies accept ROV/remote in-water surveys but the surveyor stays in the loop.** DNV-OTG-08 allows diver or ROV bottom surveys "supervised by a DNV surveyor" [23]; Bureau Veritas ran a remote in-water survey PoC with Seasam in Jan 2021 [14]; Notilo's platform is "selected by DNV on Veracity" [11]. No class society has published acceptance of AI-only grading (not found).
- **In industrial radiography, codes still require a certified human interpreter.** ISO 9712 Level 2 (or SNT-TC-1A/CP-189/NAS 410) personnel own the disposition; "An AI output does not discharge that responsibility" [37]. There is "a lack of explicit standards governing the qualification of ADR systems" [38]. Commercial ADR (Waygate X|approver, VisiConsult) is sold on-prem to manufacturers, not as SaaS to asset owners [34][38]. Vendor accuracy claims (90–95%, POD 97% for porosity on 5,000+ Aramco radiographs) are unaudited marketing [36].
- **Gecko Robotics is the reference "physical AI" inspection company**: $1.25B valuation, $347M raised, $71M/5-yr US Navy contract, robotics-as-a-service priced "tied to asset coverage rather than hourly rates" [43]. It owns the sensor+robot+software stack; it does not ingest third-party imagery.
- **Disaster damage assessment is standardized on FEMA's four classes (Affected / Minor / Major / Destroyed)** [61][62] and CAL FIRE's DINS percentages (Affected 1–9%, Minor 10–25%, Major 26–50%, Destroyed >50%) [58]. FEMA's July-2025 PDA Guide explicitly says "Advanced analytics could be used to automatically identify and categorize damaged structures from imagery" and asks for 6-inch oblique imagery [62]. That is a government-endorsed opening for AI grading.
- **Insurers already get building-level damage within 24–48 h** from ICEYE (SAR, binary destroyed/undamaged, 24 h, still "beta" for wildfire) [46][47], Nearmap ImpactResponse (24–48 h, "5-tier FEMA classification") [54] and Vexcel Gray Sky (10 cm imagery, first LA-fire captures on day 4–5) [48]. These are portfolio-triage products for P&C carriers; none grades engineered infrastructure (poles, spans, piers, blades).
- **The academic/open ecosystem shows the real accuracy ceiling.** xView2 damage-classification F1 was 0.66 for IBM's entry [69]; Microsoft's HASTE reports 96% recall / 82% precision (Black River, Jamaica) and 86% / 71% (Montego Bay) after Hurricane Melissa, with 65,000 of 110,000 footprints cloud-obscured [68]; drone-vs-satellite labels disagree on 29.02% of 15,814 buildings [67]; the first operational drone-ML deployment (Hurricanes Debby/Helene) saw 82.6% label flips from resolution changes and 39.1% from footprint misalignment [65].
- **Concrete 2025–2026 events**: LA fires (Jan 7–31 2025) damaged/destroyed 18,189+ structures [56]; the DINS Palisades table holds 12,081 records (6,845 destroyed) [58]; Eaton reached "100% of all structures" inspected [57]; insured loss estimates ranged $20B (JPMorgan) to $40B (Swiss Re) [56], Moody's RMS $20–30B [51]. The 2025 Atlantic season had only one US landfall (TS Chantal, ~$500M) but Hurricane Melissa damaged ~150,000 structures in Jamaica (>$12.2B) [70][71]. The 2026 season through 2026-09-25 has 7 tropical storms, 0 hurricanes, >$1.02B damage (TS Arthur, Galveston) [72].
- **Speed benchmarks that matter for a pitch**: FEMA joint PDA for Oklahoma wildfires took place Mar 17–19 2025 for a Mar 14–21 incident but the declaration came May 21 (2 months) [63]; Kentucky's May 16–17 2025 tornado declaration was expedited on May 23 with the PDA waived [64]. Microsoft delivered a Lahaina damage map 4 hours after imagery release (9 am→1 pm) [68]. A Duke Energy drone pilot inspected "about 10 poles in the matter of two minutes" [73].
- **White space (our edge)**: nobody sells a sensor-agnostic, standards-aware grading layer that (i) takes imagery from any drone/ROV/handheld/thermal/radiograph, (ii) triages cheaply first, (iii) grades to the buyer's own code (FEMA class, DINS %, IMO fouling 0–4, NSTM FR, NBIS condition, API/ASME acceptance), (iv) exposes per-item confidence and validation metrics, and (v) outputs a prioritized work queue. Incumbents are either hardware-locked (ROV/robot makers), imagery-locked (aerial/SAR providers), or manufacturing-locked (ADR software).

---

## Detailed findings

### A. Underwater / subsea structure inspection AI

#### A1. Vendor landscape (hardware, software, service)

| Vendor | What they sell | AI content | Public pricing / scale signals | Source |
|---|---|---|---|---|
| **Greensea IQ** (US) | EverClean hull-cleaning/grooming robots as a service; EverClean **Inspection Robot** (standalone, announced 2025-03-31) with HD cameras, ultrasonic thickness sensors, forward-looking sonar; hybrid crawl/swim; "non-magnetic attractor" | Autonomy/navigation software; outputs "coverage maps... fouling ratings, images and high quality video... ultrasonic inspection of hull plate thickness" | Claims "up to 22%" fuel savings; offers "EverClean Subscription vs. Self-Hosted EverClean". No prices published. Targets ship operators, service providers, ports, infrastructure owners | [1][2][3] |
| **Deep Trekker** (Canada) | Mini/inspection ROVs (DTG3 $8,500; PIVOT, REVOLUTION, PHOTON, SPECTRA) | Leads an $8,108,000 "AI ROV Ship Modeling and Detection Project" (Ocean Supercluster contribution $3,405,306; partners Qii.AI, Kongsberg Discovery, ABS Global Canada, DND) to flag "structural defects, corrosion, or biofouling" from sonar+video in real time; announced 2024-09-12, no completion date | Class I/II ROVs "a few thousand dollars to $40,000"; inspection/survey class "$15,000 and $300,000"; sonar add-ons "$6,000 to $300,000+" | [4][5][6] |
| **Blueye Robotics** (Norway) | X1, X3, X3 Ultra ROVs | X3 Ultra carries an Nvidia Jetson Orin NX for "object detection and tracking, collision avoidance" and sonar/camera situational awareness; Blueye Cloud | X3 recommended kit "from $30,788 ex.VAT" (Blueye) / $29,990 (RobotLAB); third-party TCO estimate: maintenance "$2,400–$3,600/year (8–12%)" | [7][8][9][10] |
| **Notilo Plus / Delair Marine** (France) — Seasam HullScan + Notilo/Delair Cloud | Hull-inspection ROV (DVL, "Hull Freeze", up to 2 knots current) + cloud AI hull reports | CNNs on a 25,000-image dataset: fouling 0–3 scale (83% accuracy), coating defect (90%), visibility (90%), niche-area ID (97%); report "in less than 30 minutes" vs "10-hour" manual; newer page claims ">90% accuracy" and "90% replicability" | "Pay-as-you-inspect plans are available from 1000€/inspection"; "selected by DNV on Veracity platform"; named customers: CMA CGM, Maersk, Bureau Veritas, Svitzer, Naval Group, DNV, French Navy, North Marine | [11][12][13] |
| **Voyis** (Canada; now part of Covelya→Kraken) | Underwater laser scanners/stills cameras; VSLAM Powered by EIVA NaviSuite 1.3 (July 2025) | Real-time voxel 3D map (2.5 cm min. resolution), live gap detection so pilots re-fly before surfacing; no defect classification claimed | Covelya (Sonardyne, EIVA, Forcys, Wavefront, Voyis, Chelsea) acquired by **Kraken Robotics** for $615M ($480M cash + $135M shares), announced 2026-03-03; combined 2025 revenue $351–379M, 24% adj. EBITDA, "more than 700 customers"; defense-led | [15][16] |
| **BeeX** (Singapore, NUS spin-off 2018) | Hovering AUVs (A.IKANBILIS, BETTA) rented per project or long-term | Cloud tool "Sambal", 3D point-cloud processing, geo-referenced multi-sensor anomaly reporting | Series A of SGD 10M / US$7.4M launched 2025-09-26; $2M bridge Nov 2023; BETTA "fully booked for deployment through 2025"; sectors: renewables, defense, infrastructure, O&G; test site with SIT (Autonomous Marine Foundry) | [17][18][80] |
| **Hullbot** (Australia) | Autonomous hull-cleaning robots as a service (ferries, small cruise) | Autonomy; inspection is incidental to cleaning | $16M Series A (2025-11-04, Regeneration VC lead); "more than 1,000 paid hull cleans"; fuel savings "10–26%"; 3,600 t CO2 avoided; customer NRMA Marine | [19][79] |
| **Nauticus Robotics** (US, NASDAQ: KITT) | Aquanaut AUV/ROV, ToolKITT autonomy software; ROV services (SeaTrepid) for US East Coast wind and Gulf energy | Autonomy software; no imagery-grading claims found | 2025 revenue $5.3M (vs $1.8M 2024), net loss $40.8M (reported 2026-04-16); Aquanaut operated at 2,300 m | [20][21] |
| **Subsea Tech** (France) | Mini-ROVs (Tortuga 19–38 kg, 300–500 m), micro-ROVs, USVs | None published | Clients listed: Canal de Panamá, EDF, Naval Group, Aramco, Thales, CNRS, IFREMER; no prices | [22] |
| **Ocean Infinity** (UK) | Remote/robotic vessel fleet (Armada), survey and inspection data services | Marketing mentions "software, AI, data, and robotics"; no product-level detail found on homepage | Fleet size, revenue: not found | — |
| **Gecko Robotics** (US) | Wall-crawling TOKA robots (UT, eddy current, cameras, LiDAR) + Cantilever software — also used on ship hulls | See Section B3 | See Section B3 | [43] |

Inference: the only company selling *imagery-in, graded-report-out* AI decoupled from its own robot is Notilo/Delair, and even it bundles its own ROV. Everyone else monetizes hardware or day-rate services.

#### A2. Who buys, and why

- **Ship owners / operators and hull-service providers** — biofouling (fuel/CII), coating condition, class surveys. Notilo names CMA CGM, Maersk, Svitzer, North Marine [12]. Hull cleaning is a "fuel-saving service" market (Hullbot 10–26% fuel; Greensea "up to 22%") [19][3].
- **Class societies (DNV, BV, ABS, LR) and flag states** — accept in-water surveys (UWILD) in lieu of one of two dry-dockings per 5-year cycle [26]; DNV-OTG-08 permits diver or ROV bottom surveys "supervised by a DNV surveyor" and requires flag acceptance and an approved In-Service Inspection Plan [23]; BV demonstrated a remotely supervised in-water survey (Marseille→Paris) on Corsica Linea's MEDITERRANNEE on 2021-01-19 [14]. USCG codifies UWILD in 46 CFR 115.615 / 71.50-5 / 167.15-33 [27]. A trade guide says UWILD can extend dry-dock interval "from 2.5 years to up to 5 years" and lists 2026 costs of "$5,000–$15,000" and 6–12 hours per survey (low-authority blog; treat as indicative) [24].
- **Navies / defense** — Kraken's Covelya deal is defense-led [16]; Deep Trekker's project includes Canada's DND [5]; Notilo lists French Navy and Naval Group [12]; Gecko's largest contract is the US Navy ($71M/5 yr) [43].
- **Offshore wind and O&G operators** — monopiles, scour protection, cable entries; Nauticus supports "the wind industry along the US East Coast" [21]; BeeX sells to renewables/O&G [17]. Day-rates for offshore ROV inspection: not found.
- **Bridge owners (state DOTs)** — 23 CFR 650.311 requires underwater inspection "at regular intervals not to exceed 60 months", 24 months for scour-critical/poor-condition, up to 72 months where satisfactory and FHWA-approved [31]; Level I = 100% visual/tactile, Level II = cleaning ≥10% of members, Level III = NDT [32]. WSDOT and CDOT obtained FHWA approval to use camera ROVs to supplement divers in depths >120 ft (FHWA HIF-18-049; search summary only, PDF too large to fetch) [33].
- **Ports, dams, canals, nuclear** — Subsea Tech client list (Canal de Panamá, EDF) [22]; Greensea targets "port authorities... infrastructure owners" [2].
- **Aquaculture** — Blueye lists aquaculture first among target industries [9]; no AI net-inspection vendor pricing found.

#### A3. Grading standards an AI product must speak

- **IMO 2023 Biofouling Guidelines (MEPC, July 2023)** — fouling rating scale: Level 0 "No fouling", 1 "Microfouling", 2 "Light Macrofouling", 3 "Medium macrofouling", 4 "Heavy macrofouling" [28]. Notilo's 0–3 scale predates this [11]. A search summary attributed to Seacoat states Brazil's NORMAM-401 (in force 2026-06-10) requires fouling rating ≤1 for port entry — verify before quoting [30].
- **US Navy NSTM Chapter 081 Fouling Rating (FR 0–100)**: soft fouling FR 10–30, hard fouling FR 40–90 [29].
- **Class in-water survey scope (UWILD)**: hull plating and weld seams, sea chests/gratings, thrusters/propeller/rudder, cathodic protection and anode depletion, UT thickness where required; deliverable is HD video "organized by hull zone" plus thickness results acceptable to class [25]. Surveyors witness UT gauging at stress zones and CP voltage readings [24].
- **Bridges**: NBIS underwater intervals above [31]; condition ratings follow the NBI/SNBI scale (not fetched — gap).
- **RT/UT acceptance codes** apply to subsea welds too (see B1).

#### A4. Pricing signals (underwater)

- Mini ROV hardware: DTG3 $8,500 [4]; Blueye X3 ~$30k [7][8]; inspection-class ROVs up to $300k; navigation packs $20k–$100k+ [4].
- AI hull report: from €1,000 per inspection (Notilo) [11].
- UWILD survey: $5k–$15k per survey per the 2026 trade blog (unverified) [24].
- Services model: BeeX rents HAUVs per project [17]; Hullbot and Greensea sell cleaning-as-a-service [19][3].
- Diver day-rates and per-bridge dive-inspection costs: **not found**.

#### A5. Gaps in the underwater segment (facts + inference)

- Published AI accuracy is modest and narrow (fouling 83%, coating 90%) and is for hulls only [11]. Pier/pile/monopile corrosion, spalling, scour and marine-growth grading models with published metrics: not found.
- Everything is hardware-coupled; Inference: an owner with a Blueye and a Deep Trekker gets two silos and no shared grading.
- Class societies still require a surveyor to supervise [23]; Inference: AI is positioned as evidence-organizer, not decision-maker — which is exactly the "human-verified" posture regulators accept and a product can be built around.
- Turbid water, no GPS: position-tagging of findings is an unsolved workflow problem that Voyis addresses with SLAM (2.5 cm voxels) [15] but only inside its own stack.

### B. Industrial NDT with X-ray / radiographic / thermal imagery and AI

#### B1. Regulatory/code context the product must respect

- **API in-service inspection intervals** (owner-operators, refineries, terminals) [41]:
  - API 510 pressure vessels: internal/on-stream "lesser of half the remaining life or 10 years"; external "lesser of 5 years or the required internal/on-stream interval".
  - API 570 piping: Class 1 thickness 5 yr / visual 5 yr; Class 2 10 yr / 5 yr; Class 3 10 yr / 10 yr; Class 4 optional; capped at half remaining life.
  - API 653 tanks: routine in-service ≤1 month; external formal ≤5 yr; internal baseline 10 yr, ceiling 20 yr (30 yr with release-prevention barrier).
  - All three allow RBI per API RP 580 as an alternative.
- **Radiographic weld acceptance** is code-specific (ISO 10675-1 levels 1–3; ASME VIII UW-51 / B31.3; API 1104 §9 with density-chart rounded-indication method; AWS D1.1 Tables 6.1/6.2). Cracks, lack of fusion and incomplete penetration are categorically rejectable in every code [40].
- **Who may interpret**: all codes require ISO 9712 Level 2 (or equivalent SNT-TC-1A / CP-189 / NAS 410) certified personnel; the record must carry the interpreter's certificate number and expiry [40]. "An AI output does not discharge that responsibility"; AI's accepted role today is "screening and support tool rather than as the final evaluation"; POD/false-call must be established per MIL-HDBK-1823A on representative parts [37].
- The VisiConsult paper (NDE 4.0 2025) confirms: "there is a lack of explicit standards governing the qualification of ADR systems"; regulators are moving toward "performance benchmarks (probability of detection, false call rate)" and "requiring a human in the loop for certain critical inspections"; bodies named as working on guidance: ASTM, ASME, EASA, ISO [38].
- **IDMS/RBI software** (where results must land): an IDMS structures "master data, CML/TML, thickness readings, visual findings, damage mechanisms, remaining life, recommendations"; example product IntelliSuite by AsInt; article (2026-05-03) mentions no AI [42]. Inference: our output must export into these systems (CSV/GeoPackage/API), not replace them.

#### B2. AI/ADR vendors for radiography and weld inspection

| Vendor / product | Domain | Claims | Pricing | Source |
|---|---|---|---|---|
| **Waygate Technologies (Baker Hughes) X\|approver** | On-prem ADR for X-ray/CT: batteries, castings, electronics, field radiography (wall thickness, aerospace cracks) | "5 to 10 times greater throughput"; "90% + reduction in operator time"; "teachable" models retrained on operator annotations | not published | [34] |
| Waygate blog (Nov 2025) | Strategy | "Rather than replacing inspectors, AI augments their capabilities"; certification-readiness via regulators; barriers: data, regulation, human-machine collaboration; no metrics | — | [35] |
| **VisiConsult** (Germany) | Industrial X-ray systems + deep-learning ADR (e.g., laser welds with GKN Aerospace) | Recommends AI as pre-screen: flag suspicious images for human review so "likely defect-free images don't consume inspector time" — the exact triage pattern we plan | not published | [38] |
| **OnestopNDT ADR** (Zuluf Offshore Water Injection Project, Saudi Aramco) | Weld radiographs (6 defect classes) | "Over 5,000" radiographs; "90–95%" detection; POD porosity 97%, LOF >91%, LOP 90%, slag >90%, IQI/ROI 98%; "under 1 minute per radiograph" vs 5 min manual; YOLOv5/v8; checks against ASME B31.3, API 1104, ASME V, AWS D1.1 — **vendor marketing, no CI or methodology** | not published | [36] |
| Mapvision WSI 2025, IUNA Weld Inspector, Overview.ai OV80i, iFactory AI Vision | Optical/visual weld inspection in manufacturing | Claims "97–99%" accuracy; Overview.ai "94% reduction in downstream weld failures"; example "$180K (2 cells)" with "5.3 months" payback (Sept 2026 blog; unverified) | $180K/2 cells (one example) | [39] |
| Evident (Olympus) WeldSight / OmniScan X3; Zetec | Phased-array UT weld software | Code-compliant scan planning; no AI grading found | not found | (search only) |
| "Xsight" | — | **Not found** as an NDT AI vendor in any search; drop from competitor list unless the team has a specific reference | — | — |

#### B3. Robotic inspection platform — Gecko Robotics (benchmark for "asset health" positioning)

- $125M Series D (2025-06-12, Cox Enterprises lead) at **$1.25B** valuation; total raised $347.43M; founded 2013, Pittsburgh [43][44].
- Model: "vertically integrated robotics-as-a-service" — inspection fees "tied to asset coverage rather than hourly rates", Cantilever software subscriptions, engineering consulting; each robot "can generate hundreds of thousands of dollars in annual revenue" [43]. US Navy 5-year $71M contract; ADNOC partnership [43]. Revenue: not disclosed (Black Scarab, 2026-07-07, warns figures are company-reported) [45].
- Sensors: phased-array UT, eddy current, HD cameras, LiDAR on magnetic crawlers for tanks, boilers, hulls, pipelines [43]. Inference: Gecko wins where wall-thickness data matters; it does not compete on ingesting a customer's own drone/ROV photos.

#### B4. Thermal imagery in industrial NDT

Not researched in depth in this angle (search budget exhausted). Zeitview lists thermal, LiDAR and methane capture and states "Our models scan every frame and flag what's wrong. Certified analysts review each finding before it reaches you" [78] — i.e., human-verified AI is the incumbent pattern in drone inspection too. Substation/transformer thermography AI vendors: not found here (defer to the solar/wind competitor research file).

#### B5. Gaps in industrial NDT AI

- No code accepts AI-only disposition [37][38][40]; every vendor sells "assist". Inference: a product that logs the Level II interpreter's sign-off against the AI suggestion (audit trail + POD tracking over time, as VisiConsult's Fig. 4 suggests [38]) is more sellable than one claiming autonomy.
- ADR is sold to fabricators with fixed geometry and high volume (castings, batteries) [34][38]; field radiography of in-service piping/tank welds under API 570/653 is explicitly called "traditionally lower image throughput" [38] — a thinner, less-served market.
- Film digitization: the paper notes analog film "precluded any meaningful automation" [38]; a large legacy film archive exists (size: not found).
- Pricing is opaque everywhere; only one datapoint ($180K for a two-cell optical system) [39].

### C. Disaster damage assessment

#### C1. How damage is assessed today (government, utilities, insurers)

**FEMA Preliminary Damage Assessment (PDA)** — governs federal declarations [61][62]:
- Four classes for homes. Pocket guide (July 2025): **Affected** = "Some damage to the structure and contents, but still habitable"; **Minor** = "damaged and uninhabitable, but may be made habitable in short period of time"; **Major** = "Substantial failure to structural elements... or damage that will take more than 30 days to repair"; **Destroyed** = "Total loss... not economically feasible to repair, or complete failure to major structural components" [61]. Flood rules key on waterline vs. electrical outlets and essential living space [61].
- Methods allowed: door-to-door, **windshield surveys**, flyovers, **virtual sensing** ("helicopters, fixed-wing aircraft, or drones... High-resolution satellite imagery... LiDAR, SAR, or multispectral"), and geospatial analysis; the Guide states "Advanced analytics could be used to automatically identify and categorize damaged structures from imagery", prefers nadir plus "6-inch oblique imagery", and describes FEMA's Response Geospatial Office "Geospatial Damage Assessment (GDA) tool" [62]. SLTT governments are encouraged to self-report "taking pictures with geotags, using GIS... and using drones" [61].
- Joint PDA may be waived for expedited declarations (44 CFR 206.36(d)) [64].
- Timelines from actual 2025 reports: **Oklahoma wildfires** (FEMA-4866-DR): incident Mar 14–21 2025; joint PDAs Mar 17–19; Governor's request Mar 21; declaration **May 21 2025**; 538 residences (515 destroyed, 9 major, 9 minor, 5 affected); IA estimate $6,799,455 [63]. **Kentucky storms/tornadoes** (FEMA-4875-DR): incident May 16–17 2025; expedited request May 20; declared **May 23**; 470 residences (149 destroyed, 126 major, 70 minor, 125 affected); IA estimate $3,089,359 [64]. Inference: field PDAs can be done in ~3 days for hundreds of homes, but the paperwork-to-declaration path is what stretches to weeks or months.

**CAL FIRE DINS (Damage Inspection)** — wildfire structure-by-structure inspection [58][59]:
- Categories: **No Damage; Affected (1–9%); Minor (10–25%); Major (26–50%); Destroyed (>50%); Inaccessible** [58].
- Palisades 2025 table: 12,081 records — 6,845 destroyed, 72 major, 171 minor, 732 affected, 4,261 no damage; dominant types multi-story SFR 5,383, single-story SFR 3,691, utility structures 1,793 [58]. Eaton: 9,419 destroyed, 1,076 damaged, "100% of all structures within the fire footprint" inspected; contained Jan 31 2025 [57]. Inspectors from LA County Fire and CAL FIRE went "structure to structure", uploading photos and damage % to public maps (LA County, 2025-01-17) [59]. IBHS ran its own field investigation of 252 properties Jan 13–19 2025 and used the 30,000+ DINS records [60].
- Inference: DINS is the best public, photo-backed, per-structure labelled dataset for wildfire grading; its 5-bin percentage scheme is a ready-made target label set for a VLM.

**Utilities (storm/wildfire restoration)**:
- Workflow per Skydio white paper: deploy drones, capture imagery/video, transmit to command center, direct ground crews, prioritize; AEP flew at night after Helene; a Duke pilot "inspected about 10 poles in the matter of two minutes"; US weather-related outages up 60% over the decade [73]. Skydio utilities page: AEP "30 million customer minutes of interruption avoided" over 2.5 years; aerial inspection "3x faster" than bucket trucks; customers include Dominion, NYPA, PG&E, Duke, BHE, BGE, Southern Co, Idaho Power, National Grid, AEP, ComEd [74]. Duke and Southern used drones after Helene/Milton (2024) (search summary; page fetch blocked) [83]. None of these pages describe AI grading of the imagery — analysis is by "experts" in the command center [73].
- Traditional first reconnaissance by contractors "typically waited 3 to 7 days"; the widely repeated "60% reduction in processing time" drone claim has no primary source [76]. EEI storm-process page: fetch failed (404) — gap.

**Insurers (P&C)** — see C2: imagery + AI triage within 24–48 h, then adjuster dispatch. Claims-cycle-time statistics: not found.

**Earthquake (ATC-20 red/yellow/green placards)**: not researched (search budget) — gap.

#### C2. Commercial vendors (post-catastrophe)

| Vendor | Product | Speed / classes | Evidence from 2025 events | Pricing | Source |
|---|---|---|---|---|---|
| **ICEYE** (SAR satellites) | Flood Insights, Wildfire Insights, **Hurricane Solution** (launched 2025-03-31: wind + flood "within 24 hours of a hurricane making landfall", plot-level heatmap, flood depth in inches) | 24 h; wildfire output is **binary "destroyed" or "undamaged"** vector points/footprints; Wildfire Insights described as beta | Page cites a "Retrospective analysis: LA fires 2025" without numbers | not disclosed; 700+ employees | [46][47] |
| **Vexcel** Gray Sky | 10 cm aerial ortho/oblique/multispectral after wildfire/hurricane/tornado; **Elements: Damage Assessment** ML outputs an overall CAT score, "FEMA classification estimate", debris %, roof condition, missing material %, tarp % (GIC members) | LA fires: first captures published Jan 11–12 (day 4–5), more Jan 12–13, Jan 21–22, final Feb 2; ~360 km²; three Palisades flights, two Eaton | Cotality (CoreLogic) embedded Vexcel imagery in Weather Insight on 2025-01-24 for "portfolio... damage assessments and total reconstruction costs" | GIC consortium membership; not disclosed | [48][49][50] |
| **Nearmap ImpactResponse** (Nearmap acquired Betterview) | Post-cat imagery "within 24 hours of capture", outreach "24–48 hours"; Classifications AI = "5-Tier FEMA Classification"; Detections AI = roof damage, tarps, missing shingles, exposed decks | Users shown: Kin, Gulf States, Arch, EMC | — | not disclosed | [54][55] |
| **Moody's / CAPE Analytics** | Acquired 2025-01-13; address-level AI risk insights "back-tested and validated on proprietary insurance claims data"; Moody's RMS event response (LA fires $20–30B) | Portfolio/loss estimation, not per-asset grading | LA one-year review: $25–30B insured, 18,000+ structures, SCE $1B compensation pool (Nov 2025) | not disclosed | [51][52][53] |
| **Cotality (CoreLogic)** | Weather Insight + CoreAI; Vexcel alliance | Portfolio impact | Activated for LA fires Jan 24 2025 | not disclosed | [49] |
| **Verisk (Geomni/geospatial)** | Aerial imagery + Xactimate ecosystem | — | Pages returned 404; **not verified** | — | — |
| **Skydio** | Autonomous drones for utilities/public safety; "Skydio Extend" integrations (AWS, Esri, Fusus) | Capture, not grading | See C1 | not disclosed | [73][74] |
| **Zeitview** | Drone/aircraft inspection for solar, wind, T&D, O&G, commercial roofs; human-verified AI | No dedicated post-storm program found on homepage | — | not disclosed | [78] |
| Censys Technologies, Paladin, Airborne Response, First To Deploy | Drone service crews after Helene/Milton (infrastructure assessment, S&R, debris survey) | Manual review | 2024 | — | [82] |

#### C3. Research / open tools that set the technical bar

- **xView2 / xBD**: 850,736 building polygons, 45,362 km², 19 disasters, classes no-damage/minor/major/destroyed; IBM's entry scored localization F1 0.81, damage-classification F1 **0.66**, combined 0.71; heavy class imbalance toward "no damage" [69].
- **Microsoft AI for Good — HASTE** (open source, MIT; tech report 2026-07-13) [68]:
  - 31 events since early 2023; partners American Red Cross, World Central Kitchen, WFP, UNDP, OCHA; results "within hours to days of imagery becoming available"; 45 public before/after visualizers; layers released on HDX.
  - Lahaina 2023: SkySat imagery at 9 am → assessment by 1 pm; 1,700 damaged (≥1,200 destroyed); ~97% accuracy, 99% recall, 96% precision. Rolling Fork tornado 2023: 0.86 precision / 0.80 recall "in under two hours per scene". Turkey 2023: 3,800 damaged buildings in first three days. Mapped Palisades and Eaton fires Jan 2025 (no metrics given).
  - Hurricane Melissa (landfall 2025-10-28): ~2,300 km² over four AOIs (Vantor satellite + NOAA/NGS aerial); cloud obscured 65,000 of 110,000 footprints in Black River; validation 96% recall / 82% precision (Black River), 86% / 71% (Montego Bay), 76% / 91% (St. Elizabeth); estimated 31,000 damaged buildings in Black River (62%, CI 26k–37k), 18,000 in Montego Bay (49%), 20,000 St. Elizabeth, 21,000 Westmoreland.
  - Cyclone Gezani, Madagascar: Feb 15 2026 pass 23,000 damaged (55%; 97% recall / 79% precision) vs Mar 29 2026 pass 13,000 (43%; 83% / 87%) — shows repair/cleanup drift. June 2026 Venezuela earthquakes: ~72,000 buildings, 3,000 cloud-unknown, 8,400 flagged (12%).
  - Independent validation on Turkey health facilities: specificity 94%, sensitivity 43% (kappa 0.38 after aggregation).
  - Method 2 (foundation-model embeddings + in-browser logistic regression) reaches 0.84 macro ROC-AUC with 1% of labels, 0.92 at 50%; label-efficient vs fine-tuned ResNet-50 (0.77 at 1%).
  - Stated limitations: interior damage under intact roofs uncounted; rubble outside footprint not credited; cloud/misregistration → "unknown".
- **Texas A&M CRASAR sUAS-ML (first operational drone ML deployment, Hurricanes Debby & Helene 2024)** [65][66]:
  - Attention U-Net trained on CRASAR-U-DROIDs; labels per the Joint Damage Scale; 415 buildings assessed in ~18 minutes; dataset 21,716 building labels; field teams produced 47–369 GB/day.
  - Four operational failures: GSD varied 1.65–25.3 cm/px (>10x) causing **82.6% label disagreement** between full-res and transmitted orthomosaics; footprint misalignment caused **39.1%** disagreement; wireless connectivity delayed inference (456 GB PA flood set); GeoJSON/KML "not always sufficient" for emergency managers.
- **Drone vs satellite label agreement** (ACM FAccT'25): 29.02% disagreement across 15,814 buildings (Ian, Michael, Harvey); satellites under-report damage by ≥20.43% [67].
- Aerial thermal + ML for Eaton/Palisades (Remote Sensing 17(24):3962): exists; page blocked (403) — metrics not captured [81].

Inference: (1) overhead imagery caps out around F1 0.66–0.8 for 4-class damage; binary damaged/undamaged is what ships operationally; (2) resolution and geo-alignment, not model architecture, break deployments; (3) confidence intervals and validation reports are becoming the expected deliverable — HASTE "exposes validation metrics... rather than presenting automated damage layers as ground truth" [68].

#### C4. 2025–2026 events — numbers for the pitch

- **January 2025 Southern California fires**: ignitions Jan 7–23, full containment Jan 31; 57,529 acres; 31 deaths (study estimate up to 440 incl. indirect); 18,189+ structures destroyed/damaged (Palisades 7,854; Eaton 10,491 per Wikipedia [56]; CAL FIRE Eaton page: 9,419 destroyed + 1,076 damaged [57]); insured loss estimates: JPMorgan >$20B, Swiss Re $40B [56], Moody's RMS $20–30B [51], Moody's one-year review $25–30B [52]; economic loss JPMorgan $50B, AccuWeather $250–275B [56]. Vexcel imagery days 4–5 [48]; Microsoft mapped both fires [68]; DINS reached 100% for Eaton [57].
- **2025 Atlantic season**: 13 named storms, 5 hurricanes, 4 major; only US landfall TS Chantal (Jul 6, SC, ~$500M, 6 deaths); season ≥$12.7B, Melissa >$12.2B [70]. **Hurricane Melissa**: Cat 5, 185 mph at Jamaica landfall Oct 28 2025; 95 deaths; ~150,000 structures damaged, ~120,000 roofs lost, ~24,000 totaled in Jamaica; ~992,000 houses damaged/destroyed in eastern Cuba; 530,000 without power in Jamaica [71].
- **2026 Atlantic season (through 2026-09-25)**: 7 tropical storms (Arthur–Gonzalo), 0 hurricanes ("first since 1914" by mid-September, El Niño); TS Arthur (Jun 17–18, Galveston) >$1B; Bertha (Jul 22, LA) and Edouard (Sep 1, LA) tens of millions each; season >$1.02B, 4 deaths [72]. Inference: for the demo, wildfire and earthquake are the safer 2026 narratives; hurricane data will come from 2024–2025 archives.
- **Oklahoma Mar 2025 wildfires** and **Kentucky May 2025 tornadoes**: see C1 [63][64].

#### C5. Time-to-assess and cost (what we could find)

- Imagery availability: SAR 24 h [46][47]; aerial 24–48 h to days [54][48]; satellite→map 4 h (Lahaina, Microsoft) [68]; drone-ML 415 buildings/18 min once imagery is on the compute [66].
- Ground truth: DINS structure-by-structure over ~3 weeks for ~30,000 structures (Jan 7–~Jan 31 2025) [57][59][60] — per-structure inspector time: not found.
- Federal: joint PDA field work ~3 days for ~500 homes; declaration 3 days (expedited) to ~2 months [63][64].
- Costs per assessed structure, adjuster backlog days, per-mile utility patrol costs: **not found**.

#### C6. Gaps in disaster assessment

- Products serve **insurers' residential portfolios**; utility/transport infrastructure (poles, conductors, towers, bridge elements, piers) is assessed by drone video and expert eyes, not graded AI [73][74].
- Overhead imagery cannot see interior/under-roof damage or under-deck bridge damage [68]; oblique and ground/ROV imagery is required — FEMA itself asks for 6-inch oblique [62].
- Binary outputs dominate (ICEYE) [47]; 4–5 class grading is offered but with unpublished accuracy (Nearmap, Vexcel) [54][50].
- Field-tested failure modes (resolution drift, misalignment, connectivity, data formats) are documented and unsolved [65].
- No vendor found that unifies **everyday inspection** and **disaster surge** on the same asset registry (FEMA's own guide notes drones/GIS are "if available") [61].

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| Blueye X3 recommended kit price | from $30,788 ex VAT | https://www.blueyerobotics.com/rov/x3 | 2025–26 page |
| Blueye X3 reseller price | $29,990 | https://www.robotlab.com/store/blueye-x3/ | 2025–26 |
| Deep Trekker DTG3 price | $8,500 | https://www.deeptrekker.com/resources/rov-buying-guide | 2025 |
| Inspection-class ROV range | $15,000–$300,000 | https://www.deeptrekker.com/resources/rov-buying-guide | 2025 |
| Deep Trekker AI ROV project value / OSC share | $8,108,000 / $3,405,306 | https://www.deeptrekker.com/news/ai-rov-ship-modeling-detection-project-canada-ocean-supercluster | 2024-09-12 |
| Notilo Cloud fouling / coating / visibility / niche accuracy | 83% / 90% / 90% / 97% | https://www.delairmarine.com/hull-reports-notilo-cloud-platform/ | undated (post-2023) |
| Notilo training set | 25,000 images | https://www.delairmarine.com/hull-reports-notilo-cloud-platform/ | — |
| Notilo report time vs manual | <30 min vs 10 h | https://www.delairmarine.com/hull-reports-notilo-cloud-platform/ | — |
| Notilo price | from €1,000/inspection | https://www.delairmarine.com/hull-reports-notilo-cloud-platform/ | — |
| Notilo newer accuracy claim | >90% biofouling, 90% replicability | https://www.delairmarine.com/ship-hull-reports-for-ship-owners/ | 2025–26 |
| BV remote in-water survey PoC | 2021-01-19, MEDITERRANNEE | https://marine-offshore.bureauveritas.com/newsroom/underwater-success-remote-survey | 2021 |
| Kraken–Covelya deal | $615M ($480M cash + $135M shares); 2025 rev $351–379M; 24% EBITDA; 700+ customers | https://www.krakenrobotics.com/news-releases/kraken-robotics-announces-signing-of-strategic-acquisition-to-expand-global-maritime-capabilities/ | 2026-03-03 |
| Voyis VSLAM 1.3 voxel resolution | 2.5 cm | https://www.marinetechnologynews.com/news/voyis-unveils-updated-visual-651614 | Jul 2025 |
| BeeX Series A | SGD 10M / US$7.4M (launched) | https://www.backscoop.com/newsletter-posts/autonomous-underwater-vehicle-developer-beex-raises-7-4m | 2025-09-26 |
| Hullbot Series A / cleans / fuel saving | $16M / 1,000+ / 10–26% | https://www.smartcompany.com.au/startupsmart/aussie-startup-hullbot-nets-16-million-to-take-its-hull-cleaning-robots-global/ | 2025-11-04 |
| Greensea EverClean fuel-saving claim | up to 22% | https://go.greenseaiq.com/everclean-2026 | 2026 |
| Nauticus 2025 revenue / net loss | $5.3M / $40.8M | https://www.prnewswire.com/news-releases/nauticus-robotics-inc-reports-2025-year-end-results-and-earnings-call-timing-advances-commercialization-of-autonomous-subsea-solutions-302745045.html | 2026-04-16 |
| UWILD survey cost (blog, unverified) | $5,000–$15,000; 6–12 h | https://shipfeeds.portleads.com/maritime-blog/uwild-survey | 2026 |
| Bottom inspections per 5-yr cycle | 2 (UWILD may replace 1) | https://inspectionvendorindex.com/guides/maritime-hull-inspection-ndt | 2025–26 |
| IMO 2023 fouling rating levels | 0–4 | https://safety4sea.com/cm-new-imo-biofouling-guidelines/ | 2023 |
| NSTM fouling rating | FR 0–100 (soft 10–30, hard 40–90) | https://www.researchgate.net/figure/US-Naval-Ships-Technical-Manual-fouling-rating-fr-NSTM-Naval-Sea-Systems-Command-2006_tbl1_341364277 | 2006 manual |
| NBIS underwater inspection interval | ≤60 months (24 / 72 risk-based) | https://www.law.cornell.edu/cfr/text/23/650.311 | current CFR |
| API 570 Class 1 thickness/visual interval | 5 yr / 5 yr | https://reliamag.com/guides/api-510-570-653-inspection-intervals/ | 2025–26 |
| API 653 internal ceiling | 20 yr (30 with RPB) | https://reliamag.com/guides/api-510-570-653-inspection-intervals/ | — |
| Waygate X\|approver throughput / operator time | 5–10x / 90%+ reduction | https://www.bakerhughes.com/waygate-technologies/ndt-software/xapprover-adr-xray-and-ct | 2025–26 |
| Aramco Zuluf ADR (vendor claim) | 5,000+ radiographs; 90–95%; POD porosity 97%; <1 min/image vs 5 min | https://www.onestopndt.com/ndt-articles/ai-powered-automated-defect-recognition-for-weld-radiography | undated |
| AI cannot sign off RT | "An AI output does not discharge that responsibility" | https://www.onestopndt.com/ndt-articles/ai-digital-radiography-interpretation | 2026-09-22 |
| No ADR qualification standard | "lack of explicit standards governing the qualification of ADR systems" | https://www.ndt.net/article/nde40-2025/papers/AB015.pdf | 2025 |
| Optical weld AI system example cost | $180K (2 cells), 5.3-month payback | https://www.engineermd.com/2026/09/ai-for-welding-inspection.html | 2026-09-11 |
| Gecko valuation / total raised / Navy contract | $1.25B / $347.43M / $71M 5-yr | https://sacra.com/c/gecko-robotics/ | 2025 |
| Gecko Series D | $125M | https://www.cnbc.com/2025/06/12/gecko-robotics-raises-125-million-surpassing-billion-dollar-valuation.html | 2025-06-12 |
| ICEYE hurricane data latency | within 24 h of landfall | https://www.iceye.com/newsroom/press-releases/iceye-launches-pioneering-hurricane-solution-to-introduce-multi-peril-assessment-in-the-insurance-sector | 2025-03-31 |
| ICEYE wildfire classes | destroyed / undamaged (binary), 24 h, beta | https://www.iceye.com/solutions/insurance/wildfire-insights | 2025–26 |
| Vexcel LA fire imagery | 10 cm; first publish Jan 11–12; final Feb 2; ~360 km² | https://vexceldata.com/stories/gray-sky-california-wildfires/ | Jan–Feb 2025 |
| Cotality–Vexcel alliance | 2025-01-24 | https://www.cotality.com/press-releases/corelogic-provides-enhanced-visualization-and-portfolio-impacts-on-the-los-angeles-wildfires-through-new-strategic-relationship-with-vexcel-imaging | 2025-01-24 |
| Nearmap ImpactResponse latency / classes | 24–48 h / 5-tier FEMA | https://www.nearmap.com/products/impactresponse | 2025–26 |
| Moody's RMS LA insured loss | $20–30B | https://www.moodys.com/web/en/us/insights/announcements/moodys-rms-event-response-preliminary-estimate-for-us-insure.html | Jan 2025 |
| Moody's one-year LA review | $25–30B insured; 18,000+ structures; SCE $1B pool | https://www.moodys.com/web/en/us/insights/insurance/one-year-after-the-2025-los-angeles-fires.html | Jan 2026 |
| Moody's–CAPE acquisition | announced 2025-01-13 | https://www.moodys.com/web/en/us/insights/announcements/moodys-to-acquire-cape-analytics.html | 2025-01-13 |
| LA fires structures / acres / deaths | 18,189+ / 57,529 / 31 | https://en.wikipedia.org/wiki/January_2025_Southern_California_wildfires | 2025 |
| LA insured loss estimates | JPMorgan >$20B; Swiss Re $40B | https://en.wikipedia.org/wiki/January_2025_Southern_California_wildfires | Jan 2025 |
| Eaton destroyed / damaged / inspected | 9,419 / 1,076 / 100% | https://www.fire.ca.gov/incidents/2025/1/7/eaton-fire | updated 2026-08-06 |
| DINS Palisades records & classes | 12,081; destroyed 6,845; major 72; minor 171; affected 732; no damage 4,261 | https://hub.arcgis.com/api/v3/datasets/c336759e45764c45861a1e62c4c5e2db_0 | created 2025-01-08 |
| DINS class thresholds | Affected 1–9%, Minor 10–25%, Major 26–50%, Destroyed >50% | https://hub.arcgis.com/api/v3/datasets/c336759e45764c45861a1e62c4c5e2db_0 | — |
| IBHS field study | 252 properties, Jan 13–19 2025; 30,000+ DINS records | https://ibhs.org/ibhs-news-releases/ibhs-findings-on-la-countys-palisades-and-eaton-fires/ | 2025-12-10 |
| FEMA PDA classes (definitions) | Affected/Minor/Major/Destroyed | https://www.fema.gov/sites/default/files/documents/fema_rd_pda-pocket-guide_07012025.pdf | 2025-07-01 |
| FEMA endorses analytics on imagery; wants 6-inch oblique | quoted | https://www.fema.gov/sites/default/files/documents/fema_rd_pda-guide_07012025.pdf | 2025-07-01 |
| OK wildfires PDA timeline | incident Mar 14–21; PDA Mar 17–19; declared May 21 2025; 538 homes (515 destroyed) | https://fema.gov/sites/default/files/documents/PDAReport_FEMA4866DR-OK.pdf | 2025 |
| KY tornado expedited timeline | incident May 16–17; declared May 23 2025; 470 homes; PDA waived | https://www.fema.gov/sites/default/files/documents/PDAReport_FEMA4875DRexpedited-KY.pdf | 2025 |
| xBD size / IBM damage F1 | 850,736 buildings; 45,362 km²; F1 0.66 | https://www.ibm.com/think/insights/the-xview2-ai-challenge | 2019–20 |
| HASTE events / partners | 31 events since 2023; Red Cross, WCK, WFP, UNDP, OCHA | https://arxiv.org/abs/2607.11838 | 2026-07-13 |
| HASTE Lahaina | 9 am→1 pm; 1,700 damaged; ~97% acc, 99% recall, 96% precision | https://arxiv.org/abs/2607.11838 | Aug 2023 |
| HASTE Melissa | 2,300 km²; 65k/110k cloud-obscured; 96%/82% and 86%/71% recall/precision | https://arxiv.org/abs/2607.11838 | Oct–Nov 2025 |
| HASTE Madagascar repeat | 23,000 (Feb 15 2026) → 13,000 (Mar 29 2026) damaged | https://arxiv.org/abs/2607.11838 | 2026 |
| HASTE Venezuela quake | ~72,000 buildings; 8,400 flagged (12%) | https://arxiv.org/abs/2607.11838 | Jun 2026 |
| Drone-ML at Debby/Helene | GSD 1.65–25.3 cm/px; 82.6% and 39.1% label disagreement; 456 GB | https://arxiv.org/abs/2506.15890 | 2025-06-18 |
| Drone-ML throughput | 415 buildings in ~18 min; 21,716 labels; 47–369 GB/day | https://arxiv.org/abs/2511.03132 | Nov 2025 |
| Drone vs satellite label disagreement | 29.02%; satellites under-report ≥20.43%; 15,814 buildings | https://arxiv.org/abs/2505.08117 | 2025-05-12 |
| 2025 Atlantic season | 13/5/4; TS Chantal only US landfall (~$500M); ≥$12.7B | https://en.wikipedia.org/wiki/2025_Atlantic_hurricane_season | 2025 |
| Hurricane Melissa damage | 95 deaths; >$12.2B Jamaica; ~150,000 structures damaged; 992,000 houses Cuba | https://en.wikipedia.org/wiki/Hurricane_Melissa | Oct 2025 |
| 2026 Atlantic season to date | 7 TS, 0 hurricanes; >$1.02B; 4 deaths | https://en.wikipedia.org/wiki/2026_Atlantic_hurricane_season | updated 2026-09-25 |
| Duke drone pilot pole rate | ~10 poles in 2 minutes | https://www.skydio.com/resources/whitepapers/drones-for-storm-response-reducing-down-time-increasing-reliability | 2024–25 |
| AEP outage minutes avoided | 30 million over 2.5 years | https://www.skydio.com/solutions/utilities | 2025–26 |
| Contractor first recon lag | 3–7 days | https://overwatchmapping.com/blog/drone-disaster-response-storm-damage/ | 2025 |

---

## Implications for our product / edge (white-space analysis)

1. **Position as the grading and prioritization layer, not another sensor or robot.** Every underwater competitor monetizes hardware or day-rates [4][7][17][19]; every disaster competitor monetizes imagery access [46][48][54]; ADR vendors sell on-prem software to fabricators [34][38]. Nobody sells "bring any image, get a code-referenced grade plus a prioritized queue". Inference: this is the white space; it also avoids competing with Gecko/Kraken capex.

2. **Make the small-VLM triage the cost story, with a human-verified heavy stage.** VisiConsult recommends exactly this: AI "quickly flag the most suspicious ones for human review" so clean images "don't consume inspector time" [38]; Zeitview's positioning is "confirmed, not just detected" [78]; codes require a certified human to sign [37][40]; class societies keep a surveyor supervising [23]. Inference: sell "AI-assisted, human-certified" and log the reviewer's decision against the AI's — that audit trail (POD/false-call tracking over time, as VisiConsult's qualification chart implies [38]) is a compliance feature incumbents lack.

3. **Grade to the buyer's existing schema, per industry, out of the box.** Concrete targets with public definitions: FEMA Affected/Minor/Major/Destroyed [61]; DINS 1–9/10–25/26–50/>50% [58]; IMO fouling 0–4 [28] and NSTM FR 0–100 [29]; NBIS underwater Level I/II/III and 24/60/72-month risk classes [31][32]; API 510/570/653 intervals and RP 580 RBI [41]; RT acceptance per ISO 10675 / ASME / API 1104 / AWS D1.1 [40]. Inference: a schema registry that maps VLM outputs to these labels is a defensible product asset and demoable in 4 days.

4. **Publish per-item confidence, coverage/unknown flags and a validation report** — HASTE's operational lesson is to expose "validation metrics, cloud and unknown flags, and confidence intervals rather than presenting automated damage layers as ground truth" [68]; PDA teams and class surveyors need evidence, not verdicts [62][25].

5. **Own the ground/oblique/underwater viewpoint that overhead imagery cannot see.** Overhead systems miss interior and under-roof damage [68], under-report vs drones by ≥20% [67], and are cloud-limited (65k of 110k footprints in Jamaica) [68]. FEMA asks for 6-inch oblique [62]; bridge substructure and hull surveys are inherently below the waterline [31][25]. Inference: our multi-viewpoint ingestion (drone oblique, handheld, ROV, thermal, radiograph) is complementary to ICEYE/Vexcel/Nearmap, and a partner story rather than a head-on fight.

6. **Design for the documented field failure modes**: resolution normalization (1.65–25.3 cm/px caused 82.6% label flips), footprint/asset misalignment (39.1%), offline/edge inference for weak connectivity, and outputs in the formats responders actually use (not just GeoJSON/KML) [65]. Inference: a small on-device triage model directly answers the connectivity problem.

7. **Same platform for everyday inspection and disaster surge.** Everyday cadence is codified (API 5–10 yr, NBIS 24–72 months, class 5-yr cycles) [41][31][26]; surge events produce 47–369 GB/day of drone imagery [66] and 30,000-structure inspection campaigns [60]. Inference: an asset registry with baseline grades makes post-event change detection possible — the judging brief's "everyday first, disaster as high-value add-on".

8. **First-100-customers hints (facts→inference).** Named buyers of adjacent AI already exist: CMA CGM, Maersk, Svitzer, Bureau Veritas, DNV, French Navy (Notilo) [12]; Dominion, NYPA, PG&E, Duke, Southern Co, National Grid, AEP, ComEd (Skydio) [74]; Kin, Gulf States, Arch, EMC (Nearmap) [54]; Saudi Aramco (ADR pilot) [36]; ADNOC, US Navy (Gecko) [43]. Inference: hull-service providers and drone-service crews (Censys, Airborne Response, Paladin [82]) are the cheapest channel — they already hold imagery and need reports; state DOT underwater-inspection contractors and Level II RT interpreters are the equivalent channels in bridges and NDT.

9. **Do not claim autonomy or accuracy we have not measured.** Public benchmarks: F1 0.66 (xView2 4-class) [69]; 83–90% (Notilo hull) [11]; vendor ADR 90–95% is unaudited [36]. Inference: demo with real images and report our own held-out numbers with the caveats above; that satisfies the hackathon rule against fabricated performance claims.

---

## Open questions / gaps

- Diver day-rates, per-bridge underwater inspection cost, offshore ROV day-rates: **not found**.
- Class-society acceptance of AI-generated gradings (ABS/LR/DNV documents): not found; only "selected by DNV on Veracity" and BV PoC [11][14].
- Ocean Infinity fleet/revenue, Subsea Tech pricing, Greensea pricing: not found.
- Xsight as an NDT AI vendor: not found — confirm the name.
- AI-in-NDT market size: not found (no credible source fetched).
- Pricing of Waygate X|approver, VisiConsult ADR, ICEYE, Nearmap, Vexcel/GIC, Verisk: not disclosed.
- Verisk Geomni current product pages: 404 — verify current name/offer.
- Thermal AI for substations/transformers and pipeline ILI AI (ROSEN/NDT Global): not researched here.
- ATC-20 earthquake placarding and any AI automation: not researched.
- Insurer claims-cycle times after LA fires / Helene: not found.
- Per-structure inspector time for DINS and total DINS completion dates for Palisades: not found (Eaton "100%" [57]).
- MDPI aerial-thermal Eaton/Palisades paper metrics: page blocked [81].
- Whether Nearmap's "5-tier FEMA classification" has published accuracy: not found [54].
- Brazil NORMAM-401 fouling ≤1 requirement (2026-06-10) came from a search summary attributed to Seacoat — verify [30].

---

## Sources

1. https://www.unmannedsystemstechnology.com/2025/04/greensea-iq-to-present-autonomous-everclean-robot-at-ocean-business-2025/ — Greensea IQ EverClean inspection robot at Ocean Business 2025 (Apr 2025).
2. https://greenseaiq.com/news/greensea-iq-to-showcase-everclean-inspection-robot-at-ocean-business-2025/ — Greensea announcement 2025-03-31: sensors, targets, "commercially available".
3. https://go.greenseaiq.com/everclean-2026 — EverClean 2026 landing page: up to 22% fuel savings; subscription vs self-hosted.
4. https://www.deeptrekker.com/resources/rov-buying-guide — Deep Trekker ROV price tiers; DTG3 $8,500; sonar/nav add-on ranges.
5. https://www.deeptrekker.com/news/ai-rov-ship-modeling-detection-project-canada-ocean-supercluster — $8.108M AI ROV hull project with Qii.AI, ABS, DND (2024-09-12).
6. https://www.marinetechnologynews.com/news/trekker-leads-modeling-detection-640350 — same project, trade press.
7. https://www.blueyerobotics.com/rov/x3 — Blueye X3 kit from $30,788 ex VAT; specs.
8. https://www.robotlab.com/store/blueye-x3/ — Blueye X3 reseller price $29,990.
9. https://www.blueyerobotics.com/rov/x3-ultra — X3 Ultra: Jetson Orin NX onboard AI, 4K, 305 m, industries.
10. https://robotomated.com/explore/construction/blueye-x3 — third-party ROI/TCO assumptions for Blueye X3.
11. https://www.delairmarine.com/hull-reports-notilo-cloud-platform/ — Notilo Cloud AI accuracies, 25k images, <30 min reports, €1,000/inspection, DNV Veracity.
12. https://www.delairmarine.com/ship-hull-reports-for-ship-owners/ — Notilo/Delair hull reports: >90% accuracy claim, named customers.
13. https://www.delairmarine.com/seasam-hullscan-best-rov-for-ship-hull-inspection/ — Seasam HullScan ROV features.
14. https://marine-offshore.bureauveritas.com/newsroom/underwater-success-remote-survey — BV remote in-water survey PoC with Seasam (2021-01-19).
15. https://www.marinetechnologynews.com/news/voyis-unveils-updated-visual-651614 — Voyis VSLAM 1.3 (July 2025), 2.5 cm voxels.
16. https://www.krakenrobotics.com/news-releases/kraken-robotics-announces-signing-of-strategic-acquisition-to-expand-global-maritime-capabilities/ — Kraken–Covelya $615M (2026-03-03), revenue, EBITDA, customers.
17. https://www.backscoop.com/newsletter-posts/autonomous-underwater-vehicle-developer-beex-raises-7-4m — BeeX Series A (2025-09-26), BETTA, rental model, Sambal.
18. https://sg.finance.yahoo.com/news/beex-sit-launch-test-ai-003417097.html — BeeX/SIT Autonomous Marine Foundry test site.
19. https://www.smartcompany.com.au/startupsmart/aussie-startup-hullbot-nets-16-million-to-take-its-hull-cleaning-robots-global/ — Hullbot $16M (2025-11-04), 1,000+ cleans, 10–26% fuel.
20. https://www.prnewswire.com/news-releases/nauticus-robotics-inc-reports-2025-year-end-results-and-earnings-call-timing-advances-commercialization-of-autonomous-subsea-solutions-302745045.html — Nauticus FY2025 results (2026-04-16).
21. https://oceannews.com/news/milestones/nauticus-robotics-completes-first-quarter-of-the-2025-offshore-season/ — Nauticus ROVs supporting US East Coast wind, Gulf energy.
22. https://www.subsea-tech.com/ — Subsea Tech ROV/USV products and clients.
23. https://www.dnv.com/services/bottom-survey-in-water/ — DNV in-water bottom survey, DNV-OTG-08, diver/ROV under DNV surveyor supervision.
24. https://shipfeeds.portleads.com/maritime-blog/uwild-survey — UWILD 2026 guide (blog): $5k–15k, 6–12 h, class requirements (low authority).
25. https://www.hpsoffshore.com/en/insights/what-is-a-uwild-inspection/ — UWILD scope and deliverables.
26. https://inspectionvendorindex.com/guides/maritime-hull-inspection-ndt — two bottom inspections per 5-yr cycle; UWILD in lieu of one; provider list.
27. https://www.ecfr.gov/current/title-46/chapter-I/subchapter-K/part-115/subpart-F/section-115.615 — 46 CFR 115.615 UWILD (USCG).
28. https://safety4sea.com/cm-new-imo-biofouling-guidelines/ — IMO 2023 biofouling guidelines; fouling levels 0–4.
29. https://www.researchgate.net/figure/US-Naval-Ships-Technical-Manual-fouling-rating-fr-NSTM-Naval-Sea-Systems-Command-2006_tbl1_341364277 — NSTM fouling rating FR 0–100 table.
30. https://seacoat.com/biofouling-management-plan-for-ships-imo-2023-compliance-performance-guide/ — Biofouling management plan guide (Brazil NORMAM-401 claim via search summary; verify).
31. https://www.law.cornell.edu/cfr/text/23/650.311 — 23 CFR 650.311 underwater inspection intervals (60/24/72 months).
32. https://uvision.dk/articles/underwater-inspection/guide-to-bridge-inspection/ — Underwater bridge inspection Levels I–III, intervals, ROV use.
33. https://www.fhwa.dot.gov/bridge/nbis/hif18049.pdf — FHWA HIF-18-049 underwater imaging technologies (WSDOT/CDOT ROV approval; via search summary).
34. https://www.bakerhughes.com/waygate-technologies/ndt-software/xapprover-adr-xray-and-ct — Waygate X|approver ADR claims.
35. https://www.bakerhughes.com/waygate-technologies/blog/future-autonomous-ndt-aipowered-inspection-systems — Waygate blog Nov 2025 on AI augmentation and barriers.
36. https://www.onestopndt.com/ndt-articles/ai-powered-automated-defect-recognition-for-weld-radiography — Aramco Zuluf ADR vendor case (unaudited metrics).
37. https://www.onestopndt.com/ndt-articles/ai-digital-radiography-interpretation — AI in DR interpretation; certified-interpreter responsibility; MIL-HDBK-1823A (2026-09-22).
38. https://www.ndt.net/article/nde40-2025/papers/AB015.pdf — Schulenburg (VisiConsult), "Artificial Intelligence in Digital Radiography", NDE 4.0 2025.
39. https://www.engineermd.com/2026/09/ai-for-welding-inspection.html — AI weld inspection vendor roundup with accuracy claims and one cost example (2026-09-11).
40. https://www.therness.com/blog/radiographic-testing-weld-acceptance-criteria-iso-asme-api/ — RT acceptance criteria ISO/ASME/API/AWS; ISO 9712 Level 2.
41. https://reliamag.com/guides/api-510-570-653-inspection-intervals/ — API 510/570/653 maximum intervals; RBI.
42. https://inspenet.com/en/articles/digital-rbi-integrate-api-510-570-and-653/ — IDMS/digital RBI (2026-05-03); IntelliSuite by AsInt.
43. https://sacra.com/c/gecko-robotics/ — Gecko Robotics valuation, funding, business model, Navy contract.
44. https://www.cnbc.com/2025/06/12/gecko-robotics-raises-125-million-surpassing-billion-dollar-valuation.html — Gecko $125M Series D (2025-06-12) (via search summary; page blocked).
45. https://www.blackscarab.ai/insights/gecko-robotics-asset-health-physical-ai-guide — Gecko deep dive (2026-07-07); caveat on company-reported data.
46. https://www.iceye.com/newsroom/press-releases/iceye-launches-pioneering-hurricane-solution-to-introduce-multi-peril-assessment-in-the-insurance-sector — ICEYE Hurricane Solution (2025-03-31), 24 h.
47. https://www.iceye.com/solutions/insurance/wildfire-insights — ICEYE Wildfire Insights: binary classes, 24 h, beta.
48. https://vexceldata.com/stories/gray-sky-california-wildfires/ — Vexcel Gray Sky LA fires capture timeline, 10 cm, ~360 km².
49. https://www.cotality.com/press-releases/corelogic-provides-enhanced-visualization-and-portfolio-impacts-on-the-los-angeles-wildfires-through-new-strategic-relationship-with-vexcel-imaging — Cotality–Vexcel alliance (2025-01-24).
50. https://vexceldata.com/stories/announcing-catastrophe-analytics-on-gray-sky-imagery-elements-damage-assessment/ — Vexcel Elements: Damage Assessment outputs (GIC).
51. https://www.moodys.com/web/en/us/insights/announcements/moodys-rms-event-response-preliminary-estimate-for-us-insure.html — Moody's RMS LA fires $20–30B.
52. https://www.moodys.com/web/en/us/insights/insurance/one-year-after-the-2025-los-angeles-fires.html — Moody's one-year LA review.
53. https://www.moodys.com/web/en/us/insights/announcements/moodys-to-acquire-cape-analytics.html — Moody's to acquire CAPE Analytics (2025-01-13).
54. https://www.nearmap.com/products/impactresponse — Nearmap ImpactResponse: 24–48 h, 5-tier FEMA classes, named insurers.
55. https://insurancenewsnet.com/oarticle/betterview-and-nearmap-join-forces-to-enhance-catastrophe-response-time-for-insurers — Betterview CAT-RS + Nearmap.
56. https://en.wikipedia.org/wiki/January_2025_Southern_California_wildfires — LA fires totals, loss estimates, timeline.
57. https://www.fire.ca.gov/incidents/2025/1/7/eaton-fire — CAL FIRE Eaton Fire: 9,419 destroyed, 1,076 damaged, 100% inspected.
58. https://hub.arcgis.com/api/v3/datasets/c336759e45764c45861a1e62c4c5e2db_0 — DINS 2025 Palisades dataset metadata: classes with % thresholds, counts.
59. https://recovery.lacounty.gov/2025/01/17/damage-inspectors-bring-urgently-needed-info-to-public/ — LA County on structure-to-structure DINS inspections (2025-01-17).
60. https://ibhs.org/ibhs-news-releases/ibhs-findings-on-la-countys-palisades-and-eaton-fires/ — IBHS field study (252 properties; 30,000+ DINS) (2025-12-10).
61. https://www.fema.gov/sites/default/files/documents/fema_rd_pda-pocket-guide_07012025.pdf — FEMA PDA Pocket Guide (July 2025): damage-class definitions, self-reporting with drones/GIS.
62. https://www.fema.gov/sites/default/files/documents/fema_rd_pda-guide_07012025.pdf — FEMA PDA Guide (July 2025): virtual sensing, analytics on imagery, 6-inch oblique, GDA tool.
63. https://fema.gov/sites/default/files/documents/PDAReport_FEMA4866DR-OK.pdf — FEMA-4866-DR Oklahoma PDA report (timeline, 538 homes).
64. https://www.fema.gov/sites/default/files/documents/PDAReport_FEMA4875DRexpedited-KY.pdf — FEMA-4875-DR Kentucky expedited PDA report (470 homes; PDA waived).
65. https://arxiv.org/abs/2506.15890 — Manzini et al., operational sUAS-ML damage assessment at Debby/Helene: resolution, misalignment, connectivity, formats (2025-06-18).
66. https://arxiv.org/abs/2511.03132 — Deploying rapid sUAS damage assessments: 415 buildings/18 min; 21,716 labels; 47–369 GB/day.
67. https://arxiv.org/abs/2505.08117 — Drone vs satellite damage-label disagreement 29.02% (FAccT'25).
68. https://arxiv.org/abs/2607.11838 — HASTE technical report (Microsoft AI for Good, 2026-07-13): deployments, metrics, limitations.
69. https://www.ibm.com/think/insights/the-xview2-ai-challenge — xBD dataset size and IBM xView2 F1 scores.
70. https://en.wikipedia.org/wiki/2025_Atlantic_hurricane_season — 2025 season totals, TS Chantal, Melissa share.
71. https://en.wikipedia.org/wiki/Hurricane_Melissa — Melissa landfall, deaths, structures damaged, outages.
72. https://en.wikipedia.org/wiki/2026_Atlantic_hurricane_season — 2026 season to 2026-09-25: 7 TS, 0 hurricanes, >$1.02B.
73. https://www.skydio.com/resources/whitepapers/drones-for-storm-response-reducing-down-time-increasing-reliability — Skydio storm-response white paper: Duke 10 poles/2 min, AEP night ops, workflow.
74. https://www.skydio.com/solutions/utilities — Skydio utilities: 3x faster, AEP 30M customer-minutes, customer logos.
75. https://www.skydio.com/blog/first-responders-drones-hurricane-helene-milton — Skydio Helene/Milton blog (404 at fetch time; listed for completeness).
76. https://overwatchmapping.com/blog/drone-disaster-response-storm-damage/ — 3–7 day contractor recon lag; unsourced 60% claim; CRASAR Harvey 119 flights.
77. https://dronelife.com/2025/12/22/from-reactive-response-to-predictive-defense-how-utilities-are-using-drones-to-reduce-wildfire-risk/ — Utilities using drones for wildfire risk (2025-12-22).
78. https://www.zeitview.com/ — Zeitview homepage: analyst-verified AI, sectors, sensors.
79. https://www.hullbot.com/ — Hullbot homepage.
80. https://www.beex.sg/ — BeeX homepage.
81. https://www.mdpi.com/2072-4292/17/24/3962 — Aerial thermal + AI wildfire damage assessment for 2025 Eaton/Palisades (page blocked; abstract via search).
82. https://www.commercialuavnews.com/rescue-research-and-recovery-drones-play-essential-roles-following-hurricane-helene-and-hurricane-milton — Drone service deployments after Helene/Milton (Censys, Paladin, NOAA).
83. https://www.duke-energy.com/resource-hub/residential/for-your-information/illumination/duke-energy-storm-response-takes-flight — Duke Energy drones after Helene/Milton (via search summary; fetch blocked).
