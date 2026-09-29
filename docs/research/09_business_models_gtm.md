# Business Models & Go-to-Market for Inspection AI (Research Angle 09)

Prepared 2026-09-24 (Thu) for Origin Weekend Fall 2026, Prompt D (infrastructure damage detection & recovery prioritization).
Scope: how inspection-AI / drone-analytics companies make money and reach customers; what a student startup in LA can plausibly do in its first 100 customers; unit economics of a small-VLM -> heavy-VLM cascade.

Conventions: every number carries a source URL and date. "Inference:" marks my reasoning, not a sourced fact. "Not found" means I searched and could not source it. The web-search budget for this session was exhausted mid-task (200/200), so a few items rely on search-result snippets rather than a fetched page; those are flagged "(snippet)".

---

## Summary

- **Nobody publishes enterprise price lists.** SkySpecs, Raptor Maps, Zeitview, Buzz, Sharper Shape all sell custom enterprise contracts. The only transparent price points are at the DSP/SMB layer: Scopito (EUR 1/image expert analysis, EUR 50/building platform fee, ~$5/pole at scale), DroneDeploy ($329-499/seat/month), Optelos (from ~$1,000/month, snippet), SkyeBrowse ($99-199 per processed report). Service-side benchmarks: $300-600/turbine drone visual inspection, $100-300/turbine analytics add-on, $300-500/MW solar thermal survey, ~$313/pole implied by SCE's $50M / 160k-pole contract.
- **The market is bifurcating**: (a) big utilities are bringing drone capture in-house (SCE 100+ drones; PG&E 300k+ in-house flights in 2024; Georgia Power 60% cost savings), which commoditizes DSP flying and raises demand for analytics software that in-house teams and DSPs can use; (b) incumbents that started as service companies (Zeitview) are pivoting to software.
- **Funding/traction calibration**: Buzz Solutions raised a $20M Series A on 2026-08-04 with three named utility customers (Dominion, AEP, NYPA) and 3x customer growth / 400% revenue growth since its prior round - i.e., a handful of utility logos is Series-A-grade traction. Zeitview raised $60M (Mar 2025, ~$174M total). SkySpecs $20M Series E (Mar 2025). Skydio $110M Series F at $4.4B (Apr 2026). Voliro $23M total with 40+ customers in 17 countries. Nearthlab ~$24M total with 100k+ blades inspected.
- **Utility sales cycles are gated, not judged**: safety prequalification (ISNetworld/Avetta), insurance thresholds, NDAA-compliant fleet, cybersecurity, Part 107 - fail any and "your proposal never gets read"; only then data quality, turnaround, scalability; price is evaluated last. MissionGO flew trials for SCE from 2019 before the 3-year $50M award announced Oct 2022 (Inference: ~3 years pilot-to-scale).
- **Shortcuts exist**: paid proof-of-concept programs (EPRI Incubatenergy Labs; Free Electrons with E.ON/EDP/ESB/Hydro-Quebec etc.), DOT grants that fund public agencies to buy drone inspection tech (USDOT DIIG $9M FY26, ~5 awards of $0.5-9M, notice 2026-09-15, close 2026-11-15; SMART gave Alaska DOT $12M+ for drone inspection), CEC EPIC ($130M+/yr; GFO-26-501 on wildfire-resilient grid data/modeling had its pre-application workshop 2026-09-10).
- **Inference is nearly free relative to price**: a gate on Gemini 3.1 Flash-Lite costs ~$0.26-0.40 per 1,000 images; Moondream cloud is $0.06 per 1,000 images; a heavy pass on Claude Sonnet 5 costs ~$0.01-0.02 per full-res image (half that via Batch API). A 360-image turbine costs ~$0.70-1.25 to grade with a 20%-flag cascade vs a $100-300 analytics price. Inference: gross margin on compute is >95%; real COGS are human QA, storage, support, and customer acquisition. The cascade's value is throughput/latency and enabling a self-serve free tier, more than margin at enterprise prices.
- **Best first-100 hypothesis** (consistent with two independent DSP-facing sources): sell to small/mid drone service providers and independent O&M firms who must now deliver "AI-ready, utility-grade" data but lack analytics, and to regional wind/solar owners - explicitly *not* to Tier-1 utilities first. Price per asset (turbine/pole/MW) with a self-serve upload-and-grade free tier.
- **Contradictions noted**: Zeitview pilot network is "11K+ pilots" (its own US utilities page) vs "80,000 pilots worldwide" (third-party snippet). Percepto: a "Dec 8, 2025 unattributed VC round" appears in one aggregator snippet but not in another aggregator's round list. SkySpecs' March 2025 round is described as "Series D" in one snippet and "Series E $20M" in another. Treat all aggregator figures as approximate.

---

## Detailed findings

### 1. Pricing models with public examples

#### 1a. Service-side price benchmarks (what the end customer pays today)

| Segment | Price point | Source (date) |
|---|---|---|
| Wind - standard visual drone inspection | $300-600 per turbine (US, 2025-26) | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ (2025); https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ (updated 2026-06-01) |
| Wind - broader range | $300-1,000 per turbine; "basic visual" $800-2,000; thermal/advanced $2,000-4,000+ | https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost (2025-05-05) - note internal inconsistency in that article |
| Wind - **data processing / analytics add-on** | **$100-300 per turbine** | https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost (2025-05-05) |
| Wind - rope access (incumbent) | $1,500-3,000 per turbine; 3-6 hrs/turbine vs 15-45 min by drone | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ (2025) |
| Wind - independent triangulation | $300-769 per turbine; Recon Aerial case: $76,900 for 100 turbines | https://averroes.ai/blog/wind-turbine-drone-inspection-cost-breakdown-advice (2026-05-18) |
| Wind - DSP day rate | $1,500-3,500 per day; 18-25 turbines/day | https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ (2026-06-01) |
| Wind - downtime | $3,000-17,000 per turbine per day | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ (2025) |
| Solar - thermal survey | $300-500 per MW; full diagnostic + report $500-1,200 per MW; large-site annual contract $10,000-30,000+ | https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know (2025-05-05, updated Aug) |
| Solar - alt range | $150-500 per MW (snippet) | https://www.geowgs84.com/post/how-much-does-a-drone-solar-panel-inspection-cost |
| Distribution poles - utility contract | SCE: $50M / 3 years / ~160,000 poles = ~$313 per pole (implied) | https://dronedj.com/2022/10/20/southern-california-edison-drone-inspection/ (2022-10-20) |
| Roofs (insurance/property) | Drone roof inspection $150-400 vs $300-600 traditional; +$99-199 software processing per 3D/ortho report | https://www.skyebrowse.com/news/posts/drone-roof-inspection-cost (2026-03-16) |
| Bridges | Traditional inspection $2,000-5,000 labor+equipment, 8-12 hrs, 4-person crew (snippet); MnDOT 39 bridges: savings $540-21,000 per bridge, ~40% average (snippet of MDPI 2025 paper); Nevada DOT saved $40,000 on one bridge | https://www.skyebrowse.com/news/posts/bridge-and-roadway-inspections ; https://www.mdpi.com/2412-3811/10/3/63 (2025, not fetched - 403); https://informedinfrastructure.com/90540/off-rope-drones-for-bridge-inspection-increase-safety-decrease-costs-2/ (2023-10-11) |

