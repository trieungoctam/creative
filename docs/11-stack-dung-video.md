# 11 · Stack dựng video bằng code và agent: hypit · HyperFrames · Remotion · Higgsfield

Bốn công cụ nằm ở các tầng khác nhau, **không loại trừ nhau**. Chọn theo việc cần làm.

| | **hypit** | **HyperFrames** (HeyGen) | **Remotion** | **Higgsfield** |
|---|---|---|---|---|
| Bản chất | Hệ thống agent clone video viral: kịch bản neo theo từ (SVML) → generate → dựng | Framework **HTML/CSS/GSAP → MP4** tất định, thiết kế cho agent | Framework **React → video**, lâu đời nhất, hệ sinh thái lớn | **Nền tảng hosted** gom nhiều model ảnh/video + công cụ riêng |
| Mạnh nhất ở | Clone cả *workflow* của một video (A-roll, B-roll, phụ đề, MG), sinh 100 biến thể, ~$1/video | Motion graphics, phụ đề động, overlay, transition. **~450 block dựng sẵn** | App/SaaS video (Player nhúng web, render Lambda/Cloud Run), video dữ liệu | Sinh footage: Seedance, Kling, Veo, Sora, Nano Banana; nhân vật nhất quán, camera điện ảnh |
| Generate AI | Có (qua HypiHub hoặc BYOK) | Qua skill `/media-use` (HeyGen avatar/voice, hoặc tool local miễn phí) | Không có sẵn, tự gọi API | Đây chính là sản phẩm |
| Skill cho Claude Code | `npx skills add hypit-ai/hypit -g` | `claude plugin marketplace add heygen-com/hyperframes` → `claude plugin install hyperframes@hyperframes` | `npx skills add remotion-dev/skills` | MCP: `mcp.higgsfield.ai/mcp` |
| Yêu cầu | Node 22.15+, pnpm | Node 22+, FFmpeg | Node, Chrome headless | Tài khoản + credit |
| Giấy phép | Apache-2.0 **có điều kiện**: dùng nội bộ/thương mại OK; **cấm SaaS đa người thuê** và bán lại nếu chưa mua license | **Apache-2.0 thuần** (thoải mái nhất, kể cả làm SaaS) | **Miễn phí cho cá nhân, công ty ≤ 3 nhân sự**, phi lợi nhuận; lớn hơn phải mua Company License | Thương mại, trả theo credit/gói |

## Khi nào dùng cái nào

```
Cần FOOTAGE mới (người, cảnh, sản phẩm chuyển động)?
   └─► Higgsfield (hoặc API model trực tiếp / HypiHub)

Muốn CLONE nguyên một video viral rồi ra hàng loạt biến thể?
   └─► hypit

Cần LỚP ĐỒ HỌA: phụ đề động, danh sách, chart, transition, overlay, khung điện thoại?
   └─► HyperFrames (agent-first, nhiều block sẵn)  ─ hoặc ─  Remotion (nếu đã quen React)

Xây SẢN PHẨM/SaaS render video cho khách hàng?
   └─► HyperFrames (Apache-2.0) hoặc Remotion (cần Company License khi team > 3 người)
       ⚠ không dùng hypit làm backend đa người thuê nếu chưa có license thương mại
```

**Combo khuyến nghị cho bạn:** Higgsfield (hoặc API) sinh A-roll/B-roll → HyperFrames làm phụ đề và MG →
`vkit finish` xuất bản. Thêm hypit khi cần clone theo lô.

> Liên quan đến plan sản phẩm của bạn: trong nghiên cứu, "Template render" đang ghi *BUILD: hypit
> (license single-tenant OK)*. Nếu sau này lên SaaS đa người thuê (Phase "Scale"), **HyperFrames
> (Apache-2.0) là lựa chọn an toàn hơn về giấy phép** cho tầng render. Hypit vẫn dùng được cho xưởng nội bộ.

## HyperFrames: những con số đáng học (từ `skills/hyperframes/references/`)

Phần này hữu ích ngay cả khi bạn dựng bằng CapCut/Premiere, vì là kinh nghiệm đo từng khung trên các
phim launch chính thức của họ.

**Chuyển động**
- Chuyển động nhanh kéo dài 0,3–0,6s và có motion blur ở khung nhanh nhất.
- **Vào chậm, ra gọn**: ease-out đuôi dài khi xuất hiện (`expo.out`, `power4.out`). Khi ra thì ngắn hơn
  vào 40–50% và đi một mạch.
