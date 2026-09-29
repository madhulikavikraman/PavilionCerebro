"""Download the five public datasets Pavilion Cerebro replays into data/raw/ (gitignored).

  python data/download_datasets.py            # all
  python data/download_datasets.py hvac battery

Then `python data/prepare_samples.py` rebuilds data/samples/ (already committed, so this is
only needed to regenerate them). Sources and licenses:

  upv      Durrani & Haroon (2025), UHPC compressive strength / UPV / rebound hammer, UMN DRUM,
           doi:10.13020/h3m2-1h76, CC0
  bms      CU-BEMS smart building electricity and indoor environmental sensor data, Chulalongkorn
           University, figshare 11726517, CC BY 4.0 (floor 2, 2018). Substitute for the IEEE DataPort
           Honeywell AHU dataset, which requires a paid DataPort subscription.
  battery  NASA Ames PCoE Li-ion Battery Aging (B0005/6/7/18), PHM Society S3 mirror
  hvac     ASHRAE RP-1043 chiller fault data, figshare 28435232, CC0
  crack    Concrete Crack Images for Classification (Oezgenel, CC BY 4.0), test split of the Hugging
           Face mirror mohammadnajeeb/concrete_crack_images
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
UA = {"User-Agent": "Mozilla/5.0 (pavilion-cerebro dataset fetch)"}

SOURCES = {
    "upv": [("umn_upv/UHPC_NDE_Dataset.xlsx", "https://conservancy.umn.edu/server/api/core/bitstreams/34ed3a86-bc5a-4fce-9db9-f37a3ecfd1a9/content"),
            ("umn_upv/README_UHPC_NDE.txt", "https://conservancy.umn.edu/server/api/core/bitstreams/0983c6d0-d0cf-4d5b-84e9-f65c1cd9a151/content")],
    "bms": [("cu_bems/2018Floor2.csv", "https://ndownloader.figshare.com/files/21350166")],
    "battery": [("nasa_battery/battery.zip", "https://phm-datasets.s3.amazonaws.com/NASA/5.+Battery+Data+Set.zip")],
    "hvac": [("ashrae_rp1043/rp1043.zip", "https://ndownloader.figshare.com/files/52432007")],
    "crack": [("crack_images/test.zip", "https://huggingface.co/datasets/mohammadnajeeb/concrete_crack_images/resolve/main/data/test.zip")],
}


def fetch(rel: str, url: str) -> Path:
    dest = RAW / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"exists: {rel}")
        return dest
    print(f"downloading {rel} ...")
    with requests.get(url, headers=UA, stream=True, timeout=300) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with tmp.open("wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
        tmp.rename(dest)
    return dest


def unzip(path: Path, into: Path) -> None:
    with zipfile.ZipFile(path) as z:
        z.extractall(into)


def main(names) -> int:
    for name in names or list(SOURCES):
        for rel, url in SOURCES[name]:
            p = fetch(rel, url)
            if p.suffix == ".zip":
                unzip(p, p.parent)
        if name == "battery":
            inner = RAW / "nasa_battery" / "5. Battery Data Set" / "1. BatteryAgingARC-FY08Q4.zip"
            unzip(inner, inner.parent / "fy08q4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
