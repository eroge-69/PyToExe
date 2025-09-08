import asyncio
import json
import re
import random
import os
from datetime import datetime
from typing import List, Set, Optional
from playwright.async_api import async_playwright
try:
    from playwright_stealth import Stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("[⚠] playwright-stealth не установлен. Работаем без stealth режима.")
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# Конфигурация
class Config:
    API_PATTERN = re.compile(r"/basketapi/api/v1/Basket/ctnList/")
    OUTPUT_FILE = "beeline_numbers.json"
    MAX_CYCLES = 6000
    URL_BASKET = "https://vladivostok.beeline.ru/basket/"
    NUM_CONTEXTS = 7
    CAPTCHA_TIMEOUT = 60
    PROXY_CREDENTIALS = {"username": "eD7spc", "password": "nRh1VM"}
    CHROME_VERSIONS = list(range(131, 140))
    
    # Селекторы
    CAPTCHA_SELECTORS = [
        "iframe[src*='captcha']",
        "iframe[src*='yandex']", 
        "[data-testid*='captcha']",
        ".captcha", 
        ".smart-captcha"
    ]
    
    BROWSER_ARGS = [
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins-discovery", 
        "--disable-default-apps",
        "--no-first-run",
        "--disable-dev-shm-usage",
        "--window-size=375,812",
        "--no-sandbox",
        "--disable-gpu"
    ]


