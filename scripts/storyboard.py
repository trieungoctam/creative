#!/usr/bin/env python3
"""storyboard — từ production.toml ra storyboard, animatic và timeline cho mọi tool edit.

  storyboard.py board    <production.toml>              → storyboard.html (mở bằng trình duyệt, in PDF được)
  storyboard.py animatic <production.toml> [--out f]    → output/animatic.mp4: dựng thô theo đúng mốc kịch bản;
                                                           shot chưa có asset hiện thành khung giữ chỗ
  storyboard.py export   <production.toml> --to xml|json|csv|srt|hf [--out f]
        xml  FCP7 XML (xmeml) — Premiere Pro, DaVinci Resolve, Final Cut Pro 7 nhập được
        json timeline trung lập — cho Remotion / script riêng
        csv  danh sách marker (Selection, Moment, Segment, shot)
        srt  phụ đề theo cụm || của kịch bản — CapCut, Premiere, Resolve, YouTube
        hf   project HyperFrames (index.html: A-roll + B-roll + overlay đúng mốc)

Mốc thời gian lấy từ <script>.timing.json (sau `vscript align`) hoặc ước lượng theo tốc độ nói.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from production import FRAMES, VIDEO_EXT, Production  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent


def rel(prod: Production, p: Path | None) -> str:
    return str(p.relative_to(prod.root)) if p else ""


def shot_media(prod: Production, shot: dict, use_candidates: bool = True) -> Path | None:
    p = prod.asset(shot)
    if not p and use_candidates:
        c = prod.candidates(shot)
        p = c[0] if c else None
    return p


def placed_shots(prod: Production) -> list[dict]:
    out = []
    for s in prod.shots:
        w = prod.window(s.get("during"))
        if w and s.get("layer") in ("broll", "overlay"):
            out.append({**s, "start": w[0], "end": w[1], "media": shot_media(prod, s)})
    return sorted(out, key=lambda s: s["start"])


# ---------------------------------------------------------------- board
CSS = """
:root{--bg:#f6f4ef;--fg:#1d1d1f;--mut:#6b6b70;--card:#fff;--line:#e4e0d8;--acc:ACCENT}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececee;--mut:#9a9aa2;--card:#1f1f23;--line:#2d2d33}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 Inter,system-ui,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 80px}h1{margin:0 0 4px;font-size:26px}
.meta{color:var(--mut);margin-bottom:18px}.warn{background:#fff3c4;color:#5a4300;padding:8px 12px;border-radius:8px;margin:10px 0}
section{margin-top:28px}h2{font-size:18px;margin:0 0 8px;display:flex;gap:10px;align-items:baseline}h2 small{color:var(--mut);font-weight:400}
.script{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;font-size:17px;line-height:2}
.w{border-radius:4px;padding:1px 0}.sel{background:color-mix(in srgb,var(--acc) 30%,transparent);box-shadow:inset 0 -2px var(--acc)}
.cue{color:var(--line);padding:0 4px}.tag{font-size:11px;background:var(--acc);color:#111;border-radius:4px;padding:0 5px;margin:0 2px;vertical-align:2px}
.mom{color:#e0443e;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin-top:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.thumb{aspect-ratio:9/16;background:repeating-linear-gradient(45deg,var(--line) 0 10px,transparent 10px 20px);display:flex;align-items:center;justify-content:center;color:var(--mut);position:relative}
.thumb img,.thumb video{width:100%;height:100%;object-fit:cover}.thumb .badge{position:absolute;left:8px;top:8px;background:#000a;color:#fff;font-size:12px;border-radius:99px;padding:2px 8px}
.body{padding:10px 12px}.id{font-weight:700}.small{color:var(--mut);font-size:13px}
details{margin-top:6px}summary{cursor:pointer;color:var(--mut);font-size:13px}pre{white-space:pre-wrap;font-size:12px;margin:6px 0 0}
.cands{display:flex;gap:4px;margin-top:6px;overflow-x:auto}.cands img,.cands video{height:56px;border-radius:4px}
"""


def word_html(prod: Production, seg: str) -> str:
    tm = prod.timing
    sels = tm["selections"]
    moms = sorted(tm["moments"].items(), key=lambda kv: kv[1])
    cue_starts = {c["units"][0] for c in tm["cues"]}
    out, opened = [], set()
    for i, w in enumerate(tm["words"]):
        if w["segment"] != seg or not w["display"]:
            continue
        if i in cue_starts and out:
            out.append('<span class="cue">||</span>')
        for name, t in moms:
            if abs(t - (w["start"] or -1)) < 1e-3:
                out.append(f'<span class="mom" title="Moment">◆{html.escape(name)}</span> ')
        inside = [n for n, s in sels.items() if s["start"] - 1e-3 <= (w["start"] or -1) < s["end"] - 1e-3]
        for n in inside:
            if n not in opened:
                out.append(f'<span class="tag">{html.escape(n)}</span>')
                opened.add(n)
        cls = "w sel" if inside else "w"
        title = f'{w["start"]:.2f}–{w["end"]:.2f}s' + (f' · đọc: {w["spoken"]}' if w["spoken"] != w["display"] else "")
        out.append(f'<span class="{cls}" title="{html.escape(title)}">{html.escape(w["display"])}</span> ')
    return "".join(out)


def media_tag(prod: Production, p: Path | None, cls: str = "") -> str:
    if not p:
        return ""
    src = quote(rel(prod, p))
    if p.suffix.lower() in VIDEO_EXT:
        return f'<video class="{cls}" src="{src}" muted loop playsinline preload="metadata"></video>'
    return f'<img class="{cls}" src="{src}" alt="">'


def cmd_board(a) -> None:
    prod = Production(a.production)
    tm = prod.timing
    parts = [f"<!doctype html><html lang='vi'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>Storyboard · {html.escape(prod.name)}</title><style>{CSS.replace('ACCENT', prod.accent)}</style></head><body><main>",
             f"<h1>{html.escape(prod.name)}</h1><div class='meta'>{prod.W}×{prod.H} · {prod.fps}fps · "
             f"{tm['duration']:.1f}s · {len(prod.shots)} shot · kịch bản <code>{html.escape(prod.script_path.name)}</code></div>"]
    if prod.timing_source == "estimate":
        parts.append("<div class='warn'>Mốc thời gian đang là <b>ước lượng</b> theo tốc độ nói. Sau khi có A-roll, chạy "
                     "<code>vscript.py align</code> để storyboard bám mốc thật.</div>")
    by_seg = {s: [] for s in tm["segments"]}
    unplaced = []
    for s in prod.shots:
        d = s.get("during")
        w = prod.window(d) if d else None
        seg = None
        if w:
            seg = next((x["name"] for x in segment_plan(prod)
                        if x["start"] - 1e-3 <= w[0] < x["start"] + x["dur"] - 1e-3), None)
        (by_seg[seg] if seg else unplaced).append((s, w))
    for seg, win in tm["segments"].items():
        parts.append(f"<section><h2>{html.escape(seg)} <small>{win['start']:.2f}–{win['end']:.2f}s</small></h2>"
                     f"<div class='script'>{word_html(prod, seg)}</div><div class='grid'>")
        for s, w in sorted(by_seg[seg], key=lambda x: x[1][0]):
            parts.append(card_html(prod, s, w))
        parts.append("</div></section>")
    if unplaced:
        parts.append("<section><h2>Tài sản tham chiếu <small>không gắn thời gian</small></h2><div class='grid'>")
        parts += [card_html(prod, s, w) for s, w in unplaced]
        parts.append("</div></section>")
    parts.append("</main></body></html>")
    dst = Path(a.out) if a.out else prod.root / "storyboard.html"
    dst.write_text("\n".join(parts))
    print(dst)


def card_html(prod: Production, s: dict, w) -> str:
    media = shot_media(prod, s, use_candidates=False)
    cands = prod.candidates(s)
    thumb = media_tag(prod, media) or media_tag(prod, cands[0] if cands else None) or "chưa có hình"
    when = f"{w[0]:.2f}–{w[1]:.2f}s" if w else "—"
    status = "✓ đã chốt" if media else (f"{len(cands)} ứng viên" if cands else "cần tạo")
    excerpt = prod.script_excerpt(s.get("during")) if w else ""
    strip = "".join(media_tag(prod, c) for c in cands[:8])
    return (f"<div class='card'><div class='thumb'>{thumb}<span class='badge'>{html.escape(s.get('layer', ''))} · {when}</span></div>"
            f"<div class='body'><div class='id'>{html.escape(s['id'])}</div>"
            f"<div class='small'>{html.escape(' · '.join(x for x in (s.get('model'), s.get('kind'), s.get('frame'), status) if x))}</div>"
            + (f"<div class='small'>“{html.escape(excerpt)}”</div>" if excerpt else "")
            + (f"<div class='cands'>{strip}</div>" if strip else "")
            + f"<details><summary>prompt</summary><pre>{html.escape(s.get('prompt', '').strip())}</pre></details></div></div>")


# ---------------------------------------------------------------- animatic
def ff(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def segment_plan(prod: Production) -> list[dict]:
    tm = prod.timing
    segs = list(tm["segments"].items())
    plan = []
    for i, (name, w) in enumerate(segs):
        end = segs[i + 1][1]["start"] if i + 1 < len(segs) else tm["duration"]
        plan.append({"name": name, "start": w["start"], "dur": max(0.1, end - w["start"])})
    return plan


def aroll_still(prod: Production, seg: str) -> Path | None:
    for s in prod.shots:
        if s.get("layer") == "aroll" and s.get("during") == f"segment:{seg}":
            if s.get("image", "").startswith("shot:"):
                p = prod.asset(prod.shot(s["image"][5:]))
                if p:
                    return p
            p = shot_media(prod, s)
            if p:
                return p
    hero = next((s for s in prod.shots if s.get("layer") == "ref"), None)
    return prod.asset(hero) if hero else None


def cmd_animatic(a) -> None:
    from vkit import font_file
    prod = Production(a.production)
    W, H, fps = prod.W, prod.H, prod.fps
    font = font_file()
    tmp = Path(tempfile.mkdtemp(prefix="animatic-"))
    seg_files = []
    whole = prod.takes.get("all")
    plan = [{"name": "all", "start": 0.0, "dur": prod.timing["duration"]}] if whole else segment_plan(prod)
    for i, seg in enumerate(plan):
        out = tmp / f"seg{i:02d}.mp4"
        take = prod.takes.get(seg["name"])
        label = f"drawtext=fontfile='{font}':text='{seg['name']}':x=24:y=24:fontsize=28:fontcolor=white@0.8:box=1:boxcolor=black@0.4:boxborderw=8"
        norm = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},setsar=1"
        if take and take.exists():
            audio = "[0:a]aresample=48000,apad[a]" if has_audio(take) else "[1:a]acopy[a]"
            ff(["-i", str(take), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", f"[0:v]{norm},tpad=stop=-1:stop_mode=clone[v];{audio}",
                "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-t", f"{seg['dur']:.3f}", str(out)])
        else:
            still = aroll_still(prod, seg["name"])
            vo = vo_file(prod, seg["name"])
            src = ["-loop", "1", "-i", str(still)] if still else ["-f", "lavfi", "-i", f"color=c=0x1d1d22:s={W}x{H}:r={fps}"]
            vf = (f"{norm}," if still else "") + label + (",eq=brightness=-0.05" if still else "")
            aud = ["-i", str(vo)] if vo else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
            ff([*src, *aud, "-t", f"{seg['dur']:.3f}", "-vf", vf, "-af", "aresample=48000,apad",
                "-map", "0:v", "-map", "1:a", "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", "-t", f"{seg['dur']:.3f}", str(out)])
        seg_files.append(out)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in seg_files))
    base = tmp / "base.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(base)])

    # lớp B-roll / overlay + phụ đề
    timing_file = tmp / "timing.json"
    timing_file.write_text(json.dumps(prod.timing, ensure_ascii=False))
    subprocess.run([sys.executable, "-I", str(SCRIPTS / "vscript.py"), "captions", str(timing_file), "--out",
                    str(tmp / "caps"), "--width", str(W), "--height", str(H), "--highlight", prod.accent,
                    "--keyword", prod.accent], check=True, capture_output=True)
    inputs, chains, last, n_in = ["-i", str(base)], [], "[0:v]", 1
    for k, s in enumerate(placed_shots(prod)):
        l, t, r, b = FRAMES.get(s.get("frame", "full" if s["layer"] == "broll" else "center"), FRAMES["center"])
        x, y, bw, bh = int(l * W), int(t * H), int((r - l) * W), int((b - t) * H)
        en = f"enable='between(t,{s['start']:.3f},{s['end']:.3f})'"
        if s["media"]:
            idx, n_in = n_in, n_in + 1
            if s["media"].suffix.lower() in VIDEO_EXT:
                inputs += ["-itsoffset", f"{s['start']:.3f}", "-i", str(s["media"])]
            else:
                inputs += ["-loop", "1", "-t", f"{prod.timing['duration']:.3f}", "-i", str(s["media"])]
            fit = (f"scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh}" if s["layer"] == "broll"
                   else f"scale={bw}:{bh}:force_original_aspect_ratio=decrease")
            chains.append(f"[{idx}:v]{fit},format=yuva420p[o{k}]")
            ox = f"{x}+({bw}-overlay_w)/2"
            chains.append(f"{last}[o{k}]overlay=x={ox}:y={y}:{en}[v{k}]")
        else:
            txt = s["id"].replace(":", " ")
            chains.append(f"{last}drawbox=x={x}:y={y}:w={bw}:h={bh}:color={prod.accent}@0.35:t=fill:{en},"
                          f"drawbox=x={x}:y={y}:w={bw}:h={bh}:color={prod.accent}:t=6:{en},"
                          f"drawtext=fontfile='{font}':text='{txt}':x={x}+24:y={y}+24:fontsize=40:fontcolor=white:"
                          f"box=1:boxcolor=black@0.5:boxborderw=10:{en}[v{k}]")
        last = f"[v{k}]"
    ass = str(tmp / "caps.ass").replace(":", "\\:")
    chains.append(f"{last}subtitles='{ass}'[vout]")
    # âm thanh: giọng (A-roll / VO) + nhạc nền tự duck + SFX tại đúng mốc
    D = prod.timing["duration"]
    mix, labels = [], ["[voice]"]
    mus = music_track(prod)
    sfx = sfx_events(prod)
    if mus or sfx:
        mix.append("[0:a]asplit=2[voice][sc]" if mus else "[0:a]anull[voice]")
    if mus:
        inputs += ["-stream_loop", "-1", "-i", str(mus["file"])]
        mi, n_in = n_in, n_in + 1
        mix.append(f"[{mi}:a]atrim=0:{D:.3f},afade=t=out:st={max(0, D - 0.8):.3f}:d=0.8,volume={mus['gain']}[mus]")
        mix.append("[mus][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[duck]")
        labels.append("[duck]")
    for j, ev in enumerate(sfx):
        inputs += ["-i", str(ev["file"])]
        si, n_in = n_in, n_in + 1
        ms = int(ev["t"] * 1000)
        mix.append(f"[{si}:a]adelay={ms}:all=1,volume={ev['gain']}[s{j}]")
        labels.append(f"[s{j}]")
    if mix:
        mix.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0[aout]")
        chains += mix
    amap = "[aout]" if mix else "0:a"
    dst = Path(a.out) if a.out else prod.root / "output" / "animatic.mp4"
    dst.parent.mkdir(parents=True, exist_ok=True)
    ff([*inputs, "-filter_complex", ";".join(chains), "-map", "[vout]", "-map", amap, "-t", f"{prod.timing['duration']:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", str(dst)])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"{dst}  ({prod.timing['duration']:.1f}s, mốc: {prod.timing_source})")


def vo_file(prod: Production, seg: str) -> Path | None:
    p = prod.root / prod.cfg.get("audio", {}).get("vo_dir", "assets/vo") / f"{seg}.mp3"
    return p if p.exists() else None


def music_track(prod: Production) -> dict | None:
    m = prod.cfg.get("music")
    if not m or not m.get("file") or not (prod.root / m["file"]).exists():
        return None
    return {"file": prod.root / m["file"], "gain": m.get("gain", 0.18)}


def sfx_events(prod: Production, include_missing: bool = False) -> list[dict]:
    out = []
    for s in prod.cfg.get("sfx", []):
        f = prod.root / s.get("file", f"assets/sfx/{s['id']}.mp3")
        at = s.get("at")
        if not at:
            continue
        t = float(at) if isinstance(at, (int, float)) else prod.window(at)[0]
        out.append({"id": s["id"], "t": t + float(s.get("offset", 0)), "file": f, "exists": f.exists(),
                    "gain": s.get("gain", 0.6)})
    return out if include_missing else [e for e in out if e["exists"]]


def has_audio(p: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return bool(out.strip())


# ---------------------------------------------------------------- export
def timeline(prod: Production) -> dict:
    tm = prod.timing
    aroll = []
    whole = prod.takes.get("all")
    for seg in ([{"name": "all", "start": 0.0, "dur": tm["duration"]}] if whole else segment_plan(prod)):
        take = prod.takes.get(seg["name"])
        aroll.append({"segment": seg["name"], "start": seg["start"], "end": seg["start"] + seg["dur"],
                      "file": rel(prod, take) if take and take.exists() else None})
    tracks = {"aroll": aroll, "broll": [], "overlay": []}
    for s in placed_shots(prod):
        tracks[s["layer"]].append({"id": s["id"], "start": s["start"], "end": s["end"], "file": rel(prod, s["media"]),
                                   "frame": s.get("frame", "full"), "box": FRAMES.get(s.get("frame", "full")),
                                   "motion": s.get("motion", "none")})
    for seg in tracks["aroll"]:
        vo = vo_file(prod, seg["segment"])
        if not seg["file"] and vo:
            seg["audio"] = rel(prod, vo)
    mus = music_track(prod)
    tracks["music"] = [{"id": "music", "start": 0.0, "end": tm["duration"], "file": rel(prod, mus["file"]),
                        "gain": mus["gain"]}] if mus else []
    tracks["sfx"] = [{"id": e["id"], "start": e["t"], "end": e["t"] + 1.0, "file": rel(prod, e["file"]) if e["exists"] else None,
                      "gain": e["gain"]} for e in sfx_events(prod, include_missing=True)]
    markers = ([{"name": n, "kind": "selection", **v} for n, v in tm["selections"].items()]
               + [{"name": n, "kind": "moment", "start": t, "end": t} for n, t in tm["moments"].items()]
               + [{"name": n, "kind": "segment", **v} for n, v in tm["segments"].items()])
    return {"name": prod.name, "width": prod.W, "height": prod.H, "fps": prod.fps, "duration": tm["duration"],
            "timing_source": prod.timing_source, "tracks": tracks, "markers": sorted(markers, key=lambda m: m["start"]),
            "captions": [{"start": c["start"], "end": c["end"], "text": c["text"]} for c in tm["cues"]]}


def to_xml(prod: Production, tl: dict) -> str:
    fps = tl["fps"]
    f = lambda t: int(round(t * fps))  # noqa: E731
    rate = f"<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>"
    files: dict[str, str] = {}

    def file_el(path: str) -> str:
        if path in files:
            return f'<file id="{files[path]}"/>'
        fid = files[path] = f"file-{len(files) + 1}"
        abs_p = (prod.root / path).resolve()
        return (f'<file id="{fid}"><name>{html.escape(abs_p.name)}</name>'
                f"<pathurl>file://localhost{quote(str(abs_p))}</pathurl>{rate}"
                f"<media><video><samplecharacteristics><width>{tl['width']}</width><height>{tl['height']}</height>"
                f"</samplecharacteristics></video><audio/></media></file>")

    def clip(cid: str, name: str, path: str, s: float, e: float, src_in: float = 0.0) -> str:
        n = f(e) - f(s)
        return (f'<clipitem id="{cid}"><name>{html.escape(name)}</name><enabled>TRUE</enabled><duration>{n}</duration>{rate}'
                f"<start>{f(s)}</start><end>{f(e)}</end><in>{f(src_in)}</in><out>{f(src_in) + n}</out>{file_el(path)}</clipitem>")

    v_tracks = []
    for key in ("aroll", "broll", "overlay"):
        items = [clip(f"{key}-{i}", c.get("id") or c.get("segment"), c["file"], c["start"], c["end"])
                 for i, c in enumerate(tl["tracks"][key]) if c.get("file")]
        v_tracks.append("<track>" + "".join(items) + "</track>")
    def aclip(cid: str, name: str, path: str, s: float, e: float) -> str:
        return clip(cid, name, path, s, e).replace(
            "</clipitem>", "<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>")

    a_tracks = []
    voice = [aclip(f"a-{i}", c["segment"], c.get("file") or c.get("audio"), c["start"], c["end"])
             for i, c in enumerate(tl["tracks"]["aroll"]) if c.get("file") or c.get("audio")]
    a_tracks.append("<track>" + "".join(voice) + "</track>")
    for key in ("music", "sfx"):
        items = [aclip(f"{key}-{i}", c["id"], c["file"], c["start"], c["end"]) for i, c in enumerate(tl["tracks"][key]) if c.get("file")]
        if items:
            a_tracks.append("<track>" + "".join(items) + "</track>")
    markers = "".join(f"<marker><name>{html.escape(m['kind'] + ': ' + m['name'])}</name><comment></comment>"
                      f"<in>{f(m['start'])}</in><out>{f(m['end']) if m['end'] > m['start'] else -1}</out></marker>"
                      for m in tl["markers"])
    fmt = (f"<format><samplecharacteristics>{rate}<width>{tl['width']}</width><height>{tl['height']}</height>"
           f"<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4">'
            f'<sequence id="seq-1"><name>{html.escape(tl["name"])}</name><duration>{f(tl["duration"])}</duration>{rate}'
            f"<media><video>{fmt}{''.join(v_tracks)}</video><audio>{''.join(a_tracks)}</audio></media>"
            f"{markers}</sequence></xmeml>\n")


def to_hf(prod: Production, tl: dict, out: Path) -> None:
    W, H, D = tl["width"], tl["height"], tl["duration"]
    els, tweens, z = [], [], 1
    (out / "assets").mkdir(parents=True, exist_ok=True)

    def local(path: str) -> str:
        # HyperFrames chỉ đọc media trong assets/ của project (không có ../)
        src = prod.root / path
        dst = out / "assets" / src.name
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            shutil.copy(src, dst)
        return f"assets/{src.name}"

    for i, c in enumerate(tl["tracks"]["aroll"]):
        if c["file"]:
            els.append(f'<video id="aroll-{i}" class="clip" src="{html.escape(local(c["file"]))}" data-start="{c["start"]:.3f}" '
                       f'data-duration="{c["end"] - c["start"]:.3f}" data-track-index="0" data-has-audio="true" playsinline '
                       f'style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;object-fit:cover;z-index:{z}"></video>')
    for key, track in (("broll", 1), ("overlay", 2)):
        for c in tl["tracks"][key]:
            if not c["file"]:
                continue
            z += 1
            l, t, r, b = c["box"]
            box = f"left:{l * W:.0f}px;top:{t * H:.0f}px;width:{(r - l) * W:.0f}px;height:{(b - t) * H:.0f}px"
            fit = "cover" if key == "broll" else "contain"
            style = f'width:100%;height:100%;object-fit:{fit};border-radius:{0 if key == "broll" else 24}px'
            src = html.escape(local(c["file"]))
            media = (f'<video id="{c["id"]}-m" src="{src}" muted playsinline style="{style}"></video>'
                     if Path(c["file"]).suffix.lower() in VIDEO_EXT else
                     f'<img id="{c["id"]}-m" src="{src}" alt="" style="{style}"/>')
            els.append(f'<div id="{c["id"]}" class="clip" data-start="{c["start"]:.3f}" data-duration="{c["end"] - c["start"]:.3f}" '
                       f'data-track-index="{track}" style="position:absolute;{box};z-index:{z}">{media}</div>')
            if c["motion"] == "pop":
                tweens.append(f'tl.fromTo("#{c["id"]}-m",{{scale:0.7,opacity:0}},{{scale:1,opacity:1,duration:0.2,ease:"expo.out"}},{c["start"]:.3f});')
            elif c["motion"] == "kenburns":
                tweens.append(f'tl.fromTo("#{c["id"]}-m",{{scale:1}},{{scale:1.08,duration:{c["end"] - c["start"]:.3f},ease:"none"}},{c["start"]:.3f});')
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(f"""<!doctype html>
<html lang="vi"><head><meta charset="UTF-8"/><title>{html.escape(tl['name'])}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<style>html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:#000}}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="{W}" data-height="{H}">
{chr(10).join(els)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tweens)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
</script></body></html>
""")
    print(f"{out / 'index.html'}  — media đã chép vào {out / 'assets'}. Tiếp: npx hyperframes check --json → preview."
          " Phụ đề: skill /hyperframes (captions) hoặc ghép file .srt khi xuất.")


def cmd_export(a) -> None:
    prod = Production(a.production)
    tl = timeline(prod)
    stem = prod.root / "output" / prod.name
    stem.parent.mkdir(parents=True, exist_ok=True)
    if a.to == "json":
        dst = Path(a.out or f"{stem}.timeline.json")
        dst.write_text(json.dumps(tl, ensure_ascii=False, indent=2))
    elif a.to == "csv":
        dst = Path(a.out or f"{stem}.markers.csv")
        rows = ["kind,name,start,end"] + [f"{m['kind']},{m['name']},{m['start']:.3f},{m['end']:.3f}" for m in tl["markers"]]
        rows += [f"shot-{k},{c['id']},{c['start']:.3f},{c['end']:.3f}" for k in ("broll", "overlay") for c in tl["tracks"][k]]
        rows += [f"sfx,{c['id']},{c['start']:.3f},{c['start']:.3f}" for c in tl["tracks"]["sfx"]]
        dst.write_text("\n".join(rows) + "\n")
    elif a.to == "xml":
        dst = Path(a.out or f"{stem}.xml")
        dst.write_text(to_xml(prod, tl))
        missing = [c.get("id") or c.get("segment") for k in tl["tracks"] for c in tl["tracks"][k] if not c.get("file")]
        if missing:
            print(f"  (bỏ qua {len(missing)} clip chưa có file: {', '.join(missing)} — marker vẫn có đủ)")
    elif a.to == "srt":
        from vkit import srt_time
        dst = Path(a.out or f"{stem}.srt")
        dst.write_text("\n".join(f"{i + 1}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n"
                                 for i, c in enumerate(tl["captions"])))
    else:
        to_hf(prod, tl, Path(a.out) if a.out else prod.root / "output" / "hyperframes")
        return
    print(dst)


def main() -> None:
    p = argparse.ArgumentParser(prog="storyboard", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("board", cmd_board), ("animatic", cmd_animatic)):
        c = sub.add_parser(name)
        c.add_argument("production")
        c.add_argument("--out")
        c.set_defaults(fn=fn)
    e = sub.add_parser("export")
    e.add_argument("production")
    e.add_argument("--to", choices=["xml", "json", "csv", "srt", "hf"], required=True)
    e.add_argument("--out")
    e.set_defaults(fn=cmd_export)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
