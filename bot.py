import os
from telegram import Update, ReplyKeyboardMarkup
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

# --- КЛАВИАТУРЫ ---
lang_kb = ReplyKeyboardMarkup(
    [["Русский 🇷🇺", "Қазақша 🇰🇿"]],
    resize_keyboard=True
)

anon_kb = ReplyKeyboardMarkup(
    [
        ["Анонимно / Анонимді"],
        ["Не анонимно / Анонимді емес"]
    ],
    resize_keyboard=True
)

role_kb = ReplyKeyboardMarkup(
    [
        ["Ученик / Оқушы"],
        ["Родитель / Ата-ана"],
        ["Учитель / Мұғалім"]
    ],
    resize_keyboard=True
)

class_kb = ReplyKeyboardMarkup(
    [[str(i) for i in range(1, 12)]],
    resize_keyboard=True
)

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users[update.effective_user.id] = {"step": 0}
    await update.message.reply_text(
        "Выберите язык / Тілді таңдаңыз",
        reply_markup=lang_kb
    )

# --- ОСНОВНАЯ ЛОГИКА ---
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in users:
        users[user_id] = {"step": 0}

    step = users[user_id]["step"]

    # --- 0 ЯЗЫК ---
    if step == 0:
        if text == "Русский 🇷🇺":
            users[user_id]["lang"] = "ru"
        elif text == "Қазақша 🇰🇿":
            users[user_id]["lang"] = "kz"
        else:
            await update.message.reply_text("Пожалуйста, выберите язык кнопкой")
            return

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

    # --- 1 АНОНИМНОСТЬ ---
    elif step == 1:
        if "Не анонимно" in text or "Анонимді емес" in text:
            users[user_id]["anon"] = False
            users[user_id]["step"] = 2

            if users[user_id]["lang"] == "ru":
                await update.message.reply_text("Введите Ф.И.О:")
            else:
                await update.message.reply_text("Аты-жөніңізді жазыңыз:")
        else:
            users[user_id]["anon"] = True
            users[user_id]["name"] = "Аноним"
            users[user_id]["step"] = 3

            if users[user_id]["lang"] == "ru":
                await update.message.reply_text("Выберите роль:", reply_markup=role_kb)
            else:
                await update.message.reply_text("Рөліңізді таңдаңыз:", reply_markup=role_kb)

    # --- 2 ФИО ---
    elif step == 2:
        users[user_id]["name"] = text
        users[user_id]["step"] = 3

        if users[user_id]["lang"] == "ru":
            await update.message.reply_text("Выберите роль:", reply_markup=role_kb)
        else:
            await update.message.reply_text("Рөліңізді таңдаңыз:", reply_markup=role_kb)

    # --- 3 РОЛЬ ---
    elif step == 3:
        users[user_id]["role"] = text

        if "Ученик" in text or "Оқушы" in text or "Родитель" in text or "Ата-ана" in text:
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

    # --- 4 КЛАСС ---
    elif step == 4:
        users[user_id]["class"] = text
        users[user_id]["step"] = 5

        if users[user_id]["lang"] == "ru":
            await update.message.reply_text("Ваши предложения или жалобы:")
        else:
            await update.message.reply_text("Ұсыныстар мен шағымдар:")

    # --- 5 ФИНАЛ ---
    elif step == 5:
        users[user_id]["text"] = text

        user = update.effective_user
        username = f"@{user.username}" if user.username else "нет"
        link = f"<a href='tg://user?id={user.id}'>Открыть профиль</a>"

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


# --- ЗАПУСК ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

if __name__ == "__main__":
    app.run_polling()
