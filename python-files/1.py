import subprocess
import sys
import os
import logging
from datetime import datetime

# --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ: РЕДАКТИРОВАТЬ ТОЛЬКО ЭТОТ БЛОК! ---

# Путь к лог-файлу. Убедись, что папка C:\temp существует!
LOG_FILE_PATH = r"C:\temp\plugin_host_debug.log"

# Полный путь к твоему RunAsDate.exe
RUNASDATE_PATH = r"C:\путь\к\RunAsDate\RunAsDate.exe"

# Полный путь к НАСТОЯЩЕМУ, переименованному хосту плагинов
REAL_HOST_PATH = r"C:\Program Files\Bitwig Studio\bin\BitwigPluginHost-64_real.exe"

# Словарь: 'ключевое_слово_из_аргументов': 'дата_в_формате_ДД/ММ/ГГГГ'
# Ключевые слова не чувствительны к регистру (Serum и serum - одно и то же)
special_plugins = {
    'State Machine Faded Keys': '04/03/2024',
    'FabFilter': '01/09/2022',
    'Kontakt': '10/10/2020',
    # Добавляй сюда свои плагины по аналогии
}
# --- КОНЕЦ НАСТРОЕК ---


# Настройка системы логирования. Будет писать и в файл, и в консоль.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='a'),  # Запись в файл
        logging.StreamHandler(sys.stdout)  # Вывод в консоль
    ]
)

# --- ОСНОВНАЯ ЛОГИКА СКРИПТА ---

logging.info("================ ЗАПУСК СКРИПТА-ПЕРЕХВАТЧИКА ================")
try:
    # 1. Получаем и логируем аргументы от Bitwig
    arguments = sys.argv[1:]
    full_argument_string = " ".join(arguments)
    logging.info(f"Получены аргументы от Bitwig: {full_argument_string}")
    if not arguments:
        logging.warning("Скрипт запущен без аргументов. Вероятно, это тестовый запуск.")

    # 2. Ищем, есть ли в аргументах упоминание наших особых плагинов
    date_to_set = None
    detected_plugin = "N/A"
    for keyword, date in special_plugins.items():
        if keyword.lower() in full_argument_string.lower():
            date_to_set = date
            detected_plugin = keyword
            logging.info(f"Обнаружен плагин '{detected_plugin}'. Для него установлена особая дата: {date_to_set}")
            break  # Нашли совпадение, выходим из цикла

    if not date_to_set:
        logging.info("Особых плагинов не обнаружено. Хост будет запущен с системной датой.")

    # 3. Собираем финальную команду для запуска
    final_command = []
    if date_to_set:
        # Команда с подменой даты через RunAsDate
        final_command.extend([RUNASDATE_PATH, '/immediate', date_to_set, REAL_HOST_PATH])
        final_command.extend(arguments)
    else:
        # Обычная команда для прямого запуска
        final_command.append(REAL_HOST_PATH)
        final_command.extend(arguments)

    logging.info(f"Сформирована команда для выполнения: {' '.join(final_command)}")

    # 4. Выполняем команду
    logging.info("Передаю управление настоящему хосту...")
    process_result = subprocess.run(final_command, capture_output=True, text=True)

    # 5. Логируем результат выполнения
    logging.info(f"Настоящий хост завершил работу с кодом: {process_result.returncode}")
    if process_result.stdout:
        logging.info(f"Стандартный вывод хоста:\n{process_result.stdout}")
    if process_result.stderr:
        logging.warning(f"Ошибки от хоста:\n{process_result.stderr}")

except Exception as e:
    logging.exception("КРИТИЧЕСКАЯ ОШИБКА! В работе скрипта-перехватчика произошел сбой:")

logging.info("================ ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА ================\n")