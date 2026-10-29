"""Đọc production.toml + kịch bản + timing, dùng chung cho vgen.py và storyboard.py."""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import vscript

FRAMES = {
    # tên: (trái, trên, phải, dưới) theo tỉ lệ khung
    "full": (0.0, 0.0, 1.0, 1.0),
    "upper": (0.06, 0.12, 0.94, 0.46),
    "lower": (0.06, 0.52, 0.94, 0.80),
    "center": (0.12, 0.28, 0.88, 0.68),
    "card-left": (0.05, 0.50, 0.55, 0.76),
    "card-right": (0.45, 0.50, 0.95, 0.76),
    "phone": (0.32, 0.44, 0.68, 0.76),
}

RATES = {"vi": 4.5, "en": 3.0}


class Production:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self.root = self.path.parent
        self.cfg = tomllib.loads(self.path.read_text())
        p = self.cfg.setdefault("project", {})
        self.name = p.get("name", self.root.name)
        self.W, self.H = int(p.get("width", 1080)), int(p.get("height", 1920))
        self.fps = int(p.get("fps", 30))
        self.lang = p.get("lang", "vi")
        self.accent = p.get("accent", "#FFE14D")
        self.script_path = self.root / p.get("script", "script.vs")
        self.script = vscript.parse(self.script_path.read_text())
        self.takes = {k: self.root / v for k, v in self.cfg.get("takes", {}).items()}
        self.shots = self.cfg.get("shot", [])
        self.timing, self.timing_source = self._timing()

    # ------------------------------------------------------------ timing
    def timing_path(self) -> Path:
        return self.script_path.with_suffix(".timing.json")

    def _timing(self) -> tuple[dict, str]:
        tp = self.timing_path()
        if tp.exists():
            return json.loads(tp.read_text()), "align"
        return self.estimated_timing(), "estimate"

    def estimated_timing(self, gap: float = 0.3) -> dict:
        """Thời gian giả định theo tốc độ nói, dùng cho storyboard/animatic trước khi có A-roll."""
        sc = vscript.parse(self.script_path.read_text())
        step = 1.0 / RATES.get(self.lang, 4.0)
        t, seg_windows = 0.0, {}
        for s in sc.segments:
            start = t
            for u in (u for u in sc.units if u.segment == s):
                u.start = round(t, 3)
                t += step * max(1, len(u.spoken))
                u.end = round(t, 3)
                if re.search(r"[.!?…,;:]$", u.display):
                    t += 0.15
            seg_windows[s] = [round(start, 3), round(t, 3)]
            t += gap
        res = vscript.resolve(sc, seg_windows)
        return {
            "script": self.script_path.name, "duration": round(t - gap, 3),
            "segments": {s: {"start": w[0], "end": w[1]} for s, w in seg_windows.items()},
            "takes": [], **res,
            "words": [{"display": u.display, "spoken": " ".join(u.spoken), "start": u.start, "end": u.end,
                       "segment": u.segment, "role": u.role, "attrs": u.attrs} for u in sc.units],
            "cues": vscript.build_cues(sc),
        }

    def window(self, during: str | None) -> tuple[float, float] | None:
        if not during:
            return None
        tm = self.timing
        m = re.fullmatch(r"moment:([a-z0-9_-]+)(?:\+([0-9.]+))?", during)
        if m:
            t = tm["moments"][m.group(1)]
            return t, t + float(m.group(2) or 1.5)
        if during.startswith("segment:"):
            s = tm["segments"][during.split(":", 1)[1]]
            return s["start"], s["end"]
        if during in tm["selections"]:
            s = tm["selections"][during]
            return s["start"], s["end"]
        raise SystemExit(f"shot during='{during}' không khớp Selection/Segment/Moment nào trong kịch bản")

    # ------------------------------------------------------------ shots
    def shot(self, sid: str) -> dict:
        for s in self.shots:
            if s["id"] == sid:
                return s
        raise SystemExit(f"không có shot '{sid}' trong {self.path.name}")

    def asset(self, shot: dict) -> Path | None:
        a = shot.get("asset")
        p = self.root / a if a else None
        return p if p and p.exists() else None

    def candidates(self, shot: dict) -> list[Path]:
        d = self.root / "assets" / "gen" / shot["id"]
        return sorted(p for p in d.glob("*") if p.suffix.lower() in MEDIA_EXT) if d.exists() else []

    def script_excerpt(self, during: str | None) -> str:
        w = self.window(during)
        if not w:
            return ""
        a, b = w
        return " ".join(x["display"] for x in self.timing["words"]
                        if x["display"] and x["start"] is not None and x["start"] >= a - 1e-3 and x["end"] <= b + 1e-3)


MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".webm"}
VIDEO_EXT = {".mp4", ".mov", ".webm"}
