#!/usr/bin/env python3
"""vgen — tạo ảnh/video bằng nhiều model từ cùng một production.toml.

  vgen.py models                                   Liệt kê model trong config/models.toml
  vgen.py cards  <production.toml> [--shot id]     Viết thẻ prompt prompts/<shot>.md (dán vào web/app)
  vgen.py run    <production.toml> --shot id [--model a,b] [-n 2] [--yes]
                                                   Gọi model qua API (mặc định chỉ in payload = chạy thử)
  vgen.py pick   <production.toml> --shot id --file <ứng viên>   Chốt ứng viên → đường dẫn `asset`

Ưu tiên nhà cung cấp chính chủ: `model = "gpt-image"` / `"seedance"`... là model LOGIC, vgen chọn tuyến đầu
tiên trong [prefer] của config/models.toml mà bạn đã có key (OpenAI → fal, BytePlus → fal...).
Khóa: OPENAI_API_KEY · ARK_API_KEY (BytePlus ModelArk, Seedance) · FAL_KEY (fal.ai, dự phòng nhiều model).
Model provider="manual" chỉ có thẻ prompt (Higgsfield, Midjourney, Kling app...).
Ứng viên lưu ở assets/gen/<shot>/, nhật ký ở prompts/<shot>.log.jsonl — mọi lần chạy đều tái lập được.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import shutil
import sys
import time
import tomllib
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import vscript  # noqa: E402
from production import Production  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


KEYS = {"fal": "FAL_KEY", "openai": "OPENAI_API_KEY", "byteplus": "ARK_API_KEY", "elevenlabs": "ELEVENLABS_API_KEY"}


def config() -> dict:
    return tomllib.loads((ROOT / "config" / "models.toml").read_text())


def registry() -> dict:
    return config()["models"]


def resolve_model(name: str, quiet: bool = False) -> tuple[str, dict]:
    """Model logic → tuyến cụ thể: tuyến chính chủ đầu tiên có key; nếu chưa có key nào thì tuyến đầu."""
    cfg = config()
    reg, prefer = cfg["models"], cfg.get("prefer", {})
    if name in reg:
        return name, reg[name]
    if name not in prefer:
        die(f"không có model '{name}' trong config/models.toml (xem `vgen models`)")
    routes = prefer[name]
    ready = [r for r in routes if reg[r]["provider"] == "manual" or os.environ.get(KEYS.get(reg[r]["provider"], ""))]
    pick = ready[0] if ready else routes[0]
    if not quiet:
        why = "có key" if ready else "chưa có key nào — hiển thị tuyến ưu tiên nhất"
        print(f"  {name} → {pick} ({reg[pick]['provider']}, {why}; thứ tự: {' > '.join(routes)})")
    return pick, reg[pick]


def die(msg: str) -> None:
    raise SystemExit(f"vgen: {msg}")


# ---------------------------------------------------------------- prompt assembly
def resolve_path(prod: Production, ref: str) -> Path:
    if ref.startswith("shot:"):
        sh = prod.shot(ref[5:])
        p = prod.asset(sh)
        if not p:
            die(f"tham chiếu {ref}: shot '{sh['id']}' chưa có asset đã chốt ({sh.get('asset')})")
        return p
    p = prod.root / ref
    if not p.exists():
        die(f"không thấy file tham chiếu {p}")
    return p


def full_prompt(prod: Production, shot: dict) -> str:
    text = shot.get("prompt", "").strip()
    seg = shot.get("dialogue")
    if seg:
        text += "\n\nDialogue:\n" + vscript.dialogue(prod.script, seg)
    return text


def shot_duration(prod: Production, shot: dict) -> int | None:
    if "duration" in shot:
        return int(shot["duration"])
    seg = shot.get("dialogue")
    if seg and seg in prod.timing["segments"]:
        s = prod.timing["segments"][seg]
        return int(s["end"] - s["start"] + 1.999)   # làm tròn lên + chừa ~1s cho phản ứng
    return None


def snap_duration(d: int | None, allowed: list | None, rng: list | None) -> int | None:
    if d is None or not (allowed or rng):
        return d
    if rng:
        lo, hi = rng
        if d > hi:
            print(f"  ⚠ cần {d}s nhưng model tối đa {hi}s — chia Segment ở chỗ ý chuyển hướng (docs/03)")
        return max(lo, min(d, hi))
    fits = [x for x in sorted(allowed) if x >= d]
    if not fits:
        print(f"  ⚠ cần {d}s nhưng model tối đa {max(allowed)}s — chia Segment ở chỗ ý chuyển hướng (docs/03)")
    return fits[0] if fits else max(allowed)


def data_uri(p: Path) -> str:
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def build_payload(prod: Production, shot: dict, model: dict) -> dict:
    inp = model.get("inputs", {})
    payload = dict(model.get("defaults", {}))
    payload[inp.get("prompt", "prompt")] = full_prompt(prod, shot)
    if "aspect" in inp and shot.get("aspect"):
        payload[inp["aspect"]] = model.get("aspect_map", {}).get(shot["aspect"], shot["aspect"])
    if "resolution" in inp and shot.get("resolution"):
        payload[inp["resolution"]] = shot["resolution"]
    if "duration" in inp:
        d = snap_duration(shot_duration(prod, shot), model.get("durations"), model.get("duration_range"))
        if d:
            payload[inp["duration"]] = model.get("duration_format", "{}").format(d)
    if "audio" in inp and "audio" in shot:
        payload[inp["audio"]] = bool(shot["audio"])
    refs = shot.get("refs", [])
    if shot.get("image"):
        if "image" not in inp:
            die(f"model không nhận ảnh đầu; bỏ 'image' hoặc chọn model image-to-video")
        payload[inp["image"]] = data_uri(resolve_path(prod, shot["image"]))
    if shot.get("end_image"):
        if "end_image" not in inp:
            die("model không nhận khung cuối (end_image)")
        payload[inp["end_image"]] = data_uri(resolve_path(prod, shot["end_image"]))
    if refs:
        if "images" in inp:
            payload[inp["images"]] = [data_uri(resolve_path(prod, r)) for r in refs]
        elif "image" in inp and inp["image"] not in payload:
            payload[inp["image"]] = data_uri(resolve_path(prod, refs[0]))
        else:
            die("model này không nhận ảnh tham chiếu — dùng bản *-edit hoặc model khác")
    return payload


def openai_request(prod: Production, shot: dict, model: dict) -> dict:
    body = {"model": model["model_id"], "prompt": full_prompt(prod, shot), **model.get("defaults", {})}
    if shot.get("aspect"):
        body["size"] = model.get("size_map", {}).get(shot["aspect"], "auto")
    refs = [resolve_path(prod, r) for r in shot.get("refs", [])] + \
           ([resolve_path(prod, shot["image"])] if shot.get("image") else [])
    return {"body": body, "files": refs}


def byteplus_request(prod: Production, shot: dict, model: dict) -> dict:
    content = [{"type": "text", "text": full_prompt(prod, shot)}]
    for key, role in (("image", "first_frame"), ("end_image", "last_frame")):
        if shot.get(key):
            content.append({"type": "image_url", "image_url": {"url": data_uri(resolve_path(prod, shot[key]))}, "role": role})
    for r in shot.get("refs", []):
        content.append({"type": "image_url", "image_url": {"url": data_uri(resolve_path(prod, r))}, "role": "reference_image"})
    for r in shot.get("ref_videos", []):
        if not r.startswith("http"):
            die("BytePlus chỉ nhận video tham chiếu dạng URL công khai (ref_videos)")
        content.append({"type": "video_url", "video_url": {"url": r}, "role": "reference_video"})
    body = {"model": model["model_id"], "content": content, **model.get("defaults", {})}
    if shot.get("aspect"):
        body["ratio"] = shot["aspect"]
    if shot.get("resolution"):
        body["resolution"] = shot["resolution"]
    if "audio" in shot:
        body["generate_audio"] = bool(shot["audio"])
    d = snap_duration(shot_duration(prod, shot), model.get("durations"), model.get("duration_range"))
    if d:
        body["duration"] = d
    return body


def preview(payload: dict) -> str:
    def short(v):
        if isinstance(v, str) and v.startswith("data:"):
            return v[:40] + f"…({len(v) // 1024} KB)"
        if isinstance(v, list):
            return [short(x) for x in v]
        return v
    return json.dumps({k: short(v) for k, v in payload.items()}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- providers
def http(method: str, url: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Key {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read() or b"{}")


def run_fal(endpoint: str, payload: dict, timeout: int) -> tuple[dict, str]:
    key = os.environ.get("FAL_KEY")
    if not key:
        die("thiếu FAL_KEY — tạo key ở fal.ai/dashboard/keys rồi `export FAL_KEY=...`")
    sub = http("POST", f"https://queue.fal.run/{endpoint}", key, payload)
    rid, status_url, resp_url = sub["request_id"], sub["status_url"], sub["response_url"]
    print(f"  · đã gửi {endpoint} (request {rid})")
    t0 = time.time()
    while True:
        st = http("GET", status_url, key)
        if st.get("status") == "COMPLETED":
            if st.get("error"):
                die(f"{endpoint} lỗi: {st['error']}")
            break
        if time.time() - t0 > timeout:
            die(f"quá {timeout}s chưa xong; request_id={rid} (lấy lại kết quả bằng response_url sau)")
        print(f"  · {st.get('status')} {st.get('queue_position', '')}", end="\r")
        time.sleep(4)
    return http("GET", resp_url, key), rid


def run_openai(req: dict, timeout: int) -> list[bytes]:
    key = os.environ.get("OPENAI_API_KEY") or die("thiếu OPENAI_API_KEY")
    body, files = req["body"], req["files"]
    if not files:
        r = urllib.request.Request("https://api.openai.com/v1/images/generations", data=json.dumps(body).encode(),
                                   headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    else:
        # chỉnh sửa / tham chiếu: multipart với image[] (nhiều ảnh)
        boundary = "vgen" + os.urandom(8).hex()
        parts = []
        for k, v in body.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for f in files:
            mime = mimetypes.guess_type(f.name)[0] or "image/png"
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{f.name}"\r\n'
                         f"Content-Type: {mime}\r\n\r\n".encode() + f.read_bytes() + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        r = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"".join(parts),
                                   headers={"Authorization": f"Bearer {key}",
                                            "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return [base64.b64decode(d["b64_json"]) for d in data.get("data", []) if d.get("b64_json")]


def run_byteplus(body: dict, base: str, timeout: int) -> tuple[str, str]:
    key = os.environ.get("ARK_API_KEY") or die("thiếu ARK_API_KEY (BytePlus ModelArk console → API keys)")

    def ark(method: str, path: str, payload: dict | None = None) -> dict:
        r = urllib.request.Request(f"{base}{path}", method=method, data=json.dumps(payload).encode() if payload else None,
                                   headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=120) as resp:
            return json.loads(resp.read())

    task = ark("POST", "/contents/generations/tasks", body)
    tid = task["id"]
    print(f"  · đã gửi BytePlus task {tid}")
    t0 = time.time()
    while True:
        st = ark("GET", f"/contents/generations/tasks/{tid}")
        status = st.get("status")
        if status == "succeeded":
            return st["content"]["video_url"], tid
        if status in ("failed", "cancelled", "expired"):
            die(f"BytePlus task {tid}: {status} {st.get('error')}")
        if time.time() - t0 > timeout:
            die(f"quá {timeout}s; task {tid} vẫn {status}")
        print(f"  · {status}", end="\r")
        time.sleep(5)


def output_urls(result: dict, field: str) -> list[str]:
    v = result.get(field)
    if isinstance(v, list):
        return [x["url"] for x in v if isinstance(x, dict) and "url" in x]
    if isinstance(v, dict) and "url" in v:
        return [v["url"]]
    return []


def download(url: str, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as r:
        ext = mimetypes.guess_extension(r.headers.get_content_type() or "") or Path(url).suffix or ".bin"
        out = dst.with_suffix(".jpg" if ext == ".jpe" else ext)
        out.write_bytes(r.read())
    return out


# ---------------------------------------------------------------- commands
def cmd_models(_a) -> None:
    cfg = config()
    print("Model logic (dùng trong production.toml) → tuyến theo thứ tự ưu tiên:")
    for name, routes in cfg.get("prefer", {}).items():
        chosen, _ = resolve_model(name, quiet=True)
        print(f"  {name:14s} " + " > ".join(f"[{r}]" if r == chosen else r for r in routes))
    print("  ([...] = tuyến sẽ dùng với các key hiện có)\n")
    for alias, m in registry().items():
        mark = "✓" if m.get("verified") else ("·" if m["provider"] == "manual" else "?")
        print(f"{mark} {alias:22s} {m['provider']:9s} {m['type']:6s} {m.get('endpoint', m.get('model_id', m.get('url', '')))}")
        if m.get("strengths"):
            print(f"    {m['strengths']}")
    print("\n✓ đã đối chiếu schema · ? cần kiểm tra endpoint trước khi chạy · · thủ công (web/app)")


CARD = """# Thẻ prompt · {id}

