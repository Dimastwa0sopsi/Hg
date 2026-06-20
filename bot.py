import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== КОНФИГ ==========
BOT_TOKEN = "8999200261:AAEpyHzNYgbDntnx3GZ8o11WJWkMqULNtM8"  # ВСТАВЬ ТОКЕН
ADMIN_ID = 7761721600
USERS_FILE = "users.txt"
LOG_FILE = "bot_log.txt"

logging.basicConfig(level=logging.INFO)

# ========== ФУНКЦИИ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        return True
    return False

def get_all_users():
    return load_users()

def log_action(action, user_id, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action} | User: {user_id} | {details}"
    logging.info(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

# ========== УСЛУГИ ==========
services = [
    {
        "name": "🌐 Сайт под ключ",
        "price": "200 ₽",
        "desc": "Создание и настройка сайта навсегда. GitHub, SSL, неон-дизайн.",
        "link": "https://t.me/Kitty_Kittys"
    },
    {
        "name": "🤖 Telegram-бот",
        "price": "50 ₽",
        "desc": "Боты на BotHost, Python 24/7. Для продаж, игр, администрирования.",
        "link": "https://t.me/Kitty_Kittys"
    },
    {
        "name": "🎨 Дизайн",
        "price": "100 ₽",
        "desc": "Киберпанк, неон, минимализм. Адаптив, анимации, glow-эффекты.",
        "link": "https://t.me/Kitty_Kittys"
    }
]

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📔 Заказать", callback_data="order")],
        [InlineKeyboardButton("🟥 Поддержка", callback_data="support")],
        [InlineKeyboardButton("❗ Правила", callback_data="rules")],
        [InlineKeyboardButton("🌐 Сайт", callback_data="site")]
    ])

def services_keyboard():
    keyboard = []
    for idx, service in enumerate(services):
        keyboard.append([InlineKeyboardButton(
            f"{service['name']} — {service['price']}",
            callback_data=f"service_{idx}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ])

def service_detail_keyboard(service):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Написать менеджеру", url=service['link'])],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_services")]
    ])

# ========== СОСТОЯНИЯ ==========
user_support_mode = {}
admin_news_mode = {}

# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if save_user(user_id):
        log_action("NEW_USER", user_id, f"@{user.username or 'без username'}")
    
    log_action("START", user_id, f"@{user.username or 'без username'}")
    await update.message.reply_text(
        "🤖 Привет! Я бот GimPrograms.\n"
        "Выбери пункт меню 👇",
        reply_markup=main_keyboard()
    )

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Нет прав.")
        return
    
    admin_news_mode[user_id] = True
    await update.message.reply_text(
        "📢 Режим рассылки\n\n"
        "Отправь мне сообщение, которое нужно разослать всем пользователям.\n"
        "Это может быть: текст, фото, видео, документ — что угодно.\n\n"
        "Чтобы отменить: /cancel_news"
    )

