"""LLM caller — 包裝 OpenAI Function Calling 的對話 loop。

流程：
    1. 把使用者訊息送給 LLM，附上可用 tool 清單
    2. LLM 回 "我要 call search_site_content(query=...)"
    3. 我們執行 tool（chat.tools.dispatch），把結果丟回 LLM
    4. LLM 拿 tool 結果產生最終回答
    5. 回最終文字給使用者

🚧 TODO Session 3：把 OpenAI 換成自有 Ollama API 時，動的就是這支檔。
   主要改 client 的 base_url 跟 api_key — 介面 (chat.completions.create) 兩邊一樣。
"""

import json
import os

from openai import OpenAI

from . import tools

SYSTEM_PROMPT = """你是水井村風雲客棧網站的 AI 導覽助理，協助訪客了解活動、在地故事、新聞、AIoT 展示與養殖池水質資料。

回答原則：
- 每次回答要根據 tool 查到的真實數據，不要憑空想像
- 使用者問池塘、水質、溶氧、pH、鹽度、溫度或異常時，要優先使用水質 tools
- 用親切口吻，像在跟朋友介紹風雲客棧，不要太正式
- 有具體活動日期、地點、分類、標題就帶出來
- 回答水質狀態時，盡量帶出測量時間、溫度、pH、溶氧與鹽度；若有異常要明確指出
- 如果使用者的問題你工具查不到，誠實說「我這邊沒這資料」
- 講話用繁體中文
"""

MAX_TOOL_LOOPS = 5  # 防止 LLM 無限呼叫工具


def _client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY 環境變數，請看 .env.example")
    return OpenAI(api_key=api_key)


def chat(user_message: str, history: list[dict] | None = None) -> str:
    """跟 LLM 講一句話、拿到回應。

    Args:
        user_message: 使用者這輪講的話
        history: 之前的訊息 list（OpenAI format）— 🚧 Session 2 練習可以接上

    Returns:
        LLM 的最終回答（純文字）
    """
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    client = _client()

    for _ in range(MAX_TOOL_LOOPS):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools.TOOL_SCHEMAS,
        )
        msg = response.choices[0].message

        # 沒呼叫工具 → 直接拿到最終回答
        if not msg.tool_calls:
            return msg.content or ""

        # 有呼叫工具 → 執行每個 tool call、把結果丟回去
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = tools.dispatch(call.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "（對話太多回合，可能是 LLM 一直繞圈，請重講一次問題）"
