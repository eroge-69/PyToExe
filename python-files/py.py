import asyncio
import logging
import re
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import aiofiles
import aiohttp
import chardet
from HdRezkaApi import HdRezkaSession
from tqdm import tqdm
from tqdm.asyncio import tqdm as asyncio_tqdm

# ========================================
# ДАННЫЕ ДЛЯ ВХОДА В АККАУНТ
# ========================================
class Credentials:
    EMAIL: str = "gazanovik@gmail.com"
    PASSWORD: str = "7162654909"

# ========================================
# КОНФИГУРАЦИЯ ЗАГРУЗЧИКА
# ========================================
class Config:
    BASE_URL: str = "https://standby-rezka.tv/"
    MAX_CONCURRENT_DOWNLOADS: int = 10
    DOWNLOAD_MAX_RETRIES: int = 3
    CHUNK_SIZE: int = 32768  # Увеличен размер чанка для лучшей производительности
    REQUEST_TIMEOUT: int = 120
    DOWNLOAD_FOLDER: str = "Rezka_Downloads"
    
    # Настройки для фазы сбора ссылок
    API_REQUEST_DELAY: float = 0.2  # Уменьшена задержка
    API_MAX_RETRIES: int = 3
    API_RETRY_DELAY: float = 1.0
    
    # Новые настройки
    PROGRESS_UPDATE_INTERVAL: int = 1024

