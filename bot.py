import sqlite3
from datetime import datetime
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters, ContextTypes

# ========== КОНФИГУРАЦИЯ ==========
TOKEN = "8424133093:AAEOvW_Y0mpxDnk1h8XjrslWt8vP7ItG5Mw"  # Замените на ваш токен
ADMIN_ID = 7761721600  # ID администратора
DEV_LINK = "https://dimastwa0sopsi.github.io/GimStudiosWeb/"

# Состояния для ConversationHandler
NAME, ABOUT, CITY, AGE, PHOTO = range(5)

# ========== БАЗА ДАННЫХ ==========
def init_db():
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  name TEXT,
                  about TEXT,
                  city TEXT,
                  age INTEGER,
                  photo_id TEXT,
                  active INTEGER DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

def save_profile(user_id, name, about, city, age, photo_id):
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO users 
                 (user_id, name, about, city, age, photo_id, active) 
                 VALUES (?, ?, ?, ?, ?, ?, 1)''',
              (user_id, name, about, city, age, photo_id))
    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('SELECT name, about, city, age, photo_id FROM users WHERE user_id = ? AND active = 1', (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_all_profiles(exclude_user_id):
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('SELECT user_id, name, about, city, age, photo_id FROM users WHERE user_id != ? AND active = 1', (exclude_user_id,))
    results = c.fetchall()
    conn.close()
    return results

def delete_profile(user_id):
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def deactivate_profile(user_id):
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('UPDATE users SET active = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def activate_profile(user_id):
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('UPDATE users SET active = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('dating_bot.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    results = c.fetchall()
    conn.close()
    return [r[0] for r in results]

# ========== ДЕКОРАТОР ДЛЯ АДМИНА ==========
def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("⛔ У вас нет доступа к этой команде.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# ========== КЛАВИАТУРЫ ==========
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📝 Создать анкету", callback_data="create_profile")],
        [InlineKeyboardButton("🔍 Искать анкеты", callback_data="search")],
        [InlineKeyboardButton("⚙️ Меню", callback_data="menu")],
        [InlineKeyboardButton("👨‍💻 Разработчик", url=DEV_LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)

def menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔕 Отключить анкету", callback_data="deactivate")],
        [InlineKeyboardButton("🔍 Искать дальше", callback_data="search")],
        [InlineKeyboardButton("✏️ Изменить анкету", callback_data="edit_profile")],
        [InlineKeyboardButton("🗑️ Удалить анкету", callback_data="delete_profile")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("🗑️ Удалить анкету по ID", callback_data="admin_delete")],
        [InlineKeyboardButton("📢 Рассылка сообщения", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== ОБРАБОТЧИКИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌟 <b>Добро пожаловать в бот для знакомств!</b>\n\n"
        f"📌 <b>Функции бота:</b>\n"
        f"• Создайте свою анкету\n"
        f"• Ищите анкеты других пользователей\n"
        f"• Управляйте своей анкетой в меню\n\n"
        f"👇 <b>Нажмите кнопку ниже, чтобы создать анкету:</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "create_profile":
        await query.edit_message_text("Давай создадим твою анкету! Напиши своё <b>имя</b>:", parse_mode="HTML")
        return NAME
    
    elif data == "search":
        profiles = get_all_profiles(query.from_user.id)
        if not profiles:
            await query.edit_message_text("😔 Пока нет других анкет. Попробуй позже!", reply_markup=main_menu_keyboard())
            return ConversationHandler.END
        
        context.user_data['search_index'] = 0
        context.user_data['profiles'] = profiles
        await show_profile(update, context, query.from_user.id)
        return ConversationHandler.END
    
    elif data == "menu":
        await query.edit_message_text("⚙️ <b>Меню управления анкетой</b>", parse_mode="HTML", reply_markup=menu_keyboard())
    
    elif data == "main_menu":
        await query.edit_message_text("🏠 <b>Главное меню</b>", parse_mode="HTML", reply_markup=main_menu_keyboard())
    
    elif data == "deactivate":
        deactivate_profile(query.from_user.id)
        await query.edit_message_text("🔕 Ваша анкета отключена. Вы не будете показываться в поиске.", reply_markup=main_menu_keyboard())
    
    elif data == "delete_profile":
        delete_profile(query.from_user.id)
        await query.edit_message_text("🗑️ Ваша анкета удалена. Чтобы создать новую, нажмите 'Создать анкету'.", reply_markup=main_menu_keyboard())
    
    elif data == "edit_profile":
        await query.edit_message_text("✏️ Напишите новое <b>имя</b> (или отправьте /cancel для отмены):", parse_mode="HTML")
        context.user_data['edit_mode'] = True
        return NAME
    
    elif data == "next_profile":
        context.user_data['search_index'] += 1
        await show_profile(update, context, query.from_user.id)
    
    elif data == "admin_delete" and query.from_user.id == ADMIN_ID:
        await query.edit_message_text("Введите <b>ID пользователя</b>, анкету которого нужно удалить:", parse_mode="HTML")
        context.user_data['admin_mode'] = 'delete'
    
    elif data == "admin_broadcast" and query.from_user.id == ADMIN_ID:
        await query.edit_message_text("Введите <b>сообщение для рассылки</b> всем пользователям:", parse_mode="HTML")
        context.user_data['admin_mode'] = 'broadcast'
    
    return ConversationHandler.END

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    profiles = context.user_data.get('profiles', [])
    index = context.user_data.get('search_index', 0)
    
    if index >= len(profiles):
        await update.callback_query.edit_message_text("🎉 Вы просмотрели все анкеты! Новые появятся позже.", reply_markup=main_menu_keyboard())
        return
    
    profile = profiles[index]
    prof_user_id, name, about, city, age, photo_id = profile
    
    text = f"👤 <b>{name}</b>, {age} лет\n📍 <b>Город:</b> {city}\n📝 <b>О себе:</b> {about}"
    
    keyboard = [[InlineKeyboardButton("➡️ Следующая анкета", callback_data="next_profile")]]
    
    if photo_id:
        await update.callback_query.edit_message_caption(
            caption=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ========== СОЗДАНИЕ АНКЕТЫ ==========
async def create_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Давай создадим твою анкету! Напиши своё <b>имя</b>:", parse_mode="HTML")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("✨ Расскажи немного <b>о себе</b> (хобби, интересы и т.д.):", parse_mode="HTML")
    return ABOUT

async def get_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['about'] = update.message.text
    await update.message.reply_text("🏙️ В каком <b>городе</b> ты живешь?", parse_mode="HTML")
    return CITY

async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['city'] = update.message.text
    await update.message.reply_text("🎂 Сколько тебе <b>лет</b>?", parse_mode="HTML")
    return AGE

async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
        if age < 16 or age > 100:
            await update.message.reply_text("Пожалуйста, введите возраст от 16 до 100 лет.")
            return AGE
        context.user_data['age'] = age
        await update.message.reply_text("📸 Отправь своё <b>фото</b> (можно отправить как фото или файл):", parse_mode="HTML")
        return PHOTO
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число (ваш возраст).")
        return AGE

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1] if update.message.photo else None
    if not photo:
        await update.message.reply_text("Пожалуйста, отправьте фото.")
        return PHOTO
    
    photo_id = photo.file_id
    user_id = update.effective_user.id
    name = context.user_data['name']
    about = context.user_data['about']
    city = context.user_data['city']
    age = context.user_data['age']
    
    save_profile(user_id, name, about, city, age, photo_id)
    
    keyboard = [[InlineKeyboardButton("🔍 Искать анкеты", callback_data="search")]]
    
    await update.message.reply_photo(
        photo=photo_id,
        caption=f"🎉 <b>Поздравляю! Анкета создана!</b>\n\n"
                f"👤 {name}, {age} лет\n📍 {city}\n📝 {about}\n\n"
                f"👇 Нажми «Искать», чтобы найти анкеты других пользователей:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def edit_profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Напиши новое <b>имя</b>:", parse_mode="HTML")
    return NAME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.", reply_markup=main_menu_keyboard())
    context.user_data.clear()
    return ConversationHandler.END

# ========== АДМИН КОМАНДЫ ==========
@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 <b>Админ-панель</b>", parse_mode="HTML", reply_markup=admin_keyboard())

async def admin_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('admin_mode') == 'delete':
        try:
            user_id = int(update.message.text)
            delete_profile(user_id)
            await update.message.reply_text(f"✅ Анкета пользователя {user_id} удалена.", reply_markup=admin_keyboard())
        except:
            await update.message.reply_text("❌ Неверный ID. Попробуйте снова.", reply_markup=admin_keyboard())
        context.user_data['admin_mode'] = None
    
    elif context.user_data.get('admin_mode') == 'broadcast':
        msg = update.message.text
        users = get_all_users()
        success = 0
        for uid in users:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 <b>Рассылка от администратора:</b>\n\n{msg}", parse_mode="HTML")
                success += 1
            except:
                pass
        await update.message.reply_text(f"✅ Сообщение отправлено {success} пользователям.", reply_markup=admin_keyboard())
        context.user_data['admin_mode'] = None

# ========== ЗАПУСК БОТА ==========
def main():
    app = Application.builder().token(TOKEN).build()
    
    # ConversationHandler для создания анкеты
    conv_create = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^create_profile$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_about)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # ConversationHandler для редактирования
    conv_edit = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^edit_profile$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_about)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(conv_create)
    app.add_handler(conv_edit)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_text_handler))
    
    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
