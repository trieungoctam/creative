#!/usr/bin/env python3
"""vkit — bộ công cụ dòng lệnh cho quy trình video AI.

Lệnh con:
  new       Tạo khung thư mục một dự án video từ templates/.
  fetch     Tải video tham chiếu từ link (TikTok, Reels, Shorts...) kèm metadata.
  analyze   Bóc tách video: thông số, ảnh tổng hợp, điểm cắt cảnh, lời thoại, chỉ số nhịp.
  tile      Ghép khung hình của một đoạn thời gian (soi kỹ một hiệu ứng / chuyển cảnh).
  captions  Sinh phụ đề karaoke (.ass) + .srt từ lời thoại của video.
  finish    Hậu kỳ xuất bản: khung 9:16, chuẩn âm lượng, ghép phụ đề, nhãn AI.

Yêu cầu: ffmpeg/ffprobe; yt-dlp (fetch); faster-whisper (analyze --transcribe, captions).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PRESETS = {
    # tên: (rộng, cao, fps, mục tiêu LUFS)
    "tiktok": (1080, 1920, 30, -14),
    "reels": (1080, 1920, 30, -14),
    "shorts": (1080, 1920, 30, -14),
    "feed45": (1080, 1350, 30, -14),
    "square": (1080, 1080, 30, -14),
    "youtube": (1920, 1080, 30, -14),
}

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def die(msg: str) -> None:
    print(f"vkit: {msg}", file=sys.stderr)
    sys.exit(1)


def need(tool: str) -> None:
    if not shutil.which(tool):
        die(f"thiếu '{tool}' — cài đặt rồi chạy lại (xem README mục Cài đặt).")


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=capture)


def probe(path: Path) -> dict:
    need("ffprobe")
    out = run(["ffprobe", "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", str(path)], capture=True).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    num, _, den = v.get("r_frame_rate", "0/1").partition("/")
    return {
        "duration": float(data["format"].get("duration", 0)),
        "width": v.get("width"),
        "height": v.get("height"),
        "fps": round(float(num) / float(den or 1), 3) if num else None,
        "video_codec": v.get("codec_name"),
        "has_audio": a is not None,
        "audio_codec": a.get("codec_name") if a else None,
    }


def font_file() -> str:
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            return f
    die("không tìm thấy font đậm — truyền --font <đường dẫn .ttf/.otf>.")
    return ""


# ---------------------------------------------------------------- new
PROJECT_FILES = ["BRIEF.md", "TREATMENT.md", "STORYBOARD.md"]


def cmd_new(a: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parent.parent
    proj = root / "projects" / a.name
    if proj.exists():
        die(f"{proj} đã tồn tại.")
    for d in ["references", "prompts", "assets", "output"]:
        (proj / d).mkdir(parents=True)
    for f in PROJECT_FILES:
        shutil.copy(root / "templates" / f, proj / f)
    (proj / "PROGRESS.md").write_text(
        f"# PROGRESS · {a.name}\n\n- Đang làm: viết BRIEF\n- Còn lại: tham chiếu, TREATMENT, "
        "STORYBOARD, hero, chuyển động, dựng, QC\n- Bước tiếp theo: \n")
    print(proj)


# ---------------------------------------------------------------- fetch
def cmd_fetch(a: argparse.Namespace) -> None:
    need("yt-dlp")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cmd = ["yt-dlp", "--write-info-json", "-o", str(out / "source.%(ext)s"),
           "--merge-output-format", "mp4", a.url]
    if a.cookies_from_browser:
        cmd[1:1] = ["--cookies-from-browser", a.cookies_from_browser]
    if subprocess.run(cmd).returncode != 0:
        die("tải thất bại. Lỗi 429/đăng nhập: chờ vài phút, hoặc thêm --cookies-from-browser chrome, "
            "hoặc tải tay rồi đặt file vào " + str(out / "source.mp4"))
    info = json.loads((out / "source.info.json").read_text())
    keep = {k: info.get(k) for k in [
        "webpage_url", "uploader", "channel", "upload_date", "description",
        "like_count", "comment_count", "view_count", "duration"]}
    (out / "meta.json").write_text(json.dumps(keep, ensure_ascii=False, indent=2))
    print(json.dumps(keep, ensure_ascii=False, indent=2))
    print(f"\nĐã lưu: {out / 'source.mp4'}")


# ---------------------------------------------------------------- transcribe
def transcribe(path: Path, language: str | None, model: str) -> dict:
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        die("thiếu faster-whisper — chạy: pip install faster-whisper")
    raw = run_bytes(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                     "-ar", "16000", "-f", "f32le", "-"])
    audio = np.frombuffer(raw, np.float32)
    m = WhisperModel(model, device="auto", compute_type="int8")
    segs, info = m.transcribe(audio, language=language, word_timestamps=True,
                              vad_filter=True)
    segments, words = [], []
    for s in segs:
        segments.append({"start": round(s.start, 2), "end": round(s.end, 2),
                         "text": s.text.strip()})
        for w in s.words or []:
            words.append({"start": round(w.start, 2), "end": round(w.end, 2),
                          "word": w.word.strip()})
    return {"language": info.language, "segments": segments, "words": words}


def run_bytes(cmd: list[str]) -> bytes:
    return subprocess.run(cmd, check=True, capture_output=True).stdout


# ---------------------------------------------------------------- analyze
def scene_cuts(path: Path, threshold: float) -> list[float]:
    proc = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(path), "-vf",
         f"select='gt(scene,{threshold})',showinfo", "-an", "-f", "null", "-"],
        capture_output=True, text=True)
    return [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]


def loudness(path: Path) -> float | None:
    proc = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af",
                           "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", proc.stderr)
    return float(m[-1]) if m else None


def contact_sheet(path: Path, dst: Path, start: float, end: float, every: float,
                  cols: int, cell: int, crop: str | None = None) -> None:
    n = max(1, int((end - start) / every + 0.999))
    rows = max(1, -(-n // cols))
    vf = [f"fps=1/{every}"]
    if crop:
        vf.append(f"crop={crop}")
    vf += [f"scale={cell}:-2",
           "drawtext=fontfile='{}':text='%{{pts\\:hms}}':x=6:y=6:fontsize={}:"
           "fontcolor=white:box=1:boxcolor=black@0.6".format(font_file(), max(12, cell // 14)),
           f"tile={cols}x{rows}"]
    # setpts giữ nhãn thời gian đúng với mốc gốc của video
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(end - start),
         "-i", str(path), "-vf", f"setpts=PTS+{start}/TB," + ",".join(vf),
         "-frames:v", "1", str(dst)])


def cmd_analyze(a: argparse.Namespace) -> None:
    need("ffmpeg")
    src = Path(a.video)
    if not src.exists():
        die(f"không thấy file {src}")
    out = Path(a.out or src.with_suffix("").as_posix() + "_analysis")
    ev = out / "evidence"
    ev.mkdir(parents=True, exist_ok=True)

    info = probe(src)
    dur = info["duration"]
    print(f"• {dur:.1f}s  {info['width']}x{info['height']}  {info['fps']}fps")

    every = a.every or max(0.5, round(dur / 28, 1))
    contact_sheet(src, ev / "overview.jpg", 0, dur, every, 7, 270)
    contact_sheet(src, ev / "hook_0-3s.jpg", 0, min(3, dur), 0.25, 4, 320)
    print(f"• ảnh tổng hợp: {ev / 'overview.jpg'} (mỗi {every}s), {ev / 'hook_0-3s.jpg'}")

    cuts = scene_cuts(src, a.scene)
    shots = [0.0, *cuts, dur]
    lengths = [b - a_ for a_, b in zip(shots, shots[1:]) if b - a_ > 0.05]
    lufs = loudness(src) if info["has_audio"] else None

    summary = {"source": str(src), **info, "loudness_lufs": lufs,
               "scene_threshold": a.scene, "cuts": cuts,
               "shot_count": len(lengths),
               "avg_shot_sec": round(sum(lengths) / len(lengths), 2) if lengths else None}

    if a.transcribe and info["has_audio"]:
        print("• đang bóc lời thoại (faster-whisper)...")
        tx = transcribe(src, a.language, a.model)
        (out / "transcript.json").write_text(json.dumps(tx, ensure_ascii=False, indent=2))
        words = tx["words"]
        if words:
            speech = words[-1]["end"] - words[0]["start"]
            summary["words"] = len(words)
            summary["words_per_minute"] = round(len(words) / speech * 60) if speech else None
            summary["first_word_at"] = words[0]["start"]
            summary["hook_text_0_3s"] = " ".join(w["word"] for w in words if w["start"] < 3)
        print(f"• lời thoại: {out / 'transcript.json'}")

    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    write_analysis_stub(out, summary)
    print(json.dumps({k: summary[k] for k in summary if k not in ("cuts",)},
                     ensure_ascii=False, indent=2))
    print(f"\nXong. Mở {out / 'ANALYSIS.md'} để điền phần phân tích.")


def write_analysis_stub(out: Path, s: dict) -> None:
    template = Path(__file__).resolve().parent.parent / "templates" / "ANALYSIS.md"
    body = template.read_text() if template.exists() else "# Phân tích\n"
    facts = [
        "## Số liệu tự động (vkit analyze)",
        "",
        f"- Thời lượng: {s['duration']:.1f}s · {s['width']}x{s['height']} · {s['fps']} fps",
        f"- Số shot (ngưỡng {s['scene_threshold']}): {s['shot_count']} · "
        f"trung bình {s['avg_shot_sec']}s/shot",
        f"- Điểm cắt: {', '.join(map(str, s['cuts'])) or 'không phát hiện (thử --scene thấp hơn)'}",
        f"- Âm lượng tích hợp: {s['loudness_lufs']} LUFS (chuẩn mạng xã hội ≈ -14)",
    ]
    if "words" in s:
        facts += [f"- Lời thoại: {s['words']} từ · {s['words_per_minute']} từ/phút · "
                  f"từ đầu tiên ở {s['first_word_at']}s",
                  f"- Hook 0–3s: \"{s['hook_text_0_3s']}\""]
    facts += ["- Bằng chứng: `evidence/overview.jpg`, `evidence/hook_0-3s.jpg`", ""]
    dst = out / "ANALYSIS.md"
    if not dst.exists():
        dst.write_text("\n".join(facts) + "\n" + body)


# ---------------------------------------------------------------- tile
def cmd_tile(a: argparse.Namespace) -> None:
    need("ffmpeg")
    src = Path(a.video)
    end = a.end if a.end is not None else probe(src)["duration"]
    dst = Path(a.to or f"{src.stem}_{a.start:g}-{end:g}.jpg")
    contact_sheet(src, dst, a.start, end, a.every, a.cols, a.cell, a.crop)
    print(dst)


# ---------------------------------------------------------------- captions
def ass_time(t: float) -> str:
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def srt_time(t: float) -> str:
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def group_words(words: list[dict], max_words: int, max_chars: int, gap: float) -> list[list[dict]]:
    """Gom từ thành cụm đọc được: ngắt khi đủ từ/ký tự, khi ngừng nói, hoặc sau dấu câu."""
    cues, cur = [], []
    for w in words:
        text_len = len(" ".join(x["word"] for x in cur + [w]))
        paused = cur and w["start"] - cur[-1]["end"] > gap
        if cur and (len(cur) >= max_words or text_len > max_chars or paused):
            cues.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?,;:…]$", w["word"]):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return cues


def ass_color(hex_rgb: str) -> str:
    h = hex_rgb.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def cmd_captions(a: argparse.Namespace) -> None:
    src = Path(a.video)
    tx_path = Path(a.transcript) if a.transcript else None
    if tx_path and tx_path.exists():
        tx = json.loads(tx_path.read_text())
    else:
        need("ffmpeg")
        print("• đang bóc lời thoại...")
        tx = transcribe(src, a.language, a.model)
    words = [w for w in tx["words"] if w["word"]]
    if not words:
        die("không có từ nào trong lời thoại.")
    if a.upper:
        words = [{**w, "word": w["word"].upper()} for w in words]

    info = probe(src)
    W, H = info["width"] or 1080, info["height"] or 1920
    cues = group_words(words, a.max_words, a.max_chars, a.gap)
    fs = a.size or round(H * 0.045)
    margin_v = round(H * a.position)
    base, hi = ass_color(a.color), ass_color(a.highlight)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{a.font_name},{fs},{base},{base},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(2, fs // 12)},2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events, srt = [], []
    for i, cue in enumerate(cues, 1):
        start, end = cue[0]["start"], cue[-1]["end"]
        nxt = cues[i][0]["start"] if i < len(cues) else end + 0.3
        end = min(max(end, start + 0.35), nxt)
        if a.mode == "karaoke":
            # Mỗi từ là một Dialogue riêng: cả cụm hiện, từ đang nói đổi màu + phóng nhẹ.
            for j, w in enumerate(cue):
                w_end = cue[j + 1]["start"] if j + 1 < len(cue) else end
                parts = []
                for k, x in enumerate(cue):
                    if k == j:
                        parts.append(f"{{\\c{hi}\\fscx108\\fscy108}}{x['word']}{{\\r}}")
                    else:
                        parts.append(x["word"])
                events.append(f"Dialogue: 0,{ass_time(w['start'])},{ass_time(w_end)},Cap,,0,0,0,,"
                              + " ".join(parts))
        else:
            pop = "{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}"
            events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,"
                          + pop + " ".join(x["word"] for x in cue))
        srt.append(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n"
                   + " ".join(x["word"] for x in cue) + "\n")

    stem = Path(a.out) if a.out else src.with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{stem}.ass").write_text(header + "\n".join(events) + "\n")
    Path(f"{stem}.srt").write_text("\n".join(srt))
    print(f"{stem}.ass\n{stem}.srt  ({len(cues)} cụm)")


# ---------------------------------------------------------------- finish
def esc_filter_path(p: Path) -> str:
    return str(p.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def cmd_finish(a: argparse.Namespace) -> None:
    need("ffmpeg")
    src = Path(a.video)
    W, H, fps, lufs = PRESETS[a.preset]
    info = probe(src)
    dst = Path(a.out or f"{src.with_suffix('').as_posix()}_{a.preset}.mp4")

    if a.fit == "crop":
        vf = [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}"]
    else:
        vf = [f"scale={W}:{H}:force_original_aspect_ratio=decrease",
              f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black"]
    vf += [f"fps={fps}", "setsar=1"]
    if a.subs:
        vf.append(f"subtitles='{esc_filter_path(Path(a.subs))}'")
    if a.label:
        txt = a.label.replace(":", "\\:").replace("'", "\u2019")
        vf.append(f"drawtext=fontfile='{a.font or font_file()}':text='{txt}':"
                  f"x=w-tw-36:y=h*0.06:fontsize={round(H * 0.018)}:fontcolor=white@0.9:"
                  f"box=1:boxcolor=black@0.45:boxborderw=12")

    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", ",".join(vf),
           "-c:v", "libx264", "-preset", "slow", "-crf", str(a.crf), "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    if info["has_audio"]:
        cmd += ["-af", f"loudnorm=I={lufs}:TP=-1.0:LRA=11", "-c:a", "aac", "-b:a", "192k",
                "-ar", "48000"]
    run(cmd + [str(dst)])
    out = probe(dst)
    print(f"{dst}  {out['width']}x{out['height']} {out['fps']}fps {out['duration']:.1f}s"
          + (f"  {loudness(dst)} LUFS" if out["has_audio"] else ""))


# ---------------------------------------------------------------- main
def main() -> None:
    p = argparse.ArgumentParser(prog="vkit", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="tạo dự án mới trong projects/")
    n.add_argument("name")
    n.set_defaults(fn=cmd_new)

    f = sub.add_parser("fetch", help="tải video tham chiếu")
    f.add_argument("url")
    f.add_argument("--out", default="references/new")
    f.add_argument("--cookies-from-browser", help="chrome/firefox/safari — dùng khi nền tảng đòi đăng nhập")
    f.set_defaults(fn=cmd_fetch)

    an = sub.add_parser("analyze", help="bóc tách video tham chiếu")
    an.add_argument("video")
    an.add_argument("--out")
    an.add_argument("--every", type=float, help="giây giữa 2 khung trong ảnh tổng hợp")
    an.add_argument("--scene", type=float, default=0.3, help="ngưỡng phát hiện cắt cảnh 0–1")
    an.add_argument("--no-transcribe", dest="transcribe", action="store_false")
    an.add_argument("--language", help="mã ngôn ngữ: vi, en, zh... (bỏ trống = tự nhận)")
    an.add_argument("--model", default="small", help="model whisper: tiny/base/small/medium/large-v3")
    an.set_defaults(fn=cmd_analyze)

    t = sub.add_parser("tile", help="ghép khung hình một đoạn")
    t.add_argument("video")
    t.add_argument("--start", type=float, default=0)
    t.add_argument("--end", type=float)
    t.add_argument("--every", type=float, default=0.25)
    t.add_argument("--cols", type=int, default=6)
    t.add_argument("--cell", type=int, default=320)
    t.add_argument("--crop", help="vùng cắt ffmpeg w:h:x:y, ví dụ 520:900:280:700")
    t.add_argument("--to")
    t.set_defaults(fn=cmd_tile)

    c = sub.add_parser("captions", help="sinh phụ đề karaoke .ass + .srt")
    c.add_argument("video")
    c.add_argument("--transcript", help="transcript.json từ analyze (bỏ qua bước bóc lời)")
    c.add_argument("--out", help="đường dẫn không kèm đuôi")
    c.add_argument("--mode", choices=["karaoke", "pop"], default="karaoke")
    c.add_argument("--max-words", type=int, default=4)
    c.add_argument("--max-chars", type=int, default=22)
    c.add_argument("--gap", type=float, default=0.45, help="khoảng lặng (s) thì ngắt cụm")
    c.add_argument("--position", type=float, default=0.28, help="khoảng cách từ đáy, tỉ lệ chiều cao")
    c.add_argument("--size", type=int)
    c.add_argument("--color", default="#FFFFFF")
    c.add_argument("--highlight", default="#FFE14D")
    c.add_argument("--font-name", default="Inter ExtraBold")
    c.add_argument("--upper", action="store_true", help="viết hoa toàn bộ")
    c.add_argument("--language")
    c.add_argument("--model", default="small")
    c.set_defaults(fn=cmd_captions)

    fi = sub.add_parser("finish", help="xuất bản: khung hình, âm lượng, phụ đề, nhãn AI")
    fi.add_argument("video")
    fi.add_argument("--preset", choices=PRESETS, default="tiktok")
    fi.add_argument("--fit", choices=["crop", "pad"], default="crop")
    fi.add_argument("--subs", help="file .ass/.srt để ghép cứng")
    fi.add_argument("--label", help='nhãn hiển thị, ví dụ "Nội dung tạo bởi AI"')
    fi.add_argument("--font")
    fi.add_argument("--crf", type=int, default=18)
    fi.add_argument("--out")
    fi.set_defaults(fn=cmd_finish)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
