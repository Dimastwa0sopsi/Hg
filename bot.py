import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ТВОЙ ТОКЕН
TOKEN = "8098687202:AAGPX4yoHSgYBuD6k8aJew121G3fwsfDer4"

logging.basicConfig(level=logging.INFO)

# КЛАВИАТУРА
main_keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("💼 Услуги"), KeyboardButton("🏢 Проекты")],
    [KeyboardButton("📧 Контакты"), KeyboardButton("❓ Помощь")],
    [KeyboardButton("🎛️ Меню")]
], resize_keyboard=True)

# СТАРТ
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Привет! Я помощник студии GimPrograms.\n"
        "Я покажу тебе услуги, проекты и контакты.\n"
        "Используй кнопки внизу 👇",
        reply_markup=main_keyboard
    )

# ОБРАБОТЧИК ТЕКСТА
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎛️ Меню":
        await update.message.reply_text("🏠 Главное меню", reply_markup=main_keyboard)
        return

    if text == "💼 Услуги":
        await update.message.reply_text(
            "💼 Услуги GimPrograms\n\n"
            "🌐 Сайты под ключ — от 200 ₽\n"
            "🤖 Telegram-боты — от 50 ₽\n"
            "🎨 Дизайн — от 100 ₽\n\n"
            "⚠️ Временно новые заказы не принимаем."
        )
        return

    if text == "🚀 Проекты":
        await update.message.reply_text(
            "🚀 Наши проекты:\n\n"
            "🔹 Xile Mobile — https://dimastwa0sopsi.github.io/XileMobile/\n"
            "🔹 GimGame — https://dimastwa0sopsi.github.io/sgames/\n"
            "🔹 GimStudios  — https://dimastwa0sopsi.github.io/GimProgramsWeb/"
        )
        return

    if text == "📧 Контакты":
        await update.message.reply_text(
            "📧 Связь с нами:\n\n"
            "📨 Email: dimastvincs@gmail.com\n"
            "📱 Telegram: @Kitty_Kittys\n"
            "🔗 MAX: https://clck.ru/3TLeHu"
        )
        return

    if text == "❓ Помощь":
        await update.message.reply_text(
            "❓ Часто задаваемые вопросы:\n\n"
            "🔹 Как заказать?\n"
            "Напиши в Telegram @Kitty_Kittys или на почту.\n\n"
            "🔹 Есть ли гарантия?\n"
            "Да, на все услуги.\n\n"
            "🔹 Когда возобновятся заказы?\n"
            "Временно приостановлены. Следи за новостями."
        )
        return

    # Если текст не совпадает с кнопками
    await update.message.reply_text(
        "Я не знаю такой команды.\n"
        "Используй кнопки внизу или напиши /start."
    )

# ЗАПУСК
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Бот запущен")
    app.run_polling()

if name == "main":
    main()
