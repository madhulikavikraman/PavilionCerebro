"""Agent 0 - Structural Visual. Wraps the existing inspection cascade in src/cascade/.

The cascade (gate -> grade -> prioritize) is used as-is: this module calls
`cascade.gate.run_gate` and `cascade.grade.grade_image` and translates the
`GateRecord` / `Finding` they already return into the shared `AgentReport`. No
cascade code was changed; its outputs were already structured objects.

Backends, picked by CEREBRO_VISUAL_BACKEND (default "auto"):
  claude  cascade with the Claude gate and grader (needs ANTHROPIC_API_KEY)
  local   cascade with the local Qwen3-VL gate/grader served by Ollama
  opencv  offline fallback added for Pavilion Cerebro: classical OpenCV crack features
          (black-hat morphology, connected-component shape, edge density) with a
          logistic calibration fitted on a held-out split of the crack dataset.
          It is NOT part of the original cascade; it exists so the demo runs on a
          laptop with no model server and no API key, and every report says which
          backend produced it.
  auto    claude if a key is set, else local if Ollama answers, else opencv.

Each replay frame is scored on its own; a zone's risk is the recent-frame
maximum blended with the recent mean so one noisy frame cannot pin a zone.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Iterator, List, Optional

import cv2
import numpy as np

from .base import AgentReport, BaseAgent

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"
CALIB_PATH = SAMPLES / "models" / "crack_calibration.json"
CACHE_DIR = SAMPLES / "cache"

# unified cascade level -> risk (S4 is "escalate same day" in cascade.prioritize)
LEVEL_RISK = {"S0": 0.05, "S1": 0.25, "S2": 0.5, "S3": 0.75, "S4": 0.95}

FEATURE_NAMES = ["longest_frac", "elongation", "thin_dark_frac", "edge_density", "components", "contrast"]


def _cascade():
    """Import the existing cascade package from src/ without installing it."""
    src = str(ROOT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    import cascade.gate as gate  # noqa: F401
    import cascade.grade as grade  # noqa: F401

    return gate, grade


# ---------------------------------------------------------------- opencv fallback


def crack_features(img_bgr: np.ndarray) -> tuple:
    """Classical crack evidence: thin dark connected structures that are long and elongated."""
    g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (227, 227), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(g, (3, 3), 0)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    bh = cv2.morphologyEx(g, cv2.MORPH_BLACKHAT, k)  # dark thin structures light up
    thr = max(18.0, float(bh.mean() + 2.5 * bh.std()))
    mask = (bh > thr).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    diag = float(np.hypot(*g.shape))
    longest, elong, bbox = 0.0, 1.0, [0, 0, 0, 0]
    big = 0
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if area < 25:
            continue
        big += 1
        extent = float(np.hypot(w, h))
        if extent > longest:
            longest = extent
            ys, xs = np.nonzero(lab == i)
            if xs.size >= 5:
                cov = np.cov(np.vstack([xs, ys]).astype(float))
                ev = np.sort(np.linalg.eigvalsh(cov))
                elong = float(np.sqrt(max(ev[1], 1e-6) / max(ev[0], 1e-6)))
            bbox = [int(x), int(y), int(x + w), int(y + h)]
    edges = cv2.Canny(g, 60, 150)
    feats = np.array([
        longest / diag,
        min(elong, 30.0) / 30.0,
        float(mask.mean()),
        float((edges > 0).mean()),
        min(big, 20) / 20.0,
        float(bh.max()) / 255.0,
    ])
    return feats, bbox


class OpenCVCrackScorer:
    """Logistic calibration over `crack_features`, fitted on a held-out split."""

    def __init__(self, coef: Optional[list] = None, intercept: float = 0.0, mean=None, std=None, meta=None) -> None:
        self.coef = np.array(coef) if coef is not None else None
        self.intercept = intercept
        self.mean = np.array(mean) if mean is not None else None
        self.std = np.array(std) if std is not None else None
        self.meta = meta or {}

    @classmethod
    def load(cls, path: Path = CALIB_PATH) -> "OpenCVCrackScorer":
        d = json.loads(Path(path).read_text())
        return cls(d["coef"], d["intercept"], d["mean"], d["std"], d.get("meta"))

    def fit(self, X: np.ndarray, y: np.ndarray, meta: Optional[dict] = None) -> "OpenCVCrackScorer":
        from sklearn.linear_model import LogisticRegression

        self.mean, self.std = X.mean(0), X.std(0) + 1e-9
        lr = LogisticRegression(C=1.0, max_iter=1000).fit((X - self.mean) / self.std, y)
        self.coef, self.intercept = lr.coef_[0], float(lr.intercept_[0])
        self.meta = meta or {}
        return self

    def save(self, path: Path = CALIB_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"features": FEATURE_NAMES, "coef": self.coef.tolist(), "intercept": self.intercept, "mean": self.mean.tolist(), "std": self.std.tolist(), "meta": self.meta}, indent=1))

    def prob(self, feats: np.ndarray) -> float:
        z = float(((feats - self.mean) / self.std) @ self.coef + self.intercept)
        return 1.0 / (1.0 + np.exp(-z))


# ---------------------------------------------------------------- backend selection


def _ollama_up() -> bool:
    import requests

    try:
        return requests.get(os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/tags", timeout=1).ok
    except Exception:
        return False


def pick_backend(requested: Optional[str] = None) -> str:
    # the pre-rename variable name still works
    b = (requested or os.getenv("CEREBRO_VISUAL_BACKEND") or os.getenv("SENTINEL_VISUAL_BACKEND") or "auto").lower()
    if b != "auto":
        return b
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    if _ollama_up():
        return "local"
    return "opencv"


# ---------------------------------------------------------------- the agent

ZONES = {
    "P1-parking": "Level P1 parking structure, column line C",
    "north-facade": "North facade, levels 2-4",
    "stair-core": "Stair core B, levels 1-3",
}


def replay_plan(images: List[Path], seed: int = 3) -> List[tuple]:
    """Scripted camera sweep over the building (the sweep is simulated; every image and score is real).

    Intact-surface frames rotate across all zones. Cracked frames are assigned to the P1
    parking structure, entering the sweep partway through so the zone's risk visibly rises.
    """
    rng = np.random.default_rng(seed)
    neg = [p for p in images if p.name.startswith("negative")]
    pos = [p for p in images if p.name.startswith("positive")]
    rng.shuffle(neg)
    rng.shuffle(pos)
    zones = list(ZONES)
    plan, ni, pi = [], 0, 0
    for step in range(len(images)):
        if step >= 18 and pi < len(pos) and step % 2 == 0:
            plan.append(("P1-parking", pos[pi]))
            pi += 1
        elif ni < len(neg):
            plan.append((zones[step % 3], neg[ni]))
            ni += 1
        elif pi < len(pos):
            plan.append(("P1-parking", pos[pi]))
            pi += 1
    return plan


class StructuralVisualAgent(BaseAgent):
    agent_id = "agent-0"
    subsystem = "structural_visual"
    name = "Structural Visual"
    description = "Crack and surface-damage detection on inspection imagery (existing cascade, wrapped)."

    def __init__(self, clock=None, backend: Optional[str] = None, image_dir: Optional[Path] = None, window: int = 6) -> None:
        super().__init__(clock)
        self.backend = pick_backend(backend)
        self.image_dir = Path(image_dir or SAMPLES / "crack")
        self.window = window
        self.frames = defaultdict(lambda: deque(maxlen=window))
        self.data_source = "Concrete crack images (CC BY 4.0, Oezgenel via HF mirror mohammadnajeeb/concrete_crack_images)"
        self._scorer: Optional[OpenCVCrackScorer] = None
        self._cache_path = CACHE_DIR / f"visual_{self.backend}.jsonl"
        self._cache = self._load_cache()

    # -- per-image scoring -------------------------------------------------

    def _load_cache(self) -> dict:
        if not self._cache_path.exists():
            return {}
        rows = [json.loads(l) for l in self._cache_path.read_text().splitlines() if l.strip()]
        return {r["sha"]: r for r in rows}

    def _remember(self, row: dict) -> dict:
        self._cache[row["sha"]] = row
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with self._cache_path.open("a") as fh:
            fh.write(json.dumps(row) + "\n")
        return row

    def score_image(self, path: Path) -> dict:
        data = Path(path).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        if sha in self._cache:
            return self._cache[sha]
        if self.backend == "opencv":
            if self._scorer is None:
                self._scorer = OpenCVCrackScorer.load()
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            feats, bbox = crack_features(img)
            p = self._scorer.prob(feats)
            row = {"sha": sha, "backend": "opencv", "risk": float(p), "confidence": float(0.5 + abs(p - 0.5)), "damage": bool(p >= 0.5),
                   "level": None, "bbox_227": bbox, "detail": {k: round(float(v), 4) for k, v in zip(FEATURE_NAMES, feats)}}
            return self._remember(row)
        return self._remember(self._score_with_cascade(path, sha))

    def _score_with_cascade(self, path: Path, sha: str) -> dict:
        from PIL import Image

        gate, grade = _cascade()
        img = Image.open(path)
        img.load()
        image_id = Path(path).stem
        g = gate.run_gate(img, image_id, backend=self.backend)
        row = {"sha": sha, "backend": f"cascade:{self.backend}", "damage": g.damage_present, "gate_reason": g.reason, "level": None, "bbox_227": None}
        if not g.routed:
            row.update(risk=0.05, confidence=g.confidence)
            return row
        rubric = grade.load_rubric("bridge_element")  # closest concrete rubric in the cascade (MBEI condition states)
        f = grade.grade_image(img, finding_id=f"{image_id}/full", image_id=image_id, asset_class="bridge_element", backend=self.backend, rubric=rubric,
                              metadata={"asset_class": "bridge_element", "image_size": f"{img.width}x{img.height}"})
        lvl = f.unified.level
        row.update(level=lvl, native=f.native_scale.value, defect=f.defect_type, justification=f.justification,
                   risk=LEVEL_RISK.get(lvl, 0.5), confidence=f.measurements.confidence if lvl != "U" else 0.2)
        return row

    # -- BaseAgent ---------------------------------------------------------

    def observations(self) -> Iterator[tuple]:
        images = sorted(self.image_dir.glob("*.jpg"))
        yield from replay_plan(images)

    def observe(self, obs: tuple) -> List[AgentReport]:
        zone, path = obs
        r = self.score_image(path)
        self.frames[zone].append((r["risk"], r["confidence"], path.name))
        reports = []
        for z, frames in self.frames.items():
            if z != zone:
                continue
            risks = np.array([f[0] for f in frames])
            risk = 0.7 * risks.max() + 0.3 * risks.mean()
            conf = float(np.mean([f[1] for f in frames])) * min(1.0, len(frames) / 3)
            flagged = int((risks >= 0.5).sum())
            headline = f"{flagged} of last {len(frames)} frames show crack evidence" if flagged else f"{len(frames)} recent frames clear"
            reports.append(self.report(
                risk=risk, confidence=conf, asset_id=z, zone=ZONES[z], headline=headline,
                evidence={"backend": r["backend"], "frame": path.name, "frame_risk": round(r["risk"], 3), "bbox_227": r.get("bbox_227"),
                          "cascade_level": r.get("level"), "features": r.get("detail"), "flagged_frames": flagged, "window": len(frames)},
                metrics={"frame_risk": round(r["risk"], 3), "flagged": flagged},
            ))
        return reports


def calibrate(n_per_class: int = 800, seed: int = 11) -> dict:
    """Fit the OpenCV fallback's logistic calibration on the first half of the crack test split,
    evaluate on a disjoint slice of the second half (the replay sample is excluded). Writes the model."""
    src = ROOT / "data" / "raw" / "crack_images" / "test"
    rng = np.random.default_rng(seed)
    replay = {p.name.split("_", 1)[1] for p in (SAMPLES / "crack").glob("*.jpg")}

    def load(files):
        X = []
        for f in files:
            feats, _ = crack_features(cv2.imread(str(f)))
            X.append(feats)
        return np.array(X)

    splits = {}
    for label, y in (("Positive", 1), ("Negative", 0)):
        files = sorted((src / label).glob("*.jpg"))
        half = len(files) // 2
        cal = rng.choice(files[:half], size=n_per_class, replace=False)
        ev_pool = [f for f in files[half:] if f.name not in replay]
        ev = rng.choice(ev_pool, size=n_per_class, replace=False)
        splits[label] = (cal, ev, y)
    Xc = np.vstack([load(splits[l][0]) for l in splits])
    yc = np.concatenate([[splits[l][2]] * n_per_class for l in splits])
    Xe = np.vstack([load(splits[l][1]) for l in splits])
    ye = np.concatenate([[splits[l][2]] * n_per_class for l in splits])
    sc = OpenCVCrackScorer().fit(Xc, yc)
    p = np.array([sc.prob(x) for x in Xe])
    pred = p >= 0.5
    tp, tn = int(((pred == 1) & (ye == 1)).sum()), int(((pred == 0) & (ye == 0)).sum())
    fp, fn = int(((pred == 1) & (ye == 0)).sum()), int(((pred == 0) & (ye == 1)).sum())
    bins = np.linspace(0, 1, 6)
    rel = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (p >= lo) & (p < hi if hi < 1 else p <= hi)
        if m.sum():
            rel.append({"bin": f"{lo:.1f}-{hi:.1f}", "n": int(m.sum()), "mean_pred": round(float(p[m].mean()), 3), "frac_positive": round(float(ye[m].mean()), 3)})
    meta = {"n_calibration": int(len(yc)), "n_eval": int(len(ye)), "accuracy": round((tp + tn) / len(ye), 4), "precision": round(tp / max(1, tp + fp), 4),
            "recall": round(tp / max(1, tp + fn), 4), "tp": tp, "tn": tn, "fp": fp, "fn": fn, "reliability": rel,
            "brier": round(float(np.mean((p - ye) ** 2)), 4)}
    sc.meta = meta
    sc.save()
    return meta
