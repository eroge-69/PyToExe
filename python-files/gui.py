import subprocess
import sys
import json
import os

# Проверка и установка необходимых библиотек
def проверить_и_установить_библиотеки():
    необходимые_библиотеки = ['requests', 'loguru', 'tenacity', 'urllib3', 'certifi']
    отсутствующие_библиотеки = []

    for библиотека in необходимые_библиотеки:
        try:
            __import__(библиотека)
        except ImportError:
            отсутствующие_библиотеки.append(библиотека)

    if отсутствующие_библиотеки:
        print(f"Отсутствуют библиотеки: {', '.join(отсутствующие_библиотеки)}")
        print("Попытка установить отсутствующие библиотеки...")
        for библиотека in отсутствующие_библиотеки:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", библиотека])
                print(f"Успешно установлена библиотека {библиотека}")
            except subprocess.CalledProcessError:
                print(f"Не удалось установить {библиотека}. Установите вручную командой: 'pip install {библиотека}'")
                sys.exit(1)

# Проверка библиотек перед импортом
проверить_и_установить_библиотеки()

import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from loguru import logger
import time
import threading
from uuid import uuid4
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import SSLError, ConnectionError

class АвтоПлюсн:
    def __init__(self, токен: str, базовый_урл="https://api.lolz.live/"):
        self.токен = токен
        self.сессия = requests.session()
        self.базовый_урл = базовый_урл
        self.сессия.headers = {'Authorization': f'Bearer {self.токен}'}
        self.массив = [1]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((SSLError, ConnectionError)),
        before_sleep=lambda retry_state: logger.warning(
            f"Повторная попытка {retry_state.attempt_number} после ошибки: {retry_state.outcome.exception()}"
        )
    )
    def получить(self, урл, параметры={}):
        try:
            ответ = self.сессия.get(self.базовый_урл + урл, params=параметры)
            ответ.raise_for_status()
            return ответ.json()
        except (SSLError, ConnectionError) as ошибка:
            logger.error(f"Ошибка соединения при GET-запросе к {урл}: {ошибка}")
            raise
        except requests.exceptions.RequestException as ошибка:
            logger.error(f"Ошибка при GET-запросе к {урл}: {ошибка}")
            return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((SSLError, ConnectionError)),
        before_sleep=lambda retry_state: logger.warning(
            f"Повторная попытка {retry_state.attempt_number} после ошибки: {retry_state.outcome.exception()}"
        )
    )
    def отправить(self, урл, данные={}):
        try:
            ответ = self.сессия.post(self.базовый_урл + урл, data=данные)
            ответ.raise_for_status()
            return ответ.json()
        except (SSLError, ConnectionError) as ошибка:
            logger.error(f"Ошибка соединения при POST-запросе к {урл}: {ошибка}")
            raise
        except requests.exceptions.RequestException as ошибка:
            logger.error(f"Ошибка при POST-запросе к {урл}: {ошибка}")
            return None

    def ОтправитьСообщение(self, ид_темы: int, текст_сообщения: str):
        данные = {'thread_id': f"{ид_темы}", 'post_body': f"{текст_сообщения}"}
        return self.отправить(f"/posts", данные)

    def получить_автора(self, ид_темы: int):
        ответ = self.получить(f"/threads/{ид_темы}")
        if ответ is None:
            logger.error(f"Не удалось получить данные для темы {ид_темы}")
            return None

        try:
            if "thread" not in ответ:
                logger.warning(f"Тема {ид_темы} недоступна или удалена: {ответ}")
                return None
            return ответ["thread"]["creator_user_id"]
        except Exception as ошибка:
            logger.error(f"Ошибка при разборе JSON для темы {ид_темы}: {ошибка}")
            return None

