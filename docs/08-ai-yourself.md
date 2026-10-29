# 08 · AI Yourself: số hóa bản thân, nhân vật và phong cách cá nhân

Mục tiêu: một **digital twin** (bản sao số) đủ giống để làm talking-head, B-roll lifestyle và quảng cáo
mà không phải quay mỗi ngày. Thêm một **phong cách cá nhân** để người xem nhận ra bạn.

## 1. Bộ dữ liệu gốc (chụp một lần, dùng mãi)

| Loại | Số lượng | Yêu cầu |
|---|---|---|
| Ảnh mặt | 15–25 | Chính diện, 3/4 trái/phải, nghiêng; ánh sáng tự nhiên; không filter; vài biểu cảm |
| Ảnh nửa người / toàn thân | 8–12 | Trang phục "đặc trưng" của bạn; tư thế quen thuộc |
| Video nói | 2–5 phút | Nhìn thẳng máy, ánh sáng đều, nền gọn; nói tự nhiên như khi làm content |
| Mẫu giọng | 1–3 phút sạch | Phòng yên tĩnh, mic gần, đúng giọng khi làm video (không đọc như đọc tin) |

Lưu ở `assets/me/` và **không commit lên repo công khai**.

## 2. Ba con đường số hóa

| Đường | Công cụ ví dụ | Hợp với |
|---|---|---|
| **Avatar nói (lip-sync từ video của bạn)** | HeyGen digital twin, Arcads, TopView | Talking-head số lượng lớn, đa ngôn ngữ |
| **Ảnh tham chiếu → ảnh/video mới** | GPT Image 2, Nano Banana, Seedream + Seedance/Kling/Veo theo tham chiếu | B-roll lifestyle, cảnh mới, thay trang phục |
| **Fine-tune / LoRA nhân vật** | Flux LoRA, ComfyUI | Kiểm soát cao nhất, cần máy hoặc dịch vụ train |

Gợi ý bắt đầu: con đường 2 (rẻ, linh hoạt), cộng một avatar nói khi cần sản lượng.

## 3. Character bible

Điền `templates/CHARACTER.md` cho bạn hoặc cho nhân vật thương hiệu:
- **Danh tính nhìn thấy**: khuôn mặt (ảnh neo), tóc, 2–3 chi tiết nhận diện (kính, khuyên tai, kiểu mũ).
- **Tủ đồ**: 3–5 outfit đặc trưng, kèm ảnh.
- **Thế giới**: 2–3 bối cảnh quen thuộc (bàn làm việc, quán cà phê, xe máy) với bảng màu.
- **Giọng nói**: một đoạn mô tả ngắn và một file mẫu giọng.
- **Thái độ**: bạn đối với người xem là gì? Người anh trải nghiệm, đứa bạn thân nói thẳng, chuyên gia
  bình tĩnh?
- **Những thứ không bao giờ làm**: kiểu nói, trang phục, chủ đề tránh.

## 4. Chỉ đạo giọng nói

Tóm lược từ `voice-direction.md` của hypit:
- **Cast một giọng người ta muốn nghe tiếp**. Chọn chất giọng cụ thể (cao/thấp, sáng/ấm, trong/khàn),
  không chỉ viết "giọng hay".
- **Nén thành một đoạn mô tả sống động**: tính cách giọng, phẩm chất âm thanh, cách nói với người khác.
  Ví dụ:
  ```text
  Giọng nữ trẻ miền Nam, trong và sáng, âm vực trên tươi; nói nhanh, tinh nghịch, như đứa bạn thân
  háo hức kể món mới tìm được. Câu hỏi thì lên giọng tò mò, câu trả lời có nụ cười trong giọng.
  ```
- **Mẫu giọng nên dùng đúng ngôn ngữ và kiểu nói của video đích**. Mẫu tiếng Anh không tự chuyển thành
  giọng tiếng Việt tự nhiên.
- **Một giọng, nhiều thái độ**: cùng danh tính giọng nhưng mỗi đoạn có lý do nói riêng (kéo vào, phản
  biện, thích thú, chốt).
- Tiếng Việt: kiểm tra kỹ dấu, tên riêng và từ mượn. Viết cách đọc vào kịch bản nếu TTS hay đọc sai
  ("TikTok" → "tíc tóc").

## 5. Phong cách cá nhân (signature)

Chọn và **giữ cố định** 3–5 yếu tố để người xem nhận ra bạn sau 1 giây:
- Một khung mở đầu quen thuộc (câu chào, góc máy, động tác).
- Một kiểu phụ đề (font, màu nhấn duy nhất). Reel mẫu dùng vàng `#FFE14D` trên chữ trắng.
- Một yếu tố đồ họa lặp lại (danh sách đánh số, khung điện thoại, sticker).
- Một âm thanh đặc trưng (SFX chuyển cảnh, nhạc nền chủ đề).
- Một bảng màu bối cảnh.

## 6. Đạo đức và an toàn

- Chỉ số hóa người đã đồng ý bằng văn bản, kể cả nhân viên hay người thân.
- Gắn nhãn AI khi twin xuất hiện trong nội dung chân thực (xem `07`).
- Bảo mật dữ liệu gốc: ai có ảnh và giọng của bạn là có thể giả bạn.
