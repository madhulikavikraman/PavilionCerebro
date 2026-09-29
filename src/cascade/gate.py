"""Stage A: the gate. Two questions per image: is it usable, is there visible damage.

Default backend is a local small VLM served by Ollama (structured JSON via `format`).
Cloud fallback is Claude Haiku 4.5 through the Anthropic SDK's parse helper.
Routing is recall-first: anything unusable, anything with damage, and any low-confidence
"no damage" verdict goes on to the grader.
"""

from __future__ import annotations

import os
from typing import Optional

import requests
from PIL import Image

from .costlog import CallLog, Timer
from .crop import fit_for_model, to_base64_jpeg, upscale_small
from .schema import GateOutput, GateRecord

GATE_PROMPT = (
    "You are the first-pass triage for an infrastructure inspection pipeline. Look at this "
    "single image and answer two questions only.\n"
    "1. usable: is the image sharp enough, exposed well enough and unobstructed enough that a "
    "trained inspector could assess the surface shown? Blur, glare, heavy occlusion or an image "
    "that does not show an asset surface at all make it unusable.\n"
    "2. damage_present: is there any visible sign of damage, deterioration or abnormality on the "
    "asset (cracks, spalling, exposed rebar, corrosion, coating breakdown, erosion, hot spots, "
    "broken or missing parts, structural deformation, debris from collapse)? Normal texture, "
    "joints, dirt and shadows are not damage.\n"
    "Give a confidence between 0 and 1 for your damage_present answer and a one-sentence reason. "
    "When unsure, say damage_present is true; a missed defect costs more than a false alarm."
)


def route(out: GateOutput, no_damage_min_conf: float = 0.7) -> bool:
    """True if the image should go to the heavy grader."""
    if not out.usable:
        return True
    if out.damage_present:
        return True
    return out.confidence < no_damage_min_conf


def _prep(img: Image.Image) -> str:
    return to_base64_jpeg(fit_for_model(upscale_small(img)))


def gate_ollama(img: Image.Image, *, model: Optional[str] = None, url: Optional[str] = None, timeout: int = 180) -> tuple[GateOutput, dict]:
    # Instruct-only tag: the default qwen3-vl:4b tag runs with thinking on and can spend its whole
    # output budget on hidden reasoning before emitting the JSON (observed 2026-09-24 on a 4000x3000 image).
    model = model or os.getenv("GATE_LOCAL_MODEL", "qwen3-vl:4b-instruct")
    url = (url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
    payload = {
        "model": model,
        "stream": False,
        "format": GateOutput.model_json_schema(),
        "options": {"temperature": 0},
        "messages": [{"role": "user", "content": GATE_PROMPT, "images": [_prep(img)]}],
    }
    usage = {"input_tokens": 0, "output_tokens": 0}
    last_err = ""
    for attempt in range(2):
        try:
            r = requests.post(f"{url}/api/chat", json=payload, timeout=timeout)
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:  # server busy, OOM, 4xx/5xx: retry once, then route
            last_err = f"{type(e).__name__}: {str(e)[:120]}"
            continue
        usage = {"input_tokens": usage["input_tokens"] + int(data.get("prompt_eval_count", 0)), "output_tokens": usage["output_tokens"] + int(data.get("eval_count", 0))}
        content = (data.get("message") or {}).get("content") or ""
        try:
            return GateOutput.model_validate_json(content), usage
        except Exception as e:  # empty or malformed JSON from the local model
            last_err = f"{type(e).__name__}: {str(e)[:120]}"
            payload["options"] = {"temperature": 0.2, "num_predict": 4096}
    # Recall-first fallback: an unreadable gate reply routes the image onward instead of dropping it.
    return GateOutput(usable=True, damage_present=True, confidence=0.0, reason=f"gate returned no valid JSON after retry ({last_err}); routed by default"), usage


def gate_claude(img: Image.Image, *, model: Optional[str] = None) -> tuple[GateOutput, dict]:
    import anthropic

    model = model or os.getenv("GATE_CLOUD_MODEL", "claude-haiku-4-5")
    client = anthropic.Anthropic()
    response = client.messages.parse(
        model=model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": _prep(img)}},
                    {"type": "text", "text": GATE_PROMPT},
                ],
            }
        ],
        output_format=GateOutput,
    )
    if response.stop_reason == "refusal" or response.parsed_output is None:
        out = GateOutput(usable=False, damage_present=True, confidence=0.0, reason="model declined or returned no output")
    else:
        out = response.parsed_output
    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
    return out, usage


def run_gate(
    img: Image.Image,
    image_id: str,
    *,
    backend: str = "local",
    log: Optional[CallLog] = None,
    no_damage_min_conf: float = 0.7,
) -> GateRecord:
    with Timer() as t:
        if backend == "local":
            out, usage = gate_ollama(img)
            model = os.getenv("GATE_LOCAL_MODEL", "qwen3-vl:4b-instruct")
        elif backend == "claude":
            out, usage = gate_claude(img)
            model = os.getenv("GATE_CLOUD_MODEL", "claude-haiku-4-5")
        elif backend == "none":
            out, usage, model = GateOutput(usable=True, damage_present=True, confidence=1.0, reason="gate disabled"), {"input_tokens": 0, "output_tokens": 0}, "none"
        else:
            raise ValueError(f"unknown gate backend {backend}")
    usd = 0.0
    if log is not None:
        row = log.record(stage="gate", model=model, image_id=image_id, input_tokens=usage["input_tokens"], output_tokens=usage["output_tokens"], seconds=t.seconds)
        usd = row["usd"]
    return GateRecord(
        image_id=image_id,
        usable=out.usable,
        damage_present=out.damage_present,
        confidence=out.confidence,
        reason=out.reason,
        routed=route(out, no_damage_min_conf),
        model=model,
        seconds=round(t.seconds, 3),
        usd=usd,
    )
