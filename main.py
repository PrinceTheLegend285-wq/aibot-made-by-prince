import os
import requests
import telebot
from flask import Flask
from threading import Thread
from urllib.parse import quote

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MEMORY_API = os.getenv("MEMORY_API")

bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# AI Chat Function
def ask_ai(user_id, prompt):

    # Save user message
    requests.post(
        f"{MEMORY_API}/save",
        json={
            "user_id": str(user_id),
            "role": "user",
            "content": prompt
        }
    )

    # Get old memory
    memory_response = requests.get(
        f"{MEMORY_API}/memory/{user_id}"
    )

    old_messages = memory_response.json()

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

    messages.extend(old_messages[-10:])

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
    requests.post(
        f"{MEMORY_API}/save",
        json={
            "user_id": str(user_id),
            "role": "assistant",
            "content": reply
        }
    )

    return reply

# START COMMAND
@bot.message_handler(commands=['start'])
def start(message):

    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    welcome_text = f"""
👋 Hello {first_name} {last_name}!

🤖 Welcome to 𖤍 ᴢ ꜱʜᴀᴅᴏᴡ ʟᴇɢᴇɴᴅ ᴀɪ 𖤍 😎

✨ What can I do?
• AI Chat & Instant Answers 💬
• Study & Homework Help 📚
• Coding Assistance 💻
• Creative Ideas 🎨
• Fast & Smart Replies ⚡
• And much more...

📝 Just send your question and let the AI handle the rest!

⚡ Powered by [𓆩 𝗭 𝗦𝗵𝗮𝗱𝗼𝘄 𝗟𝗲𝗴𝗲𝗻𝗱 𓆪](https://t.me/Limited_person_msg_here_bot)

🔥 Fast • Smart • Reliable

Enjoy your experience ❤️
"""

    bot.reply_to(
        message,
        welcome_text,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# IMAGINE COMMAND
@bot.message_handler(commands=['imagine'])
def imagine(message):

    try:

        prompt = message.text.replace("/imagine", "").strip()

        if not prompt:

            bot.reply_to(
                message,
                "❌ Example:\n/imagine anime boy with blue fire"
            )

            return

        bot.reply_to(
            message,
            "🎨 Generating image..."
        )

        image_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{quote(prompt)}"
        )

        bot.send_photo(
            message.chat.id,
            image_url,
            caption=f"🖼 Prompt: {prompt}"
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"Error: {e}"
        )

# NORMAL AI CHAT
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

        bot.reply_to(
            message,
            f"Error: {e}"
        )

# WEB SERVER
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running 😎"

def run():
    bot.infinity_polling()

Thread(target=run).start()

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 8080)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )