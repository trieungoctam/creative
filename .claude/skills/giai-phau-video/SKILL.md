---
name: giai-phau-video
description: Mổ xẻ một video tham chiếu (link TikTok/Reels/Shorts hoặc file) thành ANALYSIS.md + TIMELINE.md — hook, nhịp, từng hệ thống hình/âm, vì sao giữ người xem, và nên giữ/đổi gì khi làm phiên bản mới. Dùng khi người dùng gửi link video và muốn "vọc", "phân tích", "clone", "học" video đó.
---

# Giải phẫu video tham chiếu

Đọc `docs/09-giai-phau-video.md` trước. Ca mẫu đầy đủ: `examples/tenfoldmarc-17-effects/`.

## Các bước

1. **Xác định dự án.** Nếu chưa có, hỏi hoặc tạo `python3 scripts/vkit.py new <ten>`. Tham chiếu đặt ở
   `projects/<ten>/references/<ref>/`.
2. **Lấy bằng chứng.**
   ```bash
   python3 scripts/vkit.py fetch "<link>" --out projects/<ten>/references/<ref>
   python3 scripts/vkit.py analyze projects/<ten>/references/<ref>/source.mp4 \
     --out projects/<ten>/references/<ref> --language <en|vi|...>
   ```
   Thiếu `yt-dlp`/`faster-whisper` thì `pip install yt-dlp faster-whisper`. Nếu Instagram/TikTok chặn tải,
   nhờ người dùng gửi file.
3. **Xem cả bài.** Mở `evidence/overview.jpg` và `evidence/hook_0-3s.jpg`, đọc `transcript.json`
   (theo từng từ) và `meta.json` (like, comment, caption). Hình thành giải thích tạm: video muốn người
   xem cảm/biết/làm gì.
4. **Soi chi tiết theo câu hỏi.** Dùng `vkit tile --start --end --every 0.1 [--crop w:h:x:y]` cho
   từng hệ thống hay chuyển cảnh còn mơ hồ. Đối chiếu mốc theo từ trong transcript với khung hình.
   Nhớ rằng khoảng giữa các mẫu là vùng mù. Whisper hay nghe sai tên riêng, nên sửa theo chữ trên hình.
5. **Ghi lại.** Điền `ANALYSIS.md` (đã có số liệu tự động ở đầu) và `TIMELINE.md` theo mẫu trong
   `templates/`. Tách quan sát khỏi diễn giải. Ghi mốc thời gian và đường dẫn bằng chứng.
6. **Báo lại người dùng** ngắn gọn bằng tiếng Việt: thông tin cơ bản, cấu trúc theo thời gian, các thủ
   thuật hình/âm, vì sao hiệu quả, bảng giữ/đổi. Gửi 1–2 ảnh bằng chứng tiêu biểu nếu có thể. Kèm
   gợi ý bước tiếp theo (`/len-brief` để làm phiên bản của họ; với hiệu ứng MG thì tra bảng block
   HyperFrames ở `docs/11-stack-dung-video.md`).

## Lưu ý
- Video tải về chỉ để học. Không commit media (đã có `.gitignore`).
- Tỉ lệ comment/like cao bất thường thường là do cơ chế "comment từ khóa để nhận quà". Hãy chỉ ra điều đó.
