---
name: viet-prompt
description: Viết prompt ảnh (hero, nhân vật, sản phẩm, B-roll) hoặc prompt video (talking-head, hành động, chuyển động máy) theo phương pháp đạo diễn của kit, kèm kế hoạch biến thể và bảng chấm điểm. Dùng khi người dùng cần prompt cho Midjourney/GPT Image/Nano Banana/Seedance/Kling/Veo/Higgsfield.
---

# Viết prompt như đạo diễn

**Prompt ảnh: đọc `docs/02-visual-prompt.md`. Prompt video: đọc `docs/03-video-prompt.md`.**
Dự án có CHARACTER/TREATMENT thì đọc trước để giữ nhất quán.

## Ảnh
1. Xác định ảnh sẽ trở thành gì: hero toàn màn, inset, khung đầu video, hay tham chiếu danh tính.
2. Viết 4 đoạn **Capture / Person / Shot / Setting**. Dồn chữ vào vài quyết định quan trọng:
   casting có cường độ và kiểu sức hút, tuổi thật, 2–3 neo ngoại hình, trạng thái idle (đang làm gì
   đó), khung hình chừa chỗ bằng vật thật, bối cảnh có vài chi tiết kể chuyện, bảng màu gắn vào vật.
3. Ghi rõ vai trò từng ảnh tham chiếu. Tỉ lệ khung và độ phân giải là tham số, không viết vào prompt.
4. Viết prompt bằng **tiếng Anh** (model hiểu tốt hơn), giải thích cho người dùng bằng tiếng Việt.

## Video
1. Chọn quan hệ sinh: theo tham chiếu (mặc định), khung đầu–cuối (khi điểm đến là nội dung), hoặc text.
2. Câu đầu: **thái độ** của người diễn với chủ đề và người nghe. Sau đó 1–2 chỗ nhấn nhìn thấy được.
   Không biên đạo từng câu.
3. Hành động bám vào cảnh có thật. Con số, chữ, biểu đồ để MG lo. Tránh ẩn dụ dễ bị hiểu theo nghĩa đen.
4. Bảng đầu vào theo `templates/PROMPT-VIDEO.md`, ước lượng thời lượng từ lời thoại.

## Chọn model (docs/14)
Ghi **model logic** vào shot trong `production.toml`: `gpt-image` (hero, casting), `gpt-image-edit` /
`nano-banana-edit` (giữ danh tính, cầm sản phẩm), `nano-banana` (B-roll, chữ trên ảnh), `seedance`
(talking-head có thoại: `image = "shot:hero"`, `dialogue = "<segment>"`), `kling` (chuyển động máy),
`veo` (điện ảnh). Kit ưu tiên nhà cung cấp chính chủ (OpenAI, BytePlus) trước fal.ai.
Muốn so sánh thì đề xuất `vgen run --model a,b -n 2` (chạy thử trước, `--yes` khi người dùng duyệt chi phí).

## Luôn kèm
- **Kế hoạch biến thể**: mỗi vòng chỉ đổi một biến (người → cú máy → thế giới → chi tiết).
- **Tiêu chí chấm** (thang 14 điểm ở `docs/01`) và các lỗi cần soi riêng với loại shot này.
- Ghi prompt vào shot tương ứng trong `production.toml`, rồi `vgen cards` để sinh thẻ prompt
  `prompts/<shot>.md` (dùng được cho cả app thủ công như Higgsfield hay Midjourney).
