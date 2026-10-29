# 04 · Workflow sản xuất: ý tưởng → ảnh chủ lực → concept → chuyển động → hậu kỳ

```
 [0] Tham chiếu ──► [1] BRIEF ──► [2] TREATMENT ──► [3] STORYBOARD
                                                         │
     [7] QC + xuất ◄── [6] Dựng ◄── [5] Chuyển động ◄── [4] Ảnh chủ lực
            │
            └──► đăng → đo số liệu → quay lại [1] với hook mới
```

## Cấu trúc thư mục một dự án

```
projects/<ten-du-an>/
  BRIEF.md          Mục tiêu của BẠN: sản phẩm, khách, nền tảng, CTA, ngân sách, điều bắt buộc
  TREATMENT.md      Đáp án sáng tạo: premise, hook, nhịp, nhân vật, thế giới, các hệ thống hình/âm
  STORYBOARD.md     Kịch bản chính thức + bảng shot
  PROGRESS.md       Đang làm gì, còn gì, bước tiếp theo (để phiên sau làm tiếp được)
  references/<ref>/ source.mp4 · transcript.json · ANALYSIS.md · TIMELINE.md · evidence/
  prompts/          Mỗi lần generate một file: prompt, tham chiếu, model, kết quả, điểm
  assets/           Ảnh/clip đã CHỐT (hero, nhân vật, sản phẩm, B-roll)
  output/           Bản dựng, bản xuất
```

Nguyên tắc của hypit đáng học: **file là bộ nhớ**. Mỗi sự thật chỉ có một chủ:
- Người dùng đổi mục tiêu → sửa **BRIEF**.
- Đổi câu chuyện, logic shot hay phong cách → sửa **TREATMENT**.
- Sửa prompt, chọn lại take, chỉnh vị trí chữ (cùng thiết kế) → sửa **prompts/** hoặc timeline,
  *không* động vào Treatment.
- Hiểu thêm về video tham chiếu → sửa **ANALYSIS/TIMELINE**.

## Bước 0 · Tham chiếu (30–60 phút)

`vkit fetch` và `vkit analyze` rồi điền ANALYSIS.md. Xem `09-giai-phau-video.md`. Kết quả cần có:
video này **muốn người xem cảm/biết/làm gì**, và **từng hệ thống** (phụ đề, MG, B-roll, âm thanh)
góp phần ra sao.

## Bước 1 · BRIEF (15 phút)

Chỉ ghi những gì **chỉ bạn mới biết**: mục tiêu, khách hàng, sự thật về sản phẩm, CTA, giới hạn thời
lượng/ngân sách, tài sản bắt buộc (logo, mặt người thật). Có thể chỉ cần một câu:
> "Làm lại đúng cấu trúc reel tham chiếu, thay người bằng tôi (ảnh trong `assets/me/`), sản phẩm là
> khóa học X, tiếng Việt."

## Bước 2 · TREATMENT (30 phút)

Viết bằng ngôn ngữ đạo diễn, không ghi tên tool:
- Premise và trải nghiệm người xem.
- Hook → thân → reveal/payoff → CTA, kèm nhiệm vụ của từng đoạn.
- Nhân vật và thái độ, máy quay, thế giới.
- Những hệ thống hình/âm **thật sự cần** (đừng thêm hiệu ứng vì nó có sẵn).
- Ảnh nào làm **neo danh tính và nhất quán**.

## Bước 3 · STORYBOARD

Kịch bản là bản chính thức duy nhất. Mỗi shot gồm: lời thoại, hình, chữ/MG, âm thanh, thời lượng,
và **quan hệ sinh** (text / khung đầu–cuối / tham chiếu). Mẫu ở `templates/STORYBOARD.md`.

## Bước 4 · Ảnh chủ lực (hero)

Làm **một khung đẹp nhất** trước. Nó định nghĩa người, thế giới và bảng màu cho cả video. Chạy biến thể
theo vòng (xem `02`), chấm bằng thang 14 điểm, chốt vào `assets/`. Mọi cảnh sau phát triển từ hero
(xem cây tham chiếu ở `05`).

## Bước 5 · Phát triển concept và chuyển động

1. Từ hero, sinh các **góc nhìn khác** của cùng thế giới: cận, toàn, góc ngược, sản phẩm trên tay.
2. Với từng shot, chọn quan hệ sinh video, viết prompt theo `03`, ước lượng thời lượng.
3. Generate 2–4 take mỗi shot, chọn take tốt nhất. Lưu cả take hỏng để biết model hay sai ở đâu.

## Bước 6 · Dựng hậu kỳ

Phần quyết định chất lượng. Xem `06-hau-ky.md`. Thứ tự: ráp A-roll theo nhịp lời → cắt khoảng lặng →
B-roll phủ ý → phụ đề → MG gắn với từ khóa → nhạc và SFX → màu → xuất.

## Bước 7 · QC và xuất bản

Chạy `templates/QC-CHECKLIST.md`, rồi `vkit finish`. Xem bản cuối **trên điện thoại** ở kích thước
thật, có tiếng và không tiếng.

## Ngân sách và chi phí (trước khi tốn tiền)

Ghi vào BRIEF: model/dịch vụ dùng, số lần generate dự kiến, chi phí ước tính và trần chi tiêu. Tham
khảo: hypit báo ~$1,07–1,15 cho một video 18–26s gồm ảnh GPT Image 2, video Seedance 2 Mini 720p và
căn chỉnh WhisperX. Veo 3.1 Fast qua API ~$3,84 cho 30s (theo nghiên cứu của bạn).
