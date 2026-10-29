# AI Video Kit — bộ đồ nghề làm video AI chất lượng cao

Kit này gom năm nguồn thành một quy trình dùng được ngay:

1. **Khóa học AI Creative** (tư duy giao việc, visual prompt, workflow sản xuất, kiểm soát nhất quán,
   ứng dụng thương mại, AI Yourself, game thực hành).
2. **Tay nghề đạo diễn rút từ [hypit](https://github.com/hypit-ai/hypit)**, một bộ công cụ mã nguồn mở
   dùng agent để clone video viral. Kit lấy phần *cách nghĩ* (đọc video tham chiếu, chỉ đạo ảnh/video,
   phụ đề, motion graphics, âm thanh) và diễn giải lại bằng tiếng Việt.
3. **Kinh nghiệm chuyển động và phụ đề của [HyperFrames](https://github.com/heygen-com/hyperframes)**
   (HeyGen), đo từng khung trên phim launch của họ, cùng so sánh với Remotion và Higgsfield ở `docs/11`.
4. **17 hiệu ứng mổ từng khung** từ reel @tenfoldmarc (`docs/12`), và **kiến trúc kịch bản neo theo từ**
   của hypit được dựng lại thành `vscript` (`docs/13`).
5. **Nghiên cứu thị trường của bạn** (bảng công cụ, build-vs-buy, Lean Canvas) ở `docs/10-cong-cu-va-chien-luoc.md`.

> Thông điệp xuyên suốt: **công cụ chỉ hỗ trợ sản xuất. Ý tưởng, gu, lựa chọn và hậu kỳ mới quyết định chất lượng.**

## Kit có gì

```
docs/                 Giáo trình tiếng Việt, mỗi file một kỹ năng
  00-lo-trinh-hoc.md      Lộ trình 6 tuần + bài tập/game mỗi tuần
  01-tu-duy-giao-viec.md  Khung VBNĐ (Vai trò–Bối cảnh–Nhiệm vụ–Định dạng), rèn gu, chấm điểm đầu ra
  02-visual-prompt.md     Prompt ảnh: 4 đoạn, 7 câu hỏi, casting, bối cảnh, bảng màu
  03-video-prompt.md      Prompt video: thái độ, hành động có lý do, quan hệ tham chiếu, nhịp cắt
  04-workflow-san-xuat.md Ý tưởng → ảnh chủ lực → concept → chuyển động → hậu kỳ
  05-kiem-soat-nhat-quan.md Storyboard, ảnh tham chiếu, khung đầu–cuối, cây phụ thuộc ảnh
  06-hau-ky.md            Phụ đề, motion graphics, B-roll, mix âm thanh, nhịp dựng, xuất file
  07-ung-dung-thuong-mai.md Quảng cáo sản phẩm, thay đồ, lookbook, TVC, UGC, nhãn AI
  08-ai-yourself.md       Số hóa bản thân, character bible, giọng nói
  09-giai-phau-video.md   Mổ xẻ video viral, kèm ví dụ đã làm
  10-cong-cu-va-chien-luoc.md Bản đồ công cụ, bảng giá, build vs buy
  11-stack-dung-video.md  hypit · HyperFrames · Remotion · Higgsfield: so sánh, license, con số chuyển động
  12-thu-vien-17-hieu-ung.md 17 hiệu ứng mổ từng khung: thấy gì, cơ chế lớp, cần quay gì, dựng bằng gì
  13-kich-ban-neo-theo-tu.md Kiến trúc kịch bản của hypit: lời là nguồn, hình/âm bám vào từ
  14-pipeline-da-model-da-tool.md Ảnh/video/âm thanh đa model (ưu tiên chính chủ) → storyboard → mọi tool dựng
templates/            Mẫu điền: BRIEF, TREATMENT, ANALYSIS, TIMELINE, STORYBOARD, CHARACTER,
                      PROMPT-IMAGE, PROMPT-VIDEO, QC-CHECKLIST, HOOK-BANK, script.vs, production.toml
  hyperframes/          Config mẫu cho hf_listicle.py (17 mục của reel mẫu)
config/models.toml    Danh mục model + thứ tự ưu tiên nhà cung cấp (OpenAI, BytePlus, ElevenLabs, fal, thủ công)
scripts/
  vkit.py             new · fetch · analyze · tile · captions · finish
  vscript.py          Kịch bản neo theo từ: check · dialogue · speech · estimate · align · captions
  vgen.py             Ảnh/video nhiều model: models · cards · run · pick
  vaudio.py           ElevenLabs: voices · design · save · tts (có mốc từng từ) · sfx · music
  storyboard.py       board (HTML) · animatic (MP4) · export xml|srt|csv|json|hf
  hf_listicle.py      Project HyperFrames "danh sách tô sáng + khung điện thoại"
.claude/skills/       /giai-phau-video · /len-brief · /viet-prompt · /san-xuat · /qc-video
examples/
  tenfoldmarc-17-effects/ Ca mổ xẻ reel "17 video effects" + kịch bản reel.vs neo theo từ
  demo-serum/             Dự án mẫu đầy đủ: script.vs + production.toml + storyboard + animatic
projects/             Nơi đặt từng dự án video của bạn (mỗi dự án một thư mục)
```

## Cài đặt

```bash
# macOS: brew install ffmpeg  ·  Ubuntu: sudo apt install ffmpeg
pip install yt-dlp faster-whisper          # Python 3.11+
```

Khóa API (chỉ cần cái bạn dùng; kit ưu tiên nhà cung cấp chính chủ, fal.ai là dự phòng):

```bash
export OPENAI_API_KEY=...       # ảnh: gpt-image-2.5
export ARK_API_KEY=...          # video: Seedance 2.0 qua BytePlus ModelArk
export ELEVENLABS_API_KEY=...   # giọng đọc, SFX, nhạc
export FAL_KEY=...              # dự phòng: Kling, Veo, Nano Banana, Seedance, GPT Image
```

Tùy chọn, skill dựng video bằng code cho Claude Code (cần Node 22+). Xem `docs/11` để chọn:

```bash
npx skills add hypit-ai/hypit -g          # clone video viral, ra hàng loạt biến thể
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes   # HTML → video, ~450 block MG/phụ đề
npx skills add remotion-dev/skills        # React → video
```

## Dùng nhanh

```bash
# 0. Tạo dự án
python3 scripts/vkit.py new demo

# 1. Tải và mổ xẻ một video viral
python3 scripts/vkit.py fetch "https://www.instagram.com/reel/XXXX/" --out projects/demo/references/ref1
python3 scripts/vkit.py analyze projects/demo/references/ref1/source.mp4 \
  --out projects/demo/references/ref1 --language en

# 2. Soi kỹ một đoạn 2 giây (mỗi 0,1s một khung)
python3 scripts/vkit.py tile projects/demo/references/ref1/source.mp4 --start 6.8 --end 8.8 --every 0.1

# 3. Hậu kỳ video của bạn: phụ đề karaoke + chuẩn TikTok + nhãn AI
python3 scripts/vkit.py captions projects/demo/output/draft.mp4 --language vi --upper
python3 scripts/vkit.py finish projects/demo/output/draft.mp4 --subs projects/demo/output/draft.ass \
  --label "Nội dung có sử dụng AI" --preset tiktok
```

Sản xuất từ kịch bản (xem `docs/13`, `docs/14` và `examples/demo-serum/`):

```bash
cd projects/demo                                   # đã có script.vs + production.toml từ `vkit new`
python3 ../../scripts/vscript.py check script.vs
python3 ../../scripts/storyboard.py board production.toml       # storyboard.html
python3 ../../scripts/storyboard.py animatic production.toml    # animatic với mốc ước lượng
python3 ../../scripts/vgen.py run production.toml --shot hero --model gpt-image,nano-banana --yes
python3 ../../scripts/vaudio.py tts production.toml --yes        # hoặc quay/generate A-roll
python3 ../../scripts/vscript.py align script.vs --media hook=assets/vo/hook.mp3 ...
python3 ../../scripts/storyboard.py export production.toml --to xml   # Premiere / Resolve
```

Dùng với Claude Code: mở repo này rồi gõ

```text
/giai-phau-video https://www.tiktok.com/@.../video/...
/len-brief Quảng cáo serum vitamin C, 25s, UGC, nhắm nữ 22–30
/viet-prompt Ảnh hero cho projects/serum/production.toml
/san-xuat projects/serum   (generate nhiều model, giọng ElevenLabs, align, storyboard, animatic, xuất XML)
/qc-video projects/serum/output/final_tiktok.mp4
```

## Quy trình một dự án (tóm tắt)

| Bước | Việc | File |
|---|---|---|
| 0 | Mổ xẻ 1–3 video tham chiếu | `references/*/ANALYSIS.md`, `TIMELINE.md` |
| 1 | Chốt mục tiêu của bạn | `BRIEF.md` |
| 2 | Đáp án sáng tạo của đạo diễn | `TREATMENT.md` |
| 3 | Kịch bản neo theo từ + shot gắn vào vùng nghĩa | `script.vs`, `production.toml`, `storyboard.html` |
| 4 | Ảnh chủ lực (hero) → so sánh nhiều model → chốt | `vgen run/pick`, `assets/` |
| 5 | Chuyển động + giọng: A-roll, B-roll, ElevenLabs | `vgen`, `vaudio`, rồi `vscript align` |
| 6 | Animatic → dựng: phụ đề, MG, B-roll, âm thanh | `storyboard animatic/export` → CapCut/Premiere/Resolve/HyperFrames |
| 7 | QC + xuất bản | `QC-CHECKLIST.md`, `vkit finish` |

Chi tiết xem `docs/04-workflow-san-xuat.md`.

## Ghi chú

- Video tham chiếu tải về chỉ dùng để học và phân tích. Không đăng lại nội dung của người khác.
  `.gitignore` đã chặn file media.
- Phần rút từ hypit được tóm lược và diễn giải lại, không chép nguyên văn. Bản gốc nằm trong
  `skills/hypit/references/` của repo hypit (giấy phép Apache-2.0 có điều kiện: được dùng nội bộ, kể cả
  cho thương mại; cấm chạy SaaS đa người thuê nếu chưa mua license).
