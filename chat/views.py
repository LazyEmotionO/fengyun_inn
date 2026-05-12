"""Chat views — HTML 頁面 + JSON API。"""

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import llm


def chat_page(request):
    """聊天主頁 — 一個 HTML form。"""
    return render(request, "chat/chat.html")


@csrf_exempt  # 範例為了簡單先關 CSRF；🚧 Session 3 部署前學員要加回來
@require_http_methods(["POST"])
def chat_api(request):
    """POST {"message": "..."}  →  {"reply": "..."}"""
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "body 不是合法 JSON"}, status=400)

    message = (body.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "message 不能空"}, status=400)

    history = request.session.get("chat_history", [])

    try:
        reply = llm.chat(message, history=history)
    except Exception as e:  # noqa: BLE001
        return JsonResponse(
            {"error": f"LLM 呼叫失敗：{type(e).__name__}: {e}"}, status=500
        )

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    request.session["chat_history"] = history

    return JsonResponse({"reply": reply})


@csrf_exempt
@require_http_methods(["POST"])
def clear_chat_history(request):
    """清空目前 session 的聊天記錄。"""
    request.session.pop("chat_history", None)
    return JsonResponse({"ok": True})