async def cancel_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID and admin_news_mode.get(user_id, False):
        admin_news_mode[user_id] = False
        await update.message.reply_text("❌ Рассылка отменена.")
    else:
        await update.message.reply_text("Нет активной рассылки.")

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Нет прав.")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("📌 /chat user_id текст")
        return
    
    try:
        target_id = int(args[0])
        reply = " ".join(args[1:])
        await context.bot.send_message(chat_id=target_id, text=f"🟥 Ответ поддержки:\n\n{reply}")
        await update.message.reply_text(f"✅ Отправлено пользователю {target_id}.")
        log_action("ADMIN_CHAT", user_id, f"To: {target_id}")
    except ValueError:
        await update.message.reply_text("❌ Неверный ID пользователя.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def offchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ Нет прав.")
        return
    
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("📌 /offchat user_id")
        return
    
    try:
        target_id = int(args[0])
        await context.bot.send_message(chat_id=target_id, text="🟥 Поддержка завершила диалог.")
        await update.message.reply_text(f"✅ Чат с {target_id} закрыт.")
        log_action("ADMIN_OFFCHAT", user_id, f"User: {target_id}")
    except ValueError:
        await update.message.reply_text("❌ Неверный ID пользователя.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# ========== КНОПКИ ==========
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    log_action("CALLBACK", user_id, data)

    if data == "order":
        await show_services(query)
    elif data == "support":
        await start_support(query)
    elif data == "rules":
        await show_rules(query)
    elif data == "site":
        await show_site(query)
    elif data.startswith("service_"):
        await show_service_detail(query, data)
    elif data == "back_to_menu":
        if user_id in user_support_mode:
            del user_support_mode[user_id]
        await query.edit_message_text("🏠 Главное меню", reply_markup=main_keyboard())
    elif data == "back_to_services":
        await show_services(query)

async def show_services(query):
    await query.edit_message_text(
        "📔 Наши услуги:\nВыберите интересующую услугу.",
        reply_markup=services_keyboard()
    )

async def show_service_detail(query, data):
    idx = int(data.split("_")[1])
    service = services[idx]
    text = (
        f"{service['name']}\n"
        f"💰 Цена: {service['price']}\n"
        f"📝 {service['desc']}\n\n"
        f"Для заказа свяжитесь с менеджером:"
    )
    await query.edit_message_text(text, reply_markup=service_detail_keyboard(service))

async def start_support(query):
    user_id = query.from_user.id
    user_support_mode[user_id] = True
    await query.edit_message_text(
        "🟥 Поддержка\n\nОпишите вашу проблему одним сообщением.\n"
        "Мы ответим вам как можно быстрее.\n\n"
        "⚠️ Срочно: @Kitty_Kittys",
        reply_markup=back_keyboard()
    )

async def show_rules(query):
    text = (
        "❗ ПРАВИЛА\n\n"
        "1️⃣ Цены фиксированы при заказе.\n"
        "2️⃣ Заказ через сайт или бота.\n"
        "3️⃣ Возврат: до начала работы — 100%, после начала — пропорционально.\n"
        "4️⃣ Данные не передаются третьим лицам.\n"
        "5️⃣ Ответственность за использование — на пользователе."
    )
    await query.edit_message_text(text, reply_markup=back_keyboard())

async def show_site(query):
    await query.message.reply_text(
        "🌐 НАШ САЙТ\n\n[Нажмите, чтобы перейти](https://dimastwa0sopsi.github.io/GimProgramsWeb/)",
        disable_web_page_preview=True,
        reply_markup=back_keyboard()
    )
    await query.delete_message()

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
async def handle_news_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщение от админа для рассылки"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID or not admin_news_mode.get(user_id, False):
        return
    
    users = get_all_users()
    if not users:
        await update.message.reply_text("❌ Нет пользователей для рассылки.")
        admin_news_mode[user_id] = False
        return
    
    status_msg = await update.message.reply_text(
        f"⏳ Начинаю рассылку для {len(users)} пользователей..."
    )
    
    success_count = 0
    fail_count = 0
    
    for target_id in users:
        try:
            await context.bot.copy_message(
                chat_id=target_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id,
                caption=update.message.caption
            )
            success_count += 1
        except Exception as e:
            fail_count += 1
            log_action("NEWS_FAIL", target_id, str(e)[:50])
    
    admin_news_mode[user_id] = False
    
    await status_msg.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"📤 Успешно: {success_count}\n"
        f"❌ Ошибок: {fail_count}\n"
        f"📊 Всего: {len(users)}"
    )
    
    log_action("NEWS_COMPLETE", user_id, f"Sent: {success_count}, Failed: {fail_count}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text
    log_action("MESSAGE", user_id, text[:50] if text else "[не текст]")

    # Проверка: админ ждёт новость
    if user_id == ADMIN_ID and admin_news_mode.get(user_id, False):
        await handle_news_message(update, context)
        return

    # Поддержка
    if user_support_mode.get(user_id, False):
        admin_text = (
            f"🆘 НОВОЕ ОБРАЩЕНИЕ\n"
            f"👤 @{user.username or 'без username'} (ID: {user_id})\n"
            f"📅 {update.message.date.strftime('%d.%m.%Y %H:%M')}\n"
            f"💬 {text}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
            await update.message.reply_text("✅ Обращение принято! Мы ответим вам.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка отправки: {e}")
        
        user_support_mode[user_id] = False
        await update.message.reply_text("🏠 Главное меню", reply_markup=main_keyboard())
    else:
        await update.message.reply_text("Используй кнопки или /start", reply_markup=main_keyboard())

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chat", chat_command))
    app.add_handler(CommandHandler("offchat", offchat_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("cancel_news", cancel_news))
    
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_message))
    
    print("🤖 Бот GimPrograms запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