class NumberStorage:
    def __init__(self):
        self.numbers: Set[str] = set()
        self._load_existing_numbers()
    
    def _load_existing_numbers(self):
        """Загружает существующие номера из файла"""
        if os.path.exists(Config.OUTPUT_FILE):
            try:
                with open(Config.OUTPUT_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.numbers.update(loaded)
                    print(f"[📂] Загружено {len(self.numbers)} номеров из {Config.OUTPUT_FILE}")
            except Exception as e:
                print(f"[⚠] Ошибка чтения JSON: {e}")
    
    def add_numbers(self, new_numbers: List[str]) -> List[str]:
        """Добавляет новые номера и возвращает только действительно новые"""
        truly_new = []
        for number in new_numbers:
            if number not in self.numbers:
                self.numbers.add(number)
                truly_new.append(number)
        return truly_new
    
    async def save_to_file(self):
        """Сохраняет номера в файл"""
        try:
            with open(Config.OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(list(self.numbers), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[❌] Ошибка сохранения: {e}")
    
    def __len__(self):
        return len(self.numbers)


class ProxyManager:
    def __init__(self, proxy_file: str = "proxies.txt"):
        self.proxies = self._load_proxies(proxy_file)
    
    def _load_proxies(self, file_path: str) -> List[str]:
        """Загружает список прокси из файла"""
        proxies = []
        if not os.path.exists(file_path):
            print(f"[⚠] Файл {file_path} не найден. Работаем без прокси.")
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    proxies.append(proxy)
        
        if not proxies:
            print("[⚠] Файл proxies.txt пуст! Работаем без прокси.")
        return proxies
    
    def get_random_proxy(self) -> Optional[str]:
        """Возвращает случайный прокси или None"""
        return random.choice(self.proxies) if self.proxies else None


class BeelineParser:
    def __init__(self, storage: NumberStorage, proxy_manager: ProxyManager):
        self.storage = storage
        self.proxy_manager = proxy_manager
        self.browser = None
        self.contexts = []
        self.playwright = None
    
    @staticmethod
    def format_phone_number(number: str) -> str:
        """Форматирует номер телефона"""
        digits = re.sub(r"\D", "", number)
        if digits.startswith("8"):
            digits = "7" + digits[1:]
        elif not digits.startswith("7"):
            digits = "7" + digits
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    
    @staticmethod
    def generate_user_agent(prev_version: Optional[int] = None) -> str:
        """Генерирует случайный User-Agent"""
        available_versions = [v for v in Config.CHROME_VERSIONS if v != prev_version]
        version = random.choice(available_versions)
        return f"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Mobile Safari/537.36"
    
    async def create_context(self):
        """Создает новый контекст с прокси и случайным User-Agent"""
        proxy = self.proxy_manager.get_random_proxy()
        user_agent = self.generate_user_agent()

        context_options = {
            "user_agent": user_agent,
            "viewport": {"width": 375, "height": 812},
            "is_mobile": True,
            "extra_http_headers": {
                "accept-language": "ru-RU,ru;q=0.9",
                "sec-ch-ua": f'"Chromium";v="{user_agent.split("Chrome/")[1].split(".")[0]}", "Not.A/Brand";v="99"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"'
            }
        }

        if proxy:
            context_options["proxy"] = {
                "server": proxy,
                **Config.PROXY_CREDENTIALS
            }

        context = await self.browser.new_context(**context_options)

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU','ru']});
        """)

        if STEALTH_AVAILABLE:
            try:
                stealth = Stealth()
                await stealth.apply_stealth_async(context)
            except Exception as e:
                print(f"[⚠] Ошибка применения stealth: {e}")

        return context, proxy, user_agent
    
    async def setup_browser(self):
        """Инициализирует браузер и контексты"""

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=Config.BROWSER_ARGS
        )
        
        # Создаем контексты для каждого "окна"
        for i in range(Config.NUM_CONTEXTS):
            context, proxy, user_agent = await self.create_context()
            
            self.contexts.append({
                "context": context,
                "context_id": i + 1,
                "proxy": proxy,
                "user_agent": user_agent
            })
            
            print(f"[📱][Контекст {i + 1}] Создан с User-Agent: {user_agent}")
            print(f"[🌐][Контекст {i + 1}] Прокси: {proxy if proxy else 'Отключен'}")
    
    async def check_for_captcha(self, page) -> bool:
        """Проверяет наличие капчи на странице"""
        for selector in Config.CAPTCHA_SELECTORS:
            if await page.query_selector(selector):
                return True
        return False
    
    async def wait_for_captcha_solution(self, page, context_id: int) -> bool:
        """Ждет решения капчи"""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < Config.CAPTCHA_TIMEOUT:
            try:
                if not await self.check_for_captcha(page):
                    return True
                if await page.query_selector("button[data-testid='changeNumber']"):
                    return True
            except Exception:
                pass
            #await asyncio.sleep(2)
        
        print(f"[❌][Контекст {context_id}] Таймаут ожидания решения капчи!")
        return False
        
    async def process_api_response(self, response, context_info: dict) -> None:
        """Обрабатывает ответ от API"""
        if not Config.API_PATTERN.search(response.url):
            return
        
        context = context_info["context"]
        context_id = context_info["context_id"]
        
        try:
            if response.status != 200:
                print(f"[⚠][Контекст {context_id}] HTTP {response.status}")

                await context.close()

                new_context, proxy, user_agent = await self.create_context()
                context_info.update({
                    "context": new_context,
                    "proxy": proxy,
                    "user_agent": user_agent
                })

                print(f"[🔄][Контекст {context_id}] Контекст перезапущен с новым User-Agent")
                return
            
            text = await response.text()
            if not text.strip():
                print(f"[⚠][Контекст {context_id}] Пустой ответ")
                await context.close()
                return
            
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                print(f"[⚠][Контекст {context_id}] JSON ошибка: {e}")
                await context.close()
                return
            
            # Извлекаем бесплатные номера
            new_numbers = []
            for category in data.get("numbers", []):
                if category.get("price") == 0:
                    for num in category.get("numbers", []):
                        if num.get("price") == 0:
                            value = num.get("value")
                            if value:
                                formatted_value = self.format_phone_number(value)
                                new_numbers.append(formatted_value)
            
            # Добавляем новые номера
            truly_new = self.storage.add_numbers(new_numbers)
            
            if truly_new:
                await self.storage.save_to_file()
                print(f"[💾][Контекст {context_id}] +{len(truly_new)} номеров. Всего: {len(self.storage)}")
        
        except Exception as e:
            print(f"[⚠][Контекст {context_id}] Ошибка обработки ответа: {e}")
    
    async def close_modal(self, page) -> None:
        """Закрывает модальное окно"""
        try:
            close_button = await page.wait_for_selector(
                "button[aria-label='Закрыть модальное окно']", 
                timeout=5000
            )
            if close_button:
                await close_button.click()
                await asyncio.sleep(1.6)
        except Exception:
            pass
    
    async def worker(self, context_info: dict) -> None:
        """Рабочий процесс для одного контекста"""
        context = context_info["context"]
        context_id = context_info["context_id"]
        
        page = await context.new_page()
        cycle_count = 0
        
        # Обработчик ответов
        async def handle_response(response):
            await self.process_api_response(response, context_info)
        
        page.on("response", handle_response)
        
        try:
            # Переходим на страницу
            await page.goto(Config.URL_BASKET, wait_until="networkidle")
            await asyncio.sleep(random.uniform(1, 2))
            
            # Проверяем капчу
            if await self.check_for_captcha(page):
                if not await self.wait_for_captcha_solution(page, context_id):
                    return
            
            # Главный цикл
            while cycle_count < Config.MAX_CYCLES:
                try:
                    change_button = await page.wait_for_selector(
                        "button[data-testid='changeNumber']", 
                        timeout=10000
                    )
                    
                    if change_button:
                        await asyncio.sleep(random.uniform(1, 2))
                        await change_button.click()
                        await asyncio.sleep(0.7)
                        
                        # Проверяем капчу после клика
                        if await self.check_for_captcha(page):
                            if not await self.wait_for_captcha_solution(page, context_id):
                                break
                        
                        # Закрываем модальное окно
                        await self.close_modal(page)
                        
                        cycle_count += 1
                    else:
                        print(f"[⚠][Контекст {context_id}] Кнопка смены номера не найдена")
                        break
                
                except Exception as e:
                    print(f"[⚠][Контекст {context_id}] Ошибка в цикле: {e}")
                    # Пытаемся перезагрузить страницу
                    try:
                        await page.reload(wait_until="networkidle")
                        await asyncio.sleep(2)
                    except Exception:
                        break
        
        except Exception as e:
            print(f"[❌][Контекст {context_id}] Критическая ошибка: {e}")
        
        finally:
            try:
                await page.close()
            except Exception:
                pass
            print(f"[🏁][Контекст {context_id}] Завершен.")
    
    async def run(self):
        """Запускает парсер"""
        await self.setup_browser()
        
        print(f"[▶] Запуск {Config.NUM_CONTEXTS} контекстов...")
        
        # Запускаем все контексты параллельно
        tasks = []
        for context_info in self.contexts:
            task = asyncio.create_task(self.worker(context_info))
            tasks.append(task)
            # Небольшая задержка между запусками
            await asyncio.sleep(0.7)
        
        # Ждем завершения всех задач
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"[🏁] Все контексты завершены. Итого номеров: {len(self.storage)}")
    
    async def cleanup(self):
        """Очистка ресурсов"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class BeelineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Beeline Parser")
        self.root.geometry("500x300")

        self.running = False
        self.thread = None

        # Статус
        self.status_label = ttk.Label(root, text="Ожидание запуска...")
        self.status_label.pack(pady=10)

        # Кнопки
        self.start_button = ttk.Button(root, text="▶ Запустить", command=self.start_parser)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="⏹ Остановить", command=self.stop_parser, state="disabled")
        self.stop_button.pack(pady=5)

        # Лог
        self.log_text = tk.Text(root, height=10, width=60, state="disabled")
        self.log_text.pack(pady=10)

    def log(self, msg: str):
        """Пишет в текстовое поле"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def start_parser(self):
        if self.running:
            return
        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.log("Стартуем парсер...")

        self.thread = threading.Thread(target=self._run_asyncio, daemon=True)
        self.thread.start()

    def stop_parser(self):
        if not self.running:
            return
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log("Остановка парсера...")

    def _run_asyncio(self):
        asyncio.run(self._async_main())

    async def _async_main(self):
        storage = NumberStorage()
        proxy_manager = ProxyManager()
        parser = BeelineParser(storage, proxy_manager)

        try:
            await parser.run()
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            await parser.cleanup()
            await storage.save_to_file()
            self.log(f"Финальное сохранение. Итого: {len(storage)} номеров")
            self.running = False
            self.root.after(0, self._on_finish)

    def _on_finish(self):
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log("Парсер завершён.")


if __name__ == "__main__":
    root = tk.Tk()
    app = BeelineApp(root)
    root.mainloop()
