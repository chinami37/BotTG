from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Шаги опроса
PERSONAL, QUALITY, PRESENTATION, CLEANLINESS, PRICES, SUGGESTIONS = range(6)

# Словарь для хранения текущих ответов пользователя
user_feedback = {}


# Стартовый шаг
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[str(i) for i in range(1, 11)]]  # Кнопки от 1 до 10
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    user_feedback[update.effective_user.id] = {}  # Создаём словарь для конкретного пользователя
    await update.message.reply_text(
        "Здравствуйте! Мы хотим узнать ваше мнение о нашем заведении.\n"
        "Пожалуйста, оцените каждый из пунктов по 10-бальной шкале. "
        "Для выхода отправьте /cancel."
    )
    await update.message.reply_text("Оцените персонал (1-10):", reply_markup=reply_markup)
    return PERSONAL


# Шаг 1: Оценка персонала
async def personal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = update.message.text
    if not score.isdigit() or not (1 <= int(score) <= 10):
        await update.message.reply_text("Пожалуйста, выберите число от 1 до 10.")
        return PERSONAL

    user_feedback[update.effective_user.id]['Персонал'] = int(score)
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Оцените качество еды (1-10):", reply_markup=reply_markup)
    return QUALITY


# Шаг 2: Оценка качества еды
async def quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = update.message.text
    if not score.isdigit() or not (1 <= int(score) <= 10):
        await update.message.reply_text("Пожалуйста, выберите число от 1 до 10.")
        return QUALITY

    user_feedback[update.effective_user.id]['Качество еды'] = int(score)
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Оцените подачу блюд (1-10):", reply_markup=reply_markup)
    return PRESENTATION


# Шаг 3: Оценка подачи блюд
async def presentation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = update.message.text
    if not score.isdigit() or not (1 <= int(score) <= 10):
        await update.message.reply_text("Пожалуйста, выберите число от 1 до 10.")
        return PRESENTATION

    user_feedback[update.effective_user.id]['Подача'] = int(score)
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Оцените чистоту в зале (1-10):", reply_markup=reply_markup)
    return CLEANLINESS


# Шаг 4: Оценка чистоты в зале
async def cleanliness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = update.message.text
    if not score.isdigit() or not (1 <= int(score) <= 10):
        await update.message.reply_text("Пожалуйста, выберите число от 1 до 10.")
        return CLEANLINESS

    user_feedback[update.effective_user.id]['Чистота'] = int(score)
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Оцените цены на блюда (1-10):", reply_markup=reply_markup)
    return PRICES


# Шаг 5: Оценка цен
async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = update.message.text
    if not score.isdigit() or not (1 <= int(score) <= 10):
        await update.message.reply_text("Пожалуйста, выберите число от 1 до 10.")
        return PRICES

    user_feedback[update.effective_user.id]['Цены'] = int(score)
    await update.message.reply_text("Теперь вы можете оставить свои пожелания:", reply_markup=ReplyKeyboardRemove())
    return SUGGESTIONS


# Шаг 6: Личные пожелания
async def suggestions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    suggestion = update.message.text
    user_feedback[update.effective_user.id]['Пожелания'] = suggestion

    # Сохранение отзыва в файл
    with open("feedback.txt", "a", encoding="utf-8") as file:
        feedback = user_feedback[update.effective_user.id]
        file.write(f"Пользователь {update.effective_user.id}:\n")
        for key, value in feedback.items():
            file.write(f"{key}: {value}\n")
        file.write("------\n")

    await update.message.reply_text("Спасибо за ваш отзыв! Мы обязательно учтём ваши пожелания.",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# Прерывание опроса
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос прерван. До свидания!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    # Токен бота
    application = Application.builder().token("7900292181:AAG8qnPeKmINv9rF47PLJwUzdJ8mfzh984M").build()

    # Обработчик опроса
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PERSONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal)],
            QUALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quality)],
            PRESENTATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, presentation)],
            CLEANLINESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, cleanliness)],
            PRICES: [MessageHandler(filters.TEXT & ~filters.COMMAND, prices)],
            SUGGESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, suggestions)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
