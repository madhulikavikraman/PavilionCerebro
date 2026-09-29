# 04 — Market Pain, Market Size, and Regulatory Drivers for AI-Assisted Infrastructure Inspection

Research angle: `market_pain_size_regulation` | Prepared 2026-09-24 (Thursday) for Origin Weekend Fall 2026, Prompt D.
Scope: quantify the problem and market for a startup whose wedge is **AI damage grading + repair prioritization software** (not drone hardware, not flight services), across wind blades, solar (thermal), bridges, underwater structures, power lines/poles, and telecom towers.

Conventions: every number carries a source URL and the source's date. Items marked **Inference:** are our own derivation, not a sourced fact. "Not found" means we searched and could not source it; do not put such a number on a slide. Vendor-published numbers (drone service marketplaces, inspection vendors) are marked **(vendor)** — usable for order of magnitude, weak as evidence to judges.

---

## Summary

- **Manual inspection is expensive per asset and the delta to drone capture is already large — which means the remaining cost is in *analysis*, not flight.** Rope-access wind blade inspection runs US$1,500–3,000/turbine and 3–6 hours vs. US$300–600 and 15–45 minutes by drone (vendor, skyvisor.ai, 2026). A conventional MnDOT inspection of the Blatnik Bridge cost ~$59,000 (8 days, 4 snoopers) vs. a $20,000 five-day UAS contract (MnDOT, Aug 2017). Helicopter line patrol is $1,200–1,600/mile vs. $200–300/mile by drone (Drone Launch Academy, Apr 2026). Data-processing/analytics is a separately priced add-on of ~$100–300 per turbine (UAVsphere, May 2025) — that is the software wedge.
- **Failure costs dwarf inspection costs by 10–100x.** A minor onshore blade repair is ~$30,000; a structural repair when a replacement blade is unavailable ~$500,000; offshore complex repairs $1M+ (ONYX Insight, Dec 2025). US blade repairs exceeded $1B in 2025 and blades are 37% of turbine repairs (POWER, Aug 2026; both from ONYX Insight's CEO — vendor-adjacent). Solar assets lose 5.08% of power on average to equipment anomalies, i.e. up to ~$5,070 per MW per year (Raptor Maps 2026 Global Solar Report, 373 GWdc dataset).
- **Asset counts are enormous and inspection is legally recurring.** 624,167 US bridges, 41,677 (6.7%) poor, 35% need major repair, $467B to fix (ARTBA 2025, NBI data 24 Jun 2025). 77,379 US wind turbines (USGS USWTDB v9.0, 26 Jun 2026). ~180M US utility poles (~130M wood) (DOE/LBNL, Sep 2024). 154,800 purpose-built cell towers / 248,050 macro sites at end-2024 (WIA, May 2025). 92.5 GW global offshore wind at end-2025 (GWEC, Jun 2026). Bridges must be inspected every 24 months (NBIS); PG&E proposes 3-year detailed cycles for every structure plus aerial scans in high-risk areas (PG&E 2026–28 WMP); TIA-222 requires tower inspections every 3 (guyed) or 5 (self-supporting) years.
- **Disasters concentrate the pain into days.** Duke Energy's 2024 hurricane season (Debby/Helene/Milton) cost ~$2.8B net of insurance (Duke 10-K FY2024); Milton alone required 16,000 workers and 1,560 pole replacements in Florida (Renewable Energy World, Dec 2024). Key Bridge collapse: up to $15M/day in lost state revenue (MD Chamber, Mar 2024). Rapid triage from imagery is exactly where prioritization software earns its keep.
- **Regulation is moving toward risk-based, data-rich inspection — favorable to software.** NBIS 2022 allows 48- and 72-month intervals *only* with documented risk assessment; SNBI element-level data must be fully collected by 15 Mar 2028; FHWA explicitly says UAS "may be used to supplement portions of a bridge inspection" but cannot replace qualified inspectors (NBIS Final Rule, 6 May 2022). IEC TS 62446-3:2017 governs PV thermography validity (still the current edition, stability date 2026). NAIC's AI Model Bulletin plus 13 state bulletins now regulate insurer use of aerial imagery (Carrier Management, Mar 2026). FAA Part 108 (BVLOS) is at OIRA and expected by end-2026 (Flight Brief, 14 Sep 2026).
- **The labor bottleneck is analysis, not flying.** ~30% of certified NDT personnel are over 55 (ASNT 2023 via Quality Magazine, May 2025); US NDT workforce is ~89,800 with Level II the scarcest tier (ASNT Foundation). US solar jobs grew 12% while capacity grew 286% in five years; a technician now covers 70% more MW (IREC via Raptor Maps 2026). Meanwhile there are hundreds of thousands of Part 107 remote pilots (exact FAA count not verified; FAA pages returned 403) — pilots are plentiful, qualified graders are not.
- **Analyst "market sizes" are mostly not our market.** Drone inspection & monitoring: $15.5B (2025) → $18.44B (2026) → $36.94B (2030), 19% CAGR — but defined as *service* revenue including equipment (The Business Research Company). "AI vision inspection" at $32B (2025) is manufacturing QC, not infrastructure (Precedence Research). The only software-specific figure, $0.81B (2025) for AI visual inspection software, has no infrastructure segment at all (Global Growth Insights). Use these for context only; build TAM bottom-up.
- **Defensible framing (Inference, assumptions stated in §7):** global software/analytics layer of drone inspection ≈ $2–4B (2025); US SAM for AI grading/prioritization across our five asset classes ≈ $0.2–0.6B/yr; 3-year SOM ≈ $1–5M ARR from 10–20 design-partner accounts. The pitch should lead with *avoided-failure value* ($5,070/MW/yr solar leakage, $30k→$500k blade escalation, $467B bridge backlog) rather than with inspection-cost savings, which drone vendors already claim.

---

## Detailed findings

### 1. Inspection cost per asset today, and inspection frequency

#### 1.1 Wind turbine blades
| Method | Cost per turbine | Time per turbine | Throughput | Source |
|---|---|---|---|---|
| Rope access | US$1,500–3,000 | 3–6 hrs | 1–2 turbines/day | skyvisor.ai (vendor, ©2026) https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ |
| Drone, standard visual | US$300–600 | 15–45 min | 18–25 turbines/day | same |
| Drone, range incl. advanced | US$300–1,000; thermal/advanced $2,000–4,000+ | "under an hour" | — | UAVsphere (vendor, 5 May 2025) https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost |
| **Data processing/analytics add-on** | **+$100–300 per turbine** | — | — | UAVsphere (5 May 2025), same URL |

- Downtime during inspection: rope access implies 3–6 hours of production loss per turbine (skyvisor.ai). Skyvisor puts lost production at US$3,000–17,000 per turbine per day of downtime (vendor; wide range, depends on turbine size and price).
- Frequency: skyvisor.ai states 6–12 month standard interval, 3–6 months at harsh coastal sites (vendor). POWER (Aug 2026) describes "annual drone inspections" as current standard practice. Standards: IEC 61400-5:2020 (+2025 amendment) covers blade O&M; DNV-ST-0376 (revised 2024) specifies recommended inspection intervals — both per search summaries (Hornbill Technology / GlobalSpec), not fetched directly.
- Contradiction to note: skyvisor's "rope access up to $3,000" vs. one search-summarized case of $3,770/turbine/yr rope-access spend (Drone Launch Academy page, not fetched). Order of magnitude consistent.

#### 1.2 Bridges
- **Snooper / UBIT truck:** rental ~$2,500/day; purchase >$600,000 (Flyability blog, undated) https://www.flyability.com/blog/bridge-inspections ; equipment $200,000–500,000 (Inside Unmanned Systems, 2 Mar 2021) https://insideunmannedsystems.com/advancing%E2%80%A8-bridge-inspection/
- **Worked example (large bridge):** Blatnik Bridge (MN/WI) conventional inspection = four snoopers + 80-ft lift + 8 inspection days ≈ **$59,000** (excluding mobilization/travel); UAS inspection contracted as a five-day **$20,000** project (MnDOT Technical Summary 2017-18TS, Aug 2017) https://mdl.mndot.gov/_flysystem/fedora/2023-02/201718ts.pdf . Inside Unmanned Systems (2021) cites 40–60% savings with drones depending on structure.
- **Hourly rate benchmarks (WSDOT rate comparison, undated legislative report):** state UBIT team all-in $542.41/hr (truck $128.52 + driver $94.43 + inspector $113.03 + co-inspector $94.43 + report writing $112); city/county quotes $468–$527.50/hr; **underwater inspection with report $2,265 (WSDOT) / $1,920 (private firms); dive-only $1,065 / $1,010** — the document header says dollars/hr, but the underwater lines read like per-inspection or per-day rates; verify before quoting. https://app.leg.wa.gov/ReportsToTheLegislature/Home/GetPDF?fileName=High+Cost+Bridge+Inspection+Cost+Comparison_18ee4d7a-0591-4fef-b707-e9bcd8dc9197.pdf
- **Frequency (NBIS, 23 CFR 650, final rule 6 May 2022):** routine inspection every 24 months by default; **Method 1** allows 48 months if condition rating ≥6, load rating factor ≥1.0, no AASHTO fatigue-prone E/E' details, vertical clearance ≥14 ft; **Method 2** allows up to 72 months with an FHWA-approved risk assessment panel; NSTM (fracture-critical) inspections 24 months, extendable to 48 via risk-based criteria; underwater inspections extendable up to 72 months under Method 2, with reduced intervals when underwater condition ≤3. FHWA: UAS "may be used … to supplement portions of a bridge inspection, but it cannot address all aspects" and cannot replace on-site qualified personnel. https://www.govinfo.gov/content/pkg/FR-2022-05-06/html/2022-09512.htm . Flyability summarizes the pre-existing baseline as routine 24 months, fracture-critical 24 months, underwater 60 months.
- MnDOT context: Minnesota has ~600 bridge inspectors for >20,000 bridges; poor-condition and fracture-critical bridges inspected every 12 months (MnDOT, Aug 2017).

#### 1.3 Solar PV (aerial thermography)
| Item | Value | Source |
|---|---|---|
| Drone thermal inspection price | $150–500 per MW | Averroes (vendor, 14 Jul 2026) https://averroes.ai/blog/how-much-does-drone-solar-panel-inspection-cost-2024 |
| Thermal survey only / full diagnostic + report | $300–500/MW / $500–1,200/MW | UAVsphere (vendor, 5 May 2025) https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know |
| 10 MW site, full thermographic inspection | $1,500–5,000 | Averroes (14 Jul 2026) |
| Throughput: handheld IR vs drone | 200–400 panels/hr vs 2,000–5,000 panels/hr | Averroes (14 Jul 2026) |
| Turnaround | 3–5 business days; AI-assisted processing 24–72 hrs | Averroes (14 Jul 2026) |

- Frequency: IEC TS 62446-3 does not mandate a cadence; annual aerial thermography is common industry practice (inference from vendor pages). Raptor Maps finds sites with docked autonomous drones inspect ~12x more often than sites without (Raptor Maps 2026 report, see 2.2).
- Standard: **IEC TS 62446-3:2017 (Ed. 1.0, 15 Jun 2017)** is still the current edition; IEC webstore lists stability date 2026 and no replacement https://webstore.iec.ch/en/publication/28628 . A search-summarized vendor claim of "IEC 62446-3:2025" could not be verified and should not be used. Requirements per secondary summaries (GlobalSpec / Above Surveying): minimum irradiance, camera/lens specs, ≥5x5 pixels per cell, reporting content; one 2025 study used ≥800 W/m² and ≤3 m/s wind (EPJ Photovoltaics 2025, https://www.epj-pv.org/articles/epjpv/full_html/2025/01/pv20250040/pv20250040.html , not fetched).

#### 1.4 Underwater structures
- Diver vs ROV: a vendor claims ~68% cost reduction (also stated as 50–70%, "5x lower") for ROV vs commercial dive teams, without sources (Deep Sky IQ, vendor) https://www.deepskyiq.com/underwater-rov-submerged-asset-intelligence . Treat as unverified.
- Rate benchmark: WSDOT underwater inspection with report $2,265 (state) / $1,920 (private); dive-only $1,065 / $1,010 (WSDOT rate comparison; unit ambiguity noted above).
- Frequency: NBIS underwater inspections historically every 60 months (Flyability); 2022 rule allows extension to 72 months under Method 2 (govinfo). Marine vendor guidance: timber piles annually, steel in seawater 2–3 years, concrete in freshwater 3–5 years (Deep Sky IQ, vendor).
- Commercial diver day rates: **not found** in accessible primary sources during this session.

#### 1.5 Power lines and poles
| Method | Cost per mile | Coverage per day | Source |
|---|---|---|---|
| Drone | $200–300 | 5–10 miles | Drone Launch Academy (28 Apr 2026, upd. 1 Jun 2026) https://dronelaunchacademy.com/resources/drone-power-line-inspection/ |
| Ground crew | $500–1,000 | 1–2 miles | same |
| Helicopter | $1,200–1,600 | 15–30 miles | same |
| Detailed transmission tower assessment | $500–2,000 per tower | — | same |

- Distribution pole inspection cost benchmark: **$361 per inspection** (FPL distribution inspection program, 2023–2032 estimate, nominal $, above-ground + excavation) (DOE/LBNL Utility Pole Maintenance and Upgrades, Sep 2024) https://www.energy.gov/sites/default/files/2024-11/111524_Utility_Pole_Maintenance_and_Upgrades.pdf . Same source: standard 40-ft wood distribution pole <$1,000; FPL wood-to-steel transmission structure replacement $26k average ($38k with overloads).
- Frequency: California CPUC General Order 165 requires periodic inspections; PG&E's 2026–2028 WMP proposes detailed inspections on **three-year cycles for all structures** plus a new aerial scan inspection for extreme/severe/high-consequence locations between detailed cycles (PG&E 2026–2028 WMP overview) https://www.pge.com/assets/pge/docs/outages-and-safety/outage-preparedness-and-support/2026-2028-wildfire-mitigation-plan-overview.pdf

#### 1.6 Telecom towers
- Traditional climber inspection: up to $4,000+ per tower (labor, insurance, safety gear); drone: $600–4,000 depending on scope (basic visual $400–700; standard with report $1,000–3,000; full visual+thermal+3D $2,000–5,000). One pilot completes 3–5 towers/day vs 1–2 for climbing crews (JOUAV, vendor, updated 3 Sep 2026) https://www.jouav.com/blog/drone-tower-inspection.html
- Frequency: TIA-222 — guyed towers every 3 years, self-supporting every 5 years, coastal/corrosive annually; FCC requires quarterly antenna-lighting inspections (JOUAV, same URL).

### 2. Cost of failure and downtime

#### 2.1 Wind
- Minor onshore blade repair ~$30,000; structural repair when no replacement blade is available ~$500,000; offshore simple repair ~$100,000; complex offshore repair $1M+ (ONYX Insight article, ~Dec 2025) https://onyxinsight.com/resources-support/articles/cut-turbine-maintenance-costs-90-percent/
- New blade ~$500,000; US blade repairs exceeded $1B "this year" (Wind Systems Magazine, 14 Dec 2025; author is ONYX Insight CEO; underlying "recent research" unnamed) https://www.windsystemsmag.com/preventable-blade-damage-costing-industry-billions/
- Blades = 37% of turbine repairs; business interruption ~$100,000/day during a structural failure; replacement blade $300,000–500,000 with >12-month lead time; whole turbine >$5M (POWER, 14 Aug 2026; same author) https://www.powermag.com/the-billion-dollar-blind-spot-in-wind-turbine-maintenance/
- Baseline O&M: US all-in OpEx fell from ~$80/kW-yr (late-1990s projects) to ~$40/kW-yr (2018 projects), with a $33–59/kW-yr range for 2015–2018 vintages; turbine O&M (scheduled + unscheduled) is the single largest OpEx component (LBNL, Wiser/Bolinger/Lantz, Jan 2019) https://eta-publications.lbl.gov/sites/default/files/opex_paper_final.pdf
- **Inference:** at ~$40/kW-yr, a 3 MW turbine's total OpEx is ~$120k/yr; one structural blade repair (~$500k) equals ~4 years of that turbine's entire OpEx. Early detection that keeps a $30k repair from becoming a $500k one is a ~17x payoff.

#### 2.2 Solar
Raptor Maps 2026 Global Solar Report (dataset 373 GWdc cumulative, ~80% aerial thermography) https://pages.raptormaps.com/hubfs/Marketing%20Content%20for%20Website/2026%20Global%20Solar%20Report%20by%20Raptor%20Maps%20(compressed).pdf :
- Average equipment-driven power loss **5.08% in 2025** (5.51% in 2024; 2.36% in 2021; 2020–2024 five-year average 3.5%) — "more than double what it was 5 years ago."
- A site at the 2025 average "could be losing up to **$5,070 per MW** of annualized revenue."
- Power loss at commissioning already **4.46%** (~$4,450/MWdc/yr) — QA/QC gap at handover.
- Loss composition 2025: string faults 26.89% of observed power loss (+12.5% YoY), combiner 21.51% (+10.2% YoY), trackers ~14% (+25% YoY); inverter-caused loss fell ~40% YoY. Malfunctioning trackers affect 4.21% of DC capacity on tracker sites (>2x vs 5 years ago).
- Sites with docked autonomous drones (54 GW analyzed, 3.56x YoY): **3% average power loss vs 5.08%**, and inspected ~12x more often.
- 34.2% of substations inspected more than once in 2025 had at least one high-severity issue; fires observed on >20% of sites inspected with docked drones.
- Insurance (kWh Analytics guest chapter): attritional losses = 60.5% of claims by count; inverter failures = 55% of attritional events; hail/hurricane/flood = 8% of claims by count but larger by dollar value. >99% of US solar farms sit where there is a 10% chance of >2-inch hail nearby (kWh Analytics, Jun 2025, cited in report).
- Module non-conformance rates hit a decade-high 3.36% in 2025 (industry audits cited in report).
- Prior editions for trend: 2025 report (193 GWdc): $5,720/MWdc annualized revenue loss in 2024 (SolarQuarter, 17 Feb 2026) https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ ; 2024 report: $4.6B global annual revenue loss, power loss 3.13%→4.47% (Raptor Maps press, 13 Mar 2024) https://raptormaps.com/press/global-solar-report-finds-4b-annual-revenue-loss-in-solar-industry
- Simple ROI illustration: 5% undetected yield loss on a 10 MW site earning $800k/yr = $40k/yr lost vs a $1,500–5,000 inspection (Averroes, 14 Jul 2026).

#### 2.3 Bridges
- ARTBA: $467B to make all identified repairs (state-submitted average cost data) (ARTBA 2025). FHWA: ~$248B (2024 $) to address all deficiencies; at current spending the backlog could fall ~90% over 20 years (CRS R47194, 20 Apr 2026) https://www.everycrsreport.com/files/2026-04-20_R47194_0f1eb5d76408f7e7cdb8913617fe19331d4b69f5.html — **contradiction: ARTBA ($467B) ≈ 1.9x FHWA ($248B); methodologies differ (ARTBA counts all "needing repair" incl. fair-condition work; FHWA counts deficiencies).**
- Francis Scott Key Bridge collapse (26 Mar 2024): Maryland "could lose up to $15 million a day in revenue"; 12.4M vehicles/yr (~35,000/day); Port of Baltimore ≈ $3.3B personal income and ~$400M taxes/yr (Maryland Chamber, 28 Mar 2024) https://www.mdchamber.org/2024/03/28/understanding-key-bridge-collapse-impact/ ; port handled ~50M tons / ~$80B of goods, 15,000 direct and 100k–140k indirect jobs; port blocked ~11 weeks (Brookings, 28 Mar 2024) https://www.brookings.edu/articles/economic-impact-of-the-baltimore-bridge-collapse
- Generic per-day bridge closure cost by bridge class: **not found** in a citable 2025–2026 source.

#### 2.4 Utility storm restoration
- Duke Energy 2024 hurricanes (Debby, Helene, Milton): total restoration/rebuild ~**$2.8B net of expected insurance** ($2.6B incurred by 31 Dec 2024; $0.2B in 2025); Duke Energy Carolinas $1,150M, Progress $450M, Florida $1,150M; ~3.5M customers impacted (Duke Energy 10-K FY2024, per SEC filing) https://www.sec.gov/Archives/edgar/data/1326160/000132616025000072/Financial_Report.xlsx ; earlier estimate $2.4–2.9B systemwide, Florida $1.1–1.3B (Milton $700–850M, Helene $300–400M, Debby $60M) (WUSF, 7 Nov 2024) https://www.wusf.org/economy-business/2024-11-07/duke-energy-could-seek-pass-along-over-1-billion-hurricane-losses-customers
- Florida response scale: Milton — 1M outages, 16,000 workers, 1,560 poles replaced, 95% restored in 4 days; Helene — 800k outages, 8,600 workers, 925 poles; Debby — 350k, 3,000 workers, 320 poles; customer surcharge $21 per 1,000 kWh Mar 2025–Feb 2026 (Renewable Energy World, 30 Dec 2024) https://www.renewableenergyworld.com/power-grid/outage-management/duke-energy-seeks-1-1-billion-to-cover-hurricane-costs-in-florida/
- A search-surfaced claim that "US utilities face >$25B annually in storm-related recovery costs" **could not be found** in the page it was attributed to (Think Power Solutions, 13 Feb 2025) — do not use.

#### 2.5 Insurance claims leakage
- Claims leakage = 5–10% of all claims paid, up to $30B/yr (EPAM Systems, cited by PropertyCasualty360, 12 Feb 2024) https://www.propertycasualty360.com/2024/02/12/3-leading-causes-of-claims-leakage-in-casualty-insurance/ ; Everest Group (2022) estimated $117B savings potential from technology. EY assessments put leakage at 7–14% of spend for litigated casualty claims (search summary, EY page not fetched https://www.ey.com/en_us/insights/insurance/claims-litigation ).
- Aerial imagery reduces property inspection cost ~40% and cycle time from 10–15 to 2–3 days; claims investigation ≈ 11% of premiums (search summaries of EagleView / Insurance Innovation Reporter; not fetched) — treat as vendor claims.

### 3. Asset counts (US unless stated)
| Asset | Count | Source (date) |
|---|---|---|
| Highway bridges (>20 ft, public roads) | **624,167** (2025 NBI); 272,774 good / 309,716 fair / 41,677 poor | ARTBA 2025 Bridge Report, NBI downloaded 24 Jun 2025 https://artbabridgereport.org/reports/2025-ARTBA-Bridge-Report.pdf |
| Poor condition share | **6.7%** (vs 7.0% in 2021); 50% fair | ARTBA 2025; CRS Apr 2026 gives 43.7% good / 49.6% fair / 6.7% poor |
| Bridges needing major repair or replacement | 220,295 (35%), of which 74,472 should be replaced | ARTBA 2025 |
| Daily crossings of poor bridges | 163M | ARTBA 2025 |
| Prior year | 623,147 bridges; 42,067 poor; 221,800 need repair; 168.5M crossings | ARTBA press, 30 Aug 2024 https://www.artba.org/news/new-data-shows-slow-steady-progress-repairing-americas-bridges/ |
| Wind turbines | **77,379** across 45 states + GU/PR | USGS USWTDB v9.0, 26 Jun 2026 https://energy.usgs.gov/uswtdb/ |
| Global offshore wind | 92.5 GW cumulative end-2025; +9.3 GW in 2025; avg new turbine 10.3 MW; >50 GW under construction; 420 GW by 2035 | GWEC, 9 Jun 2026 https://www.gwec.net/news/gwec-report-fast-track-offshore-wind-to-help-prevent-future-energy-crises |
| US offshore wind | 174 MW operating as of 6 Mar 2025 (Block Island 30 MW/5 turbines; South Fork 132 MW); Vineyard Wind 1 construction completed 13 Mar 2026; federal stop-work order Dec 2025, injunction Jan 2026 | Wikipedia (secondary) https://en.wikipedia.org/wiki/Offshore_wind_power_in_the_United_States ; FERC-based outlook adds 4,155 MW offshore in 12 months to Feb 2027 (Electrek, 27 Apr 2026) https://electrek.co/2026/04/27/eia-80-gw-of-new-solar-wind-storage-capacity-coming-in-2026/ |
| Utility-scale solar additions | 30.8 GW (2024), 27.2 GW (2025), record 43.4 GW forecast 2026 (51% of 86 GW total additions); Texas 40% | EIA via PV Tech, 26 Feb 2026 https://www.pv-tech.org/eia-us-add-record-43-4gw-new-utility-scale-solar-pv-capacity-2026/ |
| Utility-scale solar share of US capacity | 12.7% (Feb 2026) → 15.5% (Feb 2027 projected); small-scale solar 60.2 GW | Electrek, 27 Apr 2026 (FERC/SUN DAY) |
| Cumulative US utility-scale PV capacity (GW) | **Not found** — SEIA and EIA pages returned 403 during this session | — |
| Transmission lines | ~240,000 miles of high-voltage lines (National Grid); ~600,000 miles total transmission incl. lower voltages and ~5.5M miles distribution (galvanizeit.org, search summary, not fetched) | https://ngridenergyworld.com/faq-items/how-many-miles-of-power-lines-are-there-in-the-u-s/ ; https://galvanizeit.org/hot-dip-galvanized-steel-for-power-infrastructure/the-current-grid/transmission-distribution |
| Utility poles | ~**180M** total, ~130M wood; wood pole life ~60 yrs class-dependent | DOE/LBNL, Sep 2024 https://www.energy.gov/sites/default/files/2024-11/111524_Utility_Pole_Maintenance_and_Upgrades.pdf |
| Cell towers | 154,800 purpose-built towers; 248,050 macro sites; 197,850 outdoor small cells; 802,500 indoor nodes (end-2024); $63B industry spend; 368,750 FTE | WIA, 7 May 2025 https://wia.org/wireless-infrastructure-by-the-numbers-2024/ ; end-2025: 158,500 towers / 254,850 macro sites (WIA via Drone Launch Academy, 12 May 2026) https://dronelaunchacademy.com/resources/drone-cell-tower-inspection/ |

### 4. Analyst market-size estimates (and why most are not our market)
| Report | Figures | Definition / methodology caveat | Source |
|---|---|---|---|
| Drone Inspection & Monitoring (The Business Research Company) | $15.5B (2025) → $18.44B (2026) → $36.94B (2030), 19% CAGR; North America largest and fastest | "Revenues earned by entities providing drone inspection and monitoring **services**… including related goods and equipment"; segments software/services/platform/infrastructure but no share given | https://www.thebusinessresearchcompany.com/report/drone-inspection-and-monitoring-global-market-report |
| AI Vision Inspection (Precedence Research) | $32.06B (2025) → $39.38B (2026) → $250.62B (2035), 22.83% CAGR; hardware 39%; North America 36% | Manufacturing QC (electronics 27%, automotive, F&B); **no infrastructure segment** | https://www.precedenceresearch.com/ai-vision-inspection-market |
| AI-Based Visual Inspection Software (Global Growth Insights) | $0.81B (2025) → $0.92B (2026) → $2.90B (2035), 13.6% CAGR; APAC 45%, NA 25% | Applications: automotive 35%, general manufacturing 30%, medical devices 20%, electronics 15% — **zero infrastructure/energy** | https://www.globalgrowthinsights.com/market-reports/ai-based-visual-inspection-software-market-101542 |
| US wind-turbine drone inspection | $478M (2025), 14% CAGR | Vendor citing unnamed source | skyvisor.ai (vendor) https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ |
| NDT services | $3.3B now → ~$7B by 2035 | ASNT Economic Impact Report 2025 (summary page) | https://foundation.asnt.org/ndt-research/workforce-development |

**Inference:** analyst reports disagree by two orders of magnitude because they measure different things (flight services vs. factory vision systems). None isolates "AI grading/prioritization software for physical infrastructure." Judges will discount a top-down TAM slide; use a bottom-up model (§7).

### 5. Regulatory and policy drivers
1. **NBIS 2022 / SNBI (bridges).** Final rule published 6 May 2022, effective 6 Jun 2022; some sections (reduced-interval provisions, NSTM team-leader rules) effective 6 Jun 2024 (FHWA overview) https://www.fhwa.dot.gov/bridge/pubs/P1-NBIS-SNBI-Final-Rule-Overview_toHPA_V2_508v2.pdf . Risk-based intervals (24/48/72 months) require documented condition and risk data; FHWA's RIA projects $4.6M–$195.4M savings over 2022–2031 assuming 30–65% of eligible bridges move to 48-month intervals (govinfo). SNBI: agencies must begin verification/collection of new SNBI data by 1 Jan 2026 and submit a complete SNBI dataset by **15 Mar 2028** (FHWA overview; FHWA Q&A via search). FHWA position on drones: supplement only, cannot replace on-site qualified inspection (govinfo). **Implication:** software that emits SNBI-coded element condition data and a documented risk rationale directly supports the 48/72-month extension business case.
2. **IIJA bridge money and the funding cliff.** Bridge Formula Program $27.5B FY2022–26 ($5.5B/yr); Bridge Investment Program $12.5B (ARTBA 2025) — CRS reports BIP at $15.8B (includes additional appropriations; note the discrepancy). States had committed $11.7B (55%) of $21.2B available by mid-2025, funding >6,000 projects; BIP awarded $7.8B across 87 grants (ARTBA 2025). Federal bridge obligations averaged $12.0B/yr FY2022–25 vs $9.8B before (CRS, 20 Apr 2026). **IIJA authorization ends 30 Sep 2026 — six days from today** — surface-transportation reauthorization status should be checked before the pitch (JPC Engineering blog via search, not fetched: https://www.jpcengineering.com/jpc-blog/the-2026-infrastructure-funding-cliff-what-happens-when-the-iija-expires ).
3. **IEC TS 62446-3:2017 (PV thermography).** Current edition (Ed. 1.0, 15 Jun 2017; stability date 2026) https://webstore.iec.ch/en/publication/28628 . Defines valid inspection conditions, camera/resolution, reporting and anomaly classification. Insurers and lenders reference it; kWh Analytics argues high-frequency inspection programs let "asset owners and insurers alike intervene earlier" (Raptor Maps 2026 report, insurance chapter). NFPA 70B (electrical maintenance) was mentioned by vendors but not verified here.
4. **Wind blade standards.** IEC 61400-5:2020 with 2025 amendment; DNV-ST-0376 revised 2024 with recommended in-service inspection intervals (search summaries via Hornbill Technology https://hornbill.technology/end-of-warranty-wind-turbine-blade-inspection/ and GlobalSpec; not fetched). End-of-warranty inspections are a recurring commercial trigger (same source).
5. **California wildfire mitigation (CPUC GO 165, SB 901 WMPs via OEIS).** PG&E 2026–2028 WMP: 1,077 miles undergrounding, >700 miles overhead upgrades, >10,000 Gridscope sensors, 220,000 poles inspected aerially in 2024–2025, detailed inspections on 3-year cycles for all structures plus new aerial scans in extreme/severe/high-risk areas; 72% reduction in reportable ignitions with EPSS (PG&E press release 7 Apr 2025 https://www.pge.com/en/newsroom/currents/safety/three-year-wildfire-mitigation-plan-builds-upon-proven-layers-of.html ; WMP overview PDF). SCE: >200,000 annual drone inspections, >400,000 assets in high-fire-risk areas, ~10,000 inspections/week at peak, 100+ two-person drone teams, ~800 Priority-1 structures found per year with 24-hour repair, AI models for crossarm deterioration (SCE, 12 Aug 2021) https://energized.edison.com/stories/drones-and-ai-future-is-now-for-sces-aerial-inspections . **Implication:** California IOUs already generate hundreds of thousands of structure images a year and must prioritize P1/P2 repairs — a direct fit for grading + prioritization software; note the SCE figures are 2021 and should be refreshed.
6. **Insurance regulation of aerial imagery/AI.** NAIC Model Bulletin on AI Systems (Dec 2023) plus aerial-imagery bulletins from 13 states (AL, DE, LA, ME, MD, MA, MI, NH, NC, PA, RI, TN, WV) require current/accurate imagery, distinguish cosmetic vs. risk defects, specific adverse-action reasons, and dispute mechanisms (Carrier Management, 25 Mar 2026) https://www.carriermanagement.com/features/2026/03/25/286006.htm . **Implication:** explainable, severity-graded outputs with evidence crops are becoming a compliance requirement, not just a feature.
7. **FAA Part 108 (BVLOS).** NPRM published 7 Aug 2025; comments closed 6 Oct 2025 (~3,100–4,000 comments); final rule sent to OIRA 10 Jul 2026; FAA hopes to publish by end-2026, implementation likely 2027 (Flight Brief, 14 Sep 2026 https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026 ; Airdata 2026 via search https://airdata.com/blog/2026/part-108 ). Until then BVLOS needs Part 107 waivers. **Implication:** linear-infrastructure image volumes (lines, pipelines) will step up in 2027; a software-only company is not blocked by Part 108 timing, but its customers' capture volumes are.
8. **Telecom.** TIA-222 3-/5-year structural inspection cycles; FCC quarterly lighting checks (JOUAV, Sep 2026).

### 6. Labor shortage
- NDT: US workforce ~89,800; Level II technicians are 55% of the workforce and the scarcest tier; market $3.3B → ~$7B by 2035 (ASNT Foundation summary of 2024–2025 reports) https://foundation.asnt.org/ndt-research/workforce-development . Nearly 30% of certified NDT personnel are over 55 and retirements are accelerating (ASNT 2023 report, via Quality Magazine, 1 May 2025) https://www.qualitymag.com/articles/98711-behind-the-scenes-behind-schedule-ndts-workforce-shortage . Search-surfaced claims of "40% retiring within a decade," "~6,000 openings/yr (BLS)," and "2–3 openings per certified tech" were not verified on fetched pages.
- Bridge inspectors: Minnesota ~600 inspectors for >20,000 bridges (MnDOT, 2017). National inspector head-count and shortage figures: **not found**.
- Solar O&M: US solar jobs +12% vs installed capacity +286% over five years; average technician responsible for 70% more MW than in 2019 (IREC National Solar Jobs Census 2024, cited in Raptor Maps 2026 report).
- Drone pilots: a search summary cited 499,336 FAA Part 107 remote pilots as of 1 Mar 2026, but the FAA pages returned 403 and secondary pages did not contain the figure — **unverified**. FAA's Aerospace Forecast projected 472,269 certified remote pilots by 2028 (Drone U, undated) https://www.thedroneu.com/blog/part-107-license-guide/ . **Inference:** pilot supply is not the constraint; qualified defect graders (NDT Level II, PE-supervised bridge inspectors, blade engineers) are.
- Utility crews: SCE fielded 100+ two-person drone teams (2021); Duke mobilized 16,000 workers for Milton (2024) — surge labor is the expensive, scarce input in disasters.

### 7. TAM / SAM / SOM framing for an AI grading + prioritization software wedge (Inference — all assumptions explicit)

**Positioning:** we sell the analysis layer (small-VLM triage → heavy-VLM grading → prioritized work queue) to asset owners, O&M contractors, engineering inspection firms and insurers. We do not fly drones or sell hardware. Pricing anchors observed in market: analytics add-on $100–300/turbine (UAVsphere); AI-assisted full solar report $500–1,200/MW vs $300–500 thermal-only (UAVsphere) → implied analysis value ~$200–700/MW; distribution pole inspection $361 each (DOE/LBNL) → AI triage at 1–2% of that is $4–7/structure.

**TAM (global, software/analytics layer of physical-infrastructure inspection):**
- Anchor: drone inspection & monitoring services $15.5B (2025) → $36.94B (2030) (TBRC). Assumption: software/analytics captures 15–25% of service revenue (assumption; TBRC lists software as a segment without a share). → **~$2.3–3.9B (2025) growing to ~$5.5–9.2B (2030).**
- Cross-check by value-at-stake: Raptor Maps' $5,070/MW/yr loss × their own 373 GWdc analyzed = ~$1.9B/yr of revenue leakage visible in one vendor's dataset alone; global solar >3 TW in 2026 (Raptor Maps 2026) implies >$15B/yr theoretical solar underperformance — the software TAM is bounded by a share of *that* recoverable value, not by inspection fees.

**SAM (US, our five asset classes, software layer only, current inspection cadences):**
| Segment | Volume basis | Cadence | Software price assumption | Annual SAM |
|---|---|---|---|---|
| Wind blades | 77,379 turbines (USGS) | 1–2 inspections/yr (skyvisor 6–12 mo) | $100–300/turbine-inspection (UAVsphere add-on) | $8M–$46M |
| Utility-scale solar | ~150 GW US utility-scale PV (**assumption**; cumulative figure not sourced — replace with EIA/SEIA number) | 1/yr | $200–700/MW (implied analysis premium) | $30M–$105M |
| Bridges | 624,167 bridges (ARTBA) → ~312k routine inspections/yr at 24 months | every 24 mo | $150–400 per inspection for imagery grading + SNBI-coded report support | $47M–$125M |
| Distribution/transmission structures | 180M poles (DOE); assume 1/3 inspected per year (PG&E 3-yr cycle) = 60M structure-inspections; assume 25% imaged | 3-yr detailed | $4–7 per imaged structure | $60M–$105M |
| Telecom towers | 158,500 towers (WIA 2025); TIA-222 3–5 yr + annual visual → ~50k–160k inspections/yr | 3–5 yr | $100–300 | $5M–$48M |
| Underwater (bridge substructure, piers, hulls) | ~624k bridges over water subset unknown; **not sized** | 60–72 mo | — | not sized |
| **Total US SAM (software layer)** | | | | **≈ $0.15–0.43B/yr**, call it **$0.2–0.6B** allowing for insurers and disaster-surge work not in the table |

**SOM (36 months):** 10–20 design-partner accounts (2–3 wind O&M/ISPs, 3–5 solar asset managers or O&M firms, 2–3 state DOT engineering consultants, 1–2 California/Florida utilities, 1 renewables insurer) at $50k–$500k ACV → **$1–5M ARR**, i.e. ~1% of SAM. This is deliberately conservative; the team should state it as such and show the path via disaster-surge contracts (Duke's $2.8B 2024 storm bill shows the budget exists).

**Why this framing survives Q&A:** every volume number is a public count (NBI, USWTDB, WIA, DOE); every cadence is regulatory (NBIS, GO 165, TIA-222) or standard practice (annual blade/PV inspection); the only invented inputs are our price points, which are bracketed by observed vendor add-on pricing. The upside case is value-based pricing against avoided failures ($5,070/MW/yr solar; $30k→$500k blade escalation; P1 fire-risk structures), not per-inspection fees.

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| US highway bridges (NBI) | 624,167 | https://artbabridgereport.org/reports/2025-ARTBA-Bridge-Report.pdf | NBI 24 Jun 2025 |
| Bridges in poor condition | 41,677 (6.7%) | same | 2025 |
| Bridges needing major repair/replacement | 220,295 (35%); 74,472 to replace | same | 2025 |
| Cost to make all identified bridge repairs (ARTBA) | $467B | same | 2025 |
| Bridge deficiency backlog (FHWA) | ~$248B (2024 $) | https://www.everycrsreport.com/files/2026-04-20_R47194_0f1eb5d76408f7e7cdb8913617fe19331d4b69f5.html | 20 Apr 2026 |
| Daily crossings of poor bridges | 163M | ARTBA 2025 PDF | 2025 |
| Bridge Formula Program / Bridge Investment Program | $27.5B / $12.5B (ARTBA); BIP $15.8B (CRS) | ARTBA 2025 PDF; CRS R47194 | 2025 / 2026 |
| Federal bridge obligations | $12.0B/yr FY2022–25 vs $9.8B prior | CRS R47194 | 20 Apr 2026 |
| NBIS routine interval | 24 mo default; 48 mo Method 1; up to 72 mo Method 2 | https://www.govinfo.gov/content/pkg/FR-2022-05-06/html/2022-09512.htm | 6 May 2022 |
| SNBI full dataset deadline | 15 Mar 2028 | https://www.fhwa.dot.gov/bridge/pubs/P1-NBIS-SNBI-Final-Rule-Overview_toHPA_V2_508v2.pdf | FHWA overview |
| NBIS RIA savings from extended intervals | $4.6M–$195.4M over 2022–2031 (7% disc.) | govinfo NBIS final rule | 6 May 2022 |
| Conventional large-bridge inspection (Blatnik) | ~$59,000 (8 days, 4 snoopers) vs $20,000 UAS (5 days) | https://mdl.mndot.gov/_flysystem/fedora/2023-02/201718ts.pdf | Aug 2017 |
| Snooper truck rental / purchase | $2,500/day / >$600,000 | https://www.flyability.com/blog/bridge-inspections | undated |
| WSDOT UBIT team rate | $542.41/hr | https://app.leg.wa.gov/ReportsToTheLegislature/Home/GetPDF?fileName=High+Cost+Bridge+Inspection+Cost+Comparison_18ee4d7a-0591-4fef-b707-e9bcd8dc9197.pdf | undated |
| Underwater inspection w/ report (WSDOT / private) | $2,265 / $1,920 (unit ambiguous) | same | undated |
| Rope-access blade inspection | $1,500–3,000/turbine; 3–6 hrs | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ (vendor) | ©2026 |
| Drone blade inspection | $300–600/turbine; 15–45 min; 18–25/day | same (vendor) | ©2026 |
| Drone blade inspection incl. advanced | $300–1,000; thermal $2,000–4,000+; analytics +$100–300 | https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost (vendor) | 5 May 2025 |
| Turbine downtime cost | $3,000–17,000/turbine/day | skyvisor.ai (vendor) | ©2026 |
| Minor blade repair / structural repair | ~$30,000 / ~$500,000 | https://onyxinsight.com/resources-support/articles/cut-turbine-maintenance-costs-90-percent/ | ~Dec 2025 |
| Offshore blade repair | ~$100,000 simple; $1M+ complex | same | ~Dec 2025 |
| US blade repair spend | >$1B in 2025; blades 37% of repairs | https://www.powermag.com/the-billion-dollar-blind-spot-in-wind-turbine-maintenance/ | 14 Aug 2026 |
| Business interruption during structural failure | ~$100,000/day | same | 14 Aug 2026 |
| Replacement blade | $300,000–500,000; >12-mo lead | same | 14 Aug 2026 |
| US wind OpEx | ~$80/kW-yr (1990s) → ~$40/kW-yr (2018); range $33–59 | https://eta-publications.lbl.gov/sites/default/files/opex_paper_final.pdf | Jan 2019 |
| US wind turbines | 77,379 | https://energy.usgs.gov/uswtdb/ | 26 Jun 2026 (v9.0) |
| Global offshore wind | 92.5 GW; +9.3 GW 2025; 10.3 MW avg turbine | https://www.gwec.net/news/gwec-report-fast-track-offshore-wind-to-help-prevent-future-energy-crises | 9 Jun 2026 |
| US offshore wind operating | 174 MW (Mar 2025) | https://en.wikipedia.org/wiki/Offshore_wind_power_in_the_United_States | 6 Mar 2025 |
| Solar avg power loss | 5.08% (2025); 5.51% (2024); 2.36% (2021) | https://pages.raptormaps.com/hubfs/Marketing%20Content%20for%20Website/2026%20Global%20Solar%20Report%20by%20Raptor%20Maps%20(compressed).pdf | 2026 edition |
| Solar revenue loss | up to $5,070/MW/yr; $4,450/MWdc at commissioning (4.46%) | same | 2026 |
| Docked-drone sites power loss | 3% vs 5.08%; ~12x inspection frequency; 54 GW | same | 2026 |
| Loss composition | string 26.89%, combiner 21.51%, tracker ~14% | same | 2026 |
| Prior-year solar revenue loss | $5,720/MWdc (2024, 193 GWdc) | https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ | 17 Feb 2026 |
| Global solar revenue loss (2024 report) | $4.6B/yr | https://raptormaps.com/press/global-solar-report-finds-4b-annual-revenue-loss-in-solar-industry | 13 Mar 2024 |
| Solar insurance claims | attritional 60.5% by count; inverter 55% of attritional; hail/hurricane/flood 8% by count | Raptor Maps 2026 (kWh Analytics chapter) | 2026 |
| Drone PV thermal inspection price | $150–500/MW | https://averroes.ai/blog/how-much-does-drone-solar-panel-inspection-cost-2024 (vendor) | 14 Jul 2026 |
| PV inspection: thermal-only vs full report | $300–500/MW vs $500–1,200/MW | https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know (vendor) | 5 May 2025 |
| IEC TS 62446-3 edition | 2017 Ed. 1.0; stability date 2026 | https://webstore.iec.ch/en/publication/28628 | 15 Jun 2017 |
| Utility-scale solar additions | 27.2 GW (2025); 43.4 GW forecast 2026 | https://www.pv-tech.org/eia-us-add-record-43-4gw-new-utility-scale-solar-pv-capacity-2026/ | 26 Feb 2026 |
| Power line patrol cost | drone $200–300/mi; ground $500–1,000; helicopter $1,200–1,600 | https://dronelaunchacademy.com/resources/drone-power-line-inspection/ | 28 Apr 2026 |
| Transmission tower detailed assessment | $500–2,000/tower | same | 28 Apr 2026 |
| US high-voltage transmission miles | ~240,000 | https://ngridenergyworld.com/faq-items/how-many-miles-of-power-lines-are-there-in-the-u-s/ | undated |
| US utility poles | ~180M (~130M wood) | https://www.energy.gov/sites/default/files/2024-11/111524_Utility_Pole_Maintenance_and_Upgrades.pdf | Sep 2024 |
| Distribution pole inspection cost (FPL) | $361/inspection | same | Sep 2024 |
| PG&E aerial pole inspections | 220,000 poles (2024–25); 1,077 mi undergrounding | https://www.pge.com/en/newsroom/currents/safety/three-year-wildfire-mitigation-plan-builds-upon-proven-layers-of.html | 7 Apr 2025 |
| PG&E inspection cadence | detailed 3-yr cycle all structures + aerial scans high-risk | https://www.pge.com/assets/pge/docs/outages-and-safety/outage-preparedness-and-support/2026-2028-wildfire-mitigation-plan-overview.pdf | 2026–28 WMP |
| SCE drone inspections | >200,000/yr; >400,000 assets; ~800 P1/yr | https://energized.edison.com/stories/drones-and-ai-future-is-now-for-sces-aerial-inspections | 12 Aug 2021 |
| Duke Energy 2024 storm cost | ~$2.8B net of insurance; 3.5M customers | https://www.sec.gov/Archives/edgar/data/1326160/000132616025000072/Financial_Report.xlsx | FY2024 10-K |
| Duke Florida storm cost | $1.1–1.3B; Milton $700–850M | https://www.wusf.org/economy-business/2024-11-07/duke-energy-could-seek-pass-along-over-1-billion-hurricane-losses-customers | 7 Nov 2024 |
| Milton response | 1M outages; 16,000 workers; 1,560 poles | https://www.renewableenergyworld.com/power-grid/outage-management/duke-energy-seeks-1-1-billion-to-cover-hurricane-costs-in-florida/ | 30 Dec 2024 |
| Key Bridge closure | up to $15M/day; 12.4M vehicles/yr | https://www.mdchamber.org/2024/03/28/understanding-key-bridge-collapse-impact/ | 28 Mar 2024 |
| Port of Baltimore | ~$80B goods/yr; 15,000 direct jobs | https://www.brookings.edu/articles/economic-impact-of-the-baltimore-bridge-collapse | 28 Mar 2024 |
| Claims leakage | 5–10% of claims paid; up to $30B/yr | https://www.propertycasualty360.com/2024/02/12/3-leading-causes-of-claims-leakage-in-casualty-insurance/ | 12 Feb 2024 |
| States with aerial-imagery insurance bulletins | 13 | https://www.carriermanagement.com/features/2026/03/25/286006.htm | 25 Mar 2026 |
| Cell towers / macro sites | 154,800 / 248,050 (2024); 158,500 / 254,850 (2025) | https://wia.org/wireless-infrastructure-by-the-numbers-2024/ ; https://dronelaunchacademy.com/resources/drone-cell-tower-inspection/ | May 2025; May 2026 |
| Tower inspection cost | climber up to $4,000+; drone $600–4,000 | https://www.jouav.com/blog/drone-tower-inspection.html (vendor) | 3 Sep 2026 |
| TIA-222 cycles | 3 yr guyed / 5 yr self-supporting | same | 3 Sep 2026 |
| Drone inspection & monitoring market | $15.5B (2025); $18.44B (2026); $36.94B (2030); 19% CAGR | https://www.thebusinessresearchcompany.com/report/drone-inspection-and-monitoring-global-market-report | 2026 |
| AI vision inspection market (mfg) | $32.06B (2025); $250.62B (2035) | https://www.precedenceresearch.com/ai-vision-inspection-market | 2025/26 |
| AI visual inspection software (mfg) | $0.81B (2025); $2.90B (2035) | https://www.globalgrowthinsights.com/market-reports/ai-based-visual-inspection-software-market-101542 | 2025/26 |
| NDT workforce | 89,800; Level II 55%; ~30% over 55 | https://foundation.asnt.org/ndt-research/workforce-development ; https://www.qualitymag.com/articles/98711-behind-the-scenes-behind-schedule-ndts-workforce-shortage | 2024–25; 1 May 2025 |
| Solar labor gap | jobs +12% vs capacity +286% (5 yrs); +70% MW per tech | Raptor Maps 2026 (IREC) | 2026 |
| FAA Part 108 status | at OIRA; final expected end-2026; ~4,000 comments | https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026 | 14 Sep 2026 |
| Part 108 NPRM dates | published 7 Aug 2025; comments closed 6 Oct 2025; OIRA 10 Jul 2026 | https://airdata.com/blog/2026/part-108 (search summary) | 2026 |

---

## Implications for our product / edge

1. **Sell the analysis, not the flight.** Capture cost has already collapsed (drone vs rope 5–10x; drone vs helicopter 4–8x). The remaining margin — and the labor bottleneck — is in grading and prioritizing what the images show. UAVsphere's separately priced "$100–300 per turbine analytics" line item proves customers already pay for this layer.
2. **Lead with avoided-failure economics.** Solar: 5.08% average loss ≈ $5,070/MW/yr; sites inspected ~12x more often lose 3%. Wind: $30k repair vs $500k structural repair vs $100k/day interruption. Bridges: $248–467B backlog to prioritize. These are the numbers that make "prioritization" a revenue line, not a nice-to-have.
3. **Build to the regulatory data schema.** NBIS 48/72-month extensions and SNBI (deadline 15 Mar 2028) demand element-level, defensible condition data; FHWA says drones may *supplement*, so position as inspector decision-support that outputs SNBI-coded findings, not "autonomous inspection." Same logic for IEC TS 62446-3 anomaly classes (solar) and CPUC GO 165 / WMP priority codes (utilities).
4. **Explainability is becoming mandatory on the insurance side.** NAIC + 13 state bulletins require specific, non-cosmetic, disputable reasons for adverse actions — a graded, evidence-cropped, severity-scored output is a compliance asset. kWh Analytics explicitly wants high-frequency inspection programs as risk signals.
5. **Disaster mode is the wedge into utilities.** Duke's 2024 storms cost ~$2.8B and needed 16,000 surge workers; SCE and PG&E already run 200k+ aerial inspections a year with P1/24-hour repair SLAs. A triage engine that ranks thousands of post-storm or post-fire images by severity within hours plugs into an existing, funded workflow.
6. **Two-stage VLM matches the cost structure.** Cheap first-pass "damage present?" on every image, heavy grading only on flagged ones, mirrors how utilities already tier inspections (aerial scan → detailed) and how Raptor Maps reports docked-drone sites gain from *frequency*. Frequency economics only work if per-image analysis is near-free.
7. **Time your go-to-market to policy.** Part 108 (late 2026/2027) will raise linear-infrastructure image volumes; IIJA expires 30 Sep 2026 so bridge-owner budgets face uncertainty — target state DOT consultants and utilities/renewables first, DOTs second.
8. **Do not repeat the vendors' TAM slide.** Judges will have seen "$15.5B drone inspection market." Show the bottom-up SAM (~$0.2–0.6B US software layer) with public counts and regulatory cadences, then the value-at-stake upside.

## Open questions / gaps

- **Cumulative US utility-scale PV capacity (GW)** — SEIA and EIA pages returned 403; the SAM row for solar uses an unsourced ~150 GW placeholder that must be replaced.
- **Commercial diver / dive-team day rates** and ROV day rates — not found in primary sources; only a vendor's unsourced "68% cheaper" claim.
- **Per-bridge average routine inspection cost** for small/medium bridges — only a large-bridge worked example (MnDOT $59k) and hourly rates (WSDOT) found; NBIS RIA per-inspection unit costs were not extracted.
- **Annual US utility storm-restoration spend** — the "$25B/yr" claim could not be located in its cited source; only Duke's 2024 figures are solid.
- **Global onshore wind turbine count** — not sourced (GWEC gives GW and annual turbine installs, not fleet count).
- **FAA Part 107 pilot count** — 499,336 (1 Mar 2026) surfaced in search but not verifiable on fetched pages (FAA 403).
- **Bridge inspector head-count/shortage nationally** — not found; only Minnesota (600 inspectors, 2017).
- **IEC TS 62446-3 exact irradiance/resolution thresholds** — from secondary summaries, not the standard text.
- **DNV-ST-0376 (2024) recommended blade inspection intervals** — search summary only.
- **SCE inspection volumes** are from 2021; PG&E WMP total budget not extracted from the overview PDF.
- **Insurer-side numbers** for renewables/infrastructure claims leakage specifically (vs. general P&C) — not found.
- **IIJA reauthorization status** as of 24 Sep 2026 — must be checked before the pitch.

## Sources

1. https://artbabridgereport.org/reports/2025-ARTBA-Bridge-Report.pdf — ARTBA 2025 Bridge Report (NBI data 24 Jun 2025): bridge counts, condition, $467B repair estimate, IIJA bridge funding status.
2. https://artbabridgereport.org/ — ARTBA Bridge Report landing page (41,600+ poor bridges; 163M crossings; 55% of formula funds committed).
3. https://www.artba.org/news/new-data-shows-slow-steady-progress-repairing-americas-bridges/ — ARTBA 2024 release (623,147 bridges; 42,067 poor; 221,800 need repair).
4. https://www.everycrsreport.com/files/2026-04-20_R47194_0f1eb5d76408f7e7cdb8913617fe19331d4b69f5.html — CRS R47194 (20 Apr 2026): FHWA $248B backlog, IIJA bridge programs, federal obligations.
5. https://www.govinfo.gov/content/pkg/FR-2022-05-06/html/2022-09512.htm — NBIS Final Rule (6 May 2022): inspection intervals, RIA savings, UAS language.
6. https://www.fhwa.dot.gov/bridge/pubs/P1-NBIS-SNBI-Final-Rule-Overview_toHPA_V2_508v2.pdf — FHWA NBIS/SNBI overview: effective dates, SNBI 15 Mar 2028 deadline.
7. https://www.fhwa.dot.gov/bridge/nbis.cfm — FHWA NBIS page (rule history).
8. https://mdl.mndot.gov/_flysystem/fedora/2023-02/201718ts.pdf — MnDOT Technical Summary (Aug 2017): Blatnik Bridge $59k conventional vs $20k UAS; MN inspector counts.
9. https://insideunmannedsystems.com/advancing%E2%80%A8-bridge-inspection/ — Inside Unmanned Systems (2 Mar 2021): snooper costs, 40–60% savings.
10. https://www.flyability.com/blog/bridge-inspections — Flyability: snooper $2,500/day, >$600k purchase; NBIS 24/24/60-month baseline.
11. https://app.leg.wa.gov/ReportsToTheLegislature/Home/GetPDF?fileName=High+Cost+Bridge+Inspection+Cost+Comparison_18ee4d7a-0591-4fef-b707-e9bcd8dc9197.pdf — WSDOT high-cost bridge inspection rate comparison (UBIT and underwater rates).
12. https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ — SkyVisor (vendor, 2026): rope vs drone blade inspection costs, downtime, cadence.
13. https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost — UAVsphere (5 May 2025): drone blade inspection price ranges, analytics add-on.
14. https://onyxinsight.com/resources-support/articles/cut-turbine-maintenance-costs-90-percent/ — ONYX Insight (~Dec 2025): blade repair cost tiers.
15. https://www.windsystemsmag.com/preventable-blade-damage-costing-industry-billions/ — Wind Systems (14 Dec 2025): $30k repair, ~$500k blade, >$1B US blade repairs.
16. https://www.powermag.com/the-billion-dollar-blind-spot-in-wind-turbine-maintenance/ — POWER (14 Aug 2026): 37% of repairs, $100k/day interruption, blade lead times.
17. https://eta-publications.lbl.gov/sites/default/files/opex_paper_final.pdf — LBNL (Jan 2019): US wind OpEx $/kW-yr benchmarks.
18. https://energy.usgs.gov/uswtdb/ — USGS USWTDB v9.0 (26 Jun 2026): 77,379 turbines.
19. https://catalog.data.gov/dataset/united-states-wind-turbine-database-ver-8-2-december-2025 — data.gov USWTDB record (v9.0 June 2026).
20. https://www.gwec.net/news/gwec-report-fast-track-offshore-wind-to-help-prevent-future-energy-crises — GWEC Global Offshore Wind Report (9 Jun 2026).
21. https://en.wikipedia.org/wiki/Offshore_wind_power_in_the_United_States — US offshore wind operating capacity and project status (secondary).
22. https://electrek.co/2026/04/27/eia-80-gw-of-new-solar-wind-storage-capacity-coming-in-2026/ — Electrek (27 Apr 2026): FERC/SUN DAY capacity additions and solar share.
23. https://www.pv-tech.org/eia-us-add-record-43-4gw-new-utility-scale-solar-pv-capacity-2026/ — PV Tech (26 Feb 2026): EIA 43.4 GW 2026 solar forecast; 2024–25 actuals.
24. https://pages.raptormaps.com/hubfs/Marketing%20Content%20for%20Website/2026%20Global%20Solar%20Report%20by%20Raptor%20Maps%20(compressed).pdf — Raptor Maps 2026 Global Solar Report (373 GWdc): power loss, $/MW, docked drones, insurance chapter.
25. https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ — SolarQuarter (17 Feb 2026) on Raptor Maps 2025 report ($5,720/MWdc).
26. https://raptormaps.com/press/global-solar-report-finds-4b-annual-revenue-loss-in-solar-industry — Raptor Maps 2024 press ($4.6B global loss).
27. https://averroes.ai/blog/how-much-does-drone-solar-panel-inspection-cost-2024 — Averroes (14 Jul 2026): $150–500/MW, throughput, ROI example.
28. https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know — UAVsphere (5 May 2025): thermal vs full-report PV pricing.
29. https://webstore.iec.ch/en/publication/28628 — IEC TS 62446-3:2017 webstore record (current edition).
30. https://www.epj-pv.org/articles/epjpv/full_html/2025/01/pv20250040/pv20250040.html — EPJ Photovoltaics 2025 study on irradiance/altitude in PV thermography (search summary).
31. https://dronelaunchacademy.com/resources/drone-power-line-inspection/ — Drone Launch Academy (28 Apr 2026): line patrol cost per mile by method.
32. https://ngridenergyworld.com/faq-items/how-many-miles-of-power-lines-are-there-in-the-u-s/ — National Grid: ~240,000 miles HV transmission.
33. https://galvanizeit.org/hot-dip-galvanized-steel-for-power-infrastructure/the-current-grid/transmission-distribution — AGA: 600k miles transmission, 5.5M miles distribution (search summary).
34. https://www.energy.gov/sites/default/files/2024-11/111524_Utility_Pole_Maintenance_and_Upgrades.pdf — DOE/LBNL (Sep 2024): 180M poles, inspection and replacement costs.
35. https://wia.org/wireless-infrastructure-by-the-numbers-2024/ — WIA (7 May 2025): tower and site counts, industry spend.
36. https://dronelaunchacademy.com/resources/drone-cell-tower-inspection/ — Drone Launch Academy (12 May 2026): WIA end-2025 tower counts.
37. https://www.jouav.com/blog/drone-tower-inspection.html — JOUAV (3 Sep 2026): tower inspection costs, TIA-222 cycles.
38. https://www.pge.com/en/newsroom/currents/safety/three-year-wildfire-mitigation-plan-builds-upon-proven-layers-of.html — PG&E press release (7 Apr 2025): 2026–28 WMP headline numbers.
39. https://www.pge.com/assets/pge/docs/outages-and-safety/outage-preparedness-and-support/2026-2028-wildfire-mitigation-plan-overview.pdf — PG&E 2026–2028 WMP overview: 3-year detailed cycle, aerial scans, GO 165.
40. https://energized.edison.com/stories/drones-and-ai-future-is-now-for-sces-aerial-inspections — SCE (12 Aug 2021): 200k+ drone inspections/yr, AI models, P1 counts.
41. https://energized.edison.com/stories/sce-drone-inspections-help-reduce-wildfire-risk — SCE (14 Jul 2020): weekly inspection volumes.
42. https://www.sec.gov/Archives/edgar/data/1326160/000132616025000072/Financial_Report.xlsx — Duke Energy 10-K FY2024: ~$2.8B storm costs (via search summary).
43. https://www.wusf.org/economy-business/2024-11-07/duke-energy-could-seek-pass-along-over-1-billion-hurricane-losses-customers — WUSF (7 Nov 2024): Duke storm cost estimates.
44. https://www.renewableenergyworld.com/power-grid/outage-management/duke-energy-seeks-1-1-billion-to-cover-hurricane-costs-in-florida/ — Renewable Energy World (30 Dec 2024): per-storm response metrics.
45. https://www.thinkpowersolutions.com/blogs/storm-damage-assessment/ — Think Power Solutions (13 Feb 2025): checked; does NOT contain the "$25B/yr" claim.
46. https://www.mdchamber.org/2024/03/28/understanding-key-bridge-collapse-impact/ — Maryland Chamber (28 Mar 2024): $15M/day, traffic, port figures.
47. https://www.brookings.edu/articles/economic-impact-of-the-baltimore-bridge-collapse — Brookings (28 Mar 2024): port tonnage, jobs.
48. https://www.propertycasualty360.com/2024/02/12/3-leading-causes-of-claims-leakage-in-casualty-insurance/ — PropertyCasualty360 (12 Feb 2024): claims leakage 5–10%, $30B.
49. https://www.ey.com/en_us/insights/insurance/claims-litigation — EY: leakage 7–14% in litigated claims (search summary).
50. https://www.carriermanagement.com/features/2026/03/25/286006.htm — Carrier Management (25 Mar 2026): NAIC bulletin and 13 state aerial-imagery bulletins.
51. https://www.thebusinessresearchcompany.com/report/drone-inspection-and-monitoring-global-market-report — TBRC drone inspection & monitoring market ($15.5B → $36.94B).
52. https://www.precedenceresearch.com/ai-vision-inspection-market — Precedence Research AI vision inspection ($32.06B, manufacturing).
53. https://www.globalgrowthinsights.com/market-reports/ai-based-visual-inspection-software-market-101542 — Global Growth Insights AI visual inspection software ($0.81B).
54. https://foundation.asnt.org/ndt-research/workforce-development — ASNT Foundation: NDT workforce 89,800, market $3.3B → $7B.
55. https://www.qualitymag.com/articles/98711-behind-the-scenes-behind-schedule-ndts-workforce-shortage — Quality Magazine (1 May 2025): ~30% of NDT personnel over 55.
56. https://www.thedroneu.com/blog/part-107-license-guide/ — Drone U: FAA forecast 472,269 remote pilots by 2028.
57. https://www.theflightbrief.com/articles/faa-part-108-bvlos-update-september-2026 — Flight Brief (14 Sep 2026): Part 108 at OIRA, end-2026 target.
58. https://airdata.com/blog/2026/part-108 — Airdata (2026): Part 108 NPRM/comment/OIRA dates (search summary).
59. https://www.deepskyiq.com/underwater-rov-submerged-asset-intelligence — Deep Sky IQ (vendor): ROV vs diver cost claims, marine inspection cadences (unsourced).
60. https://hornbill.technology/end-of-warranty-wind-turbine-blade-inspection/ — Hornbill Technology: IEC 61400-5 / DNV-ST-0376 references (search summary).
61. https://www.jpcengineering.com/jpc-blog/the-2026-infrastructure-funding-cliff-what-happens-when-the-iija-expires — JPC Engineering: IIJA expiry 30 Sep 2026 (search summary).
