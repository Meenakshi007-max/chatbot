from pathlib import Path
import json
import os
import re
import time

import streamlit as st
from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
CHAT_FILE = BASE_DIR / "chat_memory.json"

load_dotenv(dotenv_path=ENV_FILE)
API_KEY = os.getenv("apikey")


def load_history() -> list[dict]:
    if not CHAT_FILE.exists():
        return []
    try:
        with CHAT_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            normalized: list[dict] = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                if "role" in item and "content" in item:
                    normalized.append({"role": item["role"], "content": item["content"]})
                    continue
                if "user" in item:
                    normalized.append({"role": "user", "content": str(item["user"])})
                if "model" in item:
                    normalized.append({"role": "assistant", "content": str(item["model"])})
            return normalized
    except json.JSONDecodeError:
        return []


def save_history(messages: list[dict]) -> None:
    with CHAT_FILE.open("w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


def extract_retry_seconds(error_text: str) -> float:
    patterns = [
        r"retry in ([0-9]+(?:\.[0-9]+)?)s",
        r"'retryDelay': '([0-9]+)s'",
    ]
    for pattern in patterns:
        match = re.search(pattern, error_text)
        if match:
            return float(match.group(1))
    return 30.0


def send_with_retry(chat, message: str):
    for attempt in range(2):
        try:
            return chat.send_message(message)
        except Exception as exc:
            text = str(exc)
            is_rate_limited = "RESOURCE_EXHAUSTED" in text or "429" in text
            if is_rate_limited and attempt == 0:
                wait_seconds = extract_retry_seconds(text)
                st.warning(f"Rate limit hit. Retrying in {wait_seconds:.1f}s...")
                time.sleep(wait_seconds)
                continue
            raise


st.set_page_config(page_title="Gemini Chat", page_icon="💬", layout="centered")
st.title("Gemini Chat")

if not API_KEY:
    st.error(f"API key not found in {ENV_FILE}. Add: apikey=YOUR_KEY")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = load_history()

if "chat" not in st.session_state:
    client = genai.Client(api_key=API_KEY)
    st.session_state.chat = client.chats.create(model="gemini-2.5-flash")

for msg in st.session_state.messages:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")
    with st.chat_message(role):
        st.markdown(content)

prompt = st.chat_input("Type your message...")
if prompt:
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = send_with_retry(st.session_state.chat, prompt)
        answer = response.text
    except Exception as exc:
        st.error(f"Request failed: {exc}")
        st.stop()

    bot_msg = {"role": "assistant", "content": answer}
    st.session_state.messages.append(bot_msg)
    save_history(st.session_state.messages)

    with st.chat_message("assistant"):
        st.markdown(answer)

if st.button("Clear chat history"):
    st.session_state.messages = []
    save_history([])
    st.rerun()
