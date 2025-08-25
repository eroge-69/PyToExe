import asyncio
import logging
from dotenv import load_dotenv
import os
import openpyxl
from datetime import datetime
import re
import hashlib

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Constants
STATS_FILE = "stats.xlsx"

# States
class TestState(StatesGroup):
    selecting_category = State()
    answering_question = State()

# Helper function to sanitize and truncate callback data
def sanitize_callback_data(data, max_length=50):
    """Обрезает и очищает строку для callback_data, поддерживая кириллицу."""
    data = str(data).strip().replace('\n', ' ').replace('\r', '')
    # Оставляем буквы, цифры, кириллицу и безопасные символы
    data = re.sub(r'[^\w\s\-\.]', '', data, flags=re.UNICODE)
    # Если строка слишком длинная, добавляем хэш для уникальности
    if len(data.encode('utf-8')) > max_length:
        hash_suffix = hashlib.md5(data.encode('utf-8')).hexdigest()[:6]
        data = data[:max_length-7] + hash_suffix
    if not data:
        data = "unknown"
    logging.debug(f"Sanitized callback_data: '{data}'")
    return data

# Keyboard functions
def get_categories_keyboard(categories):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    seen_callbacks = set()
    for cat in categories:
        safe_cat = sanitize_callback_data(cat)
        callback = f"category_{safe_cat}"
        # Проверяем длину callback_data
        if len(callback.encode('utf-8')) > 64:
            safe_cat = safe_cat[:30] + hashlib.md5(safe_cat.encode('utf-8')).hexdigest()[:6]
            callback = f"category_{safe_cat}"
            logging.warning(f"Категория '{cat}' обрезана до '{safe_cat}' из-за превышения лимита callback_data")
        # Проверяем уникальность callback_data
        if callback in seen_callbacks:
            safe_cat = f"{safe_cat}_{len(seen_callbacks)}"
            callback = f"category_{safe_cat}"
            logging.warning(f"Дубликат callback_data для '{cat}', добавлен суффикс: '{safe_cat}'")
        seen_callbacks.add(callback)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=cat, callback_data=callback)])
    return keyboard

def get_answers_keyboard(answers, show_back=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    seen_callbacks = set()
    for ans in answers:
        safe_ans = sanitize_callback_data(ans)
        callback = f"answer_{safe_ans}"
        if len(callback.encode('utf-8')) > 64:
            safe_ans = safe_ans[:30] + hashlib.md5(safe_ans.encode('utf-8')).hexdigest()[:6]
            callback = f"answer_{safe_ans}"
            logging.warning(f"Ответ '{ans}' обрезан до '{safe_ans}' из-за превышения лимита callback_data")
        if callback in seen_callbacks:
            safe_ans = f"{safe_ans}_{len(seen_callbacks)}"
            callback = f"answer_{safe_ans}"
            logging.warning(f"Дубликат callback_data для ответа '{ans}', добавлен суффикс: '{safe_ans}'")
        seen_callbacks.add(callback)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=str(ans), callback_data=callback)])
    if show_back:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard.inline_keyboard)

# Services
def load_tests(file_path):
    try:
        wb = openpyxl.load_workbook(file_path, read_only=True)
        tests = {}
        for sheet_name in wb.sheetnames:
            safe_sheet_name = sanitize_callback_data(sheet_name)
            sheet = wb[sheet_name]
            questions = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0]:
                    continue
                question = str(row[0]).strip()
                answers = [str(cell).strip() for cell in row[1:5] if cell is not None and str(cell).strip()]
                correct = str(row[5]).strip() if len(row) > 5 and row[5] is not None else None
                if len(answers) != 4 or not correct:
                    logging.warning(f"Пропущена строка в листе {sheet_name}: {row} (ожидается 4 варианта ответа и правильный ответ)")
                    continue
                if correct not in answers:
                    logging.warning(f"Пропущена строка в листе {sheet_name}: правильный ответ '{correct}' не найден в вариантах {answers}")
                    continue
                questions.append({"question": question, "answers": answers, "correct": correct})
            if questions:
                tests[safe_sheet_name] = questions
            logging.info(f"Загружены вопросы для категории {sheet_name} (safe: {safe_sheet_name}): {len(questions)}")
        return tests
    except Exception as e:
        logging.error(f"Ошибка загрузки тестов: {e}")
        return {}

# Utils
def ensure_stats_file():
    try:
        wb = openpyxl.load_workbook(STATS_FILE)
    except FileNotFoundError:
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "Statistics"
        sheet.append(["User ID", "Category", "Correct", "Wrong", "Last Date"])
        wb.save(STATS_FILE)
    return wb