Inference: the analytics layer is currently priced at roughly 15-50% of the capture fee in wind ($100-300 on top of $300-600). That is the price umbrella a pure-software entrant sells under.

#### 1b. Software-side price points that are actually public

| Vendor | Model | Price | Source (date) |
|---|---|---|---|
| Scopito (Denmark; DSP-friendly) | Pay-per-asset | Buildings: EUR 50/building platform access; expert analysis EUR 1/image, min EUR 150/building; "in-house analysis" EUR 0 | https://scopito.com/building-inspection-software/ (current) |
| Scopito | Pay-per-pole | ~$5 per pole at full scale incl. storage, processing, AI analysis, presentation; 14-day free trial | http://scopito.com/supercharging-utility-inspection/ (2020, updated 2025) |
| Scopito | Pay-per-pole w/ expert | EUR 40/pole incl. analysis; expert image analysis EUR 20/pylon (snippet) | http://scopito.com/power-line-inspection-software/ |
| DroneDeploy | Per seat | $329/seat/month (Individual), $499/seat/month (Business), billed annually; Enterprise custom; no published volume discount; 2-24 h processing, no SLA | https://www.skyebrowse.com/news/posts/dronedeploy-review (2026-03-13) |
| Optelos | Subscription | "starts at $1,000/month", customizable (snippet) | https://www.softwaresuggest.com/optelos |
| Pix4Dinspect | Usage | License fee "calculated in terms of the number of inspections uploaded (Inspection Blocks)"; price list on request | https://assets.ctfassets.net/go54bjdzbrgi/1z3eFwWcqCSnHEcTpmMZM7/769ff3950fec59de073ad88224bf61b3/211008_-_Additional_Term_GTC-_PIX4Dinspect.pdf |
| Pix4D (general) | Subscription | ~$300/month | https://www.sitemark.com/research/best-solar-inspection-software/ (2026-05-26) |
| SkyeBrowse | Per report | $99 per Premium model credit; $199 Premium Advanced | https://www.skyebrowse.com/news/posts/drone-roof-inspection-cost (2026-03-16) |
| Raptor Maps | Enterprise SaaS | Custom; "depends on site count, capacity, and selected platform features"; SOC 2; no public pricing | https://apps.list.solar/tools/raptor-maps/ |
| SkySpecs | Services + SaaS | Inspection services + Horizon BAM / Horizon CMS / Horizon Solar software subscriptions; no public pricing | https://skyspecs.com/blog/offshore-wind-inspections-2025/ (2025-03-03) |
| Zeitview | Two-tier | Data Capture Service (pilot network + drone-in-a-box) + Asset Insights software; priced per inspection/per site, custom | https://www.zeitview.com/utilities ; https://www.sitemark.com/research/best-solar-inspection-software/ (2026-05-26) |
| Sitemark | Enterprise SaaS | Custom, scales with portfolio; self-reports 310+ GWp, 1,100+ companies, 100+ countries | https://www.sitemark.com/research/best-solar-inspection-software/ (2026-05-26, vendor's own page) |
| Voliro | Hardware subscription | "Voliro T Subscription" (equipment-as-a-service); 40+ customers, 17 countries, 100+ contact inspections/month | https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ (2025-06-16) |
| Moondream (VLM API) | Per image | $0.06 per 1,000 images; $5/month free credits | https://moondream.ai/ (current) |

Pricing archetypes observed: (1) per-asset (pole / building / inspection block) - Scopito, Pix4Dinspect; (2) per-seat SaaS - DroneDeploy; (3) enterprise custom per portfolio - Raptor Maps, Sitemark, SkySpecs Horizon; (4) service + software bundle - Zeitview, SkySpecs; (5) hardware-as-a-service subscription - Voliro; (6) per-report credit - SkyeBrowse.
Not found: any public per-MW analytics fee from Raptor Maps/Zeitview/Sitemark; any public per-turbine Horizon fee; any insurance-linked (claims-paid or premium-linked) pricing for inspection AI.

#### 1c. Insurance-linked models
- Zeitview's Property Insights platform produces reports "used by insurance companies, roofing contractors, and property managers to estimate repair costs and prioritize projects" (snippet) - https://blog.zeitview.com/drone-insurance-inspections-for-properties
- Drone roof inspection $150-400 vs $300-600 traditional; insurers use photogrammetry-derived measurements to reduce re-inspection and disputes - https://www.skyebrowse.com/news/posts/drone-roof-inspection-cost (2026-03-16)
- Not found: any public pricing for insurer-paid infrastructure (wind/solar/bridge) inspection AI, or parametric/warranty-linked pricing. Inference: insurance is a plausible *later* channel (claims triage after storms) but no benchmark exists to price it this weekend.

### 2. Channels

**Asset owners (direct)**
- Buzz Solutions sells PowerAI directly to utilities; named customers Dominion Energy, American Electric Power, New York Power Authority; expanding into utility-scale solar - https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/ (2026-08-04)
- SkySpecs sells to owners/IPPs (e.g., ScottishPower Renewables; EDF UK Teesside) - https://skyspecs.com/blog/offshore-wind-inspections-2025/ (2025-03-03)
- Independent positioning vs OEMs: Vestas, Siemens Gamesa and GE Vernova can bundle blade inspections with repair execution and proprietary turbine data; SkySpecs' positioning relies on OEM-agnostic aggregation across mixed fleets (snippet). The 2018 CompositesWorld article confirms OEMs (Vestas, LM, Siemens Gamesa) and independents (SkySpecs, Rope Partner, etc.) both perform inspections - https://www.compositesworld.com/articles/service-repair-optimizing-wind-powers-grid-impact- (2018-03-26)

**Drone service providers (DSPs) as channel / white-label layer**
- Sharper Shape explicitly serves "transmission and distribution line owners and operators as well as drone service providers" - https://www.cbinsights.com/company/sharper-shape-oy
- Scopito is built for pay-per-asset DSP usage (see 1b).
- 2026 DSP reality (Detect Inspections, 2026-03-31): in-house utility programs displacing contractors; docks handling routine work; BVLOS producing 10x data per mission; DJI-ban forcing NDAA fleet transitions; "AI analytics requirements redefining data quality standards"; 15-25% of delivered imagery needs remediation before AI processing; in-house utility program startup $25-50k, $10-20k/yr operating - https://detectinspections.com/blog/2026-trends-for-drone-service-providers
- Training/DSP guidance says new pilots should *not* pitch "massive utility companies" but target "independent O&M providers or smaller regional wind farm owners" - https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ (2026-06-01)

**Insurers** - see 1c; no benchmarks found.

**OEMs and O&M providers**
- Nearthlab lists Siemens Gamesa, Vestas, GE ("top three global wind OEMs") plus Axess and GE Vernova as partners; 100k+ blades inspected, 40+ countries; also pivoting into defense (UAE $10M production contract) - https://www.nearthlab.com/en
- Nearthlab x Siemens Gamesa: Taiwan offshore (2020) then onshore North America - https://uasweekly.com/2020/12/23/nearthlab-enters-taiwanese-offshore-wind-turbine-market-with-siemens-gamesa-renewable-energy/
- X-ray modality: SpectX with TNO, GE Vernova and LM Wind Power launched a two-year project on drone X-ray detection of sub-surface blade defects (snippet; article 403) - https://windpowernl.com/2025/01/15/sub-surface-defects-detection-in-wind-turbine-blades-by-drone-x-ray-inspection/ (2025-01-15). Inference: OEMs are exploring X-ray themselves; a startup's role is the analysis/grading layer, not the sensor.
- SkySpecs x PLP partnership brings power-line and blade inspection together - https://skyspecs.com/resources/brochures/skyspecs-plp-partnership/
- Not found: any public AECOM/WSP inspection-AI partnership; engineering consultancies as a channel remains unvalidated.

