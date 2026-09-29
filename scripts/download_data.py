"""Download the demo datasets into data/raw/<name>/ and record the license text found.

Usage: python scripts/download_data.py corrosion_cs ir_solar
Sources and licenses: docs/research/07_datasets_for_demo.md and docs/decisions.md D-006.
dacl10k and RescueNet come from Hugging Face mirrors via scripts/download_hf.py.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

SOURCES = {
    "corrosion_cs": {
        "license": "CC0 (figshare record 16624663)",
        "files": {
            "Corrosion Condition State Classification.zip": "https://ndownloader.figshare.com/files/31729733",
            "Corrosion Annotation Guidelines.pdf": "https://ndownloader.figshare.com/files/30914467",
            "README_corrosion_dataset.rtf": "https://ndownloader.figshare.com/files/30930610",
        },
        "unzip": ["Corrosion Condition State Classification.zip"],
    },
    "ir_solar": {
        "license": "MIT (RaptorMaps/InfraredSolarModules); HF mirror tester202405/InfraredSolarModules",
        "files": {
            "test-00000-of-00001.parquet": "https://huggingface.co/datasets/tester202405/InfraredSolarModules/resolve/main/data/test-00000-of-00001.parquet",
            "train-00000-of-00001.parquet": "https://huggingface.co/datasets/tester202405/InfraredSolarModules/resolve/main/data/train-00000-of-00001.parquet",
        },
    },
}


def fetch(url: str, dest: Path, chunk: int = 1 << 20) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"exists: {dest.name}")
        return
    with requests.get(url, stream=True, timeout=120, allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        tmp = dest.with_suffix(dest.suffix + ".part")
        with tmp.open("wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
            for part in r.iter_content(chunk):
                f.write(part)
                bar.update(len(part))
        tmp.rename(dest)


def download(name: str) -> None:
    spec = SOURCES[name]
    out = RAW / name
    out.mkdir(parents=True, exist_ok=True)
    for fname, url in spec["files"].items():
        fetch(url, out / fname)
    for z in spec.get("unzip", []):
        zp = out / z
        marker = out / (z + ".extracted")
        if zp.exists() and not marker.exists():
            print(f"extracting {z}")
            with zipfile.ZipFile(zp) as zf:
                zf.extractall(out)
            marker.write_text("ok")
    (out / "LICENSE_NOTE.json").write_text(json.dumps({"dataset": name, "license_per_source": spec["license"], "verify": "confirm against the license text inside the download"}, indent=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+", choices=sorted(SOURCES))
    args = ap.parse_args()
    for n in args.names:
        download(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