| | |
|---|---|
| Lớp / khung | {layer} / {frame} |
| Gắn vào | `{during}` → {window} |
| Lời đang nói | {excerpt} |
| Model | **{model}** ({provider}) {url} |
| Tham số | {params} |
| Tham chiếu | {refs} |

**Vì sao model này:** {strengths}

**Mẹo riêng:** {tips}

## Prompt

```text
{prompt}
```

## Chấm ứng viên (thang 14 điểm, docs/01)
| Ứng viên | Model | Điểm | Lỗi | Chốt? |
|---|---|---|---|---|
| | | | | |
"""


def cmd_cards(a) -> None:
    prod = Production(a.production)
    out_dir = prod.root / "prompts"
    out_dir.mkdir(exist_ok=True)
    for shot in prod.shots:
        if a.shot and shot["id"] != a.shot:
            continue
        m = resolve_model(shot["model"], quiet=True)[1] if shot.get("model") else {}
        w = prod.window(shot.get("during"))
        params = {k: shot[k] for k in ("kind", "aspect", "resolution", "duration", "audio") if k in shot}
        d = shot_duration(prod, shot)
        if d and "duration" not in params:
            params["duration (ước lượng)"] = f"{d}s"
        refs = shot.get("refs", []) + [x for x in (shot.get("image"), shot.get("end_image")) if x]
        card = CARD.format(
            id=shot["id"], layer=shot.get("layer", "—"), frame=shot.get("frame", "—"),
            during=shot.get("during", "—"),
            window=f"{w[0]:.2f}–{w[1]:.2f}s ({prod.timing_source})" if w else "—",
            excerpt=prod.script_excerpt(shot.get("during")) or "—",
            model=shot.get("model", "—"), provider=m.get("provider", "?"),
            url=m.get("url", m.get("endpoint", m.get("model_id", ""))),
            params=", ".join(f"{k}={v}" for k, v in params.items()) or "—",
            refs=", ".join(refs) or "—", strengths=m.get("strengths", "—"), tips=m.get("tips", "—"),
            prompt=full_prompt(prod, shot))
        p = out_dir / f"{shot['id']}.md"
        p.write_text(card)
        print(p)


def cmd_run(a) -> None:
    prod = Production(a.production)
    shot = prod.shot(a.shot)
    models = (a.model or shot.get("model", "")).split(",")
    log = prod.root / "prompts" / f"{shot['id']}.log.jsonl"
    log.parent.mkdir(exist_ok=True)
    for name in filter(None, models):
        alias, m = resolve_model(name)
        prov = m["provider"]
        if prov == "manual":
            print(f"• {alias}: model thủ công — dùng `vgen cards` rồi dán prompt vào {m.get('url', 'app')}")
            continue
        if prov == "fal":
            req = build_payload(prod, shot, m)
            shown, target = preview(req), m["endpoint"]
        elif prov == "openai":
            req = openai_request(prod, shot, m)
            shown = preview(req["body"]) + (f"\n  + {len(req['files'])} ảnh tham chiếu (images/edits)" if req["files"] else "")
            target = f"openai:{m['model_id']}"
        elif prov == "byteplus":
            req = byteplus_request(prod, shot, m)
            shown = json.dumps({**req, "content": [{**c, **({"image_url": {"url": "data:…"}} if "image_url" in c else {})}
                                                   for c in req["content"]]}, ensure_ascii=False, indent=2)
            target = f"byteplus:{m['model_id']}"
        else:
            die(f"provider '{prov}' chưa hỗ trợ trong vgen")
        print(f"• {alias} → {target}" + ("" if m.get("verified") else "  (⚠ chưa đối chiếu đầy đủ — kiểm tra docs)"))
        if not a.yes:
            print(shown)
            print("  (chạy thử — thêm --yes để gọi thật; tiền tính theo bảng giá của provider)")
            continue
        out_dir = prod.root / "assets" / "gen" / shot["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        for i in range(a.n):
            stamp = datetime.now().strftime("%m%d-%H%M%S")
            files, rid = [], ""
            if prov == "fal":
                result, rid = run_fal(m["endpoint"], req, a.timeout)
                urls = output_urls(result, m.get("output", "images"))
                if not urls:
                    die(f"không thấy file kết quả trong phản hồi: {list(result)}")
                files = [download(u, out_dir / f"{alias}-{stamp}-{i}{k}") for k, u in enumerate(urls)]
            elif prov == "openai":
                fmt = req["body"].get("output_format", "png")
                for k, blob in enumerate(run_openai(req, a.timeout)):
                    f = out_dir / f"{alias}-{stamp}-{i}{k}.{fmt}"
                    f.write_bytes(blob)
                    files.append(f)
            else:
                url, rid = run_byteplus(req, m.get("base_url", "https://ark.ap-southeast.bytepluses.com/api/v3"), a.timeout)
                files = [download(url, out_dir / f"{alias}-{stamp}-{i}")]
            rels = [str(f.relative_to(prod.root)) for f in files]
            with log.open("a") as fh:
                fh.write(json.dumps({"time": stamp, "model": alias, "target": target, "request_id": rid,
                                     "prompt": full_prompt(prod, shot), "files": rels}, ensure_ascii=False) + "\n")
            for fp in rels:
                print(f"  ✓ {fp}")


def cmd_pick(a) -> None:
    prod = Production(a.production)
    shot = prod.shot(a.shot)
    if not shot.get("asset"):
        die(f"shot '{shot['id']}' chưa khai báo `asset` trong production.toml")
    src = (prod.root / a.file) if not Path(a.file).is_absolute() else Path(a.file)
    dst = prod.root / shot["asset"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)
    print(f"{src} → {dst}")


def main() -> None:
    p = argparse.ArgumentParser(prog="vgen", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models").set_defaults(fn=cmd_models)
    c = sub.add_parser("cards")
    c.add_argument("production")
    c.add_argument("--shot")
    c.set_defaults(fn=cmd_cards)
    r = sub.add_parser("run")
    r.add_argument("production")
    r.add_argument("--shot", required=True)
    r.add_argument("--model", help="ghi đè model; nhiều model cách nhau dấu phẩy để so sánh")
    r.add_argument("-n", type=int, default=1, help="số lần chạy mỗi model")
    r.add_argument("--yes", action="store_true", help="gọi API thật (tốn tiền)")
    r.add_argument("--timeout", type=int, default=900)
    r.set_defaults(fn=cmd_run)
    k = sub.add_parser("pick")
    k.add_argument("production")
    k.add_argument("--shot", required=True)
    k.add_argument("--file", required=True)
    k.set_defaults(fn=cmd_pick)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
