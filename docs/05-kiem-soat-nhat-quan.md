# 05 · Kiểm soát hình ảnh và video: storyboard, tham chiếu, khung đầu–cuối

Video AI hỏng chủ yếu vì **mất nhất quán**: mặt đổi, áo đổi, sản phẩm sai nhãn, căn phòng nhảy lung
tung. Kiểm soát nghĩa là quyết định **sự thật nào được mang sang** mỗi cảnh, và **từ ảnh nào**.

## Bốn công cụ kiểm soát

| Công cụ | Kiểm soát cái gì | Dùng khi |
|---|---|---|
| **Storyboard** | Thứ tự, nhịp, nhiệm vụ từng shot | Luôn luôn, trước khi generate |
| **Ảnh tham chiếu** | Danh tính, sản phẩm, không gian, bảng màu | Mọi cảnh có nhân vật/sản phẩm lặp lại |
| **Video chuyển động mẫu** | Nhịp diễn, đường máy, va chạm, cách hiệu ứng tiến triển | Khi chữ và ảnh tĩnh không tả nổi chuyển động |
| **Khung đầu–cuối** | Điểm xuất phát/kết thúc chính xác | Transition liền mạch, reveal sản phẩm, ghép nối 2 shot |

## Cây tham chiếu: mỗi ảnh mới mọc từ ảnh "biết" sự thật nó cần

Tóm lược từ `generated-dependencies.md` của hypit. Đừng nối ảnh theo chuỗi tuyến tính A→B→C→D, vì
chi tiết rác sẽ tích tụ dần. Hãy để mỗi ảnh mới lấy tham chiếu từ **ảnh gần nhất thực sự chứa sự thật
cần giữ**.

```
                ┌── Cận mặt (danh tính)
 HERO ──────────┼── Góc ngược của cùng quán (không gian + bảng màu)
 (người + cảnh) ├── Tay cầm sản phẩm ◄── Ảnh sản phẩm gốc (nhãn, màu)
                └── Ngoài hành lang ◄── chỉ lấy danh tính từ HERO, căn phòng đã xong việc
```

Quy tắc:
- **Một tham chiếu có thể nuôi nhiều kiểu biến thể**: cùng người nhưng đổi tay và đồ cầm; cùng quán
  nhưng đổi góc máy.
- Khi đổi địa điểm, **ngừng tham chiếu đồ đạc cũ**. Chỉ mang danh tính và đạo cụ còn dùng.
- Trong prompt, "ảnh 2" nghĩa là *ảnh thứ hai được nối vào request này*. Luôn ghi rõ vai trò của từng ảnh.

## Storyboard trước, generate sau

Mỗi shot trả lời được 5 câu thì mới generate:
1. Shot này phục vụ **câu thoại/ý nào**?
2. Người xem nhìn **đâu trước**?
3. Ảnh tham chiếu nào, giữ sự thật gì?
4. Quan hệ sinh: text, khung đầu–cuối hay tham chiếu?
5. Shot vào và ra thế nào (cắt thẳng, khớp chuyển động, zoom xuyên)?

## Khung đầu–cuối: khi nào và cách làm

- Dùng khi **điểm đến là nội dung**: chai serum xoay rồi dừng đúng góc nhãn; người bước qua cửa và
  ra đúng khung của shot kế tiếp.
- Làm khung cuối trước, sau đó sinh khung đầu từ chính nó (đổi tư thế hoặc góc) để hai khung cùng thế giới.
- Đừng ép mọi shot vào khung đầu–cuối. Chúng ràng buộc model và thường làm chuyển động cứng.

## Video chuyển động mẫu

Khi muốn lấy *cách chuyển động* của một video (điệu nhảy, cú lia máy, va chạm):
1. Cắt đoạn ngắn nhất chứa trọn hành động, kèm cả đoạn chuẩn bị và đoạn lắng lại.
2. Soi từng khung (`vkit tile --every 0.1`) để chắc đoạn đó đúng thứ bạn cần.
3. Nạp đoạn đó làm tham chiếu chuyển động, ảnh để giữ danh tính mới, prompt để nói quan hệ giữa hai bên.

## Tách nền (green screen, cutout)

Nếu cần nhân vật tách nền để ghép đồ họa phía sau (như hiệu ứng "frame break", "cover story" trong
reel mẫu):
- Khi generate mới: phông **một màu, đều sáng**, khác hẳn màu tóc, áo, đồ cầm.
- Footage có sẵn: dùng công cụ matting (RVM, Runway, CapCut "Xóa nền").
- Kiểm tra mép tách trên **nền đích thật**: vai, tóc, tay, viền màu loang.

## Bảng chấm nhất quán (dùng cho game "Nhất quán 10 cảnh")

| Cảnh | Mặt | Tóc | Trang phục | Tỉ lệ cơ thể | Sản phẩm/đạo cụ | Tổng /10 |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
