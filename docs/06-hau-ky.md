# 06 · Hậu kỳ: nơi video AI thành video có gu

Generate ra vật liệu. Dựng mới ra tác phẩm. Phần này tổng hợp kinh nghiệm dựng video ngắn với các
playbook phụ đề, motion graphics, B-roll và âm thanh của hypit.

## Thứ tự dựng khuyến nghị

1. **Ráp A-roll theo lời** (phần diễn chính: người nói / giọng dẫn). Lời quyết định thời gian.
2. **Cắt khoảng lặng và chữ thừa** ở ranh giới cụm từ (jump cut). Mục tiêu: không có giây nào chết.
3. **Phủ B-roll** lên ý cần minh họa. Tiếng A-roll vẫn chạy bên dưới.
4. **Phụ đề**, theo nhịp đọc chứ không chép máy móc transcript.
5. **MG / chữ đồ họa** gắn với đúng từ khóa (reveal rơi đúng chữ).
6. **Âm thanh**: nhạc, SFX gắn sự kiện, ducking dưới lời.
7. **Màu**: đồng bộ tông giữa các shot AI.
8. **Xuất**: `vkit finish` (khung hình, -14 LUFS, nhãn AI).

## Phụ đề

- **Phụ đề hiển thị lời nói đang được nói.** Tiêu đề giữ trên màn hình lâu sau câu nói là Typography,
  không phải phụ đề. Phân biệt hai vai trò này để dàn trang.
- **Gom cụm theo nghĩa**, không đếm từ cố định. Không tách: tên riêng, phủ định, số + đơn vị, động từ
  + tân ngữ ngắn. Tiếng Việt: giữ trọn từ ghép ("điện thoại", "khóa học") và cụm danh từ.
- **Punchline thì cho cụm riêng** để nó "rơi" đúng lúc.
- **Kiểu nhấn**: giữ cả cụm cố định và đổi màu từ đang nói (karaoke `current`), hoặc giữ màu các từ
  đã nói (`trail`), hoặc pop cả cụm. Chọn theo nhịp xem mong muốn.
- **Hiển thị và nhấn là hai lựa chọn riêng**: cả cụm hiện sẵn để đọc, còn màu chạy theo lời.
- Chọn font, cỡ, viền, bóng đổ dựa trên **kích thước xem thật trên điện thoại**. Viền đậm hợp giọng
  năng lượng cao, bóng gọn hợp giọng nhẹ.
- Vùng an toàn TikTok/Reels: tránh ~15% trên cùng, ~25–30% dưới cùng (chỗ caption và nút) và ~12% mép phải.

`vkit captions` sinh sẵn file `.ass` karaoke (mặc định chữ trắng, từ đang nói vàng và phóng 108%),
kèm `.srt` để nhập vào CapCut/Premiere.

## Motion graphics: chỉ đạo *sự thay đổi*, không chỉ màn xuất hiện

- Hỏi: trước sự kiện người xem thấy gì, cái gì thay đổi, **sau đó còn lại gì**. Một màn vào đẹp không
  cứu được trạng thái cuối không thể hiện được luận điểm.
- **Giữ danh tính vật thể** qua các thay đổi. Cùng một cái thẻ biến thành file đính kèm thì giữ hình
  và quỹ đạo, để người xem hiểu *cái gì* đã đổi. Cắt thẳng cũng là một cách chuyển tốt khi ý sau dễ
  hiểu ngay.
- **Tính cách chuyển động là cảm xúc**: nảy lò xo thì vui, thay cứng đột ngột thì mạnh, dựng chậm và
  chính xác thì dễ học.
- **Một ngôn ngữ hình ảnh**: bảng màu, kiểu chữ, cạnh, texture, chiều sâu, chuyển động và âm thanh
  cùng nói một giọng.
- **Chuyển động liên quan suy ra từ quan hệ**: con trỏ đến đúng nút nó bấm, nhãn đi theo vật nó gắn.
- Kiểm tra ở **kích thước xuất** và cả khoảnh khắc *ngay sau* chuyển động ấn tượng nhất.

### Bố cục đồ họa

