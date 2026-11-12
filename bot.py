import random
import os
import telebot
from telebot import types

from config import BOT_TOKEN, CHANNEL_USERNAME, BOT_NAME
from database import (
    init_db,
    create_user,
    get_user,
    is_code_verified,
    set_code_verified,
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# روابط Telegram Mini App والإدارة
BOT_SYRIA_APP_URL = os.getenv(
    "BOT_SYRIA_APP_URL",
    "https://YOUR-DOMAIN/"
)

BOT_SYRIA_ADMIN_URL = os.getenv(
    "BOT_SYRIA_ADMIN_URL",
    "https://YOUR-DOMAIN/admin"
)


# كود بسيط يظهر مرة واحدة للمستخدم الجديد
CODES = {
    "🐱 قطة": False,
    "🍎 تفاحة": False,
    "🚗 سيارة": False,
    "🌙 قمر": False,
}


def subscription_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 الاشتراك بالقناة",
            url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🔄 تحقق من الاشتراك",
            callback_data="check_subscription"
        )
    )

    return keyboard


def main_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "🚀 فتح BOT SYRIA",
            web_app=types.WebAppInfo(url=BOT_SYRIA_APP_URL)
        )
    )

    keyboard.add(
        types.InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
        types.InlineKeyboardButton("📋 المهام", callback_data="tasks"),
    )

    keyboard.add(
        types.InlineKeyboardButton("👥 الإحالات", callback_data="referrals"),
        types.InlineKeyboardButton("💸 السحب", callback_data="withdraw"),
    )

    keyboard.add(
        types.InlineKeyboardButton("📊 سجل الأرباح", callback_data="history"),
        types.InlineKeyboardButton("🛟 الدعم الفني", callback_data="support"),
    )

    return keyboard


def show_subscription(chat_id, message_id=None):
    text = (
        f"🎉 <b>أهلاً بك في {BOT_NAME}</b>\n\n"
        "لكي تتمكن من استخدام البوت، يجب عليك الاشتراك بالقناة أولاً.\n\n"
        "بعد الاشتراك اضغط على زر <b>تحقق من الاشتراك</b>."
    )

    if message_id:
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=subscription_keyboard()
        )
    else:
        bot.send_message(
            chat_id,
            text,
            reply_markup=subscription_keyboard()
        )


def check_user_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


def show_code(message):
    options = list(CODES.keys())
    correct = random.choice(options)

    code_data = {
        "correct": correct,
        "options": options,
    }

    bot_code = types.InlineKeyboardMarkup(row_width=2)

    shuffled = options[:]
    random.shuffle(shuffled)

    for option in shuffled:
        bot_code.add(
            types.InlineKeyboardButton(
                option,
                callback_data=f"code:{option}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🔐 <b>التحقق الأول</b>\n\n"
        "اختر الإجابة الصحيحة من الخيارات التالية:",
        reply_markup=bot_code
    )

    # حفظ الإجابة مؤقتاً في ذاكرة البوت
    pending_codes[message.from_user.id] = code_data


pending_codes = {}


def show_main_menu(chat_id, message_id=None):
    text = (
        f"🎉 <b>مرحباً بك في {BOT_NAME}</b>\n\n"
        "💰 اكسب رصيدك من خلال تنفيذ المهام المتاحة.\n\n"
        "اختر من القائمة التالية:"
    )

    if message_id:
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=main_keyboard()
        )
    else:
        bot.send_message(
            chat_id,
            text,
            reply_markup=main_keyboard()
        )


@bot.message_handler(commands=["abdalmoenal"])
def admin_command(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(
            "🛡️ فتح الإدارة",
            url=BOT_SYRIA_ADMIN_URL
        )
    )

    bot.send_message(
        message.chat.id,
        "🛡️ <b>لوحة إدارة BOT SYRIA</b>\\n\\nاضغط الزر للدخول إلى لوحة الإدارة.",
        reply_markup=keyboard
    )


@bot.message_handler(commands=["start"])
def start(message):
    user = message.from_user

    create_user(
        user.id,
        user.first_name,
        user.username
    )

    # إذا أنهى التحقق سابقاً، يذهب مباشرة للقائمة الرئيسية
    if is_code_verified(user.id):
        show_main_menu(message.chat.id)
        return

    show_subscription(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription(call):
    user_id = call.from_user.id

    if not check_user_subscription(user_id):
        bot.answer_callback_query(
            call.id,
            "❌ لم يتم العثور على اشتراكك بالقناة.",
            show_alert=True
        )
        return

    bot.answer_callback_query(call.id)

    if not is_code_verified(user_id):
        options = ["🌙 قمر", "🚗 سيارة", "🍎 تفاحة", "🐱 قطة"]
        correct = "🌙 قمر"

        pending_codes[user_id] = {
            "correct": correct,
            "options": options,
        }

        keyboard = types.InlineKeyboardMarkup(row_width=1)

        shuffled = options[:]
        random.shuffle(shuffled)

        for option in shuffled:
            keyboard.add(
                types.InlineKeyboardButton(
                    option,
                    callback_data=f"code:{option}"
                )
            )

        bot.edit_message_text(
            "🔐 <b>التحقق من الكود</b>\\n\\n"
            "اختر <b>القمر 🌙</b> من الخيارات التالية:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("code:"))
def verify_code(call):
    user_id = call.from_user.id

    data = pending_codes.get(user_id)

    if not data:
        bot.answer_callback_query(
            call.id,
            "⚠️ انتهت عملية التحقق. اضغط /start.",
            show_alert=True
        )
        return

    selected = call.data.split(":", 1)[1]

    if selected != data["correct"]:
        bot.answer_callback_query(
            call.id,
            "❌ اختيار خاطئ، حاول مرة أخرى.",
            show_alert=True
        )
        return

    set_code_verified(user_id)
    pending_codes.pop(user_id, None)

    bot.answer_callback_query(call.id, "✅ تم التحقق بنجاح!")

    show_main_menu(
        call.message.chat.id,
        call.message.message_id
    )


@bot.callback_query_handler(func=lambda call: call.data in {
    "balance",
    "tasks",
    "referrals",
    "withdraw",
    "history",
    "support",
})
def menu_placeholder(call):
    bot.answer_callback_query(
        call.id,
        "هذه الميزة سنضيفها في المرحلة القادمة.",
        show_alert=True
    )


if __name__ == "__main__":
    init_db()

    print(f"🚀 {BOT_NAME} يعمل...")

    bot.infinity_polling(
        skip_pending=True,
        allowed_updates=["message", "callback_query"]
    )