**Drone platforms / marketplaces**
- Skydio Extend integration catalog: "pre-built integrations that can be activated with a flip of a switch and partner-built integrations" - partners include Optelos, Levatas, DroneDeploy, gNext - https://www.skydio.com/software/extend-integrations ; https://www.skydio.com/blog/optelos-partner-drone-inspection ; https://www.skydio.com/integrations-catalog/gNext
- DroneDeploy x Skydio Cloud integration - https://www.dronedeploy.com/blog/introducing-the-dronedeploy-x-skydio-cloud-integration
- DJI FlightHub 2 + thermal tool is free for DJI owners but has "no AI, automated detection, or IEC reporting" - https://www.sitemark.com/research/best-solar-inspection-software/ (2026-05-26). But: FCC added all new foreign-made drones to its Covered List in Dec 2025; utilities increasingly mandate NDAA-compliant platforms (Skydio X10, Freefly Astro, Inspired Flight) (snippet) - https://detectinspections.com/blog/2026-trends-for-drone-service-providers
- Inference: a Skydio Extend / DroneDeploy listing is a realistic zero-cost distribution channel for a software-only analytics layer; being "platform-agnostic" (any camera, any drone, ROV, handheld, thermal, X-ray) is a differentiator given the NDAA fleet churn.

### 3. Sales-cycle realities at utilities and DOTs; how startups shorten them

