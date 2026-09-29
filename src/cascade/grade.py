"""Stage C: the heavy grader.

Builds a prompt from the asset class's rubric file (rows copied from the standard, see
docs/research/05_damage_grading_standards.md), optional exemplar crops, the target crop
and any measurement metadata, and asks for the GraderOutput contract. Cloud backend is
Claude through `client.messages.parse` (schema-enforced). Local backend is Ollama with the
same JSON schema. Refusals and parse failures become U findings, never S0.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests
from PIL import Image

from .costlog import CallLog, Timer
from .crop import fit_for_model, to_base64_jpeg, upscale_small
from .schema import AssetClass, Evidence, Finding, GraderOutput, Standard, unassessable_finding

RUBRIC_DIR = Path(__file__).parent / "rubrics"

RUBRIC_FOR_CLASS = {
    "steel_coating": "corrosion_cs.json",
    "bridge_element": "bridge_mbei.json",
    "pv_module": "pv_iec62446_3.json",
    "building_disaster": "disaster_fema.json",
}


def load_rubric(asset_class: AssetClass, rubric_file: Optional[str] = None) -> dict:
    name = rubric_file or RUBRIC_FOR_CLASS[asset_class]
    return json.loads((RUBRIC_DIR / name).read_text(encoding="utf-8"))


@dataclass
class Exemplar:
    image: Image.Image
    native_value: str
    note: str = ""
    image_id: str = ""  # so the pipeline never shows an image its own label


SYSTEM_TEMPLATE = """You are an inspection grading assistant. You grade ONE image crop of a {asset_label} against the rubric below and return the JSON contract exactly.

Rules:
- Emit the native scale first: set native_scale.standard to "{standard}" and native_scale.value to one of the allowed values. Put the verbatim rubric criterion text you matched into native_scale.criteria_matched (copy it, do not paraphrase).
- Then set unified.level using the mapping in the rubric. uncertainty is always "+/-1".
- If a criterion needs a measurement (width, area, temperature, percent area, section loss) that you cannot make from the image and the metadata provided, do NOT guess a value: set that measurement to null, add the flag "not_measurable", and grade only from criteria that need no measurement. If no criterion can be applied without a measurement, set unified.level to "U".
- Never describe damage that is not visible. If the crop shows no defect, use the lowest native value and unified.level "S0".
- action.code follows the rubric's action mapping; action.basis must name the rubric row or standard clause used.
- measurements.confidence is your confidence in the native grade, 0 to 1.
- justification: two or three sentences describing exactly what is visible and why it meets the criterion.

Rubric ({standard}):
{rubric_json}
"""


def build_system(asset_class: AssetClass, rubric: dict) -> str:
    return SYSTEM_TEMPLATE.format(
        asset_label=rubric.get("asset_label", asset_class),
        standard=rubric["standard"],
        rubric_json=json.dumps({k: v for k, v in rubric.items() if k not in ("asset_label",)}, indent=1),
    )


def build_user_content(img: Image.Image, metadata: dict, exemplars: Optional[List[Exemplar]] = None) -> list:
    content: list = []
    for i, ex in enumerate(exemplars or []):
        content.append({"type": "text", "text": f"Exemplar {i + 1}: native grade {ex.native_value}. {ex.note}".strip()})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": to_base64_jpeg(fit_for_model(upscale_small(ex.image)))}})
    content.append({"type": "text", "text": "Target image to grade:"})
    content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": to_base64_jpeg(fit_for_model(upscale_small(img)))}})
    meta_lines = [f"{k}: {v if v is not None else 'unknown'}" for k, v in metadata.items()]
    content.append({"type": "text", "text": "Metadata:\n" + ("\n".join(meta_lines) if meta_lines else "none") + "\nReturn the JSON contract."})
    return content


def grade_claude(img: Image.Image, asset_class: AssetClass, rubric: dict, metadata: dict, exemplars=None, model: Optional[str] = None):
    """Returns (GraderOutput or None, usage dict, stop_reason)."""
    import anthropic

    model = model or os.getenv("GRADER_MODEL", "claude-opus-5")
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=model,
        max_tokens=4096,
        system=build_system(asset_class, rubric),
        messages=[{"role": "user", "content": build_user_content(img, metadata, exemplars)}],
        output_format=GraderOutput,
    )
    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
    if response.stop_reason == "refusal":
        return None, usage, "refusal"
    return response.parsed_output, usage, response.stop_reason


def grade_ollama(img: Image.Image, asset_class: AssetClass, rubric: dict, metadata: dict, exemplars=None, model: Optional[str] = None, url: Optional[str] = None, timeout: int = 600):
    model = model or os.getenv("GRADER_LOCAL_MODEL", "qwen3-vl:8b-instruct")
    url = (url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
    content = build_user_content(img, metadata, exemplars)
    text = "\n".join(c["text"] for c in content if c["type"] == "text")
    images = [c["source"]["data"] for c in content if c["type"] == "image"]
    payload = {
        "model": model,
        "stream": False,
        "format": GraderOutput.model_json_schema(),
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": build_system(asset_class, rubric)},
            {"role": "user", "content": text, "images": images},
        ],
    }
    r = requests.post(f"{url}/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    usage = {"input_tokens": int(data.get("prompt_eval_count", 0)), "output_tokens": int(data.get("eval_count", 0))}
    try:
        return GraderOutput.model_validate_json(data["message"]["content"]), usage, "end_turn"
    except Exception as e:  # invalid JSON from a local model becomes U, not a crash
        return None, usage, f"parse_error: {e}"


def grade_image(
    img: Image.Image,
    *,
    finding_id: str,
    image_id: str,
    asset_class: AssetClass,
    backend: str = "claude",
    rubric: Optional[dict] = None,
    metadata: Optional[dict] = None,
    exemplars: Optional[List[Exemplar]] = None,
    evidence: Optional[Evidence] = None,
    log: Optional[CallLog] = None,
) -> Finding:
    rubric = rubric or load_rubric(asset_class)
    metadata = metadata or {}
    evidence = evidence or Evidence(image_ids=[image_id])
    standard: Standard = rubric["standard"]
    with Timer() as t:
        if backend == "claude":
            model = os.getenv("GRADER_MODEL", "claude-opus-5")
            out, usage, stop = grade_claude(img, asset_class, rubric, metadata, exemplars)
        elif backend == "local":
            model = os.getenv("GRADER_LOCAL_MODEL", "qwen3-vl:8b-instruct")
            out, usage, stop = grade_ollama(img, asset_class, rubric, metadata, exemplars)
        else:
            raise ValueError(f"unknown grader backend {backend}")
    usd = 0.0
    if log is not None:
        row = log.record(stage="grade", model=model, image_id=image_id, input_tokens=usage["input_tokens"], output_tokens=usage["output_tokens"], seconds=t.seconds, note=str(stop))
        usd = row["usd"]
    if out is None:
        return unassessable_finding(finding_id=finding_id, asset_class=asset_class, standard=standard, evidence=evidence, reason=f"grader returned no contract ({stop})", model=model)
    return Finding.from_grader(out, finding_id=finding_id, asset_class=asset_class, evidence=evidence, model=model, usd=usd, seconds=t.seconds)
