# 08 - Customer Voice & Discovery: Infrastructure Inspection (Public Evidence + Weekend Plan)

Research angle: customer_voice_and_discovery
Written: 2026-09-24 (Thu evening, Los Angeles) for Origin Weekend Fall 2026, Prompt D
Method: web research only (WebSearch + WebFetch + local text extraction of 4 public PDFs). No interviews were conducted; nothing below is an interview result. Every quote is tagged [PUBLIC QUOTE] with its URL; our reasoning is tagged [Inference].
Constraints hit: Reddit (reddit.com / old.reddit.com) is blocked at the fetch layer and the session's web-search budget ran out mid-task, so practitioner voice comes from trade press, vendor customer stories (named people), the Commercial Drone Pilots forum, DOT research reports, and NTSB/FHWA documents rather than Reddit.

---

## Summary

- Buyers of inspection services are mostly buying COMPLIANCE + a WORK LIST, not "AI". Public bridge RFPs (Dane County WI, Kansas DOT, Fountain County IN via INDOT, NJDOT) specify: enter every inspection into the state system (HSIS / InspectX) within a deadline, photo-document elements in condition state CS3/CS4, deliver a summary report of "recommended bridge maintenance work for each structure", and hand over all data as the owner's property. Dane County even fines "$100 per day" for late HSIS entry. Source: Dane County RFP 120048 (2020) https://www.danepurchasing.com/bids/GetBidDocument/4c14a95c-8c4d-41e3-840b-de067fec49fd
- The image-overload pain is real and quantified by a utility, not a vendor: AEP Ohio's 2025 drone pilot covered ~4% of its distribution system, produced 400,000-500,000 images, and "a single person went through the entire year spending 500 plus hours" reviewing them (Renewable Energy World, 2026-01-14). https://www.renewableenergyworld.com/power-grid/how-autonomous-drones-and-ai-are-reshaping-utility-inspection-programs/
- Inspector inconsistency is documented by FHWA (2001: 49 inspectors, 25 states; only 68% of condition ratings within +/-1 point of the mean) and again in 2026 (24 Indiana inspectors in VR; only 30% of ratings matched expected). Manual crack-area measurements vary "from as low as 18% to often exceeding 100%" (Washer et al. 2020, cited in VTRC 25-R4, Jan 2025). Sources: https://www.fhwa.dot.gov/publications/research/nde/01021.cfm ; https://ascelibrary.org/doi/10.1061/JBENF2.BEENG-7583 ; https://vtrc.virginia.gov/media/vtrc/vtrc-pdf/vtrc-pdf/25-R4.pdf
- The most expensive failures were PRIORITIZATION failures, not detection failures: NTSB found Fern Hollow Bridge collapsed because of the city's "failure to act on repeated maintenance and repair recommendations from inspection reports" (2024). The I-40 Hernando de Soto fracture was visible in 2019 drone footage but not acted on until 2021. https://www.ntsb.gov/investigations/Pages/HWY22MH003.aspx ; https://en.wikipedia.org/wiki/Hernando_de_Soto_Bridge
- Solar owners' pain is measurable and growing: equipment-driven power loss rose from 2.36% (2021) to 5.08% (2025); sites inspected 5x/yr average ~3% loss vs ~7% for 1x/yr; the average technician is responsible for 70% more capacity than five years ago (Raptor Maps via PV Tech, 2026-02-26). https://www.pv-tech.org/pv-project-power-loss-doubled-in-last-five-years-raptor-maps/
- Named asset managers say the problem is DATA, not flying: "Before working with SkySpecs, we performed inspections intermittently, and the data was helter-skelter!" (MidAmerican Energy PM); "Having inspection history centralized in one place is critical" (Madison Energy Infrastructure, Sept 2026). https://skyspecs.com/ ; https://raptormaps.com/blog-posts/raptormaps-mei-casestudy
- Buyers punish false alarms: "With technicians and analysts stretched thin, there is little patience for unreliable insights or even small numbers of false alarms" (SkySpecs blog, 2025-03-05). https://skyspecs.com/blog/unlocking-wind-energy-efficiency-data-analytics-skyspecs/
- The hands-on rule constrains bridges: ODOT pilot: "A drone can't be used for those inspections. An arm's-length inspection is mandatory." Routine NBIS inspections are due every 24 months (23 CFR 650.311) and data must be entered within 3 months (650.315). https://www.skydio.com/customer-stories/Ohio-Department-of-transportation ; https://www.law.cornell.edu/cfr/text/23/650.311
- Small utilities and independent drone pilots feel the pain from the other side: "as we dive into more uses ... that will quickly become a full time job in and of itself"; Optelos AI software "quite expensive" (Oregon PUD pilot, 2019); utilities are "getting HAMMERED with these same requests" from drone pilots (forum, 2018). https://commercialdronepilots.com/threads/data-analysis-and-drone-operations-management.2433/ ; https://commercialdronepilots.com/threads/what-is-working-now.109/
- A concrete LA weekend discovery plan follows (Section 5): 22 target organizations/roles with verified anchor facts, an outreach template, a 10-question script, and an honest logging protocol.

---

## Detailed findings

### 1. What buyers actually ask for - public RFPs / procurement documents

#### 1.1 Dane County, WI - RFP #120048 "Bridge Inspections & Re-Inspections" (issued 2020-04-20, due 2020-05-20)
Source (PDF, text extracted locally): https://www.danepurchasing.com/bids/GetBidDocument/4c14a95c-8c4d-41e3-840b-de067fec49fd

What the buyer requires [PUBLIC QUOTE, verbatim from RFP]:
- Data system + deadline: "Reports of the 2020 & 2021 inspections shall be entered into the HSIS database per WisDOT requirements."
- Work-list deliverable: "A summary report stating the overall findings of the bridge inspections and recommended bridge maintenance work for each structure shall be submitted to the County no later than December 15".
- Penalty for late data: "Failure to have all inspection reports entered into HSIS within 30 days of their due date ... will result in a $100 per day penalty being assessed against the Provider until all required reports are received."
- QA rejection loop: "The COUNTY reserves the right to disapprove any inspection reports ... The Consultant has thirty (30) days to address the report deficiencies and resubmit".
- Data ownership: "All reports and documents prepared under the Agreement become the property of the County, WisDOT and the Bridge Owner. The Consultant shall not disclose report information to any third party except by written order of the County." Also T&C 22.3: "All data, documentation, and innovations shall be the property of the County."
- Photo rules tied to condition states: "Elements that are rated CS3 or CS4 require photo documentation." CS4 structural elements trigger "a structural analysis or load rating" as a paid change order.
- Escalation: "If the condition is critical or near critical, the Provider shall so advise the County and the municipality immediately so that necessary action can be promptly initiated."
- Evaluation weights: Project Understanding & Approach 35%, Project Team 25%, Capabilities 15%, # of bridges rated 10%, load rating 10%, Cost 5%.
- No mention of drones, UAS, or AI anywhere in the 32-page RFP.

[Inference] For county/municipal bridge programs, the "product" is the HSIS/state-system record plus a maintenance-recommendation list per structure. A tool that produces CS-rated, photo-backed element findings that import into the state system, and a prioritized maintenance list, maps directly onto the deliverables buyers already pay for.

#### 1.2 Kansas DOT - RFP for Embedded State Highway System Bridge Inspection Services (Kansas Register 2025-04-17; proposals due 2025-04-30)
Source: https://www.sos.ks.gov/publications/register/Volume-44/Issues/Issue-16/04-17-25-53025.html
[PUBLIC QUOTE] Consultants must "Complete the inspection in InspectX (ratings, notes, photos, and recommendations)"; team leaders must have "completed the two-Week NHI Bridge Inspection Course (NHI 130055)", the refresher (NHI 130053), NSTM course (NHI 130078) and Underwater course (NHI 130091); firms must be "prequalified by KDOT" in "322 - Bridge Inspection" or "323 - Underwater Bridge Inspection". Evaluation weights include "Quality control approach: 15%". No drones/UAS mentioned.
[Inference] The state system of record (InspectX in KS; HSIS in WI; AASHTOWare BrM elsewhere) is the integration target for DOT buyers, not Maximo/SAP.

#### 1.3 INDOT / Fountain County, IN - Countywide Bridge Inspection Program, Des #2100288 (posted 2021-05-27)
Source (PDF, text extracted locally): https://www.in.gov/dot/div/legal/rfp/LPARFP/Archive/2021/may/RFP%202100288.pdf
[PUBLIC QUOTE] Inspection frequency table: Routine at 48 months (17 bridges), 24 months (115), 12 months (10); "Fracture Critical ... 15" bridges; "7 bridges require special inspection ... to inspect fracture critical members rated a 4 or less." "Funding: 80% Federal Funding, 20% Local Funds." Rating sheet rewards "Project Understanding and Innovation that provides cost and/or time savings."
[Inference] Even a small county has a risk-tiered schedule; a product that helps a consultant hit 12/24/48-month cycles and flag "rated 4 or less" members is speaking the buyer's language.

