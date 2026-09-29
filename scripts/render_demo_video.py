"""Render the Pavilion Cerebro demo walkthrough, frame by frame (not a screen recording).

  python scripts/render_demo_video.py            # -> site/assets/pavilion_cerebro_demo.mp4 (+ poster and stills)

How: the real swarm runs headless over the real datasets and every coordinator snapshot is
recorded. The real dashboard page is then loaded in headless Chromium in static mode and
each recorded snapshot is injected and screenshotted. Pillow composes those screenshots
into shots (crops, slow zooms, captions, title cards) and ffmpeg (imageio-ffmpeg) encodes
them. Every number on screen is what the pipeline produced; the building and the
mitigation actions are simulated, and the caption says so from the second scene onward.

Requires: pip install playwright && python -m playwright install chromium
"""

from __future__ import annotations

import io
import json
import sys
import threading
import warnings
from http.server import ThreadingHTTPServer
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from coordinator.swarm import Swarm  # noqa: E402
from dashboard.server import Handler, dumps  # noqa: E402

W, H, FPS = 1280, 720, 24
BG = (11, 13, 14)
INK = (238, 240, 241)
INK2 = (183, 190, 195)
MUTED = (125, 134, 140)
ACCENT = (57, 135, 229)
CRIT = (208, 59, 59)
LINE = (38, 43, 47)
FONTS = ROOT / "assets" / "fonts"
OUT_DIR = ROOT / "site" / "assets"
CAPTION = "Simulated monitoring feed - detection logic and readings are from real public datasets, replayed live."


