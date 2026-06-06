import os
import requests
import telebot
from flask import Flask
from threading import Thread

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MEMORY_API = os.getenv("MEMORY_API")

bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# REQUIRED CHANNELS
REQUIRED_CHANNELS = [
    "@ZShadowBots",
    "@ZShadowBots_Backup"
]

# ---------------- CHECK JOIN ----------------
def check_user_joined(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True


# ---------------- AI FUNCTION ----------------
def ask_ai(user_id, prompt):

    requests.post(
        f"{MEMORY_API}/save",
        json={
            "user_id": str(user_id),
            "role": "user",
            "content": prompt
        }
    )

    memory_response = requests.get(f"{MEMORY_API}/memory/{user_id}")
    old_messages = memory_response.json()

    messages = [
        {
            "role": "system",
            "content": """
You are Prince Legend AI created by Prince.

Rules:
- Never mention OpenAI, ChatGPT, GPT, or OpenRouter.
- If someone asks who made you, say: 'I was created by Zshadow Legend 😎'
- If someone asks your model name, say: 'I am Zshadow Legend Ai.'
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

    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()

    reply = result["choices"][0]["message"]["content"]

    requests.post(
        f"{MEMORY_API}/save",
        json={
            "user_id": str(user_id),
            "role": "assistant",
            "content": reply
        }
    )

    return reply


# ---------------- START COMMAND ----------------
@bot.message_handler(commands=['start'])
def start(message):

    user_id = message.from_user.id

    # FORCE JOIN CHECK
    if not check_user_joined(user_id):

        markup = telebot.types.InlineKeyboardMarkup()

        markup.add(
            telebot.types.InlineKeyboardButton(
                "📢 Join Channel 1",
                url="https://t.me/ZShadowBots"
            )
        )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "📢 Join Channel 2",
                url="https://t.me/ZShadowBots_Backup"
            )
        )

        markup.add(
            telebot.types.InlineKeyboardButton(
                "✅ I Have Joined",
                callback_data="check_join"
            )
        )

        bot.send_message(
            message.chat.id,
            "⚠️ You must join the required channels before using this bot 👇",
            reply_markup=markup
        )
        return

    # WELCOME MESSAGE
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

[ 🚫 IMPORTANT NOTICE ]
This AI bot is designed for educational, informational, and entertainment purposes only.
❌ Any illegal, harmful, or unethical activities are strictly not supported or allowed.
⚠️ Users are responsible for how they use the responses provided by this bot.
By using this bot, you agree to use it in a safe, legal, and responsible manner.

⚡ Powered by [𓆩 Z Shadow Legend 𓆪](https://t.me/Limited_person_msg_here_bot)

🔥 Fast • Smart • Reliable

Enjoy your experience ❤️
"""

    bot.reply_to(message, welcome_text)


# ---------------- CHECK JOIN CALLBACK ----------------
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):

    if check_user_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "You Are Verfied To Use This Bot✅")
        bot.send_message(call.message.chat.id, "🎉 Access granted! You can now use the bot 😎")
    else:
        bot.answer_callback_query(call.id, "Join All Channels To Use This Bot👿", show_alert=True)


# ---------------- CHAT ----------------
@bot.message_handler(func=lambda m: True)
def ai_chat(message):

    bot.send_chat_action(message.chat.id, "typing")

    try:
        reply = ask_ai(message.from_user.id, message.text)
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, f"Error: {e}")


# ---------------- FLASK ----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Running 😎"


def run():
    bot.infinity_polling()


Thread(target=run).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)