CONFIG = Config()
CREDENTIALS = Credentials()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hdrezka_downloader.log", "w", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================================
# УТИЛИТЫ
# ========================================
def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов."""
    sanitized = re.sub(r'[\\/*?:"<>|]', ' ', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:200] if len(sanitized) > 200 else sanitized

def format_size(size_bytes: int) -> str:
    """Форматирует размер в читаемом виде."""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def format_speed(bytes_per_second: float) -> str:
    """Форматирует скорость загрузки."""
    return f"{format_size(int(bytes_per_second))}/s"

def select_from_list(items: List[str], title: str) -> Optional[int]:
    """Интерактивный выбор из списка."""
    if not items:
        print("Нет доступных вариантов.")
        return None
    
    print(f"\n{'='*20} {title.upper()} {'='*20}")
    for i, item in enumerate(items, 1):
        print(f"{i:2d}: {item}")
    print("=" * (42 + len(title)))
    
    while True:
        try:
            choice = input(f"Выберите номер (1-{len(items)}) или 'q' для выхода: ").strip().lower()
            if choice == 'q':
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(items):
                return choice_num - 1
            
            print(f"❌ Неверный номер. Введите число от 1 до {len(items)}.")
        except ValueError:
            print("❌ Пожалуйста, введите корректное число.")
        except KeyboardInterrupt:
            print("\n👋 Выход.")
            return None

# ========================================
# АСИНХРОННЫЙ КЛАСС ЗАГРУЗЧИКА
# ========================================
class Downloader:
    def __init__(self, config: Config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_DOWNLOADS)

    async def __aenter__(self):
        # Улучшенная конфигурация коннектора
        connector = aiohttp.TCPConnector(
            limit=self.config.MAX_CONCURRENT_DOWNLOADS + 5,
            limit_per_host=self.config.MAX_CONCURRENT_DOWNLOADS,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=self.config.REQUEST_TIMEOUT,
            connect=30,
            sock_read=30
        )
        
        # Улучшенные заголовки
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers,
            trust_env=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            # Даем время на закрытие соединений
            await asyncio.sleep(0.1)

    async def get_file_size(self, url: str) -> int:
        """Получает размер файла без загрузки."""
        try:
            async with self.session.head(url) as response:
                return int(response.headers.get('content-length', 0))
        except Exception as e:
            logger.warning(f"Не удалось получить размер файла: {e}")
            return 0

    async def download_file(self, url: str, filepath: Path, description: str) -> Tuple[bool, int]:
        """Загружает файл с улучшенным прогрессом и обработкой ошибок."""
        async with self.semaphore:
            # Проверяем, существует ли файл и не является ли он временным
            if filepath.exists() and not filepath.name.endswith('.part'):
                file_size = filepath.stat().st_size
                # Проверяем размер файла на сервере
                expected_size = await self.get_file_size(url)
                if expected_size == 0 or file_size == expected_size:
                    logger.info(f"✅ Файл '{filepath.name}' уже существует, пропускаем.")
                    return True, file_size

            # Создаем директории
            filepath.parent.mkdir(parents=True, exist_ok=True)
            temp_filepath = filepath.with_suffix('.part')

            for attempt in range(self.config.DOWNLOAD_MAX_RETRIES):
                try:
                    start_time = time.time()
                    downloaded = 0

                    async with self.session.get(url) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get('content-length', 0))
                        
                        # Создаем прогресс-бар с улучшенным форматом
                        progress_bar = asyncio_tqdm(
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            desc=f"📥 {description:<20}",
                            leave=False,
                            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}] [{elapsed}<{remaining}]',
                            miniters=1
                        )

                        async with aiofiles.open(temp_filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(self.config.CHUNK_SIZE):
                                await f.write(chunk)
                                downloaded += len(chunk)
                                progress_bar.update(len(chunk))

                        progress_bar.close()
                        
                        # Переименовываем временный файл
                        if temp_filepath.exists():
                            temp_filepath.rename(filepath)
                        
                        elapsed_time = time.time() - start_time
                        speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                        logger.info(f"✅ Загружен {description} ({format_size(downloaded)} за {elapsed_time:.1f}с, {format_speed(speed)})")
                        
                        return True, downloaded

                except asyncio.TimeoutError:
                    logger.warning(f"⚠️ Таймаут при загрузке {description} (попытка {attempt + 1})")
                except aiohttp.ClientError as e:
                    logger.warning(f"⚠️ Сетевая ошибка при загрузке {description} (попытка {attempt + 1}): {e}")
                except Exception as e:
                    logger.warning(f"⚠️ Неожиданная ошибка при загрузке {description} (попытка {attempt + 1}): {e}")
                
                # Удаляем поврежденный файл
                if temp_filepath.exists():
                    try:
                        temp_filepath.unlink()
                    except OSError:
                        pass
                
                # Экспоненциальная задержка между попытками
                if attempt < self.config.DOWNLOAD_MAX_RETRIES - 1:
                    delay = min(2 ** attempt, 30)  # Максимум 30 секунд
                    logger.info(f"🔄 Повторная попытка через {delay} сек...")
                    await asyncio.sleep(delay)

            logger.error(f"❌ Не удалось скачать {description} после {self.config.DOWNLOAD_MAX_RETRIES} попыток.")
            return False, 0

# ========================================
# ОСНОВНЫЕ ФУНКЦИИ
# ========================================

async def run_async_downloads(download_tasks: List[Dict[str, Any]]):
    """Фаза 2: Асинхронно скачивает файлы по уже готовым ссылкам."""
    if not download_tasks:
        print("❌ Нет задач для загрузки.")
        return

    start_time = time.time()
    
    print(f"\n🚀 Начинаем загрузку {len(download_tasks)} файлов...")
    print(f"📊 Максимум одновременных загрузок: {CONFIG.MAX_CONCURRENT_DOWNLOADS}")
    
    try:
        async with Downloader(CONFIG) as downloader:
            # Создаем задачи для загрузки
            tasks_to_run = [
                downloader.download_file(task['url'], task['filepath'], task['description'])
                for task in download_tasks
            ]
            
            # Запускаем все задачи параллельно
            results = await asyncio.gather(*tasks_to_run, return_exceptions=True)

        # Обрабатываем результаты
        successful_downloads = 0
        failed_downloads = 0
        total_downloaded_size = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Исключение при загрузке {download_tasks[i]['description']}: {result}")
                failed_downloads += 1
            elif result[0]:  # Успешная загрузка
                successful_downloads += 1
                total_downloaded_size += result[1]
            else:
                failed_downloads += 1

        elapsed_time = time.time() - start_time
        avg_speed = total_downloaded_size / elapsed_time if elapsed_time > 0 else 0

        # Статистика
        print("\n" + "="*60)
        print("🎉 ЗАГРУЗКА ЗАВЕРШЕНА 🎉")
        print(f"✅ Успешно скачано: {successful_downloads} из {len(download_tasks)}")
        if failed_downloads > 0:
            print(f"❌ Ошибок при скачивании: {failed_downloads}")
        print(f"💾 Общий размер: {format_size(total_downloaded_size)}")
        print(f"⚡ Средняя скорость: {format_speed(avg_speed)}")
        print(f"⏱️ Затраченное время: {elapsed_time:.2f} сек.")
        print(f"📁 Файлы сохранены в: {Path(CONFIG.DOWNLOAD_FOLDER).resolve()}")
        print("="*60)

    except Exception as e:
        logger.error(f"❌ Критическая ошибка во время загрузки: {e}")
        raise

def prepare_download_links(rezka: Any, initial_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фаза 1: Последовательно получает ссылки на видео с повторными попытками."""
    if not initial_tasks:
        return []

    ready_tasks = []
    failed_count = 0
    
    print(f"\n🔗 Фаза 1: Получаем ссылки на {len(initial_tasks)} эпизодов...")
    
    with tqdm(initial_tasks, desc="Сбор ссылок", unit="эп") as pbar:
        for task in pbar:
            stream = None
            success = False
            
            # Цикл повторных попыток для каждого эпизода
            for attempt in range(CONFIG.API_MAX_RETRIES):
                try:
                    # Обновляем описание прогресс-бара
                    pbar.set_postfix_str(f"{task['description']} (попытка {attempt + 1})")
                    
                    # Основной вызов API
                    stream = rezka.getStream(task['season'], task['episode'], task['translator_id'])
                    if stream and hasattr(stream, 'videos') and stream.videos:
                        success = True
                        break
                    else:
                        raise ValueError("Пустой поток или нет видео")
                        
                except Exception as e:
                    error_msg = f"Ошибка для {task['description']} (попытка {attempt + 1}/{CONFIG.API_MAX_RETRIES}): {str(e)[:100]}"
                    if attempt < CONFIG.API_MAX_RETRIES - 1:
                        pbar.write(f"⚠️ {error_msg}")
                        time.sleep(CONFIG.API_RETRY_DELAY * (attempt + 1))  # Увеличивающаяся задержка
                    else:
                        pbar.write(f"❌ {error_msg}")

            if not success or not stream:
                failed_count += 1
                continue

            try:
                # Получаем URL видео
                video_urls = None
                available_qualities = list(stream.videos.keys())
                
                # Пробуем запрошенное качество
                if task['quality'] in available_qualities:
                    video_urls = stream(task['quality'])
                
                # Если запрошенное качество недоступно, берем лучшее
                if not video_urls and available_qualities:
                    best_quality = available_qualities[-1]  # Последнее обычно лучшее
                    pbar.write(f"ℹ️ {task['description']}: качество '{task['quality']}' недоступно. Используем '{best_quality}'")
                    video_urls = stream(best_quality)
                    task['actual_quality'] = best_quality
                else:
                    task['actual_quality'] = task['quality']

                if video_urls and len(video_urls) > 0:
                    task['url'] = video_urls[0]
                    ready_tasks.append(task)
                else:
                    pbar.write(f"❌ {task['description']}: не найдено URL для видео")
                    failed_count += 1

            except Exception as e:
                pbar.write(f"❌ Ошибка при извлечении URL для {task['description']}: {e}")
                failed_count += 1

            # Пауза между запросами к разным эпизодам
            time.sleep(CONFIG.API_REQUEST_DELAY)

    print(f"✅ Успешно получено ссылок: {len(ready_tasks)} из {len(initial_tasks)}")
    if failed_count > 0:
        print(f"❌ Не удалось получить ссылки: {failed_count}")
    
    return ready_tasks

