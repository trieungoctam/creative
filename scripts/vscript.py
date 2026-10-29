#!/usr/bin/env python3
"""vscript — kịch bản neo theo từ (phiên bản gọn của Script trong hypit).

Kịch bản là nguồn sự thật duy nhất. Hình ảnh, B-roll, phụ đề và hiệu ứng gắn vào *từ* chứ không
gắn vào giây; khi lời hoặc nhịp diễn đổi, mọi thứ tự chạy theo sau bước căn chỉnh lại.

Cú pháp (xem docs/13-kich-ban-neo-theo-tu.md):
  <hook> ... </hook>          Segment: một đoạn diễn có tên (a-z, 0-9, -, _)
  <pause/>                    Segment không lời
  <HOST>                      Vai nói (bên trong Segment)
  <TikTok|tíc tóc>            Dual Text: hiển thị | đọc;  <New York|> = gom nguyên cụm;  <|chỉ đọc>
  ||                          Ngắt cụm phụ đề
  chữ{emphasis}               Thuộc tính cho từ hiển thị ngay trước (không có dấu cách)
  @{proof} ... @{/proof}      Selection: một khoảng nghĩa có tên
  @{reveal!}                  Moment: một điểm nghĩa
  @{~x} @{/x~} @{~x!}         Biến thể ranh giới: ~ trước = cuối từ trước, ~ sau = đầu từ sau
  <!-- ghi chú -->            Bình luận

Lệnh:
  check     <file.vs>                      Phân tích và báo cấu trúc
  dialogue  <file.vs> [--segment id]       Thoại có vai (dán vào prompt video)
  speech    <file.vs> [--segment id]       Chỉ chữ đọc (cho TTS)
  estimate  <file.vs> [--lang vi|en] [--rate N]   Ước lượng thời lượng từng Segment
  align     <file.vs> --media seg=video.mp4 ... | --media all=video.mp4 | --transcript t.json  → timing.json
  captions  <timing.json> [--out stem]     Phụ đề theo cụm || đã viết (.ass karaoke + .srt)
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

NAME = r"[a-z][a-z0-9_-]{0,63}"


@dataclass
class Unit:
    display: str                # chữ hiển thị (có thể rỗng)
    spoken: list[str]           # các token đọc
    segment: str
    role: str | None
    attrs: dict = field(default_factory=dict)
    cue_break: bool = False     # bắt đầu một cụm phụ đề mới
    sep_before: bool = True     # có dấu cách trước khi hiển thị
    start: float | None = None
    end: float | None = None


@dataclass
class Marker:
    name: str
    kind: str                   # open | close | moment
    side: str                   # next | prev
    pos: int                    # số unit đứng trước marker
    segment: str | None


@dataclass
class Script:
    units: list[Unit]
    markers: list[Marker]
    segments: list[str]
    seg_ranges: dict             # id -> [i0, i1) theo unit


# ---------------------------------------------------------------- parse
def parse(text: str) -> Script:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    m = re.search(r"<script[^>]*>(.*)</script>", text, flags=re.S)
    if m:
        text = m.group(1)

    units: list[Unit] = []
    markers: list[Marker] = []
    segments: list[str] = []
    seg_ranges: dict = {}
    seg: str | None = None
    role: str | None = None
    cue_break = True
    pending_space = True
    i, n = 0, len(text)
    word = ""

    def flush_word():
        nonlocal word, cue_break, pending_space
        if not word:
            return
        if seg is None:
            raise SyntaxError(f"chữ '{word}' nằm ngoài Segment")
        if not tokens(word) and units and units[-1].segment == seg:
            # dấu câu đứng riêng (thường sau Dual Text) dính vào từ trước, không tạo token đọc
            units[-1].display += (" " if pending_space else "") + word
            word, pending_space = "", False
            return
        units.append(Unit(word, tokens(word), seg, role, cue_break=cue_break, sep_before=pending_space))
        word, cue_break, pending_space = "", False, False

    def read_until(stop: str, start: int) -> tuple[str, int]:
        out, j = [], start
        while j < n:
            c = text[j]
            if c == "\\" and j + 1 < n:
                out.append(text[j + 1])
                j += 2
                continue
            if text.startswith(stop, j):
                return "".join(out), j + len(stop)
            out.append(c)
            j += 1
        raise SyntaxError(f"thiếu '{stop}'")

    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            word += text[i + 1]
            i += 2
            continue
        if c.isspace():
            flush_word()
            pending_space = True
            i += 1
            continue
        if text.startswith("||", i):
            flush_word()
            cue_break = True
            i += 2
            continue
        if text.startswith("@{", i):
            flush_word()
            body, i = read_until("}", i + 2)
            markers.append(parse_marker(body, len(units), seg))
            continue
        if c == "{" and units and not word and not pending_space:
            body, i = read_until("}", i + 1)
            units[-1].attrs.update(parse_attrs(body))
            continue
        if c == "{" and word:
            flush_word()
            body, i = read_until("}", i + 1)
            units[-1].attrs.update(parse_attrs(body))
            continue
        if c == "<":
            flush_word()
            close = text.find(">", i)
            inner = text[i + 1:close] if close != -1 else ""
            if "|" in inner and not inner.startswith("/"):
                body, i = read_dual(text, i + 1)
                disp, _, spk = body.partition("|")
                disp, spk = disp.strip(), spk.strip()
                if seg is None:
                    raise SyntaxError("Dual Text nằm ngoài Segment")
                spoken = tokens(spk if spk else disp)
                # marker có thể nằm trong vế hiển thị khi vế đọc bỏ trống
                disp_clean = re.sub(r"@\{[^}]*\}", "", disp)
                units.append(Unit(disp_clean, spoken, seg, role, cue_break=cue_break, sep_before=pending_space))
                cue_break, pending_space = False, False
                continue
            tag = inner.strip()
            i = close + 1
            if tag.startswith("/"):
                name = tag[1:].strip()
                if name != seg:
                    raise SyntaxError(f"đóng </{name}> nhưng Segment đang mở là <{seg}>")
                seg_ranges[seg][1] = len(units)
                seg, role, cue_break = None, None, True
                continue
            if tag.endswith("/"):
                name = tag[:-1].strip()
                if not re.fullmatch(NAME, name) or seg is not None:
                    raise SyntaxError(f"Segment rỗng <{name}/> không hợp lệ ở đây")
                segments.append(name)
                seg_ranges[name] = [len(units), len(units)]
                continue
            if seg is None:
                if not re.fullmatch(NAME, tag) or tag == "script":
                    raise SyntaxError(f"tên Segment không hợp lệ: <{tag}>")
                if tag in seg_ranges:
                    raise SyntaxError(f"Segment trùng tên: <{tag}>")
                seg = tag
                segments.append(tag)
                seg_ranges[tag] = [len(units), None]
                role, cue_break = None, True
            else:
                role, cue_break = tag, True
            continue
        word += c
        i += 1
    flush_word()
    if seg is not None:
        raise SyntaxError(f"Segment <{seg}> chưa đóng")
    check_markers(markers)
    return Script(units, markers, segments, seg_ranges)


def read_dual(text: str, start: int) -> tuple[str, int]:
    out, j = [], start
    while j < len(text):
        c = text[j]
        if c == "\\" and j + 1 < len(text):
            out.append(text[j + 1])
            j += 2
            continue
        if c == ">":
            return "".join(out), j + 1
        out.append(c)
        j += 1
    raise SyntaxError("Dual Text thiếu '>'")


def parse_marker(body: str, pos: int, seg: str | None) -> Marker:
    b = body.strip()
    lead = b.startswith("~")
    b = b.lstrip("~")
    if b.endswith("!"):
        name = b[:-1]
        kind, side = "moment", "prev" if lead else "next"
    elif b.startswith("/"):
        trail = b.endswith("~")
        name = b[1:].rstrip("~")
        kind, side = "close", "next" if trail else "prev"
    else:
        name = b
        kind, side = "open", "prev" if lead else "next"
    if not re.fullmatch(NAME, name):
        raise SyntaxError(f"tên marker không hợp lệ: @{{{body}}}")
    return Marker(name, kind, side, pos, seg)


def check_markers(markers: list[Marker]) -> None:
    opened: dict[str, int] = {}
    seen: set[str] = set()
    for mk in markers:
        if mk.kind == "open":
            if mk.name in opened or mk.name in seen:
                raise SyntaxError(f"Selection '{mk.name}' mở hai lần")
            opened[mk.name] = mk.pos
        elif mk.kind == "close":
            if mk.name not in opened:
                raise SyntaxError(f"đóng '@{{/{mk.name}}}' khi chưa mở")
            del opened[mk.name]
            seen.add(mk.name)
        else:
            if mk.name in seen or mk.name in opened:
                raise SyntaxError(f"tên '{mk.name}' đã dùng")
            seen.add(mk.name)
    if opened:
        raise SyntaxError(f"Selection chưa đóng: {', '.join(opened)}")


def parse_attrs(body: str) -> dict:
    out = {}
    for part in body.split(","):
        part = part.strip()
        if not part:
            continue
        k, eq, v = part.partition("=")
        out[k.strip()] = (num(v.strip()) if eq else True)
    return out


def num(v: str):
    try:
        return float(v) if "." in v else int(v)
    except ValueError:
        return v


def tokens(s: str) -> list[str]:
    return [t for t in re.split(r"\s+", s.strip()) if norm(t)]


def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower().replace("đ", "d"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]", "", t)


# ---------------------------------------------------------------- projections
def dialogue(sc: Script, segment: str | None) -> str:
    lines, cur_role, buf = [], None, []
    for u in sc.units:
        if segment and u.segment != segment:
            continue
        if u.role != cur_role and buf:
            lines.append((f"{cur_role}: " if cur_role else "") + " ".join(buf))
            buf = []
        cur_role = u.role
        buf.extend(u.spoken)
    if buf:
        lines.append((f"{cur_role}: " if cur_role else "") + " ".join(buf))
    return "\n".join(lines)


def speech(sc: Script, segment: str | None) -> str:
    return " ".join(t for u in sc.units if not segment or u.segment == segment for t in u.spoken)


# ---------------------------------------------------------------- align
def align_units(units: list[Unit], words: list[dict], offset: float) -> int:
    """Gán thời gian cho token đọc của units từ transcript; nội suy chỗ không khớp. Trả về số token khớp."""
    toks = [(ui, norm(t)) for ui, u in enumerate(units) for t in u.spoken]
    a = [t for _, t in toks]
    b = [norm(w["word"]) for w in words]
    times: list[tuple[float, float] | None] = [None] * len(a)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    matched = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                w = words[j1 + k]
                times[i1 + k] = (w["start"], w["end"])
                matched += 1
        elif tag == "replace" and words[j1:j2]:
            # chia đều khoảng thời gian của các từ transcript cho các token script
            s, e = words[j1]["start"], words[j2 - 1]["end"]
            step = (e - s) / (i2 - i1)
            for k in range(i2 - i1):
                times[i1 + k] = (s + k * step, s + (k + 1) * step)
    # nội suy các token còn trống
    known = [k for k, t in enumerate(times) if t]
    if not known:
        raise SystemExit("không khớp được từ nào giữa kịch bản và lời thoại — kiểm tra ngôn ngữ/file")
    for k, t in enumerate(times):
        if t:
            continue
        prev = max((p for p in known if p < k), default=None)
        nxt = min((p for p in known if p > k), default=None)
        if prev is not None and nxt is not None:
            s, e = times[prev][1], times[nxt][0]
            span = max(e - s, 0.0) / (nxt - prev)
            times[k] = (s + (k - prev - 1) * span, s + (k - prev) * span)
        elif prev is not None:
            times[k] = (times[prev][1], times[prev][1] + 0.25)
        else:
            times[k] = (max(times[nxt][0] - 0.25, 0), times[nxt][0])
    for (ui, _), (s, e) in zip(toks, times):
        u = units[ui]
        u.start = round(s + offset, 3) if u.start is None else min(u.start, round(s + offset, 3))
        u.end = round(e + offset, 3) if u.end is None else max(u.end, round(e + offset, 3))
    return matched


def resolve(sc: Script, seg_windows: dict) -> dict:
    def seg_bound(segment: str | None, which: str, pos: int) -> float:
        if segment:
            return seg_windows[segment][0 if which == "start" else 1]
        # marker ngoài Segment: lấy ranh giới Segment kề bên
        for s in sc.segments:
            i0, i1 = sc.seg_ranges[s]
            if which == "start" and i0 >= pos:
                return seg_windows[s][0]
        for s in reversed(sc.segments):
            i0, i1 = sc.seg_ranges[s]
            if which == "end" and i1 <= pos:
                return seg_windows[s][1]
        return seg_windows[sc.segments[0 if which == "start" else -1]][0 if which == "start" else 1]

    def at(mk: Marker) -> float:
        if mk.side == "next":
            nxt = next((u for u in sc.units[mk.pos:] if u.spoken and (mk.segment is None or u.segment == mk.segment)), None)
            return nxt.start if nxt else seg_bound(mk.segment, "end", mk.pos)
        prv = next((u for u in reversed(sc.units[:mk.pos]) if u.spoken and (mk.segment is None or u.segment == mk.segment)), None)
        return prv.end if prv else seg_bound(mk.segment, "start", mk.pos)

    selections, moments, open_at = {}, {}, {}
    for mk in sc.markers:
        if mk.kind == "open":
            open_at[mk.name] = at(mk)
        elif mk.kind == "close":
            selections[mk.name] = {"start": open_at.pop(mk.name), "end": at(mk)}
        else:
            moments[mk.name] = at(mk)
    return {"selections": selections, "moments": moments}


def build_cues(sc: Script) -> list[dict]:
    cues, cur = [], None
    for ui, u in enumerate(sc.units):
        if u.cue_break or cur is None or u.segment != sc.units[cur["units"][-1]].segment:
            cur = {"units": []}
            cues.append(cur)
        cur["units"].append(ui)
    out = []
    for c in cues:
        shown = [i for i in c["units"] if sc.units[i].display]
        if not shown:
            continue
        us = [sc.units[i] for i in c["units"]]
        text = ""
        for i in shown:
            u = sc.units[i]
            text += (" " if text and u.sep_before else "") + u.display
        out.append({"start": us[0].start, "end": us[-1].end, "text": text, "units": shown,
                    "role": us[0].role, "segment": us[0].segment})
    return out


def media_duration(path: Path) -> float:
    from vkit import probe
    return probe(path)["duration"]


def cmd_align(a: argparse.Namespace) -> None:
    sc = parse(Path(a.script).read_text())
    seg_windows: dict = {}
    takes: list[dict] = []
    single = dict(m.split("=", 1) for m in a.media or []).get("all")
    if single and not a.transcript:
        # một video chứa cả kịch bản: bóc lời một lần rồi căn chỉnh như --transcript
        from vkit import transcribe
        path = Path(single)
        tx_path = path.with_suffix(".transcript.json")
        if not tx_path.exists() or a.retranscribe:
            print(f"• bóc lời {path} ...", file=sys.stderr)
            tx_path.write_text(json.dumps(transcribe(path, a.language, a.model), ensure_ascii=False, indent=2))
        a.transcript = str(tx_path)
    if a.transcript:
        # một bản ghi duy nhất cho cả kịch bản
        words = json.loads(Path(a.transcript).read_text())["words"]
        matched = align_units(sc.units, words, 0.0)
        total = len([t for u in sc.units for t in u.spoken])
        for s in sc.segments:
            us = [u for u in sc.units if u.segment == s]
            seg_windows[s] = [us[0].start, us[-1].end] if us else [0.0, 0.0]
        dur = media_duration(Path(single)) if single else max(w["end"] for w in words)
        takes.append({"segments": sc.segments, "transcript": a.transcript, "matched": matched, "tokens": total})
    else:
        if not a.media:
            raise SystemExit("cần --transcript hoặc ít nhất một --media seg=file")
        from vkit import transcribe
        cursor = 0.0
        given = dict(m.split("=", 1) for m in a.media)
        for s in sc.segments:
            if s not in given:
                raise SystemExit(f"thiếu --media cho Segment '{s}'")
            path = Path(given[s])
            tx_path = path.with_suffix(".transcript.json")
            if tx_path.exists() and not a.retranscribe:
                tx = json.loads(tx_path.read_text())
            else:
                print(f"• bóc lời {path} ...", file=sys.stderr)
                tx = transcribe(path, a.language, a.model)
                tx_path.write_text(json.dumps(tx, ensure_ascii=False, indent=2))
            dur = media_duration(path)
            us = [u for u in sc.units if u.segment == s]
            matched = align_units(us, tx["words"], cursor) if us else 0
            seg_windows[s] = [round(cursor, 3), round(cursor + dur, 3)]
            takes.append({"segment": s, "media": str(path), "start": round(cursor, 3), "duration": round(dur, 3),
                          "matched": matched, "tokens": sum(len(u.spoken) for u in us)})
            cursor += dur
        dur = cursor

    res = resolve(sc, seg_windows)
    out = {
        "script": a.script,
        "duration": round(dur, 3),
        "segments": {s: {"start": w[0], "end": w[1]} for s, w in seg_windows.items()},
        "takes": takes,
        **res,
        "words": [{"display": u.display, "spoken": " ".join(u.spoken), "start": u.start, "end": u.end,
                   "segment": u.segment, "role": u.role, "attrs": u.attrs} for u in sc.units],
        "cues": build_cues(sc),
    }
    dst = Path(a.out or Path(a.script).with_suffix(".timing.json"))
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    for t in takes:
        rate = t["matched"] / t["tokens"] * 100 if t["tokens"] else 100
        flag = "" if rate >= 70 else "  ⚠ khớp thấp — kiểm tra lời đọc có đúng kịch bản không"
        print(f"• {t.get('segment', 'toàn bộ')}: khớp {t['matched']}/{t['tokens']} token ({rate:.0f}%){flag}")
    for k, v in res["selections"].items():
        print(f"  @{{{k}}}  {v['start']:7.2f} → {v['end']:7.2f}s")
    for k, v in res["moments"].items():
        print(f"  @{{{k}!}} {v:7.2f}s")
    print(dst)


# ---------------------------------------------------------------- captions
def cmd_captions(a: argparse.Namespace) -> None:
    from vkit import ass_color, ass_time, srt_time
    tm = json.loads(Path(a.timing).read_text())
    words, cues = tm["words"], tm["cues"]
    W, H = a.width, a.height
    fs = a.size or round(H * 0.045)
    base, hi, key = ass_color(a.color), ass_color(a.highlight), ass_color(a.keyword)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{a.font_name},{fs},{base},{base},&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{max(2, fs // 12)},2,2,60,60,{round(H * a.position)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events, srt = [], []
    for ci, cue in enumerate(cues):
        nxt = cues[ci + 1]["start"] if ci + 1 < len(cues) else cue["end"] + 0.4
        end = min(max(cue["end"], cue["start"] + 0.35), nxt)
        idx = cue["units"]

        def render(active: int | None) -> str:
            out = ""
            for k in idx:
                w = words[k]
                txt = w["display"].upper() if a.upper else w["display"]
                emph = any(w["attrs"].get(x) for x in ("emphasis", "keyword", "highlight"))
                if k == active:
                    txt = f"{{\\c{hi}\\fscx108\\fscy108}}{txt}{{\\r}}"
                elif emph:
                    txt = f"{{\\c{key}}}{txt}{{\\r}}"
                out += (" " if out else "") + txt
            return out

        if a.mode == "karaoke":
            for j, k in enumerate(idx):
                s = words[k]["start"]
                e = words[idx[j + 1]]["start"] if j + 1 < len(idx) else end
                events.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Cap,,0,0,0,,{render(k)}")
        else:
            pop = "{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}"
            events.append(f"Dialogue: 0,{ass_time(cue['start'])},{ass_time(end)},Cap,,0,0,0,,{pop}{render(None)}")
        srt.append(f"{ci + 1}\n{srt_time(cue['start'])} --> {srt_time(end)}\n{cue['text']}\n")
    stem = Path(a.out) if a.out else Path(a.timing).with_suffix("")
    Path(f"{stem}.ass").write_text(header + "\n".join(events) + "\n")
    Path(f"{stem}.srt").write_text("\n".join(srt))
    print(f"{stem}.ass\n{stem}.srt  ({len(cues)} cụm theo ||)")


# ---------------------------------------------------------------- main
def main() -> None:
    p = argparse.ArgumentParser(prog="vscript", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check")
    c.add_argument("script")
    d = sub.add_parser("dialogue")
    d.add_argument("script")
    d.add_argument("--segment")
    s = sub.add_parser("speech")
    s.add_argument("script")
    s.add_argument("--segment")
    e = sub.add_parser("estimate")
    e.add_argument("script")
    e.add_argument("--lang", default="vi")
    e.add_argument("--rate", type=float, help="token/giây (mặc định vi 4.5, en 3.0)")

    al = sub.add_parser("align")
    al.add_argument("script")
    al.add_argument("--media", action="append",
                    help="seg=file.mp4 cho từng Segment (theo thứ tự), hoặc all=file.mp4 khi một video chứa cả kịch bản")
    al.add_argument("--transcript", help="một transcript.json cho cả kịch bản")
    al.add_argument("--language")
    al.add_argument("--model", default="small")
    al.add_argument("--retranscribe", action="store_true")
    al.add_argument("--out")

    cp = sub.add_parser("captions")
    cp.add_argument("timing")
    cp.add_argument("--out")
    cp.add_argument("--mode", choices=["karaoke", "pop"], default="karaoke")
    cp.add_argument("--width", type=int, default=1080)
    cp.add_argument("--height", type=int, default=1920)
    cp.add_argument("--size", type=int)
    cp.add_argument("--position", type=float, default=0.28)
    cp.add_argument("--color", default="#FFFFFF")
    cp.add_argument("--highlight", default="#FFE14D")
    cp.add_argument("--keyword", default="#FFE14D", help="màu cho từ có {emphasis}/{keyword}")
    cp.add_argument("--font-name", default="Inter ExtraBold")
    cp.add_argument("--upper", action="store_true")
    a = p.parse_args()

    try:
        if a.cmd in ("check", "dialogue", "speech", "estimate"):
            sc = parse(Path(a.script).read_text())
        if a.cmd == "check":
            sels = sorted({m.name for m in sc.markers if m.kind == "open"})
            moms = sorted({m.name for m in sc.markers if m.kind == "moment"})
            roles = sorted({u.role for u in sc.units if u.role})
            print(f"Segments ({len(sc.segments)}): {', '.join(sc.segments)}")
            print(f"Vai: {', '.join(roles) or '—'}")
            print(f"Selections ({len(sels)}): {', '.join(sels) or '—'}")
            print(f"Moments ({len(moms)}): {', '.join(moms) or '—'}")
            print(f"Từ hiển thị: {sum(1 for u in sc.units if u.display)} · token đọc: "
                  f"{sum(len(u.spoken) for u in sc.units)} · cụm phụ đề: {len(build_cues(sc))}")
        elif a.cmd == "dialogue":
            print(dialogue(sc, a.segment))
        elif a.cmd == "speech":
            print(speech(sc, a.segment))
        elif a.cmd == "estimate":
            rate = a.rate or (4.5 if a.lang == "vi" else 3.0)
            total = 0.0
            for sname in sc.segments:
                ntok = sum(len(u.spoken) for u in sc.units if u.segment == sname)
                sec = ntok / rate
                total += sec
                print(f"{sname:20s} {ntok:4d} token  ≈ {sec:5.1f}s")
            print(f"{'TỔNG':20s}       ≈ {total:5.1f}s  (tốc độ {rate} token/s; cộng thêm thời gian cho phản ứng)")
        elif a.cmd == "align":
            cmd_align(a)
        elif a.cmd == "captions":
            cmd_captions(a)
    except SyntaxError as err:
        raise SystemExit(f"vscript: lỗi cú pháp: {err}")


if __name__ == "__main__":
    main()
