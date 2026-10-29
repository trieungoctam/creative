# Thẻ prompt · hero

| | |
|---|---|
| Lớp / khung | ref / — |
| Gắn vào | `—` → — |
| Lời đang nói | — |
| Model | **gpt-image** (openai) gpt-image-2.5-sunburst |
| Tham số | kind=image, aspect=9:16 |
| Tham chiếu | — |

**Vì sao model này:** OpenAI chính chủ, bản ưu tiên độ chính xác khi chỉnh sửa; chân dung kiểu điện thoại rất thật, chữ/UI chuẩn; images/edits nhận nhiều ảnh tham chiếu.

**Mẹo riêng:** Cấu trúc Capture / Person / Shot / Setting (docs/02). Kiểm tra model khả dụng: GET /v1/models.

## Prompt

```text
Vertical 9:16 frame from an iPhone front-camera video, natural available light, true-to-life skin
texture with visible pores, slight handheld framing, no studio lighting, no cinematic bokeh.

PERSON: A Vietnamese girl in her mid twenties, strikingly beautiful with the fresh, approachable
presence of a top V-pop idol; glossy shoulder-length black hair tucked behind one ear, dewy skin,
small gold hoops; very broad shoulders and excellent head-to-shoulder proportions.

SHOT: Close half-body view, she speaks to the camera like telling a close friend a secret, one hand
gesturing; face points straight toward the lens, no head tilt or rotation; sits slightly right,
a bathroom shelf on the left leaves room for a product card.

SETTING: A small Saigon apartment bathroom in the morning: terracotta tiles, a round mirror, a few
skincare bottles and a green potted pothos; warm terracotta and leaf-green palette.
```

## Chấm ứng viên (thang 14 điểm, docs/01)
| Ứng viên | Model | Điểm | Lỗi | Chốt? |
|---|---|---|---|---|
| | | | | |
