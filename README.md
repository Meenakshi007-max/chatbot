# Gemini Chatbot

Simple Gemini-powered chatbot with:
- a Streamlit web chat UI
- a terminal (CLI) chat script
- local JSON chat history persistence

## Project Structure

```text
gemini_doc_ai/
  app.py              # Streamlit chat app
  basic.py            # CLI chat app
  chat_memory.json    # persisted chat history
```

## Prerequisites

- Python 3.10+
- A Google Gemini API key

## Setup

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install streamlit python-dotenv google-genai
```

3. Create environment file:

Create `gemini_doc_ai/.env` with:

```env
apikey=YOUR_GEMINI_API_KEY
```

Notes:
- `app.py` explicitly reads `gemini_doc_ai/.env`.
- `basic.py` uses `load_dotenv()`; running it from `gemini_doc_ai/` is the safest option.

## Run (Web App)

From project root:

```bash
streamlit run gemini_doc_ai/app.py
```

Open the local URL shown in terminal (usually `http://localhost:8501`).

Features:
- chat-style UI
- retries once on rate-limit errors
- "Clear chat history" button

## Run (CLI)

```bash
cd gemini_doc_ai
python basic.py
```

Type messages and use `exit` to quit.

## Chat History

- Stored in `gemini_doc_ai/chat_memory.json`.
- Both apps use this file for persistence.