#### 1.4 NJDOT - Bridge Resource Program-1 research RFP 2024-05 (announced 2024-12-12; closed 2025-01-20)
Source (PDF, text extracted locally): https://www.nj.gov/transportation/business/research/pdf/ResearchProcureRFPs/2024/RFP_2024-05.pdf
[PUBLIC QUOTE] NJDOT wants help to "investigate a model-based bridge data extraction method for both textual and graphical information from Structural Assets inspection reports ... leveraging text mining methods to automatically extract critical information from inspection reports as well as image recognition methods to align photographs of bridge deck conditions with bridge models", and to "Research and assist in investigating drone and robotic systems inspection guidance". Budget: "shall not exceed $700,000 US Dollars ($350,000 per year)". Only NJ public universities may apply.
[Inference] A state DOT is explicitly asking for VLM-style extraction over inspection reports and photos - strong evidence the "heavy VLM grading + report" idea is what DOT asset-management groups want, even if procurement routes it through universities.

#### 1.5 Longmont Power & Communication (CO) - Overhead Drone Infrastructure Inspection RFP (published 2025-01-07; due 2025-02-05)
Source: https://proposalalert.com/rfp/overhead-drone-infrastructure-inspection
[PUBLIC QUOTE] "non-contact condition evaluations and maintenance identification across LPC's distribution infrastructure"; "FAA-registered small unmanned aerial systems"; one year with four optional renewals; insurance required; electronic submission via Rocky Mountain E-Purchasing System. Full deliverable spec sits behind BidNet login (not retrieved).
[Inference] Municipal utilities buy drone inspection as a multi-year service with "maintenance identification" as the output - i.e., they want the work list, not raw images.

#### 1.6 Federal baseline every bridge buyer must meet (23 CFR 650, NBIS)
Sources: https://www.law.cornell.edu/cfr/text/23/650.311 ; https://www.law.cornell.edu/cfr/text/23/650.315
[PUBLIC QUOTE] Routine: "Each bridge must be inspected at regular intervals not to exceed 24 months"; risk-based extensions to 48 months (Method 1) and 72 months (Method 2); underwater inspections at intervals "not to exceed" 60 months; NSTM 24 months (12 for poor condition). Data: "Inventory data must include element level bridge inspection data for bridges on the NHS collected in accordance with the 'Manual for Bridge Element Inspection.'" and changes must be entered "within 3 months after the month when the field portion of the inspection is completed."
Scale: TxDOT alone has "57,000 bridges on the National Bridge Inventory requiring inspection" every two years (Skydio customer story, undated) https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections ; nationally "over 41,600 bridges rated in poor condition" and "1 out of 3 U.S. bridges still needs to be replaced or repaired" (ARTBA, July 2025) https://artbabridgereport.org/

#### 1.7 Solar buyers - the de facto spec is IEC TS 62446-3
No formal solar-farm inspection RFP document was retrievable (gap). What owners/lenders/insurers ask for is described by service providers:
- "All PV modules shall be recorded with a minimum resolution of 5x5 pixels per cell." (Above Surveying explainer of IEC TS 62446-3, 2023-11-01) https://www.abovesurveying.com/blog/understanding-iec-62446-32017-outdoor-infrared-thermography
- Minimum irradiance "typically 600 W/m2"; "Final reports are typically delivered within 5 to 10 working days after the flight operation is completed." (Impact Aerial, 2026-06-26) https://www.impactaerial.co.uk/2026/06/26/drone-thermal-survey-for-solar-farms-the-2026-guide-to-pv-inspection/
- Severity is communicated as Delta-T thresholds (10 C minor, >30 C critical) and a "Red, Amber, Green" rating; stakeholders listed: asset managers (warranty claims), O&M (geo-tagged repairs), manufacturers (warranty), insurers (compliance), lenders (Impact Aerial, 2026-07-10) https://www.impactaerial.co.uk/2026/07/10/drone-thermal-survey-for-solar-farms-the-ultimate-guide-to-pv-asset-optimisation/
[Inference] For solar, "report format" = IEC-conformant anomaly register with severity class + module-level geolocation; a 5-10 working-day turnaround is the incumbent baseline to beat.

#### 1.8 Wind buyers - who buys and what they require (service-provider guidance, not an RFP)
Source (Drone Launch Academy, updated 2026-06-01): https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/
[PUBLIC QUOTE] Warranty-grade data: "1mm/pixel or better, along with precise time-stamps and GPS metadata"; inspections "every 6-12 months typically; 3-6 months for harsh environments"; go-to-market advice: pitch "independent Operations and Maintenance (O&M) providers or smaller regional wind farm owners" rather than "massive utility companies". Pricing (vendor-stated, uncited): "$300 and $600 per turbine" standard visual; "$2,000-$4,000 per turbine" with LiDAR/lightning testing; day rates "$1,500 to $3,500".
[Inference] Wind ISPs (independent service providers) and small IPPs are the reachable first customers; OEM-locked fleets (Vestas/GE/Siemens Gamesa service contracts) are not.

#### 1.9 Utility procurement signals (transmission/distribution)
- Utility Dive (2026-07-06): Southwestern Public Service's $113M Texas reliability grant "covers a drone-based pole inspection program and live monitoring". https://www.utilitydive.com/news/southwestern-public-service-reliability-grant-texas-puc/824464/
- UAV Coach (2026-04-12) price benchmarks for service providers: "$300 to $2,000 per mile" and "$150 and $500" per structure; in-house program startup "$25,000-$50,000"; software "$3,000-$10,000 annually". https://uavcoach.com/powerline-inspection-drones/
- Security/integration expectations named by a utility-focused platform: SAP, Maximo, GIS/Esri integrations; "SOC 2, ISO 27001, and FedRAMP"; on-prem/edge deployment options (Unleash Live, 2025-10-16; vendor claim). https://unleashlive.com/blog/how-utilities-can-unlock-the-value-of-drone-and-ai-inspections-for-utility-asset-monitoring/
- ComEd feeds Skydio imagery into "ComEd's Optelos image analytics platform" (Skydio customer story, undated). https://www.skydio.com/customer-stories/comed
[Inference] Investor-owned utilities already own an image platform (Optelos, etc.) and an EAM (Maximo/SAP). We should be the grading/prioritization layer that exports to those, not a replacement.

### 2. Practitioner voices (public, attributable)

