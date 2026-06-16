# UI Redesign · Tab Học + Atlas + Gieo hạt

## Tóm tắt

Refactor toàn bộ flow chính của `ai-atlas.html`:
- **Bỏ tab Thế giới** (📷 camera) — không còn liên quan sau khi bỏ feature đọc biển hiệu
- **Rebuild tab Học** — thêm Spotlight chữ mới + Mini-quiz hiểu nghĩa
- **Redesign tab Atlas** — Hero current city + sub-cards điểm đến tương lai
- **Rebuild trang Gieo hạt** — gắn city đã chọn, không còn generic
- **Thêm nút Back** vào mọi màn hình
- **Fix translation nonsense** trong fallback generator
- **Đổi `c.topic` → `c.nameVi`** (tên Hán-Việt) ở nhiều chỗ
- **Tên thành phố theo level** trong picker (Hán → English → Hán-Việt)

## Thay đổi chi tiết

### 1. Bỏ tab Thế giới (📷)

**Trước:** 5 tabs · Atlas · Học · Phát âm · **Thế giới** · Hành trình
**Sau:** 4 tabs · Atlas · Học · Phát âm · Hành trình

Đã xoá:
- Entry `{s:'camera',ic:'📷',label:'Thế giới'}` khỏi `TABS[]`
- `case 'camera'` trong `render()`
- Functions `scrCamera`, `pickSign`, `nextSign`, `scanSign`
- Data `SIGNS{}`, biến `curSign`
- Nút "Đọc ngoài đời →" trong tab Học

### 2. Tab Học · Rebuild

**Layout mới (top → bottom):**

```
← Quay lại                          ⚙
SHANGHAI · Thượng Hải      ✦ AI i+1

LOST IN
SHANGHAI

──────────────────────────
你 好 (tap chữ → phát âm)
nǐ hǎo
"Xin chào"

✦ CHỮ MỚI HÔM NAY
┌─────────────────────────┐
│  好   hǎo  [Thanh 3]   │ ← tap chữ to → phát âm
│  ┐    "tốt"             │
│  │   Cấu thành: 女     │ ← tap pill → nghe bộ
│  ↑ Chạm chữ để nghe    │
└─────────────────────────┘

MÂY · HƯỚNG DẪN
[câu chuyện về city]

✓ Bạn đọc được 1/2 chữ — chỉ 好 là mới.

✓ HIỂU CHƯA?
好 (hǎo) — nghĩa là gì?
○ tốt   ○ lửa   ○ trà    ← +5 XP nếu đúng

[ ✓ Thuộc rồi → Câu tiếp theo ]  +10 XP
```

**Helper mới:**
- `toneOf(pin)` — detect thanh điệu 1-4 từ dấu pinyin
- `makeQuizOptions(rightVi, newChar)` — sinh 3 đáp án (1 đúng + 2 distractor)
- `quizAnswer(idx, rightIdx)` — handle click, +5 XP nếu đúng
- `markLearned()` — +10 XP rồi `go('lesson')` sinh câu mới

### 3. Tab Atlas · Redesign

**Trước:** Card current city và 5 mini cards (110px height) đều cùng cấp → mất focus.

**Sau:** Hierarchy rõ ràng:

```
★ THÀNH PHỐ HIỆN TẠI
┌────────────────────────────┐ ← 200px hero
│ [Poster Shanghai]      45% │
│                            │
│ 上海                       │ ← 34px gold
│ SHANGHAI                   │ ← 24px ivory
│ Thượng Hải                 │ ← 13px ivory mờ
│ ████░░░░░░░ progress       │
│              XEM CHI TIẾT ›│
└────────────────────────────┘
[ 📖 Tiếp tục bài học → ]

ĐIỂM ĐẾN TƯƠNG LAI   5 THÀNH PHỐ
Tập trung hoàn thành Thượng Hải trước.

┌────┬────┬────┐ ← 80px sub-cards
│成都│北京│杭州│
│CD  │BJ  │HZ  │
│Th.Đô│B.Kinh│H.Châu│
│CHƯA│CHƯA│CHƯA│
└────┴────┴────┘
┌────┬────┐
│西安│桂林│
└────┴────┘
```

### 4. Trang Gieo hạt · City-specific

**Trước:** Hard-code ⛰️→山, 3 cards toàn 山口人 cho mọi city.
**Sau:** Tied vào city đã chọn:

- Header: `Ngày 01 · Gieo hạt · {tên city Hán-Việt}`
- Ví dụ pictograph dùng radical đầu tiên của city (Thành Đô: 🔥→火, Thượng Hải: 🧍→人, Hàng Châu: 💧→水, …)
- 3 cards = 3 pictograph thật từ `CITIES[k].seed` (filter `rad:true` + có `pic`)
- Card có emoji + chữ + pinyin + nghĩa, tap-to-speak
- Bridge card xanh giải thích AI i+1 ở bước tiếp theo

