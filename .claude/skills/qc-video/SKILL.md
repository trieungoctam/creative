---
name: qc-video
description: Kiểm tra chất lượng một video thành phẩm trước khi đăng (hook, nhịp, lỗi hình AI, phụ đề, vùng an toàn, âm lượng, nhãn AI, thông số kỹ thuật) rồi xuất bản chuẩn bằng vkit finish. Dùng khi người dùng gửi bản dựng và hỏi "ổn chưa", "QC giúp", "xuất cho TikTok".
---

# QC và xuất bản

1. Chạy đo đạc:
   ```bash
   python3 scripts/vkit.py analyze <video> --out <video>_qc --language <vi|en>
   ```
   Đọc `summary.json` (LUFS, fps, kích thước, từ đầu tiên, số từ/phút, độ dài shot).
2. Xem `evidence/hook_0-3s.jpg`, `evidence/overview.jpg`. Soi thêm bằng `vkit tile` ở các chuyển cảnh
   và shot có người hoặc sản phẩm (tay, miệng, nhãn).
3. Đi qua `templates/QC-CHECKLIST.md` từng mục. Mục nào không kiểm tra được từ file (ví dụ license nhạc,
   đồng ý dùng mặt người) thì ghi "cần người dùng xác nhận", đừng đánh dấu đạt.
4. So nhịp với video tham chiếu của dự án (nếu có `references/*/summary.json`).
5. Báo cáo: **Phải sửa** (kèm mốc thời gian) · **Nên sửa** · **Đạt**. Mỗi mục kèm cách sửa cụ thể.
6. Khi người dùng đồng ý xuất:
   ```bash
   python3 scripts/vkit.py finish <video> --preset tiktok [--subs <file.ass>] --label "Nội dung có sử dụng AI"
   ```
   Kiểm tra lại file xuất: kích thước, fps, LUFS ≈ -14, xem khung giữa và cuối.
