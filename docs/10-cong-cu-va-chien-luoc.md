# 10 · Bản đồ công cụ và chiến lược (tóm tắt từ nghiên cứu của bạn)

Chi tiết tầng dựng (hypit, HyperFrames, Remotion, Higgsfield) xem ở `11-stack-dung-video.md`.

## Công cụ theo bước trong workflow

| Bước | Lựa chọn | Ghi chú |
|---|---|---|
| Tìm video tham chiếu | TikTok Creative Center, FastMoss, Kalodata, Meta Ad Library | Lưu link vào `references/` |
| Tải + mổ xẻ | `vkit fetch/analyze/tile` (yt-dlp + ffmpeg + faster-whisper) | Miễn phí, chạy local |
| Kịch bản, phân tích | Claude (skill `/giai-phau-video`, `/len-brief`) | |
| Ảnh hero/nhân vật | GPT Image 2, Nano Banana Pro, Seedream, Flux | Xem `02` |
| Video từ ảnh/tham chiếu | Seedance 2 Mini/2.5, Kling 3/4, Veo 3.1, Wan; gom qua Higgsfield/HypiHub | Xem `03` |
| Avatar nói / UGC | HeyGen, TopView, Arcads, Creatify, MakeUGC, varg | Xem bảng giá bên dưới |
| Giọng | ElevenLabs, MiniMax, Fish Audio | Kiểm tra tiếng Việt kỹ |
| Lớp đồ họa, phụ đề | HyperFrames, Remotion, CapCut, Premiere/After Effects | |
| Xuất bản | `vkit finish`; TikTok Content Posting API (Phase 2) | |

## Giá tham khảo mỗi ad 30s (từ nghiên cứu của bạn, cần xác minh lại khi dùng)

| Tool | Giá/30s | Điểm chính | API/MCP |
|---|---|---|---|
| HeyGen | $0,39–1,16 | 175+ ngôn ngữ, digital twin | MCP mọi gói |
| TopView | ~$1,08 (trả năm) | Rẻ nhất nếu trả năm | API + MCP từ gói entry |
| AdMakeAI | ~$2,65 | Viết script từ hook đối thủ | — |
| Creatify | ~$2,73–3,90 | URL → video | API/MCP $99+/tháng |
| varg | ~500 credit (~$24/tháng) | Dùng ảnh nhân vật/sản phẩm của bạn | API + MCP mọi gói |
| MakeUGC | $5,80–11,80 | Product-in-hand | $99+/tháng |
| Arcads | ~$11 | Diễn viên thật, đẹp nhất | MCP (cần sub) |
| Higgsfield | $7,32–19,99 | Đa model + Marketing Studio | MCP (trả phí) |
| *Nền: Veo 3.1 Fast API* | *~$3,84* | *model thô* | |
| *Nền: hypit tự host* | *~$1,15/20s* | *trọn gói, mã nguồn mở* | |

## Build vs Buy theo module (plan của bạn)

| Module | Quyết định | Ghi chú cập nhật |
|---|---|---|
| Discovery | BUILD: scrape Creative Center + FastMoss API | |
| Script + phân tích | BUILD: agent sẵn có | Skill trong kit này là bản prototype |
| Avatar/UGC | BUY trước (HeyGen/varg API-MCP), BUILD sau | |
| Template render | BUILD | hypit cho xưởng nội bộ; **HyperFrames (Apache-2.0)** nếu lên SaaS đa người thuê |
| Publish | BUILD: xin TikTok Content Posting API | |
| Analytics | BUILD: UTM + affiliate API | |

## Pain đáng giải nhất (theo Running Lean)

P1 chi phí khi làm số lượng lớn · P2 quy trình đứt gãy qua 4–6 tool · P4 hook không được đo có kỷ luật.
Beachhead: agency/team affiliate 2–10 người, ≥ 20 video/tuần.

Liên hệ với kit: muốn bán "xưởng video chất lượng" thì trước tiên **chính bạn phải làm ra video chất
lượng một cách lặp lại được**. Lộ trình `00` + portfolio là bằng chứng cho buổi problem interview và
concierge MVP: bạn tự chạy pipeline thủ công cho 5 team đầu tiên.

## Giả định rủi ro cần test (giữ nguyên thứ tự)

1. Team thấy pain giá-theo-khối-lượng đủ lớn để đổi tool → 15–20 problem interview, pass khi ≥ 40% xếp vào top 3.
2. Chấp nhận BYOK / tự host → concierge onboard 5 team, pass khi ≥ 4/5 tự setup trong ≤ 15 phút.
3. Sẵn sàng trả subscription → smoke test trang giá + pre-order, pass khi ≥ 5 team đặt cọc.
4. Chất lượng render đủ chạy ads thật → 10 video, ads $5–10 mỗi video, pass khi CTR không thua video làm tay.
