# Problem Statement

| Field | Value |
|---|---|
| Project | Origin Weekend Fall 2026, Prompt D (Infrastructure & Resilience) |
| Version | 1.0 (sourced; v0.1 draft superseded 2026-09-24) |
| Date | 2026-09-24 |
| Owner | Founding team |
| Status | For team review. Wedge choice is Proposed in `docs/decisions.md` D-001. |

**Citation key.** R01..R09 = the notes in `docs/research/`. Labels per `docs/decisions.md` D-011: [Sourced: Rxx], [Inference], [Assumption].

## 1. The prompt we are answering

> **Prompt D:** How can we detect infrastructure damage and failures before they become expensive, and rapidly prioritize recovery when they occur?

The prompt's own framing: utilities, telecoms, transportation networks, insurers, industrial operators and infrastructure owners spend billions inspecting, maintaining and repairing physical assets. Much of that work is manual and reactive. Disasters force organizations to assess thousands of assets while every hour of downtime compounds losses. Meanwhile satellites, drones, vehicles, phones, cameras and sensors produce more physical-world imagery than ever. The strongest solutions serve **everyday inspection and maintenance workflows first**, with disasters as an additional high-value application.

## 2. The problem in one sentence

**Infrastructure owners and the inspection providers who serve them now capture far more imagery than they can analyze, so damage is graded late, inconsistently, and without a defensible priority order. The result is avoidable failures, expensive reactive repairs, and slow disaster recovery.**

## 3. Where the bottleneck actually is

Capture is no longer the constraint. Drone inspection of a wind turbine takes 15 to 45 minutes at $300 to $600 versus 3 to 6 hours at $1,500 to $3,000 by rope access; helicopter line patrol costs $1,200 to $1,600 per mile versus $200 to $300 by drone [Sourced: R04]. The constraint has moved downstream:

1. **Image overload.** AEP Ohio's 2025 drone pilot covered about 4 percent of its distribution system, produced 400,000 to 500,000 images, and one person spent more than 500 hours reviewing them [Sourced: R08]. Post-storm drone campaigns generate 47 to 369 GB per day [Sourced: R03].
2. **Inconsistent grading.** In FHWA's study of 49 inspectors across 25 states, only 68 percent of condition ratings fell within one point of the mean; in a 2026 Indiana study only 30 percent of ratings matched the expected value; manual crack-area measurements vary from 18 percent to over 100 percent [Sourced: R08]. EPRI found agreement on any one blade damage category was rare and recommends treating every category as uncertain by one level [Sourced: R05].
3. **Slow, unstructured reporting.** Public solar guidance quotes 24 to 72 hours for an AI report and 3 to 5 business days end to end; most vendors publish no turnaround at all [Sourced: R01]. Bridge inspectors describe redundant manual data entry into disparate systems and difficulty locating defects from narrative descriptions [Sourced: R08].
4. **No consequence-aware prioritization.** NTSB found the Fern Hollow Bridge collapsed because the city failed to act on repeated maintenance recommendations from inspection reports; the I-40 Hernando de Soto fracture was visible in 2019 drone footage but not acted on until 2021 [Sourced: R08]. Bridges alone carry a $467B repair backlog across 624,167 structures, 41,677 of them in poor condition [Sourced: R04].
5. **Vertical silos.** Every wind vendor found is blade-only, every solar vendor PV-only, and the cross-sector players are service companies with per-vertical pipelines; none spans wind, solar, bridges, underwater and radiography in one engine [Sourced: R01].
6. **Disasters break the process entirely.** Duke Energy's 2024 hurricane season cost about $2.8B net of insurance and Hurricane Milton alone required 16,000 workers and 1,560 pole replacements [Sourced: R04]. The 2025 Los Angeles fires damaged or destroyed more than 18,189 structures; a FEMA declaration for the March 2025 Oklahoma wildfires took two months [Sourced: R03].

## 4. Who experiences it

