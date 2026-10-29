# 13 · Kịch bản neo theo từ: kiến trúc học từ hypit

## Ý tưởng cốt lõi

Dựng video truyền thống đặt mọi thứ theo **giây**: B-roll từ 3,2s đến 4,8s, chữ hiện ở 7,1s. Chỉ cần đọc
lại một câu nhanh hơn, hoặc đổi một chữ, là mọi thứ phía sau lệch hết và phải kéo tay lại.

Hypit (SVML) đảo ngược điều đó: **kịch bản là nguồn sự thật duy nhất**, và mọi thứ khác bám vào **từ**:

```
                       ┌─ thoại có vai ──────────► prompt video (Seedance/Veo/Kling)
                       ├─ chữ đọc (vế phải Dual) ─► TTS (ElevenLabs)
 script.vs ──(parse)──►├─ tài liệu phụ đề (cụm ||) ► phụ đề karaoke
 (lời + @{vùng nghĩa}) └─ Selection / Moment ─────┐
                                                  │   màn diễn thật (video/giọng)
                                                  ▼            │
                                   căn chỉnh từng từ ◄─────────┘  (WhisperX / mốc ký tự ElevenLabs)
                                                  │
                                                  ▼
                         Selection → [đầu, cuối] giây · Moment → giây
                                                  │
               ┌──────────────┬───────────────────┼──────────────────┬───────────────┐
               ▼              ▼                   ▼                  ▼               ▼
           B-roll         overlay / MG        SFX / nhạc         phụ đề        marker cho NLE
     during=@{proof}   during=@{chart}    at=@{reveal!}     theo cụm ||   (Premiere/Resolve)
```

Hệ quả:
- **Đổi lời hay diễn nhanh chậm → căn chỉnh lại → mọi thứ tự chạy theo.** Không cần kéo timeline bằng tay.
- **Một kịch bản, nhiều hình chiếu** (projection): cùng một nguồn ra thoại cho model video, chữ đọc cho
  TTS và phụ đề. Không còn ba bản copy lệch nhau.
- **Clone video viral** trở thành: viết lại kịch bản *với cùng các vùng nghĩa*. B-roll, hiệu ứng và SFX
  giữ nguyên quan hệ "hiện khi nói tới X".
- Đây chính là cách reel 17 hiệu ứng được dựng: mỗi demo bắt đầu đúng khi tên của nó được nói
  (`examples/tenfoldmarc-17-effects/reel.vs`).

## Cú pháp vscript (tập con của SVML, chạy bằng `scripts/vscript.py`)

| Viết | Nghĩa | Ví dụ |
|---|---|---|
| `<hook> … </hook>` | **Segment**: một đoạn diễn có tên, thường là một take A-roll | `<cta>Bấm giỏ hàng</cta>` |
| `<pause/>` | Segment không lời | |
| `<HOST>` | **Vai** nói (bên trong Segment), áp dụng tới vai kế tiếp | `<HOST> … <GUEST> …` |
| `<hiển thị\|đọc>` | **Dual Text**: chữ trên màn khác với chữ đọc | `<TikTok\|tíc tóc>`, `<15%\|mười lăm phần trăm>` |
| `<New York\|>` | Gom một cụm thành một đơn vị phụ đề | |
| `<\|chỉ đọc>` | Đọc nhưng không hiện phụ đề | |
| `\|\|` | Ngắt **cụm phụ đề** | `Bro has \|\| more hair gel` |
| `chữ{emphasis}` | **Thuộc tính** cho từ ngay trước (không cách) → tô màu nhấn | `sáng{emphasis}` |
| `@{proof} … @{/proof}` | **Selection**: khoảng nghĩa có tên | B-roll bám vào |
| `@{reveal!}` | **Moment**: điểm nghĩa | SFX, cú pop |
| `@{~x}` / `@{/x~}` / `@{~x!}` | Đổi ranh giới: `~` trước = cuối từ trước; `~` sau = đầu từ sau | xem dưới |
| `<!-- … -->` | Ghi chú | |