def fix_encoding_hook(response, *args, **kwargs):
    """Hook для requests, который исправляет некорректную кодировку ответа сервера."""
    try:
        content_type = response.headers.get('Content-Type', '')
        if 'text' in content_type or 'json' in content_type:
            if response.encoding is None or 'iso-8859-1' in response.encoding.lower():
                detection = chardet.detect(response.content[:1024])  # Анализируем только первые 1024 байта
                encoding = detection.get('encoding')
                if encoding and detection.get('confidence', 0) > 0.7:
                    response.encoding = encoding
    except Exception as e:
        logger.warning(f"Ошибка в хуке кодировки: {e}")
    
    return response

def validate_credentials() -> bool:
    """Проверяет наличие учетных данных."""
    if not CREDENTIALS.EMAIL or not CREDENTIALS.PASSWORD:
        print("❌ Не заданы учетные данные (EMAIL и PASSWORD).")
        return False
    return True

def main_sync():
    """Главная синхронная функция для подготовки и запуска скачивания."""
    print("🚀 Запуск скрипта для скачивания с HDRezka...")
    
    # Проверяем учетные данные
    if not validate_credentials():
        return

    try:
        with HdRezkaSession(origin=CONFIG.BASE_URL) as session:
            # Применяем хук для исправления кодировки
            if hasattr(session, '_session') and session._session:
                session._session.hooks['response'].append(fix_encoding_hook)
                logger.info("✅ Хук для исправления кодировки применен.")
            else:
                logger.warning("⚠️ Не удалось применить хук кодировки.")

            # Авторизация
            print(f"🔐 Вход в аккаунт {CREDENTIALS.EMAIL}...")
            try:
                login_success = session.login(CREDENTIALS.EMAIL, CREDENTIALS.PASSWORD)
                if not login_success:
                    print("⚠️ Не удалось войти в аккаунт. Продолжаем без авторизации.")
                else:
                    print("✅ Успешная авторизация!")
            except Exception as e:
                logger.warning(f"Ошибка авторизации: {e}")
                print("⚠️ Ошибка при входе. Продолжаем без авторизации.")

            # Поиск сериала
            while True:
                search_query = input("\n🔍 Введите название сериала для поиска: ").strip()
                if not search_query:
                    print("❌ Пустой запрос. Попробуйте еще раз.")
                    continue
                break

            print(f"🔍 Поиск '{search_query}'...")
            try:
                search_results = session.search(search_query)
            except Exception as e:
                logger.error(f"Ошибка поиска: {e}")
                print(f"❌ Ошибка при поиске: {e}")
                return

            if not search_results:
                print("❌ Поиск не дал результатов.")
                return

            # Выбор сериала
            result_titles = [f"{item['title']} ({item.get('year', 'N/A')})" for item in search_results]
            chosen_index = select_from_list(result_titles, "Результаты поиска")
            if chosen_index is None:
                return
            
            selected_series = search_results[chosen_index]
            print(f"\n🎬 Выбран сериал: {selected_series['title']}")

            # Получаем информацию о сериале
            try:
                rezka = session.get(selected_series['url'])
                if not rezka.ok:
                    print(f"❌ Ошибка при получении информации о сериале: {rezka.exception}")
                    return
            except Exception as e:
                logger.error(f"Ошибка получения информации: {e}")
                print(f"❌ Ошибка: {e}")
                return

            # Выбор озвучки
            if not hasattr(rezka, 'translators_names') or not rezka.translators_names:
                print("❌ Не найдено озвучек для этого сериала.")
                return

            translator_names = list(rezka.translators_names.keys())
            chosen_translator_index = select_from_list(translator_names, "Выберите озвучку")
            if chosen_translator_index is None:
                return

            translator_name = translator_names[chosen_translator_index]
            translator_id = str(rezka.translators_names[translator_name]['id'])

            # Определение доступных качеств
            print("🔍 Определяем доступные качества...")
            available_qualities = ['360p', '480p', '720p', '1080p', '1080p Ultra']  # По умолчанию
            
            try:
                # Пробуем получить реальный список качеств
                if hasattr(rezka, 'episodesInfo') and rezka.episodesInfo:
                    first_season = rezka.episodesInfo[0]
                    if first_season['episodes']:
                        first_episode = first_season['episodes'][0]
                        test_stream = rezka.getStream(first_season['season'], first_episode['episode'], translator_id)
                        if test_stream and hasattr(test_stream, 'videos'):
                            available_qualities = list(test_stream.videos.keys())
                            print(f"✅ Найдены качества: {', '.join(available_qualities)}")
            except Exception as e:
                logger.warning(f"Не удалось получить список качеств: {e}")
                print("⚠️ Используем стандартный список качеств.")

            # Выбор качества
            chosen_quality_index = select_from_list(available_qualities, "Выберите качество")
            if chosen_quality_index is None:
                return
            
            quality = available_qualities[chosen_quality_index]
            print(f"🎤 Озвучка: {translator_name} | 📺 Качество: {quality}")

            # Подготовка списка задач
            if not hasattr(rezka, 'episodesInfo') or not rezka.episodesInfo:
                print("❌ Не найдено информации об эпизодах.")
                return

            initial_tasks = []
            series_name = sanitize_filename(rezka.name) if hasattr(rezka, 'name') else "Unknown_Series"
            base_path = Path(CONFIG.DOWNLOAD_FOLDER) / series_name

            for season_info in rezka.episodesInfo:
                season_num = season_info['season']
                for episode_info in season_info['episodes']:
                    episode_num = episode_info['episode']
                    
                    # Проверяем, доступна ли выбранная озвучка для этого эпизода
                    if any(str(t['translator_id']) == translator_id for t in episode_info['translations']):
                        episode_name = f"S{season_num:02d}E{episode_num:02d}"
                        initial_tasks.append({
                            'season': season_num,
                            'episode': episode_num,
                            'translator_id': translator_id,
                            'quality': quality,
                            'description': episode_name,
                            'filepath': base_path / f"Сезон {season_num:02d}" / f"{episode_name}.mp4"
                        })

            if not initial_tasks:
                print("❌ Не найдено эпизодов с выбранной озвучкой.")
                return

            print(f"📊 Найдено эпизодов: {len(initial_tasks)}")

            # Запуск фазы 1: сбор ссылок
            ready_to_download_tasks = prepare_download_links(rezka, initial_tasks)

            if not ready_to_download_tasks:
                print("❌ Не удалось получить ни одной ссылки для скачивания.")
                return

            print(f"\n✅ Готово к загрузке: {len(ready_to_download_tasks)} из {len(initial_tasks)} эпизодов")
            
            # Подтверждение загрузки
            total_estimated_size = len(ready_to_download_tasks) * 500 * 1024 * 1024  # Примерно 500MB на эпизод
            print(f"📊 Примерный размер: ~{format_size(total_estimated_size)}")
            print(f"📁 Путь сохранения: {base_path}")
            
            confirm = input(f"\nНачать загрузку {len(ready_to_download_tasks)} эпизодов? (y/n): ").lower().strip()
            if confirm not in ['y', 'yes', 'да']:
                print("❌ Загрузка отменена.")
                return

            # Запуск фазы 2: скачивание
            print("\n" + "="*60)
            print("🚀 ФАЗА 2: ПАРАЛЛЕЛЬНОЕ СКАЧИВАНИЕ")
            print("="*60)
            
            asyncio.run(run_async_downloads(ready_to_download_tasks))

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        print(f"\n❌ Произошла критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    try:
        main_sync()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем.")
        logger.info("Программа прервана пользователем.")
    except Exception as e:
        logger.critical(f"Необработанная ошибка: {e}", exc_info=True)
        print(f"\n💥 Критическая ошибка: {e}")
        print("📋 Подробности в файле hdrezka_downloader.log")
    finally:
        print("🔚 Завершение работы программы.")

