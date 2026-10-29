---
name: len-brief
description: Biến một ý tưởng hoặc yêu cầu video thành BRIEF.md, TREATMENT.md, kịch bản neo theo từ script.vs và bảng shot production.toml cho một dự án trong projects/, rồi dựng storyboard + animatic để duyệt nhịp. Dùng khi người dùng mô tả video muốn làm ("quảng cáo serum 25s", "làm lại reel này cho sản phẩm của tôi").
---

# Lên brief → treatment → storyboard

Đọc `docs/04-workflow-san-xuat.md`; với quảng cáo thì thêm `docs/07-ung-dung-thuong-mai.md`.

1. **Dự án**: `python3 scripts/vkit.py new <ten>` nếu chưa có.
2. **BRIEF** (mục tiêu của người dùng): điền từ yêu cầu, giữ nguyên câu chữ quan trọng của họ. Chỉ hỏi
   khi thiếu những thứ chỉ họ biết: sự thật sản phẩm, CTA, ngân sách/dịch vụ được tiêu tiền, mặt/giọng
   người thật, deadline. Casting, art direction, shot, phụ đề là việc của bạn, không cần hỏi.
   Có video tham chiếu thì những gì không nhắc tới mặc định kế thừa *quan hệ* từ tham chiếu (không phải pixel).
3. **TREATMENT** (đáp án của đạo diễn): premise, mạch hook → thân → payoff → CTA kèm thời lượng, nhân
   vật và thái độ, thế giới hình ảnh, chỉ những hệ thống hình/âm thực sự cần, và ảnh neo nhất quán.
   Viết bằng ngôn ngữ đạo diễn, không ghi tên tool.
4. **Kịch bản `script.vs`** (đọc `docs/13`): chia Segment theo đoạn diễn (thường = một take), vai `<HOST>`,
   `||` ở chỗ ngắt phụ đề, `chữ{emphasis}` cho từ nhấn, `<hiển thị|cách đọc>` cho tên riêng và số mà TTS dễ đọc
   sai. Đánh dấu `@{ten}…@{/ten}` ở mọi chỗ hình hoặc âm phải bám theo, `@{ten!}` cho điểm reveal.
   Chạy `python3 scripts/vscript.py check` cho tới khi sạch lỗi.
5. **`production.toml`**: mỗi shot có `during` = tên vùng nghĩa, `layer`/`frame`, model logic (`gpt-image`,
   `seedance`...), prompt (viết theo skill `viet-prompt`). Mỗi shot trả lời 5 câu ở `docs/05`: phục vụ ý nào,
   mắt nhìn đâu trước, tham chiếu gì, quan hệ sinh nào, vào/ra thế nào. Thêm `[music]` và `[[sfx]]` gắn Moment.
6. Chạy `storyboard.py board` và `storyboard.py animatic` (mốc ước lượng) để người dùng duyệt nhịp **trước
   khi tốn tiền**. Gửi storyboard.html hoặc animatic cho họ xem.
7. **Ước lượng thời lượng** theo lời (`vscript.py estimate`): tiếng Việt ~4–5 âm tiết/giây khi nói nhanh kiểu mạng xã hội,
   tiếng Anh ~170–190 từ/phút. Cộng thêm thời gian cho phản ứng.
8. Đề xuất **3 hook** khác kiểu (xem `templates/HOOK-BANK.md`), giữ thân + CTA cố định để test.
9. Trình bày cho người dùng: premise một câu, bảng mạch, 3 hook, và các câu hỏi thật sự cần họ quyết.
