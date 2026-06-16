"""
Ngữ pháp tiếng Trung HSK 1-4 — nguồn: chinese-grammar-skill (giáo trình tiếng Việt).

Data: data/grammar/hsk{1,2,3,4}.md — mỗi file chia section bằng '## N. Tên'.
Cung cấp search theo từ khóa / chữ Hán / cấp HSK cho tool của agent. Nạp 1 lần.
"""
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_DIR = os.path.join(_HERE, "data", "grammar")

# list of {level, title, body}
_SECTIONS: list[dict] = []


def _ensure_loaded() -> None:
    if _SECTIONS:
        return
    for lvl in (1, 2, 3, 4):
        path = os.path.join(_DIR, f"hsk{lvl}.md")
        if not os.path.exists(path):
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except Exception:
            continue
        # tách theo heading '## ' (giữ heading làm title); bỏ tiêu đề file (# ...)
        parts = re.split(r"\n(?=## )", text)
        for p in parts:
            m = re.match(r"##\s+(.+)", p.strip())
            if not m:
                continue
            title = m.group(1).strip()
            body = p.strip()
            _SECTIONS.append({"level": lvl, "title": title, "body": body})


def search_grammar(query: str, level: int = 0, limit: int = 3) -> list[dict]:
    """Tìm điểm ngữ pháp theo từ khóa (tiếng Việt/Anh), chữ Hán, hoặc tên cấu trúc.

    level=0: mọi cấp; 1..4: lọc theo cấp HSK.
    """
    _ensure_loaded()
    q = (query or "").strip().lower()
    if not q:
        return []
    scored = []
    for sec in _SECTIONS:
        if level and sec["level"] != level:
            continue
        title = sec["title"].lower()
        body = sec["body"].lower()
        score = 0
        if q in title:
            score += 60
        # đếm số lần xuất hiện trong body (giới hạn)
        cnt = body.count(q)
        if cnt:
            score += min(cnt * 10, 40)
        if score:
            scored.append((score, sec))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:limit]]


def list_topics(level: int) -> list[str]:
    """Liệt kê các chủ đề ngữ pháp của một cấp HSK."""
    _ensure_loaded()
    return [s["title"] for s in _SECTIONS if s["level"] == level]


def stats() -> dict:
    _ensure_loaded()
    by_lvl = {}
    for s in _SECTIONS:
        by_lvl[s["level"]] = by_lvl.get(s["level"], 0) + 1
    return {"total_sections": len(_SECTIONS), "by_level": by_lvl}
