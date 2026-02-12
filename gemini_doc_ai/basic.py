from google import genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

apikey = os.getenv("apikey")

if not apikey:
    raise ValueError("API key not found. Check your .env file.")

client = genai.Client(api_key=apikey)

CHAT_FILE = "chat_memory.json"

# Load previous chat history (only user & model messages as text)
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r") as f:
        history = json.load(f)
else:
    history = []

# Create chat session
chat = client.chats.create(
    model="gemini-2.5-flash"
)

# Restore previous history into chat session
for message in history:
    chat.send_message(message["user"])
    # We do NOT resend model replies (model will regenerate context)

print("Chat started. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Chat ended.")
        break

    response = chat.send_message(user_input)

    print("\nBot:", response.text)
    print("-" * 40)

    # Save only user messages (simpler memory)
    history.append({"user": user_input, "model": response.text})


    with open(CHAT_FILE, "w") as f:
        json.dump(history, f, indent=4)
