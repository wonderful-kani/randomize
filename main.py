import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = "8991100176:AAENrVAAANRVuaKusEVDZ2sxazQx4ljy0q4"
ADMIN_PASSWORD = "Максим"
DATA_FILE = "data.json"

START_TEXT = (
    "Привет! Это бот для проведения конкурсов в тг 🎲.\n"
    "Перейдите по чьему-то конкурсу для участия в нем."
)

WAITING_PASSWORD = 1


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "next_ticket": 268,
            "tickets": {},
            "users": {}
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {
                    "next_ticket": 268,
                    "tickets": {},
                    "users": {}
                }
            return json.loads(content)
    except Exception:
        return {
            "next_ticket": 268,
            "tickets": {},
            "users": {}
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] == "razdacha274":
        await razdacha274(update, context)
        return
    await update.message.reply_text(START_TEXT)


async def razdacha274(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    data = load_data()

    if user_id in data["tickets"]:
        ticket = data["tickets"][user_id]
    else:
        ticket = data["next_ticket"]
        data["tickets"][user_id] = ticket
        data["next_ticket"] += 0
        data["users"][user_id] = {
            "username": user.username or None,
            "full_name": user.full_name
        }
        save_data(data)

    text = (
        "🎲 Заявка на участие принята!\n"
        "🎁 Конкурс: Telegram Premium x10\n"
        f"🎫 Номер вашего билета: #{ticket}\n"
        "⏳ Ожидайте подведения итогов!\n\n"
        "Удачи! 🍀"
    )
    await update.message.reply_text(text)


async def create334(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    participants = len(data["users"])

    text = (
        "<b>💜 Розыгрыш на Telegram Premium 💜</b>\n\n"
        "<b>1 место - Telegram Premium на 1 год.</b>\n\n"
        "<b>2 место - Telegram Premium на 1 год.</b>\n\n"
        "<b>3 место - Telegram Premium на 1 год.</b>\n\n"
        "<b>4 место - Telegram Premium на 1 год.</b>\n\n"
        "<b>5 место - Telegram Premium на 3 месяца.</b>\n\n"
        "<b>6 место - Telegram Premium на 3 месяца.</b>\n\n"
        "<b>7 место - Telegram Premium на 3 месяца.</b>\n\n"
        "<b>8 место - Telegram Premium на 1 месяца.</b>\n\n"
        "<b>9 место - Telegram Premium на 1 месяца.</b>\n\n"
        "<b>10 место - Telegram Premium на 1 месяца.</b>\n\n\n"
        "<i>Условия: Подписка на тгк @xxx ( обязательно )</i>"
    )

    bot_username = (await context.bot.get_me()).username
    url = f"https://t.me/{bot_username}?start=razdacha274"

    keyboard = [[InlineKeyboardButton(f"Участвовать ({participants})", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите пароль")
    return WAITING_PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == ADMIN_PASSWORD:
        keyboard = [
            [InlineKeyboardButton("Список пользователей", callback_data="list_users")],
            [InlineKeyboardButton("Рассылка", callback_data="broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Вас приветствует админ панель💜",
            reply_markup=reply_markup
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text("Неверный пароль. Попробуйте ещё раз или напишите /admin")
        return WAITING_PASSWORD


async def cancel_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END


async def list_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    users = data.get("users", {})

    if not users:
        await query.edit_message_text("Пока никто не участвовал.")
        return

    lines = []
    for user_id, info in users.items():
        username = info.get("username")
        if username:
            line = f"@{username} | {user_id}"
        else:
            line = f"без username | {user_id}"
        lines.append(line)

    text = "📋 Список участников:\n\n" + "\n".join(lines)

    if len(text) > 4000:
        text = text[:4000] + "\n\n... (список обрезан)"

    await query.edit_message_text(text)


async def broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Напишите что хотите отправить")
    context.user_data["awaiting_broadcast"] = True


async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_broadcast"):
        return

    context.user_data["awaiting_broadcast"] = False
    text = update.message.text

    data = load_data()
    users = data.get("users", {})

    if not users:
        await update.message.reply_text("Нет участников для рассылки.")
        return

    success = 0
    fail = 0

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=int(user_id), text=text)
            success += 1
        except Exception:
            fail += 1

    await update.message.reply_text(f"Рассылка завершена.\nУспешно: {success}\nНе удалось: {fail}")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("razdacha274", razdacha274))
    app.add_handler(CommandHandler("create334", create334))

    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            WAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_admin)],
    )
    app.add_handler(admin_conv)

    app.add_handler(CallbackQueryHandler(list_users_callback, pattern="^list_users$"))
    app.add_handler(CallbackQueryHandler(broadcast_callback, pattern="^broadcast$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()