def font(kind: str, size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    if kind == "mono":
        return ImageFont.truetype(str(FONTS / ("IBMPlexMono-SemiBold.ttf" if weight >= 600 else "IBMPlexMono-Regular.ttf")), size)
    f = ImageFont.truetype(str(FONTS / "IBMPlexSans-Variable.ttf"), size)
    try:
        f.set_variation_by_axes([weight, 100])
    except Exception:
        pass
    return f


# ------------------------------------------------------------------ 1. record the run


def record() -> dict:
    sw = Swarm(visual_backend="opencv")
    snaps = {0: json.loads(dumps(sw.snapshot()))}
    while not sw.finished:
        sw.step()
        snaps[sw.tick] = json.loads(dumps(sw.snapshot()))
    mit = [e for e in sw.coord.mitigation.log if e["type"] == "mitigation"]
    first = lambda sub: next(e["tick"] for e in mit if e["subsystem"] == sub)
    # a second run to the disaster moment: normal snapshot, flip, then a few ticks in disaster mode
    t_dis = 132
    s2 = Swarm(visual_backend="opencv")
    while s2.tick < t_dis:
        s2.step()
    before = json.loads(dumps(s2.snapshot()))
    rr = s2.coord.set_mode("disaster")
    after = [json.loads(dumps(s2.snapshot()))]
    for _ in range(6):
        s2.step()
        after.append(json.loads(dumps(s2.snapshot())))
    return {"snaps": snaps, "t_struct": first("structural_visual"), "t_batt": first("battery"), "t_hvac": first("hvac"),
            "dis_before": before, "dis_after": after, "rerank": rr}


# ------------------------------------------------------------------ 2. screenshot the real dashboard


class Shooter:
    SELECTORS = {"top": "header.top", "health": ".panel.health", "map": ".panel.building", "a0": "#card-agent-0", "a1": "#card-agent-1",
                 "a2": "#card-agent-2", "a3": "#card-agent-3", "queue": ".panel.queue", "feed": ".panel.feed", "agents": "#agents"}

    def __init__(self) -> None:
        from playwright.sync_api import sync_playwright

        self.srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch()
        self.page = self.browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        self.page.goto(f"http://127.0.0.1:{self.srv.server_port}/?static=1")
        self.page.evaluate("document.fonts.ready")
        self.page.wait_for_function("window.cerebroRender !== undefined")

    def shot(self, snap: dict, settle_ms: int = 750) -> tuple:
        self.page.evaluate("s => window.cerebroRender(s)", snap)
        self.page.wait_for_timeout(settle_ms)
        return self.capture()

    def capture(self) -> tuple:
        png = self.page.screenshot(full_page=True)
        img = Image.open(io.BytesIO(png)).convert("RGB")
        boxes = {}
        for k, sel in self.SELECTORS.items():
            bb = self.page.evaluate(f"(() => {{ const e = document.querySelector('{sel}'); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left + scrollX, r.top + scrollY, r.width, r.height]; }})()")
            if bb:
                boxes[k] = tuple(v * 2 for v in bb)  # device scale 2
        return img, boxes

    def close(self) -> None:
        self.browser.close()
        self.pw.stop()
        self.srv.shutdown()


# ------------------------------------------------------------------ 3. compose frames


def union(*boxes):
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y1 = max(b[1] + b[3] for b in boxes)
    return (x0, y0, x1 - x0, y1 - y0)


def lerp_box(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(4))


def ease(t):
    return t * t * (3 - 2 * t)


def place(img: Image.Image, box, area=(0, 56, W, H - 44), pad=24) -> Image.Image:
    """Crop `box` (x, y, w, h) from the screenshot and fit it inside `area` of a 1280x720 frame."""
    x, y, w, h = box
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(img.width, x + w + pad), min(img.height, y + h + pad)
    crop = img.crop((int(x0), int(y0), int(x1), int(y1)))
    ax0, ay0, ax1, ay1 = area
    s = min((ax1 - ax0) / crop.width, (ay1 - ay0) / crop.height)
    crop = crop.resize((max(1, int(crop.width * s)), max(1, int(crop.height * s))), Image.LANCZOS)
    frame = Image.new("RGB", (W, H), BG)
    frame.paste(crop, (ax0 + (ax1 - ax0 - crop.width) // 2, ay0 + (ay1 - ay0 - crop.height) // 2))
    return frame


def hud(frame: Image.Image, label: str, sub: str = "", caption: bool = True) -> Image.Image:
    d = ImageDraw.Draw(frame)
    d.rectangle([0, 0, W, 52], fill=(14, 17, 18))
    d.line([0, 52, W, 52], fill=LINE)
    hexmark(d, 30, 26, 13, ACCENT)
    d.text((52, 14), "PAVILION CEREBRO", font=font("mono", 18, 600), fill=INK)
    d.text((250, 17), label, font=font("mono", 15, 600), fill=ACCENT)
    if sub:
        d.text((W - 24, 17), sub, font=font("sans", 14), fill=INK2, anchor="ra")
    if caption:
        d.rectangle([0, H - 40, W, H], fill=(14, 17, 18))
        d.line([0, H - 40, W, H - 40], fill=LINE)
        d.text((W // 2, H - 20), CAPTION, font=font("sans", 15), fill=INK2, anchor="mm")
    return frame


def hexmark(d: ImageDraw.ImageDraw, cx, cy, r, color, width=2):
    pts = [(cx + r * np.cos(np.pi / 6 + k * np.pi / 3), cy + r * np.sin(np.pi / 6 + k * np.pi / 3)) for k in range(6)]
    d.line(pts + [pts[0]], fill=color, width=width)
    d.ellipse([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25], fill=color)


def callout(frame: Image.Image, text: str, y: int = 76, color=CRIT) -> Image.Image:
    d = ImageDraw.Draw(frame)
    f = font("mono", 16, 600)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([W // 2 - tw / 2 - 14, y - 6, W // 2 + tw / 2 + 14, y + 26], radius=4, fill=color)
    d.text((W // 2, y + 10), text, font=f, fill=(255, 255, 255), anchor="mm")
    return frame


def title_card(t: float, metrics: dict) -> Image.Image:
    f = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(f)
    a = min(1.0, t * 2)
    col = tuple(int(BG[i] + (INK[i] - BG[i]) * a) for i in range(3))
    hexmark(d, W // 2, 205, 46, ACCENT, width=4)
    d.text((W // 2, 300), "P A V I L I O N   C E R E B R O", font=font("mono", 44, 600), fill=col, anchor="mm")
    d.text((W // 2, 360), "A coordinated swarm of specialist AI agents for building structural health,", font=font("sans", 24), fill=INK2, anchor="mm")
    d.text((W // 2, 392), "damage detection and maintenance prediction.", font=font("sans", 24), fill=INK2, anchor="mm")
    if t > 0.35:
        box_w = 980
        d.rounded_rectangle([W // 2 - box_w // 2, 470, W // 2 + box_w // 2, 540], radius=6, outline=ACCENT, width=2)
        d.text((W // 2, 505), CAPTION, font=font("sans", 20, 500), fill=INK, anchor="mm")
    return f


def end_card(t: float, m: dict) -> Image.Image:
    f = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(f)
    hexmark(d, W // 2, 90, 26, ACCENT, width=3)
    d.text((W // 2, 150), "Measured on real public data (scripts/selfcheck.py)", font=font("sans", 22, 600), fill=INK, anchor="mm")
    h = m["headline"]
    stats = [
        (f"{h['subsystems_monitored']}", "subsystems monitored by live agents"),
        (f"{h['real_fault_cases_flagged']}", "real fault cases flagged (ASHRAE, NASA, UMN UPV, CU-BEMS)"),
        (f"{100 * h['hvac_diagnosis_accuracy']:.1f}%", "chiller fault diagnosis, leave-one-severity-out"),
        (f"{100 * h['hvac_false_alarm_rate']:.1f}%", "false alarms on held-out fault-free chiller runs"),
        (f"{h['battery_rul_mae_cycles']:.1f}", "cycles mean error, battery remaining-useful-life"),
        (f"{h['rerank_ms_mean']:.2f} ms", "average re-triage when disaster mode flips"),
    ]
    for i, (v, lab) in enumerate(stats):
        col, row = i % 2, i // 2
        x, y = 170 + col * 500, 215 + row * 120
        if t * 8 > i:
            d.text((x, y), v, font=font("mono", 44, 600), fill=INK)
            d.text((x, y + 58), lab, font=font("sans", 17), fill=INK2)
    d.text((W // 2, H - 60), "Hackathon prototype. Building, mitigation actions and roadmap agents are simulated; data and detection logic are real.",
           font=font("sans", 16), fill=MUTED, anchor="mm")
    return f


def crossfade(a: Image.Image, b: Image.Image, n: int = 8):
    for i in range(1, n + 1):
        yield Image.blend(a, b, i / (n + 1))


# ------------------------------------------------------------------ 4. the cut


def build(rec: dict, metrics: dict, sh: Shooter):
    snaps = rec["snaps"]
    cache: dict = {}

    def at(t: int):
        if t not in cache:
            cache[t] = sh.shot(snaps[t])
        return cache[t]

    shots = []  # list of generators of frames, one per scene

    # S1 title with the simulated-feed caption
    def s1():
        for i in range(int(5.5 * FPS)):
            yield title_card(i / (5.5 * FPS), metrics)
    shots.append(s1)

    # S2 establishing: building swarm map, slow push-in
    def s2():
        img, bx = at(20)
        n = int(6 * FPS)
        full = union(bx["health"], bx["map"])
        for i in range(n):
            b = lerp_box(full, bx["map"], ease(i / n))
            yield hud(place(img, b), "THE BUILDING", "one coordinator, four live agents, two on the roadmap")
    shots.append(s2)

    def agent_scene(key, label, sub, t0, t1, seconds, note=None, note_from=None):
        def gen():
            ticks = list(range(t0, t1 + 1))
            n = int(seconds * FPS)
            for i in range(n):
                t = ticks[min(len(ticks) - 1, int(i / n * len(ticks)))]
                img, bx = at(t)
                fr = hud(place(img, bx[key], area=(140, 64, W - 140, H - 50)), label, sub + f"   replay tick {t}")
                if note and note_from is not None and t >= note_from:
                    fr = callout(fr, note, y=H - 82)
                yield fr
        return gen

    ts = rec["t_struct"]
    shots.append(agent_scene("a0", "AGENT 0  STRUCTURAL VISUAL", "existing inspection cascade, wrapped", ts - 14, ts + 2, 8,
                             "P1 parking: crack evidence persists - zone critical", ts))
    shots.append(agent_scene("a1", "AGENT 1  INTERNAL SENSORS", "UPV material health + BMS telemetry, one scorer", 52, 70, 8))
    tb = rec["t_batt"]
    shots.append(agent_scene("a2", "AGENT 2  BATTERY & FIRE RISK", "NASA Li-ion aging cells, SOH and RUL", tb - 16, tb + 2, 8,
                             "Cell past end-of-life with impedance growth: fire-risk precursor", tb))
    th = rec["t_hvac"]
    shots.append(agent_scene("a3", "AGENT 3  HVAC CHILLER", "ASHRAE RP-1043, refrigerant leak progressing SL1 to SL4", th - 13, th + 1, 8))

    # S7 coordinator populating: full dashboard, ticks racing from 0
    def s7():
        n = int(9 * FPS)
        ticks = list(range(1, 101, 2))
        for i in range(n):
            t = ticks[min(len(ticks) - 1, int(i / n * len(ticks)))]
            img, bx = at(t)
            view = (0, 0, img.width, min(img.height, 2000))
            yield hud(place(img, view, area=(0, 56, W, H - 44), pad=0), "COORDINATOR", f"all agents fused into one ranked picture   tick {t}")
    shots.append(s7)

    # S8 mitigation fires: queue + feed around the chiller isolation
    def s8():
        n = int(8 * FPS)
        ticks = list(range(th - 3, th + 5))
        for i in range(n):
            t = ticks[min(len(ticks) - 1, int(i / n * len(ticks)))]
            img, bx = at(t)
            fr = hud(place(img, union(bx["a3"], bx["queue"]), area=(40, 64, W - 40, H - 50)), "SELF-HEALING", f"threshold crossed, simulated action logged   tick {t}")
            if t >= th:
                fr = callout(fr, "SIMULATED ACTION: CH-1 isolated, cooling switched to backup CH-2", y=H - 82)
            yield fr
    shots.append(s8)

    # S9 disaster toggle: before, flip (mid-animation frames), after
    def s9():
        img, bx = sh.shot(rec["dis_before"])
        for _ in range(int(2.5 * FPS)):
            yield hud(place(img, union(bx["top"], bx["queue"]), area=(40, 64, W - 40, H - 50)), "DISASTER MODE", "normal ranking: risk x consequence x time")
        sh.page.evaluate("s => window.cerebroRender(s)", rec["dis_after"][0])
        mids = []
        for ms in (0, 120, 240, 360, 480, 650):
            sh.page.wait_for_timeout(ms - (mids[-1][0] if mids else 0))
            mids.append((ms, sh.capture()))
        for ms, (img2, bx2) in mids:
            fr = hud(place(img2, union(bx2["top"], bx2["queue"]), area=(40, 64, W - 40, H - 50)), "DISASTER MODE", "toggled: triage by severity only")
            for _ in range(5):
                yield callout(fr.copy(), f"Re-triaged {len(rec['rerank']['moved'])} concerns in {rec['rerank']['ms']:.2f} ms", y=H - 82)
        for s in rec["dis_after"][1:]:
            img3, bx3 = sh.shot(s)
            fr = hud(place(img3, union(bx3["top"], bx3["queue"]), area=(40, 64, W - 40, H - 50)), "DISASTER MODE", "triage by severity only")
            for _ in range(int(0.6 * FPS)):
                yield fr
    shots.append(s9)

    def s10():
        for i in range(int(7 * FPS)):
            yield end_card(i / (7 * FPS), metrics)
    shots.append(s10)
    return shots


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = json.loads((ROOT / "data" / "samples" / "metrics.json").read_text())
    print("recording swarm run...")
    rec = record()
    print(f"  structural action t{rec['t_struct']}, battery t{rec['t_batt']}, hvac t{rec['t_hvac']}")
    sh = Shooter()
    out = OUT_DIR / "pavilion_cerebro_demo.mp4"
    writer = imageio.get_writer(str(out), fps=FPS, codec="libx264", quality=None, pixelformat="yuv420p",
                                ffmpeg_params=["-crf", "26", "-preset", "medium", "-movflags", "+faststart"])
    stills = {}
    last = None
    n = 0
    try:
        for si, scene in enumerate(build(rec, metrics, sh)):
            first = True
            k = 0
            for fr in scene():
                if first and last is not None:
                    for x in crossfade(last, fr):
                        writer.append_data(np.asarray(x))
                        n += 1
                first = False
                writer.append_data(np.asarray(fr))
                n += 1
                last = fr
                if k % 12 == 0:
                    stills.setdefault(si, []).append(fr)
                k += 1
            print(f"  scene {si + 1} done ({n} frames)")
            keep = stills[si]
            stills[si] = keep[len(keep) * 2 // 3]
    finally:
        writer.close()
        sh.close()
    stills[1].save(OUT_DIR / "poster.jpg", quality=88)
    for si, name in ((2, "still_crack.jpg"), (3, "still_sensors.jpg"), (4, "still_battery.jpg"), (5, "still_hvac.jpg"), (6, "still_dashboard.jpg"), (7, "still_mitigation.jpg"), (8, "still_disaster.jpg")):
        stills[si].save(OUT_DIR / name, quality=85)
    print(f"wrote {out.relative_to(ROOT)}: {n} frames, {n / FPS:.1f}s, {out.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
