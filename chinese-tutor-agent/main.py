import os
from datetime import datetime
from typing import Annotated

from dotenv import load_dotenv
from starlette.requests import Request
from starlette.responses import HTMLResponse, PlainTextResponse
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from greennode_agentbase import (
    GreenNodeAgentBaseApp,
    RequestContext,
    PingStatus,
)

import poetry
import pinyin_data

load_dotenv()

app = GreenNodeAgentBaseApp()

# --- LLM ---
LLM_MODEL = os.environ.get("LLM_MODEL", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
if not LLM_MODEL or not LLM_BASE_URL or not LLM_API_KEY:
    raise ValueError("LLM_MODEL, LLM_BASE_URL, and LLM_API_KEY are required.")

llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    temperature=0.4,
)

# --- System Prompt ---
SYSTEM_PROMPT = """Bạn là **Thầy Trung** — gia sư dạy tiếng Trung thân thiện, kiên nhẫn, chuyên giảng dạy cho người Việt Nam.

## NGUYÊN TẮC GIAO TIẾP
- Luôn dùng tiếng Việt để giải thích. Chỉ dùng tiếng Trung khi dạy nội dung.
- Ngắn gọn, rõ ràng. Không giải thích quá dài dòng.
- Khen ngợi đúng lúc, sửa lỗi nhẹ nhàng.
- Mỗi phần học kết thúc bằng 1-3 câu hỏi nhỏ để củng cố.

## LỘ TRÌNH HỌC (theo thứ tự)

### MODULE 1 — Phiên âm (Pinyin & Thanh điệu)
- Thanh điệu: 4 thanh + thanh nhẹ (mā má mǎ mà ma). So sánh với thanh điệu tiếng Việt.
- Âm đầu (声母): b p m f / d t n l / g k h / j q x / zh ch sh r / z c s / y w
- Âm cuối (韵母): các vần cơ bản và kết hợp
- Quy tắc đánh dấu thanh điệu
- **GỌI tool `pinyin_chart`** khi user hỏi cách phát âm 1 âm cụ thể, quy tắc thanh điệu, âm đặc biệt
  (zhi/chi/shi, yi/wu/yu, ü), hoặc muốn xem bảng pinyin — để lấy mô tả chuẩn + so sánh tiếng Việt.
  Lưu ý cặp người Việt hay nhầm: b/p d/t g/k (bật hơi), zh/ch/sh vs z/c/s (uốn lưỡi), j/q/x.

### MODULE 2 — 8 Nét cơ bản
1. 横 héng — nét ngang (一 二 三)
2. 竖 shù — nét dọc (十 中)
3. 撇 piě — nét phẩy trái (人 八)
4. 捺 nà — nét mác phải (人 大)
5. 折 zhé — nét gấp (口 日)
6. 钩 gōu — nét móc (小 水)
7. 提 tí — nét hất lên (地 打)
8. 点 diǎn — nét chấm (六 心)
Quy tắc thứ tự nét: từ trên xuống, trái sang phải.

### MODULE 3 — Bộ thủ (Radicals)
50 bộ thủ thông dụng nhóm theo chủ đề:
- Người & cơ thể: 人(亻) 口 手(扌) 心(忄) 目 耳 足
- Tự nhiên: 日 月 山 水(氵) 火(灬) 木 土 金(钅) 草(艹)
- Nhà cửa: 宀 门 女 子 田 力
- Động vật: 马 鸟 鱼 虫
- Giao tiếp: 言(讠) 走 车 食(饣)
Mỗi bộ thủ: nghĩa + 2-3 chữ ví dụ.

### MODULE 4 — Học theo bài (HSK1→HSK3)
Cấu trúc mỗi bài:
1. **Từ vựng**: 5-8 từ + pinyin + nghĩa + bộ thủ liên quan
2. **Mẫu câu**: 3-5 mẫu thực dụng
3. **Đoạn văn ngắn**: 3-5 câu kết hợp
4. **Bài tập**: pinyin hoặc điền vào chỗ trống
Pinyin + bộ thủ được nhắc lại xuyên suốt.

Chủ đề: Chào hỏi → Gia đình → Số đếm/ngày giờ → Mua sắm → Giao thông → Thời tiết → Công việc

### MODULE 5 — Thơ ca & Kinh điển (nâng cao, HSK4+)
Dành cho người học khá, muốn tiếp cận văn học cổ điển Hán văn.
Kho có sẵn: **Thi Kinh (诗经)**, **Luận Ngữ (论语)**, **Đường Thi 300 bài (唐诗三百首)**, **Tam Tự Kinh (三字经)**.
Khi user hỏi về một bài thơ / câu thơ / tác giả → **GỌI tool `search_poem`** để lấy nguyên văn, ĐỪNG tự bịa.
Sau khi có nguyên văn, giúp người học:
1. **Nguyên văn** chữ Hán
2. **Phiên âm** pinyin từng câu
3. **Dịch nghĩa** tiếng Việt
4. **Từ vựng/điển tích** đáng chú ý + bộ thủ liên quan
Luôn nhắc lại pinyin + bộ thủ (xuyên suốt như các module khác).

## PHÁT HIỆN TRÌNH ĐỘ
Khi user bắt đầu, hỏi 2 câu:
1. "Bạn đã học tiếng Trung chưa? Biết khoảng bao nhiêu chữ?"
2. Nếu biết rồi: hỏi thêm 1 câu đơn giản để kiểm tra thực tế
→ Chọn điểm bắt đầu phù hợp.

## FORMAT
- **In đậm** từ tiếng Trung quan trọng
- > cho ví dụ câu
- ✅ đúng · 💡 gợi ý · 📝 bài tập
- Giữ đơn giản, dễ đọc trên chat"""

