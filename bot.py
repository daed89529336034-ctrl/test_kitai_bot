import re
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8674405990:AAHSwIJnfswRZUoXNyXk2ngX59Vaj9PFH7M"

SPREADSHEET_ID = "1Xm94BJSO0Yr6vJBMUBGwtc_1MbKU7V23lliPEJQeIfU"
WORKSHEET_NAME = "2.2"

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SPREADSHEET_ID)

sheet = spreadsheet.worksheet(WORKSHEET_NAME)

TEMPLATE_TEXT = """Введите данные по шаблону:

Ш*В*Г кол Вес
Тираж Цена Образец

Пример:
200*100*50 99 10
1000 7,5 240
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEMPLATE_TEXT)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    lines = text.splitlines()

    if len(lines) != 2:
        await update.message.reply_text(TEMPLATE_TEXT)
        return

    first_line = lines[0].strip()
    second_line = lines[1].strip()

    # Только цифры и запятые
    # Точки запрещены

    match_first = re.match(
        r"^(\d+)\*(\d+)\*(\d+)\s+([\d,]+)\s+([\d,]+)$",
        first_line
    )

    match_second = re.match(
        r"^(\d+)\s+([\d,]+)\s+([\d,]+)$",
        second_line
    )

    if not match_first or not match_second:
        await update.message.reply_text(
            "Ошибка ❌\n\n"
            "Используй только запятую для дробей.\n\n"
            "Пример:\n"
            "10000 7,5 500"
        )
        return

    width, height, depth, qty_in_box, weight = match_first.groups()

    circulation, price, sample = match_second.groups()

    # Запись данных

    sheet.update(
        "D7:F7",
        [[circulation, price, sample]]
    )

    sheet.update(
        "B12:F12",
        [[width, height, depth, qty_in_box, weight]]
    )

    # Получение результатов

    result_L17 = sheet.acell("L17").value

    result_L22 = sheet.acell("L22").value

    # Ответ

    await update.message.reply_text(
        f"Готово ✅\n\n"
        f"Цена ВЭД: {result_L17}\n"
        f"Цена Карго: {result_L22}"
    )


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Бот запущен")

    app.run_polling()


if __name__ == "__main__":
    main()
