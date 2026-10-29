# 14 · Pipeline đa model, đa tool: ảnh, video, âm thanh, storyboard, dựng

```
 script.vs ─────────────┐
 (lời + vùng nghĩa)     │
                        ▼
 production.toml ── vgen.py ───► ảnh/video   (OpenAI · BytePlus Seedance · fal: Kling/Veo/Nano Banana · thủ công: Higgsfield/Midjourney)
 (shot gắn vào     ├─ vaudio.py ─► giọng/SFX/nhạc (ElevenLabs)
  vùng nghĩa)      │                  │
                   │     vscript.py align  ◄── video/giọng đã chốt
                   │                  │
                   └─ storyboard.py ──┼──► storyboard.html  (duyệt, in PDF)
                                      ├──► animatic.mp4     (dựng thô: đúng mốc, phụ đề, nhạc duck, SFX)
                                      ├──► .xml             Premiere Pro · DaVinci Resolve · FCP7
                                      ├──► .srt / .csv      CapCut · mọi NLE · YouTube
                                      ├──► hyperframes/     HTML → MP4 (MG, phụ đề động)
                                      └──► timeline.json    Remotion / script riêng
                                               │
                                     vkit.py finish ──► bản đăng (9:16, -14 LUFS, nhãn AI)
```

## 1. Nguyên tắc chọn nhà cung cấp: chính chủ trước

| Loại | Ưu tiên 1 (chính chủ) | Dự phòng | Ghi chú (đối chiếu 29/10/2026) |
|---|---|---|---|
| Ảnh | **OpenAI** `gpt-image-2.5-sunburst` (chính xác), `-flare` (nhanh) | fal `openai/gpt-image-2` | images/edits nhận nhiều ảnh tham chiếu, size tùy ý (bội số 16) |
| Ảnh sửa / giữ danh tính | OpenAI images/edits | fal Nano Banana Pro edit | |
| Video A-roll / UGC | **BytePlus ModelArk Seedance 2.0** | fal `bytedance/seedance-2.0` | khung đầu/cuối, tối đa 9 ảnh + 3 video + 3 audio tham chiếu, 4–15s, 480p–4K |
| Video chuyển động máy | Kling O3 (fal) / Kling app | | 3–15s, multi-shot |
| Video điện ảnh | Veo 3.1 (fal) | | 4/6/8s, chỉ 16:9 hoặc 9:16; endpoint fal báo ngừng 17/11/2026 |
| Giọng đọc | **ElevenLabs** `eleven_v4` | `eleven_v3` (biểu cảm), `eleven_flash_v2_5` (nhanh) | **`eleven_multilingual_v2` không có tiếng Việt** |
| SFX · nhạc | **ElevenLabs** sound-generation · music | thư viện có license | |
| Nhiều model một chỗ | Higgsfield (thủ công / MCP) | | credit; unlimited chỉ trên web |

**Không còn Sora**: OpenAI đã tắt Sora 2 và Videos API từ 24/09/2026.

Trong `production.toml`, ghi **model logic** (`gpt-image`, `seedance`, `kling`, `veo`, `nano-banana`...).
`vgen` đọc bảng `[prefer]` trong `config/models.toml` và chọn tuyến đầu tiên bạn đã có key:

```bash
export OPENAI_API_KEY=...      # ảnh OpenAI
export ARK_API_KEY=...         # BytePlus ModelArk (Seedance chính chủ)
export FAL_KEY=...             # fal.ai — dự phòng, một key cho nhiều model
export ELEVENLABS_API_KEY=...  # giọng, SFX, nhạc
python3 scripts/vgen.py models # xem model logic nào đang đi tuyến nào
```

## 2. Chọn model theo loại shot

| Shot | Model logic gợi ý | Vì sao |
|---|---|---|
| Ảnh hero người dẫn (UGC điện thoại) | `gpt-image` | casting, da thật, cấu trúc 4 đoạn |
| Biến thể casting nhanh | `gpt-image-fast` | rẻ, nhanh, cho vòng 1–2 |
| Góc nhìn mới cùng thế giới / cầm sản phẩm | `gpt-image-edit`, `nano-banana-edit` | giữ danh tính / sản phẩm từ tham chiếu |
| B-roll minh họa, poster, chữ trên ảnh | `nano-banana`, `gpt-image` | chữ chuẩn, nhiều tỉ lệ |
| Talking-head có thoại | `seedance` (image = hero, dialogue = segment) | diễn xuất, jump cut, âm thanh gốc |
| Chuyển động thân / máy (orbit, dolly) | `kling` | vật lý, chuyển động máy |
| Cảnh điện ảnh, ánh sáng đẹp | `veo` | chất phim |
| Chuyển chuyển động từ video mẫu | Higgsfield Genjutsu / Seedance omni (`ref_videos`) | "chuyển giao tham chiếu" (docs/03) |

