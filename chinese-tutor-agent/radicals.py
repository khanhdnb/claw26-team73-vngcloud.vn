"""
100 bộ thủ phổ biến nhất — nguồn: github.com/saigyo/common-chinese-radicals
(do Olle Linge / Hacking Chinese biên soạn). Nghĩa đã dịch sang tiếng Việt.

Data: data/radicals.json — mỗi entry {r, p, vi, v, ex}
  r=bộ thủ, p=pinyin(có dấu), vi=nghĩa tiếng Việt, v=biến thể, ex=chữ ví dụ.

Cung cấp tra cứu cho tool get_radical_info của agent. Nạp 1 lần.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_HERE, "data", "radicals.json")

_RADS: list[dict] = []
_BY_CHAR: dict[str, dict] = {}


def _ensure_loaded() -> None:
    if _RADS:
        return
    try:
        with open(_PATH, encoding="utf-8") as f:
            for e in json.load(f):
                _RADS.append(e)
                _BY_CHAR[e["r"]] = e
                # map cả biến thể về cùng entry (vd 亻 → 人)
                for var in (e.get("v") or "").replace("，", ",").split(","):
                    var = var.strip()
                    if var and var not in _BY_CHAR:
                        _BY_CHAR[var] = e
    except Exception:
        pass


def lookup(radical: str) -> dict | None:
    """Tra một bộ thủ theo ký tự chính hoặc biến thể."""
    _ensure_loaded()
    return _BY_CHAR.get((radical or "").strip())


def format_entry(e: dict) -> str:
    """Định dạng 1 bộ thủ thành chuỗi cho agent."""
    var = f" (biến thể: {e['v']})" if e.get("v") else ""
    ex = f" · Ví dụ: {e['ex']}" if e.get("ex") else ""
    return f"Bộ {e['r']} ({e['p']}){var} — {e['vi']}{ex}"


def search(query: str, limit: int = 6) -> list[dict]:
    """Tìm bộ thủ theo ký tự, pinyin, hoặc nghĩa tiếng Việt."""
    _ensure_loaded()
    q = (query or "").strip().lower()
    if not q:
        return []
    # ưu tiên khớp ký tự / biến thể chính xác
    exact = lookup(q)
    if exact:
        return [exact]
    scored = []
    for e in _RADS:
        score = 0
        p = e["p"].lower()
        if q == p or q in p or q == _strip_tone(p) or q in _strip_tone(p):
            score += 50
        if q in e["vi"].lower():
            score += 30
        if q in e.get("ex", ""):
            score += 20
        if score:
            scored.append((score, e))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]


_TONE_MAP = str.maketrans(
    "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü",
    "aaaaeeeeiiiioooouuuuuuuuu",
)


def _strip_tone(s: str) -> str:
    return s.translate(_TONE_MAP)


def stats() -> dict:
    _ensure_loaded()
    return {"total": len(_RADS)}
