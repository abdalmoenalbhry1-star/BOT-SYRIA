import telebot
from telebot import types
from config import BOT_TOKEN

ADMIN_ID = 8419854444

APP_URL = "https://abdalmoenalbhry1-star.github.io/BOT-SYRIA/"
ADMIN_URL = "https://abdalmoenalbhry1-star.github.io/BOT-SYRIA/admin/"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start"])
def start_command(message):
    name = message.from_user.first_name or "صديقي"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "🚀 دخول إلى التطبيق",
            web_app=types.WebAppInfo(url=APP_URL)
        )
    )

    bot.send_message(
        message.chat.id,
        f"أهلاً بك في <b>BOT SYRIA</b> 👋\n\n"
        f"يا {name} ❤️\n"
        "اربح الليرات من الإعلانات والمهمات والدعوات، هيا استعد 🚀",
        reply_markup=keyboard
    )


@bot.message_handler(commands=["abdalmoenal123"])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⚠️ هذا أمر الإدارة.")
        return

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "🛡️ فتح لوحة الإدارة",
            web_app=types.WebAppInfo(url=ADMIN_URL)
        )
    )

    bot.send_message(
        message.chat.id,
        "🛡️ <b>لوحة إدارة BOT SYRIA</b>\n\n"
        "أهلاً بك في لوحة التحكم الخاصة بالمدير.",
        reply_markup=keyboard
    )


print("BOT SYRIA STARTING...")
bot.infinity_polling(skip_pending=True)
