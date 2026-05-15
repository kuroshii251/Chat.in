import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

print(f"[DEBUG] Key: {OPENROUTER_API_KEY[:10] if OPENROUTER_API_KEY else 'NONE'}")
print(f"[DEBUG] Model: {OPENROUTER_MODEL}")

def generate_reply(character_prompt: str, history: list, user_message: str) -> str:
    """Generate reply using OpenRouter (OpenAI-compatible) API."""
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY belum diset di file .env!"

    system_message = character_prompt or ""

    messages = [{"role": "system", "content": system_message}]

    for chat in history[-6:]:
        user_text = chat.get("user")
        ai_text = chat.get("assistant") or chat.get("waifu") or chat.get("reply")

        if user_text:
            messages.append({"role": "user", "content": user_text})
        if ai_text:
            messages.append({"role": "assistant", "content": ai_text})

    messages.append({"role": "user", "content": user_message})

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }


    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "temperature": 0.9,
        "top_p": 0.95,
        "max_tokens": 512,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            try:
                err = resp.json()
            except Exception:
                err = resp.text
            return f"Waduh, koneksiku agak bermasalah nih... (Error: {err})"

        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"Waduh, koneksiku agak bermasalah nih... (Error: {str(e)})"

