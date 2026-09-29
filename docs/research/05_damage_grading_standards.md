# 05 — Industry Damage Taxonomies & Severity Grading Standards (per asset class) + Unified S0–S4 Schema

Research angle: `damage_grading_standards` · Written 2026-09-24 (Los Angeles) · For: Origin Weekend Fall 2026, Prompt D (infrastructure damage detection & recovery prioritization)

Method: 20 web searches + ~45 page/PDF fetches. Where a fetch returned a binary PDF, the PDF was converted locally with `pdftotext` and quoted from the extracted text. Every number carries a URL. Items I could not verify are marked **not found** or **Inference:**. Nothing here is a fabricated performance claim or survey result.

---

## Summary (what matters for the product)

1. **There is no cross-industry damage scale.** Each asset class has its own taxonomy and its own severity ladder, and the *action semantics* differ (blade: repair-window/derate; PV: fire-safety class; bridge: load posting/closure; weld: binary accept/reject; disaster: occupancy/aid eligibility). A credible AI inspector must output the **native** scale first; a unified scale is only a triage overlay. ([EPRI 2020](https://restservice.epri.com/publicdownload/000000003002019669/0/Product), [IEC TS 62446-3](https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf), [FHWA SNBI 2022](https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf))
2. **Wind blades: the de-facto industry scale is 5 categories (1 cosmetic → 5 imminent failure), but it is not a standard.** EPRI's 2020 white paper (prepared by DNV GL) says "There is no standard wind turbine blade damage or defect categorization system" and recommends treating any categorization as having "an uncertainty of one category." Only 112 of ~350 surveyed practitioners responded; agreement on any one category "was rare." ([EPRI 3002019669, Oct 2020](https://restservice.epri.com/publicdownload/000000003002019669/0/Product))
3. **Leading-edge erosion has the most quantitative public scheme:** IEA Wind Task 46 (Dec 2022) Levels 0–5 with area thresholds (1 cm², 10 cm², 1 m²) and a layer-based "blade integrity" ladder (topcoat → filler → immediate laminate → structural UD laminate). This is directly promptable for a VLM. ([IEA Wind Task 46, SAND2023-11986R](https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf))
4. **Solar PV: IEC TS 62446-3:2017 defines exactly three Classes of Abnormality (CoA 1 = OK, CoA 2 = thermal abnormality, CoA 3 = safety-relevant)** with a normative Annex C matrix of thermal patterns and ΔT bands (e.g., single hot cell 10–40 K → CoA 2; >40 K → CoA 3; broken front glass → CoA 3). Raptor Maps' commercial taxonomy uses ~30 anomaly types with Low/Medium/High priority and ΔT bands <10 / 10–20 / >20 °C. ([IEC TS 62446-3 preview](https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf), [Raptor Maps glossary](https://pages.raptormaps.com/raptor-maps-knowledge-hub/reviewing-solar-energy-anomalies))
5. **Bridges are the most codified:** FHWA SNBI (March 2022, FHWA-HIF-22-017) Table 20 gives the 0–9 component scale; AASHTO MBEI gives element condition states CS1–CS4 with numeric defect thresholds (RC crack <0.012 in / 0.012–0.05 in / >0.05 in; PSC 0.004 / 0.009 in; spall ≤1 in deep or ≤6 in dia vs. larger; steel "freckled rust" vs. "section loss"). ([SNBI 2022](https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf), [HDOT MBEI quick-ref](https://hidot.hawaii.gov/highways/files/2014/08/HDOT-BrM-Br-Insp-Quick-Reference-Manual.pdf), [IDOT MBEI 2019 handout](https://idot.illinois.gov/content/dam/soi/en/web/idot/documents/doing-business/industry-marketplace/bridges-and-structures-services/ielbi-elem-cs-handout-final-20200212-print.pdf))
6. **Corrosion/coatings have percent-area scales a vision model can literally compute:** ISO 4628-3 Ri0–Ri5 (0 %, 0.05 %, 0.5 %, 1 %, 8 %, 40–50 % rusted area) ↔ ASTM D610 grades 10–0; IMO/IACS hull coating GOOD/FAIR/POOR uses 20 % breakdown / 10 % hard-scale thresholds. ([ISO 4628-3 summary](https://www.scribd.com/document/858422778/Iso-4628-3-Assessment-of-Degree-of-Rusting), [ASTM D610 guide](https://qcsqci.com/astm-d610-explained-rust-grade-scale-for-coating-inspection/), [IMO Res. A.1049(27) 2011 ESP Code](https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/AssemblyDocuments/A.1049(27).pdf))
7. **Waterfront/underwater:** the six-term overall rating (Good / Satisfactory / Fair / Poor / Serious / Critical) plus element damage grades (Minor / Moderate / Advanced / Severe) with numeric section-loss and crack-width thresholds are published in NYC EDC's WFMMS manual (aligned with ASCE MOP 130 practice). ASCE MOP 130 2nd ed. (2025) itself is paywalled. ([NYCEDC WFMMS manual](https://edc.nyc/sites/default/files/2019-10/NYCEDC-WFMMS-Inspection-Guidelines-Manual.pdf), [ASCE 2025 article](https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/07/25/new-mop-brings-waterfront-facilities-inspection-and-assessment-practices-into-the-modern-era))
8. **Weld radiography is binary (accept/reject), with zero tolerance for cracks, incomplete fusion and incomplete penetration** under ASME VIII UW-51 and API 1104; only rounded/elongated indications have size limits (e.g., UW-51 elongated ≤6 mm for t<19 mm; API 1104 pore ≤3.2 mm and ≤¼ wall). A "severity" overlay for welds is therefore a triage aid, not a code output. ([Therness RT criteria](https://www.therness.com/blog/radiographic-testing-weld-acceptance-criteria-iso-asme-api/), [NDT Quality Hub UW-51/52](https://ndtqualityhub.blogspot.com/2026/04/asme-section-viii-rt-acceptance-criteria-uw51-uw52.html))
9. **Disaster scales are 4-level and mutually alignable:** FEMA PDA (Affected / Minor / Major / Destroyed + Inaccessible), xBD Joint Damage Scale (0 No damage / 1 Minor / 2 Major / 3 Destroyed), ATC-20 (Inspected-green / Restricted Use-yellow / Unsafe-red). xBD baseline F1 for "Major damage" was 0.0094 — this class is genuinely hard. ([FEMA IA Damage Matrix](https://www.fema.gov/sites/default/files/documents/fema_pda_individual-assistance-damage-matrix.pdf), [xBD paper](https://arxiv.org/pdf/1911.09296), [ATC-20 form](https://www.atcouncil.org/pdfs/rapid.pdf))
10. **Poles/lines: no public national severity ladder.** OSHA 1910.269 App. D gives inspect items and unsafe criteria; Reclamation FIST 4-6 uses circumference safety-factor tables ("replaced or stubbed immediately" below table). Vendor terms "reject / priority reject" exist but the RUS bulletin defining them was inaccessible (403). CV literature uses 3 insulator defect classes (self-explosion, flashover, broken). ([OSHA App D](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.269AppD), [FIST 4-6](https://www.usbr.gov/power//data/fist/fist_vol_4/vol4-6.pdf), [WDTA-YOLO](https://pmc.ncbi.nlm.nih.gov/articles/PMC10887842/))

---

## Detailed findings

### 1. Wind turbine blades

**1.1 Defect taxonomy (what to name).** Sources agree on the vocabulary; nomenclature below merges EPRI Table 3-3 examples and vendor pages.

| Defect family | Typical sub-types (as named in sources) | Source |
|---|---|---|
| Leading edge erosion (LEE) | pinholes, pits, gouges, delamination of LEP (leading edge protection), exposed laminate | [IEA Task 46](https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf) |
| Cracks | spanwise, chordwise, "small cracks in shells or along leading or trailing edge bonds", "long leading edge chordwise crack with spanwise cracking" | [EPRI 2020 Tables 3-3/3-4](https://restservice.epri.com/publicdownload/000000003002019669/0/Product) |
| Trailing-edge / bond-line | "Trailing edge open over a small length" (Cat 4) → "over a significant length" (Cat 5); "Large gaps or underbite/overbite at shell bonded joints" | EPRI 2020 |
| Delamination / structural | "Significant cracks, delamination, buckling of shells", "Buckled shear webs", "Separation of shear webs from spar caps", "Broken blade bolt" | EPRI 2020 |
| Lightning | "Pin holes or very small marks ... where lightning was intercepted (not at the lightning receptor)" (Cat 2–3); "Lightning penetrated the shell" (Cat 4); "Damaged LPS components (receptors, downconductor cables)" (Cat 5) | EPRI 2020 |
| Coating / gelcoat / cosmetic | discoloration, scratches, thin/flaking coating, grease, dirt, missing labels; missing vortex generators / TE devices ("aerodynamic") | EPRI 2020 |
| Manufacturing defects | wrinkles (spanwise/chordwise), under-infused laminate, voids in adhesive, foreign objects in laminate, core gaps | EPRI 2020 |
| Vendor lists | SkySpecs (tower/nacelle add-ons): "corrosion, coating damage, weld cracks, and loose components"; Zeitview external: "leading-edge erosion, cracking, impact damage, lightning strike points, and surface fatigue"; internal: "delamination, adhesive failure" | [SkySpecs](https://skyspecs.com/product/inspections/), [Zeitview](https://www.zeitview.com/wind) |

**1.2 The 5-category severity system (EPRI 3002019669, Oct 2020, prepared by DNV GL Energy USA).** Not a standard, but the closest thing to an industry consensus. Survey: ~350 invited, 112 responses, 73 % directly involved in categorization. "Most respondents considered categories 1 and 2 to apply to minor damage or defects, categories 3 and 4 for moderate damage or defects, and category 5 for major damage or defects." ([EPRI](https://restservice.epri.com/publicdownload/000000003002019669/0/Product))

| Cat | Description (EPRI Table 3-1, condensed quotes) | Growth / life | Action (EPRI Table 3-2) | Current-practice timing (EPRI Table 2-1) |
|---|---|---|---|---|
| 1 | "Minor variances from supply specifications but within acceptable ... tolerances; may affect the appearance" | Growth: "None expected"; life: "None expected" | "None needed, though some can be remedied with minimal effort in conjunction with other blade maintenance" | Cat 1–3 "can often be operated with inspections every 6 to 12 months" |
| 2 | "Minor damage or defects that exceed supply specification acceptance criteria. Multiple cosmetic findings and/or a single major cosmetic finding" | "Generally 100% growth in size or severity pushes finding into next category"; may "accelerate leading edge erosion" | Repair: "Evaluate cost/benefit"; continue operation; "Monitor during routinely scheduled maintenance" | as above |
| 3 | "Moderate to minor structural damage or minor manufacturing defects in non-critical areas ... May present as surface indications when in fact there is damage to the underlying structural laminate" | "Growth ... by 50% or more is likely to push finding into next category"; "Life is expected to be reduced without ... monitoring or repair" | "Determine depending on circumstances ... Leading edge erosion or small external cracks should be repaired to prevent damage progression"; "Inspection frequency driven by assessment of risk" | Cat 3–4 "should be repaired or shut down within 6 to 12 months with at least an inspection every 6 months" |
| 4 | "Significant damage or defects that have notable impact to structural capability and/or aerodynamic performance" | "Growth ... of 10-50% is likely to push finding into next category"; "High confidence the blade will not achieve intended life" | "Repair within a limited number of months of initial observation"; "Engineering evaluation required to deem blade can operate until repair is scheduled. Operation shall stop if repair cannot be implemented within the allowable time period" | Cat 4–5 "should be repaired or shut down within 1 to 12 months, with monthly monitoring" |
| 5 | "Severe degree of damage or defect such that there is a high risk of imminent failure" | "Likely to rapidly increase"; "expected to fail within a short period of time if operated" | "The blade is not safe to operate until the damage or defect is repaired or the blade is replaced"; repair "should be deemed a Category 3 defect until sufficient operating experience"; "formal root cause analysis" | as above |

Key caveats from EPRI: "agreement on any one damage category was rare. Most often the votes were split between two damage categories, and sometimes three"; "Lightning damage also showed particularly poor agreement." EPRI's stated goal is a DNV Recommended Practice whose content "may be included as informative guidance in a future update to standards such as DNVGL-ST-0376 or IEC 61400-5." ([EPRI](https://restservice.epri.com/publicdownload/000000003002019669/0/Product))

**1.3 Bladena / KIRT x THOMSEN (2021) layer-based categories** (as summarized by IEA Task 46): "damaged leading edge protection and leading edge erosion down to the laminate are defined as Category 3; Category 4 pertains to erosion penetrating the first layer of laminate; and Category 5 erosion through the laminate or an open leading edge." Many approaches align "the higher categories with penetration through the layers of a blade cross-section." ([IEA Task 46 p.16](https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf))

**1.4 IEA Wind Task 46 Leading Edge Erosion Classification System (Dec 2022; Sandia + ORE Catapult).** Multi-criteria: visual condition, mass loss, aerodynamic performance, blade integrity. Promptable thresholds:

| Level | Visual condition (LEP present / no LEP) | Area threshold | Blade integrity (layer) |
|---|---|---|---|
| 0 | "Initial factory condition"; pinholes "< 1mm" and "not cohesive into areas greater than 1cm2" | — | "If an LEP is present, initial erosion/degradation of this is still considered to be Level 0" |
| 1 | LEP: "Lightly worn external coating/LEP" — "instances ... greater than 1cm2 but less than 10cm2"; No-LEP: "Erosion barely visible or pinholes" | individual instances ≥1 cm² | "Initial Erosion of Topcoat ... Underlying filler is not yet visible" |
| 2 | LEP: "Notable areas of localized damage ... cohesive in areas greater than 10cm2"; No-LEP: "Localized Pitting" | ≥10 cm² (<1 m²) | "Erosion Through Topcoat ... Laminate is not yet visible" |
| 3 | LEP: "LEP is compromised over a large area and no longer providing protection" — "destruction of LEP ≥1m2"; No-LEP: "Widespread or coherent pits, some gouges" | ≥1 m² (LEP) / topcoat erosion ≥10 cm² | "Exposure of Immediate Laminate Layers ... Fiber damage not obvious" |
| 4 | "Erosion of topcoat with immediate layer underneath visible and exposed" | topcoat ≥10 cm²; laminate ≥1 cm² | "Erosion Through Immediate Laminate Layers ... Underlying structural laminate not yet visible" |
| 5 | "Notable damage to substrate" — "Any damage beyond the threshold will still be classed as Level 5" | laminate ≥1 cm² | "Exposure of Structural Laminate Layers ... UD structural layers are exposed or damaged" |

Aerodynamic categories (same report): Cat 1 "Region 2 power loss <1%"; Cat 2 "power loss 1%"; Cat 3 "Noticeable loss to L/D and CLmax (-30% and -5-10%)"; Cat 4 "Significant loss to L/D (> -40%) and CLmax (> -10%)"; "Higher power loss (>4%) can be expected when Category 5 erosion is" present. ([IEA Task 46 pp.36–38](https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf))

**1.5 Vendor practice (not standards).** SkySpecs' 2024 crack study uses risk tiers rather than 1–5: "Medium-risk ... should be repaired in the current season", "High-risk ... as soon as possible", "Very high-risk ... often require turbine shutdown"; dataset "around 65,000 damages ... from over 137,000 inspections"; two-year growth probability "around 10%" for small rotors vs "over 40%" for large rotors ([SkySpecs blog, 2024-01-12](https://skyspecs.com/blog/crack-growth-risk-in-turbine-blades-understanding-the-big-picture/)). ONYX Insight: Cat 1 = "A small (<100mm) spot of grease", Cat 5 = "One meter of the blade tip is missing"; "highest variation on the middle rating of 3"; "A detailed universal standard may be difficult to achieve" ([ONYX](https://onyxinsight.com/resources-support/articles/blade-damage-whos-the-judge/)). Sulzer Schmid lists a Siemens Gamesa collaboration on "Standarization of blade damage categorization data analytics" ([Sulzer Schmid](https://www.sulzerschmid.ch/)). A third-party CMMS vendor page (Oxmaint — marketing, not a standard) publishes a mapped version: Cat 1 "Log & monitor"; Cat 2 "Schedule next campaign" "6–12 months"; Cat 3 "Up-tower repair within 90 days"; Cat 4 "Immediate scheduled repair"; Cat 5 "Stop/derate · Engineering review" ([Oxmaint](https://oxmaint.com/industries/power-plant/wind-turbine-blade-repair-erosion-lightning-programs)). Scale: SkySpecs claims "275,000" inspections, "130" GW, "15 minutes" per turbine ([SkySpecs](https://skyspecs.com/product/inspections/)); Zeitview "60,000 Turbines inspected in 2025" ([Zeitview](https://www.zeitview.com/wind)).

**1.6 Standards landscape.** DNV-RP-0573 (Ed. 2020-12, amended 2021-10) covers LEP erosion/delamination *durability prediction*, explicitly not "prediction of damage progression beyond the incubation period" and not "other failure modes like cracking" ([DNV](https://www.dnv.com/energy/standards-guidelines/dnv-rp-0573-evaluation-of-erosion-and-delamination-for-leading-edge-protection-systems-of-rotor-blades/)). DNVGL-ST-0376 (rotor blades) and IEC 61400-5 (wind turbine blades) are the design/certification standards EPRI names as future homes for categorization guidance; I could not fetch IEC 61400-5 content (webstore 404) — **not verified**. Academic note: a 2025/26 arXiv paper reports RAG-grounded VLM zero-shot blade inspection on only "30 labeled blade images" — the public-data scarcity is real ([arXiv 2510.22868](https://arxiv.org/abs/2510.22868)).

### 2. Solar PV (thermal + visual)

**2.1 IEC TS 62446-3:2017 — the normative reference for aerial IR.** Requires irradiance "Minimum 600 W/m2 in the plane of the PV module" (Table 3). Defines three Classes of Abnormality (Table 4): ([IEC TS 62446-3 preview PDF](https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf))

| CoA | Name | Recommendation for actions (verbatim) |
|---|---|---|
| 1 | "no abnormalities – OK" | "No imminent action" |
| 2 | "thermal abnormality – tA" | "Checking the cause and, if necessary, rectification in a reasonable period." |
| 3 | "safety relevant thermal abnormality – dtA" | "Prompt interruption of operation, checking the cause and rectification in a reasonable period." |

Annex C (normative) matrix, ΔT to normal device at 1000 W/m² — the part a VLM should be prompted with:

| Pattern (Annex C) | CoA | ΔT (verbatim) | Note / recommended check |
|---|---|---|---|
| Module in open circuit | 2 | "2 K to 7 K" ("typically 4 K to 6 K") | "check module, state of operation of inverter, and condition of cabling, connectors, and fuses" |
| Module in short circuit | 2 | "2 K to 7 K" averaged | similar to broken glass / PID / mismatch |
| c-Si module with broken front glass | **3** | "0 K – 7 K" | "Beware of high voltage as isolation resistance is lost" |
| Substring in short circuit | 2 | "2 K to 7 K" | "check module and bypass diodes" |
| 1× or 2× substring open circuit (bypass diode active) | 2–3 | "2 K to 7 K" | "Loss of contact ... might lead to a serial arc ... => CoA: 3" |
| Single cell hot | a) 2 / b) **3** | a) "10 K – 40 K"; b) "> 40 K average value over the cell area" | "mostly caused by broken cells"; "Check that there is no shading or severe soiling" |
| Cells shaded by dirt | 1 (rainy site, few K) / 2 (dry site, ΔT > 40 K) | — | "Cleaning ... highly recommended" |
| Transfer resistance at cell/cross connections | 2–3 | "> 10 K" point abnormality | "review by a PV expert or thermographer level 2" |
| Heated junction box | 2–3 | "3 K higher ... compared to nearby junction box" | increased contact resistance / faulty bypass diodes |

Secondary summary (ThermalVariations) paraphrases CoA 2 as "sustained ΔT of roughly 10 °C or more" and CoA 3 as "ΔT of roughly 40 °C or more, or any finding with a credible fire or shock pathway" — consistent with Annex C's cell rows but not the module rows ([ThermalVariations](https://thermalvariations.com/learn/iec-62446-3-thermal-inspection)). Aerial literature collapses the matrix into 5 pattern types: single (A) / multiple (B) hotspots, hot substring (C), hot module (D), hot string (E) ([ScienceDirect 2023](https://www.sciencedirect.com/science/article/pii/S2451904923007321)).

**2.2 Raptor Maps commercial taxonomy** (largest US aerial-PV analytics vendor). Anomaly glossary with priority: cell-level hot spots split by ΔT — "less than 10°C" = Low, "10-20°C" = Medium, "20°C higher" = High; module-level Cracking, Damaged, Delamination, Module (offline), Missing, Reverse Polarity = High; Diode / Diode Multi ("Activated bypass diode, typically 1/3 of the module") = Medium; String, Combiner, Inverter, Tracker = High; Soiling, Shading, Vegetation, Physical Obstruction, Junction Box = Low ([Raptor Maps glossary](https://pages.raptormaps.com/raptor-maps-knowledge-hub/reviewing-solar-energy-anomalies)). Power-loss model: "Impact = Modules Affected × Peak Power (STC) × Power Factor" with a per-anomaly power factor 0–1 (exact defaults live in admin settings — **not found publicly**) ([Raptor Maps power factors](https://pages.raptormaps.com/raptor-maps-knowledge-hub/calculating-impact-of-anomalies-power-factors)). Their open dataset InfraredSolarModules has 12 classes over 20,000 images at 24×40 px (Cell, Cell-Multi, Cracking, Hot-Spot, Hot-Spot-Multi, Shadowing, Diode, Diode-Multi, Vegetation, Soiling, Offline-Module, No-Anomaly) ([GitHub](https://github.com/RaptorMaps/InfraredSolarModules)). Fleet statistics (pv magazine, 2023-03-07, from Raptor Maps' Global Solar Report): underperformance from anomalies "nearly doubled from 1.61% in 2019 to 3.13% in 2022" on 24.5 GW inspected; string 1.06 %, inverter 0.70 %, combiner 0.67 % of inspected power; "$3,350" per MW per year; cell + diode ≈70 % of module-level defects ([pv magazine USA](https://pv-magazine-usa.com/2023/03/07/raptor-maps-points-to-growing-problem-of-pv-system-underperformance/)).

**2.3 Failure-mode taxonomies (research).** IEA PVPS Task 13 failure list: "delamination, back sheet adhesion loss, junction box failure, frame breakage, EVA discoloration, cell cracks, snail tracks, burn marks, potential induced degradation, disconnected cell and string interconnect ribbons, defective bypass diodes" plus thin-film specifics ([IEA PVPS T13-01:2014](https://iea-pvps.org/wp-content/uploads/2020/01/IEA-PVPS_T13-01_2014_Review_of_Failures_of_Photovoltaic_Modules_Final.pdf); 2025 update with Photovoltaic Failure Fact Sheets: [T13-30:2025](https://www.iea-pvps.org/wp-content/uploads/2025/02/IEA-PVPS-T13-30-2025-EX-SUMM-Degradation-and-Failure.pdf)). NREL/Sandia fault-class taxonomy with severity mapping: **not found** as a single public document in this session (Sandia hosts the PVPS reports).

### 3. Bridges

**3.1 NBI component condition ratings 0–9 (FHWA SNBI, March 2022, FHWA-HIF-22-017, Table 20; applies to Items B.C.01–B.C.07 deck, superstructure, substructure, culvert, etc.). "The entire code description must be satisfied for the code to apply."** ([SNBI 2022 PDF](https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf); cross-checked with [TarmacView](https://www.tarmacview.com/glossary/condition-rating/) and [Geocadra](https://www.geocadra.com/en/standards/fhwa-nbis-snbi))

| Code | Condition | Description (SNBI Table 20) | Federal bucket / trigger |
|---|---|---|---|
| 9 | EXCELLENT | "Isolated inherent defects." | Good (7–9) |
| 8 | VERY GOOD | "Some inherent defects." | Good |
| 7 | GOOD | "Some minor defects." | Good |
| 6 | SATISFACTORY | "Widespread minor or isolated moderate defects." | Fair (5–6) |
| 5 | FAIR | "Some moderate defects; strength and performance of the component are not affected." | Fair |
| 4 | POOR | "Widespread moderate or isolated major defects; strength and/or performance of the component is affected." | Poor (≤4) — any component ≤4 makes the bridge "Poor" |
| 3 | SERIOUS | "Major defects; strength and/or performance ... seriously affected. Condition typically necessitates more frequent monitoring, load restrictions, and/or corrective actions." | Poor |
| 2 | CRITICAL | "Major defects; component is severely compromised. Condition typically necessitates frequent monitoring, significant load restrictions, and/or corrective actions in order to keep the bridge open." | Poor |
| 1 | IMMINENT FAILURE | "Bridge is closed to traffic due to component condition. Repair or rehabilitation may return the bridge to service." | Poor |
| 0 | FAILED | "Bridge is closed due to component condition, and is beyond corrective action. Replacement is required to restore service." | Poor |

Inspection intervals: routine "not exceeding 24 months"; NBIS risk-based Method 1 → "12, 24, or 48 months", Method 2 → "12, 24, 48, or 72 months" ([SNBI B.IE.07 commentary](https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf); [Geocadra](https://www.geocadra.com/en/standards/fhwa-nbis-snbi)). Secondary sources state a Critical Finding is triggered at ratings ≤3 ([Geocadra](https://www.geocadra.com/en/standards/fhwa-nbis-snbi), [TarmacView](https://www.tarmacview.com/glossary/condition-rating/)); **the regulatory definition (23 CFR 650.305) could not be fetched** (Federal Register blocked) — treat as secondary.

**3.2 AASHTO MBEI element condition states CS1–CS4 (element-level, NHS bridges).** Quantities per element are split across four states that sum to the element total. Generic meaning: CS1 Good, CS2 Fair, CS3 Poor, CS4 Severe = "The condition warrants a structural review to determine the effect on strength or serviceability of the element or bridge; OR a structural review has been completed and the defects impact strength or serviceability." Defect-specific thresholds (AASHTO MBEI 2019 as reproduced by Illinois DOT and Hawaii DOT): ([IDOT MBEI 2019 handout](https://idot.illinois.gov/content/dam/soi/en/web/idot/documents/doing-business/industry-marketplace/bridges-and-structures-services/ielbi-elem-cs-handout-final-20200212-print.pdf), [HDOT quick reference](https://hidot.hawaii.gov/highways/files/2014/08/HDOT-BrM-Br-Insp-Quick-Reference-Manual.pdf))

| Defect (MBEI no.) | CS1 Good | CS2 Fair | CS3 Poor | CS4 Severe |
|---|---|---|---|---|
| Delamination / Spall / Patched Area (1080) — concrete | "None." | "Delaminated. Spall 1 in. or less deep or 6 in. or less in diameter. Patched area that is sound." | "Spall greater than 1 in. deep or greater than 6 in. diameter. Patched area that is unsound or showing distress. Does not warrant structural review." | structural-review clause |
| Exposed Rebar (1090) | "None." | "Present without measurable section loss." | "Present with measurable section loss, but does not warrant structural review." | " |
| Efflorescence / Rust Staining (1120) | "None." | "Surface white without build-up or leaching without rust staining." | "Heavy build-up with rust staining." | " |
| Cracking, reinforced concrete (1130) | "Width less than 0.012 in. or spacing greater than 3.0 ft." | "Width 0.012–0.05 in. or spacing of 1.0–3.0 ft." | "Width greater than 0.05 in. or spacing of less than 1 ft." | " |
| Cracking, prestressed concrete (1110) | "Width less than 0.004 in. or spacing greater than 3.0 ft." | "Width 0.004–0.009 in. or spacing 1.0–3.0 ft." | "Width greater than 0.009 in. or spacing of less than 1 ft." | " |
| Abrasion / Wear (1190) | "No abrasion or wearing." | "Abrasion or wearing has exposed coarse aggregate but the aggregate remains secure" | "Coarse aggregate is loose or has popped out" | " |
| Corrosion, steel (1000) | "None." | "Freckled Rust. Corrosion of the steel has initiated." | "Section loss is evident or pack rust is present but does not warrant structural review." | " |
| Cracking, steel (1010) | "None." | "Crack that has self arrested or has been arrested with effective arrest holes, doubling plates, or similar." | "Identified crack exists that is not arrested but does not warrant structural review" | " |
| Connection, steel (1020) | "Connection is in place and functioning as intended." | "Loose fasteners or pack rust without distortion is present but the connection is in place" | "Missing bolts, rivets, broken welds, fasteners or pack rust with distortion but does not warrant structural review" | " |
| Decay / Section Loss, timber (1140) | "None." | "Affects less than 10% of the member section." | "Affects 10% or more of the member but does not warrant structural review." | " |
| Steel Protective Coating — Peeling/Bubbling/Cracking (3420) | "None." | "Finish coats only." | "Finish and primer coats." | "Exposure of bare metal." |
| Steel coating Effectiveness (3440) | "Fully effective." | "Substantially effective." | "Limited effectiveness." | "Failed, no protection of the underlying metal" |

MBEI 2019 footnote (IDOT handout): "Reinforced Concrete: In general, cracks less than 0.012 inches can be considered insignificant, cracks ranging from 0.012 to 0.05 inches can be considered moderate, and cracks greater than 0.05 inches can be considered wide. Prestressed Concrete: ... 0.004 ... 0.009 ... Pattern (Map) Cracking: ... moderate is 1 ft. to 3 ft. spacing and heavy is less than 1 ft. spacing." Also: "The inspector should consider exposure and environment when evaluating crack width." Note for CV: 0.012 in = 0.30 mm; 0.004 in = 0.10 mm — below typical drone ground-sampling distance without close-up imaging (**Inference**).

### 4. Corrosion / steel coatings

**4.1 ISO 4628-3 (2016; EN ISO 4628-3:2024) rust grades and ASTM D610 correlation.** ([ISO 4628-3 summary](https://www.scribd.com/document/858422778/Iso-4628-3-Assessment-of-Degree-of-Rusting), [ISO catalogue](https://www.iso.org/standard/66400.html), [EN ISO 4628-3:2024](https://standards.iteh.ai/catalog/standards/cen/d6ad1765-c591-4894-838f-454bc1312e0b/en-iso-4628-3-2024))

| ISO 4628-3 | Rusted area | ≈ ASTM D610 grade | Typical action (source: coatings-industry summary) |
|---|---|---|---|
| Ri 0 | 0 % | 10 | none |
| Ri 1 | 0.05 % | 9 | "Ri1–Ri3 will require patch repair painting" |
| Ri 2 | 0.5 % | 7 | patch repair |
| Ri 3 | 1 % | 6 | patch repair |
| Ri 4 | 8 % | 4 | "Ri4 and Ri5 indicate ... corrosion protection capacity ... depleted ... requiring full repainting" |
| Ri 5 | 40–50 % | 1–2 | full repaint |

ASTM D610 full ladder (percent of area rusted): 10 "<0.01%", 9 "<0.03%", 8 "<0.1%", 7 "<0.3%", 6 "<1%", 5 "~3%", 4 "~10%", 3 "~16%", 2 "~33%", 1 "~50%", 0 "~100%"; "rust grades below 4 generally indicate serious coating failure." ASTM D610 also codes rust *distribution* (Spot S, General G, Pinpoint P, Hybrid H) — definitions **not extracted** here ([QCS ASTM D610 guide](https://qcsqci.com/astm-d610-explained-rust-grade-scale-for-coating-inspection/)). AMPP/NACE: no separate visual rust-grade ladder was found in this session beyond joint SSPC-VIS 2/ASTM D610 practice — **not verified**.

**4.2 Ship/offshore hull coating & wastage (IMO Res. A.1049(27), 2011 ESP Code, adopted 30 Nov 2011; mirrors IACS UR Z10).** Verbatim §1.2.11: "GOOD condition with only minor spot rusting; FAIR condition with local breakdown of coating at edges of stiffeners and weld connections and/or light rusting over 20% or more of areas under consideration, but less than as defined for POOR condition; and POOR condition with general breakdown of coating over 20% or more of areas or hard scale at 10% or more of areas under consideration." §1.2.9: "Substantial corrosion is an extent of corrosion such that assessment of corrosion pattern indicates wastage in excess of 75% of allowable margins, but within acceptable limits" (CSR ships: measured thickness "between tnet + 0.5 mm and tnet"). §1.2.8: "Suspect areas are locations showing substantial corrosion and/or are considered by the surveyor to be prone to rapid wastage." ([IMO A.1049(27) PDF](https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/AssemblyDocuments/A.1049(27).pdf))

### 5. Underwater / waterfront / marine structures

**5.1 Overall condition assessment rating (six terms).** From NYC EDC's Waterfront Facilities Maintenance Management System Inspection Guidelines Manual §3.3 (large port owner; uses the same six terms and inspection types as ASCE MOP 130 — **Inference** on alignment; ASCE's own text is paywalled): ([NYCEDC WFMMS](https://edc.nyc/sites/default/files/2019-10/NYCEDC-WFMMS-Inspection-Guidelines-Manual.pdf))

| Rating | Definition (verbatim) |
|---|---|
| Good | "No problems or only minor problems noted. Structural elements may show some very minor deterioration, but no overstressing observed." |
| Satisfactory | "Minor to moderate defects and deterioration observed, but no overstressing observed." |
| Fair | "All primary structural elements are sound; but minor to moderate defects and deterioration observed. Localized areas of moderate to advanced deterioration may be present but do not significantly reduce the load bearing capacity" |
| Poor | "Advanced deterioration or overstressing observed on widespread portions of the structure, but does not significantly reduce the load carrying capacity" |
| Serious | "Advanced deterioration, overstressing, or breakage may have significantly affected the load bearing capacity of primary structural elements. Local failures are possible and loading restrictions may be necessary." |
| Critical | "Very advanced deterioration, overstressing, or breakage has resulted in localized failure(s) of primary structural elements. More widespread failures are possible or likely to occur and load restrictions should be implemented as necessary." |

Rating judgement factors: "Scope of damage", "Severity of damage", "Distribution of damage (local vs. general)", "Types of components affected". Action tiers: "Priority level actions should be completed within 1 to 3 years"; "Routine" actions go into scheduled maintenance. ASCE MOP 130 (2015) practice per Heffron (2015 AAPA slides): "Reduction in design capacity of primary members of 20% or more is considered potentially significant"; "Structures that are rated 'Poor' or below are considered to exhibit potentially significant damage" requiring structural evaluation before repair ([Heffron/AAPA 2015](https://www.ports.org/files/SeminarPresentations/2015Seminars/2015FacEngineering/Ron%20Heffron.pdf)). ASCE MOP 130 2nd edition (2025): "The condition rating system has been updated for greater consistency, with improved guidance on translating observed conditions into actionable ratings" and incorporates "drones, imaging, and digital data management" ([ASCE 2025-07-25](https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/07/25/new-mop-brings-waterfront-facilities-inspection-and-assessment-practices-into-the-modern-era)).

**5.2 Element damage grades (NYC EDC Tables 3-3 to 3-6; "Any defect listed below is sufficient to identify relevant damage grade").** ([NYCEDC WFMMS](https://edc.nyc/sites/default/files/2019-10/NYCEDC-WFMMS-Inspection-Guidelines-Manual.pdf))

| Grade | Steel | Reinforced concrete | Prestressed concrete | Timber |
|---|---|---|---|---|
| Minor | "<50 percent of perimeter ... affected by corrosion"; "Loss of thickness up to 15 percent" | mechanical/impact spalls; cracks up to 1/32 in | "impact spalls up to 0.5 in. deep"; "Structural cracks up to 1/32 in." | "Checks, splits and gouges less than 0.5 in. wide" |
| Moderate | ">50 percent of perimeter"; "Loss of thickness 15 to 30 percent" | "Structural cracks up to 1/16 in."; "Corrosion cracks up to 1/4 in."; "rounding of corners up to 1 in. deep" | "Structural cracks 1/32 in. to 1/8 in."; "Any corrosion cracks generated by strands" | "Checks and splits wider than 0.5 in."; "Remaining diameter loss up to 15 percent"; "Cross section area loss up to 25 percent"; marine borer evidence |
| Advanced | "Loss of nominal thickness 30 to 50" %; "Partial loss of flange edges" | "Structural cracks 1/16 in. to 1/4 in. ... partial breakages (structural spalls)"; "Corrosion cracks wider than 1/4 in. and open spalls" | "cracks wider than 1/16 in."; softening up to 1 in. deep | "Remaining diameter loss 15 to 30 percent"; "Cross section area loss 25 to 50 percent" |
| Severe | (not extracted; >50 % loss / buckling implied) | "Structural cracks wider than 1/4 in. or complete breakage"; "over 30 percent of diameter loss for any main reinforcing bar"; "Loss of over 30 percent of cross section" | "Structural cracks wider than 1/8 in. and at least partial breakage"; "Corrosion spalls over any prestressing steel" | "Remaining diameter reduced by more than 30 percent"; "Cross section area loss more than 50 percent"; "Partial or complete breakage" |

Crack-width vocabulary used underwater/topside: "Hairline – Crack width less than 1/32 in. Fine – 1/32 to 1/16 in. Medium – 1/16 to 1/8 in. Wide – greater than 1/8 in." Steel corrosion descriptors: Minor "light surface corrosion with no apparent loss of section"; Moderate "loose and flaking with some pitting ... measurable but not significant loss of section"; Severe "Heavy, stratified corrosion ... Significant loss of section." Note the manual's inspection tables require "marine growth" removal on a sampling basis (e.g., "Every 50 LF" / "Every 100 LF") before rating — an ROV image with growth on it cannot be graded for section loss (**Inference**).

**5.3 Marine growth grading & class-society hull defect ladders.** A public numeric marine-growth thickness grading scheme (soft/hard fouling, mm by depth band): **not found** in this session (DNV-RP-C205 / NORSOK N-003 define design profiles, not inspection grades — not fetched). Class-society (DNV/ABS/LR) underwater-inspection defect grading: vendors say reports include "defect grading" aligned to "DNV-RP-C203, Lloyd's Register Class rules, ABS underwater inspection programmes" but publish no ladder ([NDTScan](https://ndtscan.com/services/underwater-surveying-and-inspection/)). DNV-RP-C210 is about probabilistic fatigue-crack inspection planning, not visual grading ([DNV](https://www.dnv.com/energy/standards-guidelines/dnv-rp-c210-probabilistic-methods-for-planning-of-inspection-for-fatigue-cracks-in-offshore-structures/)).

### 6. Weld radiography (X-ray / digital RT)

Indication taxonomy: cracks, incomplete (lack of) fusion, incomplete penetration, elongated indications (slag), rounded indications (porosity: "any indication with a length equal to or less than three times the width"), undercut, burn-through. Acceptance is code-based and largely binary: ([Therness](https://www.therness.com/blog/radiographic-testing-weld-acceptance-criteria-iso-asme-api/), [NDT Quality Hub](https://ndtqualityhub.blogspot.com/2026/04/asme-section-viii-rt-acceptance-criteria-uw51-uw52.html), [welding&NDT](https://www.weldingandndt.com/acceptance-criteria-for-weld-defects/))

| Code | Cracks / LOF / IP | Elongated (slag) | Rounded (porosity) |
|---|---|---|---|
| ASME BPVC VIII-1 UW-51 (100 % RT) | "Any crack or zone of incomplete fusion" rejectable; IP rejectable where full penetration specified | t < 19 mm: "6 mm (1/4 in.)"; 19–57 mm: "t/3"; > 57 mm: "19 mm (3/4 in.)"; aligned group: sum > "2t in 150 mm" | per Section VIII Mandatory Appendix 4 charts (Section V Art. 2 App. for digital) |
| ASME UW-52 (spot RT) | same zero tolerance | "2/3 t" with floor "1/4 in. (6 mm)" acceptable and cap "3/4 in. (19 mm)" unacceptable | same charts |
| API 1104 §9 (pipelines) | crack / LOF rejectable | individual > "50 mm in 300 mm of weld" rejectable; combined > 50 mm in any 300 mm; any indication > "two-thirds of the weld thickness" | "No individual pore may exceed one-quarter of the nominal wall thickness"; "No individual pore may exceed 3.2 mm in diameter"; density chart |
| ISO 5817 / ISO 10675-1 (B/C/D) | cracks rejectable at all levels | B: "0.5×t (min 1.5 mm, max 6 mm)"; C: "1×t (min 2 mm, max 8 mm)"; D: "2×t (min 3 mm, max 16 mm)" | B: pore ≤ "0.25×t ... max 3 mm", area ≤ 1 %; C: 0.5×t, 2 %; D: 1×t, 4 % |
| AWS D1.1 static (Table 6.1) | rejectable | "> 19 mm for welds > 38 mm thick" | pore ≤ "3 mm or ... one-third of smaller of base/weld thickness"; sum ≤ "10 mm in any 25 mm" |

Therness and the blog are secondary summaries; the primary ASME/API texts are paywalled — use as design guidance, verify before claiming code compliance.

### 7. Disaster / post-event assessment

**7.1 FEMA Preliminary Damage Assessment — degrees of damage (Individual Assistance Damage Matrix; PDA Guide current version 2025, effective 2025-07-01; pocket guide May 2020).** ([FEMA IA Damage Matrix PDF](https://www.fema.gov/sites/default/files/documents/fema_pda_individual-assistance-damage-matrix.pdf), [FEMA PDA Guide page](https://www.fema.gov/disaster/how-declared/preliminary-damage-assessments/guide), [FEMA Pocket Guide](https://www.fema.gov/sites/default/files/2020-07/fema_preliminary-disaster-assessment_pocket-guide.pdf))

| Degree | Conventionally built home — definition & flood waterline | Non-flood examples (verbatim excerpts) |
|---|---|---|
| Affected | "minimal cosmetic damage" — waterline "In Unfinished Basement" / crawlspace | "paint discoloration or loose siding", "Minimal missing shingles or siding" |
| Minor | "damage that does not affect structural integrity" — waterline "Below Electrical Outlets" in an essential living space | "Nonstructural damage to roof components", "Multiple small vertical cracks in the foundation", chimney damage, mechanical components |
| Major | "significant structural damage and requires extensive repairs" — waterline "At or Above Electrical Outlets" (or first floor if basement fully submerged) | "Failure or partial failure to structural elements of the roof ... walls ... foundation, to include crumbling, bulging, collapsing, horizontal cracks, and shifting" |
| Destroyed | "total loss ... repair is not feasible, requires demolition, and/or confirmed to be in imminent danger" — waterline "At or Above Ceiling" | "Only foundation remains", "Complete failure of two or more major structural components", "impending landslide, mudslide, or sinkhole" |
| Inaccessible | "Damage to residence cannot be visually verified" | roads blocked / bridge out |

Pocket-guide one-liners: "Affected ... mostly cosmetic", "Minor: a home with repairable non-structural damage", "Major: a home with structural damage or other significant damage that requires extensive repairs", "Destroyed: the home is a total loss." Manufactured homes use a parallel matrix keyed to the floor system.

**7.2 xBD / xView2 Joint Damage Scale (Gupta et al., 2019).** Ordinal 0–3: "no damage", "minor damage", "major damage", "destroyed"; "refined in collaboration with agencies such as CAL FIRE, the California Air National Guard, and FEMA"; authors say "This scale is not meant as an authoritative damage assessment rating." Dataset: "850,736 building annotations across 45,362 km2", 22,068 images, 19 disasters; class counts 313,033 / 36,860 / 29,904 / 31,560 (+14,011 unclassified). Baseline damage-classification F1 (Table 3): No Damage 0.6631, Minor 0.1435, **Major 0.0094**, Destroyed 0.4657; weighted F1 0.2654 — "Major damage instances were often classified as minor damage." Per-level structural descriptions live in Figure 4 (image) — **text not extracted**. ([xBD arXiv 1911.09296](https://arxiv.org/pdf/1911.09296), [EmergentMind summary](https://www.emergentmind.com/topics/xbd-dataset))

**7.3 ATC-20 rapid evaluation (Applied Technology Council; form © 1995-07).** Observed conditions (checked as Minor/None, Moderate, Severe): "Collapse, partial collapse, or building off foundation"; "Building or story leaning"; "Racking damage to walls, other structural damage"; "Chimney, parapet, or other falling hazard"; "Ground slope movement or cracking"; estimated damage bins 0–1 %, 1–10 %, 10–30 %, 30–60 %, 60–100 %, 100 %. Posting rule: "Severe conditions endangering the overall building are grounds for an Unsafe posting. Localized Severe and overall Moderate conditions may allow a Restricted Use posting." Placards: INSPECTED (Green), RESTRICTED USE (Yellow), UNSAFE (Red). ([ATC-20 Rapid form](https://www.atcouncil.org/pdfs/rapid.pdf), [ATC-20 page](https://www.atcouncil.org/atc-20))

### 8. Power lines / poles / insulators

- **OSHA 29 CFR 1910.269 App. D (wood poles):** inspect "general condition", "Cracks" ("Horizontal cracks perpendicular to the grain ... may weaken the pole"), "Holes" (woodpecker), "Shell rot and decay", "Knots", "Depth of setting", "Soil conditions", "Burn marks". Tests: hammer (~1.4 kg, "Decay pockets will be indicated by a dull sound"), prod ("If substantial decay is present, the pole is unsafe"), rocking ("If the pole cracks during the test, it is unsafe"). ([OSHA](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.269AppD))
- **Reclamation FIST 4-6 Wood Pole Maintenance (Aug 1992):** decay classification "(1) General external decay, (2) External pocket, (3) Hollow heart, or (4) Enclosed pocket"; serviceability via "permissible reduced circumference" safety-factor tables — "If the reduced circumference indicates a pole safety factor less than that specified ... the pole should be replaced or stubbed immediately"; inspection frequency table: initial 15 yr (cedar) / 12 yr (fir/larch), re-inspect sound pole 12/12, minor decay 6/6 years. ([FIST 4-6](https://www.usbr.gov/power//data/fist/fist_vol_4/vol4-6.pdf))
- **Cycles & vendor classes:** California GO 165: patrol 1 yr urban / 2 yr rural; detailed 5 yr; intrusive groundline 10 yr for poles >15 yr ([Detect Inspections](https://detectinspections.com/blog/utility-poles)); "Most U.S. utilities operate pole inspection programs on 8-12 year cycles" ([Katapult](https://www.katapultengineering.com/blog/utility-pole-inspections)); Osmose: "Comprehensive Inspection" finds "98% of rejects", lesser methods leave "10%-30% of rejects unidentified", cycles 2–4 / 4–6 / 8–12 yr by method; remaining strength via "StrengthCalc®" ([Osmose](https://www.osmose.com/wood-pole-inspection)). Formal "reject / priority reject / danger pole" definitions and the NESC remaining-strength threshold (commonly cited as 2/3 of original) are in RUS Bulletin 1730B-121 — **could not be fetched (HTTP 403); not verified**.
- **Insulators / conductors:** CV literature uses three classes — "self-explosion" (shattered/missing shed), "flashover damage", "broken" insulators; MD-Insulator dataset 16,430 images (5,318 defective); best mAP@50 88.3 % multi-domain ([WDTA-YOLO, PMC10887842](https://pmc.ncbi.nlm.nih.gov/articles/PMC10887842/)); CPLID 600 normal + 248 defective images ([PMC11128844](https://pmc.ncbi.nlm.nih.gov/articles/PMC11128844/)). A utility-grade severity ladder for insulators/conductors (EPRI or utility standards) was **not found** publicly in this session.

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| EPRI blade categorization survey | ~350 invited, 112 responses, 73 % decision-involved | https://restservice.epri.com/publicdownload/000000003002019669/0/Product | Oct 2020 |
| Recommended uncertainty of blade category | ±1 category | same | Oct 2020 |
| Cat 1–3 operate with inspections every | 6–12 months | same | Oct 2020 |
| Cat 3–4 repair/shutdown within | 6–12 months, inspect every 6 months | same | Oct 2020 |
| Cat 4–5 repair/shutdown within | 1–12 months, monthly monitoring | same | Oct 2020 |
| Growth to next category (EPRI) | 100 % (low cats), 50 % (Cat 3), 10–50 % (Cat 4) | same | Oct 2020 |
| IEA LEE Level thresholds | 1 cm² / 10 cm² / 1 m² instances; pinholes <1 mm | https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf | Dec 2022 |
| LEE aero Cat 3 / Cat 4 lift-drag loss | L/D −30 % & CLmax −5–10 % / L/D >−40 % & CLmax >−10 % | same | Dec 2022 |
| LEE Cat 5 power loss | ">4%" | same | Dec 2022 |
| SkySpecs crack study | ~65,000 damages from >137,000 inspections; 2-yr growth prob. ~10 % (small rotors) vs >40 % (large) | https://skyspecs.com/blog/crack-growth-risk-in-turbine-blades-understanding-the-big-picture/ | 2024-01-12 |
| SkySpecs scale | 275,000 inspections; 130 GW; 15 min/turbine | https://skyspecs.com/product/inspections/ | 2026 (page) |
| Zeitview scale | 60,000 turbines inspected in 2025; 40 countries | https://www.zeitview.com/wind | 2026 (page) |
| IEC TS 62446-3 min irradiance | 600 W/m² in module plane | https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf | 2017 |
| IEC CoA for single hot cell | 10–40 K → CoA 2; >40 K → CoA 3 | same | 2017 |
| IEC CoA for module open-circuit | 2–7 K → CoA 2 | same | 2017 |
| IEC CoA broken front glass | CoA 3 (0–7 K) | same | 2017 |
| Raptor Maps hot-spot priority ΔT bands | <10 °C Low; 10–20 °C Medium; >20 °C High | https://pages.raptormaps.com/raptor-maps-knowledge-hub/reviewing-solar-energy-anomalies | 2026 (page) |
| Raptor InfraredSolarModules | 20,000 images, 12 classes, 24×40 px | https://github.com/RaptorMaps/InfraredSolarModules | 2020-02-14 |
| PV anomaly underperformance | 1.61 % (2019) → 3.13 % (2022); 24.5 GW inspected; $3,350/MW/yr | https://pv-magazine-usa.com/2023/03/07/raptor-maps-points-to-growing-problem-of-pv-system-underperformance/ | 2023-03-07 |
| System-level anomaly losses | string 1.06 %, inverter 0.70 %, combiner 0.67 % | same | 2023-03-07 |
| NBI Good / Fair / Poor | 7–9 / 5–6 / 0–4 | https://www.tarmacview.com/glossary/condition-rating/ | 2026 (page) |
| NBIS routine interval; risk-based | ≤24 mo; Method 1: 12/24/48; Method 2: 12/24/48/72 mo | https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf | Mar 2022 |
| MBEI RC crack CS thresholds | <0.012 in / 0.012–0.05 in / >0.05 in | https://idot.illinois.gov/content/dam/soi/en/web/idot/documents/doing-business/industry-marketplace/bridges-and-structures-services/ielbi-elem-cs-handout-final-20200212-print.pdf | MBEI 2019 (handout 2020-02-12) |
| MBEI PSC crack CS thresholds | <0.004 / 0.004–0.009 / >0.009 in | same | 2019 |
| MBEI spall CS2→CS3 | ≤1 in deep or ≤6 in dia → >1 in deep or >6 in dia | https://hidot.hawaii.gov/highways/files/2014/08/HDOT-BrM-Br-Insp-Quick-Reference-Manual.pdf | 2014 |
| MBEI timber decay CS2→CS3 | <10 % → ≥10 % of section | same | 2014 |
| ISO 4628-3 Ri grades | 0 / 0.05 / 0.5 / 1 / 8 / 40–50 % area | https://www.scribd.com/document/858422778/Iso-4628-3-Assessment-of-Degree-of-Rusting | ISO 2016 |
| ASTM D610 grades | 10 <0.01 % … 4 ~10 % … 0 ~100 % | https://qcsqci.com/astm-d610-explained-rust-grade-scale-for-coating-inspection/ | 2026 (page) |
| ESP Code coating FAIR / POOR | light rusting ≥20 % / breakdown ≥20 % or hard scale ≥10 % | https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/AssemblyDocuments/A.1049(27).pdf | 2011-11-30 |
| ESP Code substantial corrosion | wastage >75 % of allowable margin | same | 2011 |
| Waterfront steel damage grades | thickness loss ≤15 % / 15–30 % / 30–50 % | https://edc.nyc/sites/default/files/2019-10/NYCEDC-WFMMS-Inspection-Guidelines-Manual.pdf | 2019-10 |
| Waterfront RC severe | cracks >1/4 in; >30 % rebar diameter loss; >30 % section loss | same | 2019-10 |
| Waterfront priority-action window | 1–3 years | same | 2019-10 |
| ASCE MOP 130 "significant" damage | ≥20 % reduction in primary-member capacity; rating Poor or below | https://www.ports.org/files/SeminarPresentations/2015Seminars/2015FacEngineering/Ron%20Heffron.pdf | 2015-10 |
| UW-51 elongated limits | 6 mm (t<19); t/3 (19–57); 19 mm (>57 mm) | https://www.therness.com/blog/radiographic-testing-weld-acceptance-criteria-iso-asme-api/ | 2026 (page) |
| API 1104 pore limit | ≤¼ wall and ≤3.2 mm | same | 2026 (page) |
| xBD dataset | 850,736 buildings; 22,068 images; 45,362 km²; 19 disasters | https://arxiv.org/pdf/1911.09296 | 2019 |
| xBD baseline F1 (Major damage) | 0.0094 (weighted overall 0.2654) | same | 2019 |
| ATC-20 damage bins | 0–1 / 1–10 / 10–30 / 30–60 / 60–100 / 100 % | https://www.atcouncil.org/pdfs/rapid.pdf | form © 1995-07 |
| FEMA PDA current guide | 2025 edition effective 2025-07-01 | https://www.fema.gov/disaster/how-declared/preliminary-damage-assessments/guide | 2025 |
| FIST 4-6 pole re-inspection | 12 yr sound / 6 yr minor decay | https://www.usbr.gov/power//data/fist/fist_vol_4/vol4-6.pdf | Aug 1992 |
| CA GO 165 pole cycles | patrol 1/2 yr; detailed 5 yr; intrusive 10 yr (>15-yr poles) | https://detectinspections.com/blog/utility-poles | 2026 (page) |
| Osmose reject detection | comprehensive finds 98 % of rejects; others miss 10–30 % | https://www.osmose.com/wood-pole-inspection | 2026 (page) |
| Insulator defect dataset | MD-Insulator 16,430 images (5,318 defective); mAP@50 88.3 % | https://pmc.ncbi.nlm.nih.gov/articles/PMC10887842/ | 2024 |

---

## Proposed UNIFIED cross-asset severity schema (S0–S4) with native-scale mapping

Design rules: (a) the VLM **always** emits the native scale first, the unified level second; (b) S-levels are defined by **action semantics**, not by appearance, so they are comparable across industries; (c) an explicit `U` (unknown / not assessable) state is mandatory — every standard above has one (FEMA "Inaccessible", MBEI "not inspected", IEC "additional appropriate inspections shall be applied", ATC-20 "Detailed Evaluation recommended"); (d) severity uncertainty is reported as ±1 level, following EPRI's guidance.

| Unified | Name | Action semantics (what the work queue does) | Typical SLA (from sources) |
|---|---|---|---|
| **S0** | No finding / as-built | Record only; baseline for change detection | next routine cycle |
| **S1** | Cosmetic / minor | Log; monitor at routine cadence; bundle with other work | 6–12 mo blade cycle (EPRI); ≤24 mo bridge routine |
| **S2** | Moderate / schedule | Plan repair in next campaign; no operating restriction | blade "6 to 12 months" (EPRI Cat 3–4); waterfront "Priority ... 1 to 3 years"; PV CoA 2 "reasonable period" |
| **S3** | Major / prioritize | Engineering review; repair within weeks–months; consider derate / load posting / partial restriction; increased monitoring | blade "1 to 12 months, with monthly monitoring" (EPRI Cat 4–5); NBI 4 → 12-mo inspection; waterfront Serious "loading restrictions may be necessary" |
| **S4** | Critical / safety | Immediate escalation (same day); stop / derate / isolate / close / red-tag; do not operate until repaired or evaluated | blade Cat 5 "not safe to operate"; IEC CoA 3 "Prompt interruption of operation"; NBI 2–0; ATC-20 UNSAFE |
| **U** | Not assessable | Re-image / close-up / other NDT; never silently default to S0 | — |

**Mapping table (native → unified).** Arrows with "→" are deterministic; "flag" adds a modifier the VLM must set.

| Asset / native scale | S0 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|
| Wind blade — EPRI/industry Cat 1–5 | — | Cat 1, Cat 2 | Cat 3 | Cat 4 | Cat 5 |
| Wind blade — IEA LEE Level 0–5 | L0 | L1, L2 | L3 | L4 | L5 flag `open_LE_or_crack` → S4 else S3 |
| Wind blade — Bladena layers | — | — | Cat 3 (LEP/erosion to laminate) | Cat 4 (first laminate layer) | Cat 5 (through laminate / open LE) |
| Solar — IEC TS 62446-3 CoA | CoA 1 | — | CoA 2 (module/substring, ΔT 2–7 K) | CoA 2 hot cell 10–40 K, string/combiner/inverter outage (production S3) | CoA 3 (>40 K cell, broken glass, arc) |
| Solar — Raptor Maps priority | No-Anomaly | Low (soiling, shading, vegetation, hot spot <10 °C) | Medium (diode, 10–20 °C) | High (>20 °C, cracking, string/combiner/inverter/tracker) | Damaged w/ exposed conductors / burn marks (flag `fire_shock_pathway`) |
| Bridge — NBI component 0–9 | 9, 8 | 7, 6 | 5 | 4, 3 (flag `load_posting_review` at 3) | 2, 1, 0 |
| Bridge — MBEI element CS | CS1 | CS2 | CS3 | CS4 ("structural review") | CS4 + instability / collapse indicators |
| Coatings — ISO 4628-3 / ASTM D610 | Ri0 / 10 | Ri1 / 9–8 | Ri2–Ri3 / 7–5 (patch) | Ri4–Ri5 / 4–0 (full repaint); flag `section_loss` | only if section loss compromises structure |
| Hull — ESP Code coating / wastage | GOOD | — | FAIR | POOR; "substantial corrosion" (>75 % margin) | wastage beyond allowable / fracture |
| Waterfront — six-term overall | Good | Satisfactory | Fair | Poor, Serious (flag `load_restriction`) | Critical |
| Waterfront — element damage grade | No Damage | Minor | Moderate | Advanced | Severe |
| Weld RT — ASME/API/ISO | Accept, no indications | Accept, indications within limits (record) | — (codes have no "monitor") | Reject, non-planar (porosity/slag over limit) → repair before service | Reject, planar (crack, LOF, IP) — zero tolerance |
| Disaster — FEMA PDA | (undamaged) | Affected | Minor | Major | Destroyed; Inaccessible → U |
| Disaster — xBD JDS 0–3 | 0 | — | 1 Minor | 2 Major | 3 Destroyed |
| Disaster — ATC-20 | INSPECTED (Minor/None) | INSPECTED w/ notes | — | RESTRICTED USE (yellow) | UNSAFE (red) |
| Poles — OSHA / FIST / vendor | sound | minor decay (re-inspect 6 yr) | shell rot / woodpecker damage w/o strength loss | "reject" (below safety factor, schedule replace/stub) | "unsafe" per OSHA tests; danger pole; leaning/burned |
| Insulators / hardware (CV classes) | intact | contamination | flashover marks (single unit) | broken/chipped shed; single missing unit | multiple shattered ("self-explosion") units; conductor broken strands (flag `line_outage_risk`) |

**Recommended VLM output contract (per finding):**

```json
{
  "asset_class": "wind_blade | pv_module | bridge_element | steel_coating | hull | waterfront_element | weld_rt | building_disaster | pole | insulator",
  "defect_type": "<native taxonomy term, e.g. 'leading_edge_erosion', 'hot_cell', 'spall', 'lack_of_fusion'>",
  "native_scale": {"standard": "EPRI-5cat | IEA-T46-LEE | IEC-62446-3-CoA | NBI-0-9 | MBEI-CS | ISO-4628-3 | ESP-coating | NYCEDC-6term | ASME-UW51 | FEMA-PDA | xBD-JDS | ATC-20 | OSHA-App-D", "value": "<code>", "criteria_matched": ["<verbatim threshold matched>"]},
  "unified": {"level": "S0|S1|S2|S3|S4|U", "uncertainty": "±1", "flags": ["fire_shock_pathway", "load_posting_review", "open_LE_or_crack", "section_loss", "not_measurable"]},
  "measurements": {"area_cm2": null, "crack_width_mm": null, "delta_t_k": null, "percent_area_rusted": null, "section_loss_pct": null, "confidence": 0.0},
  "action": {"code": "record|monitor|schedule|prioritize|escalate", "sla_days": null, "basis": "<citation to standard clause>"},
  "evidence": {"image_ids": [], "bbox": [], "gsd_mm_per_px": null, "irradiance_wm2": null}
}
```

---

## Implications for our product / edge

1. **"Native scale first" is the credibility moat.** Every incumbent publishes only its own severity numbers (SkySpecs, Zeitview, Raptor Maps). EPRI documents that categorization is disputed between owners, OEMs and ISPs ("categories may be disputed by stakeholders"). A report that cites the *clause and threshold matched* (e.g., "MBEI 1130 CS3: width 0.06 in > 0.05 in") is auditable in a way a vendor's "Severity 3" is not. This is the differentiator to pitch to owners who arbitrate warranty and repair-scope disputes.
2. **The heavy VLM should be prompted with the standard's own tables** (IEC Annex C rows, MBEI defect rows, IEA LEE thresholds, EPRI Table 3-1/3-2, ESP §1.2.11). Those are exactly the artifacts assembled above — they become the RAG corpus. The 2025/26 arXiv work shows RAG-grounded VLMs outperform plain VLMs on blade defects, but on 30 images; we must not overclaim.
3. **Measurability gates severity.** Bridge CS thresholds (0.3 mm / 0.1 mm cracks), IEC ΔT bands, ISO 4628-3 % areas and waterfront section-loss % all need scale/radiometric metadata. The pipeline must carry GSD, irradiance (≥600 W/m² or the thermal grade is invalid per IEC), and emit `U`/`not_measurable` rather than guess. This is also a safety/liability posture judges will respect.
4. **Two-stage triage maps cleanly onto the standards:** small VLM = "S0 vs ≥S1 + image-quality gate" (IEC even distinguishes "simplified" drone inspection from "detailed" inspection); heavy VLM = native + unified + action. Cat 5 / CoA 3 / NBI ≤2 / ATC-20 Unsafe are the "same-hour escalation" class — a single cross-asset escalation channel is a real operational feature.
5. **Prioritization economics differ by industry — expose the right lever:** PV uses production loss (Raptor: modules × STC power × power factor; 3.13 % fleet loss, $3,350/MW/yr); wind uses AEP loss (>4 % at LEE Cat 5) plus structural-failure risk; bridges use load posting/closure; ports use "Priority (1–3 yr) vs Routine". The queue-ranking model should be pluggable per asset class rather than a single "risk score".
6. **Disaster mode is a re-labeling of the same engine:** FEMA / xBD / ATC-20 are all 3–4-level ladders that map onto S1–S4; but xBD's baseline F1 of 0.0094 on "Major" warns that mid-scale classes are where VLMs fail. Demo with pre/post pairs and show confidence + `U` handling.
7. **Human-in-the-loop is non-negotiable in regulated classes** (NBIS certified inspectors; class surveyors; ATC-20 qualified evaluators). Position the product as decision support that pre-fills the native form (SNBI items, MBEI CS quantities, IEC report content list "recommended actions based on classification", FEMA matrix), not as the inspector of record.
8. **Data-scarcity is public and quantifiable:** only ~30 labeled blade images in the cited VLM paper; 20,000 tiny 24×40 IR tiles for PV; 850k satellite footprints for disaster. A startup edge is a **standards-aligned labeling schema** (the JSON above) that lets owners contribute labeled findings in their own native scale.

---

## Open questions / gaps

- IEC 61400-5 (blades) and DNVGL-ST-0376 content on in-service damage categorization — **not fetched** (webstore 404); confirm whether either now includes informative categorization guidance as EPRI hoped.
- Exact SkySpecs / Zeitview / Sulzer Schmid / OEM (GE, Vestas, Siemens Gamesa) 1–5 category definitions — proprietary; **not published**. Oxmaint's version is a third-party paraphrase.
- Raptor Maps default power-factor values per anomaly — behind admin UI; **not found**.
- 23 CFR 650.305 "critical finding" wording and 12-month interval rule for Poor bridges — Federal Register blocked; rely on secondary sources for now.
- ASCE MOP 130 (2015 / 2nd ed. 2025) verbatim six-level definitions and element damage grades — paywalled; NYC EDC manual used as the public proxy.
- Marine-growth thickness grading and class-society (DNV/ABS/LR) underwater visual-defect ladders — **not found**.
- RUS Bulletin 1730B-121 pole classes ("reject", "priority reject") and NESC remaining-strength threshold — HTTP 403; **not verified**.
- xBD Joint Damage Scale per-level structural descriptions (Figure 4) — image only; obtain from the paper PDF figure or xView2 site if needed for prompts.
- ASTM D610 distribution codes (S/G/P/H) and AMPP/NACE visual guides — **not extracted**.
- Utility-grade insulator/conductor severity ladders (EPRI, IEEE) — **not found**; only CV-paper classes.
- Web-search budget was exhausted mid-task (200/200); the ~20 remaining fetches were URL-guessing, so vendor pages may have newer 2026 versions not seen here.

---

## Sources

1. https://restservice.epri.com/publicdownload/000000003002019669/0/Product — EPRI 3002019669, "A White Paper on Wind Turbine Blade Defect and Damage Categorization: Current State of the Industry" (Oct 2020; prepared by DNV GL). Tables 2-1, 3-1, 3-2, 3-3, 3-4.
2. https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf — IEA Wind Task 46, "Leading Edge Erosion Classification System" (Dec 2022; Sandia SAND2023-11986R). Levels 0–5, aero categories, Bladena and EPRI summaries.
3. https://skyspecs.com/blog/standardization-of-blade-damage-categorization-critical-to-the-future-of-wind-energy/ — SkySpecs blog on need for standardization (2019-10-17).
4. https://skyspecs.com/blog/crack-growth-risk-in-turbine-blades-understanding-the-big-picture/ — SkySpecs crack growth study (2024-01-12).
5. https://skyspecs.com/product/inspections/ — SkySpecs inspections product page (scale stats).
6. https://www.zeitview.com/wind — Zeitview wind page (damage types, 60,000 turbines in 2025).
7. https://onyxinsight.com/resources-support/articles/blade-damage-whos-the-judge/ — ONYX Insight on 5-tier categorization variability.
8. https://oxmaint.com/industries/power-plant/wind-turbine-blade-repair-erosion-lightning-programs — third-party CMMS vendor summary of Cat 1–5 actions (marketing page).
9. https://www.sulzerschmid.ch/ — Sulzer Schmid (Siemens Gamesa standardization collaboration mention).
10. https://clobotics.com/resources/insights/wind-turbine-blade-inspection-methods-defects-reporting/ — Clobotics blade defect taxonomy (qualitative).
11. https://www.dnv.com/energy/standards-guidelines/dnv-rp-0573-evaluation-of-erosion-and-delamination-for-leading-edge-protection-systems-of-rotor-blades/ — DNV-RP-0573 scope (Ed. 2020-12, amended 2021-10).
12. https://arxiv.org/abs/2510.22868 — "Seeing the Unseen": RAG + VLM zero-shot blade inspection (30 images).
13. https://arxiv.org/abs/2407.07186 — barely-visible hairline crack dataset for blades (2024-07-09).
14. https://datatec.es/wp-content/uploads/2019/09/Normativa-IEC-TS-62446-3.pdf — IEC TS 62446-3:2017 (preview copy incl. Table 3, Table 4, Annex C matrix).
15. https://thermalvariations.com/learn/iec-62446-3-thermal-inspection — secondary explainer of IEC 62446-3 classes.
16. https://www.sciencedirect.com/science/article/pii/S2451904923007321 — aerial IR PV thermography (5 anomaly patterns A–E).
17. https://pages.raptormaps.com/raptor-maps-knowledge-hub/reviewing-solar-energy-anomalies — Raptor Maps Solar Anomaly Glossary with priorities and ΔT bands.
18. https://pages.raptormaps.com/raptor-maps-knowledge-hub/calculating-impact-of-anomalies-power-factors — Raptor Maps power-factor impact formula.
19. https://github.com/RaptorMaps/InfraredSolarModules — Raptor Maps open IR dataset (12 classes, 20,000 images).
20. https://pv-magazine-usa.com/2023/03/07/raptor-maps-points-to-growing-problem-of-pv-system-underperformance/ — Raptor Maps Global Solar Report numbers (2023-03-07).
21. https://iea-pvps.org/wp-content/uploads/2020/01/IEA-PVPS_T13-01_2014_Review_of_Failures_of_Photovoltaic_Modules_Final.pdf — IEA PVPS T13-01:2014 module failure review.
22. https://www.iea-pvps.org/wp-content/uploads/2025/02/IEA-PVPS-T13-30-2025-EX-SUMM-Degradation-and-Failure.pdf — IEA PVPS T13-30:2025 exec summary (PVFS 2025).
23. https://www.fhwa.dot.gov/bridge/snbi/snbi_march_2022_publication.pdf — FHWA SNBI, FHWA-HIF-22-017 (Mar 2022): Table 20 condition codes; B.IE.07 risk-based intervals.
24. https://www.tarmacview.com/glossary/condition-rating/ — secondary: NBI 0–9 with Good/Fair/Poor buckets.
25. https://www.geocadra.com/en/standards/fhwa-nbis-snbi — secondary: NBI ratings, CS1–4, 24-month interval, critical finding ≤3.
26. https://idot.illinois.gov/content/dam/soi/en/web/idot/documents/doing-business/industry-marketplace/bridges-and-structures-services/ielbi-elem-cs-handout-final-20200212-print.pdf — Illinois DOT reproduction of AASHTO MBEI 2019 elements/defects/condition states incl. crack-width footnotes.
27. https://hidot.hawaii.gov/highways/files/2014/08/HDOT-BrM-Br-Insp-Quick-Reference-Manual.pdf — Hawaii DOT MBEI quick reference (defect CS tables).
28. https://ifactoryapp.com/industries/infrastructure-management/element-level-bridge-inspection-mbei-condition-states — secondary MBEI CS1–CS4 overview.
29. https://onlinepubs.trb.org/onlinepubs/nchrp/nchrp_rpt_654AppendixA.pdf — NCHRP 654 App. A crack-width literature (FHWA/MDOT hairline <0.004 in, narrow <0.010 in).
30. https://www.fhwa.dot.gov/bridge/nbi/140725_a3.pdf — FHWA SNBIBE FAQ (element data references AASHTO MBEI 2013).
31. https://www.scribd.com/document/858422778/Iso-4628-3-Assessment-of-Degree-of-Rusting — ISO 4628-3 rust-grade table summary (Ri0–Ri5 %, ASTM mapping).
32. https://www.iso.org/standard/66400.html — ISO 4628-3:2016 catalogue entry.
33. https://standards.iteh.ai/catalog/standards/cen/d6ad1765-c591-4894-838f-454bc1312e0b/en-iso-4628-3-2024 — EN ISO 4628-3:2024 catalogue entry.
34. https://qcsqci.com/astm-d610-explained-rust-grade-scale-for-coating-inspection/ — ASTM D610 grade table (percent rusted area).
35. https://wwwcdn.imo.org/localresources/en/KnowledgeCentre/IndexofIMOResolutions/AssemblyDocuments/A.1049(27).pdf — IMO Resolution A.1049(27), 2011 ESP Code: coating condition GOOD/FAIR/POOR, substantial corrosion.
36. https://edc.nyc/sites/default/files/2019-10/NYCEDC-WFMMS-Inspection-Guidelines-Manual.pdf — NYC EDC WFMMS Inspection Guidelines Manual (Oct 2019): six-term ratings, damage grades, action tiers.
37. https://www.ports.org/files/SeminarPresentations/2015Seminars/2015FacEngineering/Ron%20Heffron.pdf — Heffron, "New ASCE Waterfront Facilities Inspection & Assessment Manual" (AAPA, Oct 2015).
38. https://www.asce.org/publications-and-news/civil-engineering-source/article/2025/07/25/new-mop-brings-waterfront-facilities-inspection-and-assessment-practices-into-the-modern-era — ASCE MOP 130 2nd ed. (2025) article.
39. https://trid.trb.org/View/1410660 — TRID record for ASCE MOP 130 (2016 entry).
40. https://ndtscan.com/services/underwater-surveying-and-inspection/ — ROV inspection vendor (standards named, no grading ladder).
41. https://www.therness.com/blog/radiographic-testing-weld-acceptance-criteria-iso-asme-api/ — RT acceptance criteria summary (ASME UW-51, B31.3, API 1104, ISO 5817/10675, AWS D1.1).
42. https://ndtqualityhub.blogspot.com/2026/04/asme-section-viii-rt-acceptance-criteria-uw51-uw52.html — UW-51 vs UW-52 explainer (Apr 2026).
43. https://www.weldingandndt.com/acceptance-criteria-for-weld-defects/ — rounded-indication definition.
44. https://www.fema.gov/sites/default/files/documents/fema_pda_individual-assistance-damage-matrix.pdf — FEMA PDA Individual Assistance Damage Matrix (manufactured and conventional homes).
45. https://www.fema.gov/disaster/how-declared/preliminary-damage-assessments/guide — FEMA PDA Guide page (2025 edition effective 2025-07-01).
46. https://www.fema.gov/sites/default/files/2020-07/fema_preliminary-disaster-assessment_pocket-guide.pdf — FEMA PDA Pocket Guide (May 2020).
47. https://arxiv.org/pdf/1911.09296 — Gupta et al., "xBD: A Dataset for Assessing Building Damage from Satellite Imagery" (2019): Joint Damage Scale, stats, baseline F1.
48. https://www.emergentmind.com/topics/xbd-dataset — xBD summary page (2025-08-29).
49. https://www.atcouncil.org/pdfs/rapid.pdf — ATC-20 Rapid Evaluation Safety Assessment Form.
50. https://www.atcouncil.org/atc-20 — ATC-20 program page (placards).
51. https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.269AppD — OSHA 1910.269 App. D, Methods of Inspecting and Testing Wood Poles.
52. https://www.usbr.gov/power//data/fist/fist_vol_4/vol4-6.pdf — Bureau of Reclamation FIST 4-6 Wood Pole Maintenance (Aug 1992).
53. https://www.katapultengineering.com/blog/utility-pole-inspections — pole inspection cycles (8–12 yr).
54. https://detectinspections.com/blog/utility-poles — CA GO 165 intervals; defect list; standards cited.
55. https://www.osmose.com/wood-pole-inspection — Osmose inspection methods, reject detection rates, cycles.
56. https://pmc.ncbi.nlm.nih.gov/articles/PMC10887842/ — WDTA-YOLO insulator defect detection (3 defect classes; MD-Insulator dataset).
57. https://pmc.ncbi.nlm.nih.gov/articles/PMC11128844/ — lightweight insulator defect model (CPLID; mAP 97.3 %).
