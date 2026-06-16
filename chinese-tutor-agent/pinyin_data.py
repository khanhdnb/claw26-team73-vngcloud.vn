"""
Bảng phiên âm Pinyin đầy đủ — kiến thức ngôn ngữ học chuẩn (giống bảng Yabla nhưng dạng text).

Cung cấp:
- 21 thanh mẫu (声母 initials) nhóm theo cách phát âm + so sánh tiếng Việt
- 39 vận mẫu (韵母 finals)
- Quy tắc đánh dấu thanh điệu (5 thanh)
- Các âm tiết đặc biệt (zhi/chi/shi/ri, zi/ci/si, yi/wu/yu, ü)
- Cảnh báo cặp âm người Việt hay nhầm

Dùng cho tool pinyin_chart trong agent. Không có audio (Yabla có, agent text thì không).
"""

# --- 21 THANH MẪU (Initials / 声母) ---
INITIALS = {
    "song môi & môi-răng": {
        "b": "như 'p' tiếng Việt nhưng KHÔNG bật hơi (爸 bà)",
        "p": "như 'p' tiếng Việt CÓ bật hơi mạnh (怕 pà)",
        "m": "như 'm' tiếng Việt (妈 mā)",
        "f": "như 'ph' tiếng Việt (发 fā)",
    },
    "đầu lưỡi": {
        "d": "như 't' tiếng Việt, KHÔNG bật hơi (大 dà)",
        "t": "như 'th' tiếng Việt, bật hơi (他 tā)",
        "n": "như 'n' tiếng Việt (你 nǐ)",
        "l": "như 'l' tiếng Việt (来 lái)",
    },
    "cuống lưỡi": {
        "g": "như 'c/k' tiếng Việt, KHÔNG bật hơi (哥 gē)",
        "k": "như 'kh' tiếng Việt, bật hơi (口 kǒu)",
        "h": "như 'h' tiếng Việt nhưng nặng hơn, hơi như 'kh' nhẹ (好 hǎo)",
    },
    "mặt lưỡi": {
        "j": "gần 'ch' tiếng Việt nhưng mềm, lưỡi áp vòm (鸡 jī)",
        "q": "như 'j' nhưng bật hơi mạnh (七 qī)",
        "x": "gần 'x' tiếng Việt, lưỡi áp vòm trên (西 xī)",
    },
    "lưỡi cong (uốn lưỡi)": {
        "zh": "uốn lưỡi, gần 'tr' tiếng Việt, KHÔNG bật hơi (中 zhōng)",
        "ch": "uốn lưỡi, như 'zh' CÓ bật hơi (吃 chī)",
        "sh": "uốn lưỡi, gần 's' nặng / 'sh' (是 shì)",
        "r": "uốn lưỡi, gần 'r' tiếng Anh, KHÔNG rung như 'r' tiếng Việt (日 rì)",
    },
    "đầu lưỡi trước (xuýt)": {
        "z": "như 'ch' nhẹ không bật hơi, lưỡi sát răng (字 zì)",
        "c": "như 'z' CÓ bật hơi, giống 'ts' (菜 cài)",
        "s": "như 's' tiếng Việt, êm (四 sì)",
    },
}

# --- 39 VẬN MẪU (Finals / 韵母) ---
FINALS = {
    "đơn (single)": ["a", "o", "e", "i", "u", "ü"],
    "kép (compound)": ["ai", "ei", "ao", "ou", "ia", "ie", "ua", "uo", "üe", "iao", "iou(iu)", "uai", "uei(ui)"],
    "mũi trước -n": ["an", "en", "in", "un", "ün", "ian", "uan", "üan", "uen"],
    "mũi sau -ng": ["ang", "eng", "ing", "ong", "iang", "uang", " ueng", "iong"],
    "cong lưỡi -r": ["er"],
}

# --- 5 THANH ĐIỆU ---
TONES = """5 THANH ĐIỆU (lấy âm 'ma' làm ví dụ):
1. Thanh 1 (阴平) — dấu ¯ : mā — cao, bằng, kéo dài đều. Như hát nốt cao giữ nguyên.
2. Thanh 2 (阳平) — dấu ´ : má — đi LÊN từ trung tới cao. Gần thanh sắc/hỏi-lên tiếng Việt.
3. Thanh 3 (上声) — dấu ˇ : mǎ — XUỐNG rồi LÊN (hình chữ V). Gần thanh hỏi tiếng Việt.
4. Thanh 4 (去声) — dấu ` : mà — đi XUỐNG dứt khoát từ cao. Gần thanh nặng/huyền-xuống.
5. Thanh nhẹ (轻声) — KHÔNG dấu : ma — nhẹ, ngắn, không nhấn (vd 妈妈 māma)."""