#### 2.1 Utility drone program managers
- Jake Reed, AEP Ohio drone program (Renewable Energy World, 2026-01-14) [PUBLIC QUOTE]: pilot inspected "about 4%" of the distribution system, found "more than 150 'tier one' issues", collected "between 400,000 and 500,000 images", and "A single person went through the entire year spending 500 plus hours" reviewing. On a thermally flagged pole: "When they cut that open, it kind of looked like a cigar. So it was burning from the inside out." Levatas (AI vendor) claims post-flight analysis "under three to four minutes post flight". https://www.renewableenergyworld.com/power-grid/how-autonomous-drones-and-ai-are-reshaping-utility-inspection-programs/
- Same person (title given as "Program Manager - Center for Customer Reliability, American Electric Power" on Skydio's site) [PUBLIC QUOTE]: "We track our savings realized, our customer minutes of interruption avoided, everything down to the mileage that we've flown ... Over the last two and a half years, we've avoided about 30 million customer minutes of interruption". https://www.skydio.com/solutions/utilities  (Note: the two sources give different titles for Reed - "Project Manager, AEP Ohio Drone Program" vs "Program Manager - Center for Customer Reliability".)
- Chuck Salvo, EchoStor (T&D World, 2024-11-13) describing a Northeast utility client [PUBLIC QUOTE]: drone program consumed "8.5 terabytes of their 10-terabyte allocation with images and videos of transmission line inspections"; "Traditional manual image analysis required 3-5 minutes per image"; "at least five or six different groups regularly needed access to this inspection data" (maintenance, permitting, vegetation management silos). https://www.tdworld.com/smart-utility/article/55242455/modernizing-utility-infrastructure-inspections-where-ai-meets-asset-management
- ZBlackwood, licensed pilot at a small Oregon public utility district (Commercial Drone Pilots forum, 2019-09-09) [PUBLIC QUOTE]: "The quantity is small enough we can handle things after each flight with no problem but as we dive into more uses and more full time use, that will quickly become a full time job in and of itself." "We have viewed a demo of the Optelos software and it's pretty darn impressive what it can do, but quite expensive." Wants "one stop shop for operation requests, flight logs, reports, requesting and approving missions." https://commercialdronepilots.com/threads/data-analysis-and-drone-operations-management.2433/
- Mattdbal, "large power utility in the Midwest" (same forum, 2018-01-18) [PUBLIC QUOTE]: "Utility companies are going to be split on hiring contractors or doing it in house." https://commercialdronepilots.com/threads/what-is-working-now.109/

#### 2.2 State DOT bridge inspection staff
- Daniel Breda, Regional UAS Pilot, Ohio DOT (Skydio customer story, undated) [PUBLIC QUOTE]: "A drone can't be used for those inspections. An arm's-length inspection is mandatory." / "Without the drone footage, they would have missed the issue entirely. It changed the actual job plan." / "We're identifying defects we couldn't see before."
- Jamie Davis, GIS Data Manager, ODOT [PUBLIC QUOTE]: "We're hoping to feed all that footage into software that just gives us a daily report - so nobody has to watch hours of traffic video." ODOT has "500TB of archived drone video and imagery", "40+ trained drone operators", claims "$800K+ cost avoidance" and 0.2 mm crack resolution. https://www.skydio.com/customer-stories/Ohio-Department-of-transportation
- TxDOT (unnamed staff, Skydio story) [PUBLIC QUOTE]: "We have no safe way to inspect other than closing part of the bridge down, which takes a long time." "We're trying to move towards every structure in our inventory to have a digital twin, and every two years have a 3D scan done." https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections
- Chris Grazioso, Chief UAS Operations, MassDOT: "We have one job, and it is to gather data to help improve transportation in Massachusetts." (30 licensed pilots; program since 2018.) https://www.skydio.com/customer-stories/massdot-modernizes-infrastructure-oversight-with-drone-technology
- Caltrans SM&I (Mile Marker, Spring 2020): 42 aircraft and 64 certified pilots statewide; "For some inspection areas, drone savings could range from 40 percent to 70 percent"; limits: "cannot be operated in areas with flight restrictions, in poor weather conditions, or at bridges with limited vertical clearance." Named: Erol Kaslan (Chief, SM&I North Investigations Office), James Drago. https://dot.ca.gov/programs/public-affairs/mile-marker/spring-2020/bridge-inspections-taking-to-the-skies
- VDOT inspectors via Virginia Tech (VTRC 25-R4, Jan 2025; 20 DOT interviews nationwide, 41 VDOT inspector survey responses, 6 engineer responses, 3 bridges + 1 culvert shadowed) [PUBLIC QUOTE]: field workflow "necessitated redundant manual data entries into disparate systems, often leading to inaccuracies and issues with data integrity"; "the subjective nature of manual measurements and the difficulty in locating defects based on narrative descriptions were identified as significant obstacles"; inspectors showed "a cautious stance towards adopting new technological solutions, rooted in previous unsuccessful attempts to integrate modern devices into their workflow"; "tablet interfaces are not preferred by inspectors, due to issues with glare and portability"; the best result came from "hybrid automation approaches, where the inspector was able to refine automated defect labels" - fully automated measurement "exhibited a significantly higher variation, suggesting lesser reliability". Recommendation: integrate "with existing software (InspectX, AASHTOWare Bridge, or others)". https://vtrc.virginia.gov/media/vtrc/vtrc-pdf/vtrc-pdf/25-R4.pdf

#### 2.3 Wind asset managers / O&M
- Mark Jeratowski, Project Manager, MidAmerican Energy (SkySpecs homepage testimonial) [PUBLIC QUOTE]: "Before working with SkySpecs, we performed inspections intermittently, and the data was helter-skelter!"
- Isaiah Mathew, Operations Engineer, BluEarth Renewables [PUBLIC QUOTE]: "When you start the process, it can be scary. However, working with SkySpecs is helping us to identify how to prioritize and manage our repairs." https://skyspecs.com/
- SkySpecs blog (2025-03-05) [PUBLIC QUOTE, vendor voice]: "The wind industry faces a talent shortage, particularly when it comes to skilled analysts and asset managers." "With technicians and analysts stretched thin, there is little patience for unreliable insights or even small numbers of false alarms." Dataset: "inspections of over 275,000 blades, covering more than 91,600 wind turbines" (homepage now says "745,000+ blades inspected", "65% of North American blades monitored annually"). https://skyspecs.com/blog/unlocking-wind-energy-efficiency-data-analytics-skyspecs/
- UMass Lowell (2025-01-31; $356k NOWRDC grant) describing status quo [PUBLIC QUOTE]: "a person walks up and down the first two-thirds of the length of the blade, looking for defects". https://www.uml.edu/news/stories/2025/sabato-niezrecki-nowrdc-grant.aspx
- HammerMissions (forum, 2022-08-02) on deliverables [PUBLIC QUOTE]: "Since a wind turbine is a vertical structure with very similar looking surfaces, both 2D Maps and 3D photogrammetry are unviable options." https://commercialdronepilots.com/threads/how-do-you-currently-deliver-the-data.4098/
- SkySpecs internal-blade technician job posting shows the human cost baseline: rotations "3 weeks on, 1 week off", "50-90 hrs" per week, climb "2-3 towers daily". https://jobs.techstars.com/companies/skyspecs/jobs/68271601-internal-blade-inspection-technician-junior-and-senior-positions-available

#### 2.4 Solar asset managers / O&M
- Madison Energy Infrastructure (Raptor Maps case study, Sept 2026; ~1 GW operating, ~800 sites in 30 states) [PUBLIC QUOTE]: Mitchel Gehlig, Regional Asset Manager: "On many of our older systems, we do not have string or module level visibility." Matt Messer, VP Asset Management: "Because the inspection data told us exactly where the problems were, our crews could arrive on site with a defined scope of work." Esteban Schrick, Sr. Manager of Analytics: "Having inspection history centralized in one place is critical." Result claimed: 3 MW restored in 3 weeks after acquiring a ~300 MW portfolio; "hundreds of offline strings" undetected by SCADA. https://raptormaps.com/blog-posts/raptormaps-mei-casestudy
- Daniel Tomer, founder, vHive (pv magazine, 2026-07-10) [PUBLIC QUOTE]: "You have a very small window of time where you can really do a thermal scan. Somewhere between four to five, six hours, that's it." "When you have those large-scale solar farms, a manual survey is just impossible at this point." https://www.pv-magazine.com/2026/07/10/multi-drone-platform-for-autonomous-solar-inspections-digital-twin-creation/
- Public speakers on inspection decision-making (potential interview targets): Andreas Fladung (MD, Aerial PV Inspection) and Joerg Althaus (Director Engineering Services & QA, Intertek CEA), pv magazine webinar 2026-02-04. https://www.pv-magazine.com/webinars/how-to-make-the-right-inspection-decisions-for-solar-assets-from-the-factory-to-the-field/

#### 2.5 Ports
- Kimberley Holtz, Director of Survey, Port of Long Beach (AAPA Seaports, 2021-09-09) [PUBLIC QUOTE]: "We originally acquired drones for disaster situations so the port could do a quick assessment to make sure it was safe to put people back in certain areas, after an earthquake for example." "With the drones, via GPS, it assigns a coordinate to every picture where it was taken, so now we can plot those points and it gives you the exact location of the asset and its current condition." Hugo Aguilar, POLB remote pilot: "we're streamlining the process of providing that information not only to engineers but to several stakeholders at the same time." https://www.aapaseaports.com/index.php/2021/09/09/eyes-in-the-sky-ports-continue-to-expand-use-of-drones/
- POLB requires a drone permit ($100 fee, insurance, flight plans, up to 10 days processing) for operations over the port (LA Business Journal, 2017-11-10). https://labusinessjournal.com/manufacturing/international-trade/permits-now-required-drone-operations-long-beach-p/

#### 2.6 Inspection service providers / independent drone pilots (the "user" side)
- Detect Inspections blog (utility ISP workflow; date shows "March 26", year not given) [PUBLIC QUOTE, vendor voice]: "Rejected images, unpaid reflights, inconsistent capture across pilots, manual QA that doesn't scale - these problems compound silently"; "The utility rejects the batch. You eat the reflight."; "Two weeks later, the analytics team flags missing angles and out-of-focus images. Now you're sending a crew back to the site on your own dime." https://detectinspections.com/blog/utility-drone-inspection-workflow
- BigAl07 (forum moderator, 2018-01-12) on utilities [PUBLIC QUOTE]: "They are getting HAMMERED with these same requests...thousands of others...reaching out...each and every day." https://commercialdronepilots.com/threads/what-is-working-now.109/
- On the marketplace model (DroneBase, now Zeitview; forum 2021-02) [PUBLIC QUOTE]: "At the rate of pay you can't afford insurance. But don't expect to earn any real money" (JimD); "the race to the bottom is already won" (JimD); "DroneBase is a bottom feeder IMHO" (BigAl07). https://commercialdronepilots.com/threads/dronebase.3432/
- Anthony Ivory (forum, 2023-02-17) on power-line EMI: "We noticed signal interference began inside 50 ft. A new guy lost one of our drones at 20 feet". https://commercialdronepilots.com/threads/powerline-inspection.4212/
[Inference] ISPs are squeezed between low marketplace rates and utility QA rejections; a tool that catches bad captures in the field and produces the buyer's report format is valuable to them even before AI grading.

#### 2.7 Researchers building for inspectors (what they learned about users)
- Univ. of Houston BridgeEQA (arXiv, submitted 2025-11-16, rev. 2026-04-20): benchmark of "2,200 open-vocabulary question-answer pairs grounded in professional inspection reports" over "200 real-world bridge scenes" with "47.93 images on average per scene" - the task "demands multi-scale reasoning and long-range spatial understanding". https://arxiv.org/abs/2511.12676
[Inference] Real inspection scenes have ~50 images each; report-grounded QA over image sets is exactly the heavy-VLM step in our pipeline, and there is now a public benchmark to validate against.

### 3. Case studies and post-mortems that quantify the pain

| Case | What happened | Why it matters to us | Source |
|---|---|---|---|
| FHWA Visual Inspection Reliability Study (June 2001) | 49 inspectors from 25 states, 10 tasks, 7 bridges: "only 68 percent of the Condition Ratings will vary within one rating point of the average, and 95 percent will vary within two points." In-depth visual inspections "are not likely to detect or identify the specific types of defects for which the inspection is prescribed." Factors: fear of traffic, visual acuity, light, "Inspector Rushed Level". | Inter-inspector disagreement is the baseline our grading must beat; consistency is a sellable feature. | https://www.fhwa.dot.gov/publications/research/nde/01021.cfm |
| Indiana VR consistency study (J. Bridge Eng., Feb 2026) | 24 inspectors from six Indiana districts; "only 30% of inspectors' assigned ratings precisely matched the expected ratings", worst on concrete superstructure. | Same problem persists 25 years later, under the 2022 SNBI. | https://ascelibrary.org/doi/10.1061/JBENF2.BEENG-7583 ; https://rosap.ntl.bts.gov/view/dot/72826 |
| Washer et al. 2020 (cited in VTRC 25-R4) | 40 inspectors measuring the same bridge: crack-area measurement variation "from as low as 18% to often exceeding 100%". | Quantitative grading (area, width) is where automation adds the most consistency. | https://vtrc.virginia.gov/media/vtrc/vtrc-pdf/vtrc-pdf/25-R4.pdf |
| Fern Hollow Bridge collapse, Pittsburgh (Jan 2022; NTSB final Feb 2024) | Probable cause: tie-plate failure "due to corrosion and section loss resulting from the City of Pittsburgh's failure to act on repeated maintenance and repair recommendations from inspection reports"; contributing: "the poor quality of inspections, the incomplete identification of the bridge's fracture-critical members ... and the incorrect load rating calculations". Rated poor since Sept 2011. | Detection existed; prioritization/follow-through failed. A ranked, persistent work queue with "recommended-but-not-done" tracking is the gap. | https://www.ntsb.gov/investigations/Pages/HWY22MH003.aspx ; https://en.wikipedia.org/wiki/Fern_Hollow_Bridge |
| I-40 Hernando de Soto Bridge (Memphis, May 2021) | Fracture found 2021-05-11; "Archived drone footage from May 2019 inspection revealed the fracture"; amateur photos show damage from 2016; mandated hands-on inspections "had not been undertaken"; inspector fired; bridge closed to vehicles ~3 months (to 2021-07-31/08-02). | Exactly our thesis: imagery already contained the defect; nobody triaged it. A cheap first-pass "is damage present?" over archived imagery would have flagged it. | https://en.wikipedia.org/wiki/Hernando_de_Soto_Bridge |
| Vineyard Wind blade failure (2024-07-13) | GE Vernova attributed it to "insufficient bonding" and a quality-control lapse; GE inspected "more than 100 other blades" and removed blades from "at least two turbines"; six Nantucket beaches closed; $10.5M settlement with Nantucket (July 2025). | Offshore blade re-inspection at fleet scale is the burst-demand scenario our two-stage pipeline is built for. | https://en.wikipedia.org/wiki/Vineyard_Wind |
| Raptor Maps Global Solar Reports (2023-2026) | Equipment-driven power loss: 1.61% (2019) -> 3.13% (2022) -> 5.08% (2025); 2022 per-MW loss "$3,350/year"; 2024 "$5,720 per MWdc"; sites with five annual inspections ~3% loss vs ~7% with one; tracker faults ~14% of 2025 losses; average technician responsible for 70% more capacity than five years earlier; US solar jobs +12% vs capacity +286% over five years. Dataset 193 GWdc (2025 report), 373 GWdc (2026 report). | Inspection frequency correlates with recovered revenue; labor scarcity means analysis must be automated. | https://www.pv-magazine.com/2023/03/07/raptor-maps-points-to-growing-problem-of-pv-system-underperformance/ ; https://www.pv-tech.org/pv-project-power-loss-doubled-in-last-five-years-raptor-maps/ ; https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ ; https://raptormaps.com/resources/2025-global-solar-report |
| AEP Ohio 2025 drone pilot | 4% of distribution system, 400k-500k images, 500+ review hours, 150+ tier-one issues. Company-wide AEP cites "30 million customer minutes of interruption" avoided over 2.5 years and "$8 million" saved (vendor page). | The review bottleneck is the wedge; utilities already measure the KPI (CMI) our output should move. | https://www.renewableenergyworld.com/power-grid/how-autonomous-drones-and-ai-are-reshaping-utility-inspection-programs/ ; https://www.skydio.com/customer-stories/american-electric-power-company-aep |
| ODOT drone program | "500TB of archived drone video and imagery"; "$800K+ cost avoidance"; "60% faster" flights. | Archived imagery is an untapped dataset for a retro-triage demo. | https://www.skydio.com/customer-stories/Ohio-Department-of-transportation |
| Caltrans drone adoption | 42 aircraft / 64 pilots (2020); savings "40 percent to 70 percent" for some inspection areas; 2026: $12.4M SMART-funded SOAR autonomous-dock program with Alaska DOT&PF. | Our local DOT already flies; they lack analysis, not aircraft. | https://dot.ca.gov/programs/public-affairs/mile-marker/spring-2020/bridge-inspections-taking-to-the-skies ; https://www.skydio.com/customer-stories/soar-program-brings-autonomous-drone-docks-to-ca-and-ak |

Contradictions / cautions noted:
- Wind market size "$478 million in 2025, 14% CAGR" appears on SkyVisor's page with no external citation - do not use as a sourced number. https://www.skyvisor.ai/en-us/wind-turbine-drone-inspection-2025-u-s-costs-roi-best-practices/
- Turbine inspection prices ($300-600 drone vs $1,500-3,000 rope access) are vendor-stated without sources (SkyVisor, Drone Launch Academy). Treat as anecdotal ranges.
- Raptor Maps loss percentages differ by report vintage and dataset (3.13% for 2022 in the 2023 report; 5.08% for 2025 in the 2026 report). Cite the year and the report.
- A "24.9 MW Sumatra plant, 64,140 modules, 1.05% defect rate" study surfaced in a search snippet but could not be traced to a URL - NOT verified; do not use.
- Zeitview (ex-DroneBase) lists its HQ as San Diego (4275 Executive Square), not Santa Monica. https://www.zeitview.com/about

### 4. Buyer and user personas (KPIs, budget authority)

Each persona below is anchored to a public source; the KPI/budget statements marked [Inference] are our reading, to be validated in interviews.

1. State/County DOT Bridge Program Manager (buyer)
   - Anchors: NBIS 24-month cycle, 3-month data-entry rule (23 CFR 650); Kansas RFP evaluation weights; Dane County penalties.
   - KPIs [Inference]: % inspections on time; % NBI records entered within 3 months; FHWA metrics-review findings; count of poor-condition bridges; backlog of "recommended maintenance" items.
   - Budget: consultant inspection contracts are often 80% federal / 20% local (INDOT RFP). Multi-year (2-4 yr) term contracts; procurement via RFP/prequalification. https://www.in.gov/dot/div/legal/rfp/LPARFP/Archive/2021/may/RFP%202100288.pdf
   - Integration must-have: state system of record (InspectX, HSIS, AASHTOWare BrM) - not Maximo.

2. Consultant Bridge Inspection Team Leader (user; also a buyer of tools)
   - Anchors: NHI 130055/130053/130078/130091 certifications (KDOT); "redundant manual data entries into disparate systems" (VTRC); prefers hybrid automation with human refinement (VTRC).
   - KPIs [Inference]: bridges/day, report rejection rate (Dane: 30-day disapproval loop), office hours per field hour, penalties avoided.
   - Budget [Inference]: firm-level software budgets; low willingness to change field hardware ("previous unsuccessful attempts").

3. Utility Drone/UAS Program Manager (buyer/champion)
   - Anchors: Jake Reed (AEP); ZBlackwood (Oregon PUD); ComEd's Optelos platform.
   - KPIs [PUBLIC QUOTE] "savings realized, our customer minutes of interruption avoided ... mileage that we've flown" (AEP). [Inference] also: images reviewed per analyst-hour, tier-one findings per 1,000 structures, time from flight to work order.
   - Budget [Inference]: program budgets in the low millions at IOUs (AEP cites $8M saved), tens of thousands at small PUDs (Optelos "quite expensive" for a PUD).

4. Utility Asset Management / Reliability Engineer (economic buyer)
   - Anchors: "five or six different groups regularly needed access" (EchoStor/T&D World); SAP/Maximo/GIS integration and SOC2/ISO27001/FedRAMP expectations (Unleash Live).
   - KPIs [Inference]: SAIDI/SAIFI/CMI, wildfire-ignition risk findings closed, regulatory (e.g., CPUC WMP) reporting completeness.

5. Wind Asset Manager / O&M Lead (buyer)
   - Anchors: MidAmerican "data was helter-skelter"; BluEarth "prioritize and manage our repairs"; "little patience for ... false alarms" (SkySpecs).
   - KPIs [Inference]: availability %, blade repair backlog by severity, cost per repair campaign, warranty claims won (needs "1mm/pixel ... GPS metadata" per Drone Launch Academy).
   - Budget [Inference]: annual inspection campaigns priced per turbine; small IPPs and ISPs are the reachable segment (Drone Launch Academy advice).

6. Solar Asset Manager / Analytics Lead (buyer)
   - Anchors: MEI quotes (string/module visibility; centralized inspection history; defined scope of work for crews); Raptor Maps loss stats; IEC 62446-3 spec.
   - KPIs [Inference]: DC health %, kWh recovered per inspection dollar, days from inspection to remediation, lender/insurer report acceptance.
   - Budget [Inference]: per-MW inspection pricing; O&M budgets under pressure from labor shortage (technician covers +70% capacity).

7. Inspection Service Provider / Drone Pilot (user; channel partner)
   - Anchors: Detect Inspections rework quotes; DroneBase pay complaints; BigAl07 on utilities being "HAMMERED".
   - KPIs [Inference]: reflights avoided, report turnaround (solar baseline 5-10 working days), margin per mission.

8. Port Survey / Engineering Director (buyer)
   - Anchors: POLB Director of Survey Kimberley Holtz - GPS-tagged photos plotted to asset locations; disaster/earthquake rapid assessment; permit regime.
   - KPIs [Inference]: time to reopen berths after an event, asset condition inventory completeness.

9. Insurer (property/renewables underwriting & claims) (buyer, later)
   - Anchors: IEC-conformant reports are used by "insurance providers (for compliance documentation)" (Impact Aerial); kWh Analytics presented on solar insurance at RaptorCon (Raptor Maps resources, 2026-05-21). https://raptormaps.com/resources
   - KPIs [Inference]: loss ratio, claim cycle time. Treat as a Phase-2 segment; no primary insurer voice found.

10. County Planning / Code-Enforcement UAS Program (adjacent buyer)
   - Anchor: LA County Planning "owns and operates Skydio and DJI drones" to inspect "large landfills, surface mines, solar farms, tall wireless communications facilities". Contact: UASprogram@planning.lacounty.gov, (213) 974-6483. https://planning.lacounty.gov/unmanned-aircraft-systems-uas-program/

### 5. Weekend customer-discovery plan (USC team, Los Angeles, Sept 25-28, 2026)

Goal: 8-15 real conversations (even 10-minute ones) by Sunday afternoon, logged verbatim, so the Customer Insights slide can say "n=X conversations" truthfully. Everything below is a plan, not a result.

#### 5.1 Target list (22 organizations / roles) - anchor facts verified where a URL is given
Public-sector infrastructure owners (LA):
1. Caltrans District 7 (Los Angeles + Ventura counties; District Director Gloria Roberts) - roles: Structure Maintenance & Investigations (SM&I) South bridge inspectors; District UAS pilots (Caltrans has 64+ certified pilots statewide, SOAR dock program). Ask: what happens to drone imagery after a flight? https://en.wikipedia.org/wiki/California_Department_of_Transportation ; https://dot.ca.gov/programs/public-affairs/mile-marker/spring-2020/bridge-inspections-taking-to-the-skies
2. Caltrans HQ Office of SM&I / Division of Aeronautics UAS Program (Sacramento; remote call) - named in Mile Marker: Erol Kaslan (Chief, SM&I North Investigations).
3. LADWP (HQ 111 N. Hope St; >1.5M electric customers; 7,340 miles of water pipe) - roles: Power System transmission/distribution inspection, Wildfire mitigation, Water System pipeline/reservoir inspection. LADWP drone-program specifics NOT verified - ask. https://en.wikipedia.org/wiki/Los_Angeles_Department_of_Water_and_Power
4. Southern California Edison - roles: Aerial/drone inspection program ("100+ drones", "one of the largest autonomous inspection programs in the country" per Skydio), Wildfire Mitigation image-review team. https://www.skydio.com/customer-stories/sce-scales-drone-inspections-to-transform-grid-safety
5. Port of Long Beach - Director of Survey (Kimberley Holtz, publicly quoted 2021), Engineering Design (wharf/pile inspection), Remote pilot Hugo Aguilar. https://www.aapaseaports.com/index.php/2021/09/09/eyes-in-the-sky-ports-continue-to-expand-use-of-drones/
6. Port of Los Angeles - Engineering Division / Construction & Maintenance (wharf, crane, underwater structures). No public drone quote found - discovery target.
7. LA Bureau of Engineering (City of LA) - Bridge Improvement Program / structural engineering staff (website fetch was blocked; verify contact via eng.lacity.org).
8. LA County Public Works - bridge inspection / maintenance divisions (not researched; verify).
9. LA County Planning UAS Program - UASprogram@planning.lacounty.gov, (213) 974-6483; inspects solar farms and telecom towers by drone. Easiest public-sector warm contact. https://planning.lacounty.gov/unmanned-aircraft-systems-uas-program/
10. LA Metro - facilities/structures inspection (elevated guideways, stations). Not researched; verify.
11. Metropolitan Water District of Southern California - dam/pipeline/reservoir inspection (not researched; verify).

Private asset owners / O&M (California):
12. Terra-Gen (operator of Alta Wind Energy Center, Tehachapi, 1,550 MW / 600 Vestas turbines; 4.2 GW gross portfolio, 34 sites) - roles: wind O&M manager, blade engineer, asset management. https://en.wikipedia.org/wiki/Alta_Wind_Energy_Center ; https://www.terra-gen.com/
13. Other Tehachapi/San Gorgonio wind operators (e.g., Brookfield, EverPower phases of Alta per Wikipedia) - ask via LinkedIn for site O&M leads.
14. Solar O&M / asset managers with California fleets (identify via LinkedIn: "solar asset manager" Los Angeles / San Diego). Public interview-ready names from trade press: Mitchel Gehlig, Matt Messer, Esteban Schrick (MEI - not CA-based; remote).
15. Zeitview (ex-DroneBase; HQ San Diego; solar/wind/roof inspection; "largest drone pilot network") - roles: solar analyst, product manager. Treat as competitor-and-channel; ask about analyst workload and false positives. https://www.zeitview.com/about
16. Local independent drone inspection pilots (find via Commercial Drone Pilots forum "Drone Jobs and Gigs" and LinkedIn "Part 107 Los Angeles inspection"). Ask about deliverable formats and rejections/reflights.

Engineering consultancies (buyers of tools; deliver inspections):
17. Moffatt & Nichol (global HQ Long Beach; ports/marine structures) - waterfront inspection engineers. https://www.moffattnichol.com/about/
18. Bridge inspection consultants with LA offices (e.g., firms prequalified for Caltrans/LA County bridge inspection - verify names on Caltrans/LA County prequalification lists). Ask about InspectX/AASHTOWare workflows and report QA rejections.

Insurers / finance (LA):
19. Farmers Insurance (HQ Woodland Hills; property and small-business commercial lines) - roles: property claims innovation, aerial imagery. No public drone-claims fact found; discovery target. https://en.wikipedia.org/wiki/Farmers_Insurance_Group
20. Mercury Insurance (LA-based; unverified) / renewable-energy insurers via kWh Analytics (SF) - remote.

USC / academic (fast, on campus):
21. USC Sonny Astani Dept. of Civil & Environmental Engineering - Structural Engineering & Infrastructure faculty; USC Center for Autonomy and AI. Ask who at Caltrans/LA they collaborate with; ask for intros. https://cee.usc.edu/
22. USC Facilities Planning & Management - campus bridges/parking structures/roofs; they are an asset owner with inspection contracts (not researched; walk in).

#### 5.2 Outreach message template (email / LinkedIn; ~90 words)
Subject: USC student team - 15 min on how you review inspection imagery?

Hi [Name], I'm [Name], a USC [major] student. This weekend our team is in a 4-day startup sprint on infrastructure inspection. We're NOT selling anything - we're trying to understand how [organization] handles imagery from drone/field inspections today: who reviews it, how long it takes, how findings become work orders. Could you spare 15 minutes by phone/Zoom Friday-Sunday, or point us to the right person? We'll share back a one-page summary of what we learn from all conversations. Thank you - [Name], [phone], [USC email]

Rules for use [team rule]: one follow-up max; never imply a business relationship; never quote anyone by name without explicit permission; offer anonymity ("a bridge inspector at a state DOT").

#### 5.3 Ten-question interview script (15 minutes; open questions first, no pitching until Q10)
1. Walk me through the last inspection your team did that involved photos or video. Who flew/captured, who reviewed, and what happened to the files afterward?
2. Roughly how many images or how many hours of footage does a typical [structure/circuit/turbine/site] produce, and how long does review take per [unit]? (Probe: AEP reported 500+ hours for ~450k images - does that resonate?)
3. What does the deliverable look like - a PDF, entries in a system (InspectX/HSIS/Maximo/SAP/Optelos), a spreadsheet? Who consumes it next?
4. How do you decide what gets fixed first? Is there a written severity/priority scheme (CS1-4, category 1-5, RAG)? Does it differ between inspectors or vendors?
5. Tell me about a time two inspectors (or a vendor and your team) disagreed on a rating. How was it resolved?
6. What do you do with "maybe" findings - AI or human false alarms? How costly is a false positive vs a missed defect for you?
7. What happened after a big event (storm, quake, wildfire)? How many assets had to be assessed, how fast, and what broke in your process?
8. If a tool could pre-screen images and hand you a ranked list with evidence, what would it have to prove before you trusted it? (Probe: accuracy target, audit trail, who is liable.)
9. Who signs off on buying inspection software or services, what budget does it come from, and what would make procurement say no (security, data ownership, integration)?
10. Who else should we talk to - and may we quote you anonymously (role + org type) in a student pitch?

#### 5.4 How to log and quote results honestly
- Create docs/research/interviews/LOG.csv with columns: date_time, channel (call/email/in-person), org_type, role (never name unless permitted), consent_to_quote (yes/anon/no), duration_min, verbatim_quotes (in quotes, exactly as said), paraphrase, pain_score_1to5 (our judgment, labeled), follow_up.
- Verbatim vs paraphrase: only text inside quotation marks that was said or written by the interviewee is a quote. Everything else is paraphrase, labeled.
- Separate evidence classes on the slide: (a) public sources (this file), (b) our interviews (n=X), (c) our inferences. Never blend them.
- No percentages from small n: with fewer than ~15 interviews, report counts ("6 of 9 said ...") not percentages.
- No fabrication: if we get zero interviews in a segment, the slide says so and leans on public quotes with URLs.
- Record refusals and non-responses too (outreach count vs responses) - judges respect honest funnel numbers.
- Keep raw notes (typed during call) in docs/research/interviews/<date>_<orgtype>_<role>.md; quotes on the slide must trace to a raw-notes file.

---

## Key numbers table

| Claim | Value | Source URL | Source date |
|---|---|---|---|
| AEP Ohio 2025 drone pilot - share of distribution system inspected | ~4% | https://www.renewableenergyworld.com/power-grid/how-autonomous-drones-and-ai-are-reshaping-utility-inspection-programs/ | 2026-01-14 |
| AEP Ohio - images collected | 400,000-500,000 | same | 2026-01-14 |
| AEP Ohio - human review time | "500 plus hours" by one person | same | 2026-01-14 |
| AEP Ohio - tier-one issues found | >150 | same | 2026-01-14 |
| AEP - customer minutes of interruption avoided | ~30 million over 2.5 yrs | https://www.skydio.com/solutions/utilities | undated (vendor) |
| AEP - operating cost saved (vendor page) | $8 million | https://www.skydio.com/customer-stories/american-electric-power-company-aep | undated (vendor) |
| Northeast utility storage consumed by inspection media | 8.5 TB of 10 TB | https://www.tdworld.com/smart-utility/article/55242455/modernizing-utility-infrastructure-inspections-where-ai-meets-asset-management | 2024-11-13 |
| Manual image analysis time | 3-5 min per image | same | 2024-11-13 |
| Groups needing access to inspection data | "five or six" | same | 2024-11-13 |
| FHWA reliability study - inspectors / states | 49 / 25 | https://www.fhwa.dot.gov/publications/research/nde/01021.cfm | June 2001 |
| Condition ratings within +/-1 point of mean | 68% (95% within +/-2) | same | June 2001 |
| Indiana VR study - inspectors; ratings matching expected | 24; 30% | https://ascelibrary.org/doi/10.1061/JBENF2.BEENG-7583 | Feb 2026 |
| Crack-area measurement variation among 40 inspectors | 18% to >100% | https://vtrc.virginia.gov/media/vtrc/vtrc-pdf/vtrc-pdf/25-R4.pdf (citing Washer et al. 2020) | Jan 2025 |
| VTRC inspector survey responses | 41 inspectors, 6 engineers, 20 DOT interviews | same | Jan 2025 |
| NBIS routine inspection interval | <= 24 months (48/72 risk-based) | https://www.law.cornell.edu/cfr/text/23/650.311 | current CFR |
| NBIS underwater inspection interval | <= 60 months | same | current CFR |
| NBIS data-entry deadline | within 3 months after field inspection month | https://www.law.cornell.edu/cfr/text/23/650.315 | current CFR |
| TxDOT bridges on NBI | 57,000 | https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections | undated (vendor) |
| US bridges in poor condition | >41,600; 1 in 3 need repair/replacement | https://artbabridgereport.org/ | July 2025 |
| Dane County late-HSIS penalty | $100 per day | https://www.danepurchasing.com/bids/GetBidDocument/4c14a95c-8c4d-41e3-840b-de067fec49fd | 2020-04-20 |
| Dane County evaluation weight - approach / cost | 35% / 5% | same | 2020-04-20 |
| NJDOT BRP-1 research budget | <= $700,000 ($350k/yr) | https://www.nj.gov/transportation/business/research/pdf/ResearchProcureRFPs/2024/RFP_2024-05.pdf | 2024-12-12 |
| Fountain County IN bridge cycle mix | 17 @48 mo, 115 @24 mo, 10 @12 mo; 15 fracture-critical | https://www.in.gov/dot/div/legal/rfp/LPARFP/Archive/2021/may/RFP%202100288.pdf | 2021-05-27 |
| Fountain County funding split | 80% federal / 20% local | same | 2021-05-27 |
| Longmont drone RFP term | 1 yr + 4 renewals | https://proposalalert.com/rfp/overhead-drone-infrastructure-inspection | 2025-01-07 |
| ODOT archived drone media | 500 TB | https://www.skydio.com/customer-stories/Ohio-Department-of-transportation | undated (vendor) |
| ODOT cost avoidance / crack resolution | $800K+ / 0.2 mm | same | undated (vendor) |
| Caltrans drone fleet / pilots | 42 aircraft / 64 pilots | https://dot.ca.gov/programs/public-affairs/mile-marker/spring-2020/bridge-inspections-taking-to-the-skies | Spring 2020 |
| Caltrans savings estimate for some inspection areas | 40-70% | same | Spring 2020 |
| Caltrans/Alaska SOAR program funding | $12.4M (SMART) | https://www.skydio.com/customer-stories/soar-program-brings-autonomous-drone-docks-to-ca-and-ak | undated (vendor) |
| Solar equipment-driven power loss | 2.36% (2021) -> 5.08% (2025) | https://www.pv-tech.org/pv-project-power-loss-doubled-in-last-five-years-raptor-maps/ | 2026-02-26 |
| Solar loss vs inspection frequency | ~3% (5 inspections/yr) vs ~7% (1/yr) | same | 2026-02-26 |
| Tracker faults share of 2025 loss | ~14% (+25% YoY) | same | 2026-02-26 |
| Technician capacity load | +70% capacity per tech vs 5 yrs prior | same | 2026-02-26 |
| Solar loss 2019 -> 2022; $/MW/yr (2022) | 1.61% -> 3.13%; $3,350 | https://www.pv-magazine.com/2023/03/07/raptor-maps-points-to-growing-problem-of-pv-system-underperformance/ | 2023-03-07 |
| Solar revenue loss per MWdc (2024) | $5,720 | https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ | 2026-02-17 |
| Raptor Maps dataset | 193 GWdc (2025 rpt); 373 GWdc (2026 rpt) | https://raptormaps.com/resources/2025-global-solar-report ; https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ | 2026 |
| MEI case: MW restored / time / strings | 3 MW / 3 weeks / "hundreds" offline strings | https://raptormaps.com/blog-posts/raptormaps-mei-casestudy | Sept 2026 |
| IEC 62446-3 thermal resolution | >= 5x5 pixels per cell | https://www.abovesurveying.com/blog/understanding-iec-62446-32017-outdoor-infrared-thermography | 2023-11-01 |
| IEC 62446-3 irradiance; report turnaround | ~600 W/m2; 5-10 working days | https://www.impactaerial.co.uk/2026/06/26/drone-thermal-survey-for-solar-farms-the-2026-guide-to-pv-inspection/ | 2026-06-26 |
| Thermal scan window per day | "four to five, six hours" | https://www.pv-magazine.com/2026/07/10/multi-drone-platform-for-autonomous-solar-inspections-digital-twin-creation/ | 2026-07-10 |
| SkySpecs blades inspected | 275,000 (blog) / 745,000+ (homepage) | https://skyspecs.com/blog/unlocking-wind-energy-efficiency-data-analytics-skyspecs/ ; https://skyspecs.com/ | 2025-03-05 / 2026 |
| Wind data spec for warranty claims | 1 mm/pixel + GPS + timestamps | https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ | 2026-06-01 |
| Turbine drone inspection price (vendor-stated, uncited) | $300-600 visual; $2,000-4,000 advanced | same; https://www.skyvisor.ai/en-us/wind-turbine-drone-inspection-2025-u-s-costs-roi-best-practices/ | 2026 |
| Powerline inspection service price (uncited) | $300-2,000/mile; $150-500/structure | https://uavcoach.com/powerline-inspection-drones/ | 2026-04-12 |
| Vineyard Wind blades inspected / removed | >100 / "at least two turbines" | https://en.wikipedia.org/wiki/Vineyard_Wind | 2024-2025 |
| Vineyard Wind settlement with Nantucket | $10.5M | same | July 2025 |
| Fern Hollow poor rating start | Sept 2011 (collapse Jan 2022) | https://en.wikipedia.org/wiki/Fern_Hollow_Bridge | 2024 |
| I-40 bridge fracture visible in drone footage | May 2019 (found May 2021; ~3-month closure) | https://en.wikipedia.org/wiki/Hernando_de_Soto_Bridge | 2021 |
| Alta Wind Energy Center | 1,550 MW; 600 Vestas turbines; Tehachapi | https://en.wikipedia.org/wiki/Alta_Wind_Energy_Center | 2022 |
| Terra-Gen portfolio | 4.2 GW; 34 sites | https://www.terra-gen.com/ | 2026 |
| LADWP scale | >1.5M electric customers; 7,340 mi water pipe | https://en.wikipedia.org/wiki/Los_Angeles_Department_of_Water_and_Power | 2019-2022 data |
| SPS Texas grant incl. drone pole inspection | $113M | https://www.utilitydive.com/news/southwestern-public-service-reliability-grant-texas-puc/824464/ | 2026-07-06 |
| BridgeEQA benchmark | 2,200 QA pairs; 200 scenes; ~48 images/scene | https://arxiv.org/abs/2511.12676 | 2025-11 / 2026-04 |
| UMass Lowell blade-inspection AI grant | ~$356,000 | https://www.uml.edu/news/stories/2025/sabato-niezrecki-nowrdc-grant.aspx | 2025-01-31 |

---

## Implications for our product / edge

1. Sell the WORK LIST, not the model. Every RFP deliverable is "recommended maintenance per structure" entered into the owner's system. Our heavy-VLM output should be a ranked, evidence-linked list (image crop + grade + rationale + location) that exports as (a) element/condition-state records for DOT systems (InspectX/HSIS/AASHTOWare), (b) IEC-style anomaly registers for solar, (c) work-order payloads for Maximo/SAP. [Inference from Sections 1.1-1.9]
2. The cheap first-pass judge is justified by the numbers: 3-5 min/image manual vs 400-500k images/yr for a 4% pilot. Pitch the small-VLM screen as "no human looks at the images with nothing in them" - but we must MEASURE our own recall on a labeled set before claiming any percentage (rules forbid fabricated performance). [Sources 2.1; Inference]
3. Consistency is a feature buyers can verify: the 68% / 30% / >100% variability numbers give us a benchmark story - "same grade for the same defect every time, with an audit trail" - and the VTRC finding says keep the human in the loop ("hybrid automation ... inspector refines automated labels"), so design for review-and-confirm, not auto-approve. [Sources 3]
4. Prioritization + persistence is the unowned gap. Fern Hollow and I-40 were failures to act on already-documented findings. A "recommended-but-not-done" tracker with time-since-first-flag and risk escalation is differentiated vs vendors that stop at the report. [Sources 3]
5. False alarms are a churn risk, not a footnote. Wind buyers have "little patience for ... even small numbers of false alarms"; solar analysts must rule out bird droppings/shadows. Show the RGB/thermal cross-check and per-finding confidence, and let users mute classes. [Sources 2.3, 1.7]
6. Integration and data ownership are procurement gates: expect "all data ... property of the County" clauses, SOC 2/ISO 27001 questions, and on-prem/edge asks from utilities. Position from day one as owner-owned data, exportable, with an on-prem path. [Sources 1.1, 1.9]
7. Go-to-market wedge for first 100 customers [Inference from 1.8, 2.6]: (i) inspection service providers and engineering consultants who must produce RFP-shaped reports and eat reflights; (ii) small/municipal utilities and PUDs that find Optelos-class tools "quite expensive"; (iii) independent wind/solar O&M and small IPPs. Large IOUs and OEM-locked fleets come later through the ISPs.
8. Demo data exists in public: archived drone imagery is piling up (ODOT 500 TB); a demo of "retro-triage" over a public bridge/blade/solar image set, ending in a prioritized queue and an export file, mirrors the exact buyer deliverable.
9. Disaster mode is a credible extension, not the core: POLB bought drones "for disaster situations ... after an earthquake"; Vineyard Wind forced 100+ blade re-inspections. Same pipeline, burst load. [Sources 2.5, 3]

---

## Open questions / gaps

- No Reddit content could be retrieved (blocked); r/drones, r/StructuralEngineering, r/solar, r/NDT voices are absent. The Commercial Drone Pilots forum was the only fetchable practitioner community.
- No retrievable RFP documents for wind, solar, port/underwater, or telecom inspection services; only bridge and one municipal-utility drone RFP. Deliverable specs for those segments are inferred from provider pages and IEC 62446-3.
- Utility image volumes for PG&E and SCE (the local IOUs) were not found; SCE's public pages defer to its Wildfire Mitigation quarterly progress reports (not fetched).
- No public per-turbine or per-farm analyst review-hours figure for wind (AEP's 500 hours is a distribution utility). SkySpecs damage-prevalence-by-severity statistics not found.
- No inter-inspector disagreement rate for wind blade or solar thermal grading (only bridges).
- LADWP, Port of LA, LA Metro, LA BOE, LA County Public Works: no public drone/inspection-workflow facts found; they are discovery targets, not documented.
- Insurer voice is absent; only indirect signals (IEC reports "for compliance documentation"; kWh Analytics session).
- Pricing figures (per turbine, per mile, per MW) are all vendor/blog-stated without primary sources.
- The "24.9 MW Sumatra / 64,140 modules / 1.05% defect" statistic is unverified and excluded.
- Vendor customer stories (Skydio, SkySpecs, Raptor Maps) are undated and promotional; quotes are attributed to named people but selected by the vendor.

---

## Sources

1. https://www.renewableenergyworld.com/power-grid/how-autonomous-drones-and-ai-are-reshaping-utility-inspection-programs/ - Renewable Energy World (2026-01-14): AEP Ohio pilot, 400-500k images, 500+ review hours, Jake Reed quotes.
2. https://www.tdworld.com/smart-utility/article/55242455/modernizing-utility-infrastructure-inspections-where-ai-meets-asset-management - T&D World (2024-11-13), Chuck Salvo/EchoStor: 8.5 of 10 TB, 3-5 min/image, 5-6 groups.
3. https://www.fhwa.dot.gov/publications/research/nde/01021.cfm - FHWA Reliability of Visual Inspection (2001): 49 inspectors, 68%/95% variability.
4. https://ascelibrary.org/doi/10.1061/JBENF2.BEENG-7583 - J. Bridge Eng. (Feb 2026): Indiana VR consistency study, 30% match.
5. https://rosap.ntl.bts.gov/view/dot/72826 - ROSA P record of the Indiana VR study.
6. https://vtrc.virginia.gov/media/vtrc/vtrc-pdf/vtrc-pdf/25-R4.pdf - VTRC 25-R4 (Jan 2025): AR/AI bridge inspection, inspector surveys, Washer 2020 variation.
7. https://www.danepurchasing.com/bids/GetBidDocument/4c14a95c-8c4d-41e3-840b-de067fec49fd - Dane County RFP 120048 (2020): bridge inspection deliverables, HSIS, penalties, data ownership.
8. https://www.sos.ks.gov/publications/register/Volume-44/Issues/Issue-16/04-17-25-53025.html - Kansas DOT embedded bridge inspection RFP (Apr 2025): InspectX, NHI courses, weights.
9. https://www.in.gov/dot/div/legal/rfp/LPARFP/Archive/2021/may/RFP%202100288.pdf - INDOT/Fountain County bridge inspection RFP (2021): cycle table, funding split.
10. https://www.nj.gov/transportation/business/research/pdf/ResearchProcureRFPs/2024/RFP_2024-05.pdf - NJDOT BRP-1 RFP (Dec 2024): text mining/image recognition/drone guidance, $700k.
11. https://proposalalert.com/rfp/overhead-drone-infrastructure-inspection - Longmont Power & Communication drone inspection RFP (Jan 2025).
12. https://www.law.cornell.edu/cfr/text/23/650.311 - 23 CFR 650.311 inspection intervals.
13. https://www.law.cornell.edu/cfr/text/23/650.315 - 23 CFR 650.315 inventory/element-level data, 3-month entry.
14. https://artbabridgereport.org/ - ARTBA Bridge Report (July 2025): 41,600 poor bridges.
15. https://www.ntsb.gov/investigations/Pages/HWY22MH003.aspx - NTSB Fern Hollow probable cause and findings.
16. https://en.wikipedia.org/wiki/Fern_Hollow_Bridge - Fern Hollow timeline (poor since 2011).
17. https://en.wikipedia.org/wiki/Hernando_de_Soto_Bridge - I-40 fracture; 2019 drone footage; closure.
18. https://en.wikipedia.org/wiki/Vineyard_Wind - 2024 blade failure, GE Vernova root cause, re-inspections, settlement.
19. https://www.pv-tech.org/pv-project-power-loss-doubled-in-last-five-years-raptor-maps/ - PV Tech (2026-02-26): Raptor Maps 2026 report numbers.
20. https://www.pv-magazine.com/2023/03/07/raptor-maps-points-to-growing-problem-of-pv-system-underperformance/ - pv magazine (2023): earlier Raptor Maps report numbers.
21. https://solarquarter.com/2026/02/17/benchmarking-dc-health-protecting-revenue-in-expanding-solar-fleets/ - SolarQuarter (2026-02-17): $5,720/MWdc, 193 GWdc.
22. https://raptormaps.com/resources/2025-global-solar-report - Raptor Maps report landing page (373 GWdc for 2026 edition).
23. https://raptormaps.com/blog-posts/raptormaps-mei-casestudy - Raptor Maps / Madison Energy Infrastructure case study (Sept 2026) with named quotes.
24. https://raptormaps.com/resources - Raptor Maps resources list (case studies, kWh Analytics insurance session).
25. https://skyspecs.com/ - SkySpecs homepage: customer testimonials (MidAmerican, BluEarth, NTR), 745k blades.
26. https://skyspecs.com/blog/unlocking-wind-energy-efficiency-data-analytics-skyspecs/ - SkySpecs blog (2025-03-05): talent shortage, false alarms, 275k blades.
27. https://jobs.techstars.com/companies/skyspecs/jobs/68271601-internal-blade-inspection-technician-junior-and-senior-positions-available - SkySpecs blade technician job posting (rotation, hours).
28. https://www.uml.edu/news/stories/2025/sabato-niezrecki-nowrdc-grant.aspx - UMass Lowell (2025-01-31): blade inspection AI grant, status-quo description.
29. https://dronelaunchacademy.com/resources/drone-wind-turbine-inspection-2/ - Drone Launch Academy (2026): wind inspection pricing, buyer targeting, 1mm/pixel spec.
30. https://www.skyvisor.ai/en-us/wind-turbine-drone-inspection-2025-u-s-costs-roi-best-practices/ - SkyVisor (2026): uncited market size and cost ranges (flagged).
31. https://uavcoach.com/powerline-inspection-drones/ - UAV Coach (2026-04-12): powerline inspection cost benchmarks.
32. https://unleashlive.com/blog/how-utilities-can-unlock-the-value-of-drone-and-ai-inspections-for-utility-asset-monitoring/ - Unleash Live (2025-10-16): utility pain framing, integrations, security certs (vendor).
33. https://detectinspections.com/blog/utility-drone-inspection-workflow - Detect Inspections: ISP rework/reflight pain (vendor).
34. https://www.utilitydive.com/news/southwestern-public-service-reliability-grant-texas-puc/824464/ - Utility Dive (2026-07-06): SPS $113M grant incl. drone pole inspection.
35. https://www.utilitydive.com/news/faa-uav-drones-utility-inspection-bvlos/756610/ - Utility Dive (2025-08-05): BVLOS rule timeline.
36. https://www.skydio.com/solutions/utilities - Skydio utilities page: AEP quote (30M customer minutes), named utility customers.
37. https://www.skydio.com/customer-stories/american-electric-power-company-aep - Skydio/AEP story ($8M saved).
38. https://www.skydio.com/customer-stories/Ohio-Department-of-transportation - Skydio/ODOT story: 500 TB, $800K+, quotes from Jamie Davis and Daniel Breda.
39. https://www.skydio.com/customer-stories/texas-dot-conducts-safer-more-efficient-bridge-inspections - Skydio/TxDOT story: 57,000 bridges, quotes.
40. https://www.skydio.com/customer-stories/massdot-modernizes-infrastructure-oversight-with-drone-technology - Skydio/MassDOT story: 30 pilots, Chris Grazioso quote.
41. https://www.skydio.com/customer-stories/soar-program-brings-autonomous-drone-docks-to-ca-and-ak - Skydio/Caltrans SOAR ($12.4M).
42. https://www.skydio.com/customer-stories/sce-scales-drone-inspections-to-transform-grid-safety - Skydio/SCE story (100+ drones).
43. https://www.skydio.com/customer-stories/comed - Skydio/ComEd story (Optelos platform).
44. https://www.skydio.com/customer-stories - Skydio customer story index (utilities, DOTs).
45. https://dot.ca.gov/programs/public-affairs/mile-marker/spring-2020/bridge-inspections-taking-to-the-skies - Caltrans Mile Marker (Spring 2020): 42 drones, 64 pilots, 40-70% savings.
46. https://en.wikipedia.org/wiki/California_Department_of_Transportation - Caltrans districts (District 7 = LA + Ventura).
47. https://dot.ca.gov/caltrans-near-me/district-7 - Caltrans District 7 page (Director Gloria Roberts).
48. https://www.aapaseaports.com/index.php/2021/09/09/eyes-in-the-sky-ports-continue-to-expand-use-of-drones/ - AAPA Seaports (2021-09-09): Port of Long Beach quotes (Holtz, Aguilar).
49. https://labusinessjournal.com/manufacturing/international-trade/permits-now-required-drone-operations-long-beach-p/ - LA Business Journal (2017-11-10): POLB drone permit rules.
50. https://planning.lacounty.gov/unmanned-aircraft-systems-uas-program/ - LA County Planning UAS Program (sites inspected, contact).
51. https://en.wikipedia.org/wiki/Los_Angeles_Department_of_Water_and_Power - LADWP scale and HQ.
52. https://en.wikipedia.org/wiki/Alta_Wind_Energy_Center - Alta Wind (Tehachapi) capacity/operators.
53. https://www.terra-gen.com/ - Terra-Gen portfolio (4.2 GW, 34 sites).
54. https://www.zeitview.com/about - Zeitview (ex-DroneBase) HQ San Diego, business description.
55. https://www.moffattnichol.com/about/ - Moffatt & Nichol, global HQ Long Beach, ports practice.
56. https://en.wikipedia.org/wiki/Farmers_Insurance_Group - Farmers Insurance HQ Woodland Hills.
57. https://cee.usc.edu/ - USC Sonny Astani CEE department research areas/centers.
58. https://commercialdronepilots.com/threads/data-analysis-and-drone-operations-management.2433/ - Forum (2019): Oregon PUD pilot on data volume and Optelos cost.
59. https://commercialdronepilots.com/threads/what-is-working-now.109/ - Forum (2018): which inspection markets pay; utilities "HAMMERED".
60. https://commercialdronepilots.com/threads/dronebase.3432/ - Forum (2021): pilot views on DroneBase pay.
61. https://commercialdronepilots.com/threads/how-do-you-currently-deliver-the-data.4098/ - Forum (2022): wind deliverable formats.
62. https://commercialdronepilots.com/threads/powerline-inspection.4212/ - Forum (2022-2024): powerline inspection equipment/EMI.
63. https://commercialdronepilots.com/forums/ - Forum index (Wind, Power Lines, Solar, Insurance subforums) for further discovery.
64. https://www.abovesurveying.com/blog/understanding-iec-62446-32017-outdoor-infrared-thermography - IEC 62446-3 explainer (5x5 px/cell).
65. https://www.impactaerial.co.uk/2026/06/26/drone-thermal-survey-for-solar-farms-the-2026-guide-to-pv-inspection/ - Impact Aerial (2026-06-26): irradiance, 5-10 day reports.
66. https://www.impactaerial.co.uk/2026/07/10/drone-thermal-survey-for-solar-farms-the-ultimate-guide-to-pv-asset-optimisation/ - Impact Aerial (2026-07-10): RAG severity, stakeholders.
67. https://www.pv-magazine.com/2026/07/10/multi-drone-platform-for-autonomous-solar-inspections-digital-twin-creation/ - pv magazine (2026-07-10): vHive quotes on thermal window.
68. https://www.pv-magazine.com/webinars/how-to-make-the-right-inspection-decisions-for-solar-assets-from-the-factory-to-the-field/ - pv magazine webinar (2026-02-04): named inspection experts.
69. https://arxiv.org/abs/2511.12676 - BridgeEQA benchmark (2025/2026): inspection-report-grounded QA over bridge image sets.
