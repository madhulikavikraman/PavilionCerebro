"""Pavilion Cerebro live dashboard server (local prototype). Standard library only.

  python -m dashboard.server            # http://localhost:8765
  python -m dashboard.server --port 9000 --interval 1.0 --visual-backend opencv

A background thread steps the swarm on a timer (one replay hour per tick) and pushes
each new coordinator snapshot to the browser over Server-Sent Events, so numbers tick
as the real datasets replay. At the end of the scenario it pauses, then restarts.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import queue
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from coordinator.swarm import Swarm  # noqa: E402

STATIC = Path(__file__).parent / "static"
CRACK = ROOT / "data" / "samples" / "crack"


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def _clean(o):
    """NaN/inf are not valid JSON; send null."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return float(o) if np.isfinite(o) else None
    return o


def dumps(o) -> str:
    return json.dumps(_clean(o), default=_default)


class Runtime:
    def __init__(self, interval: float, visual_backend: str | None) -> None:
        self.interval = interval
        self.visual_backend = visual_backend
        self.speed = 1.0
        self.paused = False
        self.lock = threading.Lock()
        self.clients: list[queue.Queue] = []
        self.swarm = Swarm(visual_backend=visual_backend)
        self.snapshot = self.swarm.snapshot()
        self.loops = 0

    def publish(self) -> None:
        self.snapshot = self.swarm.snapshot()
        self.snapshot["control"] = {"paused": self.paused, "speed": self.speed, "loops": self.loops}
        msg = dumps(self.snapshot)
        for q in list(self.clients):
            try:
                q.put_nowait(msg)
            except queue.Full:
                pass

    def run(self) -> None:
        while True:
            if not self.paused:
                with self.lock:
                    if self.swarm.finished:
                        self.publish()
                        time.sleep(8)
                        mode = self.swarm.coord.mode
                        self.swarm = Swarm(visual_backend=self.visual_backend)
                        if mode != "normal":
                            self.swarm.coord.set_mode(mode)
                        self.loops += 1
                    self.swarm.step()
                    self.publish()
            time.sleep(self.interval / self.speed)

    def control(self, body: dict) -> dict:
        with self.lock:
            act = body.get("action")
            if act == "mode":
                res = self.swarm.coord.set_mode(body.get("mode", "normal"))
            elif act == "pause":
                self.paused = True
                res = {}
            elif act == "resume":
                self.paused = False
                res = {}
            elif act == "speed":
                self.speed = float(min(8.0, max(0.25, float(body.get("speed", 1)))))
                res = {}
            elif act == "restart":
                mode = self.swarm.coord.mode
                self.swarm = Swarm(visual_backend=self.visual_backend)
                if mode != "normal":
                    self.swarm.coord.set_mode(mode)
                res = {}
            else:
                return {"error": f"unknown action {act}"}
            self.publish()
            return {"ok": True, **res}


RT: Runtime


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/state":
            return self._send(200, dumps(RT.snapshot).encode(), "application/json")
        if path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q: queue.Queue = queue.Queue(maxsize=4)
            RT.clients.append(q)
            try:
                self.wfile.write(f"data: {dumps(RT.snapshot)}\n\n".encode())
                self.wfile.flush()
                while True:
                    try:
                        msg = q.get(timeout=15)
                        self.wfile.write(f"data: {msg}\n\n".encode())
                    except queue.Empty:
                        self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                RT.clients.remove(q)
            return
        if path.startswith("/img/"):
            f = CRACK / Path(path[5:]).name
            if f.exists():
                return self._send(200, f.read_bytes(), "image/jpeg")
            return self._send(404, b"not found", "text/plain")
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        f = (STATIC / rel).resolve()
        if STATIC.resolve() in f.parents and f.exists():
            return self._send(200, f.read_bytes(), mimetypes.guess_type(str(f))[0] or "application/octet-stream")
        return self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/control":
            return self._send(404, b"not found", "text/plain")
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        return self._send(200, dumps(RT.control(body)).encode(), "application/json")


def main() -> int:
    global RT
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--interval", type=float, default=1.2, help="seconds per replay tick at 1x")
    ap.add_argument("--visual-backend", default=None, help="auto | opencv | local | claude (default: CEREBRO_VISUAL_BACKEND or auto)")
    args = ap.parse_args()
    RT = Runtime(args.interval, args.visual_backend)
    threading.Thread(target=RT.run, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    srv.daemon_threads = True
    print(f"Pavilion Cerebro dashboard: http://localhost:{args.port}  (visual backend: {RT.swarm.agents[0].backend})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
