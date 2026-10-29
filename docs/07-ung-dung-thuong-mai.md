# 07 · Ứng dụng thương mại

Năm dạng phổ biến nhất, mỗi dạng kèm cấu trúc, điểm kiểm soát và lỗi hay gặp.

## 1. Quảng cáo sản phẩm (product ad)

**Cấu trúc 20–30s:** hook (0–2s) → vấn đề (2–6s) → sản phẩm xuất hiện (6–9s) → 2–3 bằng chứng (9–22s) →
ưu đãi + CTA (22–30s).

- **Ảnh sản phẩm gốc là sự thật**: nhãn, màu nắp, chữ. Luôn nạp làm tham chiếu và kiểm tra từng khung.
  AI hay vẽ sai chữ trên nhãn, nên ghép packshot thật ở hậu kỳ nếu cần.
- Bằng chứng phải nhìn thấy được: texture, trước/sau, thao tác dùng, con số (bằng MG, không phải miệng nói suông).
- Hook mạnh hơn avatar. Nghiên cứu bạn trích (384 ads): avatar AI được +25% view nhưng -38% click.
  **Đầu tư vào hook và bằng chứng**, đừng chỉ mua avatar đẹp.

## 2. Thay trang phục / virtual try-on

- Ảnh người gốc giữ danh tính, ảnh sản phẩm thời trang giữ chất liệu, form, họa tiết.
- Prompt nói rõ phần **giữ**: mặt, tóc, dáng, bối cảnh. Phần **đổi**: chỉ trang phục.
- Kiểm tra: đường may, họa tiết lặp đúng, độ rủ vải theo dáng, tay chạm vải.
- Video: xoay người chậm 3–5s, khung đầu là ảnh try-on đã chốt.

## 3. Lookbook

- Một **thế giới thống nhất**: một capture, một bảng màu, 1–2 địa điểm. Nhiều outfit, cùng người mẫu.
- Dựng theo nhịp nhạc: mỗi outfit 1–2 beat, chuyển cảnh khớp chuyển động (match cut) hoặc whip pan.
- Thứ tự outfit kể một câu chuyện: sáng → tối, công sở → tiệc, nhạt → đậm.

## 4. TVC (phim quảng cáo kể chuyện)

- Bắt đầu từ **một ý tưởng một câu** và một cảm xúc chủ đạo.
- Storyboard đầy đủ trước khi generate. Dùng khung đầu–cuối cho các cú chuyển then chốt.
- Nhân vật và địa điểm cần **bible** (xem `08`, `templates/CHARACTER.md`).
- Âm thanh làm nửa cảm xúc: nhạc gốc hoặc nhạc có license, sound design chi tiết, voice-over được chỉ đạo.

## 5. Video UGC (người dùng review)

- Cảm giác **quay bằng điện thoại thật**: capture UGC (xem `02`), ánh sáng có sẵn, khung hơi lệch,
  jump cut.
- Người dẫn có **thái độ rõ với sản phẩm** (hào hứng khoe, hoài nghi rồi bị thuyết phục, chê yêu).
- Định dạng hay thắng: talking-head, "3 lý do", so sánh, unboxing, POV, podcast giả, phỏng vấn đường phố.
- Lặp nhanh: **giữ thân, thay hook**. Một video có thể ra 10–50 biến thể mở đầu.

## Nhãn AI và tuân thủ (bắt buộc phải biết)

- TikTok, Meta, YouTube yêu cầu **gắn nhãn nội dung AI chân thực**, nhất là người tạo bởi AI. Bật nhãn
  trong app khi đăng, và nên ghép nhãn lên hình (`vkit finish --label`).
- **FTC (Mỹ)**: không để avatar AI đóng vai *khách hàng thật* đưa lời chứng thực. EU AI Act và luật bang
  New York có yêu cầu minh bạch tương tự. Kiểm tra pháp lý cho từng thị trường trước khi chạy ads.
- Không dùng mặt hay giọng người thật khi chưa có đồng ý bằng văn bản. Không dùng logo hay nhân vật có
  bản quyền.
- Claim sản phẩm (hiệu quả, y tế) phải có căn cứ, AI không miễn trừ trách nhiệm quảng cáo sai.

## Ma trận biến thể để test (cho team affiliate)

| | Hook A: nỗi đau | Hook B: kết quả | Hook C: phản biện |
|---|---|---|---|
| Người dẫn 1 | v01 | v02 | v03 |
| Người dẫn 2 | v04 | v05 | v06 |

Chỉ đổi **một biến mỗi trục** và giữ thân + CTA cố định. Đo giữ chân 3 giây cho hook, CTR cho CTA.
Ghi kết quả vào `templates/HOOK-BANK.md`.
