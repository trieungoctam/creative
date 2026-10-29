# 12 · Thư viện 17 hiệu ứng (mổ từng khung từ reel @tenfoldmarc)

Nguồn: khung điện thoại trong reel "17 video effects claude can create", soi ở 15 khung/giây
(`vkit tile --every 0.0667 --crop 380:640:350:835`). Mỗi demo chỉ dài ~0,7–1,3s và bị thu nhỏ, nên
phần "Thấy gì" là **quan sát**, còn phần "Cơ chế" và "Cách dựng" là **suy luận để dựng lại**, không
phải mã nguồn gốc của tác giả.

## 5 viên gạch dùng lại khắp nơi

| Viên gạch | Dùng trong | Làm bằng gì |
|---|---|---|
| **A. Tách người (matte/cutout)** để chèn lớp *giữa* nền và người | 01, 02, 04, 08, 10, 12, 13, 14, 16, 17 | CapCut "Xóa nền", Premiere/Resolve Magic Mask, Runway, RVM/SAM2 (local), `npx hyperframes remove-background` |
| **B. Phụ đề từng từ có "bóng" từ kế tiếp**: từ sắp nói hiện mờ trước, rồi sáng lên khi được nói; từ khóa màu vàng | 02, 03, 05, 06, 07, 12, 15 | `vkit captions` (karaoke), HyperFrames `caption-highlight`, CapCut auto-caption + keyframe |
| **C. UI giả lập** (chat Claude, checklist, trình dựng, đồng hồ) làm bằng HTML rồi animate | 03, 06, 07, 11, 12 | HyperFrames/Remotion (HTML/React), Figma → After Effects |
| **D. Máy quay số** (zoom, lùi, dolly) có motion blur ở khung nhanh nhất | 05, 09, 11, 15 | Keyframe scale + motion blur; HyperFrames `data-motion-blur="on"` |
| **E. Nét vẽ tay / giấy** (stroke-on, boil, cắt dán) | 13, 14 | AE Trim Paths + Wiggle Path; HyperFrames `hw-*`, `paper-collage-reveal` |

