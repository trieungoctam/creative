# Thẻ prompt · proof-card

| | |
|---|---|
| Lớp / khung | overlay / card-left |
| Gắn vào | `proof` → 3.49–6.16s (estimate) |
| Lời đang nói | Serum vitamin C 15% dùng ba ngày là thấy da sáng lên. |
| Model | **gpt-image-edit** (openai) gpt-image-2.5-sunburst |
| Tham số | kind=image, aspect=4:3 |
| Tham chiếu | assets/product.png |

**Vì sao model này:** OpenAI chính chủ, bản ưu tiên độ chính xác khi chỉnh sửa; chân dung kiểu điện thoại rất thật, chữ/UI chuẩn; images/edits nhận nhiều ảnh tham chiếu.

**Mẹo riêng:** Cấu trúc Capture / Person / Shot / Setting (docs/02). Kiểm tra model khả dụng: GET /v1/models.

## Prompt

```text
Image 1 is the product: keep the exact bottle shape, label and cap colour. Show it on a sunlit
bathroom shelf next to a small day-1 / day-3 split photo of the same cheek, clearly brighter on
day 3. Clean, honest UGC style, no extra text.
```

## Chấm ứng viên (thang 14 điểm, docs/01)
| Ứng viên | Model | Điểm | Lỗi | Chốt? |
|---|---|---|---|---|
| | | | | |
