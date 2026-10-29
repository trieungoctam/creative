# Thẻ prompt · aroll-hook

| | |
|---|---|
| Lớp / khung | aroll / — |
| Gắn vào | `segment:hook` → 0.00–3.19s (estimate) |
| Lời đang nói | Da xỉn màu dù đã skincare đủ bước? Lỗi nằm ở bước này. |
| Model | **seedance** (byteplus) dreamina-seedance-2-0-260128 |
| Tham số | kind=video, aspect=9:16, resolution=720p, duration (ước lượng)=5s |
| Tham chiếu | shot:hero |

**Vì sao model này:** Seedance 2.0 chính chủ (ByteDance): khung đầu/cuối, tối đa 9 ảnh + 3 video + 3 audio tham chiếu (omni), 480p–4K, âm thanh gốc.

**Mẹo riêng:** image = khung đầu, end_image = khung cuối, refs = ảnh tham chiếu (nhân vật, sản phẩm), ref_videos = URL video chuyển động mẫu.

## Prompt

```text
She is confiding in a close friend, half-annoyed, half-amused at how her skin still looks dull.
On "dù đã skincare đủ bước" she lifts her eyebrows in disbelief; she lands "bước này" with a
knowing look into the lens. Fixed eye-level camera, framing as in the image; jump cut at the pause.
No on-screen text, no outfit change.

Dialogue:
HOST: Da xỉn màu dù đã skincare đủ bước? Lỗi nằm ở bước này.
```

## Chấm ứng viên (thang 14 điểm, docs/01)
| Ứng viên | Model | Điểm | Lỗi | Chốt? |
|---|---|---|---|---|
| | | | | |