**Ngôn ngữ hình chung**: một màu nhấn vàng (~#FFE14D, có glow), chữ sans đậm (kiểu Inter Black) cho
phụ đề, serif (Didone / italic) cho chữ "thời trang", nền kem cho UI, mọi thứ vào bằng **blur-in nhanh**
(~0,1–0,2s) thay vì trượt.

## Kế hoạch quay: một buổi đủ footage cho cả 17

Tác giả dùng **một căn hộ, 4 thiết lập máy**, mặc một bộ đồ (áo khoác olive, mũ ngược), quay iPhone dọc:

| Thiết lập | Góc | Dùng cho | Ghi chú khi quay |
|---|---|---|---|
| **S1 · Ngồi sàn cạnh sofa** | Máy đặt sàn, ngửa lên (low angle), toàn thân | 01, 03, 07, 08 | Chừa nhiều tường trống phía sau đầu để dán thẻ, giấy |
| **S2 · Ghế bành, góc rộng** | Máy thấp, rộng, thấy cửa sổ, đèn tường | 09, 15, 17, 01 | Khung tĩnh trên tripod để zoom số, dolly số không rung |
| **S3 · Sofa xanh, chính diện** | Ngang hông, toàn thân | 02, 12, 13, 14, 16 | Nền tách bạch với áo và tóc để matte sạch; chừa khoảng trên đầu cho chữ "EDIT" |
| **S4 · Selfie cầm tay** | Cận, cầm điện thoại | 04, 05, 06, 10, 11 | Cử chỉ tay hướng lên/sang ngang để "khớp" với đồ họa (chart đi lên, chỉ vào điện thoại) |

Quy tắc khi quay để dễ dựng hiệu ứng:
- **Tripod + khóa phơi sáng/lấy nét** cho mọi shot sẽ tách nền hoặc zoom số.
- Quay **4K hoặc 1080p 60fps** để zoom số 150–250% vẫn nét.
- **Diễn cử chỉ có chủ đích** cho đồ họa sẽ thêm vào: tay vuốt lên cho chart, giơ tay ra khung cho
  frame break, chỉ sang bên cho phone mockup.
- **Chừa khoảng trống** đúng chỗ đồ họa sẽ nằm (tường sau đầu, phần trên khung).
- Áo khác màu tường; tránh tóc rối trên nền rối để matte không lem.

---

## 01 · Orbit (thẻ bay quanh người)
- **Thấy gì (0,00–0,68s)**: người ngồi sàn (S1). 5–6 thẻ dọc nhỏ (ảnh chụp các video và bài đăng khác
  của tác giả) bay theo một vòng elip quanh thân: thẻ lớn hơn khi ở phía trước, nhỏ và mờ khi ở phía
  sau. Chữ: dòng sans nhỏ "and you can get the" hiện từng từ, rồi **"cool girl"** serif nghiêng màu vàng
  nhạt, có sao ✦ lấp lánh hai bên, rồi "aesthetic" xám nhỏ bên dưới.
- **Cơ chế**: nền → các thẻ *ở nửa sau* vòng → người (cutout) → các thẻ *ở nửa trước* → chữ. Vị trí thẻ
  theo góc θ(t): x = cx + R·cosθ, y = cy + r·sinθ, scale và độ mờ theo sinθ (sâu thì nhỏ và mờ).
- **Dựng**: HyperFrames `carousel-orbit-*` / `three-orbiting-cards` đặt dưới cutout (viên gạch A).
  CapCut: 2 track thẻ (sau/trước) và track "Xóa nền" ở giữa, keyframe vị trí theo vòng.
- **Lỗi hay gặp**: thẻ không đổi lớp trước/sau nên trông như dán phẳng. Vòng quay quá chậm (ở đây
  ~1 vòng/2–3s).

## 02 · Couch wall (tường bằng chứng)
- **Thấy gì (0,68–1,64s)**: người ngồi sofa (S3, low angle). Từ 0,80s, ảnh chụp màn hình các video viral
  (có lượt xem: 1.07M, 534K, 133K) **bật lên trên tường phía sau người**, mỗi thẻ cách nhau ~2 khung,
  blur→nét, tới ~1,13s thì phủ kín tường. Người luôn ở *trên* các thẻ. Chữ: "selling a" nhỏ, rồi
  **"course"** rất to, đậm, blur-in.
- **Cơ chế**: nền → lưới thẻ (stagger 40–80ms, scale 0.9→1, blur 6→0px) → cutout người → chữ.
- **Dựng**: HyperFrames `mk-clone-wall-transition` / `logo-wall` dưới cutout. CapCut: mỗi thẻ một
  track, animation "Pop in", đặt dưới lớp người đã xóa nền.
- **Ý nghĩa**: bằng chứng xã hội dồn dập đúng lúc nói "selling a course".

## 03 · UI world (thế giới giao diện)
- **Thấy gì (1,64–2,56s)**: màn hình **chia đôi**: nửa trên là giao diện chat kiểu Claude (nền kem,
  logo ✱, ô "Drop files here"); nửa dưới là người ngồi sàn (S1) bị crop. 5 thumbnail clip **rơi từ
  trên vào ô thả**. Ô thả **morph** thành ô chat "How can I help you today?" chứa 5 thumbnail và một
  chip "RAW CLIPS" được **tô dạ quang vàng** (vệt highlight quét qua). Rồi chữ gõ "/video-edi…" (lệnh
  slash). Phụ đề "DROP" → "DROP CLIPS" → "TRIGGER THE".
- **Cơ chế**: UI HTML có 3 trạng thái (drop zone → input có file → đang gõ lệnh), mỗi trạng thái gắn với
  một từ trong lời thoại.
- **Dựng**: HyperFrames `claude-exchange`, `typed-prompt`, `cursor-drag-drop`, `marker-highlight`.
  Không có code: dựng UI trong Figma, export từng trạng thái, rồi dùng morph/smart animate.

## 04 · Frame break (phá khung)
- **Thấy gì (2,56–3,42s)**: selfie cận toàn màn (S4) → trong ~0,2s, video **thu nhỏ thành một thẻ bo góc**
  giống bài đăng Instagram (tim, bình luận, chia sẻ, @tenfoldmarc, Follow), nền xung quanh tối và mờ.
  Nhưng **tay và đầu người vẫn tràn ra ngoài mép thẻ** (2,67s trở đi).
- **Cơ chế**: nền mờ tối → thẻ (video bị crop trong khung + UI IG) → **cutout người cùng scale, không bị
  crop** đè lên trên, nên phần tay vượt khỏi khung trông như "phá khung".
- **Dựng**: HyperFrames `vfx-portal` / tự dựng: `clip-path` cho thẻ + cutout không clip. CapCut: nhân
  đôi track, track dưới thêm mask hình chữ nhật bo góc, track trên xóa nền.
- **Khi quay**: phải có cử chỉ tay *đưa ra ngoài khung* (vươn về phía máy) thì hiệu ứng mới đã.

## 05 · Digital zoom (punch-in số)
- **Thấy gì (3,42–4,54s)**: selfie (S4), phụ đề một dòng nhỏ "or know anything about". Ở 3,73s có
  **1–2 khung nhòe chuyển động**, rồi khung hình **cận hơn hẳn** (mặt to ~1,4×). Phụ đề đổi sang chữ to
  "**video**" và "**editing**" vàng (blur-in từng từ).
- **Cơ chế**: scale 1.0 → ~1.4 trong ~0,1s, motion blur ở khung nhanh nhất, **rơi đúng từ khóa**. Đồng thời
  đổi phong cách phụ đề (nhỏ → to) để đánh dấu cao trào.
- **Dựng**: keyframe scale + motion blur (CapCut: "Zoom in" + "Motion blur"). HyperFrames `push-in` /
  `cinematic-zoom` trên wrapper (không tween trực tiếp lên `<video>`).

## 06 · Phone mockup (điện thoại nổi cạnh mặt)
- **Thấy gì (4,54–5,50s)**: selfie cận (S4). Một **iPhone 3D** đứng cạnh đầu, màn hình là app chat "Ads
  Assistant": dấu "…" đang gõ → tin nhắn "Pause Ad 3, move the budget to Ad 1" kèm **vệt sáng chéo quét
  qua màn kính** (4,60s) → nút "Approve" hiện ra → một **chấm chạm** (touch indicator) di chuyển tới
  và nhấn Approve (5,07–5,27s). Phụ đề "all you need to do" hiện từng từ, từ kế tiếp mờ.
- **Cơ chế**: mockup thiết bị + màn hình HTML có trạng thái + glare + con trỏ chạm.
- **Dựng**: HyperFrames `vfx-iphone-device` / `device-frame-stage` + `gesture-tap` / `touch-indicator`
  + `gloss-sweep`.

## 07 · Checklist (danh sách tự tick)
- **Thấy gì (5,50–6,32s)**: shot rộng ngồi sàn (S1). Một **bảng kính tối mờ** (frosted) ở 1/3 trên: tiêu
  đề nhỏ "• ALL YOU NEED TO DO", bộ đếm "0 of 3" và thanh tiến độ. Có 3 dòng skeleton. Khi nói "Drop
  your clips": chữ dòng 1 blur-in từng từ, dòng được tô nền, vòng tròn → **dấu tick vàng pop** (to rồi
  co về), chữ chuyển vàng, bộ đếm "1 of 3", thanh tiến độ vàng 1/3. Sau đó dòng 2 "Trigger the skill"
  bắt đầu gõ vào.