- Quyết định mắt tìm **cái gì trước**, cái gì đỡ phía sau, cái gì đổi ở nhịp tiếp theo. Dùng cỡ, khoảng
  cách, nhóm, tương phản, màu và chuyển động để thể hiện thứ bậc đó.
- **Phối cả khung**: người dẫn lệch để chừa chỗ cho bảng; *một* màu nhấn nối phụ đề, icon và cú reveal
  (reel mẫu chỉ dùng một màu vàng duy nhất).
- Bảo vệ miệng, cử chỉ quan trọng, chi tiết sản phẩm và dòng chữ đang gánh nhịp hiện tại.
- Cẩn thận: mảng panel nhạt đặt sau áo nhạt sẽ làm khung hình bẹt.

## B-roll: cho vật liệu một lý do để xuất hiện

| Quan hệ với lời | Khi dùng | Ví dụ |
|---|---|---|
| **Khớp chính xác** | Ý nghĩa phụ thuộc vào việc thấy đúng hình ở đúng lúc | "Nhìn nè, 3 ngày là thấy da sáng" → cận da thật |
| **Một ý qua nhiều hình** | Kể thói quen, quá trình, thái độ | "Mỗi sáng tôi…" → 3–4 cảnh sinh hoạt theo nhịp nhạc |

- Một hình chọn đúng có thể gánh cả ý **tốt hơn** một shot mới cho mỗi danh từ.
- B-roll có thể chiếm toàn khung trong khi tiếng A-roll vẫn tiếp tục, hoặc nằm trong khung, mặt nạ hay
  viền (kiểu "phone mockup" trong reel mẫu).
- Tiếng gốc của B-roll (cửa đóng, tiếng cười) chỉ dùng khi nó giúp khoảnh khắc.

## Âm thanh và mix

- **Nghe vật liệu đã có trước khi thêm.** Tiếng phòng, tiếng thao tác có thể đã đủ.
- **Khi lời mang ý, lời phải rõ.** Nhạc và SFX nhường chỗ quanh tên riêng, con số, claim, punchline;
  được phép lấn ra trong khoảng nghỉ hoặc đoạn hành động. Ducking -8 đến -12 dB dưới giọng.
- **Mỗi SFX một lý do**: reveal xứng đáng một tiếng chính xác; lặp một tiếng chỉ vì có cú cắt sẽ làm nó
  mất nghĩa.
- **Cắt hình không có nghĩa là cắt âm**: room tone và nhạc nối các cú cắt; đổi nơi chốn hay người nói
  mới cần chuyển âm rõ.
- Im lặng có chủ đích cũng là một lựa chọn biểu cảm.
- Chuẩn xuất: -14 LUFS tích hợp, true peak ≤ -1 dBTP (`vkit finish` làm tự động).

## Nhịp dựng: đo, đừng đoán

`vkit analyze` cho số liệu của video tham chiếu: độ dài shot trung bình, số từ/phút, thời điểm từ đầu
tiên. Reel mẫu: 191 từ/phút, từ đầu tiên ở 0,0s, mỗi ý ~0,95s. Hãy so bản dựng của bạn với các chỉ số
đó. Nhanh hơn thì có thể khó hiểu, chậm hơn thì người xem lướt qua.

## Màu và tính đồng bộ

- Áp **một LUT/preset** cho mọi shot AI rồi chỉnh lệch nhỏ từng shot.
- Thêm grain nhẹ (2–4%) để các shot từ nhiều model "dính" vào nhau và giảm cảm giác da sáp.
- Dải tối đừng đen bệt. Video AI hay bị crush shadow, nâng nhẹ lift.

## Xuất bản

```bash
python3 scripts/vkit.py finish output/edit.mp4 --preset tiktok --subs output/edit.ass \
  --label "Nội dung có sử dụng AI"
```

| Preset | Kích thước | Ghi chú |
|---|---|---|
| tiktok / reels / shorts | 1080×1920 | 30fps, H.264 High, CRF 18, AAC 192k 48kHz, faststart |
| feed45 | 1080×1350 | Feed Instagram/Facebook |
| square | 1080×1080 | |
| youtube | 1920×1080 | |

`--fit crop` (mặc định) cắt phần thừa để lấp đầy khung, `--fit pad` thêm viền đen để giữ trọn khung hình.