| Segment | Role feeling the pain | What they need | Evidence |
|---|---|---|---|
| Transportation agencies and their inspection consultants (**primary wedge, D-001**) | Bridge inspection engineer at a consulting firm or county | Element-level condition states that fit federal reporting, with CS3/CS4 photo documentation and a per-structure work list, entered into the state system on deadline | RFPs from Dane County WI, Kansas DOT, INDOT and NJDOT specify exactly this; one fines $100 per day for late entry [Sourced: R08] |
| Wind and solar owners and O&M providers (**secondary, D-002**) | O&M lead, reliability engineer | Faster blade and thermal anomaly triage, graded on the scales OEMs and insurers accept | Solar equipment-driven loss rose from 2.36 percent (2021) to 5.08 percent (2025); a technician now covers 70 percent more MW than five years ago [Sourced: R04, R08] |
| Drone and inspection service providers | Owner-operator, chief pilot | An analytics layer they can resell so they compete on more than flight time | DSPs must now deliver "AI-ready, utility-grade" data; 15 to 25 percent of DSP imagery needs remediation [Sourced: R09] |
| Utilities (electric, telecom) | Asset manager, wildfire mitigation lead | Pole, conductor, insulator and tower defect triage across hundreds of thousands of assets | SCE runs 200,000+ inspections a year; PG&E aerially inspected 220,000 poles in 2024-25 [Sourced: R02] |
| Ports, offshore, marine owners | Port or marine engineer | Underwater structure and hull condition from ROV or diver video without weeks of review | Hull report AI exists at about 83 to 90 percent accuracy from one vendor; class surveyors stay in the loop [Sourced: R03] |
| Industrial operators | Inspection or NDT lead | Weld radiograph screening tied to code acceptance criteria | A certified interpreter must still sign; about 30 percent of NDT personnel are over 55 [Sourced: R03, R04] |
| Insurers, emergency managers | Claims, CAT and resilience teams | Rapid, consistent post-event grading | FEMA's 2025 PDA guide invites analytics on imagery; existing products grade buildings, not infrastructure [Sourced: R03] |

The initial wedge and the order of the other segments are recorded in `docs/decisions.md` D-001, D-002 and D-003, with the rationale and the alternatives rejected.

## 5. Why existing solutions leave the problem open (hypotheses and verdicts)

Verdicts come from the competitor research; details in `docs/research/00_research_brief.md` section 2.

- **H1. Single-vertical, closed-model tools.** *Supported.* Incumbents sell closed-vocabulary detectors per asset class [Sourced: R01, R02].
- **H2. Detection without industry-native grading.** *Supported.* Vendors advertise "severity ratings" without publishing definitions or per-finding rationale; no vendor found ships MBEI condition states with the clause cited [Sourced: R01, R02].
- **H3. No prioritization tied to consequence.** *Partially supported.* SkySpecs and Raptor Maps express findings in energy or dollar terms, but no cross-asset, consequence-ranked work queue was found [Sourced: R01].
- **H4. Enterprise-only economics.** *Supported.* Every analytics incumbent is quote-only except Scopito; small providers are left with AI-less generic tools at about $300 per month [Sourced: R01, R09].
- **H5. Poor fit for thermal, radiographic, and underwater imagery.** *Partially supported.* Thermal is well served inside solar; radiography software is sold on-prem to manufacturers; underwater AI is a thin bolt-on to hardware; nobody spans modalities [Sourced: R01, R03].
- **H6. Nothing built for the disaster surge.** *Refined.* Insurers get building-level classes within 24 to 48 hours from satellite and aerial providers; nobody grades engineered infrastructure after an event [Sourced: R03].

## 6. Why now

