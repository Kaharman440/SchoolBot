import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not TOKEN:
    raise Exception("BOT_TOKEN не задан")

if not ADMIN_ID:
    raise Exception("ADMIN_ID не задан")

users = {}

# --- Клавиатуры ---
lang_kb = ReplyKeyboardMarkup(
    [["Русский 🇷🇺", "Қазақша 🇰🇿"]], resize_keyboard=True
)

anon_kb = ReplyKeyboardMarkup(
    [["Анонимно", "Не анонимно"], ["Анонимді", "Анонимді емес"]],
    resize_keyboard=True,
)

role_kb = ReplyKeyboardMarkup(
    [["Ученик", "Родитель", "Учитель"],
     ["Оқушы", "Ата-ана", "Мұғалім"]],
    resize_keyboard=True,
)

class_kb = ReplyKeyboardMarkup(
    [[str(i) for i in range(1, 12)]],
    resize_keyboard=True,
)

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {"step": 0}
    await update.message.reply_text(
        "Выберите язык / Тілді таңдаңыз",
        reply_markup=lang_kb
    )

# --- MAIN HANDLER ---
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in users:
        users[user_id] = {"step": 0}

    step = users[user_id]["step"]

    # --- Язык ---
    if step == 0:
        users[user_id]["lang"] = "ru" if "Рус" in text else "kz"
        users[user_id]["step"] = 1

        if users[user_id]["lang"] == "ru":
            await update.message.reply_text(
                "Хотите продолжить анонимно?",
                reply_markup=anon_kb
            )
        else:
            await update.message.reply_text(
                "Анонимді жалғастырғыңыз келе ме?",
                reply_markup=anon_kb
            )

    # --- Анонимность ---
    elif step == 1:
        users[user_id]["anon"] = text
        users[user_id]["step"] = 2

        if "не" in text.lower() or "емес" in text.lower():
            if users[user_id]["lang"] == "ru":
                await update.message.reply_text("Введите Ф.И.О:")
            else:
                await update.message.reply_text("Аты-жөніңізді жазыңыз:")
        else:
            users[user_id]["name"] = "Аноним"
            users[user_id]["step"] = 3

            if users[user_id]["lang"] == "ru":
                await update.message.reply_text("Выберите роль:", reply_markup=role_kb)
            else:
                await update.message.reply_text("Рөліңізді таңдаңыз:", reply_markup=role_kb)

    # --- ФИО ---
    elif step == 2:
        users[user_id]["name"] = text
        users[user_id]["step"] = 3

        if users[user_id]["lang"] == "ru":
            await update.message.reply_text("Выберите роль:", reply_markup=role_kb)
        else:
            await update.message.reply_text("Рөліңізді таңдаңыз:", reply_markup=role_kb)

    # --- Роль ---
    elif step == 3:
        users[user_id]["role"] = text

        if any(x in text.lower() for x in ["ученик", "родитель", "оқушы", "ата"]):
            users[user_id]["step"] = 4

            if users[user_id]["lang"] == "ru":
                await update.message.reply_text("Выберите класс:", reply_markup=class_kb)
            else:
                await update.message.reply_text("Сыныбыңызды таңдаңыз:", reply_markup=class_kb)
        else:
            users[user_id]["class"] = "-"
            users[user_id]["step"] = 5

            if users[user_id]["lang"] == "ru":
                await update.message.reply_text("Ваши предложения или жалобы:")
            else:
                await update.message.reply_text("Ұсыныстар мен шағымдар:")

    # --- Класс ---
    elif step == 4:
        users[user_id]["class"] = text
        users[user_id]["step"] = 5

        if users[user_id]["lang"] == "ru":
            await update.message.reply_text("Ваши предложения или жалобы:")
        else:
            await update.message.reply_text("Ұсыныстар мен шағымдар:")

    # --- Финал ---
    elif step == 5:
        users[user_id]["text"] = text

        user = update.effective_user
        username = f"@{user.username}" if user.username else "нет"
        link = f"<a href='tg://user?id={user.id}'>Профиль</a>"

        result = (
            f"📩 Новый ответ:\n\n"
            f"👤 Имя: {users[user_id]['name']}\n"
            f"🔗 Username: {username}\n"
            f"{link}\n"
            f"🎭 Роль: {users[user_id]['role']}\n"
            f"🏫 Класс: {users[user_id]['class']}\n"
            f"💬 Сообщение:\n{users[user_id]['text']}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=result,
            parse_mode="HTML"
        )

        if users[user_id]["lang"] == "ru":
            await update.message.reply_text("Спасибо 👍")
        else:
            await update.message.reply_text("Рақмет 👍")

        del users[user_id]


# --- APP ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

if __name__ == "__main__":
    app.run_polling()
