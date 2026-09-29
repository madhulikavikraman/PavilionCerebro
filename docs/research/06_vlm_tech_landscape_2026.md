# 06 - VLM Technical Landscape for Visual Infrastructure Inspection (2025-2026)

Research angle: `vlm_tech_landscape_2026`
Researched: 2026-09-24 (Thursday evening PT), for Origin Weekend Fall 2026 (Prompt D: infrastructure damage detection and recovery prioritization).
Method: 14 web searches + ~45 page fetches (official vendor docs, arXiv abstracts, model cards, dataset pages). Every number carries a source URL; where a source could not be read, the item is marked **not found** or **not verified**. Items marked **Inference:** are my derivation from cited facts, not a published number.

---

## Summary

1. **The two-stage cascade the team proposed is exactly what the 2025-2026 literature converged on** - a cheap detector/small VLM as a pre-filter that "triggers an expensive VLM only when pre-filters activate," cutting VLM calls 240x in one deployed system [42]; MLLM-based cascades from image-level to patch-level crack classification in steel bridges [30]; a detector + LMM orchestrator + evidence-grounded reflection loop for X-ray NDT (F1 96.54% on GDXray+) [36]; and a VLM + "quality guard agent" that rejects low-quality outputs before priority scoring for Japanese bridge inspection [34].
2. **Frontier VLMs are good at image-level "is there damage / what kind" and weak at precise localization of small defects.** MMAD (ICLR 2025, 39,672 questions / 8,366 industrial images): best commercial model GPT-4o averaged 74.9%, "inadequate for practical industrial deployment," weakest on small defects and localization [29]. InspectVLM (ICCV 2025 workshop) found a fine-tuned Florence-2 "performs competitively on image-level classification" but produces "degenerate outputs for fine-grained object detection" and "defaults to memorized language responses regardless of visual input" [28]. A 2025 benchmark of GPT-4o/Gemini/Claude on COCO-style tasks: "not close to the state-of-the-art specialist models at any task" [40]. Anthropic's own docs: "Claude's coordinate and localization outputs are approximate" [2].
3. **Therefore: localize with a specialist/zero-shot detector, grade with the VLM on a crop.** Weld-LLaVA (2026) used YOLOv8 candidate boxes drawn as colored visual prompts + CoT fine-tuning of LLaVA-1.5-7B to reach 87.13% VQA classification accuracy, beating GPT-4o, Claude 3.7 Sonnet and Qwen2.5-VL-72B zero-shot [35]. A July 2026 paper shows cropping with bounding boxes "significantly improves grading accuracy and reduces FLOPs" for 4B-72B models [44]. Zero-shot localizers with permissive licenses exist today: Grounding DINO (Apache-2.0, 48.4 COCO zero-shot AP) [46], OWLv2 (Apache-2.0, 0.2B) [47], Florence-2 (MIT, 37.5 zero-shot COCO mAP) [23]; SAM 3 / 3.1 (848M params, proprietary "SAM License") adds text/exemplar-prompted segmentation [45].
4. **Small/edge judge candidates that actually fit a laptop in 2026:** Qwen3-VL-2B/4B/8B (Apache-2.0, Ollama pulls 1.9 / 3.3 / 6.1 GB, native 2D grounding) [18][19]; Moondream 3.1 9B-A2B (2B active, native detect/point/segment, but proprietary "Moondream License", >=10 GB VRAM or GGUF CPU) [15]; Gemma 4 E2B/E4B (Apache-2.0, native `[y1,x1,y2,x2]` bbox output, configurable 70-1120 image tokens, runs on Raspberry Pi 5) [21]; SmolVLM2 256M/500M/2.2B (Apache-2.0, runs in free Colab / on iPhone, no grounding) [12][13]; InternVL3.5-2B (Apache-2.0) [24]; Florence-2 0.23B/0.77B (MIT, detection + grounding but not a chat model) [23]. Phi-4-multimodal (5.6B, MIT) [26] and MiniCPM-V 4.5 (8.7B, Apache-2.0) [27] are stronger but heavier and lack documented grounding.
5. **Frontier grader pricing (official, Sept 2026):** Claude Haiku 4.5 $1/$5, Sonnet 5 $2/$10, Opus 5.5 $4/$20, Fable 5.1 $10/$50 per MTok, Batch API 50% off [1][5]. Claude images cost `ceil(w/28) x ceil(h/28)` visual tokens; a 1000x1000 image = 1,296 tokens = about $1.30 per 1,000 images on Haiku 4.5 [2]. OpenAI GPT-5.4 $2.50/$15, GPT-5.4-mini $0.75/$4.50, GPT-5.4-nano $0.20/$1.25, GPT-5.5 $5/$30 [6]. Gemini 2.5 Flash $0.30/$2.50, 3.5 Flash-Lite $0.30/$2.50, 3.8 Flash $0.75/$3.75 (promo; doubles after 2026-12-31) [8].
6. **Structured JSON is solved on all three clouds and locally:** Claude structured outputs are GA on Haiku 4.5 / Sonnet 5 / Opus 5.5 / Fable 5.1 via `output_config.format = json_schema` [4]; Gemini returns `box_2d` normalized 0-1000 and segmentation polygons [9]; Ollama constrains any local model (including vision models) to a JSON schema via `format` [50]. Coordinate conventions differ per vendor (Claude: absolute pixels, explicitly "does not work well" with 0-1000 normalized [3]; Gemini: 0-1000 normalized [9]; Qwen3-VL: relative coords [18]; Moondream: normalized 0-1 [16]) - the pipeline must normalize.
7. **Cost model (derived, see Section 6):** heavy-only grading of 1,000 1080p drone frames on Sonnet 5 is about $10; a local Qwen3-VL judge passing 30% costs about $3 (plus laptop compute); a Haiku 4.5 judge + 30% Sonnet 5 is about $5.1; Batch API halves the Claude numbers. Savings scale with the "no damage" fraction, which is high in routine inspection and lower in disaster response.
8. **Thermal and X-ray need preprocessing before any VLM sees them.** Claude accepts only JPEG/PNG/GIF/WebP and "does not parse or receive any metadata from images" [2] - so radiometric temperature data in R-JPEG/TIFF is lost unless you extract it first (FlirImageExtractor, MIT, exiftool-based, supports FLIR + DJI H20T/M3T/M30T) [51] and bake it into a normalized image plus a text block of temperature statistics. The 2026 AIRT paper explicitly names "the domain gap between thermographic data and natural images used to train VLMs" and needed an adapter to reach ~70% IoU [37]. For radiographs, Weld-LLaVA [35] and InsightX [36] both put image enhancement + a specialist detector in front of the LMM.
9. **Weekend fine-tuning is feasible but optional.** Roboflow Maestro fine-tunes Florence-2 / PaliGemma 2 (LoRA) and Qwen2.5-VL (QLoRA) from JSONL [48]; Unsloth ships free Colab notebooks for Qwen3-VL-8B, Qwen2.5-VL-7B, Gemma 3-4B, Llama 3.2 Vision (radiography example: 1,978 rows; recommends 300-1000 px images) [49]. Public data exists: SDNET2018 (56k crack/no-crack 256px tiles, CC BY 4.0) [55], InfraredSolarModules (20k thermal 24x40 px, 12 classes, MIT) [54], PVEL-AD (36,543 EL images, 12 classes) [53]; the DTU wind-blade drone set is CC BY-NC 3.0 (non-commercial - do not train a product on it) [56]. Evidence favors retrieval/few-shot over fine-tuning for a weekend: RAG-grounded VLMs beat the same VLM without retrieval on blades [31][32], and the bridge paper found accuracy *fell* when training data grew from 3k to 4k noisy samples [34].
10. **Biggest technical risks:** hallucinated defects and "memorized" answers regardless of image [28][40]; approximate localization [2][7]; thermal domain gap [37]; tiny evaluation sets in the optimistic papers (30 images in [31]); license traps (Moondream, SAM, Gemma terms, DTU NC); Haiku 4.5 retirement "not sooner than October 15, 2026" [1]; Gemini promo pricing doubling 2027-01-01 [8].

