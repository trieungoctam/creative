# Lộ trình 6 tuần: từ người dùng tool đến người làm video có gu

Mỗi tuần gồm **học** (đọc doc), **làm** (bài tập ra sản phẩm) và **game** (rèn một kỹ năng riêng).
Mỗi tuần đều có một thứ đưa vào portfolio. Mục tiêu cuối: 6 video hoàn chỉnh và một quy trình riêng
mà bạn lặp lại được.

| Tuần | Học | Làm | Game | Đầu ra portfolio |
|---|---|---|---|---|
| 1 | `01` tư duy giao việc · `09` giải phẫu video | Mổ xẻ 5 video viral trong ngách của bạn bằng `vkit analyze` | **Đoán hook**: xem 1 giây đầu, đoán video bán gì, rồi đối chiếu | 5 file ANALYSIS + 1 "hook bank" 30 câu |
| 2 | `02` visual prompt | 1 nhân vật × 10 bối cảnh; 1 sản phẩm × 10 góc chụp | **Prompt mù**: người khác tả ảnh, bạn viết prompt; so độ khớp | Bộ ảnh nhân vật nhất quán (contact sheet) |
| 3 | `03` video prompt · `05` kiểm soát | Storyboard 6 shot → image-to-video từng shot | **Một ảnh, ba thái độ**: cùng ảnh, prompt 3 cảm xúc khác nhau | Clip 15s không dựng, chỉ ghép shot |
| 4 | `06` hậu kỳ | Dựng clip tuần 3 thành bản hoàn chỉnh: phụ đề, MG, nhạc, SFX | **Cắt 30%**: rút bản dựng ngắn đi 30% mà không mất ý | Video 20–30s đã QC |
| 5 | `07` thương mại | Quảng cáo sản phẩm thật: brief → 3 biến thể hook | **Đúng brief**: nhận brief ngẫu nhiên, nộp trong 90 phút | 3 biến thể quảng cáo + bảng so sánh |
| 6 | `08` AI Yourself · `04` workflow | Digital twin của bạn và một video talking-head dùng twin | **Clone có chủ đích**: clone 1 video viral, đổi người, sản phẩm và ngôn ngữ | Video cá nhân hóa + case study |

## Bốn game rèn kỹ năng (lặp lại bất cứ lúc nào)

1. **Kể chuyện trong 3 khung.** Chỉ được dùng 3 ảnh để kể mở đầu, biến cố và kết. Không được nói chữ
   nào. Nếu người xem không kể lại được câu chuyện thì làm lại.
2. **Nhất quán 10 cảnh.** Giữ nguyên một nhân vật qua 10 cảnh khác nhau. Chấm từng cảnh: mặt, tóc,
   trang phục, tỉ lệ cơ thể, mỗi tiêu chí 0–2 điểm. Mục tiêu ≥ 32/40.
3. **Brief roulette.** Bốc ngẫu nhiên sản phẩm, đối tượng, nền tảng và cảm xúc. Có 60 phút để ra
   BRIEF, TREATMENT và 1 khung hero.
4. **Mổ băng 0,1 giây.** Chọn một chuyển cảnh đẹp, chạy `vkit tile --every 0.1`, rồi viết lại bằng
   lời cái gì vào, đi đâu, nảy thế nào và ra khi nào. Sau đó dựng lại hiệu ứng đó.

## Thước đo tiến bộ

- **Gu**: chọn được ảnh tốt nhất trong 8 biến thể và giải thích được lý do bằng 3 tiêu chí cụ thể.
- **Kiểm soát**: số lần generate trung bình để ra 1 shot dùng được. Mục tiêu giảm từ ~10 xuống ≤ 3.
- **Tốc độ**: thời gian từ brief đến bản nháp đầu tiên.
- **Hiệu quả**: tỉ lệ giữ chân 3 giây và tỉ lệ xem hết, đo trên video đăng thật.
