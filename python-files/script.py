
import pytesseract
from PIL import Image, ImageEnhance, ImageOps, ImageGrab, ImageFilter
from pynput import mouse, keyboard
import time
import ctypes
import requests
import re
import json
import difflib
from Tray_Number import *

# ========== НАСТРОЙКИ ========== #
OUTPUT_FILE = "recognized_text.txt"
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSDATA_PATH = r'C:\Program Files\Tesseract-OCR\tessdata'

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ========== #
start_x, start_y = -1, -1
selection_active = False
hotkey_button = None
hotkey_set = False
rectangles = []

# ========== КОНФИГУРАЦИЯ TESSERACT ========== #
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ['TESSDATA_PREFIX'] = TESSDATA_PATH

ya_token = "y0__xD60ryEARjB3RMgtN3S9BLMC4mSdt7_c0ZB0RLgthYqUjG2BQ"

TELEGRAM_BOT_TOKEN = "7877141708:AAGeQxwaGQUxutUh3eUDtfXCSwQFbuDtPNk"  # Получить у @BotFather
TELEGRAM_CHAT_ID = "267363063"       # Узнать у @userinfobot

def send_to_telegram(message):
    """Отправляет сообщение в Telegram бота"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Преобразуем Unicode-escape в нормальный текст
    if isinstance(message, list):
        message = "\n".join(str(item) for item in message)
    elif isinstance(message, str) and "\\u" in message:
        message = message.encode('utf-8').decode('unicode-escape')

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Сообщение отправлено в Telegram")
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")

def preprocess_image(image):
    """Улучшение изображения для лучшего распознавания"""
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    image = image.point(lambda x: 0 if x < 140 else 255)
    return image


def clean_text(text):
    """Очистка распознанного текста"""
    cleaned = re.sub(r'[^а-яА-ЯёЁa-zA-Z0-9\s\.,!?()\-—:;]', '', text)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def calculate_spacing_threshold(lines):
    """Вычисляет динамический порог расстояния между строками"""
    if len(lines) < 2:
        return 20  # минимальный порог по умолчанию

    spacings = []
    for i in range(1, len(lines)):
        spacings.append(lines[i]['top'] - lines[i - 1]['top'])

    if not spacings:
        return 20

    avg_spacing = sum(spacings) / len(spacings)
    return max(20, avg_spacing * 0.8)  # 80% от среднего расстояния, но не менее 20


def dynamic_line_splitting(image, initial_threshold=50, min_threshold=5):
    """Динамически уменьшает порог расстояния между строками, пока не получим несколько строк"""
    for threshold in range(initial_threshold, min_threshold - 1, -5):
        data = pytesseract.image_to_data(image, lang='rus+eng', config='--psm 6', output_type=pytesseract.Output.DICT)

        lines = []
        current_line = []
        current_line_num = -1

        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text:
                continue

            line_num = data['line_num'][i]

            if line_num != current_line_num:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [text]
                current_line_num = line_num
            else:
                current_line.append(text)

        if current_line:
            lines.append(' '.join(current_line))

        if len(lines) > 1:
            return lines

    return [" ".join(line['text'] for line in data['text'] if line['text'].strip())]


def split_text_into_blocks(image):
    """Разбивает текст на блоки - группирует слова в строки и сохраняет порядок чтения"""
    data = pytesseract.image_to_data(image, lang='rus+eng', config='--psm 6', output_type=pytesseract.Output.DICT)
    
    # Собираем все элементы с текстом
    elements = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text:
            elements.append({
                'text': text,
                'left': data['left'][i],
                'top': data['top'][i],
                'height': data['height'][i]
            })
    
    if not elements:
        return []
    
    # Группируем элементы по строкам (по Y-координате)
    lines_dict = {}
    
    for elem in elements:
        # Находим существующую строку с близкой Y-координатой
        found_line_key = None
        for line_key in lines_dict.keys():
            if abs(elem['top'] - line_key) <= elem['height'] * 0.6:  # 60% высоты как порог
                found_line_key = line_key
                break
        
        if found_line_key is not None:
            lines_dict[found_line_key].append(elem)
        else:
            lines_dict[elem['top']] = [elem]
    
    # Сортируем строки по Y-координате (сверху вниз)
    sorted_lines = sorted(lines_dict.items(), key=lambda x: x[0])
    
    # Для каждой строки сортируем слова по X-координате (слева направо)
    blocks = []
    for line_top, line_elements in sorted_lines:
        # Сортируем слова в строке по X-координате
        line_elements.sort(key=lambda x: x['left'])
        # Объединяем слова в строку
        line_text = " ".join([elem['text'] for elem in line_elements])
        blocks.append(line_text)
    
    return blocks

def recognize_area(x1, y1, x2, y2):
    try:
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        processed_img = preprocess_image(screenshot)
        processed_img.save("last_processed.png")

        blocks = split_text_into_blocks(processed_img)

        # Загружаем JSON с вопросами и ответами
        try:
            with open('questions_answers.json', 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке questions.json: {e}")
            questions_data = []

        matches = match_answers_to_blocks(blocks, questions_data)

        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(f"Область: {x1},{y1}-{x2},{y2}\n")
            f.write("Распознанный текст:\n")
            for block in blocks:
                f.write(f"{block}\n")

            f.write("\nНайденные соответствия:\n")
            for res in matches:
                f.write(f"Вопрос: {res['question']}\n")
                if res['matched_answer_block_number']:
                    f.write(f" -> Ответ найден в строке №{res['matched_answer_block_number']}\n")
                else:
                    f.write(" -> Подходящий ответ не найден\n")

            f.write("\n")

        print("\nТекст успешно распознан и сохранен!")
        print("Распознанный текст:\n", "\n".join(blocks))
        for res in matches:
            print(f"Вопрос: {res['question']}")
            if res['matched_answer_block_number']:
                print("\n")
                print(f" -> Ответ найден в строке №{res['matched_answer_block_number']}")
            else:
                print("\n")
                print(" -> Подходящий ответ не найден")

        return blocks

    except Exception as e:
        print(f"Ошибка при распознавании: {str(e)}")
        return None

def on_click(x, y, button, pressed):
    """Обработчик кликов мыши"""
    global start_x, start_y, selection_active, hotkey_button, hotkey_set

    if not hotkey_set:
        # Режим назначения горячей кнопки
        if pressed:
            hotkey_button = button
            hotkey_set = True
            print(f"\nГорячая кнопка назначена: {button}")
            print("Теперь нажмите эту кнопку мыши, чтобы начать выделение области")
        return

    if button == hotkey_button and pressed and not selection_active:
        # Активация режима выделения
        selection_active = True
        start_x, start_y = -1, -1
        print("\nРежим выделения активирован! Нажмите первую точку области...")
        return

    if selection_active and pressed:
        if start_x == -1:  # Первая точка
            start_x, start_y = x, y
            print(f"\nПервая точка установлена: ({x}, {y})")
            print("Нажмите вторую точку области...")
        else:  # Вторая точка
            end_x, end_y = x, y
            selection_active = False
            print(f"Конечная точка: ({end_x}, {end_y})")

            x1, x2 = sorted([start_x, end_x])
            y1, y2 = sorted([start_y, end_y])

            recognized_text = recognize_area(x1, y1, x2, y2)

            if recognized_text:
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                    f.write(f"Область: [{x1},{y1}]-[{x2},{y2}]\n")
                    f.write("\n".join(recognized_text) + "\n\n")

                print("\nТекст успешно распознан и сохранен!")
                print(f"Координаты области: [{x1},{y1}]-[{x2},{y2}]")
                print("Распознанный текст:\n", " ".join(recognized_text)[:200] + "...")

            start_x, start_y = -1, -1  # Сброс для следующего выделения


def on_key_press(key):
    """Обработчик нажатия клавиш (только для выхода)"""
    try:
        if key == keyboard.Key.esc:
            print("\nПрограмма завершена")
            return False  # Остановить listener
    except AttributeError:
        pass


def main():
    print("=== Программа для распознавания русского текста ===")
    print("\nИнструкция:")
    print("1. Сначала назначьте горячую кнопку мыши (нажмите любую кнопку мыши)")
    print("2. Затем используйте эту кнопку для активации режима выделения")
    print("3. В режиме выделения:")
    print("   - Первый клик мыши - начальная точка области")
    print("   - Второй клик мыши - конечная точка области")
    print("4. Нажмите ESC для выхода\n")

    # Проверяем доступность Tesseract
    try:
        langs = pytesseract.get_languages(config='')
        print("Доступные языки в Tesseract:", langs)
        if 'rus' not in langs:
            print("Ошибка: русский язык не найден в Tesseract!")
            return
    except Exception as e:
        print(f"Ошибка при проверке Tesseract: {str(e)}")
        return

    # Назначение горячей кнопки
    print("\nНажмите ЛЮБУЮ кнопку мыши для назначения горячей кнопки...")
    print("(Левая, правая, средняя или боковые кнопки)")

    # Запускаем обработчики
    with keyboard.Listener(on_press=on_key_press) as k_listener:
        with mouse.Listener(on_click=on_click) as m_listener:
            k_listener.join()
            m_listener.join()

def toggle_capslock():
    """Эмулирует нажатие CapsLock"""
    ctypes.windll.user32.keybd_event(0x14, 0x45, 0x1, 0)  # Нажатие
    ctypes.windll.user32.keybd_event(0x14, 0x45, 0x3, 0)  # Отпускание

def blink_capslock(times):
    """Мигает CapsLock указанное количество раз"""
    for _ in range(times):
        toggle_capslock()
        time.sleep(0.5)  # Полсекунды включен
        toggle_capslock()
        time.sleep(0.5)  # Полсекунды выключен


def match_answers_to_blocks(blocks, questions_answers):
    """
    Проходит по блокам и ищет вопрос и наиболее подходящий ответ ниже по списку.
    Сначала проверяем явную нумерацию в первых строках, затем нумеруем остальные относительно них.
    """
    matched_results = []

    for i, block in enumerate(blocks):
        question_candidates = find_answer(block, questions_answers)

        if question_candidates and question_candidates != ["Ответ не найден"]:
            answer_blocks = blocks[i + 1:]  # Все блоки после вопроса

            # 1. Собираем явно пронумерованные строки (первые 3 символа содержат цифру 1-6)
            numbered_lines = []
            for j, ablock in enumerate(answer_blocks):
                ablock_clean = ablock.strip('{}').strip()
                # Ищем цифру 1-6 в начале строки (форматы: 1, 1., 1), 1 и т.д.)
                match = re.match(r'^\s*([1-6])[\.\)\s]*', ablock_clean)
                if match:
                    number = int(match.group(1))
                    numbered_lines.append({
                        'number': number,
                        'text': ablock_clean,
                        'position': j + 1  # Позиция в блоке (+1 для нумерации с 1)
                    })

            # Если есть хотя бы одна явно пронумерованная строка
            if numbered_lines:
                # Сортируем по номеру
                numbered_lines.sort(key=lambda x: x['number'])

                # Находим минимальный номер
                min_number = min(nl['number'] for nl in numbered_lines)

                # Создаем маппинг позиций на номера
                position_to_number = {}
                last_number = None

                # Сначала заполняем явно пронумерованные
                for nl in numbered_lines:
                    position_to_number[nl['position']] = nl['number']

                # Затем нумеруем остальные строки относительно пронумерованных
                for j in range(1, len(answer_blocks) + 1):
                    if j not in position_to_number:
                        # Ищем ближайшую пронумерованную строку выше
                        closest_num = None
                        for pos, num in sorted(position_to_number.items()):
                            if pos < j:
                                closest_num = num + (j - pos)

                        # Или ниже, если выше нет
                        if closest_num is None:
                            for pos, num in sorted(position_to_number.items()):
                                if pos > j:
                                    closest_num = num - (pos - j)
                                    break

                        if closest_num is not None:
                            position_to_number[j] = closest_num

                # Теперь ищем лучший ответ с учетом новой нумерации
                best_score = 0.0
                best_number = None
                best_answer = None

                for j, ablock in enumerate(answer_blocks):
                    ablock_clean = ablock.strip('{}').strip()
                    current_number = position_to_number.get(j + 1, j + 1)

                    for correct_answer in question_candidates:
                        score = difflib.SequenceMatcher(
                            None,
                            ablock_clean.lower(),
                            correct_answer.lower()
                        ).ratio()

                        if score > best_score:
                            best_score = score
                            best_number = current_number
                            best_answer = correct_answer

                if best_number is not None:
                    print(f"\n🔔 Мигаем CapsLock {best_number} раз(а)...")
                    blink_capslock(best_number)

                    matched_results.append({
                        'question': block,
                        'matched_answer': best_answer,
                        'matched_answer_block_number': best_number
                    })
                    continue

            # 2. Если явной нумерации нет, используем стандартный алгоритм
            best_score = 0.0
            best_index = -1
            best_answer = None

            for j, ablock in enumerate(answer_blocks):
                ablock_clean = ablock.strip('{}').lower()
                for correct_answer in question_candidates:
                    score = difflib.SequenceMatcher(None, ablock_clean, correct_answer.lower()).ratio()
                    if score > best_score:
                        best_score = score
                        best_index = j + 1  # Нумерация с 1
                        best_answer = correct_answer

            if best_index > 0:
                print(f"\n🔔 Мигаем CapsLock {best_index} раз(а)...")
                blink_capslock(best_index)

            matched_results.append({
                'question': block,
                'matched_answer': best_answer,
                'matched_answer_block_number': best_index if best_index > 0 else None
            })

    return matched_results

# Функция поиска ответа с учетом возможных неточностей
def find_answer(question, questions_answers):
    question = question.lower().replace('\n', ' ')
    print(f"\n🔍 Ищем: {question}")
    score_return = 0.00
    qustion_return = ""
    answer_return = ""

    for section in questions_answers:
        for q in section['questions']:
            q_text = q['question'].lower().replace('\n', ' ')
            score = difflib.SequenceMatcher(None, question, q_text).ratio()

            if score > 0.70:
                if score > score_return:
                    score_return = score
                    qustion_return = q['question']
                    answer_return = q['answers']
        if score_return > 0:
            print(f"✅ Найден вопрос: {qustion_return} (похожесть {score_return:.2f})")
            send_to_telegram(answer_return)
            return answer_return
    print("❌ Ничего не найдено")
    return ["Ответ не найден"]


if __name__ == "__main__":
    main()