**Gatekeepers before anyone evaluates your model** (https://detectinspections.com/blog/utility-drone-vendor-evaluation , 2024-04-09):
- Gate 1 safety prequalification: ISNetworld / Avetta, OSHA 300/301 logs, EMR, written HSE programs, drug & alcohol policy, training records, cybersecurity measures.
- Gate 2 regulatory/insurance: Part 107, NDAA-compliant fleet (Blue/Green UAS), GL insurance at utility thresholds, E&O, aviation hull & liability, workers comp, Part 108 BVLOS readiness, audit-ready geotagged chain-of-custody flight records.
- Then: data quality (rework <10%), turnaround (5-day target with severity-ranked findings), scalability; AI analytics and domain expertise are *secondary*; pricing evaluated last.
- Internal benchmark utilities compare against: Georgia Power in-house program - 14 miles/day, 5,174 abnormal conditions found by drones vs 1,150 by ground crews, 60% annual cost savings.

**Timelines from real awards**
- MissionGO flew SCE trials from 2019 (6,500+ sorties, 1,200+ flight hours, 20,000 distribution + 4,000 transmission poles) before the 3-year, $50M, ~160k-pole program announced Oct 2022 - https://dronedj.com/2022/10/20/southern-california-edison-drone-inspection/ ; https://www.commercialuavnews.com/energy/missiongo-signs-three-year-deal-to-provide-drone-based-inspections-for-southern-california-edison (2023-01-24). Inference: ~3 years from trial to scaled award; the contract coverage does not mention AI analytics - capture and analytics were procured separately.
- SCE now runs "one of the largest autonomous inspection programs in the country" with 100+ drones and docks coming - https://www.skydio.com/customer-stories/sce-scales-drone-inspections-to-transform-grid-safety ; SCE inspects 400,000+ poles/transformers/lines annually and addresses high-risk issues within 24 hours - https://landing.ai/blog/southern-california-edisons-use-of-computer-vision-and-aerial-inspections (2024-10-11)
- Generic pilot mechanics: fixed 30-90 day pilots with a conversion clause that auto-converts to a standard contract if success criteria are met (snippet) - https://dowhatmatter.com/guides/startup-pilot-program

**Security / data residency**
- NERC CIP-013-2 extends supply-chain risk obligations to EACMS/PACS vendors (snippet) - https://www.assurx.com/nerc-cip-013-cyber-security-supply-chain-risk-management-for-utilities/
- NERC's own cloud white paper lists "drone video storage" among cloud-appropriate, non-regulated utility workloads - https://www.nerc.com/comm/RSTC_Reliability_Guidelines/SITES_WhitePaper_BES_Ops_in_Cloud.pdf . Inference: inspection imagery is generally outside BES Cyber System scope, so a cloud SaaS is feasible, but expect SOC 2 questionnaires (Raptor Maps advertises SOC 2 - https://apps.list.solar/tools/raptor-maps/ ).

**Programs that shorten the cycle**
- EPRI Incubatenergy Labs (8th year): "paid proof-of-concept demonstration projects alongside top electric power companies" (snippet; press page not fetchable) - https://www.epri.com/about/media-resources/press-release/obfo6iqwyjhqigl3vnlr4qennemzssyw
- Free Electrons 2026: applications 2025-10-17 to 2026-01-31; utility partners CLP, EDP, E.ON, ESB, Hydro-Quebec, Origin Energy (snippet; site not fetchable) - https://freeelectrons.org/2026-program/ . Inference: the 2027 cohort likely opens ~Oct 2026 - worth applying right after the hackathon.
- USDOT Drone Infrastructure Inspection Grants (DIIG) FY26: $9M total, ~5 awards of $500k-$9M, eligible = state/local/tribal governments and MPOs; forecast notice 2026-09-15, close 2026-11-15 - https://dronexl.co/2026/08/03/usdot-diig-9-million-drone-inspection-grants-fy26/ (2026-08-03). Context: 23 states reported 467 grounded/restricted airframes from the DJI ban; state-agency exposure ~$56M. Inference: a startup cannot apply directly but can be the named technology partner of a city/county DOT applicant - a concrete Q4-2026 play.
- USDOT SMART: $500M over 5 years; Dec 2024 round $130M to 42 projects; Alaska DOT&PF $12M+ for drone infrastructure inspection; Indiana DOT $2M UAS; Caltrans $430k+ drone construction-site inspection - https://aashtojournal.transportation.org/usdot-issues-130m-worth-of-smart-program-grants/ (2024-12-20)
- FEMA BRIC: $1B NOFO released 2026-03-25 for FY24-25; subapplication deadline 2026-07-23 (already closed as of today); national competition up to $20M per subapplication - https://www.fema.gov/press-release/20260325/fema-announces-1-billion-federal-funding-help-states-mitigate-impact
- California Energy Commission EPIC: "invests more than $130 million annually", funded by PG&E/SCE/SDG&E ratepayers; current solicitation GFO-26-501 "Innovations in Open Data and Modeling for a Climate- and Wildfire-Resilient Electricity System" (pre-application workshop 2026-09-10); 25% of demo funding must go to disadvantaged communities - https://www.energy.ca.gov/programs-and-topics/programs/electric-program-investment-charge-epic-program
- Caltrans completed research Task 4419 "Development of Autonomous Drone Inspection for Bridge Maintenance" (Nov 2025) - https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-results/task4419-rrs-11-25-a11y.pdf . Inference: Caltrans DRISI is a warm, LA-adjacent research buyer for bridge-element grading.

### 4. Funding / traction benchmarks

| Company | Latest round | Total raised | Traction signals | Sources |
|---|---|---|---|---|
| Zeitview (ex-DroneBase, Santa Monica) | $60M Series F, 2025-03-05/07, led by Climate Investment; Valor, USV, Upfront, Euclidean, Hearst, YC | ~$174M over 11 rounds (snippet) | 200,000+ assets inspected in 2024 across 80 countries; utilities page: 300k T&D assets, 11K+ pilots, 290,000+ missions; "shifted from drone-based inspections to software-focused solutions" | https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ ; https://www.zeitview.com/utilities ; https://tracxn.com/d/companies/zeitview/__oltwPAzbfQ65ZmjANFgYdJIOSYNasexc4ohUFet2-R4 (snippet) |
| SkySpecs (Ann Arbor) | $20M Series E, 2025-03-19 (snippet; another snippet calls it Series D) | not confirmed | 102 offshore WTGs inspected in Jan 2025, <=28 min/turbine autonomous; 25 turbines/day at EDF Teesside; offices in US, Austria, Denmark, India, Ireland, Serbia; Horizon BAM/CMS/Solar SaaS | https://skyspecs.com/blog/offshore-wind-inspections-2025/ ; https://www.cbinsights.com/company/skyspecs/financials (snippet) |
| Raptor Maps (Boston) | $22M Series B, Apr 2022 | not found beyond that | 373 GWdc of solar analyzed incl. 75+ GW non-DC health inspections (2026 report); SOC 2 | https://raptormaps.com/press/solar-lifecycle-management-software-leader-raptor-maps-raises-22-million-to-advance-analytics-insights ; https://raptormaps.com/resources/2026-global-solar-report |
| Buzz Solutions (Bay Area) | $20M Series A, 2026-08-04, led by S3 Ventures; GoPoint, HearstLab, Blackhorn | not stated | Dominion, AEP, NYPA; customers 3x and revenue +400% since prior round; 0.6 s/image vs 1-2 min manual (snippet); expanding to utility-scale solar | https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/ |
| Percepto (Israel) | Series C $67M Jun 2023; one aggregator lists an unattributed round 2025-12-08 (snippet, unconfirmed) | ~$134-137M | Revenue estimate $26M (2024) with 173 staff (GetLatka estimate, not company-disclosed); customers Koch, Delek US, Siemens Energy, Enel (snippets) | https://getlatka.com/companies/percepto.co ; https://www.startuphub.ai/startups/percepto |
| Skydio (San Mateo) | $110M Series F, 2026-04-23, $4.4B valuation | ~$966M (snippet) | "hundreds of millions in annual revenue", public safety / defense / critical infrastructure / site security; "how little we are raising" | https://www.skydio.com/blog/skydio-series-f ; https://dronelife.com/2026/04/28/skydio-series-f-110m-funding-us-manufacturing/ |
| Sharper Shape (Finland/US) | secondary; no 2025 primary round found | $21.25M | Serves T&D owners **and DSPs**; launched AI Asset Insights (Oct 2024) and LiDAR Insights with 29 utility classes (Aug 2025) | https://www.cbinsights.com/company/sharper-shape-oy ; https://uasweekly.com/2025/08/06/sharper-shapes-lidar-insights-boosts-ai-driven-utility-mapping/ |
| Voliro (Zurich) | $23M Series A extension, 2025-06-16 (noa; UBS debt) | $23M | 40+ customers, 17 countries, 100+ contact inspections/month; Chevron, Holcim, Acuren; drone subscription model | https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ |
| Nearthlab (Seoul) | - | ~$24.12M (snippet) | 100k+ blades, 40+ countries, 99.9%+ mission success; OEM partners SGRE, Vestas, GE; UAE $10M defense contract | https://www.nearthlab.com/en ; https://tracxn.com/d/companies/nearthlab/__tKLMU601n90HKrsG-dCczlZvn6nfSPGLVf3Sg3UdZbo (snippet) |
| Sitemark (Belgium) | not researched | - | self-reported 310+ GWp, 1,100+ companies, 100+ countries | https://www.sitemark.com/research/best-solar-inspection-software/ (2026-05-26) |

Calibration takeaways (Inference): (a) 3 utility logos + steep growth = $20M Series A in 2026; (b) the pure-software, multi-asset players (Buzz, Sharper Shape, Sitemark) are the closest analogues to the team's idea; (c) the hardware-heavy players (Skydio, Percepto, Voliro) monetize through hardware/subscription and treat analytics as an ecosystem - which is why they run partner catalogs a software startup can join.

### 5. First-100-customers playbook (hypothesis, to validate this weekend)

**Segment ranking by (pain x speed to close x reachability from LA)** - Inference built on the sources above:
1. **Small/mid DSPs and independent O&M firms (wind, solar, T&D)** - pain is documented (AI-ready data requirements, 15-25% imagery rejection, commoditization, NDAA fleet churn - Detect 2026); they are told to avoid Tier-1 utilities and sell to regional owners (Drone Launch Academy 2026); the only transparent competitor pricing (Scopito) targets them; Sharper Shape already lists DSPs as a customer class. Sales cycle: days-weeks, card payment. LA has many (e.g., https://rayaccesspro.com/commercial-services/visual-inspections-los-angeles-ca/drone-inspections/ , https://www.thefuture3d.com/services/drone-inspections/los-angeles/ ).
2. **Regional wind/solar owners and IPPs without in-house analytics** - buy per-turbine / per-MW; analytics add-on already priced at $100-300/turbine.
3. **Public agencies via grants** - city/county DOTs (DIIG partner, Q4 2026), Caltrans DRISI research; longer but grant-funded.
4. **Tier-1 utilities and insurers** - later; requires gates (ISNetworld, SOC 2, NDAA) and 1-3 year cycles; enter via EPRI Incubatenergy / Free Electrons / CEC EPIC rather than cold RFPs.

**Pricing to start (hypothesis, anchored to public points)**
- Free tier: N images/month self-serve upload-and-grade (COGS ~$0.0003-0.02/image, see section 6).
- Per-asset: e.g., $49-99 per turbine report (under the $100-300 analytics add-on benchmark), $3-5 per pole (Scopito ~$5/pole at scale), $50-150 per MW thermal (under $300-500/MW service price).
- Per-image credits for DSPs: $0.25-1.00/image (Scopito EUR 1/image expert; Moondream/Gemini inference $0.00006-0.0004/image).
- Team/seat plan for DSPs below DroneDeploy's $329/seat/month.
- Enterprise custom for owners (annual per-site, cf. $10-30k+ solar site contracts).

**Community / dataset plays (Inference)**: publish an open grading rubric per asset class (IEC-style thermal anomaly classes for solar; blade damage categories 1-5 for wind; NBIS element condition states for bridges) and let DSPs upload and get graded for free in exchange for labeled data - the moat is the graded, industry-schema-aligned dataset, not the base VLM.

**What to validate this weekend (real interviews only, no fabricated results)**
- 5-10 LA-area DSP owners: What do you deliver today (raw images? annotated PDF?), how many hours per report, what do clients ask for that you cannot provide (AI grading, severity ranking, IEC/NBIS-aligned reports), would you pay per image or per asset, at what price?
- 2-3 regional solar/wind O&M contacts (LinkedIn/USC alumni): who buys inspection analytics, budget owner, whether SkySpecs/Raptor Maps quotes were too expensive/rigid.
- 1 public-agency contact (Caltrans DRISI, LA County UAS program https://planning.lacounty.gov/unmanned-aircraft-systems-uas-program/ ): is DIIG partnership plausible?
- Instrument the demo: log upload -> gate -> heavy-grade latency and per-image cost live, to make a real (not fabricated) performance claim.

### 6. Unit-economics sketch: small-VLM gate -> heavy VLM cascade

**Model pricing (per 1M tokens; sources)**
- Claude Haiku 4.5 $1 in / $5 out; Claude Sonnet 5 $2 / $10; Claude Opus 5 $5 / $25 - https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025 (2026-08-19); Anthropic's own pricing page is https://claude.com/pricing (linked from the vision docs). Batch API: 50% off on Anthropic (developer docs) and "50% cost reduction" on Gemini - https://ai.google.dev/gemini-api/docs/pricing .
- Gemini 3.1 Flash-Lite $0.25 / $1.50; Gemini 2.5 Flash $0.30 / $2.50; Gemini 3.5 Flash-Lite $0.30 / $2.50; Gemini 3.8/3.7 Flash $0.75 / $3.75 (introductory through 2026-12-31); Gemini 3.1 Pro $2 / $12 - https://ai.google.dev/gemini-api/docs/pricing (fetched 2026-09-24)
- GPT-5 mini $0.25 / $2.00; GPT-5 nano $0.05 / $0.40 - https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025 (2026-08-19)
- Moondream cloud $0.06 per 1,000 images; open weights 0.5B / 2B / 9B-MoE (2B active) - https://moondream.ai/
- Self-hosted Qwen2.5-VL-7B: RTX 4090 rental $0.14-0.42/hr (snippet) -> ~$0.04-0.12 per 1,000 images at 1-2 s/image - https://docs.clore.ai/guides/vision-models/qwen-vl (arithmetic is mine)

**Image token rules (this is where cost actually lives)**
- Claude: visual tokens = ceil(w/28) x ceil(h/28). Standard tier (Haiku 4.5 and other pre-4.7 models): max long edge 1568 px, max 1568 tokens. High-res tier (Claude 4.7 and later, incl. Sonnet 5 / Opus 5): max long edge 2576 px, max 4784 tokens. Examples: 1000x1000 = 1296 tokens; 1920x1080 = 1560 (standard) / 2691 (high-res); 3840x2160 = 1560 / 4784. Docs' own cost examples: Haiku 4.5 1000x1000 ~ $1.30 per 1,000 images; Opus 5 1000x1000 ~ $6.48 per 1,000; Opus 5 4K ~ $23.92 per 1,000. Up to 600 images per request; 32 MB request cap; downsample before sending to control cost - https://platform.claude.com/docs/en/build-with-claude/vision (fetched 2026-09-24)
- Gemini: 258 tokens if both dims <= 384 px; otherwise 768x768 tiles at 258 tokens each; crop unit = floor(min(w,h)/1.5); 960x540 -> 6 tiles; up to 3,600 images per request; Gemini 3+ `media_resolution` caps tokens per image - https://ai.google.dev/gemini-api/docs/image-understanding
- Independent per-image comparison (4K screenshot, 2026-08-26): Qwen3-VL Flash $0.00012, Mistral Small 4 $0.00026, Claude Haiku 4.5 $0.00156, Gemini 3.1 Pro $0.00224, Claude Sonnet 5 $0.00957, GPT-5.6 $0.01958, Claude Opus 5 $0.02392 per image (input only) - https://tokencost.app/blog/vision-api-cost-per-image . Key quote: "the capture pipeline is first-order" - resizing matters more than model choice.

**Cascade cost per image (my arithmetic on the sourced prices; assumptions flagged)**
- Gate (Gemini 3.1 Flash-Lite, 1000x1000 image = 4 tiles = 1,032 tokens @ $0.25/M) ~ $0.00026 input + ~$0.00003 output (20-token verdict) ~ **$0.0003/image** (~$0.30 per 1,000). A 20 MP drone frame (5472x3648 -> 6 tiles = 1,548 tokens) ~ $0.0004. Moondream cloud alternative: $0.00006/image. Self-hosted 7B: ~$0.0001.
- Heavy grade (Claude Sonnet 5, high-res tier): 20 MP frame downscaled to 2576 long edge = 4,784 tokens = $0.0096 input; +1,500-token grading rubric prompt ($0.003, cacheable) + ~400-token structured JSON output ($0.004) ~ **$0.015-0.017/image**; Batch API ~ $0.008. Pre-resizing to 1568 long edge (~2,128 tokens) cuts input to $0.0043 -> ~$0.011/image. Opus 5 equivalents: ~$0.024 + $0.0075 + $0.01 ~ $0.04/image (Batch ~$0.02). Haiku 4.5 as the heavy model: 1,560 tokens = $0.0016 + output ~ $0.004/image.
- Per turbine (assumption: 120 images/blade x 3 = 360 images - https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ ; assumption: 20% flagged by the gate - **unvalidated**): gate $0.14 + heavy 72 x $0.015 = $1.08 -> **~$1.20/turbine** (~$0.65 with Batch). Worst case, every image through Opus 5: 360 x $0.04 = $14.40/turbine. Compare price umbrella of $100-300/turbine analytics add-on ( https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost ) -> inference COGS 0.4-15% of price.
- Per pole (assumption: 8 images/pole - **not sourced**): gate $0.003 + heavy ~2 flagged x $0.015 = ~$0.035/pole vs Scopito ~$5/pole -> <1% of price.
- Per MW solar: images per MW **not found**; cannot compute yet - collect from a DSP interview.

**Gross-margin implication (Inference)**: at any per-asset price above ~$5, inference is <5% of revenue; the cascade's economic purpose is (a) making a self-serve free tier survivable (gate-only costs ~$0.30 per 1,000 images), (b) throughput/latency when a storm produces thousands of images at once, and (c) allowing the expensive model to spend tokens only on the ~10-30% of frames that matter. The real COGS drivers will be human QA review (Scopito charges EUR 1/image for expert analysis, which signals what human review costs), cloud storage of 20 MP imagery, and support. Uncertainties: flag rate (depends on asset class and image overlap), false-negative cost of the gate (a missed crack is expensive), and whether customers require on-prem/self-hosted models (NERC/SOC 2 posture), which would shift cost from tokens to GPUs (~$0.5-1/hr for 7-14B models, snippet https://www.cloudclusters.io/cloud/qwen ).

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| Buzz Solutions Series A | $20M, led by S3 Ventures | https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/ | 2026-08-04 |
| Buzz growth since prior round | customers 3x; revenue +400%; customers Dominion, AEP, NYPA | same | 2026-08-04 |
| Zeitview Series F | $60M led by Climate Investment | https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ | 2025-03-07 |
| Zeitview scale | 200,000+ assets in 2024, 80 countries | same | 2025-03-07 |
| Zeitview utilities | 300k T&D assets; 11K+ pilots; 290,000+ missions | https://www.zeitview.com/utilities | 2025 (page) |
| Zeitview total raised | ~$174M over 11 rounds (snippet) | https://tracxn.com/d/companies/zeitview/__oltwPAzbfQ65ZmjANFgYdJIOSYNasexc4ohUFet2-R4 | 2026 |
| SkySpecs Series E | $20M (snippet) | https://www.cbinsights.com/company/skyspecs/financials | 2025-03-19 |
| SkySpecs offshore throughput | 102 WTGs in Jan 2025; <=28 min/turbine | https://skyspecs.com/blog/offshore-wind-inspections-2025/ | 2025-03-03 |
| Raptor Maps Series B | $22M | https://raptormaps.com/press/solar-lifecycle-management-software-leader-raptor-maps-raises-22-million-to-advance-analytics-insights | 2022-04 |
| Raptor Maps analyzed | 373 GWdc; 75+ GW non-DC health inspections | https://raptormaps.com/resources/2026-global-solar-report | 2026 |
| Skydio Series F | $110M at $4.4B; "hundreds of millions" revenue | https://www.skydio.com/blog/skydio-series-f | 2026-04-23 |
| Skydio total raised | ~$966M (snippet) | https://tracxn.com/d/companies/skydio/__z1KXfwRL66HqbZoc40bpJPf2L7G4_LkQYdVL0_-9lj8/funding-and-investors | 2026 |
| Percepto revenue (estimate) | $26M in 2024, 173 staff | https://getlatka.com/companies/percepto.co | 2024 |
| Percepto total raised | ~$137M | https://www.startuphub.ai/startups/percepto | 2026 |
| Voliro raise | $23M total; 40+ customers; 17 countries; 100+ inspections/month | https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ | 2025-06-16 |
| Nearthlab scale | 100,000+ blades; 40+ countries; SGRE/Vestas/GE partners | https://www.nearthlab.com/en | 2026 (page) |
| Nearthlab total raised | $24.12M (snippet) | https://tracxn.com/d/companies/nearthlab/__tKLMU601n90HKrsG-dCczlZvn6nfSPGLVf3Sg3UdZbo | 2026 |
| Sharper Shape total raised | $21.25M; serves T&D owners and DSPs | https://www.cbinsights.com/company/sharper-shape-oy | 2026 |
| Sitemark self-reported | 310+ GWp; 1,100+ companies | https://www.sitemark.com/research/best-solar-inspection-software/ | 2026-05-26 |
| Wind drone inspection price | $300-600/turbine | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ | 2025 |
| Wind analytics add-on | $100-300/turbine | https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost | 2025-05-05 |
| Rope access | $1,500-3,000/turbine | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ | 2025 |
| Turbine downtime | $3,000-17,000/turbine/day | same | 2025 |
| Images per blade | 120 | same | 2025 |
| DSP day rate | $1,500-3,500; 18-25 turbines/day | https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ | 2026-06-01 |
| Solar thermal survey | $300-500/MW; full diagnostic $500-1,200/MW; annual $10-30k+ | https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know | 2025-05-05 |
| SCE pole program | $50M / 3 yrs / ~160,000 poles (~$313/pole implied) | https://dronedj.com/2022/10/20/southern-california-edison-drone-inspection/ | 2022-10-20 |
| SCE trial-to-award | trials from 2019; 6,500+ sorties; award Oct 2022 | same; https://www.commercialuavnews.com/energy/missiongo-signs-three-year-deal-to-provide-drone-based-inspections-for-southern-california-edison | 2023-01-24 |
| SCE fleet | 100+ drones | https://www.skydio.com/customer-stories/sce-scales-drone-inspections-to-transform-grid-safety | 2025-26 |
| SCE annual inspections | 400,000+ poles/transformers/lines; 24-h response to high-risk | https://landing.ai/blog/southern-california-edisons-use-of-computer-vision-and-aerial-inspections | 2024-10-11 |
| Georgia Power in-house benchmark | 14 mi/day; 5,174 vs 1,150 abnormal conditions; 60% savings | https://detectinspections.com/blog/utility-drone-vendor-evaluation | 2024-04-09 |
| DSP imagery rejection | 15-25% needs remediation; in-house program $25-50k start, $10-20k/yr | https://detectinspections.com/blog/2026-trends-for-drone-service-providers | 2026-03-31 |
| PG&E in-house flights | 300,000+ in 2024 | same | 2026-03-31 |
| Scopito pricing | EUR 50/building; EUR 1/image expert, min EUR 150; ~$5/pole at scale | https://scopito.com/building-inspection-software/ ; http://scopito.com/supercharging-utility-inspection/ | 2025 |
| DroneDeploy pricing | $329 / $499 per seat/month | https://www.skyebrowse.com/news/posts/dronedeploy-review | 2026-03-13 |
| Optelos pricing | from $1,000/month (snippet) | https://www.softwaresuggest.com/optelos | 2026 |
| Roof inspection | $150-400 drone vs $300-600 traditional; $99-199 software/report | https://www.skyebrowse.com/news/posts/drone-roof-inspection-cost | 2026-03-16 |
| Bridge drone savings | MnDOT 39 bridges, $540-21,000/bridge, ~40% avg (snippet) | https://www.mdpi.com/2412-3811/10/3/63 | 2025 |
| Nevada DOT bridge | $40,000 saved on one inspection | https://informedinfrastructure.com/90540/off-rope-drones-for-bridge-inspection-increase-safety-decrease-costs-2/ | 2023-10-11 |
| DIIG FY26 | $9M; ~5 awards $0.5-9M; notice 2026-09-15; close 2026-11-15 | https://dronexl.co/2026/08/03/usdot-diig-9-million-drone-inspection-grants-fy26/ | 2026-08-03 |
| SMART drone award | Alaska DOT&PF $12M+; Caltrans $430k+; program $500M/5 yrs | https://aashtojournal.transportation.org/usdot-issues-130m-worth-of-smart-program-grants/ | 2024-12-20 |
| FEMA BRIC | $1B; deadline 2026-07-23; up to $20M/subapplication | https://www.fema.gov/press-release/20260325/fema-announces-1-billion-federal-funding-help-states-mitigate-impact | 2026-03-25 |
| CEC EPIC | >$130M/yr; GFO-26-501 workshop 2026-09-10 | https://www.energy.ca.gov/programs-and-topics/programs/electric-program-investment-charge-epic-program | 2026 |
| Free Electrons 2026 | apps 2025-10-17 to 2026-01-31; CLP, EDP, E.ON, ESB, Hydro-Quebec, Origin (snippet) | https://freeelectrons.org/2026-program/ | 2025-26 |
| Claude image tokens | ceil(w/28) x ceil(h/28); 1000x1000 = 1,296 tokens; high-res cap 4,784 | https://platform.claude.com/docs/en/build-with-claude/vision | 2026-09-24 (fetched) |
| Claude per-1,000-image cost | Haiku 4.5 1000x1000 ~$1.30; Opus 5 ~$6.48; Opus 5 4K ~$23.92 | same | 2026-09-24 |
| Gemini image tokens | 258/tile of 768x768; 258 if <=384 px | https://ai.google.dev/gemini-api/docs/image-understanding | 2026 |
| Gemini prices | 3.1 Flash-Lite $0.25/$1.50; 2.5 Flash $0.30/$2.50; batch -50% | https://ai.google.dev/gemini-api/docs/pricing | 2026-09-24 (fetched) |
| Claude prices | Haiku 4.5 $1/$5; Sonnet 5 $2/$10; Opus 5 $5/$25 | https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025 | 2026-08-19 |
| GPT-5 mini | $0.25/$2.00 | same | 2026-08-19 |
| Per-image 4K comparison | Haiku 4.5 $0.00156; Sonnet 5 $0.00957; Opus 5 $0.02392 | https://tokencost.app/blog/vision-api-cost-per-image | 2026-08-26 |
| Moondream cloud | $0.06 per 1,000 images | https://moondream.ai/ | 2026 |
| Self-host 7B VLM GPU | RTX 4090 $0.14-0.42/hr (snippet) | https://docs.clore.ai/guides/vision-models/qwen-vl | 2025-26 |

---

## Implications for our product / edge

1. **Position as the analytics layer, camera- and drone-agnostic.** Capture is commoditizing (in-house utility fleets, docks, NDAA churn) while analytics requirements are rising. Nobody in the set above serves drone + ROV + handheld + thermal + X-ray in one grading pipeline; the incumbents are single-vertical (SkySpecs wind, Raptor Maps solar) or capture-led (Zeitview). Distribution via Skydio Extend / DroneDeploy catalogs is free.
2. **Sell first to DSPs and independent O&M, priced per asset with a self-serve free tier.** Two independent 2026 sources push DSPs toward regional owners and away from Tier-1 utilities; Scopito's pay-per-asset model proves the buying motion; inference cost (~$0.0003/image gate) makes free tiers survivable. Under-price the $100-300/turbine analytics add-on and the ~$5/pole benchmark.
3. **Make the cascade a product feature, not just a cost trick**: show live per-image cost and latency in the demo; the storm/disaster use case (thousands of images in hours) is where the gate's throughput matters most, matching Prompt D's "rapidly prioritize recovery" clause.
4. **Industry-schema outputs are the moat**: deliver findings in the vocabulary buyers already use (severity-ranked findings within a 5-day turnaround is the utility evaluation criterion; IEC thermal classes for solar; blade damage categories; NBIS element condition states for bridges). Graded, schema-aligned imagery becomes a dataset asset.
5. **Utility entry through programs, not RFPs**: EPRI Incubatenergy (paid POCs), Free Electrons (next cohort likely opens Oct 2026), CEC EPIC (LA-local ratepayer funds; wildfire-resilience solicitations), DIIG (partner with an LA city/county DOT before 2026-11-15). Budget 1-3 years for a Tier-1 utility award; SCE's own example is 2019 trial -> 2022 award.
6. **Plausible traction narrative for judges**: Buzz Solutions' $20M Series A rested on three utility logos and 400% growth; Voliro reached $23M with 40 customers. A believable 18-month goal is 30-100 DSP/O&M accounts plus 1-2 grant-backed public pilots - not "sign PG&E".
7. **Compliance posture to plan now**: SOC 2 roadmap, NDAA-agnostic ingestion, and an optional self-hosted small model for customers who cannot send imagery to a public API.

---

## Open questions / gaps

- No public per-MW or per-turbine analytics price from Raptor Maps, Zeitview, Sitemark or SkySpecs Horizon; the $100-300/turbine analytics add-on is from a DSP-pricing blog, not a vendor.
- Images per MW for solar thermal and images per pole are **not sourced**; needed to finish per-asset COGS. Ask DSPs this weekend.
- Flag rate of the gate (assumed 20%) is unvalidated; measure on a real dataset (e.g., public blade-damage or PV thermal sets) during the hackathon and report the *measured* number, never an assumed one.
- Insurance channel: no pricing or partnership benchmarks found for infrastructure (non-roof) inspection AI.
- Engineering consultancies (AECOM/WSP) as channel: not found.
- Utility pilot-to-contract statistics: the GridCatalyst Oct 2025 report ( https://gridcatalyst.org/wp-content/uploads/2025/10/accelerating-utility-innovation-and-startup-collaboration.pdf ) was too large to fetch; likely contains pilot duration / conversion data - read manually.
- EPRI Incubatenergy paid-POC amounts and Free Electrons pilot values: pages blocked; confirm directly.
- Aggregator conflicts: Zeitview pilot count (11K US vs 80K worldwide), Percepto Dec-2025 round, SkySpecs round letter. Verify against primary press releases before putting in the deck.
- Number of US DSPs / Part 107 pilots (TAM for the DSP segment): search budget exhausted before this was sourced - **not found**.
- Underwater/ROV inspection pricing (hull, pier, pipeline): **not found** in this session.
- Which grading standards are legally/contractually required per asset class (IEC 62446-3 for PV thermography, NBIS/AASHTO element states for bridges, OEM blade damage categories) - covered by other research angles; confirm before hard-coding schemas.

---

## Sources

1. https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ - Zeitview $60M Series F, 200k assets/80 countries, pivot to software (2025-03-07)
2. https://www.zeitview.com/utilities - Zeitview two-tier model; 300k T&D assets, 11K+ pilots, 290k missions
3. https://tracxn.com/d/companies/zeitview/__oltwPAzbfQ65ZmjANFgYdJIOSYNasexc4ohUFet2-R4 - Zeitview ~$174M total (snippet)
4. https://www.axios.com/pro/climate-deals/2025/03/05/zeitview-climate-investment-inspections-dronebase - Zeitview round coverage (not fetched)
5. https://skyspecs.com/blog/offshore-wind-inspections-2025/ - SkySpecs offshore throughput, offices, Horizon SaaS (2025-03-03)
6. https://www.cbinsights.com/company/skyspecs/financials - SkySpecs $20M Series E 2025-03-19 (snippet)
7. https://energy.toolsinfo.com/tool/skyspecs - SkySpecs positioning; no public pricing
8. https://raptormaps.com/press/solar-lifecycle-management-software-leader-raptor-maps-raises-22-million-to-advance-analytics-insights - Raptor Maps $22M Series B (2022)
9. https://raptormaps.com/resources/2026-global-solar-report - 373 GWdc analyzed
10. https://apps.list.solar/tools/raptor-maps/ - Raptor Maps custom enterprise pricing, SOC 2
11. https://dealroom.co/news/143006-buzz-solutions-raises-20m-series-a-to-scale-grid-inspection-ai/ - Buzz $20M Series A, customers, growth (2026-08-04)
12. https://getlatka.com/companies/percepto.co - Percepto $26M revenue estimate (2024)
13. https://www.startuphub.ai/startups/percepto - Percepto round history, ~$137M
14. https://www.skydio.com/blog/skydio-series-f - Skydio $110M at $4.4B (2026-04-23)
15. https://dronelife.com/2026/04/28/skydio-series-f-110m-funding-us-manufacturing/ - Skydio round coverage
16. https://tracxn.com/d/companies/skydio/__z1KXfwRL66HqbZoc40bpJPf2L7G4_LkQYdVL0_-9lj8/funding-and-investors - Skydio ~$966M total (snippet)
17. https://www.cbinsights.com/company/sharper-shape-oy - Sharper Shape $21.25M; serves DSPs
18. https://uasweekly.com/2025/08/06/sharper-shapes-lidar-insights-boosts-ai-driven-utility-mapping/ - Sharper Shape LiDAR Insights (2025-08-06)
19. https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ - Voliro $23M, 40+ customers (2025-06-16)
20. https://www.nearthlab.com/en - Nearthlab 100k+ blades, OEM partners
21. https://tracxn.com/d/companies/nearthlab/__tKLMU601n90HKrsG-dCczlZvn6nfSPGLVf3Sg3UdZbo - Nearthlab $24.12M (snippet)
22. https://uasweekly.com/2020/12/23/nearthlab-enters-taiwanese-offshore-wind-turbine-market-with-siemens-gamesa-renewable-energy/ - Nearthlab x Siemens Gamesa
23. https://www.sitemark.com/research/best-solar-inspection-software/ - vendor comparison incl. pricing models (2026-05-26)
24. https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ - wind inspection costs, downtime, 120 images/blade (2025)
25. https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost - wind price ranges, $100-300 analytics add-on (2025-05-05)
26. https://averroes.ai/blog/wind-turbine-drone-inspection-cost-breakdown-advice - wind cost triangulation (2026-05-18)
27. https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ - DSP day rates, go-to-market advice (2026-06-01)
28. https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know - solar $/MW (2025-05-05)
29. https://www.geowgs84.com/post/how-much-does-a-drone-solar-panel-inspection-cost - solar $150-500/MW (snippet)
30. https://dronedj.com/2022/10/20/southern-california-edison-drone-inspection/ - SCE $50M / 160k poles (2022-10-20)
31. https://www.commercialuavnews.com/energy/missiongo-signs-three-year-deal-to-provide-drone-based-inspections-for-southern-california-edison - MissionGO 3-year deal (2023-01-24)
32. https://www.skydio.com/customer-stories/sce-scales-drone-inspections-to-transform-grid-safety - SCE 100+ drones
33. https://landing.ai/blog/southern-california-edisons-use-of-computer-vision-and-aerial-inspections - SCE 400k+ assets/yr, CV use (2024-10-11)
34. https://detectinspections.com/blog/utility-drone-vendor-evaluation - utility vendor gates; Georgia Power benchmark (2024-04-09)
35. https://detectinspections.com/blog/2026-trends-for-drone-service-providers - DSP 2026 trends and pain points (2026-03-31)
36. https://www.nerc.com/comm/RSTC_Reliability_Guidelines/SITES_WhitePaper_BES_Ops_in_Cloud.pdf - NERC cloud white paper (drone video storage as cloud-appropriate)
37. https://www.assurx.com/nerc-cip-013-cyber-security-supply-chain-risk-management-for-utilities/ - NERC CIP-013 supply-chain scope (snippet)
38. https://dowhatmatter.com/guides/startup-pilot-program - 30-90 day pilots with conversion clauses (snippet)
39. https://www.epri.com/about/media-resources/press-release/obfo6iqwyjhqigl3vnlr4qennemzssyw - EPRI Incubatenergy paid POCs (snippet; page not fetchable)
40. https://freeelectrons.org/2026-program/ - Free Electrons 2026 dates and utilities (snippet; blocked)
41. https://dronexl.co/2026/08/03/usdot-diig-9-million-drone-inspection-grants-fy26/ - DIIG FY26 $9M details (2026-08-03)
42. https://simpler.grants.gov/opportunity/528f0601-d652-4708-bc74-3567f288f365 - DIIG official listing (blocked)
43. https://aashtojournal.transportation.org/usdot-issues-130m-worth-of-smart-program-grants/ - SMART awards incl. Alaska $12M drones (2024-12-20)
44. https://www.fema.gov/press-release/20260325/fema-announces-1-billion-federal-funding-help-states-mitigate-impact - BRIC $1B (2026-03-25)
45. https://www.energy.ca.gov/programs-and-topics/programs/electric-program-investment-charge-epic-program - CEC EPIC >$130M/yr, GFO-26-501
46. https://dot.ca.gov/-/media/dot-media/programs/research-innovation-system-information/documents/research-results/task4419-rrs-11-25-a11y.pdf - Caltrans autonomous bridge drone research (Nov 2025)
47. https://www.mdpi.com/2412-3811/10/3/63 - drone bridge inspection cost-efficiency paper (2025; 403, snippet only)
48. https://informedinfrastructure.com/90540/off-rope-drones-for-bridge-inspection-increase-safety-decrease-costs-2/ - Nevada DOT $40k savings (2023-10-11)
49. https://www.skyebrowse.com/news/posts/bridge-and-roadway-inspections - traditional bridge inspection cost (snippet)
50. https://scopito.com/building-inspection-software/ - Scopito per-building / per-image pricing
51. http://scopito.com/supercharging-utility-inspection/ - Scopito ~$5/pole at scale (2020, updated 2025)
52. http://scopito.com/power-line-inspection-software/ - Scopito EUR 40/pole (snippet)
53. https://www.skyebrowse.com/news/posts/dronedeploy-review - DroneDeploy $329/$499 per seat (2026-03-13)
54. https://www.softwaresuggest.com/optelos - Optelos from $1,000/month (snippet; blocked)
55. https://assets.ctfassets.net/go54bjdzbrgi/1z3eFwWcqCSnHEcTpmMZM7/769ff3950fec59de073ad88224bf61b3/211008_-_Additional_Term_GTC-_PIX4Dinspect.pdf - PIX4Dinspect inspection-block licensing
56. https://www.skyebrowse.com/news/posts/drone-roof-inspection-cost - roof inspection prices, $99-199 software fee (2026-03-16)
57. https://blog.zeitview.com/drone-insurance-inspections-for-properties - Zeitview insurance use (snippet)
58. https://www.skydio.com/software/extend-integrations - Skydio Extend partner integrations
59. https://www.skydio.com/blog/optelos-partner-drone-inspection - Optelos x Skydio
60. https://www.skydio.com/integrations-catalog/gNext - gNext on Skydio catalog
61. https://www.dronedeploy.com/blog/introducing-the-dronedeploy-x-skydio-cloud-integration - DroneDeploy x Skydio
62. https://www.compositesworld.com/articles/service-repair-optimizing-wind-powers-grid-impact- - OEMs vs independents performing blade inspections (2018-03-26)
63. https://windpowernl.com/2025/01/15/sub-surface-defects-detection-in-wind-turbine-blades-by-drone-x-ray-inspection/ - SpectX/TNO/GE Vernova/LM drone X-ray project (2025-01-15; 403, snippet)
64. https://skyspecs.com/resources/brochures/skyspecs-plp-partnership/ - SkySpecs x PLP
65. https://platform.claude.com/docs/en/build-with-claude/vision - Claude image token formula, tiers, cost examples (fetched 2026-09-24)
66. https://ai.google.dev/gemini-api/docs/pricing - Gemini prices, batch discount (fetched 2026-09-24)
67. https://ai.google.dev/gemini-api/docs/image-understanding - Gemini image tiling rules
68. https://intuitionlabs.ai/articles/llm-api-pricing-comparison-2025 - cross-vendor LLM prices (2026-08-19)
69. https://tokencost.app/blog/vision-api-cost-per-image - per-image cost comparison (2026-08-26)
70. https://moondream.ai/ - Moondream $0.06 per 1,000 images
71. https://docs.clore.ai/guides/vision-models/qwen-vl - GPU rental rates for Qwen2.5-VL (snippet)
72. https://www.cloudclusters.io/cloud/qwen - Qwen hosting cost ranges (snippet)
73. https://gridcatalyst.org/wp-content/uploads/2025/10/accelerating-utility-innovation-and-startup-collaboration.pdf - utility-startup collaboration report (Oct 2025; too large to fetch)
74. https://rayaccesspro.com/commercial-services/visual-inspections-los-angeles-ca/drone-inspections/ - example LA drone inspection DSP (interview target)
75. https://www.thefuture3d.com/services/drone-inspections/los-angeles/ - example LA drone inspection DSP (interview target)
76. https://planning.lacounty.gov/unmanned-aircraft-systems-uas-program/ - LA County UAS program (public-agency contact)