# --- QUY TẮC ĐÁNH DẤU THANH ---
TONE_RULES = """QUY TẮC ĐÁNH DẤU THANH ĐIỆU:
1. Dấu đặt trên NGUYÊN ÂM chính (a, o, e, i, u, ü).
2. Thứ tự ưu tiên: a > o > e > i > u > ü.
   - Có 'a' → đánh trên a (hǎo, xià)
   - Không có a, có o hoặc e → đánh trên đó (gǒu, hēi)
   - 'iu' và 'ui' → đánh trên chữ ĐỨNG SAU (liú, guì)
3. Dấu trên 'i' thì bỏ chấm: ī í ǐ ì.
4. Thanh nhẹ không đánh dấu."""

# --- ÂM TIẾT ĐẶC BIỆT ---
SPECIAL = """ÂM TIẾT & QUY TẮC ĐẶC BIỆT:
• zhi / chi / shi / ri — 'i' ở đây KHÔNG đọc 'i', mà là âm ngậm uốn lưỡi (gần 'ư').
• zi / ci / si — 'i' đọc như âm 'ư' ngắn ở đầu lưỡi, KHÔNG phải 'i'.
• i, u, ü khi đứng MỘT MÌNH (không có thanh mẫu) viết thành: yi, wu, yu.
  - i → yi, in → yin, ing → ying
  - u → wu
  - ü → yu, üe → yue, üan → yuan, ün → yun
• ü sau j/q/x/y → viết thành 'u' (ju, qu, xu, yu) nhưng VẪN đọc 'ü'.
• ü chỉ giữ 2 chấm sau n, l: nü (女), lü (绿) — phân biệt với nu, lu."""

# --- CẶP DỄ NHẦM (cho người Việt) ---
COMMON_CONFUSIONS = """CẶP ÂM NGƯỜI VIỆT HAY NHẦM:
• b/p, d/t, g/k — khác nhau ở BẬT HƠI (p/t/k bật hơi mạnh), không phải đục/trong.
• zh/ch/sh (uốn lưỡi) vs z/c/s (lưỡi thẳng) — phải uốn lưỡi cong lên vòm.
• j/q/x vs zh/ch/sh — j/q/x lưỡi áp vòm trước (mềm), zh/ch/sh uốn cong (cứng).
• n vs ng ở cuối — an/ang, en/eng khác nhau rõ (giống tiếng Việt).
• 'e' đơn (e) đọc như 'ơ' (饿 è), KHÁC 'e' trong 'ie/ei' (đọc gần 'ê')."""


def full_chart() -> str:
    """Trả về toàn bộ bảng pinyin dưới dạng text có cấu trúc."""
    parts = ["═══ BẢNG PHIÊN ÂM PINYIN ═══\n"]
    parts.append("【21 THANH MẪU — 声母 / Initials】")
    for group, items in INITIALS.items():
        parts.append(f"\n▸ {group}:")
        for sym, desc in items.items():
            parts.append(f"   {sym:4} — {desc}")
    parts.append("\n【39 VẬN MẪU — 韵母 / Finals】")
    for group, items in FINALS.items():
        parts.append(f"▸ {group}: {', '.join(s.strip() for s in items)}")
    parts.append("\n" + TONES)
    parts.append("\n" + TONE_RULES)
    parts.append("\n" + SPECIAL)
    parts.append("\n" + COMMON_CONFUSIONS)
    return "\n".join(parts)


def lookup(query: str) -> str:
    """Tra một thanh mẫu, vận mẫu, hoặc chủ đề pinyin cụ thể."""
    q = (query or "").strip().lower()
    if not q or q in ("all", "full", "bảng", "chart", "toàn bộ"):
        return full_chart()

    hits = []
    # tra initial
    for group, items in INITIALS.items():
        for sym, desc in items.items():
            if q == sym or q in sym:
                hits.append(f"Thanh mẫu '{sym}' ({group}): {desc}")
    # tra chủ đề
    if q in ("thanh", "thanh điệu", "tone", "tones", "dấu"):
        hits.append(TONES + "\n\n" + TONE_RULES)
    if q in ("đặc biệt", "special", "zhi", "chi", "shi", "ri", "zi", "ci", "si", "yi", "wu", "yu", "ü", "v"):
        hits.append(SPECIAL)
    if q in ("nhầm", "lẫn", "confusion", "khó"):
        hits.append(COMMON_CONFUSIONS)
    # tra final
    for group, items in FINALS.items():
        for fin in items:
            if q == fin.strip():
                hits.append(f"Vận mẫu '{q}' thuộc nhóm: {group}")

    return "\n\n".join(hits) if hits else full_chart()
