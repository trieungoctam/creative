# 09 · Giải phẫu video viral

Mục tiêu không phải "chép lại". Mục tiêu là **hiểu vì sao nó giữ được người xem** rồi mang những quan hệ
đó vào video của bạn. Phương pháp này tóm lược từ `creation/reference-video.md` của hypit.

## Quy trình 5 bước

### 1. Lấy bằng chứng

```bash
python3 scripts/vkit.py fetch "<link>" --out projects/<du-an>/references/<ten-ref>
python3 scripts/vkit.py analyze projects/<du-an>/references/<ten-ref>/source.mp4 --language en
```

Bạn nhận được: `summary.json` (thời lượng, số shot, độ dài shot trung bình, LUFS, số từ/phút, hook 0–3s),
`transcript.json` có mốc thời gian từng từ, `evidence/overview.jpg` (toàn bài) và `evidence/hook_0-3s.jpg`
(mỗi 0,25s).

### 2. Xem cả bài, hiểu cả bài

Xem từ đầu đến cuối, rồi trả lời:
- Video muốn người xem **cảm / biết / làm** gì?
- Hook, lập luận hay câu chuyện, payoff, CTA nằm ở đâu?
- **Ai** gánh phần diễn (A-roll)? Hình minh họa đóng góp gì?
- Có những **hệ thống** nào xuất hiện lặp lại hoặc kéo dài: phụ đề, MG, chữ, hiệu ứng, âm thanh?

Viết một giải thích tạm thời vào `ANALYSIS.md`.

### 3. Soi chi tiết theo câu hỏi

Mỗi thành phần được thiết kế cần một mô tả gồm: **nội dung và ngoại hình, vị trí, cách vào, hành vi khi
đang hiện, thời gian tồn tại, cách ra**, và nó gắn với chữ hoặc hành động nào.

```bash
# Toàn cảnh một đoạn, mỗi 1s
python3 scripts/vkit.py tile source.mp4 --start 0 --end 12 --every 1
# Soi một chuyển cảnh, mỗi 0,1s, phóng to vùng giữa
python3 scripts/vkit.py tile source.mp4 --start 6.8 --end 8.4 --every 0.1 --crop 540:960:270:480
```

Đổi phạm vi, mật độ lấy mẫu và kích thước ô theo câu hỏi đang hỏi. Lưu ý: **khoảng giữa các mẫu là vùng
mù**. Một sự kiện ngắn có thể nằm lọt giữa hai khung trông giống hệt nhau.

Tên hiệu ứng (zoom, slide) chỉ là điểm bắt đầu. Hãy soi đường đi, thay đổi cỡ/độ mờ, tốc độ, độ nảy,
cách lắng lại và quan hệ với sự kiện bên cạnh.

### 4. Ghi lại thành hai lớp

- **ANALYSIS.md** là mô hình cả bài: mục tiêu, nhịp, từng hệ thống làm gì, thứ gì lặp lại.
  **Tách sự thật quan sát được khỏi diễn giải của bạn.**
- **TIMELINE.md** chia theo đoạn thời gian và pha có nghĩa, ví dụ `## 6.07–8.27 · Khối lượng việc tăng
  tốc`. Mỗi đoạn nối vật thể đang hoạt động với chữ hoặc hành động nó phục vụ, đủ cụ thể để dựng lại.

### 5. Chuyển hiểu biết thành chỉ đạo mới

Cho mỗi quan hệ quan trọng, hỏi: **giữ, đổi hay bỏ** khi đổi người, sản phẩm, ngôn ngữ?
- Giữ quan hệ, không giữ pixel. Ví dụ: "reveal rơi đúng chữ trả lời", "danh sách tô sáng mục đang nói".
- Thời lượng của video mới do **màn trình diễn mới** quyết định, không do số giây của bản gốc.

## Checklist câu hỏi khi xem

**Hook (0–3s)**
- [ ] Từ đầu tiên nói ở giây thứ mấy? (reel mẫu: 0,0s)
- [ ] Khung đầu tiên có chữ không? Chữ hứa hẹn gì?
- [ ] Có "vòng lặp mở" (danh sách, câu hỏi, đếm ngược) khiến người xem muốn xem đến cuối không?

**Nhịp**
- [ ] Độ dài shot trung bình? Có tăng tốc ở đoạn nào không?
- [ ] Bao nhiêu từ/phút? Có khoảng lặng không?

**Hệ thống hình**
- [ ] Phụ đề: font, màu, nhấn từ, vị trí, cách gom cụm?
- [ ] MG/chữ đồ họa: cái gì tồn tại suốt, cái gì thay mỗi nhịp?
- [ ] B-roll: khớp chính xác hay minh họa ý?
- [ ] Bảng màu, số màu nhấn?

**Âm thanh**
- [ ] Nhạc nền? Ducking? SFX ở sự kiện nào?

**Chuyển đổi**
- [ ] CTA là gì, ở đâu, cơ chế gì (comment từ khóa, link bio, giỏ hàng)?
- [ ] Caption bài đăng làm gì để kéo tương tác?
- [ ] Tỉ lệ comment/like? (cao bất thường thì thường là do cơ chế comment để nhận quà)

## Ví dụ đã làm

`examples/tenfoldmarc-17-effects/` là ca mổ xẻ đầy đủ reel "17 video effects claude can create" của
@tenfoldmarc, gồm ANALYSIS.md và TIMELINE.md.
