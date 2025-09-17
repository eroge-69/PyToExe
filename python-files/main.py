#!/usr/bin/env python3
"""
Скрипт для Windows: периодически делает скриншоты и сохраняет их на сетевой шаре
(аналог вашего PowerShell-скрипта). Поддерживает мульти-монитор через mss,
уникальные имена файлов с миллисекундами, ретраи создания папки и ротацию файлов.

Зависимости:
    pip install mss pillow

Настройки в разделе CONFIG.

Запуск: запустите в интерактивной сессии пользователя (Task Scheduler с "Run only when user is logged on").
"""

import os
import sys
import time
import logging
import socket
import shutil
from pathlib import Path
from datetime import datetime, timedelta

try:
    import mss
    from PIL import Image
except Exception as e:
    print("Необходимые модули не найдены. Установите: pip install mss pillow")
    raise

# ==================== CONFIG ====================
NETWORK_SHARE_PATH = r"\\10.249.31.231\SecretNetUsers\test"  # UNC путь к сетевой папке
LOG_ROOT = r"\\10.249.31.231\SecretNetUsers\LOGS"            # UNC путь к папке логов
SCREENSHOT_INTERVAL_SECONDS = 4
JPEG_QUALITY = 15           # 0..100
USE_ALL_MONITORS = True     # True = захват всей виртуальной области (все мониторы)
FOLDER_CREATE_RETRIES = 3
FOLDER_CREATE_BACKOFF_SEC = 2
RETENTION_DAYS = 14         # 0 = отключить удаление старых
# =================================================

COMPUTER_NAME = socket.gethostname()

# Логирование
_current_log_date = None
logger = logging.getLogger("screenshot_capture")
logger.setLevel(logging.DEBUG)

# Helper: setup file logger per-day

def setup_logging():
    global _current_log_date
    today = datetime.now().strftime("%Y-%m-%d")
    if _current_log_date == today:
        return
    _current_log_date = today

    # Удаляем старые обработчики
    for h in list(logger.handlers):
        logger.removeHandler(h)
        h.close()

    log_folder = Path(LOG_ROOT) / COMPUTER_NAME / today
    try:
        log_folder.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        # Нельзя аварийно падать — логируем в консоль
        print(f"Ошибка создания папки логов '{log_folder}': {e}")

    log_file = log_folder / f"{COMPUTER_NAME}-{today}.txt"

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info(f"Логи: {log_file}")


def ensure_folder(path: Path) -> bool:
    attempt = 0
    while attempt < FOLDER_CREATE_RETRIES:
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Папка для скриншотов существует/создана: {path}")
            return True
        except Exception as e:
            attempt += 1
            logger.warning(f"Ошибка создания папки ({attempt}/{FOLDER_CREATE_RETRIES}): {e}")
            time.sleep(FOLDER_CREATE_BACKOFF_SEC * attempt)
    return False


def take_screenshot(file_path: Path):
    try:
        with mss.mss() as sct:
            # monitor 0 = виртуальный экран (все мониторы), 1..N = отдельные
            monitor = sct.monitors[0] if USE_ALL_MONITORS else sct.monitors[1]
            sct_img = sct.grab(monitor)

            # Конвертация в PIL Image
            img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
            # Сохраняем как JPEG с заданным качеством
            img.save(str(file_path), format='JPEG', quality=JPEG_QUALITY, optimize=True)
            logger.info(f"Скриншот сохранён: {file_path}")
    except Exception as e:
        logger.exception(f"Ошибка при создании скриншота: {e}")


def rotate_old_files(root_folder: Path):
    if RETENTION_DAYS <= 0:
        return
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    try:
        for p in root_folder.rglob('*.jpg'):
            try:
                if datetime.fromtimestamp(p.stat().st_mtime) < cutoff:
                    p.unlink()
                    logger.info(f"Удалён старый файл: {p}")
            except Exception as e:
                logger.warning(f"Не удалось удалить {p}: {e}")
    except Exception as e:
        logger.warning(f"Ошибка при ротации файлов: {e}")


def is_interactive_session() -> bool:
    # Простейшая эвристика: если нет окружения SESSIONNAME или оно = 'Services' => не интерактивно
    session = os.environ.get('SESSIONNAME', '')
    if session == '' or session.lower().startswith('services'):
        return False
    return True


def main_loop():
    setup_logging()

    if not is_interactive_session():
        logger.warning("Похоже, это не интерактивный сеанс. Захват экрана может не сработать.")

    while True:
        now = datetime.now()
        # Обновляем лог-файлы при переходе даты
        setup_logging()

        date_month = now.strftime('%m-%Y')
        date_day = now.strftime('%d-%m-%Y')

        folder_path = Path(NETWORK_SHARE_PATH) / date_month / COMPUTER_NAME / date_day

        ok = ensure_folder(folder_path)
        if ok:
            timestamp = now.strftime('%H-%M-%S-%f')[:-3]  # миллисекунды
            file_name = f"{timestamp}.jpg"
            file_path = folder_path / file_name

            take_screenshot(file_path)

            # Ротация (в той же ветке, можно поменять на общий путь)
            rotate_old_files(folder_path)
        else:
            logger.warning(f"Пропуск создания скриншота — папка недоступна: {folder_path}")

        time.sleep(max(0.1, SCREENSHOT_INTERVAL_SECONDS))


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info('Остановлено пользователем')
    except Exception:
        logger.exception('Необработанная ошибка, выхожу')
"