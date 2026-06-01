import telebot
import requests
import time

TELEGRAM_TOKEN = "8989531329:AAGMsy97tRPmIFc1-95CKVQJ-i2_ys3TM7o"
GEMINI_API_KEY = "AQ.Ab8RN6LtcQABIRDXujD-bgRaK7CbQdkYp1uqW1zXKLzK5dSobg"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        f"✨ Привет, {message.from_user.first_name}! ✨\n\n"
        "Я твой личный ИИ-помощник от GimoStudios и Xile Mobile!\n"
        "Ты можешь спросить у меня что угодно, и я отвечу с помощью нейросети Gemini.\n\n"
        "💬 Просто напиши свой вопрос!\n"
        "🖼 Хочешь картинку? Напиши «нарисуй [описание]»\n"
        "🔢 Напиши 67 — получишь сюрприз 😉"
    )
    bot.send_message(message.chat.id, welcome)

@bot.message_handler(content_types=['text'])
def chat(message):
    text = message.text.strip()
    
    # Пасхалка 67
    if text == "67":
        spam = "67\n" * 100
        bot.send_message(message.chat.id, spam.strip())
        return
    
    # Генерация картинок
    if text.lower().startswith("нарисуй"):
        prompt = text[7:].strip()
        if not prompt:
            bot.reply_to(message, "Пожалуйста, напиши что нарисовать. Например: «нарисуй котика»")
            return
        image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024"
        try:
            img = requests.get(image_url, timeout=30).content
            bot.send_photo(message.chat.id, img, caption=f"Вот твой рисунок: {prompt}")
        except:
            bot.reply_to(message, "Не получилось создать картинку. Попробуй другой запрос.")
        return
    
    # Общение с Gemini (с повторами)
    bot.send_chat_action(message.chat.id, 'typing')
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }
    
    for attempt in range(3):
        try:
            resp = requests.post(GEMINI_URL, json=data, headers=headers, timeout=30).json()
            if 'candidates' in resp:
                answer = resp['candidates'][0]['content']['parts'][0]['text']
                bot.reply_to(message, answer)
                return
            elif 'error' in resp:
                error_msg = resp['error'].get('message', '')
                if 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                    time.sleep(5)
                else:
                    bot.reply_to(message, f"Ошибка API: {error_msg}")
                    return
        except:
            time.sleep(2)
    
    bot.reply_to(message, "ИИ задумался... Попробуй ещё раз через пару секунд!")

bot.infinity_polling()