- **Vision-language models (VLMs) changed the cost of specialization.** Structured JSON output is generally available on the major model APIs and on local models; a grader can be prompted with the standard's own tables [Sourced: R06].
- **Small VLMs make a cheap first pass possible.** Apache-2.0 models of 2 to 8 billion parameters run on a laptop; a deployed pre-filter cut expensive VLM calls by 240x; grading 1,000 frames costs about $10 heavy-only or about $3 with a local gate [Sourced: R06].
- **The literature validates the shape but not the shortcut.** A grounded detector-plus-model pipeline produced a 4 percent hallucination rate versus 65 percent for a zero-shot VLM; frontier models are weak at localizing small defects [Sourced: R02, R06]. That is why the product grounds, constrains and audits rather than trusting a raw model.
- **Capture hardware is commoditized.** Skydio is valued at $4.4B and 49 of 50 state DOTs use its drones, yet its bridge case studies contain no defect grading [Sourced: R02].
- **Regulatory and climate pressure is rising.** NBIS routine inspections at most every 24 months; SNBI element-level data due 2028-03-15; FAA Part 108 expected by end of 2026 will raise image volumes; California wildfire plans mandate more frequent inspections [Sourced: R02, R04]. About 30 percent of NDT personnel are over 55 and solar jobs grew 12 percent while capacity grew 286 percent [Sourced: R04].

## 7. What we are building (one paragraph)

An imagery-agnostic inspection grading layer. Users upload photos or video frames from drones, ROVs, handheld cameras, thermal sensors or radiographic systems. A small local VLM gates every frame for usability and the presence of damage. Flagged frames are cropped and graded by a heavy VLM on the customer's industry-native scale with the verbatim criterion matched, plus a unified S0 to S4 severity, a confidence, and an evidence crop. Findings roll into a prioritized work queue that weights severity, asset criticality and consequence, which a qualified inspector reviews, overrides and exports. In a disaster, the same pipeline runs in surge mode: triage-first, portfolio-wide, in hours. Requirements are in `docs/PRD.md`.

## 8. Scope for this hackathon

**In scope (by Sunday 2026-09-27, 11:59 PM PT):**
- A working pipeline on real public imagery for bridge elements (primary) and PV thermal modules (secondary), plus post-disaster UAV imagery in surge mode, demonstrating the cascade, industry-native grading and a prioritized queue (D-001 to D-003, D-006).
- Measured gate and grading accuracy on a frozen held-out set with confidence intervals, reported honestly (D-007).
- Customer evidence: public procurement documents and practitioner quotes from R08, plus any interviews completed over the weekend, clearly separated from inference.
- The 6-slide deck, a 30 to 60 second demo video, and a Devpost submission.

**Out of scope for the weekend:** flight operations, drone hardware, custom model training (D-013), integrations beyond CSV or JSON export, and any accuracy claim we did not measure.

## 9. How we will know the problem is worth solving

- Asset owners or service providers confirm that image review and inconsistent grading, not capture, is their bottleneck. Public evidence already points this way (section 3); interviews will test it.
- Public RFPs and industry standards show buyers ask for graded, standards-aligned outputs, not raw detections. *Confirmed for bridges* [Sourced: R08].
- Our measured cascade cost per 1,000 images is a fraction of manual review at prevailing rates. Expected order of magnitude is single-digit dollars per 1,000 frames [Sourced: R06]; the measured figure comes from eval_v1.
- At least one segment shows a sales cycle a student team could realistically close within months. Consultants and DSPs, not Tier-1 utilities, whose trial-to-award has run about three years [Sourced: R09].

## 10. Open questions

1. ~~Which wedge?~~ Proposed in D-001 and D-002; team confirms Fri 2026-09-25 09:00.
2. ~~Which grading scales?~~ Mapped in R05 and `docs/PRD.md` section 7; MVP speaks MBEI/NBI, ISO 4628-3, IEC TS 62446-3 CoA and FEMA PDA.
3. How do frontier VLMs actually perform on thermal inputs versus RGB for our data? Answered by eval_v1 on InfraredSolarModules.
4. What is the honest measured accuracy on eval_v1, and which failure modes must the UI surface? Answered Saturday.
5. Who pays first? Hypothesis in D-008: consultants and DSPs per asset; tested in interviews.

## Related documents

- `docs/PRD.md` - product requirements
- `docs/decisions.md` - decision log
- `docs/implementation_plan.md` - build plan for the weekend
- `docs/progress.md` - running progress log
- `docs/changelog.md` - document and product change history
- `docs/documentation.md` - documentation index and technical notes
- `docs/research/00_research_brief.md` - synthesis of the research notes
- `docs/research/` - sourced research notes R01 to R09
