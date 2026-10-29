#!/usr/bin/env python3
"""vaudio — âm thanh chất lượng cao bằng ElevenLabs, neo theo kịch bản.

  vaudio.py voices                                     Liệt kê giọng trong tài khoản
  vaudio.py design <production.toml> --role HOST --description "..." [--yes]
                                                       Thiết kế giọng từ mô tả → 3 bản nghe thử
  vaudio.py save   <production.toml> --role HOST --preview 1 --name "Ten giong" [--yes]
                                                       Lưu bản nghe thử thành giọng (ghi voice_id ra màn hình)
  vaudio.py tts    <production.toml> [--segment id] [--yes]
                                                       Đọc từng Segment bằng phần ĐỌC của Dual Text → assets/vo/<seg>.mp3
                                                       + <seg>.transcript.json (mốc từng từ lấy thẳng từ ElevenLabs,
                                                       không cần Whisper) — sau đó `vscript align --media seg=...`
  vaudio.py sfx    <production.toml> [--id x] [--yes]  Sinh hiệu ứng âm thanh cho [[sfx]]   → assets/sfx/<id>.mp3
  vaudio.py music  <production.toml> [--yes]           Sinh nhạc nền cho [music]          → assets/music/<file>

Khóa: ELEVENLABS_API_KEY. Mặc định chỉ in yêu cầu (chạy thử); thêm --yes để gọi thật (tốn credit).
Lưu ý: eleven_multilingual_v2 KHÔNG hỗ trợ tiếng Việt — dùng eleven_v4 / eleven_v3 / eleven_flash_v2_5.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vscript  # noqa: E402
from production import Production  # noqa: E402

API = "https://api.elevenlabs.io"
DEFAULTS = {
    "tts_model": "eleven_v4",
    "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True},
    "sfx_model": "eleven_text_to_sound_v2",
    "music_model": "music_v1",
    "design_model": "eleven_ttv_v3",
    "format": "mp3_44100_128",
}


def die(msg: str) -> None:
    raise SystemExit(f"vaudio: {msg}")


def cfg(prod: Production) -> dict:
    a = {**DEFAULTS, **prod.cfg.get("audio", {})}
    a["voices"] = prod.cfg.get("voices", {})
    return a


def call(path: str, body: dict | None = None, method: str = "POST", query: str = "") -> bytes:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        die("thiếu ELEVENLABS_API_KEY — tạo key ở elevenlabs.io/app/settings/api-keys rồi `export ELEVENLABS_API_KEY=...`")
    req = urllib.request.Request(f"{API}{path}{query}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        die(f"{path}: HTTP {e.code} {e.read()[:400].decode(errors='replace')}")


def show(title: str, body: dict) -> None:
    print(f"• {title}\n{json.dumps(body, ensure_ascii=False, indent=2)}\n  (chạy thử — thêm --yes để gọi thật)")


# ---------------------------------------------------------------- voices
def cmd_voices(_a) -> None:
    data = json.loads(call("/v1/voices", method="GET"))
    for v in data.get("voices", []):
        labels = ", ".join(f"{k}={x}" for k, x in (v.get("labels") or {}).items())
        print(f"{v['voice_id']}  {v['name']:28s} {v.get('category', '')}  {labels}")


def cmd_design(a) -> None:
    prod = Production(a.production)
    c = cfg(prod)
    body = {"voice_description": a.description, "model_id": c["design_model"]}
    if a.text:
        body["text"] = a.text
    else:
        body["auto_generate_text"] = True
    if not a.yes:
        return show("thiết kế giọng " + a.role, body)
    data = json.loads(call("/v1/text-to-voice/design", body))
    out = prod.root / "assets" / "voice" / a.role
    out.mkdir(parents=True, exist_ok=True)
    meta = []
    for i, p in enumerate(data.get("previews", []), 1):
        f = out / f"preview-{i}.mp3"
        f.write_bytes(base64.b64decode(p["audio_base_64"]))
        meta.append({"preview": i, "generated_voice_id": p["generated_voice_id"], "file": str(f.relative_to(prod.root))})
        print(f"  ✓ {f}")
    (out / "previews.json").write_text(json.dumps({"description": a.description, "text": data.get("text"),
                                                   "previews": meta}, ensure_ascii=False, indent=2))
    print(f"Nghe thử rồi chốt: vaudio.py save {a.production} --role {a.role} --preview N --name \"...\" --yes")


def cmd_save(a) -> None:
    prod = Production(a.production)
    meta = json.loads((prod.root / "assets" / "voice" / a.role / "previews.json").read_text())
    pv = next((p for p in meta["previews"] if p["preview"] == a.preview), None) or die("không có bản nghe thử đó")
    # endpoint lưu giọng từ bản thiết kế — kiểm tra lại docs nếu ElevenLabs đổi API
    body = {"voice_name": a.name, "voice_description": meta["description"], "generated_voice_id": pv["generated_voice_id"]}
    if not a.yes:
        return show("lưu giọng", body)
    data = json.loads(call("/v1/text-to-voice", body))
    print(f"voice_id = {data.get('voice_id')}\nThêm vào production.toml:\n[voices]\n{a.role} = \"{data.get('voice_id')}\"")


# ---------------------------------------------------------------- tts
def turns(sc: vscript.Script, seg: str) -> list[tuple[str | None, str]]:
    out: list[tuple[str | None, list[str]]] = []
    for u in sc.units:
        if u.segment != seg or not u.spoken:
            continue
        if not out or out[-1][0] != u.role:
            out.append((u.role, []))
        out[-1][1].extend(u.spoken)
    return [(r, " ".join(t)) for r, t in out]


def words_from_alignment(al: dict, offset: float) -> list[dict]:
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, s0, e0 = [], "", None, None
    for ch, s, e in zip(chars, st, en):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": round(s0 + offset, 3), "end": round(e0 + offset, 3)})
            cur, s0 = "", None
            continue
        if s0 is None:
            s0 = s
        cur, e0 = cur + ch, e
    if cur:
        words.append({"word": cur, "start": round(s0 + offset, 3), "end": round(e0 + offset, 3)})
    return words


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout
    return float(out.strip() or 0)


def cmd_tts(a) -> None:
    prod = Production(a.production)
    c = cfg(prod)
    sc = prod.script
    vo_dir = prod.root / c.get("vo_dir", "assets/vo")
    segs = [a.segment] if a.segment else sc.segments
    for si, seg in enumerate(segs):
        parts = turns(sc, seg)
        if not parts:
            continue
        files, words, t = [], [], 0.0
        for k, (role, text) in enumerate(parts):
            voice = c["voices"].get(role or "default") or c["voices"].get("default")
            if not voice and not a.yes:
                voice = f"<chưa có voice_id cho {role}>"
            if not voice:
                die(f"chưa có giọng cho vai '{role}' — thêm [voices] {role or 'default'} = \"<voice_id>\" (xem `vaudio voices`)")
            body = {"text": text, "model_id": c["tts_model"], "voice_settings": c["voice_settings"]}
            if c["tts_model"] != "eleven_multilingual_v2" and prod.lang:
                body["language_code"] = prod.lang
            prev = " ".join(x for _, x in parts[:k]) or (vscript.speech(sc, segs[si - 1]) if si else "")
            if prev:
                body["previous_text"] = prev[-500:]
            if not a.yes:
                show(f"{seg} · {role} · giọng {voice}", body)
                continue
            data = json.loads(call(f"/v1/text-to-speech/{voice}/with-timestamps", body, query=f"?output_format={c['format']}"))
            vo_dir.mkdir(parents=True, exist_ok=True)
            f = vo_dir / f"{seg}.part{k}.mp3"
            f.write_bytes(base64.b64decode(data["audio_base64"]))
            al = data.get("alignment") or data.get("normalized_alignment")
            if al:
                words += words_from_alignment(al, t)
            files.append(f)
            t += duration(f)
        if not a.yes:
            continue
        dst = vo_dir / f"{seg}.mp3"
        if len(files) == 1:
            files[0].replace(dst)
        else:
            lst = vo_dir / f"{seg}.list.txt"
            lst.write_text("".join(f"file '{p.resolve()}'\n" for p in files))
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)], check=True)
            for p in files + [lst]:
                p.unlink()
        dst.with_suffix(".transcript.json").write_text(json.dumps(
            {"language": prod.lang, "source": "elevenlabs-alignment", "words": words}, ensure_ascii=False, indent=2))
        print(f"  ✓ {dst}  ({duration(dst):.1f}s, {len(words)} từ có mốc)")
    if a.yes:
        media = " ".join(f"--media {s}={(vo_dir / f'{s}.mp3').relative_to(prod.root)}" for s in segs)
        print(f"\nNeo kịch bản vào giọng đọc:\n  cd {prod.root} && python3 {Path(__file__).parent / 'vscript.py'} align "
              f"{prod.script_path.name} {media}")


# ---------------------------------------------------------------- sfx / music
def cmd_sfx(a) -> None:
    prod = Production(a.production)
    c = cfg(prod)
    for s in prod.cfg.get("sfx", []):
        if a.id and s["id"] != a.id:
            continue
        if not s.get("text"):
            continue
        body = {"text": s["text"], "model_id": c["sfx_model"], "prompt_influence": s.get("influence", 0.4)}
        if s.get("duration"):
            body["duration_seconds"] = float(s["duration"])
        if not a.yes:
            show(f"sfx {s['id']}", body)
            continue
        dst = prod.root / s.get("file", f"assets/sfx/{s['id']}.mp3")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(call("/v1/sound-generation", body, query=f"?output_format={c['format']}"))
        print(f"  ✓ {dst}")


def cmd_music(a) -> None:
    prod = Production(a.production)
    c = cfg(prod)
    m = prod.cfg.get("music") or die("chưa có bảng [music] trong production.toml")
    if not m.get("prompt"):
        die("[music] cần `prompt` để sinh (hoặc trỏ `file` tới nhạc có sẵn có license)")
    length = m.get("length") or prod.timing["duration"] + 1.0
    body = {"prompt": m["prompt"], "music_length_ms": int(max(3, length) * 1000), "model_id": c["music_model"],
            "force_instrumental": m.get("instrumental", True)}
    if not a.yes:
        return show("nhạc nền", body)
    dst = prod.root / m.get("file", "assets/music/bed.mp3")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(call("/v1/music", body))
    print(f"  ✓ {dst}")


def main() -> None:
    p = argparse.ArgumentParser(prog="vaudio", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("voices").set_defaults(fn=cmd_voices)
    d = sub.add_parser("design")
    d.add_argument("production")
    d.add_argument("--role", required=True)
    d.add_argument("--description", required=True)
    d.add_argument("--text", help="câu mẫu 100–1000 ký tự (bỏ trống để tự sinh)")
    d.add_argument("--yes", action="store_true")
    d.set_defaults(fn=cmd_design)
    s = sub.add_parser("save")
    s.add_argument("production")
    s.add_argument("--role", required=True)
    s.add_argument("--preview", type=int, required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--yes", action="store_true")
    s.set_defaults(fn=cmd_save)
    t = sub.add_parser("tts")
    t.add_argument("production")
    t.add_argument("--segment")
    t.add_argument("--yes", action="store_true")
    t.set_defaults(fn=cmd_tts)
    x = sub.add_parser("sfx")
    x.add_argument("production")
    x.add_argument("--id")
    x.add_argument("--yes", action="store_true")
    x.set_defaults(fn=cmd_sfx)
    m = sub.add_parser("music")
    m.add_argument("production")
    m.add_argument("--yes", action="store_true")
    m.set_defaults(fn=cmd_music)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
