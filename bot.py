import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from ai_integration_openrouter import generate_profession_recommendations, parse_ai_response
from db import init_db, add_profession_to_db, get_random_profession_from_db

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Школьные предметы
SUBJECTS = [
    "Русский язык", "Литература", "Иностранный язык", "Алгебра и начала анализа",
    "Геометрия", "Информатика", "Физика", "Химия", "Биология", "История",
    "Обществознание", "География", "Физкультура", "Основы безопасности и защиты Родины",
    "Разговоры о важном"
]

user_data = {}

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Начать тест", callback_data='start_test')],
        [InlineKeyboardButton("Случайная профессия", callback_data='random_profession')]
    ]
    update.message.reply_text(
        "🚀 Привет! Я помогу тебе выбрать карьеру. Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def ask_subject(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"answers": []}

    buttons = []
    for i, subject in enumerate(SUBJECTS):
        buttons.append([InlineKeyboardButton(subject, callback_data=f"subject_{i}")])
    buttons.append([InlineKeyboardButton("✅ Готово", callback_data="finish")])

    query.edit_message_text("Выбери свои любимые школьные предметы:", reply_markup=InlineKeyboardMarkup(buttons))

def handle_subject_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    idx = int(query.data.split('_')[1])
    subject = SUBJECTS[idx]

    if subject in user_data[user_id]["answers"]:
        user_data[user_id]["answers"].remove(subject)
    else:
        user_data[user_id]["answers"].append(subject)

    buttons = []
    for i, s in enumerate(SUBJECTS):
        if s in user_data[user_id]["answers"]:
            buttons.append([InlineKeyboardButton(f"✅ {s}", callback_data=f"subject_{i}")])
        else:
            buttons.append([InlineKeyboardButton(s, callback_data=f"subject_{i}")])
    buttons.append([InlineKeyboardButton("✅ Готово", callback_data="finish")])

    try:
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        if "Message is not modified" not in str(e):
            logging.error(e)

    query.answer()

def finish_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    selected_subjects = user_data[user_id]["answers"]

    if not selected_subjects:
        query.answer("Вы не выбрали ни один предмет!")
        return

    query.edit_message_text("🧠 Анализируем ваши интересы...")

    raw_ai_response = generate_profession_recommendations(selected_subjects)

    if raw_ai_response:
        try:
            professions_list = parse_ai_response(raw_ai_response)
            for prof in professions_list:
                add_profession_to_db(prof, selected_subjects)

            query.edit_message_text(raw_ai_response)
        except Exception as e:
            logging.error(f"Ошибка при парсинге/сохранении: {e}")
            query.edit_message_text(raw_ai_response)
    else:
        profession = get_random_profession_from_db()
        if profession:
            education_links = '\n  '.join(profession['education'])
            text = (
                f"📚 Мы не смогли получить ответ от ИИ, но нашли случайную профессию:\n\n"
                f"💼 *{profession['name']}*\n\n"
                f"{profession['description']}\n\n"
                f"💰 Зарплата:\n"
                f"  - {profession['salary']}\n\n"
                f"📚 Где учиться:\n"
                f"  {education_links}"
            )
            query.edit_message_text(text, parse_mode="Markdown")
        else:
            query.edit_message_text("❌ Не удалось получить ответ от ИИ и в БД нет профессий.")

def random_profession(update: Update, context: CallbackContext):
    query = update.callback_query
    profession = get_random_profession_from_db()
    if profession:
        education_links = '\n  '.join(profession['education'])
        text = (
            f"💼 *{profession['name']}*\n\n"
            f"{profession['description']}\n\n"
            f"💰 Зарплата:\n"
            f"  - {profession['salary']}\n\n"
            f"📚 Где учиться:\n"
            f"  {education_links}"
        )
        query.edit_message_text(text, parse_mode="Markdown")
    else:
        query.edit_message_text("❌ База данных пока пуста.")

def main():
    from config import BOT_TOKEN
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(ask_subject, pattern='start_test'))
    dp.add_handler(CallbackQueryHandler(handle_subject_choice, pattern=r'subject_\d+'))
    dp.add_handler(CallbackQueryHandler(finish_selection, pattern='finish'))
    dp.add_handler(CallbackQueryHandler(random_profession, pattern='random_profession'))

    print("🚀 Бот запущен...")
    init_db()
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("🚀 Запуск бота...")
    main()