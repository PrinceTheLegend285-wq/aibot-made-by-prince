import os
import requests
import telebot
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
print("SUPABASE URL =", SUPABASE_URL)
print("SUPABASE KEY =", SUPABASE_KEY)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

def ask_ai(user_id, prompt):

    # Save user message
    supabase.table("memory").insert({
        "user_id": str(user_id),
        "role": "user",
        "content": prompt
    }).execute()

    # Load old messages
    old_messages = supabase.table("memory") \
        .select("*") \
        .eq("user_id", str(user_id)) \
        .execute()

    messages = [
        {
            "role": "system",
            "content": """
You are Prince Legend AI created by Prince.

Rules:
- Never mention OpenAI, ChatGPT, GPT, or OpenRouter.
- If someone asks who made you, say:
'I was created by Prince 😎'

- If someone asks your model name, say:
'I am Prince Legend AI.'

- Remember previous messages naturally.
- Talk in a cool friendly style.
"""
        }
    ]

    # Add memory
    for msg in old_messages.data[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": messages
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data
    )

    result = response.json()

    reply = result["choices"][0]["message"]["content"]

    # Save AI reply
    supabase.table("memory").insert({
        "user_id": str(user_id),
        "role": "assistant",
        "content": reply
    }).execute()

    return reply

@bot.message_handler(commands=['start'])
def start(message):

    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    welcome_text = f"""
👋 Hello {first_name} {last_name}!

🤖 Welcome to 𖤍 ᴘʀɪɴᴄᴇ ʟᴇɢᴇɴᴅ ᴀɪ 𖤍 🚀

✨ What can I do?
• AI Chat & Instant Answers 💬
• Study & Homework Help 📚
• Coding Assistance 💻
• Creative Ideas 🎨
• Fast & Smart Replies ⚡
• And much more...

📝 Just send your question and let the AI handle the rest!

⚡ Powered by Prince
🔥 Fast • Smart • Reliable

Enjoy your experience ❤️
"""

    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda m: True)
def ai_chat(message):

    bot.send_chat_action(message.chat.id, "typing")

    try:
        reply = ask_ai(
            message.from_user.id,
            message.text
        )

        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running"

def run():
    bot.infinity_polling()

Thread(target=run).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)