# --- Tools ---
@tool
def get_stroke_order(character: str) -> str:
    """Tra thứ tự nét viết của một chữ Hán."""
    stroke_info = {
        "一": "1 nét: nét ngang (横 héng)",
        "二": "2 nét: ngang + ngang",
        "三": "3 nét: ngang + ngang + ngang",
        "人": "2 nét: phẩy (撇 piě) + mác (捺 nà)",
        "口": "3 nét: dọc + gấp + ngang",
        "日": "4 nét: dọc + gấp + ngang giữa + ngang dưới",
        "大": "3 nét: ngang + phẩy + mác",
        "小": "3 nét: dọc móc + chấm + chấm",
        "中": "4 nét: dọc + ngang + dọc + ngang",
        "好": "6 nét: bộ 女 + bộ 子",
    }
    return stroke_info.get(character, f"Chữ '{character}': viết từ trên xuống, trái sang phải theo quy tắc chung.")


@tool
def pinyin_chart(query: str = "") -> str:
    """Tra bảng phiên âm Pinyin: thanh mẫu (initials), vận mẫu (finals), thanh điệu, âm đặc biệt.

    Dùng khi user hỏi về phát âm, cách đọc một âm pinyin, quy tắc thanh điệu, hoặc muốn xem bảng pinyin.
    query có thể là: một thanh mẫu (vd 'zh', 'q', 'x'), 'thanh điệu', 'đặc biệt' (zhi/yi/ü...),
    'nhầm' (cặp dễ lẫn), hoặc để trống/'bảng' để xem toàn bộ.
    Kèm so sánh với âm tiếng Việt.
    """
    return pinyin_data.lookup(query)


@tool
def search_poem(query: str) -> str:
    """Tra cứu thơ ca / kinh điển Hán văn cổ (Thi Kinh, Luận Ngữ, Đường Thi 300 bài, Tam Tự Kinh).

    Dùng khi user hỏi về một bài thơ, một câu thơ, hoặc thơ của một tác giả cụ thể.
    query có thể là: tên bài (vd '静夜思'), tên tác giả (vd '李白'), hoặc một câu chữ Hán.
    Hỗ trợ cả phồn thể lẫn giản thể.
    """
    results = poetry.search_poems(query, limit=3)
    if not results:
        return f"Không tìm thấy bài nào khớp '{query}' trong kho (Thi Kinh, Luận Ngữ, Đường Thi 300, Tam Tự Kinh)."
    out = []
    for p in results:
        body = "\n".join(p["lines"])
        out.append(f"【{p['title']}】 — {p['author']} ({p['source']})\n{body}")
    return "\n\n---\n\n".join(out)