class АвтоПлюснИнтерфейс:
    def __init__(self, корень):
        self.корень = корень
        self.корень.title("LZTrade")
        self.корень.geometry("730x650")
        self.работает = False
        self.поток = None
        self.файл_конфигурации = "config.json"

        # Настройка логгера для вывода в интерфейс
        logger.remove()
        logger.add(self.лог_в_интерфейс, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

        # Создание элементов интерфейса
        self.создать_интерфейс()

        # Загрузка конфигурации по умолчанию
        self.конфигурация_по_умолчанию = {
            "токенЛолз": "",
            "сообщение": "",
            "темы": [],
            "скрыть": True
        }
        self.загрузить_конфигурацию()

    def создать_интерфейс(self):
        # Токен
        ttk.Label(self.корень, text="Токен:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.поле_токена = ttk.Entry(self.корень, width=50)
        self.поле_токена.grid(row=0, column=1, padx=5, pady=5)
        self.кнопка_вставить_токен = ttk.Button(self.корень, text="Вставить", command=lambda: self.вставить_из_буфера(self.поле_токена))
        self.кнопка_вставить_токен.grid(row=0, column=2, padx=5, pady=5)

        # Сообщение
        ttk.Label(self.корень, text="Сообщение:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.поле_сообщения = ttk.Entry(self.корень, width=50)
        self.поле_сообщения.grid(row=1, column=1, padx=5, pady=5)
        self.кнопка_вставить_сообщение = ttk.Button(self.корень, text="Вставить", command=lambda: self.вставить_из_буфера(self.поле_сообщения))
        self.кнопка_вставить_сообщение.grid(row=1, column=2, padx=5, pady=5)

        # Темы
        ttk.Label(self.корень, text="Темы (через запятую):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.текст_тем = scrolledtext.ScrolledText(self.корень, width=50, height=5)
        self.текст_тем.grid(row=2, column=1, padx=5, pady=5)
        self.кнопка_вставить_темы = ttk.Button(self.корень, text="Вставить", command=lambda: self.вставить_из_буфера(self.текст_тем))
        self.кнопка_вставить_темы.grid(row=2, column=2, padx=5, pady=5)

        # Скрытие
        self.переменная_скрытия = tk.BooleanVar()
        ttk.Checkbutton(self.корень, text="Скрыть сообщение", variable=self.переменная_скрытия).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Кнопка сохранения конфигурации
        self.кнопка_сохранить = ttk.Button(self.корень, text="Сохранить конфигурацию", command=self.сохранить_конфигурацию)
        self.кнопка_сохранить.grid(row=4, column=2, padx=5, pady=5)

        # Кнопки управления
        self.кнопка_запуска = ttk.Button(self.корень, text="Запустить", command=self.запустить_бота)
        self.кнопка_запуска.grid(row=4, column=0, padx=5, pady=5)
        self.кнопка_остановки = ttk.Button(self.корень, text="Остановить", command=self.остановить_бота, state="disabled")
        self.кнопка_остановки.grid(row=4, column=1, padx=5, pady=5)

        # Логи
        ttk.Label(self.корень, text="Логи:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.текст_логов = scrolledtext.ScrolledText(self.корень, width=70, height=20, state="disabled")
        self.текст_логов.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

    def вставить_из_буфера(self, поле):
        try:
            текст_из_буфера = self.корень.clipboard_get()
            if isinstance(поле, ttk.Entry):
                поле.delete(0, tk.END)
                поле.insert(0, текст_из_буфера)
            elif isinstance(поле, scrolledtext.ScrolledText):
                поле.delete("1.0", tk.END)
                поле.insert("1.0", текст_из_буфера)
            logger.info("Текст успешно вставлен из буфера обмена")
        except tk.TclError:
            logger.error("Ошибка: Буфер обмена пуст или содержит неподдерживаемый формат")

    def лог_в_интерфейс(self, сообщение):
        self.текст_логов.config(state="normal")
        self.текст_логов.insert(tk.END, сообщение + "\n")
        self.текст_логов.see(tk.END)
        self.текст_логов.config(state="disabled")

    def сохранить_конфигурацию(self):
        конфигурация = self.получить_конфигурацию()
        if конфигурация is None:
            logger.error("Не удалось сохранить конфигурацию: некорректные данные")
            return

        try:
            with open(self.файл_конфигурации, 'w', encoding='utf-8') as файл:
                json.dump(конфигурация, файл, ensure_ascii=False, indent=4)
            logger.info(f"Конфигурация успешно сохранена в {self.файл_конфигурации}")
        except Exception as ошибка:
            logger.error(f"Ошибка при сохранении конфигурации: {ошибка}")

    def загрузить_конфигурацию(self):
        if os.path.exists(self.файл_конфигурации):
            try:
                with open(self.файл_конфигурации, 'r', encoding='utf-8') as файл:
                    конфигурация = json.load(файл)
                self.поле_токена.insert(0, конфигурация.get("токенЛолз", ""))
                self.поле_сообщения.insert(0, конфигурация.get("сообщение", ""))
                self.текст_тем.insert(tk.END, ",".join(map(str, конфигурация.get("темы", []))))
                self.переменная_скрытия.set(конфигурация.get("скрыть", True))
                logger.info(f"Конфигурация успешно загружена из {self.файл_конфигурации}")
                return
            except Exception as ошибка:
                logger.error(f"Ошибка при загрузке конфигурации: {ошибка}")

        # Если файл не существует или произошла ошибка, используем конфигурацию по умолчанию
        self.поле_токена.insert(0, self.конфигурация_по_умолчанию["токенЛолз"])
        self.поле_сообщения.insert(0, self.конфигурация_по_умолчанию["сообщение"])
        self.текст_тем.insert(tk.END, ",".join(map(str, self.конфигурация_по_умолчанию["темы"])))
        self.переменная_скрытия.set(self.конфигурация_по_умолчанию["скрыть"])
        logger.info("Загружена конфигурация по умолчанию")

    def получить_конфигурацию(self):
        строка_тем = self.текст_тем.get("1.0", tk.END).strip()
        try:
            темы = [int(т.strip()) for т in строка_тем.split(",") if т.strip()]
        except ValueError:
            logger.error("Ошибка: Темы должны быть числами, разделенными запятыми!")
            return None

        конфигурация = {
            "токенЛолз": self.поле_токена.get().strip(),
            "сообщение": self.поле_сообщения.get().strip(),
            "темы": темы,
            "скрыть": self.переменная_скрытия.get()
        }

        if not конфигурация["сообщение"]:
            logger.error("Ошибка: Сообщение не может быть пустым!")
            return None
        if not конфигурация["токенЛолз"]:
            logger.error("Ошибка: Токен не может быть пустым!")
            return None
        if not конфигурация["темы"]:
            logger.error("Ошибка: Список тем не может быть пустым!")
            return None

        return конфигурация

    def цикл_авто_плюсн(self, бот, конфигурация):
        for ид_темы in конфигурация["темы"]:
            if not self.работает:
                break
            if конфигурация["скрыть"]:
                time.sleep(1)
                ид_автора = бот.получить_автора(ид_темы)
                if ид_автора is None:
                    logger.warning(f"Пропускаем тему {ид_темы}, не удалось получить ид_автора.")
                    continue
                скрытое_сообщение = f"[USERIDS={ид_автора}] {str(конфигурация['сообщение'])} [/USERIDS]"
                time.sleep(6)
                logger.info(f"Вы написали в тему с ID: {ид_темы}")
                результат = бот.ОтправитьСообщение(ид_темы, скрытое_сообщение)
                if результат is None:
                    logger.warning(f"Не удалось отправить сообщение в тему {ид_темы}")
            else:
                time.sleep(2)
                logger.info(f"Вы написали в тему с ID: {ид_темы}")
                результат = бот.ОтправитьСообщение(ид_темы, конфигурация["сообщение"])
                if результат is None:
                    logger.warning(f"Не удалось отправить сообщение в тему {ид_темы}")

    def цикл_бота(self):
        while self.работает:
            конфигурация = self.получить_конфигурацию()
            if конфигурация is None:
                self.остановить_бота()
                return
            try:
                бот = АвтоПлюсн(конфигурация["токенЛолз"])
                self.цикл_авто_плюсн(бот, конфигурация)
            except Exception as ошибка:
                logger.error(f"Произошла ошибка: {ошибка}")
            if self.работает:
                logger.info("Ожидание 15 минут до следующего запуска...")
                for _ in range(900):
                    if not self.работает:
                        break
                    time.sleep(1)

    def запустить_бота(self):
        if not self.работает:
            self.работает = True
            self.кнопка_запуска.config(state="disabled")
            self.кнопка_остановки.config(state="normal")
            self.поток = threading.Thread(target=self.цикл_бота)
            self.поток.start()
            logger.info("Бот запущен!")

    def остановить_бота(self):
        if self.работает:
            self.работает = False
            self.кнопка_запуска.config(state="normal")
            self.кнопка_остановки.config(state="disabled")
            logger.info("Бот остановлен!")

if __name__ == "__main__":
    корень = tk.Tk()
    приложение = АвтоПлюснИнтерфейс(корень)
    корень.mainloop()