---

## Detailed findings

### 1. Small / edge VLMs for the first-pass "damage present?" judge

| Model | Params | License | Runs on | Grounding (bbox) | Inspection/defect benchmark | Source |
|---|---|---|---|---|---|---|
| **SmolVLM2** (HF, Feb 20 2025) | 256M / 500M / 2.2B | Apache-2.0 | free Colab; iPhone via MLX (Swift/Python) | No (not mentioned) | none found; general: OCRBench 72.9, DocVQA 80.0 (2.2B, SmolVLM) | [12][13][14] |
| **Moondream 3 Preview** (Sep 2025) / **Moondream 3.1 9B-A2B** (Jul 7 2026) | 9B MoE, 2B active | "Moondream License" (proprietary) - check commercial terms | >=10 GB VRAM NVIDIA; Apple MLX; x86/ARM CPU via GGUF; fp8 experts | **Yes, native**: detect, point, segment; boxes normalized [x_min,y_min,x_max,y_max] | none inspection-specific; COCO det F1@0.5 81.46, ODinW-13 93.94, LVIS 67.4 | [15][16][17] |
| **Qwen3-VL 2B / 4B / 8B** (Oct 15-21 2025) | 2B / 4B / 8B (+FP8) | Apache-2.0 | Ollama pulls 1.9 / 3.3 / 6.1 GB; vLLM >=0.11; 256K ctx | **Yes**: 2D + 3D grounding, boxes and points, "relative position coordinates" | none found | [18][19] |
| **Gemma 3 4B / 12B / 27B** (Mar 2025) | 4B / 12B / 27B vision (270M, 1B text-only) | Gemma Terms of Use | Ollama 3.3 / 8.1 / 17 GB; 128K ctx | not native (community fine-tunes exist) | none found | [20] |
| **Gemma 4 E2B / E4B / 26B-MoE / 31B** (Apr 2 2026) | 2.3B eff. / 4.5B eff. / 3.8B-of-25.2B / 30.7B | **Apache-2.0** (first for Gemma) | E2B: <1.5 GB RAM, 7.6 tok/s decode on Raspberry Pi 5 (INT4) | **Yes, native** JSON `[y1,x1,y2,x2]`; image token budget 70/140/280/560/1120 | none found; MMMU-Pro 76.9 (31B) | [21] |
| **PaliGemma 2** (Dec 2024, card updated Feb 25 2025) | 3B / 10B / 28B at 224/448/896 px | Gemma Terms | GPU; "designed first and foremost ... for fine-tuning" | Yes via `<loc>` tokens (detection + segmentation codewords) | none found | [22] |
| **Florence-2** (Nov 2023) | 0.23B base / 0.77B large | **MIT** | CPU or any GPU | **Yes**: OD, region proposal, phrase grounding, OCR (not a chat/VQA model) | InspectVLM fine-tune on InspectMM: competitive image-level classification, fails fine-grained detection [28]; COCO zero-shot mAP 34.7/37.5 | [23][28] |
| **InternVL3.5-2B** (Aug 25 2025) | 2.3B (0.3B vision + 2.0B LLM) | Apache-2.0 | LMDeploy, vLLM, SGLang, llama.cpp quants | evaluated on visual grounding (scores not in card) | none found | [24] |
| **LLaVA-OneVision / -1.5** | **not verified** (only referenced as FastVLM's baseline) | not found | not found | not found | none found | [25] |
| **Apple FastVLM** (CVPR 2025) | 0.5B / 1.5B / 7B | code LICENSE + separate LICENSE_MODEL (check) | Apple Silicon, iOS demo app; "85x faster TTFT" vs LLaVA-OneVision-0.5B | not mentioned | none found | [25] |
| **Phi-4-multimodal-instruct** (Feb 2025) | 5.6B | **MIT** | 16 GB-class GPU; flash-attn wants A100/A6000/H100 (fallbacks exist) | not mentioned | none found; MMMU 55.1 vs GPT-4o 61.7 | [26] |
| **MiniCPM-V 4.5** (Sep 2025) | 8.7B | Apache-2.0 (model and code) | llama.cpp, Ollama, iPhone/iPad app; up to 1.8 MP any aspect ratio | OCR/doc parsing strong; bbox grounding not documented | none found; OpenCompass avg 77.0 | [27] |

Notes:
- **Only Moondream 3.x, Qwen3-VL, Gemma 4 and Florence-2/PaliGemma 2 offer native boxes** in the small class. For a "damage present? yes/no + coarse type" judge, grounding is optional; for the demo, being able to draw a box from the *same* small model is a nice visual.
- **Ollama structured outputs** (Dec 2024) constrain any served model to a JSON schema via `format`, demonstrated on a vision model; recommended temperature 0 [50]. This makes a local judge return `{"damage_present": bool, "confidence": float, "coarse_type": enum}` reliably.
- **Per-image latency of these models on a laptop: not found** in sources - must be measured during the hackathon and reported honestly.
- Inference: for a Windows laptop with a 6-8 GB GPU, Qwen3-VL-4B (3.3 GB pull) is the safest default judge; Qwen3-VL-2B (1.9 GB) for CPU-only fallback; Moondream 3.1 if >=10 GB VRAM is available and its license is acceptable for a demo.

### 2. Heavy frontier VLMs for detailed grading

**Anthropic Claude (official docs, fetched 2026-09-24)** [1][2][3][4][5]
- Current lineup and API IDs: `claude-fable-5-1` ($10 in / $50 out per MTok, 1M ctx, 128K out), `claude-opus-5-5` ($4/$20, 1M ctx), `claude-sonnet-5` ($2/$10, 1M ctx; the introductory price was made permanent - "the previously scheduled increase to $3/$15 ... will not occur"), `claude-haiku-4-5-20251001` alias `claude-haiku-4-5` ($1/$5, 200K ctx, 64K out). All support image input and tool use [1][5].
- Retirement commitments: Haiku 4.5 "not sooner than October 15, 2026"; Sonnet 5 June 30, 2027; Opus 5.5 Sept 22, 2027; Fable 5.1 Sept 1, 2027 [1].
- Batch API 50% off (Haiku 4.5 $0.50/$2.50; Sonnet 5 $1/$5; Opus 5.5 $2/$10; Fable 5.1 $5/$25). Prompt-cache reads 0.1x base (0.05x on Opus 5.5, 0.025x on Fable 5.1) [5].
- **Image tokens**: `ceil(width/28) x ceil(height/28)` visual tokens. Standard tier (Haiku 4.5 and other pre-4.7 models): max long edge 1568 px, max 1,568 visual tokens. High-resolution tier (Claude 4.7 and later, i.e., Sonnet 5 / Opus 5.5 / Fable 5.1): max 2576 px, 4,784 tokens. Examples: 1000x1000 = 1,296 tokens both tiers; 1920x1080 = 1,560 tokens (standard, downsized to 1456x819) vs 2,691 (high-res, not resized); 3840x2160 = 1,560 vs 4,784 [2].
- Docs' own cost example: "at Claude Haiku 4.5's $1 per million input tokens, the 1000x1000 image costs about $1.30 per thousand images"; on Opus 5 ($5/MTok) $6.48 per thousand, 4K image $23.92 per thousand [2].
- **Limits**: 600 images/request on 1M-ctx models, 100 on 200K models (Haiku 4.5); >20 images in one request triggers a stricter per-image dimension limit (resize so neither side exceeds 2000 px); 10 MB per image (5 MB on Bedrock/Vertex); 32 MB request; 8000x8000 max; Files API for reuse; JPEG/PNG/GIF/WebP only [2].
- **No metadata**: "Claude does not parse or receive any metadata from images" [2] - critical for radiometric thermal (Section 5).
- **Coordinates**: Claude returns absolute pixel coordinates in the *resized* image; "Claude does not work well when you ask for normalized coordinates" - ask for pixels and normalize yourself. Pre-resize with the documented `resized_size()` helper so coordinates map 1:1. "Small elements lose precision when an image is downscaled: for fine targets, crop the region of interest." `transformations: {"oversized_image": "error"}` turns silent resizing into a 400 error [3].
- **Limitations stated by Anthropic**: "might hallucinate or make mistakes when interpreting low-quality, rotated, or very small images under 200 pixels"; "coordinate and localization outputs are approximate"; counting approximate [2].
- **Structured outputs**: GA on Opus 5.5/5/4.x, Sonnet 5/4.6/4.5, Haiku 4.5, Fable; `output_config.format = {"type":"json_schema", ...}`; guaranteed schema-valid JSON; supports enum/anyOf/$ref; **not** supported: numeric min/max, minLength/maxLength, recursion; first call compiles a grammar (latency), cached 24 h; adds a system-prompt token cost [4]. Docs recommend structured outputs to get bboxes "as machine-readable JSON" [3].

**OpenAI GPT-5 family (official)** [6][7]
- Prices per MTok (input / cached / output): GPT-5.5 $5 / $0.50 / $30; GPT-5.4 $2.50 / $0.25 / $15; GPT-5.4-mini $0.75 / $0.075 / $4.50; GPT-5.4-nano $0.20 / $0.02 / $1.25; GPT-5 $1.25 / $0.125 / $10; GPT-5-mini $0.25 / $2; GPT-5-nano $0.05 / $0.40; Batch 50% off [6].
- Image tokens: patch-based models (gpt-5.4, 5.5, 5.6, gpt-6-astra) use 32x32 px patches x 1.2 multiplier; `detail: high` budget ~2,500 patches (about 2048x2048), `low` fits 512x512, `original` up to 30,000 patches; tile-based older models 85 base + 170/tile. **Max 1,500 images per request**, 512 MB payload; PNG/JPEG/WEBP/non-animated GIF [7].
- Stated limitations: "may misinterpret rotated or upside-down text and images"; struggles with "tasks requiring precise spatial localization"; approximate counting; small text. Bounding boxes are **not** an explicitly supported output; coordinate tasks require pre-resizing and mapping back [7].

**Google Gemini (official)** [8][9][10]
- Current IDs include `gemini-3.8-flash`, `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite` [10].
- Prices per MTok: 3.8/3.7/3.6 Flash $0.75 in / $3.75 out through 2026-12-31, then $1.50 / $7.50; 3.5 Flash $1.50 / $9.00; 3.5 Flash-Lite $0.30 / $2.50; 2.5 Flash $0.30 / $2.50; 2.5 Flash-Lite $0.10 / $0.40; 2.5 Pro $1.25 / $10 (<=200k); Batch 50% off; free tier exists [8]. Gemini 3.1 Pro $2 / $12 per third-party tracker [11] (**secondary source**).
- Image tokens: 258 tokens if both sides <=384 px; else tiled into 768x768 tiles at 258 tokens each; crop unit ~ floor(min(w,h)/1.5). **Max 3,600 images/request** [9].
- **Native detection and segmentation**: `box_2d` = `[ymin, xmin, ymax, xmax]` normalized 0-1000; segmentation returns polygons normalized 0-1000 with labels; docs advise setting thinking to minimal for segmentation [9]. This is the strongest first-party grounding story among the three vendors.

Inference on vendor choice: Claude gives the best structured-output guarantees and highest-resolution native image handling (4,784 tokens) for grading; Gemini gives the cheapest per-image input and native normalized boxes; OpenAI gives the largest per-request image count. A vendor-agnostic grader interface (one JSON schema, one prompt template) is cheap to build and protects against the price/retirement changes noted above.

### 3. Published research 2024-2026: VLMs and foundation models for infrastructure defects

**General industrial-defect capability of VLMs**
- **MMAD** (ICLR 2025): 39,672 questions on 8,366 industrial images, 7 subtasks; best commercial model GPT-4o averaged **74.9%**, judged "inadequate for practical industrial deployment"; models "struggle significantly" with small-scale defects and localizing problems [29].
- **InspectVLM / InspectMM** (ICCV 2025 VISION workshop): Florence-2 fine-tuned on a new multitask inspection dataset; "competitive on image-level classification and structured keypoint tasks" but "fails to match ResNet-based models," with "brittle behavior under low prompt variability," "degenerate outputs for fine-grained object detection," and "frequently defaults to memorized language responses regardless of visual input." Conclusion: "current VLMs lack the visual grounding and robustness necessary for deployment in precision-critical industrial inspections" [28].
- **How well does GPT-4o understand vision?** (Jul 2025): GPT-4o, o3, Gemini 1.5/2.0, Claude 3.5 Sonnet, Qwen2-VL, Llama 3.2 on COCO/ImageNet detection, segmentation, depth: "not close to the state-of-the-art specialist models at any task"; semantic tasks much better than geometric ones; hallucinated objects observed; "better models are less sensitive to prompt variations" [40].

**Bridges / concrete cracks**
- **Steel-bridge crack MLLM study** (Automation in Construction vol. 171, Mar 2025): five MLLMs vs five DL models; MLLMs "achieve performance comparable to deep learning models in image-level crack detection," but patch-level accuracy "still needs to catch up" to SegFormer-class models; proposes a **cascaded image-level -> patch-level MLLM strategy** and studies visual-prompt design [30]. (Exact percentages behind paywall - **not found**.)
- **Fine-tuning VLMs for damage understanding + priority scoring with a Quality Guard agent** (arXiv 2605.27452, May 24 2026): LLaVA-1.5-7B QLoRA on up to 4,000 bridge-damage image/inspection-text pairs, 800 held-out; a second fine-tuned Swallow-8B "quality guard" rejects low-quality VLM outputs "before priority scoring, preventing spurious scores from damaged or unrecognised images"; semantic similarity peaked at 3k samples (0.6909) and **fell at 4k (0.6739)** - "quality-curated mid-scale data outperforms larger but noisier corpora"; optimized inference 10.06 s/image (-70.2%) [34].
- **TunnelMIND** (Apr 30 2026): training-free tunnel inspection via foundation models with visual recalibration and reconstruction into structured defect entities (category, location, geometry, severity, context); F1 0.68 visible / 0.78 GPR / 0.72 road [38].
- **FacadeFixer** multi-agent building inspection (Mar 2026) was **withdrawn** on May 4 2026 for "a major methodological error regarding the multi-agent orchestration setup" - do not cite it; it is a reminder that agentic-orchestration claims in this space are fragile [39].

**Wind turbine blades**
- **Seeing the Unseen** (arXiv 2510.22868, Oct 26 2025, rev. Aug 1 2026): RAG (technical docs + reference images + guidelines, hybrid text-image retriever with keyword reranking) grounding a VLM; evaluated on **only 30 labeled blade images**; RAG-grounded VLM "correctly classified all samples," un-grounded VLM worse in accuracy and precision. VLM identity not in abstract [31].
- **Few-shot visual reasoning via RAG + VLM** (IFAC / ScienceDirect, 2025): 98.3% classification accuracy and 0.862 Dice with 15 training samples per class (from search snippet; full text returned HTTP 403 - **not verified**) [32]. A follow-up "hierarchical retrieval" paper exists (2026) [58] - abstract not read.
- **LLM-YOLOMS** (Nov 13 2025): YOLO multi-scale detector with sliding-window crops + domain-tuned LLM for reports; 90.6% fault detection accuracy, 89% maintenance-report accuracy [33].

**PV / thermal**
- **HOTSPOT-YOLO** (Aug 2025): 90.8% mAP for thermal hotspots in drone PV inspection [41]. Specialist detectors dominate PV thermal; **no VLM-on-PV-thermal accuracy paper was found**.
- **AIRT vision-text** (Mar 11 2026): GroundingDINO + Qwen-VL-Chat + CogVLM with a lightweight adapter for active-thermography subsurface defects; 25 CFRP sequences; SNR gain >10 dB; zero-shot IoU ~70%; explicitly motivated by "the domain gap between thermographic data and natural images used to train VLMs" [37].
- Datature (Mar 2026) operational notes: IEC 62446-3 conditions - irradiance >=600 W/m2, wind <5 m/s; Swin Transformer 0.88 P / 0.85 R / 0.87 mAP; YOLO variants 85-95% mAP with 500-1,000 labeled images [53].

**Weld radiographs / X-ray NDT**
- **Weld-LLaVA** (Welding in the World, 2026): enhancement -> YOLOv8 candidate boxes -> colored bounding-box visual prompts -> CoT dialogue -> LLaVA-1.5-7B fine-tune; 1,798 images / 3,465 defect instances; **87.13% VQA classification accuracy**, outperforming GPT-4o, Claude 3.7 Sonnet, Qwen2.5-VL-72B, Mistral-Small and base LLaVA-7B (abstract via search snippet; Springer full text behind auth - **partially verified**) [35].
- **InsightX Agent** (Jul 2025, rev. Feb 2026): LMM orchestrator + Sparse Deformable Multi-Scale Detector proposals + "Evidence-Grounded Reflection" (context assessment, per-defect analysis, false-positive elimination, confidence recalibration, QA); **F1 96.54%** on GDXray+ [36].

**Cascade / judge patterns and cost**
- **Paza** (Apr 16 2026): cheap detector + pose run continuously; VLM invoked only after a multi-signal pre-filter, "reduces VLM invocations by 240x"; zero-shot VLM 89.5% precision / 92.8% specificity / 59.3% recall; $50-100/month/store vs $200-500 commercial; vendor-agnostic OpenAI-compatible endpoint (Gemma 4, Qwen3.5-Omni, GPT-4o) [42].
- **FrugalGPT** (May 2023): learned LLM cascade matches GPT-4 with "up to 98% cost reduction" or +4% accuracy at equal cost [43].
- **Bounding boxes for small-model grading** (Jul 2026, AIED SLM4ED workshop): cropping with boxes "significantly improves grading accuracy and reduces computational cost (FLOPs)" across 4B-72B models (education domain; transferable pattern) [44].

**Zero-shot localizers to run before the grader**
- Grounding DINO: Apache-2.0; Swin-T 48.4 COCO zero-shot AP; Grounding DINO 1.5/1.6 live in a separate API repo (licensing **not verified**) [46].
- OWLv2: Apache-2.0, 0.2B, CLIP backbone with per-token box heads [47].
- SAM 3 / 3.1 (Nov 19 2025 / Mar 27 2026): 848M params, text or exemplar "concept" prompts -> detect + segment + track; SA-Co image cgF1 54.1; needs CUDA 12.6+, PyTorch 2.7+; **"SAM License" (proprietary)** [45].
- Florence-2: MIT; 37.5 zero-shot COCO mAP (large) [23].

### 4. Fine-tuning and adaptation options for a weekend

| Option | Tooling | Evidence it works | Weekend cost/risk |
|---|---|---|---|
| **Few-shot prompting with reference exemplars** (2-6 labeled crops per severity class in the prompt) | Claude/Gemini/OpenAI multi-image (600 / 3,600 / 1,500 images per request) [2][9][7]; cache the exemplar prefix (Claude cache reads 0.1x) [5] | RAG-grounded VLM beat un-grounded on blades [31][32]; "better models are less sensitive to prompt variations" [40] | Hours, not days; no GPU; cost = extra input tokens per call (mitigated by prompt caching) |
| **Retrieval over past defects (image RAG)** | CLIP/SigLIP or `gemini-embedding-2-preview` multimodal embeddings [10]; FAISS/pgvector | Same as above; hybrid text-image retriever with reranking in [31] | ~1 day; needs a seed library (SDNET2018 tiles, IR modules) [55][54] |
| **LoRA/QLoRA on a small VLM** | Roboflow Maestro: Florence-2 (LoRA), PaliGemma 2 (LoRA), Qwen2.5-VL (QLoRA), JSONL, Apache-2.0 [48]; Unsloth: Qwen3-VL-8B, Qwen2.5-VL-7B, Gemma 3-4B, Llama 3.2 Vision 11B, free Colab notebooks, radiography example 1,978 rows, images 300-1000 px [49] | Weld-LLaVA 87.13% [35]; bridge paper: 2k samples optimal validation loss in 2.9 h, more data hurt [34] | 1 GPU-day incl. data prep; risk of overfitting and "memorized language" [28]; VRAM figures **not found** in Unsloth docs |
| **Fine-tune a specialist detector** (YOLO/RF-DETR) for localization only | Roboflow/Ultralytics | YOLO 85-95% mAP with 500-1,000 labels on PV [53]; HOTSPOT-YOLO 90.8% mAP [41] | Half a day per asset class if labels exist |

Public datasets found: SDNET2018 - >56,000 256x256 tiles from 230 photos, decks/walls/pavements, cracks 0.06-25 mm, CC BY 4.0 [55]; InfraredSolarModules - 20,000 thermal images at 24x40 px, 12 classes (Cell, Hot-Spot, Diode, Vegetation, Soiling, Offline-Module ...), MIT [54]; PVEL-AD - 36,543 EL images, 12 classes with boxes [53]; DTU drone blade images - **CC BY-NC 3.0**, 2017-2018 (non-commercial, counts/resolution not in page) [56]; GDXray weld radiographs - page redirect broken, details **not verified**.

Inference: for this hackathon, few-shot exemplars + retrieval + a zero-shot localizer gives most of the measured benefit with none of the training risk; keep a LoRA on Qwen3-VL-4B as a stretch goal and only if a clean labeled set (SDNET2018 or IR modules) is used.

### 5. Thermal and X-ray inputs

**Thermal (radiometric)**
- Frontier APIs accept only 8-bit JPEG/PNG/GIF/WebP [2][7]; Claude discards all image metadata [2]. Radiometric R-JPEG/TIFF temperature data therefore never reaches the model unless extracted.
- Extraction: FlirImageExtractor (MIT, `pip install flirimageextractor`, exiftool-based) returns temperature arrays as NumPy/CSV and renders palettes; tested on FLIR AX8/B60/E40/T640 and DJI H20T/XT2/XTR/XTS/H20N/M3T/M30T [51]. DJI publishes a Thermal SDK (existence confirmed; capabilities **not verified** from the download page) [52].
- Recommended preprocessing (Inference, from [2][37][51][53]): (a) decode to float temperature matrix; (b) apply emissivity/reflected-temperature/distance corrections in the SDK; (c) compute scene statistics - min/max/mean, per-module or per-region delta-T vs. neighbors, hottest-pixel coordinates; (d) render two 8-bit images - a fixed-range grayscale (so absolute temps are comparable across frames) and an auto-contrast pseudo-color for visibility; (e) pass the statistics as text alongside the image so the VLM grades on measured delta-T (IEC 62446-3 style thresholds) rather than colors; (f) record IEC 62446-3 capture conditions (>=600 W/m2, wind <5 m/s) as metadata [53].
- Evidence of domain gap: the AIRT paper needed an adapter to align thermographic data with VLM encoders and still reached only ~70% IoU zero-shot [37]; no paper was found showing a frontier VLM grading PV thermal at specialist accuracy. Specialist detectors report 90.8% mAP [41].
- The only public PV thermal set found is 24x40 px per module [54] - far below the "under 200 pixels" threshold where Claude warns of mistakes [2]; upscale/tile modules before sending, or use it only to train/evaluate a small classifier.

**X-ray / radiographs**
- Sources agree on enhancement + specialist proposals before the LMM: Weld-LLaVA (radiographic enhancement -> YOLOv8 candidates -> colored visual prompts) [35]; InsightX (multi-scale sparse detector -> LMM reflection) [36].
- Anthropic notes Claude "is not designed to interpret complex diagnostic scans" (medical context) [2]; OpenAI lists medical imaging among limitations [7]. Industrial radiographs are out of these models' core training distribution - treat VLM output as a *second opinion* on detector crops, not a primary detector.
- Preprocessing (Inference): read 16-bit TIFF/DICONDE; window (percentile clip) to 8-bit; CLAHE; tile at native resolution so porosity/cracks are not lost in the 28-px patching; send crops with the detector box drawn in color as a visual prompt (the technique that worked in [35]).

### 6. Cost model per 1,000 images (derived from official prices; assumptions stated)

Assumptions (Inference): image 1920x1080 (typical drone frame); ~300 tokens of cacheable prompt; judge output ~40 tokens; grader output ~400 tokens of JSON. Token counts from vendor formulas [2][7][9]; prices from [5][6][8]. Local model API cost = $0 (laptop electricity and engineer time excluded).

| Role | Model | Image tokens (1920x1080) | Input $/1k imgs | Output $/1k imgs | **Total $/1k imgs** | Batch (-50%) |
|---|---|---|---|---|---|---|
| Judge | Claude Haiku 4.5 | 1,560 (downsized to 1456x819) [2] | $1.86 | $0.20 | **$2.06** | $1.03 |
| Judge | GPT-5.4-nano | ~2,448 (60x34 patches x1.2) [7] | $0.55 | $0.05 | **$0.60** | $0.30 |
| Judge | Gemini 2.5 Flash | ~1,548 (6 tiles x 258) [9] | $0.55 | $0.10 | **$0.65** | $0.33 |
| Judge | Local Qwen3-VL-4B / Moondream 3.1 | n/a | $0 | $0 | **~$0 API** | - |
| Grader | Claude Sonnet 5 (full-res) | 2,691 [2] | $5.98 | $4.00 | **$9.98** | $4.99 |
| Grader | Claude Sonnet 5 (pre-downsized 1456x819) | 1,560 | $3.72 | $4.00 | **$7.72** | $3.86 |
| Grader | Claude Opus 5.5 (full-res) | 2,691 | $11.96 | $8.00 | **$19.96** | $9.98 |
| Grader | Claude Fable 5.1 (full-res) | 2,691 | $29.91 | $20.00 | **$49.91** | $24.96 |
| Grader | GPT-5.4 | ~2,448 | $6.87 | $6.00 | **$12.87** | $6.44 |
| Grader | GPT-5.4-mini | ~2,448 | $2.06 | $1.80 | **$3.86** | $1.93 |
| Grader | Gemini 3.8 Flash (promo) | ~1,548 | $1.39 | $1.50 | **$2.89** | $1.45 |

Cascade scenarios (grader = Sonnet 5 full-res at $9.98 / 1k):

| Pipeline | Pass-through to grader | $/1k images | Saving vs heavy-only |
|---|---|---|---|
| Heavy-only (Sonnet 5 on every image) | 100% | $9.98 | - |
| Local judge -> Sonnet 5 | 30% | $2.99 (+ local compute) | 70% |
| Local judge -> Sonnet 5 | 10% | $1.00 (+ local compute) | 90% |
| Haiku 4.5 judge -> Sonnet 5 | 30% | $2.06 + $2.99 = $5.05 | 49% |
| Haiku 4.5 judge -> Sonnet 5 | 10% | $2.06 + $1.00 = $3.06 | 69% |
| Local judge -> Opus 5.5 | 30% | $5.99 | 70% (vs $19.96) |
| Any of the above via Batch API | - | halve the Claude terms | - |

Sanity check against the vendor's own figure: Haiku 4.5 input for a 1000x1000 image is "$1.30 per thousand images" [2]; my 1080p Haiku input of $1.86 includes prompt tokens and a larger image, so it is consistent.

Caveats: (1) savings are proportional to the "no damage" fraction, which is high in routine inspections and drops in post-disaster triage; (2) the judge's false-negative rate is the real cost - a missed crack is worth far more than $0.01, so tune the judge for recall (Paza reported 59.3% recall zero-shot [42] - unacceptable for a safety filter without tuning); (3) Gemini 3.x image tokenization may differ from the 2.5 rule quoted (a third-party page lists 560 tokens per image for 3 Pro Image [11]); (4) Gemini Flash promo pricing doubles on 2027-01-01 [8]; (5) Haiku 4.5 could be retired as early as 2026-10-15 [1].

---

## Key numbers table

| Claim | Value | Source URL | Date |
|---|---|---|---|
| Claude Fable 5.1 price / ID | $10 in, $50 out per MTok; `claude-fable-5-1`; 1M ctx | https://platform.claude.com/docs/en/about-claude/models/overview | fetched 2026-09-24 |
| Claude Opus 5.5 price / ID | $4 / $20; `claude-opus-5-5`; 1M ctx | same | 2026-09-24 |
| Claude Sonnet 5 price / ID | $2 / $10 (made permanent Sept 2026); `claude-sonnet-5` | https://platform.claude.com/docs/en/about-claude/pricing | 2026-09-24 |
| Claude Haiku 4.5 price / ID / retirement | $1 / $5; `claude-haiku-4-5-20251001`; retire not sooner than 2026-10-15 | models overview | 2026-09-24 |
| Claude Batch API discount | 50% (Haiku 4.5 $0.50/$2.50; Sonnet 5 $1/$5; Opus 5.5 $2/$10) | pricing page | 2026-09-24 |
| Claude image token formula | ceil(w/28) x ceil(h/28); std tier max 1,568 tokens / 1568 px; hi-res tier 4,784 tokens / 2576 px | https://platform.claude.com/docs/en/build-with-claude/vision | 2026-09-24 |
| Claude 1000x1000 image cost on Haiku 4.5 | ~$1.30 per 1,000 images (input) | same | 2026-09-24 |
| Claude images per request | 600 (1M-ctx models), 100 (200K models), 20 on claude.ai; >20 images -> <=2000 px each | same | 2026-09-24 |
| Claude reads image metadata? | No | same | 2026-09-24 |
| Claude coordinates | Absolute pixels in resized image; normalized 0-1000 "does not work well" | https://platform.claude.com/docs/en/build-with-claude/vision-coordinates | 2026-09-24 |
| Claude structured outputs | GA on Haiku 4.5, Sonnet 5, Opus 5.5, Fable; `output_config.format` json_schema | https://platform.claude.com/docs/en/build-with-claude/structured-outputs | 2026-09-24 |
| GPT-5.5 / 5.4 / 5.4-mini / 5.4-nano prices | $5/$30; $2.50/$15; $0.75/$4.50; $0.20/$1.25 per MTok | https://developers.openai.com/api/docs/pricing | 2026-09-24 |
| OpenAI image tokens | 32x32 patches x 1.2 (gpt-5.4/5.5); ~2,500-patch high-detail budget; 1,500 images/request | https://developers.openai.com/api/docs/guides/images-vision | 2026-09-24 |
| Gemini 3.8 Flash price | $0.75 / $3.75 through 2026-12-31, then $1.50 / $7.50 | https://ai.google.dev/gemini-api/docs/pricing | 2026-09-24 |
| Gemini 2.5 Flash / 3.5 Flash-Lite price | $0.30 / $2.50 | same | 2026-09-24 |
| Gemini image tokens | 258 per image <=384 px; else 258 per 768x768 tile; 3,600 images/request | https://ai.google.dev/gemini-api/docs/image-understanding | 2026-09-24 |
| Gemini bbox format | `box_2d` [ymin,xmin,ymax,xmax] normalized 0-1000; segmentation polygons | same | 2026-09-24 |
| SmolVLM2 sizes / license / date | 256M, 500M, 2.2B; Apache-2.0; 2025-02-20 | https://huggingface.co/blog/smolvlm2 ; https://playground.roboflow.com/models/hugging-face/smolvlm2 | Feb 2025 |
| Moondream 3.1 9B-A2B | 9.0B total / 2.0B active; Moondream License; >=10 GB VRAM; COCO F1@0.5 81.46; released 2026-07-07 | https://moondream.ai/models/moondream_3-1_9B_A2B | Jul 2026 |
| Qwen3-VL small variants | 2B/4B/8B, Apache-2.0, released 2025-10-15/21; Ollama 1.9/3.3/6.1 GB | https://github.com/QwenLM/Qwen3-VL ; https://ollama.com/library/qwen3-vl | Oct 2025 |
| Gemma 4 | Released 2026-04-02; E2B 2.3B eff.; Apache-2.0; native [y1,x1,y2,x2]; 7.6 tok/s on RPi 5 | https://datature.io/blog/gemma-4-what-computer-vision-engineers-actually-need-to-know | Apr 2026 |
| Gemma 3 vision sizes | 4B/12B/27B (3.3/8.1/17 GB); Gemma Terms | https://ollama.com/library/gemma3 | 2025 |
| PaliGemma 2 | 3B/10B/28B, 224/448/896 px, fine-tune-first design | https://ai.google.dev/gemma/docs/paligemma/model-card-2 | Feb 2025 |
| Florence-2 | 0.23B / 0.77B; MIT; zero-shot COCO mAP 34.7 / 37.5 | https://huggingface.co/microsoft/Florence-2-large | 2023-2024 |
| InternVL3.5-2B | 2.3B; Apache-2.0; 2025-08-25 | https://huggingface.co/OpenGVLab/InternVL3_5-2B | Aug 2025 |
| FastVLM | 0.5B/1.5B/7B; 85x faster TTFT vs LLaVA-OneVision-0.5B | https://github.com/apple/ml-fastvlm | CVPR 2025 |
| Phi-4-multimodal | 5.6B; MIT; MMMU 55.1 | https://huggingface.co/microsoft/Phi-4-multimodal-instruct | Feb 2025 |
| MiniCPM-V 4.5 | 8.7B; Apache-2.0; OpenCompass 77.0 | https://huggingface.co/openbmb/MiniCPM-V-4_5 | Sep 2025 |
| MMAD benchmark | 39,672 Qs / 8,366 images; GPT-4o 74.9% | https://arxiv.org/abs/2410.09453 | ICLR 2025 |
| InspectVLM | Florence-2 FT; fails fine-grained detection; memorized responses | https://arxiv.org/abs/2508.01921 | Aug 2025 |
| Steel bridge MLLM cascade | image-level comparable to DL; patch-level lags SegFormer | https://trid.trb.org/View/2500048 | Mar 2025 |
| Bridge priority + quality guard | LLaVA-1.5-7B QLoRA; 4k pairs; sim 0.6909 @3k vs 0.6739 @4k; 10.06 s/img | https://arxiv.org/abs/2605.27452 | May 2026 |
| WTB zero-shot RAG-VLM | 30 images; RAG-grounded classified all correctly | https://arxiv.org/abs/2510.22868 | Oct 2025 / Aug 2026 |
| WTB few-shot RAG-VLM | 98.3% acc, 0.862 Dice, 15 samples/class (snippet only) | https://www.sciencedirect.com/science/article/pii/S2405896325029192 | 2025 |
| LLM-YOLOMS | 90.6% fault detection; 89% report accuracy | https://arxiv.org/abs/2511.10394 | Nov 2025 |
| Weld-LLaVA | 87.13% VQA acc; 1,798 imgs / 3,465 instances; beats GPT-4o, Claude 3.7 Sonnet, Qwen2.5-VL-72B | https://link.springer.com/article/10.1007/s40194-026-02557-1 | 2026 |
| InsightX Agent | F1 96.54% on GDXray+ | https://arxiv.org/abs/2507.14899 | Jul 2025 / Feb 2026 |
| AIRT vision-text | SNR >10 dB; IoU ~70%; thermal domain gap | https://arxiv.org/abs/2603.10549 | Mar 2026 |
| TunnelMIND | F1 0.68 / 0.78 / 0.72 | https://arxiv.org/abs/2604.27928 | Apr 2026 |
| HOTSPOT-YOLO | 90.8% mAP PV hotspots | https://arxiv.org/pdf/2508.18912 | Aug 2025 |
| Paza cascade | 240x fewer VLM calls; 89.5% P / 92.8% spec / 59.3% R; $50-100/mo/store | https://arxiv.org/abs/2604.14846 | Apr 2026 |
| FrugalGPT | up to 98% cost reduction | https://arxiv.org/abs/2305.05176 | May 2023 |
| Grounding DINO | Apache-2.0; 48.4 COCO zero-shot AP | https://github.com/IDEA-Research/GroundingDINO | 2023+ |
| OWLv2 | Apache-2.0; 0.2B | https://huggingface.co/google/owlv2-base-patch16-ensemble | 2023+ |
| SAM 3 / 3.1 | 848M; SAM License; cgF1 54.1; SAM 3.1 2026-03-27 | https://github.com/facebookresearch/sam3 | Nov 2025 / Mar 2026 |
| Maestro | Florence-2, PaliGemma 2, Qwen2.5-VL; LoRA/QLoRA; Apache-2.0 | https://github.com/roboflow/maestro | 2025 |
| Unsloth vision FT | Qwen3-VL-8B, Qwen2.5-VL-7B, Gemma 3-4B, Llama 3.2 V; 300-1000 px; radiography example 1,978 rows | https://unsloth.ai/docs/basics/vision-fine-tuning | 2025-2026 |
| Ollama structured outputs | JSON schema via `format`; vision demo | https://ollama.com/blog/structured-outputs | 2024-12-06 |
| FlirImageExtractor | MIT; exiftool; FLIR + DJI H20T/M3T/M30T | https://github.com/nationaldronesau/FlirImageExtractor | current |
| IEC 62446-3 capture conditions | >=600 W/m2, wind <5 m/s | https://datature.io/blog/solar-panel-defect-detection-with-vision-ai-from-drone-thermography-to-deployed-models | Mar 2026 |
| SDNET2018 | >56,000 256x256 tiles; cracks 0.06-25 mm; CC BY 4.0 | https://digitalcommons.usu.edu/all_datasets/48/ | 2018 |
| InfraredSolarModules | 20,000 IR images 24x40 px; 12 classes; MIT | https://github.com/RaptorMaps/InfraredSolarModules | current |
| PVEL-AD | 36,543 EL images; 12 classes; boxes | Datature blog (above) | Mar 2026 |
| DTU blade drone images | CC BY-NC 3.0 (non-commercial) | https://data.mendeley.com/datasets/hd96prn3nc/2 | 2018 |

---

## Implications for our product / edge

1. **Build the cascade as three explicit stages and show each on screen**: (A) local small-VLM judge with JSON output and a recall-first threshold; (B) zero-shot/specialist localizer that produces crops with drawn boxes; (C) frontier grader on the crop with an asset-specific rubric and structured JSON (severity, confidence, evidence, recommended action, pixel bbox). This mirrors the strongest published systems [30][34][35][36][42] and directly answers the localization weakness every benchmark reports [2][7][28][29][40].
2. **Our differentiator is not "we use a VLM" (everyone will); it is the *grading + prioritization contract***: per-industry rubric schemas (bridge element condition states, IEC 62446-3 delta-T classes, blade damage categories, weld acceptance criteria) enforced by schema-guaranteed outputs [4], a quality-guard step that refuses to score low-confidence/inconsistent outputs [34], and an audit trail (which crop, which exemplar, which rubric line) - an inspector can defend the score.
3. **Cost story judges can verify**: with official prices we can state "about $10 per 1,000 drone frames on Sonnet 5 heavy-only vs about $3 with a local pre-filter at 30% pass-through, half that on Batch" (Section 6) - and make the point that the *expensive* number is the missed defect, so the judge is tuned for recall.
4. **Edge/offline mode is a real wedge**: Gemma 4 E2B on a Raspberry Pi 5 [21] and Qwen3-VL-2B at 1.9 GB [19] make an on-drone or on-ROV pre-filter plausible; underwater and remote wind sites often have no connectivity - the cascade lets the heavy model run later in batch.
5. **Multi-vendor grader abstraction protects us**: Haiku 4.5 may retire mid-October 2026 [1]; Gemini promo prices double in January 2027 [8]. One JSON schema + one prompt template across Claude/Gemini/OpenAI is cheap insurance and lets us show the same image graded by two models (disagreement = escalate to human).
6. **Thermal and X-ray handling is a moat if done right**: extract radiometric temperatures, pass delta-T statistics as text, keep fixed-range grayscale plus pseudo-color [51][53][37]; window 16-bit radiographs and send detector crops with colored boxes [35][36]. Most generic "upload a photo to GPT" competitors will not do this.
7. **Be honest about accuracy**: the rules forbid fabricated performance claims. Quote the literature (MMAD 74.9%, Weld-LLaVA 87.13%, InsightX F1 96.54%) as *evidence of feasibility*, and show our own measured confusion matrix on a held-out SDNET2018 / IR-modules subset live in the demo - even if it is a few hundred images.
8. **Prefer retrieval and few-shot over fine-tuning this weekend**; keep a LoRA run as a stretch goal. Exemplar retrieval also becomes a product feature: "similar past defects at this site."

---

## Open questions / gaps

- **Per-image latency and accuracy of Qwen3-VL-2B/4B, Moondream 3.1, Gemma 4 E2B on our actual laptop** - not published; must be measured Friday.
- **Moondream License, SAM License, Gemma Terms, FastVLM LICENSE_MODEL** - commercial-use terms not read; verify before putting any of them in a "production" slide. Grounding DINO 1.5/1.6 API licensing not verified.
- **Weld-LLaVA full text** (Springer auth wall) - only abstract numbers; per-defect-class results unknown.
- **Few-shot RAG blade paper** (ScienceDirect 403) - 98.3% / 0.862 Dice from a search snippet only; dataset and VLM unknown.
- **GDXray** weld subset size/annotations - site redirect broken; not verified.
- **LLaVA-OneVision-1.5 and Gemma 3n** specifics (params, license, grounding) - not fetched.
- **Gemini 3.x image tokenization** - docs quote the 768-px tile rule; a third-party page implies a flat 560-token rule for 3 Pro Image; check the model card before quoting Gemini per-image costs.
- **Exact OpenAI token count per image** - derived from the documented 32-px patch x 1.2 rule; the interactive calculator was not readable.
- **No paper found that measures a frontier VLM grading PV thermal or underwater imagery** - our claims there must rest on our own demo measurements.
- **Unsloth/Maestro VRAM and wall-clock** for a few-hundred-image LoRA - not stated; budget one GPU-day and a Colab fallback.
- **Steel-bridge MLLM cascade exact accuracies** (Automation in Construction) - behind paywall.

---

## Sources

1. https://platform.claude.com/docs/en/about-claude/models/overview - Claude models overview: IDs, prices, context, retirement dates (fetched 2026-09-24).
2. https://platform.claude.com/docs/en/build-with-claude/vision - Claude vision: 28-px patch token math, resolution tiers, image limits, formats, no-metadata, limitations.
3. https://platform.claude.com/docs/en/build-with-claude/vision-coordinates - Claude bounding boxes/points: absolute pixel coords, resize/pad rules, `oversized_image: error`.
4. https://platform.claude.com/docs/en/build-with-claude/structured-outputs - Structured outputs GA, `output_config.format`, schema limits.
5. https://platform.claude.com/docs/en/about-claude/pricing - Full price table, Batch API, prompt caching multipliers, Sonnet 5 price made permanent.
6. https://developers.openai.com/api/docs/pricing - GPT-5.x family prices and batch discount.
7. https://developers.openai.com/api/docs/guides/images-vision - OpenAI image token rules, 1,500 images/request, limitations.
8. https://ai.google.dev/gemini-api/docs/pricing - Gemini 3.x/2.5 prices, promo expiry, batch.
9. https://ai.google.dev/gemini-api/docs/image-understanding - Gemini image tokens, 3,600 images/request, `box_2d` 0-1000, segmentation.
10. https://ai.google.dev/gemini-api/docs/models - Current Gemini model IDs.
11. https://www.morphllm.com/gemini-api-pricing - Third-party Gemini 3.1 Pro pricing and 560-token image note (secondary).
12. https://huggingface.co/blog/smolvlm2 - SmolVLM2 release blog (sizes, MLX/iPhone).
13. https://playground.roboflow.com/models/hugging-face/smolvlm2 - SmolVLM2 license (Apache-2.0) and summary.
14. https://huggingface.co/blog/smolvlm - SmolVLM benchmarks (OCRBench, DocVQA).
15. https://moondream.ai/models/moondream_3-1_9B_A2B - Moondream 3.1 model card (params, license, VRAM, benchmarks).
16. https://huggingface.co/moondream/moondream3-preview - Moondream 3 preview card (MoE architecture, normalized bbox output).
17. https://moondream.ai/blog/moondream-3-preview - Moondream 3 preview blog (native detect/point/segment).
18. https://github.com/QwenLM/Qwen3-VL - Qwen3-VL sizes, Apache-2.0, release dates, grounding.
19. https://ollama.com/library/qwen3-vl - Ollama Qwen3-VL pull sizes and context.
20. https://ollama.com/library/gemma3 - Gemma 3 vision sizes and license on Ollama.
21. https://datature.io/blog/gemma-4-what-computer-vision-engineers-actually-need-to-know - Gemma 4 release, variants, Apache-2.0, native bbox, RPi 5 numbers.
22. https://ai.google.dev/gemma/docs/paligemma/model-card-2 - PaliGemma 2 model card.
23. https://huggingface.co/microsoft/Florence-2-large - Florence-2 params, MIT, COCO mAP.
24. https://huggingface.co/OpenGVLab/InternVL3_5-2B - InternVL3.5-2B card.
25. https://github.com/apple/ml-fastvlm - FastVLM sizes, TTFT claim, licenses.
26. https://huggingface.co/microsoft/Phi-4-multimodal-instruct - Phi-4-multimodal card.
27. https://huggingface.co/openbmb/MiniCPM-V-4_5 - MiniCPM-V 4.5 card.
28. https://arxiv.org/abs/2508.01921 - InspectVLM: "Unified in Theory, Unreliable in Practice" (ICCV 2025 workshop).
29. https://arxiv.org/abs/2410.09453 - MMAD benchmark for MLLMs in industrial anomaly detection (ICLR 2025).
30. https://trid.trb.org/View/2500048 - Crack image classification in steel bridges with MLLMs (Automation in Construction, Mar 2025).
31. https://arxiv.org/abs/2510.22868 - Zero-shot wind turbine blade inspection with RAG-grounded VLMs.
32. https://www.sciencedirect.com/science/article/pii/S2405896325029192 - Few-shot RAG + VLM blade damage detection (abstract via search snippet; 403 on fetch).
33. https://arxiv.org/abs/2511.10394 - LLM-YOLOMS wind turbine component fault diagnosis.
34. https://arxiv.org/abs/2605.27452 - Fine-tuning VLMs for damage understanding and priority scoring with a Quality Guard agent (bridges, May 2026).
35. https://link.springer.com/article/10.1007/s40194-026-02557-1 - Weld-LLaVA X-ray weld defect VLM (abstract via search snippet).
36. https://arxiv.org/abs/2507.14899 - InsightX Agent: LMM + detector + reflection for X-ray NDT.
37. https://arxiv.org/abs/2603.10549 - Cognitive defect analysis in active infrared thermography with vision-text cues.
38. https://arxiv.org/abs/2604.27928 - TunnelMIND training-free tunnel defect inspection.
39. https://arxiv.org/abs/2603.20143 - FacadeFixer multi-agent building inspection (WITHDRAWN May 2026).
40. https://arxiv.org/abs/2507.01955 - How well does GPT-4o understand vision? (MFMs vs specialist CV models).
41. https://arxiv.org/pdf/2508.18912 - HOTSPOT-YOLO for PV thermal anomalies (90.8% mAP).
42. https://arxiv.org/abs/2604.14846 - Paza: orchestrated zero-shot vision cascade with VLM pre-filter (240x fewer VLM calls).
43. https://arxiv.org/abs/2305.05176 - FrugalGPT LLM cascades.
44. https://arxiv.org/abs/2607.18767 - Bounding boxes improve small-model performance on vision grading tasks (Jul 2026).
45. https://github.com/facebookresearch/sam3 - SAM 3 / 3.1 repo: params, license, benchmarks.
46. https://github.com/IDEA-Research/GroundingDINO - Grounding DINO repo: Apache-2.0, COCO zero-shot AP.
47. https://huggingface.co/google/owlv2-base-patch16-ensemble - OWLv2 card.
48. https://github.com/roboflow/maestro - Roboflow Maestro VLM fine-tuning.
49. https://unsloth.ai/docs/basics/vision-fine-tuning - Unsloth vision fine-tuning docs.
50. https://ollama.com/blog/structured-outputs - Ollama structured outputs with vision models.
51. https://github.com/nationaldronesau/FlirImageExtractor - FLIR/DJI radiometric JPEG temperature extraction (MIT).
52. https://www.dji.com/downloads/softwares/dji-thermal-sdk - DJI Thermal SDK download listing (existence only).
53. https://datature.io/blog/solar-panel-defect-detection-with-vision-ai-from-drone-thermography-to-deployed-models - PV defect detection overview, datasets, IEC 62446-3 conditions (Mar 2026).
54. https://github.com/RaptorMaps/InfraredSolarModules - Infrared Solar Modules dataset (20k, 12 classes, MIT).
55. https://digitalcommons.usu.edu/all_datasets/48/ - SDNET2018 concrete crack dataset (CC BY 4.0).
56. https://data.mendeley.com/datasets/hd96prn3nc/2 - DTU drone inspection images of wind turbine (CC BY-NC 3.0).
57. https://pmc.ncbi.nlm.nih.gov/articles/PMC12190611 - PV IR defect detection with improved YOLOv8 (PeerJ CS, Apr 2025).
58. https://www.sciencedirect.com/science/article/pii/S2590123026022152 - Few-shot VLMs with hierarchical retrieval for blade inspection (2026; title only).