- **Dựng**: HyperFrames `marker-checklist-card`, `mk-specs-list`, `success-check`, `onboarding-stepper-flow`.
  Đặt checklist ở vùng trên, người ở vùng dưới.

## 08 · Headline wall (tường tiêu đề)
- **Thấy gì (6,32–7,32s)**: ngồi sàn cạnh sofa (S1). Giấy ghi chú, **tiêu đề báo** serif ("Claude edits
  everyone's videos now", "Claude cut my whole reel"), thẻ tweet, thanh tìm kiếm "can claude edit
  videos", thẻ đen "POV:" lần lượt **bật lên tường sau đầu**, hơi nghiêng ±3–8°, phủ dày dần trong ~0,8s.
  Thẻ cuối "Claude can edit your videos now" có chữ "Claude" **tô dạ quang vàng**.
- **Khác 02**: 02 là bằng chứng *số liệu* (lượt xem), 08 là bằng chứng *dư luận* (báo, tweet, search).
- **Dựng**: HyperFrames `notes-reveal`, `x-post`, `notification-pileup` dưới cutout; `marker-highlight` cho thẻ cuối.

## 09 · Zoom-through cut (zoom xuyên cảnh)
- **Thấy gì (7,32–8,62s)**: shot rộng ghế bành (S2) với chữ serif "cool girl aesthetic" → 7,60s máy
  **lao thẳng vào người** (scale tăng mạnh, nhòe chuyển động) → 7,80–7,90s **nhòe xuyên tâm** (radial
  zoom blur) gần như trừu tượng → **ra cảnh mới** (ghế bành khác góc) cũng từ trạng thái nhòe xuyên tâm
  rồi nét lại ở 8,07s. Phụ đề đổi phong cách: chữ in hoa nhỏ, giãn chữ rất rộng "OR  YOU  CAN  GET  THE".
- **Cơ chế (theo số đo HyperFrames)**: cảnh ra scale ~1 → 2.5 trong ~0,35s với ease-in mạnh (`power3.in`)
  và radial blur tăng. Cảnh vào bắt đầu to và nhòe, ease-out về 1. **Cắt ở khung nhanh nhất.**
- **Dựng**: HyperFrames `zoom-through-transition`; CapCut transition "Zoom in" / "Pull in" + "Radial blur".

## 10 · Chart grow (biểu đồ mọc sau lưng)
- **Thấy gì (8,62–9,42s)**: selfie (S4). Phía sau đầu là một **biểu đồ đường**: nhãn thứ M T W T F S S
  trên cùng, các đường gióng nét đứt, một **đường phát sáng vàng vẽ dần từ trái sang phải và đi lên**,
  kết bằng chấm sáng ở "S". Pill vàng "**SCALE ↗**" pop ở cột F. **Tay người che lên đường biểu đồ**,
  tức là biểu đồ nằm *dưới* cutout. Cử chỉ tay đi lên cùng nhịp đường.
- **Dựng**: HyperFrames `animated-bar-chart` / `mk-line-graph` / `svg-stroke-trace` dưới cutout;
  `badge-pop` cho pill. CapCut: vẽ đường bằng mask "Linear" chạy keyframe.
- **Khi quay**: diễn cử chỉ vuốt tay đi lên.

## 11 · Pull-back reveal (lùi ra lộ ra phần mềm)
- **Thấy gì (9,42–10,68s)**: clip talking-head toàn màn **thu lại thành cửa sổ app** "test-slot.mp4 · Assistant"
  trên nền kem. Một panel "Working on [edit]" trượt vào bên trái, các bước lần lượt quay vòng → tick
  xanh: Transcribed 1 clip → Picked the take → Cut 3 shots → Captions added → Rendered 150 frames.
  Dưới clip là thanh render có waveform chạy xanh dương "089/150 → 150/150" rồi **chuyển xanh lá** khi
  xong. Góc trái trên có **số serif lớn lăn kiểu máy đánh bạc** 37 → 62 → 98 → **100%** (huy hiệu xanh dương).
- **Ý nghĩa**: lộ ra rằng video đang xem *chính là* sản phẩm được dựng, một cú meta reveal.
- **Dựng**: HyperFrames `pull-back-reveal` / `parallax-unzoom` + `notes-typing` / `onboarding-stepper-flow`
  + `count-up` / `slot-machine-roll` / `number-wheel`.

## 12 · Green screen (đổi nền sang giao diện)
- **Thấy gì (10,68–11,68s)**: shot sofa chính diện (S3) → 10,80s **blur chuyển** → người (cutout) đứng
  trước một **trang web**: dải gradient tím–xanh, thanh "FOCUS 49:57 Write the sales page · End sprint"
  (đồng hồ đếm ngược thật: 49:57 → 49:56), danh sách việc, ô chat có con trỏ. Phụ đề **hộp đen chữ
  trắng** "you need **edits**" (edits vàng) + dòng serif "✱ Everything else waits." **nằm sau đầu người**.
- **Cơ chế**: nền UI → chữ serif → cutout người → phụ đề hộp đen.
- **Dựng**: `segmentation-flood` / `remove-background` + UI HTML. CapCut: "Xóa nền" + ảnh hoặc video UI
  làm nền dưới.

## 13 · Paper cut (cắt dán giấy)
- **Thấy gì (11,68–12,68s)**: người cutout có **viền sticker trắng + mép giấy xé răng cưa**, đặt trên nền
  giấy kẻ ô màu ngà, có các mảng **sáp màu** (khối nguệch ngoạc tím lavender, mảnh giấy vàng xé, nét
  hồng, dấu X, vòng xoắn). Chữ kiểu **thư nặc danh (ransom note)**: "1", "0", "0", "%" lần lượt pop,
  mỗi chữ một mảnh giấy, font và màu khác nhau, hơi xoay. Sau đó một **vòng elip đỏ vẽ tay** khoanh "100%".
  Chuyển động hơi giật kiểu stop-motion.
- **Dựng**: HyperFrames `paper-collage-reveal`, `torn-paper-rip`, `stop-motion-cadence`, `hw-callout-circle`.
  CapCut: cutout + "Stroke" trắng + sticker giấy; giảm fps phần đồ họa xuống ~12 cho cảm giác stop-motion.

## 14 · Doodle boil (nét vẽ tay rung rinh)
- **Thấy gì (12,68–13,68s)**: shot tối, ngồi sofa (S3). Người có **viền phấn trắng vẽ tay** bám theo dáng,
  nét **rung nhẹ mỗi ~2 khung** (boil). Các doodle được **vẽ dần** (stroke-on): trái tim tô sáp hồng có
  tia lấp lánh, một hình chữ nhật biến thành **clapperboard** rồi được tô sọc hồng, một ô vuông nhỏ.
- **Cơ chế**: viền = đường bao của matte, thêm nhiễu và vẽ lại mỗi 2 khung; doodle = SVG path + trim.
- **Dựng**: HyperFrames `hw-boil`, `outline-draw`, `svg-line-draw-loader`, `hw-scribble-transition`.
  AE: Stroke effect trên matte + "Wiggle Paths" với posterize time 12fps.

## 15 · Vertigo (dolly zoom)
- **Thấy gì (13,68–14,70s)**: ghế bành góc rộng (S2). Trong ~1s **nền giãn ra** (tường, cửa sổ đổi phối
  cảnh) trong khi người giữ kích thước gần như cũ, nên có cảm giác chóng mặt kiểu Hitchcock. Phụ đề
  "SUCK" → "SUCK AT" → "SUCK AT **DESIGN**" (vàng).
- **Cơ chế số** (không cần dolly thật): scale **nền** và **cutout người** ngược chiều nhau (nền 1→1.25,
  người giữ nguyên hoặc 1→0.95), ease `power2.inOut`. Muốn thật hơn thì quay dolly thật kết hợp zoom ống kính.
- **Dựng**: HyperFrames `camera-dolly-zoom`.

## 16 · Cover story (bìa tạp chí)
- **Thấy gì (14,70–15,72s)**: shot sofa (S3). Chữ **"EDIT"** serif Didone khổng lồ (kiểu masthead Vogue)
  **mọc lên từ dưới qua mặt nạ** (14,67–15,07s), nằm **sau đầu người** (mũ đè lên chữ). Thêm **khung viền
  trắng mảnh** quanh mép như bìa tạp chí và tông màu hơi bạc, phẳng.
- **Cơ chế**: nền → chữ (mask reveal từ dưới) → cutout người → khung viền. Theo HyperFrames: chữ sau người
  bị che **30–55%** là đẹp nhất.
- **Dựng**: HyperFrames `titlecard-lockup` + cutout; `svg-mask-reveal`. CapCut: chữ + mask + đặt dưới lớp xóa nền.
- **Khi quay**: chừa 1/4 trên khung, đầu thấp hơn mép trên.

## 17 · Glass type (chữ kính 3D)
- **Thấy gì (15,72–16,50s)**: ghế bành góc rộng (S2). Chữ **"DESIGN" 3D bằng kính/chrome** đặt *trong
  phòng*, dán theo phối cảnh tường (nghiêng), khúc xạ nền phía sau, có **vệt sáng chạy qua**. Chữ hiện
  từ trong suốt sang rõ (15,74–15,94s) rồi đứng yên, ánh sáng tiếp tục lướt.
- **Dựng**: HyperFrames `glass-hero`, `glass-shard-title`, `ios26-liquid-glass`, `light-sweep-pass`
  (khớp phối cảnh bằng CSS 3D transform). Blender hoặc Spline nếu cần thật hơn.

---

## Nhịp chung của cả chuỗi (để áp vào video của bạn)
- Mỗi hiệu ứng **bắt đầu đúng từ đầu tiên của tên nó** và kết thúc khi tên kế tiếp bắt đầu (word-anchored).
  Đây chính là tinh thần "neo theo từ" của hypit (xem `docs/13`).
- **Phần lõi của hiệu ứng xảy ra trong 0,3s đầu** (pop, zoom, morph), phần còn lại là "trạng thái đã đáp"
  để mắt kịp đọc.
- Mỗi demo tự có **phụ đề riêng của nó**: khoe luôn phong cách phụ đề như một phần của hiệu ứng.
- Nhiều clip demo được quay **cùng buổi, cùng trang phục**, nên chuỗi 17 cảnh khác nhau vẫn liền mạch.
