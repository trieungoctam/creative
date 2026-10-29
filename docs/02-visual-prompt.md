# 02 · Visual Prompt: chỉ đạo một bức ảnh

Công thức cơ bản của khóa học: **chủ thể + bối cảnh + ánh sáng + cảm xúc**, cộng thêm từ khóa phong
cách, tỉ lệ khung và biến thể. Phần dưới nâng công thức đó lên cấp "đạo diễn", dựa trên kinh nghiệm
thực nghiệm mà hypit ghi lại trong `playbooks/craft/image-direction.md`.

## Hai nguyên tắc nền

1. **Model là họa sĩ có thói quen.** Viết "một người ngồi bàn làm việc" thì model sẽ điền khuôn mặt,
   trang phục và căn phòng theo thói quen trung bình của nó. Muốn ảnh không nhạt, bạn phải chỉ đạo
   **vài quyết định quan trọng** bằng lời mạnh.
2. **Vài nét quyết định gánh cả bức ảnh.** Với người dẫn, đó là gương mặt cuốn hút và cách họ đối diện
   máy quay. Với sản phẩm, đó là hình khối đặc trưng và cách dùng. Với địa điểm, đó là vài đồ vật kể
   chuyện. Dồn chữ vào những chỗ này, phần còn lại để model tự điền. Liệt kê dài các chi tiết phụ
   không làm ảnh tốt hơn.

## Cấu trúc 4 đoạn (ảnh người trong cảnh, kiểu quay điện thoại)

| Đoạn | Bạn quyết định gì |
|---|---|
| **Capture** (ngôn ngữ chụp) | Ảnh này được "chụp" bằng gì: iPhone quay dọc, ánh sáng tự nhiên, độ nét kiểu video, không bokeh giả. Viết một lần, dùng lại cho mọi cảnh cùng "thế giới". |
| **Person** (con người) | Người này là ai, vì sao cuốn hút, và vài chi tiết ngoại hình làm họ *riêng biệt*. |
| **Shot** (cú máy) | Họ đang làm gì, nói với ai, máy quay gặp mặt, thân và không gian xung quanh ra sao. |
| **Setting** (bối cảnh) | Ở đâu, bảng màu, vài chi tiết làm nơi đó có người sống. |

### Mẫu Capture tái sử dụng (UGC điện thoại)

```text
Vertical 9:16 frame from an iPhone front-camera video, natural available light, true-to-life skin
texture with visible pores, slight handheld framing, everyday phone-video sharpness and dynamic
range, no studio lighting, no cinematic bokeh, no retouching.
```

Đây là bản mẫu của kit, viết theo tinh thần của `phone-ugc-v1` trong hypit. Hãy test với model bạn
dùng rồi khóa lại một bản cho dự án.

## Bảy câu hỏi cho ảnh người dẫn

1. Đây là kiểu ảnh "chụp" gì?
2. Người này là ai, sức hút **kiểu gì** và **mạnh đến đâu**?
3. Chi tiết ngoại hình nào khiến họ dễ nhận ra, không chung chung?
4. Họ đang ở trạng thái gì để video tiếp nối được?
5. Máy quay đóng khung cuộc gặp ra sao: mặt, thân, ánh mắt, chừa khoảng trống cho chữ/đồ họa?
6. Quan hệ nào cho thấy người và nơi chốn thuộc về nhau?
7. Màu nào tạo nên tính cách của cả bức ảnh?

Không cần trả lời đủ 7 câu thành 7 câu prompt. Một cụm từ có thể trả lời nhiều câu cùng lúc.

## Casting mạnh tay

- **Ghi rõ tuổi thật** và đưa một hình mẫu so sánh cho vẻ đẹp. Ví dụ: "a Vietnamese girl in her late
  twenties, strikingly beautiful, with the fresh presence of a top V-pop idol". Cách này có lực hơn
  hẳn "attractive". Hypit ghi nhận với GPT Image 2, mở đầu bằng *girl/boy + tuổi trưởng thành cụ thể*
  cho gương mặt sống động. Hãy test với model của bạn.
- **Vẻ đẹp cần cả cường độ lẫn kiểu.** "Exceptionally beautiful" cho cường độ. "Clean girl / soft goth
  / founder Gen Z" cho kiểu.
- **Neo cấu trúc cơ thể.** Ảnh nửa người hay bị đầu to, vai hẹp. Thêm "very broad shoulders and
  excellent head-to-shoulder proportions" để chữa.
- **Chọn vài neo nhìn thấy được**: tóc quanh mặt, kiểu trang điểm mắt, một món phụ kiện đáng nhớ.

## Chọn trạng thái "chờ" (idle) cho ảnh sẽ thành video

Ảnh dùng làm khung đầu cho video phải là **một hoạt động đang diễn ra**, không phải một tư thế đóng
băng. Ví dụ: đang nói với người xem và tay rảnh đang ra dấu. Một nụ cười toe hay mặt giật mình sẽ
khóa ảnh vào đúng một khoảnh khắc, trừ khi khoảnh khắc đó chính là nội dung.

Với người dẫn nói thẳng vào máy, thêm: *"face points straight toward the lens, no head tilt or
rotation"*. Mặt giữ ổn định, còn thân và tay vẫn tự do.

## Đóng khung cho thứ ảnh sẽ trở thành

- Đặt mặt ở vị trí mà bố cục sau này cần. Muốn chừa bên trái cho icon thì đặt người lệch phải,
  nhưng **tả bằng cảnh vật thật** (một cái bàn, cánh cửa) để việc lệch trông tự nhiên.
- **Đừng vẽ đồ họa vào ảnh** nếu sau này nó cần chuyển động riêng. Icon hay chữ cần animate thì để
  thành asset riêng.
- Ảnh hero toàn màn hình nên làm ở 2K, ảnh inset 1K là đủ. Tỉ lệ khung và độ phân giải là **tham
  số của model**, đừng viết vào prompt.

## Dựng bối cảnh bằng vài chi tiết

Bối cảnh phải mang một **thế giới xã hội**, không chỉ là một mảng màu sau lưng. Gọi tên nơi chốn và
vài chi tiết giải thích vì sao người này ở đó: "quán cà phê sân thượng Sài Gòn, ly cà phê muối uống
dở, dây đèn vàng, mái tôn phía xa". Thêm một khung cửa hay khoảng mở phía sau để có chiều sâu.

**Màu có chủ đích** và gắn vào vật thật: "đỏ san hô và vàng nghệ" nằm trên quần áo, cây cối, biển
hiệu, không phải một bức tường sơn đều.

## Tham chiếu: nói rõ mỗi ảnh đóng góp gì

"Ảnh 1 = danh tính khuôn mặt. Ảnh 2 = sản phẩm (giữ đúng nhãn và màu nắp). Ảnh 3 = không gian và
bảng màu." Khi tham chiếu đã gánh phần khó, prompt chỉ cần tả **cuộc gặp mới** hoặc **góc nhìn mới**.

## Biến thể có hệ thống

Đừng bấm generate lại may rủi. Mỗi lượt chỉ đổi **một biến**:

| Vòng | Giữ | Đổi | Mục đích |
|---|---|---|---|
| 1 | Capture, Setting | Person (3 kiểu casting) | Chọn người |
| 2 | Person đã chọn | Shot (3 khoảng cách/góc) | Chọn cú máy |
| 3 | Person + Shot | Setting/bảng màu (3 phương án) | Chọn thế giới |
| 4 | Tất cả | Seed / chi tiết nhỏ | Đánh bóng |

Ghi mọi prompt và kết quả vào `prompts/` theo mẫu `templates/PROMPT-IMAGE.md` để tái lập được.
