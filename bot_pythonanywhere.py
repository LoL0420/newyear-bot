import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Безопасное получение токена
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    print("❌ ОШИБКА: Переменная BOT_TOKEN не установлена!")
    print("Добавьте её в настройках Render: Settings → Environment")
    exit(1)

print(f"✅ Токен загружен ({len(BOT_TOKEN)} символов)")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def is_leap_year(year):
    """Проверяет, является ли год високосным"""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def days_in_year(year):
    """Возвращает количество дней в году"""
    return 366 if is_leap_year(year) else 365


def days_until_new_year():
    """Считает дни до Нового Года"""
    today = datetime.now().date()
    next_year = today.year if today.month == 1 and today.day == 1 else today.year + 1
    new_year_date = datetime(next_year, 1, 1).date()
    delta = new_year_date - today
    return delta.days


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие"""
    user = update.effective_user

    message = (
        f"🎅 <b>Привет, {user.first_name}!</b>\n\n"
        f"🎄 Я <b>Хэппи Нью Э</b> — новогодний бот!\n\n"
        f"<b>📋 Доступные команды:</b>\n"
        f"/start - это сообщение\n"
        f"/days - сколько дней до Нового Года\n"
        f"/countdown - детальный отсчет\n"
        f"/progress - прогресс в процентах\n"
        f"/facts - интересные факты\n"
        f"/time - сколько осталось в часах\n"
        f"/help - помощь\n\n"
        f"<i>Попробуй разные команды!</i>"
    )

    await update.message.reply_html(message)


async def days_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /days - простой ответ"""
    days = days_until_new_year()

    if days == 0:
        message = "🎉🎊 <b>С НОВЫМ ГОДОМ!</b> 🎊🎉\nУра! Праздник наступил! 🥳"
    elif days == 1:
        message = f"🎄 Ура! До Нового Года остался всего <b>{days} день</b>!\nПора готовить салат оливье! 🥗"
    elif 2 <= days <= 4:
        message = f"🎄 Совсем скоро! До Нового Года осталось <b>{days} дня</b>!\nПроверь гирлянды! 💡"
    elif 5 <= days <= 20:
        message = f"🎄 До Нового Года осталось <b>{days} дней</b>!\nВремя закупать мандарины! 🍊"
    else:
        message = f"🎄 До Нового Года осталось <b>{days} дней</b>!\nЕще есть время подготовиться! 📅"

    # Добавим эмодзи в зависимости от времени
    hour = datetime.now().hour
    if 6 <= hour < 12:
        message += "\n\n☀️ Доброе утро!"
    elif 12 <= hour < 18:
        message += "\n\n🌤️ Добрый день!"
    elif 18 <= hour < 23:
        message += "\n\n🌙 Добрый вечер!"
    else:
        message += "\n\n🌜 Доброй ночи!"

    await update.message.reply_html(message)


async def countdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /countdown - детальный отсчет"""
    now = datetime.now()
    next_year = now.year if now.month == 1 and now.day == 1 else now.year + 1
    new_year = datetime(next_year, 1, 1, 0, 0, 0)

    # Вычисляем разницу
    time_left = new_year - now
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Прогресс-бар с учётом високосного года
    current_year_days = days_in_year(now.year)
    days_passed = current_year_days - days
    filled = min(10, max(1, days_passed) // (current_year_days // 10))
    progress = "🎁" * filled + "🔘" * (10 - filled)
    percent = (days_passed / current_year_days) * 100

    message = (
        f"⏳ <b>Детальный отсчет до Нового Года:</b>\n\n"
        f"📅 <b>Дней:</b> {days}\n"
        f"🕐 <b>Часов:</b> {hours}\n"
        f"⏰ <b>Минут:</b> {minutes}\n"
        f"⚡ <b>Секунд:</b> {seconds}\n\n"
        f"📊 <b>Прогресс года:</b>\n"
        f"{progress}\n"
        f"{percent:.1f}% выполнено\n\n"
        f"<i>Тикают секунды... ⏱️</i>"
    )

    await update.message.reply_html(message)


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /progress - прогресс в процентах"""
    now = datetime.now()
    days = days_until_new_year()
    current_year_days = days_in_year(now.year)

    # Процент выполнения года
    percent_done = ((current_year_days - days) / current_year_days) * 100
    percent_left = (days / current_year_days) * 100

    # Визуализация (10 эмодзи)
    done_emojis = int(percent_done / 10)  # 10 эмодзи = 100%
    left_emojis = 10 - done_emojis

    # Создаем прогресс-бар
    progress_bar = "🎁" * done_emojis + "🔘" * left_emojis

    # Определяем сезон
    month = now.month
    if month in [12, 1, 2]:
        season = "❄️ Зима"
    elif month in [3, 4, 5]:
        season = "🌸 Весна"
    elif month in [6, 7, 8]:
        season = "☀️ Лето"
    else:
        season = "🍂 Осень"

    message = (
        f"📊 <b>Прогресс {now.year} года:</b>\n\n"
        f"✅ <b>Выполнено:</b> {percent_done:.1f}%\n"
        f"🎯 <b>Осталось:</b> {percent_left:.1f}%\n"
        f"🌤️ <b>Сезон:</b> {season}\n"
        f"📅 <b>Дней в году:</b> {current_year_days}\n\n"
        f"{progress_bar}\n\n"
        f"⏱️ <b>До Нового Года:</b> {days} дней\n"
        f"📅 Это примерно {days // 30} месяцев и {days % 30} дней\n\n"
        f"<i>Каждый день приближает к празднику! 🎄</i>"
    )

    await update.message.reply_html(message)


