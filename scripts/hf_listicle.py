#!/usr/bin/env python3
"""Sinh project HyperFrames cho hiệu ứng "danh sách tô sáng + khung điện thoại".

Tái hiện hệ thống hình của reel mẫu (examples/tenfoldmarc-17-effects): bảng danh sách đánh số cố định,
mục đang nói đổi màu nhấn, và một khung điện thoại đặt trên A-roll để chiếu demo từng mục, kèm bộ đếm N/M.

    python3 scripts/hf_listicle.py config.json --out projects/demo/hf
    python3 scripts/hf_listicle.py config.json --transcript ref/transcript.json --out ...

`--transcript` (transcript.json của vkit) tự điền mốc `at` cho từng mục bằng cách tìm từ đầu tiên
của nhãn (hoặc trường `match`) trong lời thoại, theo thứ tự.

Mọi phần tử có thời gian đều được viết tĩnh trong HTML (class="clip", data-start, data-duration)
để chỉnh được trong HyperFrames Studio. Sau khi sinh: copy A-roll và ảnh demo vào assets/, rồi
`npx hyperframes check --json` → `npx hyperframes preview`.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path

W, H = 1080, 1920


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9đ]+", "", s.replace("đ", "d"))


def fill_times(items: list[dict], transcript: Path) -> None:
    words = json.loads(transcript.read_text())["words"]
    i = 0
    for it in items:
        if "at" in it:
            continue
        key = norm(re.split(r"[\s\-_/]+", (it.get("match") or it["label"]).strip())[0])
        while i < len(words) and not norm(words[i]["word"]).startswith(key):
            i += 1
        if i == len(words):
            raise SystemExit(f"không tìm thấy '{key}' trong lời thoại — thêm 'at' hoặc 'match' cho mục này")
        it["at"] = words[i]["start"]
        i += 1


def fmt(t: float) -> str:
    return f"{t:.2f}".rstrip("0").rstrip(".")


def build_scene(cfg: dict) -> str:
    items = cfg["items"]
    n = len(items)
    accent = cfg.get("accent", "#FFE14D")
    list_end = cfg["list_end"]
    half = -(-n // 2)
    cols = [items[:half], items[half:]]

    rows = []
    for c, col in enumerate(cols):
        lis = []
        for k, it in enumerate(col):
            idx = k + c * half
            lis.append(f'          <li id="li-{idx + 1:02d}"><span class="no">{idx + 1:02d}</span>'
                       f'{html.escape(it["label"])}</li>')
        rows.append(f'        <ol class="col col-{c}">\n' + "\n".join(lis) + "\n        </ol>")

    demos, counters, tweens = [], [], []
    for idx, it in enumerate(items):
        start = it["at"]
        end = items[idx + 1]["at"] if idx + 1 < n else list_end
        dur = fmt(end - start)
        if it.get("demo"):
            attrs = (f'id="demo-{idx + 1:02d}" class="clip demo" src="{html.escape(it["demo"])}"'
                     f' data-start="{fmt(start)}" data-duration="{dur}"')
            if it["demo"].endswith((".mp4", ".webm", ".mov")):
                demos.append(f"        <video {attrs} muted playsinline></video>")
            else:
                demos.append(f'        <img {attrs} alt="" />')
        counters.append(f'        <span id="count-{idx + 1:02d}" class="clip count" data-start="{fmt(start)}"'
                        f' data-duration="{dur}">{idx + 1:02d}/{n:02d}</span>')
        sel = f"#li-{idx + 1:02d}"
        tweens.append(f'      tl.fromTo("{sel}", {{ color: DIM, scale: 1 }}, '
                      f'{{ color: ACCENT, scale: 1.06, duration: 0.12, ease: "power3.out" }}, {fmt(start)});')
        tweens.append(f'      tl.fromTo("{sel}", {{ color: ACCENT, scale: 1.06 }}, '
                      f'{{ color: DIM, scale: 1, duration: 0.1, ease: "power2.in" }}, {fmt(max(start, end - 0.1))});')

    title_num = html.escape(str(cfg.get("title_number", n)))
    title_rest = html.escape(cfg.get("title", "mẹo bạn cần biết"))
    title_2 = html.escape(cfg.get("title_line2", ""))

    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; font-family: "Inter", sans-serif; }}
    #lc-head {{ position: absolute; left: 0; right: 0; top: 230px; text-align: center; color: #fff;
      font-weight: 900; font-size: 74px; line-height: 0.98; letter-spacing: -2px;
      text-shadow: 0 4px 18px rgba(0,0,0,.45); }}
    #lc-head .num {{ color: {accent}; }}
    #lc-board {{ position: absolute; left: 48px; right: 48px; top: 420px; display: flex;
      justify-content: space-between; }}
    .col {{ list-style: none; margin: 0; padding: 18px 26px; border-radius: 26px;
      background: rgba(20,20,20,.42); backdrop-filter: blur(14px); }}
    .col li {{ font-weight: 700; font-size: 31px; line-height: 1.32; color: rgba(255,255,255,.55);
      transform-origin: left center; white-space: nowrap; }}
    .col .no {{ display: inline-block; width: 50px; font-size: 22px; font-weight: 400; opacity: .7; }}
    #lc-phone {{ position: absolute; left: 330px; top: 880px; width: 420px; height: 746px;
      border-radius: 54px; padding: 10px; background: rgba(255,255,255,.9);
      box-shadow: 0 30px 80px rgba(0,0,0,.45); }}
    #lc-screen {{ position: relative; width: 100%; height: 100%; border-radius: 44px; overflow: hidden;
      background: #111; }}
    .demo {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
    .count {{ position: absolute; left: 22px; top: 22px; z-index: 5; padding: 4px 12px; border-radius: 99px;
      background: rgba(0,0,0,.55); color: #fff; font-weight: 700; font-size: 20px; }}
  </style>
  <div id="root" data-composition-id="listicle" data-width="{W}" data-height="{H}">
    <div id="lc-head"><span class="num">{title_num}</span> {title_rest}<br />{title_2}</div>
    <div id="lc-board">
{chr(10).join(rows)}
    </div>
    <div id="lc-phone">
      <div id="lc-screen">
{chr(10).join(demos)}
{chr(10).join(counters)}
      </div>
    </div>
  </div>
  <script>
    (() => {{
      const ACCENT = "{accent}";
      const DIM = "rgba(255,255,255,0.55)";
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#lc-head", {{ opacity: 0, filter: "blur(8px)" }},
        {{ opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }}, 0);
      tl.fromTo("#lc-board", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.2, ease: "power2.out" }}, 0.05);
      tl.fromTo("#lc-phone", {{ opacity: 0, y: 60, scale: 0.92 }},
        {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "expo.out" }}, 0);
{chr(10).join(tweens)}
      tl.fromTo(["#lc-head", "#lc-board", "#lc-phone"], {{ opacity: 1, filter: "blur(0px)" }},
        {{ opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }}, {fmt(list_end - 0.22)});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["listicle"] = tl;
    }})();
  </script>
</template>
"""


