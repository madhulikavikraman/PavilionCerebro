# Competitive Landscape: AI Inspection of Bridges / Civil Structures, Power Lines / Poles / Substations, and Telecom Towers

Research angle: `competitors_bridges_powerlines_telecom`
Compiled: 2026-09-24 (Los Angeles). Author: research subagent for the Origin Weekend Fall 2026 team (Prompt D).
Method: 30+ web searches and ~60 page fetches. Facts carry a source URL; anything without a URL is marked **Inference:** or **not found**. Claims taken from a search-engine snippet whose underlying page could not be opened are marked **(snippet, unverified)**. Vendor-authored marketing pages are labelled as such.

---

## Summary

1. **The capture layer is crowded and well funded; the grading/reporting layer is not.** Skydio raised a $110M Series F at a $4.4B valuation (Apr 23, 2026) and says 49 of 50 US state DOTs use its drones, yet its own bridge case studies (MnDOT/Collins, TxDOT, NDOT/Stantec) describe 3D Scan digital twins and *no AI defect detection or condition grading* ([Skydio Series F](https://www.skydio.com/blog/skydio-series-f), [Skydio bridge page](https://www.skydio.com/solutions/bridge-inspection), [Collins story](https://www.skydio.com/customer-stories/collins-engineers-inc)).
2. **Utilities are the most mature AI-analytics segment and the hardest to enter head-on.** Buzz Solutions closed a $20M Series A on Aug 4, 2026 ($30M total; Dominion, AEP, NYPA; 25,000 images/hour; 50+ pre-trained models; "90%+ detection accuracy") ([Dealroom](https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/), [buzzsolutions.com](https://www.buzzsolutions.com/)). Sharper Shape (95% accuracy claim, 40+ components), Hepta (30+ DSO/TSOs in 21 countries, 3,000 km/month), Optelos (ComEd, SSE), Zeitview ($60M, Mar 2025; 200,000 assets in 2024), Cyberhawk (500k inspections) and Noteworthy AI (fleet-vehicle cameras; FirstEnergy, NextEra, Exelon) all sell closed-vocabulary CNN detectors plus a data platform. **None of the pages fetched advertises VLM/LLM narrative report generation or standards-cited grading.**
3. **Bridges/civil structures have no dominant AI-grading vendor.** Dynamic Infrastructure (founded 2017; Suffolk County NY; funding not found; company domain currently unreachable), Mind Foundry Windward Inspect (UK; WSP pilot Dec 2024; 50% reporting-time reduction claim), Datagrid (AI agents for NBIS/SNBI paperwork, Dec 2025), and university programs (UMD SMART grant Oct 2025; NC A&T with NCDOT) are the field. Regulation requires condition ratings to be assigned by qualified inspectors, so every credible player positions as *inspector assist*, not replacement ([Datagrid](https://datagrid.com/blog/ai-agent-identifies-cracks-deterioration-bridge-deck-photos)).
4. **Telecom towers are an inventory/capacity problem more than a damage problem today.** Bentley OpenTower iQ (launched Mar 25, 2021; one operator digitized 25,000 towers; "tower visits reduced by 50%") and Pix4Dinspect (antenna auto-detection) dominate; Optelos integrated with OpenTower iQ in Sept 2023. Damage grading against ANSI/TIA-222 condition assessment is under-served ([Bentley](https://www.bentley.com/software/opentower-iq/), [Optelos](https://optelos.com/digitally-transform-cell-tower-inspection/)).
5. **Regulation makes demand non-discretionary.** 23 CFR 650.311: routine bridge inspections at intervals not to exceed 24 months (12 months if condition rating 3 or less; 48 months extended; up to 72 months under Method 2 risk-based) ([LII](https://www.law.cornell.edu/cfr/text/23/650.311)). SNBI: first SNBI-based NBI submittal March 2026; 100% verified data due March 2028 ([AssetIntel, Aug 2025](https://www.assetintel.co/blogs/the-fhwa-metrics-guide-meeting-nbis-standards-today-and-snbi-tomorrow)). CPUC GO 165 mandates patrol, detailed (3-5 yr) and intrusive (10/20 yr) pole inspections **(snippet)**. California WMPs: PG&E aerial-inspected 220,000 poles in 2024-25; SCE runs 200,000+ inspections/yr in high-fire-risk areas; SDG&E plans ~6,500 drone inspections per WMP cycle.
6. **FAA Part 108 (BVLOS) is still not final as of Sept 2026** (NPRM Aug 7, 2025; ~3,100 comments; at OIRA since July 10, 2026; FAA "hopes" to publish by end-2026). Until then routine BVLOS needs a Part 107 waiver. Capture volume will jump when it lands; analytics of *already captured* imagery is not blocked ([Airdata](https://airdata.com/blog/2026/part-108), [Flight Brief](https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026)).
7. **Price signals are clear at the hardware layer and opaque at the analytics layer.** Skydio X10 ~$14k-25k/unit; 3D Scan $2,999/yr (plus a required Autonomy Enterprise license, historically $1,500/yr); Elios 3 system $40k-55k; DroneDeploy $329-$649/seat/month; every analytics vendor (Buzz, Sharper, Optelos, Hepta, Zeitview, Bentley iQ) is quote-only. Hepta claims average savings of EUR 3M/yr per utility ([heptainsights.com](https://heptainsights.com/)).
8. **Peer-reviewed support for the team's small-model-gate + heavy-model-grader design exists.** arXiv 2605.26533 (May 26, 2026): YOLO detector + 4-bit Qwen-2.5-1.5B (QLoRA) produced structured JSON reports with a 4% hallucination rate and 8.6/10 expert score vs 65% and 3.3/10 for a zero-shot VLM, at 47 tok/s on a single T4 ([arXiv](https://arxiv.org/abs/2605.26533)). Zero-shot VLM grading alone is not credible; grounded hybrid is.
9. **White space for a new entrant:** (a) standards-cited grading across asset classes (AASHTO MBEI condition states, GO 165 condition ratings, TIA-222 checklist) with the clause quoted next to each finding; (b) auditable narrative reports with evidence crops; (c) capture-agnostic ingestion (phones, legacy PDFs, any drone) - Dynamic Infrastructure's CEO: "Drone inspection is fancy, but when you look at the numbers it's less than 1% of the market" ([CTech, Jan 2021](https://www.calcalistech.com/ctech/articles/0,7340,L-3889391,00.html)); (d) transparent per-asset pricing for the long tail (counties, co-ops, drone service providers, consulting engineers) that enterprise vendors ignore; (e) a disaster/storm triage mode.

---

## Detailed findings

### A. Capture-layer platforms (drones, robots, docks)

#### Skydio (Redwood City, CA)
- **Sells:** X10 / X10D autonomous drones, Dock for X10, software (3D Scan, Asset Command, Ops Center, DFR Command). Markets: public safety, defense, critical infrastructure, site security ([Series F post, Apr 23, 2026](https://www.skydio.com/blog/skydio-series-f)).
- **Funding:** $230M Series E (2023) ([Skydio](https://www.skydio.com/blog/skydio-raises-230-million-series-e-funding-round)); $110M Series F, $4.4B valuation, "hundreds of millions in annual revenue" (Apr 2026) ([Skydio](https://www.skydio.com/blog/skydio-series-f), [DroneLife](https://dronelife.com/2026/04/28/skydio-series-f-110m-funding-us-manufacturing/)).
- **Pricing:** X10 "$16,000 to $25,000 a unit in public safety deployments"; ~$15,000 standalone ([DroneXL](https://dronexl.co/drone-companies/skydio/skydio-x10/)); independent guide: "$14,000-$22,000" ([Reliamag, Mar 2026](https://reliamag.com/guides/best-drones-industrial-inspection-2026/)). 3D Scan add-on "$2,999 per year" ([Capterra](https://www.capterra.com/p/238131/Skydio-3D-Scan/)); users report 3D Scan requires the Autonomy Enterprise Foundation license ($1,500/yr in 2021), so ~$4,500/yr software per drone ([SkydioPilots forum, Jun 2021](https://skydiopilots.com/threads/3-d-scan-is-more-expensive-than-anyone-is-reporting.870/)).
- **Bridge claims:** "49 out of 50 state transportation agencies" use Skydio; "half the time and at less than half the cost"; "cut inspection costs by as much as 75%" (vendor marketing) ([Skydio bridge page](https://www.skydio.com/solutions/bridge-inspection)). MnDOT/Collins: 30% cost reduction, ~50% field-time reduction, "70-80% of defects detected on the digital twins before field inspections" ([Skydio](https://www.skydio.com/customer-stories/collins-engineers-inc)). NDOT/Stantec: 10 days to 5 days, "50% cost savings" ([Skydio](https://www.skydio.com/customer-stories/stantec-transforms-infrastructure-inspections-with-autonomous-drones)). TxDOT: Pecos River High Bridge; "57,000 bridges" in Texas on NBI; 3D scans every two years for change tracking ([Skydio](https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections)). NCDOT: first statewide BVLOS bridge-inspection waiver with Skydio (Oct 2020) ([Skydio blog](https://www.skydio.com/blog/ncdot-bvlos-waiver-for-bridge-inspection-skydio-2)).
- **Grading approach:** None. Asset Command organizes captures by asset ID and pushes "structured datasets ... downstream to analysis tools" via APIs ([Asset Command](https://www.skydio.com/software/asset-command)). No AASHTO/NBI mapping, no defect AI on the pages fetched.
- **Weaknesses:** Hardware-first; AI is flight autonomy, not condition assessment; software stack is per-drone licensed; leaves the grading/report layer to partners or the inspector.

#### Flyability (Switzerland) - Elios 3
- **Sells:** Collision-tolerant caged drone for confined spaces (box girders, culverts, piers); Inspector software; LiDAR/UT/RAD payloads quote-only ([Flyability pricing page](https://www.flyability.com/elios-3-price)).
- **Pricing:** "Complete system approximately $40,000-$55,000" ([Reliamag, Mar 2026](https://reliamag.com/guides/best-drones-industrial-inspection-2026/)); other listings cite ~$25,000 base, $40,000+ with LiDAR **(snippet)**.
- **Bridge relevance:** Used in MnDOT Phase 3 confined-space work (20-25 bridges, 2017-18) ([MnDOT research](https://mntransportationresearch.org/tag/drone/)); claims >$3,000 saved on a small bridge vs truck rental and traffic control **(snippet, Flyability case study)**.
- **Weaknesses:** 12-minute flight time without payload **(snippet)**; no AI grading; niche (interiors).

#### Voliro (Zurich)
- **Sells:** Voliro T contact-inspection drone (UT thickness etc.), subscription incl. hardware, payloads, training, insurance ([Voliro blog](https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/), [Reliamag](https://reliamag.com/guides/best-drones-industrial-inspection-2026/)).
- **Funding:** Series A extension to $23M total (Jun 16, 2025; noa, UBS debt; Cherry Ventures led A). 40+ customers, 17 countries, 100+ contact inspections/month; Chevron, Holcim, Acuren. Roadmap explicitly includes "AI-powered diagnostics" ([Voliro](https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/)).
- **Weaknesses:** NDT-contact niche (flare stacks, tanks, transmission towers, wind blades); not a visual grading platform.

#### Percepto (Israel) - drone-in-a-box
- **Sells:** AIM software + autonomous docked drones; utility solution launched Mar 26, 2025 with "FAA-approved BVLOS remote operations", thermal + RGB analytics, GIS/SAP integration ([Percepto](https://percepto.co/percepto-launches-ai-powered-solution-for-electric-utilities/)). FPL plans "hundreds of Percepto drones" across substations; relationship since 2018 ([Renewable Energy World, Mar 2025](https://www.renewableenergyworld.com/power-grid/grid-modernization/autonomous-drone-company-releases-end-to-end-ai-powered-remote-inspection-solution-at-distributech/)).
- **Funding:** $67M Series C (Jun 13, 2023), >$139M total; Koch Disruptive Technologies, Zimmer Partners ([Facilities Dive](https://www.facilitiesdive.com/news/percepto-drone-raises-67M-gets-faa-waiver/652827/)).
- **Weaknesses:** Fixed-site (substations, plants); pricing undisclosed; AI is anomaly/thermal, not standards-based grading.

#### Ondas / American Robotics / Airobotics
- Acquired American Robotics for $70.6M (2021) and Airobotics (2023) **(snippet)**. Optimus is "the only FAA Type Certified" sUAS for security/inspection; BVLOS waiver incl. flights over people/vehicles from a remote ops center (Jan 3, 2025) ([Ondas IR](https://ir.ondas.com/press-releases/detail/187/ondas-american-robotics-secures-its-latest-faa-bvlos)). Q2 2026 revenue $83.8M, backlog $757M **(snippet, financialcontent)** - now largely defense/border security. **Inference:** not a direct competitor for inspection analytics.

#### Infravision (Australia/US)
- $91M Series B led by GIC (Nov 4, 2025); 40+ projects, 4 countries; **construction (power-line stringing), not inspection** ([DroneLife](https://dronelife.com/2025/11/04/infravision-secures-91-million-to-scale-drone-powered-grid-infrastructure/)). Signals investor appetite for grid robotics.

#### Gecko Robotics (Pittsburgh) - adjacent
- Wall-climbing robots + Cantilever software for boilers, tanks, pipelines; Navy, Air Force, Siemens, ADNOC; $71M Navy deal (Mar 2026) ([geckorobotics.com](https://www.geckorobotics.com/)). Funding/valuation: **not verified this session**. Not in bridges/powerlines/telecom.

### B. Utility analytics platforms (power lines, poles, substations)

#### Buzz Solutions (Palo Alto) - PowerAI, PowerGUARD
- **Sells:** Visual AI platform for transmission, distribution, substations, solar; PowerGUARD real-time substation video analytics. Integrations: Esri, IBM Maximo ([buzzsolutions.com](https://www.buzzsolutions.com/)).
- **Buyers/customers:** Dominion Energy (47,000 transmission towers analyzed), AEP Texas (88,000+ images in a season), NYPA, Ameren, City of Troy (1,118 hours/yr manual review eliminated) ([buzzsolutions.com](https://www.buzzsolutions.com/)).
- **Funding:** $20M Series A led by S3 Ventures, Aug 4, 2026 (GoPoint, HearstLab, Blackhorn); $30M total; customers tripled, revenue +400% YoY; expanding to utility-scale solar ([Dealroom](https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/)).
- **Accuracy claims:** "25,000+ images/hour", "0.6 seconds per image", "50+ pre-trained models", "70% improved inspection analysis efficiency", "90%+ detection accuracy" (vendor) ([buzzsolutions.com](https://www.buzzsolutions.com/)).
- **Grading/report:** detects and maps assets/defects/anomalies; prioritization dashboards. No LLM/agent/report-writing features disclosed. **Pricing:** not disclosed.
- **Weaknesses:** Closed defect taxonomy; utility-only; enterprise sales cycle; no bridges/telecom.

#### Sharper Shape (Helsinki / Salt Lake City) - CORE, Asset Insights
- **Sells:** Sharper CORE platform + Asset Insights (Oct 8-9, 2024): ML component identification (40+ distribution/transmission components) and defect detection (cracked insulators, rust, transformer leaks); "analyze 1,000 images instantly" with "over 95% accuracy"; Living Digital Twin ([Sharper Shape](https://sharpershape.com/sharper-shape-bolsters-utility-inspection-offering-with-ai-powered-asset-insights-for-automated-component-identification-and-defect-detection/), [DroneLife](https://dronelife.com/2024/10/09/sharper-shape-introduces-ai-powered-asset-insights-for-utility-inspections/)).
- **Buyers:** Tier-1 utilities and drone service providers (Soaring Eagle Technologies named). **Funding:** $18M Series B, May 2022 **(snippet, Tracxn/GeoWeek; not verified on page)**. **Pricing:** not disclosed.
- **Weaknesses:** Utility-only; LiDAR/helicopter heritage; accuracy claim is unqualified (no dataset, no precision/recall split).

#### Hepta Insights / Hepta Airborne (Estonia) - uBird
- **Sells:** uBird software ingesting drone, helicopter, LiDAR, satellite and ground-patrol photos; detects mechanical faults, corrosion, missing components, thermal anomalies, vegetation; API/CMMS/EAM/GIS integrations ([heptainsights.com](https://heptainsights.com/)).
- **Traction/claims:** "more than 30 DSOs and TSOs in 21 countries", ">3000 KM of power lines every month", DTEK 300% SAIDI improvement, Enefit cycle 7 yrs to 2.5 yrs, "average of EUR 3,000,000 per utility" annual savings (vendor) ([heptainsights.com](https://heptainsights.com/)). Cross-arm models: 95% precision, F-score >94%, trained on >10,000 images (May 17, 2022) ([Hepta](https://heptainsights.com/latest-ai-models-added-to-heptas-power-line-inspection-platform-ubird/)). Earlier: "250 km of power line data ... in 5 minutes" vs 30 engineer-days; ">33% increased accuracy" vs conventional ([Tehnopol, Feb 3, 2021](https://www.tehnopol.ee/en/hepta-airborne-raises-e2m-to-digitize-energy-infrastructure-and-automate-inspection/)).
- **Funding:** EUR 2M seed (Feb 2021; SpeedUp, EIT InnoEnergy) ([Tehnopol](https://www.tehnopol.ee/en/hepta-airborne-raises-e2m-to-digitize-energy-infrastructure-and-automate-inspection/)). Later rounds: **not found**.
- **Weaknesses:** Europe-centric; small; per-defect models added one class at a time.

#### Optelos (Texas)
- **Sells:** Visual data management + AI model library ("select from a large library of AI models or deploy their own"), fault detection (insulators, corrosion, missing components, pole/tower defects), vegetation via LiDAR, anomaly scoring/severity prioritization, custom reports, trouble tickets, EAM/GIS/ServiceNow integration ([Optelos utilities](https://optelos.com/utilities-inspections/)).
- **Customers:** ComEd, United Utility, Scottish & Southern Electric, Grupo Saesa (utilities); Viaero Wireless, a Tier-1 carrier (telecom: onsite time 5 days to 2.4 days, "52% labor cost savings per 5G tower upgrade") ([Optelos telecom](https://optelos.com/telecom/cell-tower-inspection-audits/)). Partnered with FlyGuys (drone service network) and Bentley OpenTower iQ (Sept 5, 2023) ([Optelos](https://optelos.com/digitally-transform-cell-tower-inspection/)).
- **Pricing:** "customizable" quote-only ([SoftwareSuggest](https://www.softwaresuggest.com/optelos)). **Funding:** not found.
- **Weaknesses:** Platform/DSP tooling rather than an opinionated grading engine; "millimeter-level accuracy" claim is about photogrammetry, not defect classification.

#### Zeitview (formerly DroneBase, Los Angeles)
- **Sells:** Insights platform + managed capture network; sectors solar, wind, utilities, properties, telecom. $60M round led by Climate Investment (Mar 2025; prior $55M two years earlier); "over 200,000 assets" inspected in 2024 across 80 countries, doubled YoY ([pv magazine USA](https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/), [BusinessWire](https://www.businesswire.com/news/home/20250304009141/en/Zeitview-Secures-$60M-to-Advance-AI-Powered-Inspections-of-Global-Critical-Infrastructure)).
- **Weaknesses:** Solar-heavy; telecom page not reachable (404) so telecom depth unclear; services-plus-software model.

#### Cyberhawk (Scotland) - iHawk
- 40 countries, 300+ customers, "11k iHawk users", "over 500k inspections"; Shell, BP, National Grid, AEP, Duke Energy; "proprietary AI models" for defect detection; quote-only ([thecyberhawk.com](https://thecyberhawk.com/)). Services-led.

#### Noteworthy AI (US) - Noteworthy Inspect
- Smart cameras on utility fleet vehicles detect pole defects (cross-arm damage, leaning poles), inventory assets, storm damage; customers FirstEnergy, NextEra, Alabama Power, Exelon, Georgia Power, Xcel; claims "only 10% of poles receive annual evaluation", up to 75% O&M cost reduction, storm assessment "up to 50x faster"; investors Techstars, Earthshot; NVIDIA/Dell/Esri partners ([noteworthy.ai](https://www.noteworthy.ai/)). **Relevance:** proves non-drone (ground-vehicle) capture is a real channel for pole condition data.

#### Asset Vision (Australia, ASX: ASV)
- AutoPilot vehicle-mounted road-defect AI, CoPilot field capture, cloud asset platform; roads first, bridges/poles secondary; councils, state transport, ports ([Asset Vision](https://www.assetvision.com.au/2026/05/28/ai-condition-monitoring/)). No metrics or pricing published.

### C. Bridge / civil-structure analytics

#### Dynamic Infrastructure (New York / Israel / Germany)
- Founded 2017 by Saar Dickman (CEO) and Amichay Cohen; SaaS that analyses existing inspection photos and PDF reports to find deterioration (erosion, rust) and tracks health over 5/10/20-year horizons; customers in Israel, Germany, Greece, Italy, Switzerland, US (Suffolk County, NY) and Horsham Rural City Council (Victoria, Australia). CEO quote: "Drone inspection is fancy, but when you look at the numbers it's less than 1% of the market" ([CTech, Jan 25, 2021](https://www.calcalistech.com/ctech/articles/0,7340,L-3889391,00.html)).
- Described in 2026 coverage as an "Engineering AI agent platform for critical civil infrastructure" and "the category's most established player" **(snippet, TheStreet/iFactory; TheStreet page 403)**. A Global Highways article titled "Faster AASHTO bridge defect detection with Dynamic Infrastructure's AI platform" exists ([URL](https://globalhighways.com/faster-aashto-bridge-defect-detection-dynamic-infrastructures-ai-platform)) but returned 403; AASHTO mapping details **not verified**.
- **Funding / pricing:** **not found**. Company domains dynamicinfrastructure.ai (parked) and dynamicinfrastructure.com (no response) were unreachable on 2026-09-24. **Inference:** small, possibly restructured; the "most established" label comes from a competitor's marketing page.

#### Mind Foundry (Oxford, UK) - Windward Inspect
- App-based capture (incl. 360-degree cameras), image rectification, AI defect type/extent detection, millimetre-accurate defect maps, change over time; WSP pilot in South Wales (Dec 2024) on rail and footbridges; claims 48% lifecycle cost saving, 30% less planning, 30% less inspection, 50% less reporting time ([Mind Foundry WSP case study](https://www.mindfoundry.ai/resources/case-study/wsp-windward-inspect)). UK spends GBP 1.5B/yr on ~100,000 road/rail structures **(snippet, New Civil Engineer, Mar 2025)**. Pricing not disclosed. Positioned around UK "digital custodianship", not US NBIS/AASHTO.

#### Datagrid (US) - AI agents for bridge inspection records
- Audit Agent and Fast Search Agent validate inspection documents/photos against audit requirements, support AASHTO Good/Fair/Poor/Severe condition states and prepare SNBI JSON submissions; explicitly leaves condition ratings to qualified personnel per NBIS; screening uses "approved computer-vision models"; no pricing, no named customers (published Dec 17, 2025; updated Aug 17, 2026) ([Datagrid](https://datagrid.com/blog/ai-agent-identifies-cracks-deterioration-bridge-deck-photos)). **Inference:** closest thing found to an LLM-agent product in bridges, but it is a horizontal document-agent company, not a vision-grading engine.

#### AssetIntel (bridge management software)
- Publishes NBIS/SNBI compliance content (23 FHWA metrics, timelines); a BMS vendor rather than an AI-vision vendor ([AssetIntel, Aug 7, 2025](https://www.assetintel.co/blogs/the-fhwa-metrics-guide-meeting-nbis-standards-today-and-snbi-tomorrow)). **Inference:** potential integration partner/channel (SNBI export target).

#### Academic / public programs
- University of Maryland: drones (LiDAR + thermal) plus AI to flag corrosion, cracks, water penetration and build digital twins; USDOT SMART grant with North Central Regional Planning Commission (Salina, Kansas) (Oct 30, 2025) ([UMD CEE](https://cee.umd.edu/news/story/affordable-bridge-inspection-with-ai)).
- NC A&T / NCDOT: $300k+ research phase; NCDOT maintains 13,500 bridges; goal "integrating UAVs into bridge inspection processes - but not replace - human inspectors"; partners Skydio, Parrot, Digital Aerolus (Sept 13, 2021) ([NC A&T](https://www.ncat.edu/news/2021/09/ncdot-industry-uav-bridge-inspection.php)).
- Caltrans DRISI Task 4419 "Development of Autonomous Drone Inspection for Bridge Maintenance" (research note May 2025; results Nov 2025) - PDFs are image-only, content **not extracted** ([Caltrans RNS](https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-notes/task4419-rns-05-25-a11y.pdf), [Caltrans RRS](https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-results/task4419-rrs-11-25-a11y.pdf)).
- Research on automated AASHTO condition-state prediction exists (e.g., deck-crack condition-state assessment, Sensors 2023: https://doi.org/10.3390/s23094192) but no commercial product found that outputs element-level CS1-CS4 quantities.

### D. Telecom tower inspection

#### Bentley Systems - OpenTower iQ (powered by iTwin)
- Launched Mar 25, 2021 as a co-venture with Visual Intelligence (Houston) and Aeroprotechnik (Portugal); drone imagery to millimetre-accurate digital twins; AI detects "bolts, wires, ladders and other items"; targets operators with "tens of thousands of towers" ([DE247](https://www.digitalengineering247.com/article/bentley-acceleration-initiatives-launchesopentower-iq)).
- Product page: AI asset detection/classification, mount capacity analysis, colocation planning; case studies "tower visits reduced by 50%" and "25,000 towers digitized with AI automation"; related list prices OpenTower Designer from $4,477 and Mount Analysis from $1,511; iQ itself is request-based enterprise pricing ([Bentley](https://www.bentley.com/software/opentower-iq/)). Sept 24, 2025 blog reiterates AI detection/classification without metrics ([Bentley blog](https://www.bentley.com/blog/software/know-your-tower/)).
- A widely repeated claim that manual inspection costs ~$5,700/tower/yr vs ~$2,200 with OpenTower iQ appeared in search snippets; the cited Bentley page now returns 404 - **unverified**.
- **Weaknesses:** Engineering/capacity focus (mounts, azimuth, loading), not corrosion/damage grading; enterprise pricing; Bentley ecosystem lock-in.

#### Pix4D - PIX4Dinspect + PIX4Dscan
- Cloud inspection platform with semi-automatic cell-tower flight plans, automatic antenna recognition, measurements, asset inventory; IVADRONES case: 50 towers, ~40 minutes capture per tower (Jan 17, 2022) ([Pix4D](https://www.pix4d.com/blog/telecom-inspection-scalability)); "60% faster transmission tower inspections" claim **(Pix4D blog snippet)**. Pricing page lists PIX4Dmatic from $125/mo, PIX4Dmapper from $333/mo; PIX4Dinspect pricing not published ([Pix4D pricing](https://www.pix4d.com/pricing)).

#### Optelos, Zeitview, Cyberhawk - see B above (all offer telecom).

#### Market structure and standards
- US towers: 142,100 cell towers (>50 ft), 209,500 macrocell sites, 452,200 outdoor small-cell nodes at end-2022 (WIA/iGR) ([Light Reading](https://www.lightreading.com/digital-transformation/us-cell-towers-and-small-cells-by-the-numbers)); ~185,000 towers in 2026 per one industry blog **(snippet, Steel in the Air)**. Major owners: American Tower, Crown Castle, SBA (counts not retrieved).
- ANSI/TIA-222: condition assessments at least every 3 years (guyed) and 5 years (self-supporting), annually in coastal/corrosive settings, plus after severe weather; quarterly lighting/alarm checks ([JOUAV, updated Sept 3, 2026](https://www.jouav.com/blog/drone-tower-inspection.html); [PCI Tower FAQ](https://pcitower.com/tower-inspection-faq/)).
- Costs: climber inspection "up to $4,000+" vs drone "$600-4,000" per tower; 1.5-3.5 hours on site plus 8-12 hours processing for 3D deliverables; pilot covers 3-5 towers/day vs 1-2 for climb crews ([JOUAV](https://www.jouav.com/blog/drone-tower-inspection.html)). Another snippet cites $2,500-$5,000 per climb and $65-85/hr crews **(snippet, unverified)**.

### E. Generic drone-data platforms
- **DroneDeploy:** Individual ~$329/seat/month, Business ~$499, Advanced $649 (billed annually; Advanced adds AI analytics, thermal, GCPs) **(snippets: SkyeBrowse, checkthat.ai)**; Capterra lists Individual $329 and Advanced $599 with "vertical facade inspection, radiometric thermal" in Advanced, Teams/Enterprise quote-only ([Capterra](https://www.capterra.com/p/197016/DroneDeploy/pricing/)). Note the per-month vs per-year ambiguity across sources. Construction-centric; inspection AI is generic.
- **Pix4D:** see D.
- **iFactory (ifactoryapp.com):** publishes "2025 buyer's guide" comparison pages claiming purpose-built AI licenses of "$40K-$120K annually" and ">95% true-positive precision"; this is the vendor's own marketing (Apr 17, 2026) and should not be cited as market data ([iFactory](https://ifactoryapp.com/industries/infrastructure-management/ai-infrastructure-inspection-platform-comparison-2025)).

### F. State DOT drone programs
- **MnDOT (with Collins Engineers):** Phase 1 (2015, Aeryon SkyRanger, 4 bridges), Phase 2 (2016-17, senseFly albris, incl. Blatnik Bridge), Phase 3 (2017-18, confined spaces with albris + Elios, ~20-25 bridges). Blatnik: conventional would need "four snoopers, an 80-foot lift and eight days ... about $59,000" vs a "five-day, $20,000" UAS project (~66% saving) ([MnDOT research](https://mntransportationresearch.org/tag/drone/)); Inside Unmanned Systems (Mar 7, 2023) repeats "up to 66%" and notes a state snooper truck cost "$950,000" ([IUS](https://insideunmannedsystems.com/no-bridge-too-far-drones-find-a-niche-in-bridge-inspections/)). Skydio-era results: 30% cost, 50% time ([Skydio](https://www.skydio.com/customer-stories/collins-engineers-inc)).
- **NCDOT:** 13,500 bridges; drones since 2016; first statewide BVLOS bridge waiver (Oct 2020) using Skydio ([Skydio](https://www.skydio.com/blog/ncdot-bvlos-waiver-for-bridge-inspection-skydio-2), [NC A&T](https://www.ncat.edu/news/2021/09/ncdot-industry-uav-bridge-inspection.php)).
- **TxDOT:** Skydio X10 on Pecos River High Bridge; "57,000 bridges" statewide ([Skydio](https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections)).
- **Nevada DOT (via Stantec):** I-80 bridges; 10 to 5 days; 50% cost saving ([Skydio](https://www.skydio.com/customer-stories/stantec-transforms-infrastructure-inspections-with-autonomous-drones)).
- **Caltrans:** UAS governed by Division of Aeronautics; encroachment permit needed inside state right-of-way; UAS handbook Oct 2021; official page does not list bridge inspection as a use case ([Caltrans UAS](https://dot.ca.gov/programs/aeronautics/unmanned-aircraft-systems)); Skydio says Caltrans tracks 2,200+ construction projects with drones **(Skydio story title)**; DRISI research Task 4419 on autonomous drone bridge inspection completed 2025 (content not extractable).
- **Pattern:** DOTs buy drones (mostly Skydio) and consulting engineers (Collins, Stantec, WSP) do the inspection; defect identification remains manual on the 3D model or in the field. **Inference:** consulting engineers are the natural first buyer of a grading/report layer.

### G. Regulatory context driving demand

#### Bridges - NBIS (23 CFR 650 Subpart C) and SNBI
- Routine inspections: Method 1 - "not to exceed 24 months"; bridges with a condition rating of 3 or less "not to exceed 12 months"; qualifying bridges "not to exceed 48 months". Method 2 - rigorous risk assessment into 12/24/48/72-month categories with Risk Assessment Panel and FHWA submission; a service inspection is required midway when the interval exceeds 48 months. Underwater: 60 months regular, 24 reduced, 72 extended. NSTM: 24/12/48 ([LII 23 CFR 650.311](https://www.law.cornell.edu/cfr/text/23/650.311)).
- NBIS final rule published May 6, 2022; effective June 2022 ([FHWA NBIS](https://www.fhwa.dot.gov/bridge/nbis.cfm), [AssetIntel](https://www.assetintel.co/blogs/the-fhwa-metrics-guide-meeting-nbis-standards-today-and-snbi-tomorrow)).
- SNBI transition: Jan 1, 2026 last date to begin verification/collection of SNBI data; first SNBI-based NBI submittal March 2026; transition tool sunsets June 2026; 100% populated and verified SNBI data by March 2028 (non-compliance after Mar 15, 2028) ([AssetIntel](https://www.assetintel.co/blogs/the-fhwa-metrics-guide-meeting-nbis-standards-today-and-snbi-tomorrow); FHWA memo PDF [here](https://www.fhwa.dot.gov/bridge/pubs/Memo-Implementation_Specifications_National_Bridge_Inventory_FINAL.pdf) - image PDF, dates taken from snippets). FHWA SNBI page last updated validation logic 09/16/2026 ([FHWA SNBI](https://www.fhwa.dot.gov/bridge/snbi.cfm)).
- Element-level: AASHTO Manual for Bridge Element Inspection distributes each element's quantity across four condition states (Good/Fair/Poor/Severe = CS1-CS4); required under SNBI **(snippet; MBEI itself paywalled)**.
- Scale: 623,218 US bridges; 44.1% good, 49.1% fair, 6.8% poor (~42,360 poor); 63,085 load-posted; 221,791 need repair/replacement; $373B ten-year gap; IIJA Bridge Formula Program $27.5B and Bridge Investment Program $12.5B over 5 years ([ASCE 2025](https://infrastructurereportcard.org/cat-item/bridges-infrastructure/)).

#### Utilities - CPUC GO 165 and Wildfire Mitigation Plans (California)
- GO 165 requires inspections "in no case" less frequent than the appendix table; records must include circuit/equipment, inspector, date, problems, condition ratings for detailed/intrusive inspections; annual report due July 1 ([CPUC GO 165 IV](https://ia.cpuc.ca.gov/gos/OriginalGO165/GO_165(IV).html)). Table values (from snippets of the GO 165 PDF; PDF not text-extractable): patrols annually in urban areas and Southern California high-fire-threat areas, every 2 years rural; detailed inspections every 3-5 years by equipment type; intrusive wood-pole inspections at 10 years then every 20 years **(snippet)** ([GO 165 PDF](https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M078/K606/78606034.PDF)).
- **PG&E 2026-2028 WMP (Apr 8, 2025):** 220,000 poles aerially inspected in 2024-25; aerial span (mid-span) inspections to be piloted 2026-28; 1,077 miles undergrounding; 570-700+ miles overhead hardening; 10,000+ Gridscope sensors on 900 circuit miles; AI used for wildfire cameras and weather (not stated for inspection imagery) ([PG&E](https://www.pge.com/en/newsroom/currents/safety/three-year-wildfire-mitigation-plan-builds-upon-proven-layers-of.html), [Renewable Energy World](https://www.renewableenergyworld.com/power-grid/outage-management/1000-miles-of-undergrounding-drones-and-more-pge-goes-all-in-on-wildfire-mitigation/)).
- **SCE:** "more than 200,000 annual inspections" in high-fire-risk areas; 400,000+ poles/transformers/lines; aerial mix shifted to 75% drones / 25% helicopters; ~800 Priority-1 repairs in a year; >10,000 structures/week at peak; AI/ML flags cross-arm deterioration and blurry photos (Aug 12, 2021) ([Energized by Edison](https://energized.edison.com/stories/drones-and-ai-future-is-now-for-sces-aerial-inspections)); LandingAI describes SCE computer vision for cross-arms, transformers and thermal anomalies (Oct 11, 2024) ([LandingAI](https://landing.ai/blog/southern-california-edisons-use-of-computer-vision-and-aerial-inspections)); SCE site: "AI-enabled inspections" under development; ~200 AI wildfire cameras; ~2,000 weather stations ([SCE](https://www.sce.com/outages-safety/wildfire-safety/wildfire-mitigation-efforts/advanced-technology)).
- **SDG&E:** ~6,500 drone inspections planned in the 2026-28 WMP cycle; "intelligent image processing (IIP)" plus probability-of-failure/ignition modelling to select structures (May 24, 2025 workshop) ([Citizen Portal summary](https://citizenportal.ai/articles/6228246/california/executive/other-state-agencies/office-of-energy-infrastructure-safety/sdge-presents-expanded-drone-inspections-earlyfault-detection-and-a-tcc-effort-to-limit-psps-scope)).
- **Inference:** California IOUs already run in-house/bespoke CV (SCE with LandingAI; SDG&E IIP); they are reference customers, not first customers, for a startup. Smaller utilities, co-ops and munis outside California (which still face NESC/state PUC pole cycles) are more accessible.
- US utility pole count and per-pole inspection cost: **not found** (search budget exhausted).

#### Telecom - ANSI/TIA-222: see D.

#### FAA - Part 107 and Part 108
- Part 108 NPRM published Aug 7, 2025; comments closed Oct 6, 2025 (~3,100); limited reopening Jan 28, 2026 on right-of-way and electronic conspicuity; final rule to OIRA July 10, 2026; still pending mid/late Sept 2026; FAA hopes to publish by end-2026, implementation roughly a year later. Two tiers: Operating Permit (lower risk, incl. rural infrastructure inspection) and Operating Certificate (higher risk, over people, SMS). Until then routine BVLOS requires a Part 107 waiver ([Airdata](https://airdata.com/blog/2026/part-108), [Flight Brief, Sept 2026](https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026), [Drone Authority](https://droneauthority.org/laws/part-108)). Existing nationwide/statewide waivers: Percepto (2023), NCDOT with Skydio (2020), American Robotics (2025).

### H. LLM / VLM in inspection: research and products (2025-2026)
- **arXiv 2605.26533 (May 26, 2026), Malikussaid & Gohar:** "Eyes" (YOLO26-x-obb detector) -> "Bridge" (deterministic spatial tokens) -> "Brain" (4-bit Qwen-2.5-1.5B + QLoRA) generating structured JSON wind-blade reports. Hallucination rate 4% vs 65% for a zero-shot VLM; expert score 8.6/10 vs 3.3; BLEU-4 0.41 vs 0.07; beat a 671B generalist API model; 47 tok/s on a single T4; trained on 947 synthetic reports ([arXiv](https://arxiv.org/abs/2605.26533)). Directly validates a gate-then-grade architecture and warns against naive VLM grading.
- **Deployment pattern:** keep a CNN gate as the real-time filter and invoke the VLM only on flagged crops on a GPU service **(iFactory VLM page, vendor marketing)**.
- **Products:** Datagrid agents (document/audit, Dec 2025); Voliro "AI-powered diagnostics" on roadmap (Jun 2025); no incumbent page fetched (Buzz, Sharper, Hepta, Optelos, Bentley, Skydio, Zeitview, Cyberhawk) mentions LLM/VLM narrative report generation or standards-cited grading as a shipped feature. **Inference:** the incumbents' moat is data + utility relationships, not the language layer.

### I. Contradictions and skepticism
- Bridge drone savings range from 30% (Skydio/Collins) to 40% (older MnDOT synthesis, snippet) to 66% (Blatnik single case) to "as much as 75%" (Skydio marketing). Use the sourced 30% and the $59k-vs-$20k example, not the 75%.
- Drone inspection is ~"1% of the market" per Dynamic Infrastructure's CEO (2021) vs Skydio's 49/50 DOT adoption (2026); both can be true: agencies own drones but most inspection imagery is still handheld.
- Accuracy claims (Sharper ">95%", Buzz "90%+", Hepta 95% precision on one class) are vendor-stated, without public datasets. A Virginia Transportation Research Council (Dec 2025) study reportedly found no agreement among four NDE consultants surveying the same decks **(snippet via iFactory; primary not retrieved)** - inter-rater variability is a real risk for any AI grader's ground truth.
- DroneDeploy Individual: $329/month (multiple reviews) vs "$329/year" (Capterra summary) - likely a per-month figure billed annually.
- Bentley per-tower cost claim ($5,700 vs $2,200) circulates but the source page is gone.
- iFactory "buyer's guides" are self-promotional and should not be cited as market data.

### J. White-space analysis for a new entrant

| Gap | Evidence | Who is closest | Our angle |
|---|---|---|---|
| Standards-cited grading (AASHTO MBEI CS1-4, GO 165 condition ratings, TIA-222 checklist) with clause citations | No vendor page shows element-level CS outputs; Datagrid only validates paperwork; SNBI deadline Mar 2028 | Datagrid, Dynamic Infrastructure (unverified), Mind Foundry (UK grades) | Heavy VLM constrained to a per-standard JSON schema; every finding cites the rule text; human sign-off workflow satisfies NBIS |
| Auditable narrative reports with evidence crops and hallucination metrics | arXiv 2605.26533 shows 4% vs 65% hallucination gap; incumbents ship dashboards, not reports | none shipped | Publish our own hallucination/expert-score eval on a public dataset; "report in minutes" for consulting engineers |
| Capture-agnostic ingestion (phone, legacy PDFs, any drone, thermal, radiographs) | Dynamic Infrastructure: drones <1% of market; Noteworthy uses truck cameras; Hepta ingests ground patrol photos | Hepta, Dynamic Infrastructure | Cheap small-VLM gate lets us accept messy, mixed-source imagery at low cost |
| Cross-asset platform (bridge + pole + tower + solar + wind) | Vendors are single-vertical (Buzz/Sharper utilities; Bentley/Pix4D telecom; Mind Foundry bridges); Zeitview is multi-sector but services-heavy | Zeitview, Cyberhawk | One grading engine with pluggable standard packs; sell to consulting engineers and DSPs who serve multiple asset owners |
| Transparent per-asset pricing for the long tail | All analytics vendors quote-only; hardware and DroneDeploy are transparent; drone tower inspection $600-4,000 | none | Per-asset/per-report pricing (e.g., tens of dollars per tower or pole, hundreds per bridge) - **Inference**, to be validated |
| Disaster/storm triage mode | Noteworthy "50x faster" storm assessment; WMP and PSPS pressures; Prompt D explicitly values recovery prioritization | Noteworthy AI, Buzz | Same gate-then-grade pipeline re-ranked by consequence (traffic, customers served) |
| Post-Part-108 BVLOS volume | Rule expected late 2026/2027; capture volume will outpace human review | Percepto, Skydio (capture) | Be the review layer their APIs push to (Skydio Extend, Percepto AIM, DroneDeploy) |

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| Skydio Series F / valuation | $110M; $4.4B | https://www.skydio.com/blog/skydio-series-f | 2026-04-23 |
| Skydio Series E | $230M | https://www.skydio.com/blog/skydio-raises-230-million-series-e-funding-round | 2023 |
| Skydio X10 unit price | $16k-$25k (public safety); ~$15k standalone | https://dronexl.co/drone-companies/skydio/skydio-x10/ | 2026 |
| Skydio X10 price (independent) | $14k-$22k | https://reliamag.com/guides/best-drones-industrial-inspection-2026/ | 2026-03 |
| Skydio 3D Scan license | $2,999/yr | https://www.capterra.com/p/238131/Skydio-3D-Scan/ | 2026 |
| 3D Scan requires AEF license | $3,000 + $1,500 = $4,500/yr per drone | https://skydiopilots.com/threads/3-d-scan-is-more-expensive-than-anyone-is-reporting.870/ | 2021-06-26 |
| State DOTs using Skydio | 49 of 50 (vendor) | https://www.skydio.com/solutions/bridge-inspection | 2026 |
| MnDOT/Collins savings with Skydio | 30% cost; ~50% field time; 70-80% defects found on twin | https://www.skydio.com/customer-stories/collins-engineers-inc | n.d. |
| MnDOT Blatnik Bridge UAS vs conventional | $20,000 / 5 days vs ~$59,000 / 8 days | https://mntransportationresearch.org/tag/drone/ | 2017-18 |
| Snooper truck purchase cost | $950,000 | https://insideunmannedsystems.com/no-bridge-too-far-drones-find-a-niche-in-bridge-inspections/ | 2023-03-07 |
| NDOT/Stantec I-80 | 10 days -> 5 days; 50% cost saving | https://www.skydio.com/customer-stories/stantec-transforms-infrastructure-inspections-with-autonomous-drones | n.d. |
| NCDOT bridges | 13,500; research award >$300k | https://www.ncat.edu/news/2021/09/ncdot-industry-uav-bridge-inspection.php | 2021-09-13 |
| Texas NBI bridges | 57,000 | https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections | n.d. |
| Elios 3 complete system | $40k-$55k | https://reliamag.com/guides/best-drones-industrial-inspection-2026/ | 2026-03 |
| Voliro funding / traction | $23M total; 40+ customers; 17 countries; 100+ contact inspections/mo | https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ | 2025-06-16 |
| Percepto Series C / total | $67M; >$139M | https://www.facilitiesdive.com/news/percepto-drone-raises-67M-gets-faa-waiver/652827/ | 2023-06-13 |
| Percepto utility launch; FPL | "hundreds of drones" planned | https://www.renewableenergyworld.com/power-grid/grid-modernization/autonomous-drone-company-releases-end-to-end-ai-powered-remote-inspection-solution-at-distributech/ | 2025-03-26 |
| Buzz Solutions Series A / total | $20M; $30M total; revenue +400% | https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/ | 2026-08-04 |
| Buzz PowerAI throughput | 25,000+ images/hr; 0.6 s/image; 50+ models; "90%+ accuracy" | https://www.buzzsolutions.com/ | 2026 |
| Buzz customer scale | Dominion 47,000 towers; AEP Texas 88,000+ images/season | https://www.buzzsolutions.com/ | 2026 |
| Sharper Shape Asset Insights | 40+ components; ">95% accuracy"; 1,000 images "instantly" | https://sharpershape.com/sharper-shape-bolsters-utility-inspection-offering-with-ai-powered-asset-insights-for-automated-component-identification-and-defect-detection/ | 2024-10-08 |
| Sharper Shape Series B | $18M (snippet, unverified) | https://tracxn.com/d/companies/sharpershape/__Hwjsvmsi1pLPNEfAARltmWACrU5mrqKDOep7MKqvCnM | 2022-05 |
| Hepta traction | 30+ DSO/TSOs; 21 countries; >3,000 km/month; avg EUR 3M/yr savings | https://heptainsights.com/ | 2026 |
| Hepta cross-arm model | 95% precision; F >94%; >10,000 training images | https://heptainsights.com/latest-ai-models-added-to-heptas-power-line-inspection-platform-ubird/ | 2022-05-17 |
| Hepta seed | EUR 2M | https://www.tehnopol.ee/en/hepta-airborne-raises-e2m-to-digitize-energy-infrastructure-and-automate-inspection/ | 2021-02-03 |
| Zeitview round / scale | $60M; 200,000+ assets in 2024; 80 countries | https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ | 2025-03-07 |
| Cyberhawk scale | 500k+ inspections; 300+ customers; 40 countries | https://thecyberhawk.com/ | 2026 |
| Noteworthy AI claims | 10% of poles evaluated annually; up to 75% O&M cut; 50x faster storm assessment | https://www.noteworthy.ai/ | 2026 |
| Optelos telecom case | 5 days -> 2.4 days onsite; 52% labor saving per 5G upgrade | https://optelos.com/telecom/cell-tower-inspection-audits/ | n.d. |
| Infravision Series B | $91M (construction, not inspection) | https://dronelife.com/2025/11/04/infravision-secures-91-million-to-scale-drone-powered-grid-infrastructure/ | 2025-11-04 |
| Bentley OpenTower iQ | 25,000 towers digitized; tower visits -50%; Designer from $4,477; Mount Analysis from $1,511 | https://www.bentley.com/software/opentower-iq/ | 2026 |
| OpenTower iQ launch | co-venture, digital twin, AI component detection | https://www.digitalengineering247.com/article/bentley-acceleration-initiatives-launchesopentower-iq | 2021-03-25 |
| Pix4Dinspect telecom case | 50 towers; ~40 min capture/tower | https://www.pix4d.com/blog/telecom-inspection-scalability | 2022-01-17 |
| Pix4D list prices | PIX4Dmatic from $125/mo; PIX4Dmapper from $333/mo | https://www.pix4d.com/pricing | 2026 |
| DroneDeploy plans | Individual $329, Advanced $599-649, Teams/Enterprise quote | https://www.capterra.com/p/197016/DroneDeploy/pricing/ | 2026 |
| US cell towers / macro sites / small cells | 142,100 / 209,500 / 452,200 (end-2022, WIA) | https://www.lightreading.com/digital-transformation/us-cell-towers-and-small-cells-by-the-numbers | 2023 |
| Tower inspection cost | climb "up to $4,000+"; drone $600-4,000; 3-5 towers/day by drone | https://www.jouav.com/blog/drone-tower-inspection.html | 2026-09-03 |
| TIA-222 intervals | 3 yr guyed; 5 yr self-supporting; annual coastal | https://www.jouav.com/blog/drone-tower-inspection.html | 2026-09-03 |
| NBIS routine intervals | <=24 mo; <=12 mo if rating <=3; <=48 extended; <=72 Method 2 | https://www.law.cornell.edu/cfr/text/23/650.311 | current |
| NBIS underwater / NSTM | 60/24/72 mo; 24/12/48 mo | https://www.law.cornell.edu/cfr/text/23/650.311 | current |
| NBIS final rule | published 2022-05-06 | https://www.fhwa.dot.gov/bridge/nbis.cfm | 2022 |
| SNBI milestones | first SNBI submittal Mar 2026; full compliance Mar 2028 | https://www.assetintel.co/blogs/the-fhwa-metrics-guide-meeting-nbis-standards-today-and-snbi-tomorrow | 2025-08-07 |
| US bridges / condition | 623,218; 6.8% poor (~42,360); 49.1% fair | https://infrastructurereportcard.org/cat-item/bridges-infrastructure/ | 2025 |
| Bridge funding gap | $373B over 10 yrs; IIJA BFP $27.5B; BIP $12.5B | https://infrastructurereportcard.org/cat-item/bridges-infrastructure/ | 2025 |
| PG&E aerial pole inspections | 220,000 poles (2024-25); 1,077 mi undergrounding; 10,000+ Gridscope | https://www.pge.com/en/newsroom/currents/safety/three-year-wildfire-mitigation-plan-builds-upon-proven-layers-of.html | 2025-04-08 |
| SCE HFRA inspections | 200,000+/yr; 400,000+ assets; 75% drone / 25% heli; ~800 P1 repairs/yr | https://energized.edison.com/stories/drones-and-ai-future-is-now-for-sces-aerial-inspections | 2021-08-12 |
| SDG&E drone inspections | ~6,500 per WMP cycle | https://citizenportal.ai/articles/6228246/california/executive/other-state-agencies/office-of-energy-infrastructure-safety/sdge-presents-expanded-drone-inspections-earlyfault-detection-and-a-tcc-effort-to-limit-psps-scope | 2025-05-24 |
| GO 165 cycles | patrol 1 yr urban / 2 yr rural; detailed 3-5 yr; intrusive 10 then 20 yr (snippet) | https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M078/K606/78606034.PDF | 2013 |
| Part 108 timeline | NPRM 2025-08-07; ~3,100 comments; OIRA 2025-07-10 receipt; pending Sept 2026 | https://airdata.com/blog/2026/part-108 | 2026-07-20 |
| Part 108 status | at OIRA; FAA targets end-2026 | https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026 | 2026-09 |
| Hybrid VLM report generation | 4% hallucination vs 65% zero-shot; 8.6 vs 3.3 expert score; 47 tok/s on T4 | https://arxiv.org/abs/2605.26533 | 2026-05-26 |
| Mind Foundry / WSP pilot | 48% lifecycle cost; 50% reporting time; 30% inspection time | https://www.mindfoundry.ai/resources/case-study/wsp-windward-inspect | 2024-12 pilot |
| Dynamic Infrastructure | founded 2017; drones "<1% of the market" | https://www.calcalistech.com/ctech/articles/0,7340,L-3889391,00.html | 2021-01-25 |
| Gecko Robotics Navy deal | $71M | https://www.geckorobotics.com/ | 2026-03 |

---

## Implications for our product / edge

1. **Do not build a drone or compete on capture.** Skydio ($4.4B), Percepto, Flyability, Voliro own it and are increasingly API-open (Skydio Extend, Percepto AIM integrations). Position as the grading-and-report layer any capture source pushes into: Skydio Cloud exports, DroneDeploy/Pix4D outputs, phone photos, helicopter stills, legacy PDF reports, thermal and radiographs.
2. **Make standards the product.** Nobody found ships element-level AASHTO MBEI condition-state outputs with quoted clauses, GO 165 condition ratings, or TIA-222 checklist scoring from imagery. The heavy VLM should be constrained by a per-standard JSON schema and cite the clause text next to every finding. Export SNBI-ready fields (Datagrid does this for documents; we do it from pixels). Keep a mandatory human sign-off step; NBIS requires qualified personnel, and every credible vendor says "assist, not replace".
3. **Adopt the validated architecture and publish the metric.** arXiv 2605.26533 shows detector/small-model gate + constrained small LLM beats zero-shot VLMs by ~16x on hallucination. Our small-VLM gate ("damage present?") mirrors this; the heavy VLM must be grounded on detector crops and schema-constrained. Report our own hallucination rate and expert agreement on a public set (e.g., SDNET, CODEBRIM, a public insulator dataset) - it is a differentiator judges can verify and rules-compliant (no fabricated performance).
4. **Wedge customers:** consulting engineering firms that perform DOT inspections (Collins, Stantec, WSP-type firms), drone service providers (FlyGuys, Soaring Eagle-type DSPs currently using Optelos/Sharper), county/municipal bridge owners facing the March 2028 SNBI deadline, and co-ops/munis outside California with NESC/PUC pole cycles. California IOUs and Tier-1 telcos already have in-house CV; treat as later reference accounts.
5. **Pricing edge:** all analytics incumbents are quote-only; hardware is transparent. A published per-asset price (**Inference:** tens of dollars per pole/tower report, low hundreds per bridge element set) fits under the $600-4,000 drone-tower and $20k-59k bridge job costs, and lets DSPs resell it.
6. **Disaster mode is a feature, not a pivot.** Same pipeline, re-ranked by consequence (ADT, customers served, HFTD tier). Noteworthy's "50x faster storm assessment" and SDG&E/PG&E PSPS pressure show buyers value speed of triage after events - exactly Prompt D's second half.
7. **Regulatory timing works for us.** SNBI full compliance (Mar 2028) and Part 108 (late 2026/2027) both increase data volume and reporting burden within the next 18 months.
8. **Avoid the incumbents' credibility traps:** unqualified "95% accuracy" numbers, unverifiable per-tower savings, and marketing "buyer's guides". Show precision/recall per defect class, dataset, and an inter-rater caveat (VTRC-style variability).

---

## Open questions / gaps

- Dynamic Infrastructure: funding, pricing, current status (both domains unreachable on 2026-09-24), and whether its AASHTO defect mapping is element-level - Global Highways article returned 403.
- Exact CPUC GO 165 appendix table values (only snippet-level; PDF is image-only). Also NESC / other state PUC pole inspection cycles outside California.
- US utility pole count and cost per pole inspection - **not found** (WebSearch budget exhausted).
- Bentley's per-tower cost claim ($5,700 vs $2,200) - source page 404; Bentley OpenTower iQ pricing.
- Per-asset analytics pricing for Buzz, Sharper Shape, Optelos, Hepta, Zeitview, Cyberhawk - none disclosed.
- Has any incumbent shipped LLM/VLM report generation? None found on fetched pages; check Buzz, Zeitview and Optelos release notes and DTECH 2026 talks (FirstEnergy session page 404).
- Caltrans Task 4419 results (image-only PDFs) and Caltrans' drone/AI vendors.
- Tower owner (American Tower, Crown Castle, SBA) inspection practices and vendors; number of towers each owns.
- Primary source for the Virginia Transportation Research Council Dec 2025 NDE reliability study.
- Gecko Robotics funding/valuation (not verified this session); "Exponent" turned out to be an engineering consulting firm ($166.3M Q1 2026 revenue, snippet), not an inspection-AI startup; "Aren" not found.
- Sharper Shape Series B ($18M, May 2022) needs a primary source.
- Public defect datasets suitable for our eval (bridges: SDNET2018, CODEBRIM; powerlines: insulator datasets; towers: none found) - to be covered by the dataset research angle.

---

## Sources

1. https://www.skydio.com/blog/skydio-series-f - Skydio Series F ($110M, $4.4B), Apr 23, 2026.
2. https://dronelife.com/2026/04/28/skydio-series-f-110m-funding-us-manufacturing/ - DroneLife on Skydio Series F.
3. https://www.skydio.com/blog/skydio-raises-230-million-series-e-funding-round - Skydio Series E ($230M).
4. https://dronexl.co/drone-companies/skydio/skydio-x10/ - Skydio X10 pricing and deployments (2026).
5. https://reliamag.com/guides/best-drones-industrial-inspection-2026/ - Independent 2026 pricing for Elios 3, X10, Voliro T, DJI M350.
6. https://www.capterra.com/p/238131/Skydio-3D-Scan/ - Skydio 3D Scan $2,999/yr listing.
7. https://skydiopilots.com/threads/3-d-scan-is-more-expensive-than-anyone-is-reporting.870/ - Forum: 3D Scan requires AEF license (2021).
8. https://www.skydio.com/solutions/bridge-inspection - Skydio bridge page (49/50 DOTs, savings claims).
9. https://www.skydio.com/software/asset-command - Skydio Asset Command features.
10. https://www.skydio.com/customer-stories/collins-engineers-inc - MnDOT/Collins results.
11. https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections - TxDOT story.
12. https://www.skydio.com/customer-stories/stantec-transforms-infrastructure-inspections-with-autonomous-drones - NDOT/Stantec story.
13. https://www.skydio.com/blog/ncdot-bvlos-waiver-for-bridge-inspection-skydio-2 - NCDOT BVLOS waiver.
14. https://mntransportationresearch.org/tag/drone/ - MnDOT drone research phases and Blatnik costs.
15. https://insideunmannedsystems.com/no-bridge-too-far-drones-find-a-niche-in-bridge-inspections/ - Drones in bridge inspection, snooper cost (2023).
16. https://www.ncat.edu/news/2021/09/ncdot-industry-uav-bridge-inspection.php - NC A&T / NCDOT program.
17. https://dot.ca.gov/programs/aeronautics/unmanned-aircraft-systems - Caltrans UAS program page.
18. https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-notes/task4419-rns-05-25-a11y.pdf - Caltrans Task 4419 research note (image PDF).
19. https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-results/task4419-rrs-11-25-a11y.pdf - Caltrans Task 4419 results (image PDF).
20. https://www.flyability.com/elios-3-price - Flyability Elios 3 package page.
21. https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ - Voliro $23M.
22. https://percepto.co/percepto-launches-ai-powered-solution-for-electric-utilities/ - Percepto utility launch (Mar 2025).
23. https://www.renewableenergyworld.com/power-grid/grid-modernization/autonomous-drone-company-releases-end-to-end-ai-powered-remote-inspection-solution-at-distributech/ - Percepto/FPL.
24. https://www.facilitiesdive.com/news/percepto-drone-raises-67M-gets-faa-waiver/652827/ - Percepto Series C.
25. https://ir.ondas.com/press-releases/detail/187/ondas-american-robotics-secures-its-latest-faa-bvlos - American Robotics BVLOS waiver (Jan 2025).
26. https://dronelife.com/2025/11/04/infravision-secures-91-million-to-scale-drone-powered-grid-infrastructure/ - Infravision $91M.
27. https://www.geckorobotics.com/ - Gecko Robotics overview.
28. https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/ - Buzz Solutions Series A (Aug 2026).
29. https://www.buzzsolutions.com/ - Buzz Solutions product claims.
30. https://sharpershape.com/sharper-shape-bolsters-utility-inspection-offering-with-ai-powered-asset-insights-for-automated-component-identification-and-defect-detection/ - Sharper Shape Asset Insights.
31. https://dronelife.com/2024/10/09/sharper-shape-introduces-ai-powered-asset-insights-for-utility-inspections/ - DroneLife on Asset Insights.
32. https://tracxn.com/d/companies/sharpershape/__Hwjsvmsi1pLPNEfAARltmWACrU5mrqKDOep7MKqvCnM - Sharper Shape funding profile (snippet only).
33. https://heptainsights.com/ - Hepta Insights claims.
34. https://heptainsights.com/latest-ai-models-added-to-heptas-power-line-inspection-platform-ubird/ - Hepta cross-arm models (2022).
35. https://www.tehnopol.ee/en/hepta-airborne-raises-e2m-to-digitize-energy-infrastructure-and-automate-inspection/ - Hepta EUR 2M (2021).
36. https://optelos.com/utilities-inspections/ - Optelos utilities.
37. https://optelos.com/telecom/cell-tower-inspection-audits/ - Optelos telecom.
38. https://optelos.com/digitally-transform-cell-tower-inspection/ - Optelos + OpenTower iQ (Sept 2023).
39. https://www.softwaresuggest.com/optelos - Optelos pricing (custom).
40. https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ - Zeitview $60M.
41. https://www.businesswire.com/news/home/20250304009141/en/Zeitview-Secures-$60M-to-Advance-AI-Powered-Inspections-of-Global-Critical-Infrastructure - Zeitview press release.
42. https://thecyberhawk.com/ - Cyberhawk overview.
43. https://www.noteworthy.ai/ - Noteworthy AI overview.
44. https://www.assetvision.com.au/2026/05/28/ai-condition-monitoring/ - Asset Vision AI condition monitoring.
45. https://www.calcalistech.com/ctech/articles/0,7340,L-3889391,00.html - Dynamic Infrastructure profile (Jan 2021).
46. https://globalhighways.com/faster-aashto-bridge-defect-detection-dynamic-infrastructures-ai-platform - Dynamic Infrastructure AASHTO article (403, not read).
47. https://www.mindfoundry.ai/resources/case-study/wsp-windward-inspect - Mind Foundry / WSP case study.
48. https://datagrid.com/blog/ai-agent-identifies-cracks-deterioration-bridge-deck-photos - Datagrid AI agents for bridge inspection.
49. https://www.assetintel.co/blogs/the-fhwa-metrics-guide-meeting-nbis-standards-today-and-snbi-tomorrow - AssetIntel NBIS/SNBI guide (Aug 2025).
50. https://cee.umd.edu/news/story/affordable-bridge-inspection-with-ai - UMD bridge AI (Oct 2025).
51. https://doi.org/10.3390/s23094192 - Machine-aided bridge deck crack condition state assessment (Sensors 2023).
52. https://www.bentley.com/software/opentower-iq/ - OpenTower iQ product page.
53. https://www.digitalengineering247.com/article/bentley-acceleration-initiatives-launchesopentower-iq - OpenTower iQ launch (Mar 2021).
54. https://www.bentley.com/blog/software/know-your-tower/ - Bentley telecom blog (Sept 2025).
55. https://www.pix4d.com/blog/telecom-inspection-scalability - PIX4Dinspect telecom case (Jan 2022).
56. https://www.pix4d.com/pricing - Pix4D pricing.
57. https://www.capterra.com/p/197016/DroneDeploy/pricing/ - DroneDeploy pricing.
58. https://ifactoryapp.com/industries/infrastructure-management/ai-infrastructure-inspection-platform-comparison-2025 - iFactory vendor comparison (marketing).
59. https://www.lightreading.com/digital-transformation/us-cell-towers-and-small-cells-by-the-numbers - WIA tower counts.
60. https://www.jouav.com/blog/drone-tower-inspection.html - Tower inspection costs, TIA-222 intervals (Sept 2026).
61. https://pcitower.com/tower-inspection-faq/ - TIA-222 inspection FAQ.
62. https://www.law.cornell.edu/cfr/text/23/650.311 - 23 CFR 650.311 inspection intervals.
63. https://www.fhwa.dot.gov/bridge/nbis.cfm - FHWA NBIS page.
64. https://www.fhwa.dot.gov/bridge/snbi.cfm - FHWA SNBI page.
65. https://www.fhwa.dot.gov/bridge/pubs/Memo-Implementation_Specifications_National_Bridge_Inventory_FINAL.pdf - FHWA SNBI implementation memo (image PDF).
66. https://infrastructurereportcard.org/cat-item/bridges-infrastructure/ - ASCE 2025 bridges.
67. https://ia.cpuc.ca.gov/gos/OriginalGO165/GO_165(IV).html - CPUC GO 165 Section IV.
68. https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M078/K606/78606034.PDF - CPUC GO 165 (2013 PDF).
69. https://www.pge.com/en/newsroom/currents/safety/three-year-wildfire-mitigation-plan-builds-upon-proven-layers-of.html - PG&E 2026-28 WMP release.
70. https://www.renewableenergyworld.com/power-grid/outage-management/1000-miles-of-undergrounding-drones-and-more-pge-goes-all-in-on-wildfire-mitigation/ - PG&E WMP coverage.
71. https://energized.edison.com/stories/drones-and-ai-future-is-now-for-sces-aerial-inspections - SCE drones and AI (2021).
72. https://landing.ai/blog/southern-california-edisons-use-of-computer-vision-and-aerial-inspections - LandingAI on SCE (2024).
73. https://www.sce.com/outages-safety/wildfire-safety/wildfire-mitigation-efforts/advanced-technology - SCE advanced technology page.
74. https://citizenportal.ai/articles/6228246/california/executive/other-state-agencies/office-of-energy-infrastructure-safety/sdge-presents-expanded-drone-inspections-earlyfault-detection-and-a-tcc-effort-to-limit-psps-scope - SDG&E WMP workshop summary (May 2025).
75. https://airdata.com/blog/2026/part-108 - Part 108 explainer (Jul 2026).
76. https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026 - Part 108 status (Sept 2026).
77. https://droneauthority.org/laws/part-108 - Part 108 status page.
78. https://arxiv.org/abs/2605.26533 - Hybrid vision-language defect reasoning and report generation (May 2026).
79. https://www.thestreet.com/technology/next-big-ai-opportunity-us-physical-infrastructure-inspection-management - TheStreet on infrastructure inspection AI (403, snippet only).
80. https://www.forbes.com/sites/daraabasiita/2026/07/23/ai-tackles-a-37-trillion-infrastructure-blind-spot/ - Forbes (Jul 2026; 403, not read).