- **Ease theo vai trò**: xuất hiện dùng đuôi dài; chuyển máy hoặc đổ màu dùng `power2.inOut`; zoom xuyên
  hoặc thoát dùng gia tốc `power3.in`. Mọi thứ cùng `power2.out` 0,5s là dấu hiệu "trông như AI làm".
- **Lò xo** theo hệ số giảm chấn: 0,7–0,85 sang trọng, 0,4–0,6 vui, < 0,3 hoạt hình. Opacity và màu
  không bao giờ nảy.
- **Chồng nhịp**: phần tử sau bắt đầu khi phần tử trước xong 30–50%. Stagger: chữ cái cách 1 khung,
  từ 60–120ms, mục danh sách 40–80ms.
- **Tiêu đề đã đáp thì đứng yên tuyệt đối.** Chuyển động chuyển sang phần tử khác, máy quay hoặc nền.
- **Thời gian giữ chữ**: ~0,5s + 0,3s mỗi từ; dòng cuối phim ≥ 2s.
- **Nhịp**: montage cắt mỗi 0,13–0,8s; demo giữ khung 7–10s trong khi UI hoạt động; shot trung bình
  1,8–3s. Giữ 0,3–0,75s trước payoff.
- **Theo beat nhạc**: số khung mỗi beat = fps × 60 / BPM. Tính từ chỉ số beat rồi làm tròn, đừng cộng
  dồn số đã làm tròn (sẽ trôi). Cắt trên beat, đổi layout trên ô nhịp.
- **Chuyển cảnh có nguyên nhân**: dùng 3–5 kiểu mỗi phim, mỗi kiểu do một vật trên màn hình gây ra
  (zoom xuyên nút, vật thể thành thế giới, morph, đổ màu, whip, iris từ điểm click, dip cut).
  Cắt cứng ≤ 1/3 số mối nối.
- **Mặc định trông "generated"** cần tránh: tiêu đề "thở" hoặc lơ lửng liên tục, mọi cảnh vào cùng một
  kiểu, mọi phần tử fade + trượt lên, UI nảy, vòng tròn click.

**Video dọc 9:16**
- Khung 0 là thumbnail và hook: mặt người, kết quả hoặc một dòng chữ đậm. Không bao giờ đen, không logo.
- Trên khung 1080×1920: không đặt gì ở 168px trên cùng; chữ và sản phẩm nằm trong dải **168–1330px**;
  dưới 1330px chỉ để texture; không đặt chữ dưới dải nút bên phải.
- Chữ to hơn bản ngang ~1,35 lần, không chữ nào < 28px, mỗi dòng claim ≤ ~5 từ tiếng Anh. Thừa thì
  cắt bớt chữ, đừng thu nhỏ.
- Shot 1–2s, nhịp mới mỗi 2–4s, payoff trước khi người xem lướt.

**Phụ đề**
- Cụm 2–3 từ cho năng lượng cao, 3–5 cho trò chuyện, 4–6 cho điềm tĩnh. Ngắt ở cuối câu, khoảng lặng
  ≥ 150ms hoặc giới hạn từ.
- Mỗi lúc chỉ hiện một cụm. Phụ đề bắt đầu đúng 0s trông như có sẵn, nên bắt đầu ở 0,1–0,3s.
- Bản dọc đặt cách đáy ~600–700px, không bao giờ đè lên mặt.
- Whisper hay **bịa "Thank you."** trong đoạn im lặng cuối, nên lọc các từ nằm trong đoạn lặng.
- **Chữ sau lưng người** (kiểu "cover story"): video → chữ → cutout người. Chữ bị che 30–55% là đẹp nhất.

## 17 hiệu ứng trong reel mẫu → block HyperFrames tương ứng

Tra trong registry (`npx hyperframes catalog --json`, hoặc thư mục `registry/` của repo). Đây là đối
chiếu theo **tên và mô tả block**, chưa render thử từng cái.

