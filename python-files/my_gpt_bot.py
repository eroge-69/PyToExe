import os
import pandas as pd
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ✅ ВСТАВЬ СВОЙ ТОКЕН
TELEGRAM_TOKEN = "7945592810:AAHydUsDxW8tlwWchMqoM7Qo_YkKuB0NVCo"

# Основные клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    [["Загрузить ещё файл", "Сделать расчёт"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

new_calc_keyboard = ReplyKeyboardMarkup(
    [["Новый расчёт"]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

MAX_FILES = 10

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["uploaded_files"] = []
    await update.message.reply_text(
        "Привет! Пришли мне Excel-файл (.xls или .xlsx), и я сделаю сводную таблицу по оборудованию.",
        reply_markup=ReplyKeyboardRemove(),
    )

async def new_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["uploaded_files"] = []
    await update.message.reply_text(
        "Отлично! Начнём сначала.\nПришли мне Excel-файл (.xls или .xlsx), и я сделаю сводную таблицу по оборудованию.",
        reply_markup=ReplyKeyboardRemove(),
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    uploaded_files = context.user_data.get("uploaded_files", [])
    if len(uploaded_files) >= MAX_FILES:
        await update.message.reply_text(
            f"Ты уже загрузил {MAX_FILES} файлов. Давай сделаем расчёт!",
            reply_markup=ReplyKeyboardMarkup(
                [["Сделать расчёт"]],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        )
        return

    file = await document.get_file()
    file_path = f"temp_{len(uploaded_files)}_{document.file_name}"
    await file.download_to_drive(file_path)

    uploaded_files.append(file_path)
    context.user_data["uploaded_files"] = uploaded_files

    await update.message.reply_text(
        f"Файл сохранён.\nВсего файлов загружено: {len(uploaded_files)}.\n"
        "Ты можешь загрузить ещё или сразу сделать расчёт.",
        reply_markup=main_keyboard,
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uploaded_files = context.user_data.get("uploaded_files", [])

    if not uploaded_files:
        await update.message.reply_text(
            "Пока нет загруженных файлов. Пришли мне Excel-файл (.xls или .xlsx).",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    all_dfs = []

    try:
        for file_path in uploaded_files:
            raw_df = pd.read_excel(file_path, header=None)

            if raw_df.shape[0] >= 5:
                fifth_row = raw_df.iloc[4].astype(str)
                if fifth_row.str.contains(
                    "ВНИМАНИЕ! Данное КП составлено по спецификации",
                    case=False
                ).any():
                    header_row = 14
                    print("Обнаружена строка с предупреждением → заголовки в строке 15")
                else:
                    header_row = 13
                    print("Строка с предупреждением НЕ найдена → заголовки в строке 14")
            else:
                header_row = 13
                print("Файл слишком короткий → используем строку 14 как заголовок")

            df = pd.read_excel(file_path, header=header_row)
            df.columns = df.columns.str.strip()

            if 'Модель' not in df.columns or 'Кол-во' not in df.columns:
                await update.message.reply_text(
                    f"В файле {os.path.basename(file_path)} нет колонок 'Модель' или 'Кол-во'. "
                    f"Найдено: {df.columns.tolist()}",
                    reply_markup=new_calc_keyboard,
                )
                return

            df['Кол-во'] = pd.to_numeric(df['Кол-во'], errors='coerce')
            df['Кол-во'] = df['Кол-во'].fillna(0)

            all_dfs.append(df[['Модель', 'Кол-во']])

        combined_df = pd.concat(all_dfs, ignore_index=True)

        pivot_df = combined_df.groupby('Модель', as_index=False)['Кол-во'].sum()
        total = pivot_df['Кол-во'].sum()
        pivot_df.loc[len(pivot_df.index)] = ['Общий итог', total]

        output_filename = "Свод оборудования.xlsx"
        pivot_df.to_excel(output_filename, index=False)

        await update.message.reply_document(document=open(output_filename, 'rb'))

        await update.message.reply_text(
            "Расчёт завершён! Если хочешь начать новый расчёт, нажми кнопку ниже:",
            reply_markup=new_calc_keyboard,
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка при обработке файлов: {e}",
            reply_markup=new_calc_keyboard,
        )
    finally:
        for path in uploaded_files:
            if os.path.exists(path):
                os.remove(path)
        if os.path.exists("Свод оборудования.xlsx"):
            os.remove("Свод оборудования.xlsx")

        context.user_data["uploaded_files"] = []

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^Новый расчёт$"),
            new_calc
        )
    )
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("^Сделать расчёт$"),
            calculate
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Document.FileExtension("xls") | filters.Document.FileExtension("xlsx"),
            handle_document
        )
    )

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
