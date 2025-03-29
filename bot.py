import logging
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ChatMemberHandler,
    filters,
    ContextTypes
)

# ---------------------------------------
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ---------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Отключаем (понижаем уровень) детальные логи от внутренних модулей, чтобы не засоряли консоль
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.bot").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ---------------------------------------
# КОНСТАНТЫ И СОСТОЯНИЯ
# ---------------------------------------
# Для заказа услуги (два шага):
ORDER_PROJECT, ORDER_NAME_PHONE = range(2)

# Для /newpost (четыре шага):
NP_TEXT, NP_NEED_BUTTON, NP_BUTTON_URL, NP_BUTTON_TEXT = range(4)

# IDs и токен
ADMIN_ID = 2045410830
GROUP_CHAT_ID = "@applab_ua"
TOKEN = "7548740282:AAGjI2kJsiVC8C1dJWHU9EXDHdEF2BVJgkM"

# ---------------------------------------
# ОБРАБОТЧИК /start
# ---------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Приветственное сообщение с фото, кратким описанием, списком услуг и 2 кнопками:
    - «Замовити додаток 📱»
    - «AppLab 🤖»
    Логируем нажатие команды /start (кто нажал и когда).
    """
    user = update.effective_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{now}] {user.full_name} (ID: {user.id}) использовал команду /start")

    # Текст услуг
    services_text = (
        "1. 🎮 Додатки для Telegram (клікери, P2E, міні-ігри)\n"
        "2. 🤖 Розумні Telegram-боти для продажів\n"
        "3. 🧠🤖 Додатки та боти з штучним інтелектом\n"
        "4. 📱 Мобільні додатки для App Store та Google Play\n"
        "5. 💳 Інтернет-магазини з інтеграцією оплат\n"
        "6. 📈 Торгові боти для трейдингу\n"
        "7. ⚙️ Автоматизація бізнесу\n"
        "8. 🔮 Інтеграція штучного інтелекту\n"
        "9. 🌐🔗 Сайти та блокчейн-додатки\n"
    )
    caption_text = (
        "🚀 Ласкаво просимо до AppLab! 🚀\n\n"
        "Ми створюємо інноваційні додатки, боти та веб-рішення для вашого бізнесу.\n\n"
        f"{services_text}\n"
        "Оберіть послугу, щоб дізнатись більше."
    )

    # Клавиатура
    keyboard = [
        [InlineKeyboardButton("Замовити додаток 📱", callback_data="order_app")],
        [InlineKeyboardButton("AppLab 🤖", web_app=WebAppInfo(url="https://applabua.github.io/AppLab/"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="https://i.ibb.co/MyKXZPRf/photo-2025-03-04-09-29-07.jpg",
        caption=caption_text,
        reply_markup=reply_markup
    )

# ---------------------------------------
# CALLBACK: "Замовити додаток 📱"
# ---------------------------------------
async def order_app_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Вызывается, когда пользователь нажимает кнопку «Замовити додаток 📱».
    Логируем нажатие и отправляем меню услуг.
    """
    query = update.callback_query
    user = update.effective_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{now}] {user.full_name} (ID: {user.id}) нажал кнопку 'Замовити додаток'")

    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🎮 Додатки для Telegram (клікери, P2E, міні-ігри)", callback_data="select_service_1")],
        [InlineKeyboardButton("🤖 Розумні Telegram-боти для продажів", callback_data="select_service_2")],
        [InlineKeyboardButton("🧠🤖 Додатки та боти з штучним інтелектом", callback_data="select_service_3")],
        [InlineKeyboardButton("📱 Мобільні додатки для App Store та Google Play", callback_data="select_service_4")],
        [InlineKeyboardButton("💳 Інтернет-магазини з інтеграцією оплат", callback_data="select_service_5")],
        [InlineKeyboardButton("📈 Торгові боти для трейдингу", callback_data="select_service_6")],
        [InlineKeyboardButton("⚙️ Автоматизація бізнесу", callback_data="select_service_7")],
        [InlineKeyboardButton("🔮 Інтеграція штучного інтелекту", callback_data="select_service_8")],
        [InlineKeyboardButton("🌐🔗 Сайти та блокчейн-додатки", callback_data="select_service_9")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Оберіть послугу:", reply_markup=reply_markup)

# ---------------------------------------
# CALLBACK: выбор конкретной услуги
# ---------------------------------------
async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Когда пользователь нажимает на одну из услуг (select_service_1 и т.д.).
    Логируем, какую услугу выбрал пользователь.
    Затем спрашиваем описание проекта.
    """
    query = update.callback_query
    user = update.effective_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await query.answer()
    service_number = query.data.split("_")[-1]
    services = {
        "1": "Додатки для Telegram (клікери, P2E, міні-ігри)",
        "2": "Розумні Telegram-боти для продажів",
        "3": "Додатки та боти з штучним інтелектом",
        "4": "Мобільні додатки для App Store та Google Play",
        "5": "Інтернет-магазини з інтеграцією оплат",
        "6": "Торгові боти для трейдингу",
        "7": "Автоматизація бізнесу",
        "8": "Інтеграція штучного інтелекту",
        "9": "Сайти та блокчейн-додатки"
    }
    service_title = services.get(service_number, "Невідома послуга")

    logger.info(f"[{now}] {user.full_name} (ID: {user.id}) выбрал услугу: {service_title}")

    context.user_data["selected_service"] = service_title
    text = (
        f"Ви обрали: {service_title}\n\n"
        "Опишіть коротко ваш проєкт:"
    )
    await query.message.reply_text(text)
    return ORDER_PROJECT

# ---------------------------------------
# ШАГ 1: Получаем описание проекта
# ---------------------------------------
async def order_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Пользователь присылает описание проекта.
    Сохраняем и переходим к запросу имени и номера телефона.
    """
    context.user_data["project_description"] = update.message.text
    await update.message.reply_text(
        "Дякуємо! Тепер введіть ваше ім'я та номер телефону:"
    )
    return ORDER_NAME_PHONE

# ---------------------------------------
# ШАГ 2: Получаем имя и номер телефона
# ---------------------------------------
async def order_name_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Пользователь присылает имя и телефон.
    Собираем всю информацию и отправляем админу.
    """
    context.user_data["name_phone"] = update.message.text

    service = context.user_data.get("selected_service", "Невідома послуга")
    project = context.user_data.get("project_description", "")
    name_phone = context.user_data.get("name_phone", "")

    message_to_admin = (
        f"Нове замовлення:\n"
        f"Послуга: {service}\n"
        f"Проєкт: {project}\n"
        f"Ім'я та телефон: {name_phone}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=message_to_admin)
        await update.message.reply_text(
            "Дякуємо, ми з вами зв’яжемося протягом години.\n"
            "Якщо у вас є додаткові питання, зверніться до @applab_manager."
        )
    except Exception as e:
        logger.error(f"Помилка при надсиланні замовлення: {e}")
        await update.message.reply_text("Виникла помилка при надсиланні замовлення.")

    return ConversationHandler.END

# ---------------------------------------
# /newpost ДЛЯ АДМИНИСТРАТОРА
# ---------------------------------------
async def start_newpost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{now}] {user.full_name} (ID: {user.id}) использовал /newpost")

    if user.id != ADMIN_ID:
        await update.message.reply_text("Вибачте, ця команда доступна лише адміністратору.")
        return ConversationHandler.END

    await update.message.reply_text("Введіть текст публікації:")
    return NP_TEXT

async def receive_newpost_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["newpost_text"] = update.message.text
    await update.message.reply_text("Чи потрібна кнопка? Напишіть 'так' або 'ні'.")
    return NP_NEED_BUTTON

async def newpost_need_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().lower()
    if answer == "так":
        await update.message.reply_text("Введіть URL для кнопки:")
        return NP_BUTTON_URL
    else:
        post_text = context.user_data.get("newpost_text", "")
        try:
            await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=post_text)
            await update.message.reply_text("Публікацію надіслано!")
        except Exception as e:
            logger.error(f"Помилка при надсиланні публікації: {e}")
            await update.message.reply_text("Виникла помилка при надсиланні публікації.")
        return ConversationHandler.END

async def newpost_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["button_url"] = update.message.text.strip()
    await update.message.reply_text("Введіть назву для кнопки:")
    return NP_BUTTON_TEXT

async def newpost_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    button_text = update.message.text.strip()
    post_text = context.user_data.get("newpost_text", "")
    button_url = context.user_data.get("button_url", "")
    keyboard = [
        [InlineKeyboardButton(button_text, url=button_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=post_text, reply_markup=reply_markup)
        await update.message.reply_text("Публікацію надіслано!")
    except Exception as e:
        logger.error(f"Помилка при надсиланні публікації: {e}")
        await update.message.reply_text("Виникла помилка при надсиланні публікації.")
    return ConversationHandler.END

# ---------------------------------------
# /cancel (отмена любого ConversationHandler)
# ---------------------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{now}] {user.full_name} (ID: {user.id}) отменил операцию /cancel")

    await update.message.reply_text("Операцію скасовано.")
    return ConversationHandler.END

# ---------------------------------------
# ОТСЛЕЖИВАНИЕ УЧАСТНИКОВ В ГРУППЕ/СУПЕРГРУППЕ
# ---------------------------------------
async def track_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Вызывается, когда статус участника чата (группы/супергруппы) меняется.
    Мы будем фиксировать всех, кто "зашёл" (new_status = 'member' или 'administrator' и т.д.).
    Сохраняем в set() bot_data["channel_visitors"].
    """
    chat_id = update.chat_member.chat.id
    # Если хотите отслеживать только конкретный чат, можно проверить:
    # if chat_id != -1001234567890: return

    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status
    user = update.chat_member.new_chat_member.user

    # Инициализируем хранилище посетителей
    if "channel_visitors" not in context.bot_data:
        context.bot_data["channel_visitors"] = set()

    # Если пользователь стал участником (member/administrator/creator), логируем
    if new_status in ("member", "administrator", "creator") and old_status not in ("member", "administrator", "creator"):
        context.bot_data["channel_visitors"].add((user.id, user.full_name))
        logger.info(f"User {user.full_name} (ID: {user.id}) joined chat {chat_id}")

# ---------------------------------------
# Команда /channel_visitors – кто заходил
# ---------------------------------------
async def show_channel_visitors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет список зашедших участников из bot_data["channel_visitors"].
    """
    if "channel_visitors" not in context.bot_data or not context.bot_data["channel_visitors"]:
        await update.message.reply_text("Поки що ніхто не заходив.")
        return

    visitors_list = list(context.bot_data["channel_visitors"])
    # Формируем текст-список
    text_lines = []
    for user_id, full_name in visitors_list:
        text_lines.append(f"- {full_name} (ID: {user_id})")

    text_result = "Список користувачів, які заходили в групу:\n" + "\n".join(text_lines)
    await update.message.reply_text(text_result)

# ---------------------------------------
# MAIN
# ---------------------------------------
def main() -> None:
    """
    Точка входа в бота.
    """
    application = ApplicationBuilder().token(TOKEN).build()

    # -----------------------------------
    # 1) Conversation для заказа услуги
    # -----------------------------------
    order_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_service, pattern="^select_service_")],
        states={
            ORDER_PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_project)],
            ORDER_NAME_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name_phone)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    application.add_handler(order_conv_handler)

    # -----------------------------------
    # 2) Conversation для /newpost
    # -----------------------------------
    newpost_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("newpost", start_newpost)],
        states={
            NP_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_newpost_text)],
            NP_NEED_BUTTON: [MessageHandler(filters.TEXT & ~filters.COMMAND, newpost_need_button)],
            NP_BUTTON_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, newpost_button_url)],
            NP_BUTTON_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, newpost_button_text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(newpost_conv_handler)

    # -----------------------------------
    # /start
    # -----------------------------------
    application.add_handler(CommandHandler("start", start))

    # -----------------------------------
    # Callback для кнопки «Замовити додаток 📱»
    # -----------------------------------
    application.add_handler(CallbackQueryHandler(order_app_callback, pattern="^order_app$"))

    # -----------------------------------
    # Отслеживание новых участников (ChatMemberHandler)
    # -----------------------------------
    application.add_handler(ChatMemberHandler(track_chat_members, ChatMemberHandler.CHAT_MEMBER))

    # -----------------------------------
    # Команда /channel_visitors
    # -----------------------------------
    application.add_handler(CommandHandler("channel_visitors", show_channel_visitors))

    # -----------------------------------
    # Запуск бота
    # -----------------------------------
    application.run_polling()

if __name__ == "__main__":
    main()