| # | Hiệu ứng | Block / component gợi ý |
|---|---|---|
| 01 | orbit | `carousel-orbit-1…5`, `three-orbiting-cards` |
| 02 | couch wall | `mk-clone-wall-transition`, `logo-wall` |
| 03 | ui world | `claude-exchange`, `chatgpt-exchange`, `ai-chat-reveal` |
| 04 | frame break | `vfx-portal`, `wireframe-portal-title` |
| 05 | digital zoom | `push-in`, `cinematic-zoom`, `ui-focus-zoom` |
| 06 | phone mockup | `vfx-iphone-device`, `device-frame-stage`, `multi-device-splay` |
| 07 | checklist | `marker-checklist-card`, `mk-specs-list` |
| 08 | headline wall | `notes-reveal`, `notification-pileup` |
| 09 | zoom-through cut | `zoom-through-transition` |
| 10 | chart grow | `animated-bar-chart`, `data-chart`, `mk-line-graph` |
| 11 | pull-back reveal | `pull-back-reveal`, `parallax-unzoom` |
| 12 | green screen | `segmentation-flood` + `npx hyperframes remove-background` |
| 13 | paper cut | `paper-collage-reveal`, `torn-paper-rip` |
| 14 | doodle boil | `hw-boil`, `hw-scribble-transition`, `hw-callout-circle` |
| 15 | vertigo | `camera-dolly-zoom` |
| 16 | cover story | chữ sau cutout (xem phần Phụ đề ở trên) + `titlecard-lockup` |
| 17 | glass type | `glass-hero`, `glass-shard-title`, `ios26-liquid-glass` |

Phụ đề có sẵn: `caption-pill-karaoke`, `caption-highlight`, `caption-kinetic-slam`, `caption-emoji-pop`...

## Template của kit: `scripts/hf_listicle.py`

Sinh sẵn project HyperFrames cho hệ thống "**danh sách đánh số tô sáng + khung điện thoại chiếu demo +
bộ đếm N/M**" của reel mẫu, với mốc thời gian lấy **tự động từ lời thoại của bạn**:

```bash
python3 scripts/vkit.py analyze projects/x/aroll.mp4 --language vi        # → transcript.json
python3 scripts/hf_listicle.py templates/hyperframes/listicle.example.json \
  --transcript projects/x/aroll_analysis/transcript.json --out projects/x/hf
cp projects/x/aroll.mp4 projects/x/hf/assets/aroll.mp4                    # + ảnh demo-01.jpg...
cd projects/x/hf && npx hyperframes check --json && npx hyperframes preview
```

Chạy với transcript của reel mẫu, script tự tìm đúng 17 mốc (0,00 · 0,68 · 1,64 … 15,72s), khớp bản gốc.
⚠ Project sinh ra được viết theo hợp đồng trong tài liệu HyperFrames, nhưng **chưa được render thử**
trong môi trường dựng kit. Lần đầu hãy chạy `npx hyperframes check --json` và sửa theo dòng `Fix:`.

## Remotion: khi nào đáng dùng

- Đã có đội React hoặc cần **nhúng player** vào web app (`@remotion/player`).
- Render hàng loạt trên cloud (`@remotion/lambda`), video cá nhân hóa theo dữ liệu (tên khách, số liệu).
- Skill chính thức: `/remotion-best-practices` (router), `/remotion-create`, `/remotion-captions`,
  `/remotion-render`, `/remotion-saas`.
- Muốn chuyển project Remotion sang HyperFrames: dùng skill `/remotion-to-hyperframes`.
- **Kiểm tra license**: công ty > 3 nhân sự phải mua Company License (remotion.pro).

## Higgsfield: dùng thế nào cho đáng tiền

- Gói tháng (tham khảo 10/2026, giá thay đổi thường xuyên, kiểm tra trang pricing): Starter ~$19
  (270 credit) · Plus ~$47–59 (1.200) · Ultra ~$99–129 (3.000). Có API trả theo lượt (ra mắt 09/2026).
- **MCP cho Claude** (`mcp.higgsfield.ai/mcp`) tiêu cùng quỹ credit của gói. Các chế độ "unlimited"
  và miễn phí **chỉ có trên web**, không có qua MCP/CLI. Bản dùng thử MCP có báo cáo tự gia hạn
  sang gói Plus: đọc kỹ điều khoản trước khi bật.
- Mạnh ở: chọn nhiều model trong một chỗ (Seedance, Kling, Veo, Sora, Wan, Nano Banana); Soul ID cho
  nhân vật nhất quán; Cinema Studio cho chuyển động máy; Genjutsu (dùng chuyển động của video tham
  chiếu cho nhân vật, sản phẩm của bạn), đúng kiểu "chuyển giao tham chiếu" ở `03`.
- Áp dụng kỷ luật ở `02`/`03`: hero trước, biến thể theo vòng, ghi lại prompt. Credit đắt nhất là
  credit tiêu cho lần generate không có chủ đích.

Nguồn: README và skill của từng repo (hypit-ai/hypit, heygen-com/hyperframes, remotion-dev/remotion,
bản clone ngày 29/10/2026); trang chủ higgsfield.ai; tổng hợp giá từ krea.ai, blotato.com, aituber.app.