def build_index(cfg: dict) -> str:
    dur = fmt(cfg["duration"])
    aroll = html.escape(cfg.get("aroll", "assets/aroll.mp4"))
    return f"""<!doctype html>
<html lang="vi">
  <head>
    <meta charset="UTF-8" />
    <title>{html.escape(cfg.get("name", "listicle"))}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <style>
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}"
      data-width="{W}" data-height="{H}">
      <video id="aroll" class="clip" src="{aroll}" data-start="0" data-duration="{dur}"
        data-track-index="0" data-has-audio="true" playsinline
        style="position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; z-index: 1"></video>
      <div id="listicle" class="clip" data-composition-id="listicle"
        data-composition-src="compositions/listicle.html" data-start="0"
        data-duration="{fmt(cfg["list_end"])}" data-track-index="1" data-track-kind="graphics"
        data-width="{W}" data-height="{H}" style="z-index: 2"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config")
    p.add_argument("--transcript", help="transcript.json để tự điền mốc thời gian")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    cfg = json.loads(Path(a.config).read_text())
    if a.transcript:
        fill_times(cfg["items"], Path(a.transcript))
    missing = [it["label"] for it in cfg["items"] if "at" not in it]
    if missing:
        raise SystemExit(f"thiếu 'at' cho: {', '.join(missing)} (hoặc truyền --transcript)")
    cfg["items"].sort(key=lambda it: it["at"])
    last = cfg["items"][-1]["at"]
    cfg.setdefault("list_end", round(last + cfg.get("last_hold", 0.9), 2))
    cfg.setdefault("duration", cfg["list_end"])

    out = Path(a.out)
    (out / "compositions").mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    (out / "index.html").write_text(build_index(cfg))
    (out / "compositions" / "listicle.html").write_text(build_scene(cfg))
    (out / "timing.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
    print(f"{out}/index.html  ({len(cfg['items'])} mục, danh sách 0–{cfg['list_end']}s, video {cfg['duration']}s)")
    for it in cfg["items"]:
        print(f"  {it['at']:6.2f}s  {it['label']}")


if __name__ == "__main__":
    main()
