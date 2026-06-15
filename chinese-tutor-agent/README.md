# chinese-tutor-agent — Thầy Trung 🇨🇳

AI gia sư dạy tiếng Trung cho người Việt, chạy trên GreenNode AgentBase.

## Lộ trình học

1. **Phiên âm (Pinyin & Thanh điệu)** — so sánh với tiếng Việt
2. **8 nét cơ bản** — nền tảng viết chữ Hán
3. **Bộ thủ (Radicals)** — 50 bộ thủ thông dụng
4. **Học theo bài** — từ vựng → mẫu câu → đoạn văn → bài tập (pinyin + bộ thủ xuyên suốt)

## Setup local

```bash
cd chinese-tutor-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Điền LLM_API_KEY, LLM_MODEL vào .env
python main.py
```

## Cách gọi agent

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào thầy, tôi muốn học tiếng Trung từ đầu",
    "history": []
  }'
```

Để gửi tiếp theo có lịch sử:
```json
{
  "message": "Câu tiếp theo của tôi",
  "history": [
    {"role": "user", "content": "Xin chào thầy..."},
    {"role": "assistant", "content": "Chào bạn! ..."}
  ]
}
```

## LLM Config

Dùng GreenNode AI Platform (OpenAI-compatible):
```
LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1
LLM_API_KEY=<lấy từ /agentbase-llm>
LLM_MODEL=<tên model từ /agentbase-llm models list>
```

## Deploy

```bash
/agentbase-deploy   # trong Claude Code, từ thư mục này
```
