---
name: san-xuat
description: Chạy phần sản xuất của một dự án trong projects/ từ script.vs + production.toml — generate ảnh/video bằng nhiều model (ưu tiên chính chủ OpenAI, BytePlus Seedance; fal.ai dự phòng), giọng/SFX/nhạc bằng ElevenLabs, căn chỉnh kịch bản vào màn diễn, storyboard, animatic và xuất timeline sang Premiere/Resolve/CapCut/HyperFrames/Remotion. Dùng khi người dùng muốn "làm tiếp", "generate", "lồng tiếng", "dựng thô", "xuất sang Premiere".
---

# Sản xuất từ kịch bản

Đọc `docs/14-pipeline-da-model-da-tool.md` (và `docs/13` nếu cần cú pháp kịch bản). Làm việc trong
thư mục dự án; các lệnh nằm ở `../../scripts/`.

## 0. Kiểm tra trạng thái
- `vscript.py check script.vs`, `vgen.py models` (tuyến nào đang có key), đọc `PROGRESS.md`.
- `storyboard.py board production.toml` để biết shot nào **cần tạo / có ứng viên / đã chốt**.

## 1. Tiền (bắt buộc)
Mọi `vgen run`, `vaudio tts|sfx|music|design` **mặc định là chạy thử**. Trình bày cho người dùng: shot nào,
model/tuyến nào, bao nhiêu biến thể, ước tính chi phí theo bảng giá provider (nói rõ là ước tính). Chỉ
thêm `--yes` khi họ đồng ý, rồi ghi phạm vi và ngân sách đã duyệt vào BRIEF.md.

## 2. Thứ tự sản xuất
1. **Hero/nhân vật trước**: `vgen run --shot hero --model gpt-image,nano-banana -n 2 --yes`. Cho người
   dùng xem các ứng viên (storyboard.html có dải ứng viên), chấm theo thang 14 điểm, rồi `vgen pick`.
2. **Giọng**: chưa có `[voices]` thì `vaudio design --role HOST --description "..."` → nghe 3 bản → `vaudio save`.
3. **A-roll**: hoặc `vgen run --shot aroll-<seg>` (Seedance: image = shot:hero, dialogue = segment), hoặc
   `vaudio tts` (giọng đọc có mốc từng từ) khi video do người thật quay hoặc là dạng narration.
4. **Căn chỉnh**: `vscript.py align script.vs --media <seg>=<file> ...` (hoặc `--media all=`). Khớp dưới 70%
   nghĩa là lời đọc lệch kịch bản: báo người dùng, đừng bỏ qua.
5. **B-roll / overlay**: generate theo `during`, chốt bằng `vgen pick`.
6. **Âm thanh phụ**: `vaudio sfx`, `vaudio music` (hoặc nhạc có license của người dùng).
7. **Animatic**: `storyboard.py animatic` và xem lại khung hình tại các Moment, Selection quan trọng.
8. **Xuất**: hỏi người dùng dựng bằng tool gì, rồi `storyboard.py export --to xml|srt|csv|hf|json`. Hướng dẫn
   import đúng tool (bảng ở docs/14 mục 5).
9. Bản cuối: `vkit.py finish`, rồi skill `qc-video`.

## Lưu ý
- Sửa lời thì sửa `script.vs`, rồi chạy lại `align` (nếu đã có take) hoặc generate lại take của Segment đó.
- Model `?` trong `vgen models` là tuyến chưa đối chiếu schema: đọc trang API của provider trước khi chạy thật.
- Không có Sora (đã ngừng 24/09/2026). Tiếng Việt với ElevenLabs: `eleven_v4`/`eleven_v3`/`eleven_flash_v2_5`.
- Cập nhật `PROGRESS.md` sau mỗi bước để phiên sau làm tiếp được.
