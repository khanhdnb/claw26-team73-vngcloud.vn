"""
Kho thơ ca / kinh điển Hán văn — nguồn: github.com/chinese-poetry/chinese-poetry (MIT).

Chuẩn hóa 4 bộ data về một schema chung rồi cung cấp hàm tìm kiếm cho agent.
Schema chuẩn: {"title", "author", "source", "lines": [str, ...]}

Data nằm trong ./data/*.json, được nạp 1 lần khi import (in-memory, không DB).
"""
import json
import os

try:
    from zhconv import convert as _zh_convert

    def _to_simplified(text: str) -> str:
        return _zh_convert(text or "", "zh-hans")
except Exception:  # zhconv không có → không chuyển đổi, vẫn chạy
    def _to_simplified(text: str) -> str:
        return text or ""

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "data")

# Bộ nhớ thơ đã chuẩn hóa
_POEMS: list[dict] = []


def _load_shijing(path: str) -> list[dict]:
    # list[{title, chapter, section, content[]}]
    out = []
    with open(path, encoding="utf-8") as f:
        for it in json.load(f):
            out.append({
                "title": it.get("title", ""),
                "author": "佚名 (khuyết danh)",
                "source": f"诗经 · {it.get('chapter','')}{it.get('section','')}".strip(" ·"),
                "lines": it.get("content", []),
            })
    return out


def _load_lunyu(path: str) -> list[dict]:
    # list[{chapter, paragraphs[]}]
    out = []
    with open(path, encoding="utf-8") as f:
        for it in json.load(f):
            out.append({
                "title": it.get("chapter", ""),
                "author": "孔子及弟子 (Khổng Tử và môn đệ)",
                "source": f"论语 · {it.get('chapter','')}",
                "lines": it.get("paragraphs", []),
            })
    return out


def _load_tangshi300(path: str) -> list[dict]:
    # {title, content: [{type, content: [{chapter, author, paragraphs[]}]}]}
    out = []
    with open(path, encoding="utf-8") as f:
        root = json.load(f)
    for group in root.get("content", []):
        gtype = group.get("type", "")
        for poem in group.get("content", []):
            out.append({
                "title": poem.get("chapter", ""),
                "author": poem.get("author", ""),
                "source": f"唐诗三百首 · {gtype}".strip(" ·"),
                "lines": poem.get("paragraphs", []),
            })
    return out


def _load_sanzijing(path: str) -> list[dict]:
    # dict {title, author, tags, paragraphs[]}
    with open(path, encoding="utf-8") as f:
        it = json.load(f)
    return [{
        "title": it.get("title", "三字經"),
        "author": it.get("author", "王應麟"),
        "source": "蒙学 · 三字经",
        "lines": it.get("paragraphs", []),
    }]


_LOADERS = {
    "shijing.json": _load_shijing,
    "lunyu.json": _load_lunyu,
    "tangshisanbaishou.json": _load_tangshi300,
    "sanzijing.json": _load_sanzijing,
}


def _ensure_loaded() -> None:
    if _POEMS:
        return
    for fname, loader in _LOADERS.items():
        path = os.path.join(_DATA_DIR, fname)
        if os.path.exists(path):
            try:
                items = loader(path)
            except Exception:
                # bỏ qua file lỗi, không làm chết agent
                continue
            for p in items:
                # cache bản giản thể để so khớp phồn↔giản
                p["_s_title"] = _to_simplified(p["title"])
                p["_s_author"] = _to_simplified(p["author"])
                p["_s_body"] = _to_simplified("".join(p["lines"]))
                _POEMS.append(p)


def search_poems(query: str, limit: int = 3) -> list[dict]:
    """Tìm bài thơ/đoạn kinh điển theo tên bài, tác giả, hoặc một câu/cụm chữ Hán.

    So khớp không phân biệt phồn thể / giản thể (vd '静夜思' khớp '靜夜思').
    """
    _ensure_loaded()
    q = _to_simplified((query or "").strip())
    if not q:
        return []

    scored = []
    for p in _POEMS:
        score = 0
        title = p["_s_title"]
        author = p["_s_author"]
        body = p["_s_body"]
        if q == title:
            score += 100
        elif q in title:
            score += 60
        if q in author:
            score += 40
        # chỉ tính nội dung khi truy vấn đủ dài (>=2 chữ) để tránh nhiễu
        if len(q) >= 2 and q in body:
            score += 20
        if score:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    # trả về bản sạch (bỏ field cache _s_*)
    return [{k: v for k, v in p.items() if not k.startswith("_s_")}
            for _, p in scored[:limit]]


def stats() -> dict:
    _ensure_loaded()
    by_source = {}
    for p in _POEMS:
        key = p["source"].split(" · ")[0]
        by_source[key] = by_source.get(key, 0) + 1
    return {"total": len(_POEMS), "by_source": by_source}
