import re
import random
import logging
import sys
import time
from colorama import init, Fore, Style

init()

# Настройка логирования
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Варианты для выбора с нужным соотношением
choice_weights = ['ТОТР'] * 35 + ['НЕТОТР'] * 65

# Ввод имени файла
input_filename = 'doc.txt'  # Замените на ваш файл

try:
    with open(input_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print("Файл не найден.")
    sys.exit(1)

pattern = re.compile(r'^\d+:\d+$')

for line in lines:
    line = line.strip()
    # Задержка между выводами (0.5-1 секунды)
    interval = random.uniform(0.5, 1)
    time.sleep(interval)

    if pattern.match(line):
        choice = random.choice(choice_weights)
        if choice == 'ТОТР':
            print(Fore.RED + 'ТОТР' + Style.RESET_ALL)
            logging.info('ТОТР')
        else:
            print(Fore.GREEN + 'НЕТОТР' + Style.RESET_ALL)
            logging.info('НЕТОТР')
    else:
        print(Fore.YELLOW + 'Ошибка формата: ' + line + Style.RESET_ALL)
        logging.info('Ошибка формата: ' + line)