### Ranh giới: khoảng lặng giữa hai câu thuộc về ai?

```text
@{coffee} my coffee @{/coffee}  @{~smoothie} my smoothie @{/smoothie}   ← khoảng lặng thuộc hình SAU
@{coffee} my coffee @{/coffee~} @{smoothie} my smoothie @{/smoothie}    ← khoảng lặng thuộc hình TRƯỚC
```

Reel mẫu dùng kiểu thứ hai: demo cũ giữ hình qua khoảng lặng, cắt đúng lúc tên mới được nói.

### Ví dụ tiếng Việt

```text
<script>
<hook>
  <HOST>
  Da xỉn màu @{pain}dù đã skincare đủ bước?@{/pain} || Lỗi nằm ở @{reveal!}bước{emphasis} này.
</hook>
<body>
  <HOST>
  @{proof}Serum vitamin C 15% || dùng ba ngày || là thấy da sáng{emphasis} lên.@{/proof}
</body>
<cta>
  <HOST>
  Bấm giỏ hàng || <TikTok|tíc tóc> Shop đang giảm{emphasis} 30%.
</cta>
</script>
```

## Lệnh

```bash
python3 scripts/vscript.py check    script.vs                 # cấu trúc: Segment, vai, Selection, Moment
python3 scripts/vscript.py dialogue script.vs --segment hook  # "HOST: …" để dán vào prompt video
python3 scripts/vscript.py speech   script.vs --segment cta   # chữ đọc cho TTS (đã thay Dual Text)
python3 scripts/vscript.py estimate script.vs --lang vi       # ước lượng giây mỗi Segment → chọn độ dài request

# Sau khi có màn diễn thật:
python3 scripts/vscript.py align script.vs --media hook=assets/aroll/hook.mp4 --media body=... --language vi
python3 scripts/vscript.py align script.vs --media all=assets/aroll/full.mp4   # một video cho cả kịch bản
python3 scripts/vscript.py captions script.timing.json --upper                 # phụ đề theo cụm || đã viết
```

`align` so khớp từng token đọc với lời thật (thuật toán sắp xếp chuỗi, bỏ qua dấu tiếng Việt khi so) và
nội suy chỗ nhận dạng sai. Nó báo tỉ lệ khớp, **dưới 70% là có cảnh báo**. Nếu media là giọng đọc
ElevenLabs, mốc từng từ đã có sẵn trong `<file>.transcript.json` do `vaudio tts` ghi ra, không cần Whisper.

Kết quả `script.timing.json` được mọi công cụ khác đọc: `storyboard.py`, `vgen.py` (độ dài request,
thẻ prompt), `hf_listicle.py --timing`.

## So sánh với SVML đầy đủ của hypit

| | hypit SVML | vscript của kit |
|---|---|---|
| Kịch bản: Segment, Role, Dual Text, `\|\|`, thuộc tính, Selection, Moment | ✓ | ✓ (cùng cú pháp) |
| Sinh ảnh, video, giọng ngay trong file nguồn | ✓ (`<gpt:Image>`, `<seedance:ReferenceVideo>`) | tách sang `production.toml` + `vgen`/`vaudio` |
| Component (bảng xếp hạng, phụ đề, B-roll) tiêu thụ `during={story.selection.x}` | ✓ (render HTML trong hypit) | `during = "x"` trong production.toml → animatic, HyperFrames, XML cho Premiere/Resolve |
| Run / Candidate / tái sử dụng output | ✓ (`.svrun`) | `assets/gen/<shot>/` + `vgen pick` + log jsonl |
| Căn chỉnh | WhisperX | faster-whisper hoặc mốc ký tự ElevenLabs |

Kit giữ đúng **tư tưởng** (kịch bản là nguồn, neo theo từ, nhiều hình chiếu) nhưng để bạn dựng ở **bất kỳ
tool nào**. Khi cần sức mạnh đầy đủ (component dựng sẵn, clone hàng loạt), chuyển sang hypit: kịch bản
vscript chép gần như nguyên vào `<script id="story">`.
