# Competitive Landscape: AI / Drone Inspection of Wind Turbine Blades and Solar PV Farms

Research angle: `competitors_wind_solar` | Written: 2026-09-24 (Origin Weekend Fall 2026, Prompt D) | Method: 16 web searches + ~60 page fetches (the session's web-search budget ran out mid-task; later gaps were filled with direct page fetches of URLs already surfaced). Facts carry a URL; my own conclusions are labelled **Inference:**. Where a number comes only from a search-result snippet and the page itself could not be fetched, it is marked *(snippet; page not fetched)*.

---

## Summary

- **This is a funded, consolidating market with clear incumbents, not white space.** Zeitview (ex-DroneBase) raised $60M in March 2025 and says it inspected 60,000 turbines in 2025 and 600 GW of PV cumulatively with an 80,000-pilot network; SkySpecs raised $20M (Goldman Sachs Alternatives, March 2025), claims 745,000+ blades inspected and "65% of North American blades monitored annually"; Raptor Maps' cumulative solar dataset is 373 GWdc; Clobotics claims 180,000+ blade inspections in 40+ countries; Cornis claims 37,000+ inspections and 10M processed images. (Sources in profiles below.)
- **Business models converge on "service + SaaS platform", and almost nobody publishes prices.** Zeitview, SkySpecs, Raptor Maps, Sulzer Schmid, Above, Cyberhawk, Clobotics, Optelos all quote custom/enterprise pricing. The only public per-asset software prices found are Scopito's: EUR 160/turbine (AI-analysed), EUR 80/turbine (self-analysed), EUR 20/asset solar, EUR 16/asset power lines. Market service benchmarks: US $300-600 per turbine for a standard visual drone inspection (up to $2,000-4,000 with LiDAR/LPS testing); solar thermal $300-500/MW ($150-200/MW for non-IEC-compliant flyovers).
- **Damage grading is semi-standardised but proprietary in practice.** Wind: a de facto 5-level severity scale (Cat 1 cosmetic -> Cat 5 stop turbine) with repair windows, explicitly "no universal industry standard". Solar: IEC TS 62446-3 defines Class 1/2/3 thermal abnormalities (roughly dT >= 10 C = scheduled repair, >= 40 C = immediate) with 600 W/m2 minimum irradiance; a revised edition was expected fall 2025. Incumbents say "severity ratings" on their marketing pages but do not publish definitions.
- **Public accuracy claims are rare and unaudited.** Clobotics: ">95% defect recall, >98% major-defect recall, 1 mm". Sterblue (2020, grid): 98% on 5 of 35 defect types. Zeitview published a crack dataset (9,107 high-severity cracks, 988 sites, 195 blade models) but no metrics on its marketing page. Raptor Maps, SkySpecs, Sulzer Schmid, Above, Cyberhawk: no quantified accuracy found.
- **Turnaround is mostly unpublished.** Found: Sterblue 2 days (2020), generic solar guides 24-72 h for AI report / 3-5 business days end-to-end, Sitemark "<60 minutes for C&I" (self-claim). Zeitview, SkySpecs, Raptor Maps: no public SLA found.
- **Documented weaknesses exist but are thin.** Zeitview Trustpilot 2.6/5 on only 4 reviews (platform outage, slow support, pilot pay under $80/job, a contractor non-payment claim). Competitor commentary (Sitemark, self-serving): Zeitview = "limited AI analytics, primarily data acquisition"; Raptor Maps = "O&M only, limited global support". Optelos reviews: cluttered UI, slow processing, "slightly expensive for SME firms". SkySpecs: "narrow scope" (blades only), Glassdoor mentions of executive churn and layoffs. Generic tools (DroneDeploy, DJI FlightHub, Pix4D) have no solar-specific AI and require manual classification.
- **Structural gaps a new entrant can attack:** (1) single-asset silos - blade-only (SkySpecs, Sulzer Schmid, Cornis, Nearthlab, Clobotics) or solar-only (Raptor Maps, Above, Sitemark); only Zeitview/Aerodyne/Cyberhawk span sectors, and they are service-heavy; (2) no incumbent publishes explainable, standard-referenced grading rationale per finding; (3) on-prem/edge processing is rare (Scopito enterprise licence, SkyVisor "on-premises data control"); (4) small ISPs/drone service providers and sub-100-MW owners are priced into either custom enterprise quotes or AI-less generic tools; (5) thermal+RGB fusion is treated as a solar-only feature, and X-ray/underwater imagery is outside every wind/solar vendor's scope.
- **Foundation-model / VLM approaches are academic so far, not shipped.** 2025-2026 papers: RAG-augmented VLM zero-shot blade inspection (100% on a 30-image test set - too small to mean much), few-shot VLM with hierarchical retrieval (98.3% accuracy with 15 samples/class, claimed +13.3 pts over strongest supervised baseline), VLM fine-tuning for damage description plus 5-level repair priority with a "quality guard" agent (bridges, May 2026), DINOv2-based blade defect recognition (2025). No commercial wind/solar vendor found advertising a VLM cascade. **Inference:** the cascade idea is technically timely and un-occupied commercially, but judges will ask for measured precision/recall, not paper numbers.
- **The pain is real and quantified by third parties:** blade replacement EUR 500k to EUR 2-3M per blade; 0.5-1% of blades replaced per year; ~65% of blade repairs unscheduled; lightning damage >$100M/yr to the wind industry (60% blade losses); turbine downtime $3,000-17,000 per turbine per day; solar equipment-driven underperformance up 214% in 5 years, ~$10B unrealised revenue in 2024 (Raptor Maps).

---

## Detailed findings

### 1. Market context and who buys

- Wind turbine drone inspection market: USD 418.5M (2025) -> USD 478.8M (2026) -> USD 1,838.3M (2036), CAGR 14.4% (Fact.MR, updated 2026-09-03). https://www.factmr.com/report/wind-turbine-drone-inspection-market
  - Contradiction: a Drone Launch Academy article says the *U.S.* market "will top $478 million in 2025" at 14% CAGR *(snippet)* - the same figure Fact.MR gives for *global* 2026. Treat market-size numbers as order-of-magnitude only.
- Wind O&M spend was "around USD 15 billion" in 2019; 57% of repairs unplanned; leading-edge erosion cuts AEP "up to 5%" and can start after 2 years (Sulzer Schmid, 2022-10-13). https://www.sulzerschmid.ch/2022/10/tracking-blade-damage-progression-to-enable-predictive-maintenance-can-generate-huge-savings-and-increase-annual-energy-production/
- Blade economics (Perceptual Robotics via Zag Daily, 2025-12-16): blade replacement EUR 500,000 to EUR 2-3M; ~65% of blade repairs unscheduled; 0.5-1% of blades replaced annually. https://zagdaily.com/zag-air/wind-turbine-inspections-show-how-drones-work-at-scale/
- Lightning: >$100M/yr damage to the wind industry, 60% of it blade losses; a 200 m turbine averages 1.2 strikes/yr; ~25% of US wind farms see >= 1 strike per turbine per year (Voliro article in Wind Systems, 2025-03-15). https://www.windsystemsmag.com/drone-inspections-can-prevent-million-dollar-lightning-losses/
- Downtime: $3,000-17,000 per turbine per day (Drone Launch Academy, 2026-05-05). https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/
- Solar: equipment-driven underperformance up 214% over 5 years; "potentially US$10 billion in unrealized revenue" in 2024, from 193 GWdc analysed (Raptor Maps 2025 Global Solar Report). https://raptormaps.com/resources/global-solar-report-2025 ; 2024 report: ~180% rise in fault-related underperformance since 2019, up to $4.6B potential annual loss in 2023; 2026 report: 373 GWdc analysed, >3 GW of installed autonomous docked-drone capacity documented. https://raptormaps.com/resources/reports
- Aerial inspection frequency per solar asset "has grown by 70% year-over-year" (Raptor Maps Solar Sentry page). https://raptormaps.com/products/raptor-solar-sentry
- **Buyer types observed across vendor pages:** asset owners/IPPs (Vestas, EDF, Enel, Orsted, RWE, Iberdrola, Vattenfall appear as logos), OEMs (Vestas Europe campaign for Sulzer Schmid; Siemens Gamesa for Clobotics), independent service providers/ISPs and O&M contractors, drone service providers (Zeitview's 80k pilot network; Above's 500+ data-collection partners), and utilities (FPL for Percepto). Sulzer Schmid explicitly lists "OEMs, owners and operators and field operation partners". https://www.sulzerschmid.ch/offering/
- **Regulatory friction:** most blade inspection still requires visual line of sight; BVLOS permissions are "site-specific"; most Perceptual Robotics customers are wind technicians, not drone pilots (Zag Daily, 2025-12-16). Percepto holds a nationwide FAA BVLOS waiver (Nov 2022) and a 1-pilot-to-30-drones waiver (Nov 2023). https://dronedj.com/guides/percepto/

### 2. Company profiles

Format per company: what they sell | who buys | pricing | funding/traction | accuracy | grading | turnaround | weaknesses.

#### 2.1 Zeitview (formerly DroneBase) - Santa Monica, US
- **Sells:** "Insights" AI platform + managed inspection service via pilot network; solar (procurement, construction monitoring, thermal O&M, serial-ID mapping, shading), wind (external blade, internal blade crawlers, tower/nacelle, LPS testing, onshore/offshore), utilities, telecom, properties. https://www.zeitview.com/wind ; https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/
- **Buyers:** asset owners/OEMs (Vestas, EDF Renewables, Enel named on wind page). Also recruits drone pilots as a gig marketplace.
- **Pricing:** quote-based; Sitemark characterises it as "per-inspection/per-site service-based". https://www.sitemark.com/research/best-solar-inspection-software/
- **Funding/traction:** $60M round led by Climate Investment (announced 2025-03-04/07); prior $55M Series D two years earlier; investors Valor, USV, Upfront, Euclidean, Energy Transition Ventures, Hearst, Y Combinator; 200,000+ assets inspected in 2024 across 80 countries, "doubled" in 2024. https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ Wind page: 60,000 turbines inspected in 2025, >500 GW renewable capacity serviced, 40 countries. https://www.zeitview.com/wind Solar page: 600 GW PV inspected cumulative, 80,000 pilots. https://www.zeitview.com/solar
- **Accuracy:** "award-winning" barely-visible crack detection; ZVCD dataset 9,107 high-severity cracks, 988 locations, 195 blade models from 34 manufacturers; tile-classification approach with ResNet-18 / EfficientNet-B3 / MobileNetV3, "emphasis on high precision to avoid missed cracks"; **no precision/recall published on the page** (paper arXiv 2407.07186). https://www.zeitview.com/resource/wind-turbine-crack-detection
- **Grading:** "severity and prevalence" ratings, AI + "expert analysts"; no public scale definition; no IEC 62446-3 reference on the solar page. https://www.zeitview.com/solar
- **Turnaround:** not published (API marketed as reducing turnaround). https://www.zeitview.com/wind-insights (page returned 404 on 2026-09-24)
- **Weaknesses:** Trustpilot 2.6/5, 4 reviews, all 1-star (Oct 2025: platform non-functional, could not access past missions; Aug 2025: contractor non-payment claim; Jun 2024: pilot pay "under $80 per job"; Mar 2024: contacts lacking drone expertise). Small sample, but zero positives. https://www.trustpilot.com/review/www.zeitview.com Competitor (Sitemark) framing: "limited AI analytics; primarily data acquisition service". https://www.sitemark.com/research/best-solar-inspection-software/ **Inference:** Zeitview's moat is capture logistics (pilot network), not model quality; its pilot marketplace shows margin pressure on the supply side.

#### 2.2 SkySpecs - Ann Arbor, US
- **Sells:** autonomous drone blade inspections (Foresight drones, "15 minutes per turbine"), Horizon BAM (blade asset management incl. third-party inspection ingestion, damage propagation trends, lightning monitoring, repair workflow, AEP-loss analysis, warranty tracking), Horizon CMS (drivetrain), Horizon Solar, Risk Management, repair-vendor management. https://skyspecs.com/product/inspections/ ; https://skyspecs.com/horizon-bam/ ; https://skyspecs.com/
- **Buyers:** owner-operators (Statkraft and Equinor Ventures are strategic investors). *(snippet: cbinsights)*
- **Pricing:** not public. https://energy.toolsinfo.com/tool/skyspecs
- **Funding/traction:** $20M growth round led by Goldman Sachs Alternatives, closed March 2025 *(BusinessWire page 403; snippet)*; total funding ~$142M *(snippet: robotics.press/cbinsights)*; 745,000+ blades inspected, 130 GW served, "65% of North American blades monitored annually", "$42B in assets under contract", 6 offices (Ann Arbor, Graz, Vejle, Hyderabad, Dublin, Novi Sad). https://skyspecs.com/ 275,000 turbine inspections globally. https://skyspecs.com/product/inspections/
- **Strategy:** "deliberate transition from inspection services toward a software-driven O&M optimization stack"; new CTO 2025 *(snippets)*.
- **Accuracy:** none published; inspections page describes "categorization and expert commentary", i.e. human analysts.
- **Grading:** not published on the Horizon page; "prioritized repair campaigns to maximize ROI". https://skyspecs.com/horizon-bam/
- **Turnaround:** not published.
- **Weaknesses:** "narrow scope... specifically designed for wind turbine blade management" (energy.toolsinfo.com); Glassdoor reviews mention "excessive churn... on the Executive level, leading to layoffs" *(snippet)*. **Inference:** strongest wind-blade data moat in North America; weakest on multi-asset and on transparent AI.

#### 2.3 Sulzer & Schmid Laboratories (3DX) - Switzerland
- **Sells:** hybrid SaaS + hardware + services: 3DX Blade Platform (cloud analytics), autonomous drones with proprietary 3DX Payload and AutoPilot, annotation services, campaign management, optional field execution. Two tiers: "3DX Inspection Manager" (capture + processing + annotation, 6-month access) and "3DX Asset Manager" (unlimited access, trend monitoring, fleet reporting, repair recommendations). 30-min downtime per turbine; half-day pilot training; Vestas Europe campaign (2021). https://www.sulzerschmid.ch/offering/ Listed in the DJI Enterprise ecosystem. https://enterprise.dji.com/ecosystem/sulzerschmid-3dx
- **Buyers:** "OEMs, owners and operators and field operation partners" (i.e. it licenses ISPs to fly).
- **Pricing:** quote only.
- **Funding:** not found.
- **Accuracy:** AI partnership with NNAISENSE announced 2019-09-03 to "flag all areas of concern", with "damage categories and severity levels" planned for later versions; no metrics. https://www.marinelink.com/news/advanced-ai-engine-automated-blade-damage-470216
- **Grading:** platform can "establish damage categories and severity levels"; Damage Progression module (2022-07-12) builds a "damage chain" time-series per defect. https://www.sulzerschmid.ch/2022/07/press-release-new-3dx-damage-progression-module/
- **Weaknesses:** "Focuses narrowly on blade inspection rather than full-turbine assessment" (Robotics & Automation News, 2025-12-26). https://roboticsandautomationnews.com/2025/12/26/best-5-wind-turbine-inspection-software-platforms/97853/

#### 2.4 Aerodyne Group - Malaysia (global)
- **Sells:** "DT3" drone-tech/data-tech/digital-transformation services; "vertikaliti" AI cloud asset-management platform; WTG and solar inspection among many verticals. Claims 45 countries, 752,700 critical assets inspected, 722,000 km inspected, 8,300 MW solar inspected (as of Dec 2022). https://aerodyne.group/
- **Note:** Its Danish blade unit Aerodyne AtSite (blade specialists since 2013, "industry-standard defect categorization and reporting solutions used across Europe") was acquired by Clobotics on 2020-04-03. https://investindk.com/cases/clobotics-acquires-aerodyne-atsite-to-expand-its-wind-industry-capabilit
- **Pricing / accuracy / grading / turnaround:** not found. Market reports say it launched real-time AI flagging in 2024 *(snippet; not verified)*.
- **Inference:** generalist service provider; AI is a feature of a services business, not a product.

#### 2.5 Cyberhawk - UK
- **Sells:** drone inspection services + iHawk data platform; wind: ultra-high-res visual + thermal blade inspection, defects "logged, sized, and categorized against OEM standards" to support warranty claims; solar: full-array thermal + visual. 500,000+ inspections, 17+ years, 40 countries, 300+ customers, 11,000+ iHawk users; managed drone-in-a-box and AVIATE advisory. https://thecyberhawk.com/ ; https://thecyberhawk.com/renewable-energy
- **Traction:** 55% revenue increase FY2024; Phase One global partnership *(snippet; not verified)*.
- **Pricing / accuracy / turnaround:** not public. **Grading:** against OEM standards (implies per-OEM schemes, not one open scale).

#### 2.6 Cornis - France
- **Sells:** wind-only multi-modal inspection: Cornis Drone App (20-min inspection), IntraBlade internal (2 h), Panoblade ground-based telescope (35 min), Quick Control (10 min ground), LPS drone inspection (45 min), Blade Manager SaaS. 37,000+ inspections, 6,500+ offshore, "45% of offshore wind turbine inspections in Europe", 10M+ processed images, 710,000+ defects analysed; customers ABB, EDF, ENGIE, Iberdrola, Orsted, RWE, Siemens, SSE, Statkraft, TotalEnergies, Vestas, Voltalia. https://cornis.fr/ AI trained on 5M+ images (WindEurope 2025 listing). https://event.businessfrance.fr/wind-europe-2025/cornis-inspection-blade-data-management/
- **Pricing / accuracy / grading:** not public; "100% blade surface coverage" claim only.
- **Inference:** the ground-based Panoblade option is a real differentiator vs drone-only players for low-cost frequent checks.

#### 2.7 Sterblue - France
- **Sells:** flight-guidance + ML anomaly detection + automatic reports; wind turbine inspection time cut from 80+ min to <40 min; reports within 2 days; Enedis grid pilot found "5 out of 35 types of defects... with 98% accuracy" at 50% of original cost; 11 employees (2020); "pay-as-you-use" model per Sterblue site *(snippet; site refused connection)*. https://enterprise.dji.com/news/detail/grid-and-wind-turbine-inspections-made-easy-by-drone-solutions ; https://www.sterblue.com/industrial-applications/wind-turbine
- **Status 2025-2026:** not verified (site unreachable during research). **Gap.**

#### 2.8 Raptor Maps - Boston, US (solar only)
- **Sells:** solar digital-twin platform, AI thermal anomaly detection (module cracking, tracker misalignment, BOS defects, vegetation/fire risk, erosion, wiring, structural), production analytics normalising SCADA/DAS, RS Mobile offline technician app, warranty/serial tracking, 3D/4D construction monitoring; Raptor Solar Sentry robotics-agnostic drone-in-a-box "deployed across 4GW+". Data collection via Remote Operations (docked drones), Turnkey (vetted third-party pilots) or Self-Perform. https://raptormaps.com/products/solar-inspections-analytics ; https://raptormaps.com/products/raptor-solar-sentry ; https://apps.list.solar/tools/raptor-maps/
- **Buyers:** IPPs, O&Ms, EPCs (utility-scale and C&I). https://raptormaps.com/
- **Pricing:** custom enterprise SaaS "based on site count, capacity, and selected platform features"; "no transparent public pricing". https://apps.list.solar/tools/raptor-maps/
- **Funding:** $22M Series B, April 2022 (pv magazine; page blocked, title verified). https://www.pv-magazine.com/2022/04/15/solar-drone-inspection-provider-raptor-maps-secures-22-million-series-b/ Later rounds: not found.
- **Traction:** 373 GWdc cumulative analysed (2026 report), 67 GWdc in 2024 alone. https://raptormaps.com/resources/reports
- **Accuracy:** none quantified ("more accurate reporting"). One customer: remediation started "25% faster" with Sentry. https://raptormaps.com/
- **Grading:** IEC TS 62446-3 adherence (per Sitemark's comparison); severity tiers not on public pages. https://www.sitemark.com/research/best-solar-inspection-software/
- **Turnaround:** "fast turnaround", no SLA.
- **Weaknesses:** requires high-quality aerial imagery and drone access, implementation complexity, training needed (apps.list.solar); "O&M only (no construction/commissioning), limited global support, requires supplemental tools" (Sitemark, self-serving); zero reviews on SourceForge. https://sourceforge.net/software/product/Raptor-Maps/

#### 2.9 Above Surveying (SolarGain) - UK (solar only)
- **Sells:** SolarGain cloud platform + mobile app (component-level digital twin, data-source agnostic), thermographic inspection with dual-camera drones, topographic mapping, digital construction management. 10,000+ sites, 900+ companies, 500+ data-collection partners, NPS 71+, ISO 9001/14001/45001. https://www.abovesurveying.com/
- **Pricing:** not listed; demo required (Drone Life NJ) *(snippet)*.
- **Accuracy:** unquantified ("higher accuracy and more precision" customer quote). **Grading / turnaround:** not public.

#### 2.10 Sitemark - Belgium (solar; added as a relevant competitor)
- **Sells:** AI solar lifecycle platform (construction -> O&M), "25+ anomaly types", C&I results "<60 minutes", "310+ GWp across 1,100+ companies"; custom pricing. Its self-published comparison (2026-05-26) is the best available written critique of Raptor Maps, Zeitview, DroneDeploy (~$300/mo, "no anomaly categorization"), DJI FlightHub 2 (free, "no AI... data hosted in mainland China"), Pix4D ($175-300/mo, no solar intelligence). https://www.sitemark.com/research/best-solar-inspection-software/

#### 2.11 Scopito - Denmark
- **Sells:** pay-per-asset inspection data platform with AI fault detection, severity levels, PDF reports; enterprise licence includes volume discounts, custom development and **on-premise installation**; 14-day trial; "trusted by 7,000+ companies". **Prices:** EUR 160/turbine analysed, EUR 80/turbine self-analysed, EUR 20/asset solar, EUR 16/asset power lines, EUR 50/asset buildings. https://scopito.com/wind-turbine-inspection-software/ ; https://www.spotsaas.com/product/scopito/pricing
- **Buyers:** inspection companies and operators (small and large).
- **Weaknesses:** Capterra: 0 reviews, feature checklist lacks "Reporting/Analytics" and "Performance Metrics" flags. https://www.capterra.com/p/213899/Scopito/ **Inference:** Scopito is the closest thing to a transparent, small-operator-friendly price anchor; our pricing should be benchmarked against EUR 80-160/turbine.

#### 2.12 Optelos - US (asset-agnostic visual data management)
- **Sells:** visual inspection data management + AI, geolocates/correlates multi-source imagery, 3D point-cloud twins; "flexible, project-based pricing with no long-term commitment". https://optelos.com/platform-overview/
- **Reviews:** GetApp 4.8/5 on 13 reviews; cons: pricing opacity, small review base, many advanced features unused. https://www.getapp.com/business-intelligence-analytics-software/a/optelos/ Review-site commentary: UI "over cultured" with many fields, processing "sometimes takes time", "slightly expensive for SME firms" *(snippet)*.

#### 2.13 Skydio - US (autonomy hardware, not analytics)
- **Sells:** X10/X10D autonomous drones ($16,000-25,000 per unit) with 64MP narrow + 48MP tele + FLIR Boson+ thermal, Nvidia Jetson onboard; Skydio Dock; software Asset Command, Ops Center, 3D Scan; Skydio Extend for third-party analytics. Wind is not explicitly addressed in its asset-inspection FAQ. https://www.skydio.com/solutions/asset-inspection/faq
- **Funding:** $110M Series F at $4.4B post-money (2026-04-23), ~$672M total raised (article) - a search snippet said $825M; contradiction noted; "hundreds of millions" revenue, 60,000+ drones shipped, 3,800+ enterprise customers, $52M US Army order for ~3,000 X10D. https://dronexl.co/2026/04/23/skydio-110m-series-f-44-billion-valuation/
- **Defect detection:** via partners - Levatas (thermal anomalies, gauges, cracks/corrosion/spills; 2024-06-10) https://www.skydio.com/blog/elevate-your-inspections-with-ai-powered-safety-security-and-asset-maintenance-inspections and Qii.AI (wind farm inspection, North America) *(snippet; page refused connection)* https://nawindpower.com/qii-ai-skydio-partner-on-automated-infrastructure-inspections-with-drone-tech
- **Inference:** Skydio is a capture partner/channel, not a competitor: its Extend API is a distribution path for an analytics layer like ours.

#### 2.14 Percepto - Israel/US (drone-in-a-box)
- **Sells:** Air Max / Air Mobile drones, AIM autonomous inspection management, "AI-powered thermal and RGB analytics", turnkey with "white-glove" remote ops; end-to-end AI remote inspection for electric utilities launched 2025-03-26 (FPL, "hundreds" of drones planned). https://www.renewableenergyworld.com/power-grid/grid-modernization/autonomous-drone-company-releases-end-to-end-ai-powered-remote-inspection-solution-at-distributech/ ; solar high-altitude approvals; nationwide BVLOS waiver. https://dronedj.com/guides/percepto/
- **Funding:** >$120M total; $67M Series C June 2023 (Koch Disruptive Technologies). https://dronedj.com/guides/percepto/
- **Pricing / accuracy / grading:** not public. **Inference:** sells to large utilities and mines; irrelevant for small operators; another potential capture partner.

#### 2.15 Voliro - Switzerland (contact/NDT drone)
- **Sells:** Voliro T tilt-rotor drone with interchangeable NDT payloads; wind LPS full-circuit testing "5x faster", "up to 50%" cheaper, 20-30 min per turbine (blog) / 45-50 min per 3-blade turbine (CVA case study, 81 turbines; traditional aerial-platform testing ~EUR 5,000/turbine, >EUR 400k per fleet round). https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ ; https://voliro.com/case-study/wind-turbine-lps-inspection-drone-italy-cva/
- **Funding/traction:** Series A extension to $23M total (2025-06-16; Cherry Ventures, noa, UBS debt); 40+ customers, 17 countries; 100+ contact inspections monthly; subscription option exists.
- **Inference:** complementary (electrical LPS test vs. our visual grading); no visual-AI competition.

#### 2.16 Nearthlab - South Korea
- **Sells:** autonomous blade-inspection drones (Nearth Wind Basic on DJI M20: 1 mm defects; Pro on M600: 0.3 mm), ~15-min inspection, Zoomable data platform (licensed to ONYX Insight for North America, 2023-03-23), NearthWIND Mobile plug-and-play for in-house inspections. https://dronelife.com/2021/08/26/drone-inspections-for-wind-turbines-in-as-little-as-15-minutes-korean-drone-software-company-nearthlab/ ; https://dronelife.com/2023/03/23/drones-for-wind-turbine-inspection-onyx-insight-and-nearthlab/
- **Funding:** $10M seed (2021); total ~$42.3M; latest "Series C - III" $0.72M on 2025-08-14 from POSCO Capital *(snippet: Tracxn/Crunchbase)*; deployments in 30+ countries *(snippet)*. https://www.crunchbase.com/organization/nearthlab
- **Inference:** the tiny 2025 round suggests slower momentum; its UST profile title now leads with public safety/defence.

#### 2.17 Clobotics - Shanghai (global)
- **Sells:** IBIS autonomous inspection (15 min/turbine), IRIS platform ("defect annotation with precise location mapping & severity rating", "operator-ready findings & priorities"), SPARROW robotic leading-edge repair (first offshore robotic blade repair 2023; 27 min/blade, 8 blades/day). 180,000+ blade inspections, 40+ countries; customers include Vattenfall, Siemens Gamesa, RWE, Orsted, Iberdrola. **Accuracy claims:** blade classification 99%, segmentation 98%, defect recall >95% overall / >98% major defects, "1 mm defect accuracy", human review cut from 1.5 h to 25 min per turbine. https://clobotics.com/industries/wind/
- **Funding:** not found. Acquired Aerodyne AtSite (Denmark) 2020-04-03. https://investindk.com/cases/clobotics-acquires-aerodyne-atsite-to-expand-its-wind-industry-capabilit
- **Inference:** the most complete "inspect -> grade -> repair" loop in wind; the only vendor publishing recall numbers. China HQ may be a procurement obstacle for US utilities (NDAA-type concerns) - inference, not sourced.

#### 2.18 Other 2025-2026 entrants and adjacent players
- **vHive (Israel):** named "best wind turbine inspection platform" in a Dec 2025 roundup (fully automated capture -> AI classification -> cloud reports). https://roboticsandautomationnews.com/2025/12/26/best-5-wind-turbine-inspection-software-platforms/97853/ Its own roundup (2025-12-28) body could not be fetched.
- **Perceptual Robotics (UK, Dhalion):** 5,000+ inspections in 18 countries in the past year; AI + specialist off-site analysis. https://zagdaily.com/zag-air/wind-turbine-inspections-show-how-drones-work-at-scale/
- **SkyVisor (France/US):** 4K capture, auto-flight, AI pre-filtering ("no defect is missed"), "on-premises data control", Light/Pro/Expert/Custom plans, no public prices, no grading scheme or accuracy published (Aug 2025). https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/
- **Unleash Live, Droneperhour, OpenWindPower:** listed in the same Dec 2025 roundup; Droneperhour targets small operators with a "lighter, more affordable" mobile-first tool.
- **Levatas, Qii.AI:** analytics layers on Skydio imagery (see 2.13).
- **Averroes.ai:** manufacturing visual-AI vendor whose solar guide (2026-07-14) claims "98.5%+ accuracy, <2% false positives" for AI vs "60-80%" for manual thermal analysis - vendor marketing, unverified. https://averroes.ai/blog/drone-solar-panel-inspection-guide
- **Generic mapping tools** (DroneDeploy ~$300/mo, Pix4D $175-300/mo, DJI FlightHub 2 free): no asset-specific AI, manual classification. https://www.sitemark.com/research/best-solar-inspection-software/

#### 2.19 Foundation-model / VLM work (academic; no commercial vendor found)
- **Zhang, Zhou, Imani, Tang - "Seeing the Unseen: Towards Training-Free / Zero-Shot Inspection for Wind Turbine Blades Using Knowledge-Augmented VLMs"** (arXiv 2510.22868; submitted 2025-10-26, revised 2026-08-01): RAG over technical docs + reference images + guidelines feeding a VLM; 100% accuracy on **30** labelled images (Clopper-Pearson CIs reported); the VLM without retrieval was worse; authors cite difficulty acquiring verified blade imagery. https://arxiv.org/abs/2510.22868
- **Few-shot VLM with hierarchical retrieval for blade inspection** (Results in Engineering, 2026): 98.3% classification accuracy, 0.862 Dice with 15 training samples per class, "+13.3%" over the strongest supervised baseline *(abstract snippet; full page 403)*. https://www.sciencedirect.com/science/article/pii/S2590123026022152
- **Few-shot visual reasoning via RAG + VLM** (IFAC-PapersOnLine, 2025). https://www.sciencedirect.com/science/article/pii/S2405896325029192
- **Yasuno - "Fine-Tuning VLMs for Understanding Current Damage and Scoring Priority with Quality Guard Agent"** (arXiv 2605.27452, 2026-05-24): LLaVA-1.5-7B + QLoRA on Japanese bridge inspection records -> natural-language damage description -> rule-based **5-level repair priority index**; Swallow-8B "quality guard" rejects low-quality VLM outputs before scoring; 2k curated samples near-optimal (2.9 h training); 800 held-out test images; 10.06 s/image inference after optimisation. https://arxiv.org/abs/2605.27452
- **DINOv2 + YOLOv5 + SCN blade defect recognition** (PMC, 2025) *(page 403; snippet)*. https://pmc.ncbi.nlm.nih.gov/articles/PMC12300182/
- **Inference:** the literature validates exactly our architecture (cheap gate -> knowledge-grounded VLM -> standard-referenced priority score with a guard), but evaluation sets are tiny (30-800 images). Our demo must show measured precision/recall on a held-out set of real public imagery, and must not quote these paper numbers as our own.

### 3. How damage is graded today

**Wind blades (visual):**
- "There is no universal industry standard for blade defect categorization, however, there is a commonly accepted best practice which classifies damages into one of five ordinal severity levels" *(search-result summary of the Balmore page)*. Balmore's definitions: Cat 1 = integrity/performance unaffected, no risk of progression, document only; Cat 2 = small risk of developing, fix at next scheduled maintenance; Cat 3 = affects integrity/performance, repair within 6-12 months; Cat 4 = structural integrity/performance compromised, repair within 3-6 months; Cat 5 = real safety risk, stop turbine, immediate repair. https://thebalmoregroup.co.uk/wind-turbine-blade-defect-categories/
- Cyberhawk grades "against OEM standards" (each OEM has its own scheme). https://thecyberhawk.com/renewable-energy
- Aerodyne AtSite (now Clobotics) "developed industry-standard defect categorization and reporting solutions used across Europe". https://investindk.com/cases/clobotics-acquires-aerodyne-atsite-to-expand-its-wind-industry-capabilit
- Sulzer Schmid: user-defined categories + severity levels + damage-chain progression. https://www.sulzerschmid.ch/2022/07/press-release-new-3dx-damage-progression-module/
- Defect types repeatedly named across vendors: leading-edge erosion, cracks (transverse/longitudinal/hairline), lightning strike damage/receptor damage, delamination, gelcoat damage, impact damage, LPS faults. Zeitview's crack paper notes hairline cracks "often resemble dirt streaks or faint scratches". https://www.zeitview.com/resource/wind-turbine-crack-detection

**Solar PV (thermal + RGB):**
- IEC TS 62446-3 (2017; revision expected fall 2025): Class 1 no abnormality; Class 2 real anomaly, roughly dT >= 10 C vs comparable modules -> scheduled repair; Class 3 safety-critical, roughly dT >= 40 C -> immediate action; minimum 600 W/m2 plane-of-array irradiance; report must log irradiance, ambient temp, wind, sky state, equipment, and per-finding location/thermal evidence/type/dT/class/recommended action. https://thermalvariations.com/learn/iec-62446-3-thermal-inspection ; 3 cm/pixel minimum geometric resolution, trained/certified operators, simplified vs detailed inspection types. https://www.vhive.ai/navigating-the-iec-standards-for-solar-farm-inspections/ ; thermal camera >= 640x512, wind >5 m/s degrades signal, actionable dT 5-10 C. https://averroes.ai/blog/drone-solar-panel-inspection-guide ; conditions log and R-JPEG radiometric delivery. https://www.airsuv.uk/drone-inspection-uk-airsuv//iec-62446-3-solar-farm-drone-inspection-uk
- Typical anomaly taxonomy (Raptor Maps, Sitemark): hot module/cell, bypass-diode failure, string outage, PID, cracked glass, soiling, tracker misalignment, vegetation/fire risk, wiring/BOS defects; Sitemark claims "25+ anomaly types". https://raptormaps.com/products/solar-inspections-analytics ; https://www.sitemark.com/research/best-solar-inspection-software/

### 4. Pricing benchmarks (what the market pays)

| Item | Price | Source (date) |
|---|---|---|
| Standard visual drone inspection, per turbine (US) | $300-600 | SkyVisor (Aug 2025) https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ ; Drone Launch Academy (May 2026) https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ |
| Same, other estimates | $300-1,000 (UAVSphere 2025); $800-2,000 "basic" (Averroes) | *(snippets)* https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost ; https://averroes.ai/blog/wind-turbine-drone-inspection-cost-breakdown-advice |
| Advanced (LiDAR / LPS test), per turbine | $2,000-4,000 | SkyVisor; Drone Launch Academy |
| Rope access, per turbine | $1,500-3,000; 3-6 h | SkyVisor; Drone Launch Academy |
| Freelance pilot day rate | $1,500-3,500 | Drone Launch Academy (May 2026) |
| Drone throughput | 18-25 turbines/day; 15-45 min each | SkyVisor; Drone Launch Academy |
| Traditional LPS test via aerial platform | ~EUR 5,000/turbine | Voliro CVA case study https://voliro.com/case-study/wind-turbine-lps-inspection-drone-italy-cva/ |
| Solar thermal survey, per MW | $300-500 | UAVSphere (2025-05-05) https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know |
| Solar full diagnostic + report, per MW | $500-1,200 | UAVSphere |
| Solar annual contract, large sites | $10,000-30,000+ | UAVSphere |
| Solar drone inspection, per MW (range) | $150-500 | Averroes (2026-07-14) https://averroes.ai/blog/drone-solar-panel-inspection-guide |
| IEC-compliant vs non-compliant flyover, per MW | $300-500 vs $150-200 | Averroes *(snippet)* |
| Low-end estimate, per MW | $50-150 | GeoWGS84 *(snippet)* https://www.geowgs84.com/post/how-much-does-a-drone-solar-panel-inspection-cost |
| Scopito software, per turbine | EUR 160 analysed / EUR 80 self-analysed | https://scopito.com/wind-turbine-inspection-software/ |
| Scopito software, per solar asset / power-line asset | EUR 20 / EUR 16 | https://www.spotsaas.com/product/scopito/pricing |
| DroneDeploy / Pix4D (generic, no asset AI) | ~$300/mo ; $175-300/mo | Sitemark comparison (2026-05-26) |
| Skydio X10 drone | $16,000-25,000 | DroneXL (2026-04-23) |

**Inference:** software analytics is a minority of the per-turbine spend; a EUR 80-160/turbine or $20-50/MW analytics price point is the visible ceiling for a pure-software entrant selling to ISPs and small owners.

### 5. Accuracy and turnaround claims - side by side

| Vendor | Accuracy claim | Turnaround claim | Source |
|---|---|---|---|
| Clobotics | >95% defect recall, >98% major-defect recall, 1 mm | review 25 min/turbine | https://clobotics.com/industries/wind/ |
| Zeitview | dataset only (9,107 cracks); no metrics on page | none | https://www.zeitview.com/resource/wind-turbine-crack-detection |
| Sterblue (2020) | 98% on 5/35 grid defect types | report in 2 days | DJI Enterprise article |
| SkySpecs | none (human "expert commentary") | none | https://skyspecs.com/product/inspections/ |
| Sulzer Schmid | none | none | https://www.sulzerschmid.ch/offering/ |
| Raptor Maps | none quantified | "fast turnaround" | https://raptormaps.com/products/solar-inspections-analytics |
| Above | none quantified | none | https://www.abovesurveying.com/ |
| Sitemark | 25+ anomaly types; C&I results <60 min (self) | <60 min (C&I) | Sitemark comparison |
| Nearthlab | 1 mm (Basic) / 0.3 mm (Pro) detectable defect size | 15 min flight | DroneLife 2021 |
| Voliro | "3-4X more defects than conventional methods" (LPS) | 20-50 min/turbine | Voliro pages |
| Generic solar AI (Averroes) | 98.5%+, <2% FP (unverified vendor blog) | 24-72 h report; 3-5 business days total | https://averroes.ai/blog/drone-solar-panel-inspection-guide |

**Inference:** nobody publishes a precision/recall table per damage category and severity, and nobody publishes a calibration or explanation artefact. That is an open, credible differentiator.

### 6. Documented weaknesses (what customers and rivals say)

- Zeitview: platform outage / lost mission history (Oct 2025), slow support, pilot pay <$80/job, non-payment claim; Trustpilot 2.6/5 (n=4). https://www.trustpilot.com/review/www.zeitview.com "Limited AI analytics; primarily data acquisition" (Sitemark). Also "multiple points of contact lacking drone expertise" (Mar 2024 review).
- SkySpecs: blades-only scope; web-only; Glassdoor: executive churn and layoffs *(snippet)*. https://energy.toolsinfo.com/tool/skyspecs
- Raptor Maps: no public pricing; needs high-quality imagery + drone infrastructure; implementation complexity; training burden; "O&M only", "limited global support" (Sitemark). https://apps.list.solar/tools/raptor-maps/
- Optelos: cluttered UI for non-technical users; slow processing; "slightly expensive for SME firms" *(snippet)*.
- Sulzer Schmid: narrow blade focus. Robotics & Automation News (2025-12-26).
- Generic tools: no asset-specific AI, manual classification; DJI data residency in China (Sitemark).
- Whole category: VLOS rules keep a trained operator on site; BVLOS is site-specific; end users are wind technicians, not pilots (Zag Daily, 2025-12-16).
- Whole category: opaque pricing everywhere except Scopito; opaque accuracy everywhere except Clobotics; no vendor found offering underwater, X-ray/radiographic or bridge grading alongside wind/solar.

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| Zeitview funding round | $60M (led by Climate Investment); prior Series D $55M | https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ | 2025-03-07 |
| Zeitview assets inspected 2024 / countries | 200,000+ / 80 | same | 2025-03-07 |
| Zeitview turbines inspected 2025 / capacity / countries | 60,000 / >500 GW / 40 | https://www.zeitview.com/wind | fetched 2026-09-24 |
| Zeitview PV inspected / pilot network | 600 GW / 80,000 pilots | https://www.zeitview.com/solar | fetched 2026-09-24 |
| Zeitview crack dataset | 9,107 cracks, 988 sites, 195 blade models, 34 OEMs | https://www.zeitview.com/resource/wind-turbine-crack-detection | paper Jul 2024 |
| Zeitview Trustpilot | 2.6/5, 4 reviews, all 1-star | https://www.trustpilot.com/review/www.zeitview.com | reviews 2024-2025 |
| SkySpecs round | $20M led by Goldman Sachs Alternatives | https://www.businesswire.com/news/home/20250319813255/en/SkySpecs-Raises-%2420m-to-Fuel-Global-Growth-and-Innovation (403; snippet) | 2025-03-19 |
| SkySpecs total funding | ~$142M (snippet) | https://www.cbinsights.com/company/skyspecs | 2025 |
| SkySpecs scale | 745,000+ blades; 130 GW; 65% of NA blades/yr; $42B assets under contract; 275,000 inspections; 15 min/turbine | https://skyspecs.com/ ; https://skyspecs.com/product/inspections/ | fetched 2026-09-24 |
| Raptor Maps Series B | $22M | https://www.pv-magazine.com/2022/04/15/solar-drone-inspection-provider-raptor-maps-secures-22-million-series-b/ | 2022-04-15 |
| Raptor Maps cumulative analysis | 373 GWdc (2026 report); 193 GWdc (2025); 67 GWdc in 2024 | https://raptormaps.com/resources/reports | 2026 |
| Solar unrealised revenue 2024 / underperformance trend | ~$10B / +214% in 5 yrs | https://raptormaps.com/resources/global-solar-report-2025 | 2025 |
| Raptor Solar Sentry deployment | 4 GW+ | https://raptormaps.com/products/raptor-solar-sentry | fetched 2026-09-24 |
| Clobotics scale & accuracy | 180,000+ blade inspections; 40+ countries; 15 min; >95% recall; >98% major-defect recall; 1 mm | https://clobotics.com/industries/wind/ | fetched 2026-09-24 |
| Clobotics acquired Aerodyne AtSite | undisclosed terms | https://investindk.com/cases/clobotics-acquires-aerodyne-atsite-to-expand-its-wind-industry-capabilit | 2020-04-03 |
| Cornis scale | 37,000+ inspections; 6,500+ offshore; 45% of EU offshore; 10M images; 710k defects | https://cornis.fr/ | fetched 2026-09-24 |
| Cyberhawk scale | 500,000+ inspections; 40 countries; 300+ customers; 11,000 iHawk users | https://thecyberhawk.com/ | fetched 2026-09-24 |
| Aerodyne scale | 45 countries; 752,700 assets; 8,300 MW solar inspected (as of Dec 2022) | https://aerodyne.group/ | fetched 2026-09-24 |
| Above Surveying scale | 10,000+ sites; 900+ companies; 500+ capture partners; NPS 71+ | https://www.abovesurveying.com/ | fetched 2026-09-24 |
| Sitemark scale | 310+ GWp; 1,100+ companies; 25+ anomaly types; C&I <60 min | https://www.sitemark.com/research/best-solar-inspection-software/ | 2026-05-26 |
| Scopito prices | EUR 160/turbine analysed; EUR 80 self; EUR 20/solar asset; EUR 16/power-line asset | https://scopito.com/wind-turbine-inspection-software/ ; https://www.spotsaas.com/product/scopito/pricing | 2026 |
| Optelos rating | 4.8/5 (13 reviews) | https://www.getapp.com/business-intelligence-analytics-software/a/optelos/ | 2026 |
| Skydio Series F / valuation / total raised | $110M / $4.4B / ~$672M (article) vs $825M (snippet) | https://dronexl.co/2026/04/23/skydio-110m-series-f-44-billion-valuation/ | 2026-04-23 |
| Skydio X10 unit price; enterprise customers | $16,000-25,000; 3,800+ | same | 2026-04-23 |
| Percepto total funding / Series C | >$120M / $67M (Koch Disruptive) | https://dronedj.com/guides/percepto/ | Jun 2023 |
| Percepto FAA waivers | nationwide BVLOS (Nov 2022); 1 pilot : 30 drones (Nov 2023) | same | 2022-2023 |
| Voliro funding / customers | $23M total; 40+ customers; 17 countries; 100+ contact inspections/month | https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ | 2025-06-16 |
| Voliro LPS economics | 5x faster; up to 50% cheaper; traditional ~EUR 5,000/turbine; 81 turbines; 45-50 min each | https://voliro.com/case-study/wind-turbine-lps-inspection-drone-italy-cva/ | n.d. |
| Nearthlab funding | $10M seed (2021); ~$42.3M total; Series C-III $0.72M POSCO Capital (snippet) | https://dronelife.com/2021/08/26/drone-inspections-for-wind-turbines-in-as-little-as-15-minutes-korean-drone-software-company-nearthlab/ ; https://www.crunchbase.com/organization/nearthlab | 2021; 2025-08-14 |
| Nearthlab detectable defect size | 1 mm (Basic) / 0.3 mm (Pro); 15 min | https://dronelife.com/2021/08/26/drone-inspections-for-wind-turbines-in-as-little-as-15-minutes-korean-drone-software-company-nearthlab/ | 2021-08-26 |
| Sterblue results | wind inspection 80+ -> <40 min; reports in 2 days; 98% on 5/35 grid defects; 50% cost | https://enterprise.dji.com/news/detail/grid-and-wind-turbine-inspections-made-easy-by-drone-solutions | 2020 |
| Perceptual Robotics | 5,000+ inspections; 18 countries (past year) | https://zagdaily.com/zag-air/wind-turbine-inspections-show-how-drones-work-at-scale/ | 2025-12-16 |
| Blade replacement cost; unscheduled repair share; blades replaced/yr | EUR 500k-2-3M; ~65%; 0.5-1% | same | 2025-12-16 |
| Wind O&M spend; unplanned repairs; LEE AEP loss | ~$15B (2019); 57%; up to 5% | https://www.sulzerschmid.ch/2022/10/tracking-blade-damage-progression-to-enable-predictive-maintenance-can-generate-huge-savings-and-increase-annual-energy-production/ | 2022-10-13 |
| Lightning losses | >$100M/yr; 60% blade losses; 1.2 strikes/yr per 200 m turbine | https://www.windsystemsmag.com/drone-inspections-can-prevent-million-dollar-lightning-losses/ | 2025-03-15 |
| Turbine downtime cost | $3,000-17,000 per turbine per day | https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ | 2026-05-05 |
| Drone inspection price / rope access | $300-600 / $1,500-3,000 per turbine; advanced $2,000-4,000 | https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ | Aug 2025 |
| Solar thermal survey price | $300-500/MW; full diagnostic $500-1,200/MW | https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know | 2025-05-05 |
| IEC-compliant vs basic solar flyover | $300-500 vs $150-200 per MW (snippet) | https://averroes.ai/blog/drone-solar-panel-inspection-guide | 2026-07-14 |
| IEC 62446-3 thresholds | 600 W/m2; Class 2 ~dT >= 10 C; Class 3 ~dT >= 40 C | https://thermalvariations.com/learn/iec-62446-3-thermal-inspection | 2026 |
| IEC 62446-3 resolution; revision timing | 3 cm/pixel; new edition expected fall 2025 | https://www.vhive.ai/navigating-the-iec-standards-for-solar-farm-inspections/ | 2025 |
| Wind severity scale | 5 categories; Cat 3 repair 6-12 mo; Cat 4 3-6 mo; Cat 5 stop turbine | https://thebalmoregroup.co.uk/wind-turbine-blade-defect-categories/ | n.d. |
| Wind drone inspection market | $418.5M (2025) -> $478.8M (2026) -> $1,838M (2036); 14.4% CAGR | https://www.factmr.com/report/wind-turbine-drone-inspection-market | 2026-09-03 |
| RAG+VLM blade paper | 100% on 30 images; retrieval > no retrieval | https://arxiv.org/abs/2510.22868 | 2025-10 / rev 2026-08 |
| Few-shot VLM blade paper | 98.3% acc, 0.862 Dice, 15 samples/class, +13.3 pts vs supervised (snippet) | https://www.sciencedirect.com/science/article/pii/S2590123026022152 | 2026 |
| VLM damage-priority paper (bridges) | LLaVA-1.5-7B QLoRA; 5-level priority; 800 test images; 10.06 s/image | https://arxiv.org/abs/2605.27452 | 2026-05-24 |

---

## Implications for our product / edge (gap analysis)

1. **Do not compete on capture.** Zeitview (80k pilots), SkySpecs (own drones), Sulzer Schmid/Nearthlab/Clobotics (autonomy hardware), Skydio/Percepto (docks) own capture. Position as the **analysis and grading layer that accepts anyone's imagery** (BYO drone, ROV, handheld, thermal, radiographic). Skydio Extend, DJI ecosystem listings and Raptor's "Self-Perform" tier show buyers already separate capture from analytics. **Inference.**
2. **Multi-asset in one grading engine is genuinely unoccupied.** Every wind vendor is blade-only; every solar vendor is PV-only; the cross-sector players (Zeitview, Aerodyne, Cyberhawk) are service companies with per-vertical pipelines. Nobody found does wind + solar + bridge + underwater + weld/X-ray. The VLM cascade is what makes one engine across asset classes plausible (the bridge-priority paper uses the same 5-level pattern). Judges will still ask "why not focus?" - answer with one beachhead (below) and show the engine generalising as the "what's next" slide.
3. **Standard-referenced, explainable grading is the visible white space.** Incumbents output "severity ratings" without publishing definitions or rationale. Ship: Cat 1-5 (wind, Balmore-style with repair windows) and IEC TS 62446-3 Class 1/2/3 (solar, with dT, irradiance and conditions log) as first-class schema; every finding carries the retrieved reference, the measured evidence (size, dT), the rule that fired, and a confidence. No vendor page found does this.
4. **Publish precision/recall per category on a held-out set.** Only Clobotics publishes recall. A small but honest confusion matrix on real public imagery beats everyone's marketing copy in the rubric's "evidence" line - and satisfies the hackathon rule against fabricated performance claims.
5. **Price for the people incumbents ignore.** Only Scopito publishes prices (EUR 80-160/turbine, EUR 20/solar asset); everyone else is a custom enterprise quote. Small ISPs, regional drone service providers, and sub-100 MW owners are left with AI-less generic tools (~$300/mo). A pay-per-asset tier under Scopito's EUR 80 self-analysis price, with a free "is there damage?" small-VLM triage, is a credible first-100-customers wedge (drone service providers reselling reports). **Inference.**
6. **On-prem / edge is a real but niche ask.** Scopito lists on-prem only in enterprise; SkyVisor markets "on-premises data control"; Sitemark attacks DJI on China data residency. A cascade whose first stage runs on-device (small VLM on the Jetson-class compute Skydio X10 already carries) is a differentiator for utilities and defence-adjacent buyers; it also cuts cloud cost by only uploading flagged frames. **Inference.**
7. **Thermal + RGB fusion across asset classes.** Solar vendors fuse thermal + RGB; wind vendors mostly do RGB (Cyberhawk offers thermal). Percepto advertises "AI-powered thermal and RGB analytics" for utilities. Fusing both under one grading schema (e.g., thermal hotspot + visible crack on a blade LPS receptor) is unclaimed.
8. **Closed-loop to repair is where incumbents are heading.** SkySpecs (repair-vendor management, warranty tracking), Clobotics (SPARROW robotic repair), Voliro (LPS test) all move toward repair. Our "prioritised work queue" must at least export to CMMS and quantify AEP/revenue at risk per finding (SkySpecs and Raptor already frame findings in AEP/$).
9. **Regulatory reality shapes the demo.** VLOS still dominates; most users are technicians not pilots. A demo that grades a folder of photos from a handheld camera/phone or a low-cost DJI drone is more honest than a "fully autonomous" story.
10. **Disaster/rapid-recovery angle:** none of the wind/solar incumbents market post-storm/post-earthquake triage specifically; Zeitview's 80k pilots and Percepto's docks are the obvious capture partners. The cheap first-pass VLM gate is precisely the tool for "thousands of assets fast" triage; frame it as the additional high-value application per Prompt D.

**Beachhead suggestion (Inference):** independent wind O&M/ISPs and regional drone service providers in the US who already fly $300-600/turbine jobs and today hand-annotate images or pay EUR 160/turbine for analysis. Sell them a report engine that grades to Cat 1-5 with evidence and exports a CMMS-ready queue; use solar (IEC 62446-3) as the second vertical because the same providers fly both.

---

## Open questions / gaps

- Raptor Maps funding after the 2022 Series B; Sitemark/vHive/Clobotics/Sulzer Schmid/Cornis funding: **not found** (PitchBook/Crunchbase/Tracxn pages blocked; search budget exhausted).
- Sterblue current status (independent? acquired?) - site unreachable; **not verified**.
- Aerodyne 2024 "real-time AI" service and Cyberhawk "55% FY2024 revenue growth" come only from search snippets; **not verified** against a primary page.
- SkySpecs $142M total and layoff details rely on snippets (cbinsights, Glassdoor); **not verified**.
- No public SLA/turnaround for Zeitview, SkySpecs, Raptor Maps, Sulzer Schmid, Above. Would need customer interviews.
- No third-party (non-vendor) accuracy benchmark for any commercial system was found; all accuracy numbers are vendor claims or academic small-n.
- Definitive text of the IEC TS 62446-3:2025 revision (whether dT class thresholds changed) - **not found**; the ~10 C / ~40 C values are from a secondary explainer.
- Whether any incumbent already uses VLMs internally (possible but undisclosed) - **unknown**.
- Skydio total raised: $672M (DroneXL body) vs $825M (search snippet) - **contradiction unresolved**.
- Market size: Fact.MR global $418.5M (2025) vs a US-only "$478M in 2025" claim elsewhere - **contradiction; treat as rough**.
- Customer-side complaints are thin (Zeitview n=4 Trustpilot; Optelos n=13 GetApp; zero reviews for Raptor Maps and Scopito on the sites checked). Real validation needs interviews with ISPs/O&M teams.
- Underwater, bridge, telecom and X-ray/weld competitors are out of scope for this note (other research angles).

---

## Sources

1. https://pv-magazine-usa.com/2025/03/07/zeitview-raises-60-million-in-funding-to-further-advance-ai-powered-infrastructure-inspections/ - Zeitview $60M round, 200k assets, 80 countries (2025-03-07).
2. https://www.businesswire.com/news/home/20250304009141/en/Zeitview-Secures-$60M-to-Advance-AI-Powered-Inspections-of-Global-Critical-Infrastructure - Zeitview press release (403; title only).
3. https://www.zeitview.com/wind - Zeitview wind services, 60,000 turbines 2025, >500 GW, 40 countries.
4. https://www.zeitview.com/solar - Zeitview solar, 600 GW PV, 80,000 pilots.
5. https://www.zeitview.com/resource/wind-turbine-crack-detection - Zeitview crack dataset and model approach.
6. https://www.trustpilot.com/review/www.zeitview.com - Zeitview Trustpilot 2.6/5, 4 reviews.
7. https://www.zeitview.com/wind-insights - Zeitview Wind Insights (404 on fetch).
8. https://skyspecs.com/ - SkySpecs scale metrics and product lines.
9. https://skyspecs.com/product/inspections/ - SkySpecs 275k inspections, 15 min/turbine.
10. https://skyspecs.com/horizon-bam/ - Horizon Blade Asset Management features.
11. https://www.businesswire.com/news/home/20250319813255/en/SkySpecs-Raises-%2420m-to-Fuel-Global-Growth-and-Innovation - SkySpecs $20M (403; title).
12. https://www.cbinsights.com/company/skyspecs - SkySpecs funding profile (snippet).
13. https://energy.toolsinfo.com/tool/skyspecs - SkySpecs pros/cons (narrow scope).
14. https://www.sulzerschmid.ch/offering/ - Sulzer Schmid offering tiers and buyers.
15. https://www.sulzerschmid.ch/2022/07/press-release-new-3dx-damage-progression-module/ - 3DX damage chain module.
16. https://www.sulzerschmid.ch/2022/10/tracking-blade-damage-progression-to-enable-predictive-maintenance-can-generate-huge-savings-and-increase-annual-energy-production/ - O&M spend, 57% unplanned, 5% AEP.
17. https://www.marinelink.com/news/advanced-ai-engine-automated-blade-damage-470216 - Sulzer Schmid x NNAISENSE AI (2019).
18. https://enterprise.dji.com/ecosystem/sulzerschmid-3dx - 3DX in DJI ecosystem.
19. https://roboticsandautomationnews.com/2025/12/26/best-5-wind-turbine-inspection-software-platforms/97853/ - Dec 2025 roundup (vHive, 3DX, Unleash Live, Droneperhour, OpenWindPower).
20. https://aerodyne.group/ - Aerodyne scale, vertikaliti.
21. https://investindk.com/cases/clobotics-acquires-aerodyne-atsite-to-expand-its-wind-industry-capabilit - Clobotics acquires Aerodyne AtSite (2020).
22. https://thecyberhawk.com/ - Cyberhawk scale.
23. https://thecyberhawk.com/renewable-energy - Cyberhawk wind/solar, OEM-standard categorisation.
24. https://cornis.fr/ - Cornis scale and product suite.
25. https://event.businessfrance.fr/wind-europe-2025/cornis-inspection-blade-data-management/ - Cornis 5M-image AI (WindEurope 2025).
26. https://enterprise.dji.com/news/detail/grid-and-wind-turbine-inspections-made-easy-by-drone-solutions - Sterblue results (2020).
27. https://www.sterblue.com/industrial-applications/wind-turbine - Sterblue wind page (unreachable).
28. https://raptormaps.com/ - Raptor Maps platform overview.
29. https://raptormaps.com/products/solar-inspections-analytics - Raptor anomaly types, collection tiers.
30. https://raptormaps.com/products/raptor-solar-sentry - Solar Sentry 4 GW+.
31. https://raptormaps.com/resources/reports - Global Solar Reports 2023-2026 figures.
32. https://raptormaps.com/resources/global-solar-report-2025 - $10B unrealised revenue, +214%.
33. https://www.pv-magazine.com/2022/04/15/solar-drone-inspection-provider-raptor-maps-secures-22-million-series-b/ - Raptor Maps $22M Series B.
34. https://apps.list.solar/tools/raptor-maps/ - Raptor Maps pricing model, pros/cons.
35. https://sourceforge.net/software/product/Raptor-Maps/ - Raptor Maps zero reviews, alternatives list.
36. https://www.abovesurveying.com/ - Above Surveying scale and SolarGain.
37. https://www.sitemark.com/research/best-solar-inspection-software/ - Sitemark comparison of solar tools (2026-05-26).
38. https://scopito.com/wind-turbine-inspection-software/ - Scopito per-turbine pricing, on-prem enterprise.
39. https://www.spotsaas.com/product/scopito/pricing - Scopito per-asset prices.
40. https://www.capterra.com/p/213899/Scopito/ - Scopito Capterra (0 reviews).
41. https://optelos.com/platform-overview/ - Optelos platform.
42. https://www.getapp.com/business-intelligence-analytics-software/a/optelos/ - Optelos 4.8/5, 13 reviews.
43. https://www.skydio.com/solutions/asset-inspection/faq - Skydio inspection stack, no in-house grading.
44. https://www.skydio.com/blog/elevate-your-inspections-with-ai-powered-safety-security-and-asset-maintenance-inspections - Skydio x Levatas (2024).
45. https://nawindpower.com/qii-ai-skydio-partner-on-automated-infrastructure-inspections-with-drone-tech - Skydio x Qii.AI (unreachable; snippet).
46. https://dronexl.co/2026/04/23/skydio-110m-series-f-44-billion-valuation/ - Skydio $110M at $4.4B, X10 price.
47. https://dronedj.com/guides/percepto/ - Percepto funding, waivers, FPL.
48. https://www.renewableenergyworld.com/power-grid/grid-modernization/autonomous-drone-company-releases-end-to-end-ai-powered-remote-inspection-solution-at-distributech/ - Percepto AI utility solution (2025-03-26).
49. https://voliro.com/blog/voliro-secures-23m-via-series-a-extension-to-modernize-infrastructure-with-aerial-robotics/ - Voliro $23M, 40+ customers.
50. https://voliro.com/case-study/wind-turbine-lps-inspection-drone-italy-cva/ - CVA 81-turbine LPS case, EUR 5,000/turbine baseline.
51. https://voliro.com/blog/best-wind-turbine-inspection-drones/ - Voliro drone comparison (Skydio X10, DJI M350, etc.).
52. https://www.windsystemsmag.com/drone-inspections-can-prevent-million-dollar-lightning-losses/ - lightning losses >$100M/yr.
53. https://dronelife.com/2021/08/26/drone-inspections-for-wind-turbines-in-as-little-as-15-minutes-korean-drone-software-company-nearthlab/ - Nearthlab products, $10M seed.
54. https://dronelife.com/2023/03/23/drones-for-wind-turbine-inspection-onyx-insight-and-nearthlab/ - Nearthlab x ONYX Insight.
55. https://www.crunchbase.com/organization/nearthlab - Nearthlab funding (snippet).
56. https://clobotics.com/industries/wind/ - Clobotics scale, accuracy claims, SPARROW.
57. https://zagdaily.com/zag-air/wind-turbine-inspections-show-how-drones-work-at-scale/ - Perceptual Robotics, blade economics, BVLOS limits (2025-12-16).
58. https://www.skyvisor.ai/en-us/wind-turbine-inspection-costs-roi/ - SkyVisor cost/ROI figures and product.
59. https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ - per-turbine costs, pilot day rates, downtime cost (2026).
60. https://www.uavsphere.com/post/2025-wind-turbine-drone-inspection-cost - wind cost range (snippet).
61. https://averroes.ai/blog/wind-turbine-drone-inspection-cost-breakdown-advice - wind cost range (snippet).
62. https://www.uavsphere.com/post/2025-solar-panel-drone-inspection-costs-everything-you-need-to-know - solar $/MW.
63. https://averroes.ai/blog/drone-solar-panel-inspection-guide - solar $/MW, IEC camera specs, vendor accuracy claims (2026-07-14).
64. https://www.geowgs84.com/post/how-much-does-a-drone-solar-panel-inspection-cost - low-end $/MW (snippet).
65. https://thermalvariations.com/learn/iec-62446-3-thermal-inspection - IEC 62446-3 classes and thresholds.
66. https://www.vhive.ai/navigating-the-iec-standards-for-solar-farm-inspections/ - IEC 62446-3 3 cm/pixel, fall-2025 revision.
67. https://www.airsuv.uk/drone-inspection-uk-airsuv//iec-62446-3-solar-farm-drone-inspection-uk - IEC conditions log, R-JPEG delivery.
68. https://thebalmoregroup.co.uk/wind-turbine-blade-defect-categories/ - Cat 1-5 blade severity definitions.
69. https://www.factmr.com/report/wind-turbine-drone-inspection-market - market size 2025-2036.
70. https://arxiv.org/abs/2510.22868 - RAG + VLM zero-shot blade inspection (2025/2026).
71. https://www.sciencedirect.com/science/article/pii/S2590123026022152 - few-shot VLM hierarchical retrieval (2026; snippet).
72. https://www.sciencedirect.com/science/article/pii/S2405896325029192 - few-shot RAG+VLM blade damage (2025).
73. https://arxiv.org/abs/2605.27452 - VLM fine-tuning for damage + priority scoring with quality guard (2026-05-24).
74. https://pmc.ncbi.nlm.nih.gov/articles/PMC12300182/ - DINOv2 blade defect recognition (2025; snippet).