### 5. Nút Back trên mọi màn hình

Thêm `S.history[]` stack + functions `go(s)`/`goBack(fallback)`/`backBtn(dark, fallback)`.

| Screen | Back fallback |
|---|---|
| citypick | onboard |
| seed | citypick |
| atlas | citypick |
| citydetail | atlas |
| lesson | atlas |
| tone | atlas |
| pinyin | tone |
| decode | progress |
| progress | atlas |

Onboard không có back. Style: top-left, "← Quay lại" — gold trên nền tối, navy trên nền sáng.

### 6. Fix translation nonsense

**Trước:** `genLocal()` ghép cứng → sinh ra "你好辣" = "Chào cay" (vô nghĩa).

**Sau:** 27 template câu đã verify thủ công, mỗi template có `hz` + `vi` (viết sẵn) + `newC`. Algorithm pick template đầu tiên thỏa `newC` chưa thuộc + mọi chữ khác đã thuộc.

Một số câu mẫu:
| Câu | Nghĩa | Chữ mới |
|---|---|---|
| 你好 | Xin chào | 好 |
| 我爱你 | Tôi yêu bạn | 爱 |
| 中国人 | Người Trung Quốc | 人 |
| 入口 | Lối vào | 入 |
| 火锅 | Lẩu (lửa + nồi) | 锅 |
| 吃火锅 | Ăn lẩu | 吃 |
| 好辣 | Cay quá | 辣 |
| 喝茶 | Uống trà | 茶 |
| 山水 | Núi sông | 水 |

LLM path (`genLLM` với Claude API) không đổi.

### 7. Đổi `c.topic` → `c.nameVi`

Thêm field `nameVi` vào CITIES:
- chengdu: "Thành Đô"
- shanghai: "Thượng Hải"
- beijing: "Bắc Kinh"
- hangzhou: "Hàng Châu"
- xian: "Tây An"
- guilin: "Quế Lâm"

Áp dụng `nameVi` ở:
- Card city picker (sub-title)
- Atlas hero card (sub-title)
- Atlas sub-cards (sub-title)
- Lesson header (`SHANGHAI · Thượng Hải`)
- Toast khi pick city
- Seed page header + bridge text

Remove `c.topic` (Ẩm thực / Công việc / Giao tiếp / Lối sống / Lịch sử · HSK / Thiên nhiên) khỏi UI. Vẫn giữ trong CITIES data vì `genLLM` prompt dùng làm context cho Claude.

### 8. Picker card · 3 level

**Trước:**
```
成都           45%
CHENGDU      In progress
Ẩm thực  (← không liên quan)
```

**Sau:**
```
成都           45%       ← Tiếng Trung (34px gold)
CHENGDU      In progress ← English (20px ivory)
Thành Đô                 ← Hán-Việt (13px ivory mờ)
```

### 9. Misc

- Bỏ ô đỏ "Cuối hôm nay bạn đọc được 入口" ở Seed page (hardcode Shanghai, không có ý nghĩa sau khi bỏ camera)
- Bỏ nút "↻ Câu khác" ở Lesson — gộp vào nút duy nhất "✓ Thuộc rồi → Câu tiếp theo" (+10 XP)
- Lesson hero: `overflow-y:auto` + `justify-content:flex-start` để content dài không bị clip

## File thay đổi

- `ai-atlas.html` — toàn bộ thay đổi
- (file `chat.html`, `main.py`, `poetry.py`, `pinyin_data.py` không đổi)

## Test plan

- [ ] Chọn 1 city ở picker (vd Thượng Hải) → vào Seed → thấy "Ngày 01 · Gieo hạt · Thượng Hải" + 3 hạt giống đúng (人/大/心)
- [ ] Vào Atlas → hero card hiển thị poster Thượng Hải, progress %, 5 sub-cards bên dưới
- [ ] Tap "Tiếp tục bài học →" → vào Học → header "SHANGHAI · Thượng Hải"
- [ ] Tap chữ Hán to trong Spotlight → nghe phát âm `zh-CN`
- [ ] Tap pill bộ thủ (vd 女 trong câu 好) → nghe phát âm bộ
- [ ] Mini-quiz: chọn đáp án đúng → +5 XP + highlight xanh; sai → highlight đỏ + sáng đáp án đúng
- [ ] Nút "✓ Thuộc rồi → Câu tiếp theo" → +10 XP + sinh câu mới
- [ ] Nút "← Quay lại" từ Lesson về Atlas, từ Atlas về Citypick, etc.
- [ ] Không xuất hiện câu nonsense kiểu "Chào cay" trong tab Học
- [ ] Tab Phát âm và bảng Pinyin vẫn hoạt động
