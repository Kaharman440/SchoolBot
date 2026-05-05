import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes

# 🔐 Берём данные из Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    users[user.id] = {
        "step": 1,
        "username": user.username,
        "first_name": user.first_name
    }

    await update.message.reply_text(
        "Здравствуйте! Добро пожаловать на анонимный опрос.\n"
        "В каком вы классе?"
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    user = update.effective_user
    user_id = user.id
    text = update.message.text

    if user_id not in users:
        return

    step = users[user_id]["step"]

    if step == 1:
        users[user_id]["name"] = text
        users[user_id]["step"] = 2

        await update.message.reply_text(
            "Что вы чувствуете приходя в школу?"
        )

    elif step == 2:
        users[user_id]["feelings"] = text

        username = users[user_id]["username"]
        first_name = users[user_id]["first_name"]

        result = (
            f"Новый ответ:\n"
            f"Username: @{username if username else 'нет'}\n"
            f"Имя: {first_name}\n"
            f"Класс: {users[user_id]['name']}\n"
            f"Чувства: {users[user_id]['feelings']}"
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=result)

        await update.message.reply_text("Спасибо 👍")
        del users[user_id]

# 🚀 запуск бота
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

if __name__ == "__main__":
    app.run_polling()