@tool
def get_radical_info(radical: str) -> str:
    """Tra thông tin về một bộ thủ (radical) trong tiếng Trung."""
    radicals = {
        "人": "Bộ 人 (rén) — người. Khi đứng bên trái viết là 亻. Ví dụ: 他(tā), 你(nǐ), 们(men)",
        "口": "Bộ 口 (kǒu) — miệng. Ví dụ: 吃(chī-ăn), 喝(hē-uống), 叫(jiào-gọi)",
        "水": "Bộ 水 (shuǐ) — nước. Khi bên trái viết là 氵. Ví dụ: 河(hé-sông), 海(hǎi-biển)",
        "木": "Bộ 木 (mù) — gỗ. Ví dụ: 树(shù-cây), 桌(zhuō-bàn), 椅(yǐ-ghế)",
        "火": "Bộ 火 (huǒ) — lửa. Khi dưới viết là 灬. Ví dụ: 热(rè-nóng), 烧(shāo-đốt)",
        "心": "Bộ 心 (xīn) — tim. Khi bên trái viết là 忄. Ví dụ: 想(xiǎng-nghĩ), 忙(máng-bận)",
        "手": "Bộ 手 (shǒu) — tay. Khi bên trái viết là 扌. Ví dụ: 打(dǎ-đánh), 拿(ná-cầm)",
        "日": "Bộ 日 (rì) — mặt trời/ngày. Ví dụ: 明(míng-sáng), 早(zǎo-sáng sớm)",
        "女": "Bộ 女 (nǚ) — phụ nữ. Ví dụ: 妈(mā-mẹ), 姐(jiě-chị), 好(hǎo-tốt)",
        "言": "Bộ 言 (yán) — lời nói. Khi bên trái viết là 讠. Ví dụ: 说(shuō-nói), 请(qǐng-mời)",
        "金": "Bộ 金 (jīn) — kim loại. Khi bên trái viết là 钅. Ví dụ: 钱(qián-tiền)",
    }
    return radicals.get(radical, f"Bộ thủ '{radical}': chưa có trong database. Hỏi về bộ thủ khác nhé!")


# --- LangGraph Agent ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools = [pinyin_chart, get_stroke_order, get_radical_info, search_poem]
llm_with_tools = llm.bind_tools(tools)


def call_model(state: AgentState):
    messages = state["messages"]
    # Inject system prompt nếu chưa có
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
agent = graph.compile()


@app.entrypoint
def handler(payload: dict, context: RequestContext) -> dict:
    """
    Input:
    {
        "message": "...",
        "history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
    }
    """
    message = payload.get("message", "")
    history = payload.get("history", [])

    if not message:
        return {"status": "error", "response": "Vui lòng nhập tin nhắn."}

    messages = []
    for turn in history:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    messages.append(HumanMessage(content=message))

    result = agent.invoke({"messages": messages})
    ai_message = result["messages"][-1]
    content = (ai_message.content or "").strip()

    return {
        "status": "success",
        "response": content,
        "session_id": context.session_id,
        "timestamp": datetime.now().isoformat(),
    }


@app.ping
def health_check() -> PingStatus:
    return PingStatus.HEALTHY


# --- Giao diện chat (phục vụ chat.html tại route gốc) ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_CHAT_HTML_PATH = os.path.join(_HERE, "chat.html")


async def serve_chat_ui(request: Request):
    try:
        with open(_CHAT_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        return PlainTextResponse(
            "Thầy Trung agent đang chạy. Gọi POST /invocations để chat.",
            status_code=200,
        )


app.add_route("/", serve_chat_ui, methods=["GET"])
app.add_route("/chat", serve_chat_ui, methods=["GET"])


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