async def facts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /facts - интересные факты"""
    days = days_until_new_year()

    facts = [
        "🎄 В России Новый Год стали отмечать 1 января с 1700 года по указу Петра I",
        "🌍 Первой встречает Новый Год страна Кирибати в Тихом океане",
        "🎆 Традиция фейерверков пришла из Древнего Китая для отпугивания злых духов",
        "🎅 Современный Дед Мороз появился в СССР в 1930-х годах",
        "🥂 Шампанское стало новогодним напитком в России только в XIX веке",
        "🕰️ До 1700 года Новый Год в России отмечали 1 сентября",
        "🎁 В Италии под Новый Год выбрасывают старые вещи из окон",
        "🍇 В Испании съедают 12 виноградин под бой курантов",
        "🐖 В Венгрии не едят птицу на Новый Год, чтобы 'счастье не улетело'",
        "🎣 В Японии перед Новым Годом дарят грабли, чтобы 'загребать счастье'"
    ]

    # Выбираем факт в зависимости от количества дней
    fact_index = days % len(facts)

    message = (
        f"📚 <b>Интересный факт о Новом Годе:</b>\n\n"
        f"{facts[fact_index]}\n\n"
        f"🎄 А до праздника осталось: <b>{days} дней</b>!"
    )

    await update.message.reply_html(message)


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /time - сколько осталось в часах"""
    days = days_until_new_year()
    total_hours = days * 24 + (24 - datetime.now().hour)
    total_minutes = total_hours * 60
    total_seconds = total_minutes * 60

    message = (
        f"🕐 <b>До Нового Года осталось:</b>\n\n"
        f"📅 <b>Дней:</b> {days}\n"
        f"⏱️ <b>Часов:</b> {total_hours:,}\n"
        f"⏰ <b>Минут:</b> {total_minutes:,}\n"
        f"⚡ <b>Секунд:</b> {total_seconds:,}\n\n"
        f"<i>Время летит быстро! ⏳</i>"
    )

    await update.message.reply_html(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - помощь"""
    message = (
        f"❓ <b>Помощь по командам:</b>\n\n"
        f"<b>/days</b> - Простое количество дней до НГ\n"
        f"<b>/countdown</b> - Детальный отсчет (дни, часы, минуты)\n"
        f"<b>/progress</b> - Прогресс года в процентах\n"
        f"<b>/facts</b> - Интересные факты о Новом Годе\n"
        f"<b>/time</b> - Сколько осталось в часах и минутах\n"
        f"<b>/help</b> - Это сообщение\n\n"
        f"<i>Бот обновляется автоматически! 🔄</i>"
    )

    await update.message.reply_html(message)


def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("days", days_command))
    application.add_handler(CommandHandler("countdown", countdown_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CommandHandler("facts", facts_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("help", help_command))

    print("=" * 60)
    print("🤖 БОТ 'ХЭППИ НЬЮ Э' ЗАПУЩЕН")
    print("📱 Команды: /start /days /countdown /progress /facts /time /help")
    print("=" * 60)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()