# 03 · Video Prompt: chỉ đạo diễn xuất và chuyển động

Ảnh xác lập **ai** và **ở đâu**. Video làm cho kịch bản sống: lời nói, tương tác, máy quay, hành động.
Tóm lược từ `playbooks/craft/video-direction.md` của hypit, kèm kinh nghiệm của khóa học.

## 1. Chỉ đạo *lý do* của hành động, không phải biên đạo từng ngón tay

Câu đầu tiên của prompt nên nói **người này nghĩ gì về chủ đề và quan hệ thế nào với người nghe**.
Thái độ đó tự kéo theo giọng, nét mặt, tư thế và nhịp.

```text
Cô ấy đang than với bạn thân, bực mà thương, vì món này đắt vô lý. Đến chỗ nói giá, lông mày nhướng
lên, lòng bàn tay ngửa ra, giọng nhấn kiểu không tin nổi. Câu khen cuối nói với nụ cười trêu trong giọng.
```

Câu thứ nhất chỉ đạo cả cuộc gặp. Các chi tiết sau chỉ để chỗ quan trọng (giá, cú lật cuối) đọc rõ.
**Gắn một động tác tay cho mỗi câu thoại không làm diễn xuất mạnh hơn.**

Tiết chế cũng cần có mục đích: "Cô ấy cân nhắc lời quảng cáo với vẻ hoài nghi có hứng thú. Nhấn giọng
vào con số, rồi chốt bằng một cái gật đầu nhỏ, dứt khoát."

## 2. Hành động phải bám vào cảnh có thật

- Mô tả quan hệ vật lý với máy quay, đồ vật, người khác **đang có trong cảnh**.
- **Lời nói và hình ảnh có hai trách nhiệm khác nhau.** Người dẫn nói về con số, biểu đồ hay phép
  so sánh, nhưng máy quay chỉ ghi màn trình diễn của họ. Con số và biểu đồ để phụ đề/MG lo.
- Model video hay **hiểu ẩn dụ theo nghĩa đen**. "Làm ý tưởng bay lên" có thể ra một vật bay thật.
  Hãy viết bằng ngôn ngữ nhìn thấy được: ánh mắt, cử chỉ, chuyển động máy.
- Đừng bắt ngón tay giơ đúng số 3. Cử chỉ nhấn tự nhiên đáng tin hơn, con số để chữ trên màn hình lo.
- Cho clip một cái **mép**: người bị ngắt lời thì đang bận làm gì đó, người nói xong thì bắt đầu quay đi.

## 3. Mỗi đầu vào một trách nhiệm

| Đầu vào | Gánh phần gì |
|---|---|
| Ảnh nhân vật + cảnh | Ngoại hình, bối cảnh, khung hình, trạng thái vật lý cần giữ |
| Ảnh sản phẩm / giao diện | Chi tiết phải chính xác (nhãn, màu, chữ) |
| Video tham chiếu chuyển động | Nhịp diễn, đường đi, va chạm, cách máy chạy, những thứ ảnh tĩnh không tả được |
| Giọng tham chiếu | Danh tính giọng xuyên suốt (nếu model nhận) |
| Lời thoại | Câu chữ chính xác, cách đọc, lượt lời |
| Chỉ đạo đoạn | Thái độ, cách nói, sự chú ý, tương tác, máy quay, nhịp cắt |

## 4. Chọn quan hệ sinh video

| Quan hệ | Khi nào dùng |
|---|---|
| **Text → video** | Thế giới và hành động không phụ thuộc danh tính, bố cục hay chuyển động có sẵn |
| **Khung đầu–cuối** | Shot *phải* bắt đầu hoặc kết thúc ở đúng một hình (transition ghép nối, reveal sản phẩm) |
| **Theo tham chiếu** | Ảnh/video/âm thanh dẫn hướng danh tính, thế giới, giọng, chuyển động. **Mặc định nên dùng cho sản xuất có kiểm soát.** |

Với video tham chiếu chuyển động, phân biệt hai cách dùng:
- **Chuyển giao tham chiếu**: lấy *tính chất thời gian* (nhịp, đường máy, cách hiệu ứng tiến triển) để tạo
  cảnh mới.
- **Chỉnh sửa nguồn**: chính đoạn footage là vật liệu cần sửa. Nói rõ cái gì đổi, cái gì giữ.

Xem video tham chiếu để **hiểu** khác với nạp nó vào model làm **đầu vào**. Gọi là "clone" không có
nghĩa phải nạp cả video gốc.

## 5. Máy quay và nhịp cắt là một phần của đoạn diễn

- Talking-head trên mạng xã hội: ưu tiên **jump cut cắt khoảng lặng** ở ranh giới cụm từ. Khung đứng
  yên, diễn xuất có biểu cảm và cắt dày hoàn toàn đi được với nhau.
- Podcast cắt theo người nói hoặc theo phản ứng đáng giá. Phỏng vấn đường phố ưu tiên khách, cắt sang
  người hỏi để lấy phản ứng.
- Prompt "jump cut" chỉ là *xin* model một nhịp dựng. Muốn cắt chính xác thì **cắt ở hậu kỳ**.

## 6. Ước lượng thời lượng theo lời thoại

Đếm từ rồi chia cho tốc độ nói mục tiêu. Mạng xã hội nhanh: tiếng Anh ~170–190 từ/phút (reel mẫu đo
được 191), tiếng Việt ~4–5 âm tiết/giây. Cộng thêm thời gian cho phản ứng và khoảng dừng có chủ đích,
rồi chọn độ dài request mà model hỗ trợ (thường 5/8/10/15s). Nếu không vừa:
- Câu hỏi–trả lời ngắn có thể gộp chung một request.
- Câu ngắn quá thì thêm một phản ứng có ý nghĩa.
- Đoạn dài thì chia ở chỗ ý chuyển hướng.

## 7. Mẫu prompt video (talking-head theo ảnh tham chiếu)

```text
[Tham chiếu] Ảnh 1: nhân vật + bối cảnh (giữ nguyên người, trang phục, căn phòng, ánh sáng).
[Thoại] "<lời thoại chính xác>"
[Thái độ] <người này nghĩ gì về chủ đề, quan hệ với người nghe>
[Nhấn] Ở "<cụm từ>": <một phản ứng nhìn thấy được>. Kết bằng <cách chốt>.
[Máy] Máy cố định ngang mắt, khung nửa người như ảnh 1; jump cut ở chỗ ngắt câu.
[Tránh] Không chữ trên hình, không đổi trang phục, không thêm người.
```

Dùng `templates/PROMPT-VIDEO.md` để ghi lại và so sánh các lần chạy.