def save_statistics(user_id, category, correct=0, wrong=0):
    wb = ensure_stats_file()
    sheet = wb["Statistics"]

    found = False
    for row in sheet.iter_rows(min_row=2):
        if row[0].value == user_id and row[1].value == category:
            row[2].value = (row[2].value or 0) + correct
            row[3].value = (row[3].value or 0) + wrong
            row[4].value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            found = True
            break

    if not found:
        sheet.append([user_id, category, correct, wrong, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    try:
        wb.save(STATS_FILE)
        logging.info(f"Статистика сохранена для user_id={user_id}, category={category}, correct={correct}, wrong={wrong}")
    except Exception as e:
        logging.error(f"Ошибка сохранения статистики: {e}")

def get_statistics(user_id):
    wb = ensure_stats_file()
    sheet = wb["Statistics"]

    stats = {}
    overall_correct = 0
    overall_wrong = 0
    last_date = None

    for row in sheet.iter_rows(min_row=2):
        if row[0].value == user_id:
            cat = row[1].value
            correct = row[2].value or 0
            wrong = row[3].value or 0
            date = row[4].value
            stats[cat] = {"correct": correct, "wrong": wrong, "last_date": date}
            overall_correct += correct
            overall_wrong += wrong
            if date and (not last_date or date > last_date):
                last_date = date

    return {"categories": stats, "overall_correct": overall_correct, "overall_wrong": overall_wrong, "last_date": last_date or "N/A"}

# Router and handlers
router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    tests = load_tests("tests.xlsx")
    if not tests:
        await message.answer("Ошибка: не удалось загрузить тесты.")
        return

    categories = list(tests.keys())
    if not categories:
        await message.answer("Ошибка: категории не найдены. Проверьте файл tests.xlsx.")
        return

    keyboard = get_categories_keyboard(categories)
    await message.answer("Добро пожаловать в бот для подготовки к олимпиаде по китайскому языку! Выберите категорию вопросов: ", reply_markup=keyboard)
    await state.set_state(TestState.selecting_category)

@router.message(Command("stats"))
async def stats_handler(message: Message):
    user_id = message.from_user.id
    stats = get_statistics(user_id)
    stats_text = "Статистика:\nОбщий: Правильных: {overall_correct}\nНеправильных: {overall_wrong}\nДата последнего: {last_date}".format(**stats)
    if stats["categories"]:
        stats_text += "\n\nПо категориям:"
        for cat, cat_stats in stats["categories"].items():
            progress = f"{cat_stats['correct']}/{cat_stats['correct'] + cat_stats['wrong']}"
            stats_text += f"\n{cat}: {progress}, последний: {cat_stats['last_date'] or 'N/A'}"
    else:
        stats_text += "\n\nВы ещё не проходили тесты."
    await message.answer(stats_text)

@router.callback_query(TestState.selecting_category, F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("category_", "")
    tests = load_tests("tests.xlsx")
    questions = tests.get(category, [])

    if not questions:
        await callback.message.answer(f"Ошибка: категория '{category}' не найдена.")
        return

    await state.update_data(category=category, questions=questions, current_index=0, answers=[])
    await send_question(callback.message, state)
    await callback.answer()

async def send_question(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]

    if index >= len(questions):
        await finish_test(message, state)
        return

    question = questions[index]
    text = question["question"]
    answers = question["answers"]
    keyboard = get_answers_keyboard(answers, index > 0)
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(TestState.answering_question)

@router.callback_query(TestState.answering_question, F.data.startswith("answer_"))
async def answer_selected(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    index = data["current_index"]
    answers = data.get("answers", [])
    category = data["category"]
    user_id = callback.from_user.id

    selected = callback.data.replace("answer_", "")
    question = questions[index]
    correct = question["correct"]
    is_correct = selected == correct

    # Сохраняем статистику после каждого ответа
    save_statistics(user_id, category, 1 if is_correct else 0, 0 if is_correct else 1)

    indicator = "✅ Правильно!" if is_correct else f"❌ Неправильно. Правильный ответ: {correct}"

    current_text = callback.message.text
    new_text = f"{current_text}\n\nВаш ответ: {selected}\n{indicator}"

    await callback.message.edit_text(new_text, reply_markup=None)

    answers.append(is_correct)
    await state.update_data(answers=answers, current_index=index + 1)
    await send_question(callback.message, state)
    await callback.answer()

@router.callback_query(TestState.answering_question, F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    index = data["current_index"]
    answers = data.get("answers", [])
    category = data["category"]
    user_id = callback.from_user.id

    if index > 0 and answers:
        # Удаляем последний ответ из статистики
        last_answer_correct = answers.pop()
        save_statistics(user_id, category, -1 if last_answer_correct else 0, 0 if last_answer_correct else -1)
        await state.update_data(answers=answers, current_index=index - 1)
        await callback.message.edit_reply_markup(reply_markup=None)
        await send_question(callback.message, state)
    await callback.answer()

async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data["answers"]
    total = len(answers)
    correct = sum(answers)

    percentage = (correct / total * 100) if total > 0 else 0
    if percentage > 80:
        result_text = f"Отличный результат! {correct}/{total} правильных ответов."
    elif percentage > 50:
        result_text = f"Неплохо! {correct}/{total} правильных ответов. Можно лучше."
    else:
        result_text = f"Не расстраивайся! {correct}/{total} правильных ответов. Попробуй еще раз."

    await message.answer(result_text)
    await state.clear()

# Main

TOKEN = '7868596253:AAEOa23u2rALO972z-DX0P8RDfjVBGAGgfU'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())