"""
Từ vựng HSK — nguồn: github.com/drkameleon/complete-hsk-vocabulary (HSK 3.0, 1-6).

Data đã rút gọn ở data/hsk_vocab.json: 5363 từ, mỗi entry {s,p,m,r,f,l}
  s=simplified, p=pinyin, m=meanings(en), r=radical, f=frequency, l=HSK level.

Cung cấp hàm tra cứu cho tool search_vocab của agent. In-memory, nạp 1 lần.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_HERE, "data", "hsk_vocab.json")

_VOCAB: list[dict] = []
_BY_HANZI: dict[str, dict] = {}


def _ensure_loaded() -> None:
    if _VOCAB:
        return
    try:
        with open(_PATH, encoding="utf-8") as f:
            for e in json.load(f):
                _VOCAB.append(e)
                # ưu tiên entry level thấp hơn (phổ biến) nếu trùng chữ
                s = e["s"]
                if s not in _BY_HANZI or e["l"] < _BY_HANZI[s]["l"]:
                    _BY_HANZI[s] = e
    except Exception:
        pass


def lookup_word(word: str) -> dict | None:
    """Tra chính xác 1 từ theo chữ Hán giản thể."""
    _ensure_loaded()
    return _BY_HANZI.get((word or "").strip())


def search_vocab(query: str, level: int = 0, limit: int = 8) -> list[dict]:
    """Tìm từ HSK theo chữ Hán, pinyin, hoặc nghĩa (tiếng Anh).

    level=0: mọi level; level=1..6: chỉ level đó.
    Kết quả ưu tiên: khớp chữ chính xác > khớp pinyin > khớp nghĩa; rồi theo frequency.
    """
    _ensure_loaded()
    q = (query or "").strip().lower()
    if not q:
        return []

    scored = []
    for e in _VOCAB:
        if level and e["l"] != level:
            continue
        s = e["s"]
        p = e["p"].lower()
        m = e["m"].lower()
        score = 0
        if q == s:
            score += 100
        elif q in s:
            score += 50
        # pinyin: so cả có dấu lẫn không dấu
        if q == p or q == _strip_tone(p):
            score += 60
        elif q in p or q in _strip_tone(p):
            score += 30
        if q in m:
            score += 20
        if score:
            # frequency thấp (phổ biến) cộng điểm nhẹ
            scored.append((score - e["f"] / 100000, e))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]


def by_level(level: int, limit: int = 20) -> list[dict]:
    """Lấy các từ phổ biến nhất của một level HSK (sort theo frequency)."""
    _ensure_loaded()
    words = [e for e in _VOCAB if e["l"] == level]
    words.sort(key=lambda e: e["f"])
    return words[:limit]


_TONE_MAP = str.maketrans(
    "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüñ",
    "aaaaeeeeiiiioooouuuuuuuuun",
)


def _strip_tone(s: str) -> str:
    return s.translate(_TONE_MAP)


def stats() -> dict:
    _ensure_loaded()
    by_lvl = {}
    for e in _VOCAB:
        by_lvl[e["l"]] = by_lvl.get(e["l"], 0) + 1
    return {"total": len(_VOCAB), "by_level": by_lvl}