**So sánh nhiều model trên cùng một shot**, rồi chấm điểm và chốt:

```bash
python3 scripts/vgen.py run production.toml --shot hero --model gpt-image,nano-banana -n 2         # chạy thử: in payload
python3 scripts/vgen.py run production.toml --shot hero --model gpt-image,nano-banana -n 2 --yes   # gọi thật
python3 scripts/storyboard.py board production.toml      # storyboard hiện dải ứng viên của từng shot
python3 scripts/vgen.py pick production.toml --shot hero --file assets/gen/hero/openai-image-1029-101500-00.png
```

Model thủ công (Higgsfield, Midjourney, Kling app): `vgen cards` viết `prompts/<shot>.md` (prompt, tham số,
lời thoại đúng đoạn, bảng chấm). Dán vào app, tải kết quả về `assets/gen/<shot>/`, rồi `vgen pick`.

## 3. Âm thanh với ElevenLabs

```bash
python3 scripts/vaudio.py design production.toml --role HOST \
  --description "Giọng nữ trẻ miền Nam, trong và sáng, nói nhanh tinh nghịch như bạn thân khoe món mới" --yes
python3 scripts/vaudio.py save production.toml --role HOST --preview 2 --name "Host Linh" --yes   # → voice_id
# thêm vào production.toml:  [voices]  HOST = "<voice_id>"
python3 scripts/vaudio.py tts production.toml --yes        # assets/vo/<segment>.mp3 + mốc từng từ
python3 scripts/vscript.py align script.vs --media hook=assets/vo/hook.mp3 --media body=assets/vo/body.mp3 ...
python3 scripts/vaudio.py sfx production.toml --yes        # SFX gắn Moment/Selection
python3 scripts/vaudio.py music production.toml --yes      # nhạc nền đúng độ dài video
```

- TTS dùng **vế đọc** của Dual Text (`<TikTok|tíc tóc>`), nên phát âm đúng mà phụ đề vẫn ghi đúng chính tả.
- Mỗi Segment gửi kèm `previous_text` để ngữ điệu liền mạch giữa các đoạn.
- Mốc ký tự ElevenLabs trả về được ghi thành `<file>.transcript.json`, nên `vscript align` không cần Whisper.
- Animatic tự **duck** nhạc dưới giọng (sidechain) và đặt SFX đúng Moment.
- Video A-roll do Seedance/Veo sinh đã có tiếng thì giọng lấy từ video. VO chỉ dùng cho Segment không
  có video, hoặc khi bạn muốn thay tiếng (lồng tiếng lại rồi `align` lại).

## 4. Storyboard và animatic

```bash
python3 scripts/storyboard.py board    production.toml   # storyboard.html: kịch bản tô vùng nghĩa + thẻ shot
python3 scripts/storyboard.py animatic production.toml   # output/animatic.mp4
```

- **Trước khi có A-roll**: mốc thời gian **ước lượng** theo tốc độ nói (vi 4,5 âm tiết/s, en 3 từ/s).
  Animatic dùng ảnh hero làm nền, shot chưa có hình hiện thành **khung vàng giữ chỗ có tên**. Đây là
  animatic đúng nghĩa để duyệt nhịp trước khi tốn tiền generate.
- **Sau khi có A-roll / VO**: chạy `vscript align`, mọi thứ tự bám mốc thật.

## 5. Dựng ở tool nào cũng được

| Tool | Nhập gì | Lệnh |
|---|---|---|
| **Premiere Pro** | File → Import → `.xml` (FCP7 XML): A-roll V1, B-roll V2, overlay V3, giọng/nhạc/SFX A1–A3, marker cho mọi Selection/Moment | `storyboard.py export --to xml` |
| **DaVinci Resolve** | File → Import → Timeline → `.xml` (như trên); phụ đề: import `.srt` | `--to xml`, `--to srt` |
| **CapCut** | Không nhập XML: dùng `animatic.mp4` làm track tham chiếu, nhập `.srt` (Text → Import captions), đặt B-roll theo `.csv` | `--to srt`, `--to csv` |
| **HyperFrames** | Project HTML có sẵn A-roll + B-roll + overlay đúng mốc (media chép vào `assets/`) | `--to hf` → `npx hyperframes check --json` → `preview` |
| **Remotion** | `timeline.json` (tracks, markers, captions) → map vào `<Sequence from={start*fps}>` | `--to json` |
| **After Effects** | Nhập XML qua Premiere (Dynamic Link) hoặc dùng `.csv` để đặt marker | |

⚠ Các file XML và HyperFrames được sinh theo đặc tả, nhưng chưa thử import vào Premiere, Resolve hay
render HyperFrames trong môi trường dựng kit. Lần đầu dùng, hãy kiểm tra đường dẫn media và mốc.

Bước cuối luôn là `vkit.py finish` (9:16, -14 LUFS, nhãn AI), rồi QC (`/qc-video`).
