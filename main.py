import os
import requests
import telebot
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Temporary Memory
user_memory = {}

def ask_ai(user_id, prompt):

    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({
        "role": "user",
        "content": prompt
    })

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

    messages.extend(user_memory[user_id][-10:])

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

    user_memory[user_id].append({
        "role": "assistant",
        "content": reply
    })

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

⚡ Powered by 𝗣𝗿𝗶𝗻𝗰𝗲 𝗧𝗵𝗲 𝗟𝗲𝗴𝗲𝗻𝗱
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
    app.run(
        host="0.0.0.0",
        port=port
    )