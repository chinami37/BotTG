from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Настройка подключения к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("/opt/render/project/src/service_account.json", scope)

client = gspread.authorize(credentials)
sheet = client.open("Feedback").sheet1  # Убедитесь, что таблица существует

# Этапы разговора
PERSONAL, FOOD, SERVING, CLEANLINESS, PRICES, WISHES = range(6)

# Функция начала разговора
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["user_id"] = update.effective_user.id  # Сохраняем ID пользователя
    await update.message.reply_text(
        "Здравствуйте! Мы хотим узнать ваше мнение о нашем заведении.\n"
        "Пожалуйста, оцените каждый из пунктов по 10-бальной шкале. Для выхода отправьте /cancel."
    )
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Оцените персонал (1-10):", reply_markup=reply_markup
    )
    return PERSONAL

# Получение оценки персонала
async def personal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["personal"] = update.message.text
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Спасибо! Теперь оцените качество еды (1-10):", reply_markup=reply_markup
    )
    return FOOD

# Получение оценки качества еды
async def food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["food"] = update.message.text
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Спасибо! Теперь оцените подачу блюд (1-10):", reply_markup=reply_markup
    )
    return SERVING

# Получение оценки подачи блюд
async def serving(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["serving"] = update.message.text
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Спасибо! Теперь оцените чистоту в зале (1-10):", reply_markup=reply_markup
    )
    return CLEANLINESS

# Получение оценки чистоты
async def cleanliness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["cleanliness"] = update.message.text
    keyboard = [[str(i) for i in range(1, 11)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Спасибо! Теперь оцените цены на блюда (1-10):", reply_markup=reply_markup
    )
    return PRICES

# Получение оценки цен
async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["prices"] = update.message.text
    await update.message.reply_text(
        "Спасибо! Теперь напишите свои пожелания или предложения:", reply_markup=ReplyKeyboardRemove()
    )
    return WISHES

# Получение пожеланий и запись в Google Sheets
async def wishes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["wishes"] = update.message.text
    user_id = context.user_data["user_id"]  # Получаем ID пользователя
    data = [
        user_id,
        context.user_data.get("personal", ""),
        context.user_data.get("food", ""),
        context.user_data.get("serving", ""),
        context.user_data.get("cleanliness", ""),
        context.user_data.get("prices", ""),
        context.user_data.get("wishes", ""),
    ]
    sheet.append_row(data)  # Запись данных в Google Sheets
    await update.message.reply_text(
        "Спасибо за ваш отзыв! Мы обязательно учтём ваши пожелания."
    )
    return ConversationHandler.END

# Завершение разговора
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Опрос завершён. Если хотите начать заново, отправьте /start.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Основная функция
def main() -> None:
    application = Application.builder().token("7900292181:AAG8qnPeKmINv9rF47PLJwUzdJ8mfzh984M").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PERSONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, personal)],
            FOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, food)],
            SERVING: [MessageHandler(filters.TEXT & ~filters.COMMAND, serving)],
            CLEANLINESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, cleanliness)],
            PRICES: [MessageHandler(filters.TEXT & ~filters.COMMAND, prices)],
            WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, wishes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()

