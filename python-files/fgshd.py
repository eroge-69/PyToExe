#!/usr/bin/env python3
import os
import sys
import shutil
import time
import argparse
from typing import Optional, List


class FolderHopper:
    def __init__(self, script_path: str, log_file: Optional[str] = None):
        self.script_path = os.path.abspath(script_path)
        self.script_name = os.path.basename(script_path)
        self.current_dir = os.path.dirname(self.script_path)
        self.log_file = log_file
        self.setup_logging()

    def setup_logging(self) -> None:
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

    def log(self, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"

        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(log_message)
        print(log_message, end='')

    def get_sibling_folders(self) -> Optional[List[str]]:
        """Возвращает список соседних папок или None если не удалось определить"""
        parent_dir = os.path.dirname(self.current_dir)
        if not parent_dir:  # Мы в корневой директории
            return None

        try:
            all_items = os.listdir(parent_dir)
            folders = [
                item for item in all_items
                if os.path.isdir(os.path.join(parent_dir, item))
                   and not item.startswith('.')  # Игнорируем скрытые папки
            ]
            folders.sort()  # Сортируем для предсказуемого порядка
            return folders
        except Exception as e:
            self.log(f"Ошибка при получении списка папок: {e}")
            return None

    def get_next_folder(self) -> Optional[str]:
        """Определяет следующую папку для перемещения"""
        folders = self.get_sibling_folders()
        if not folders:
            return None

        current_folder = os.path.basename(self.current_dir)
        try:
            current_index = folders.index(current_folder)
        except ValueError:
            self.log(f"Текущая папка {current_folder} не найдена в списке соседних папок")
            return None

        next_index = (current_index + 1) % len(folders)
        return os.path.join(os.path.dirname(self.current_dir), folders[next_index])

    def copy_script_to_folder(self, target_folder: str) -> bool:
        """Копирует скрипт в целевую папку"""
        target_path = os.path.join(target_folder, self.script_name)

        try:
            # Сначала копируем, потом удаляем оригинал для безопасности
            shutil.copy2(self.script_path, target_path)

            # Делаем скрипт исполняемым (для Unix-систем)
            os.chmod(target_path, 0o755)

            # Удаляем оригинал только после успешного копирования
            os.remove(self.script_path)

            self.log(f"Скрипт перемещён из {self.current_dir} в {target_folder}")
            return True
        except Exception as e:
            self.log(f"Ошибка при перемещении скрипта: {e}")
            return False

    def add_to_startup(self, target_folder: str) -> None:
        """Добавляет скрипт в автозагрузку (экспериментальная функция)"""
        # Реализация зависит от ОС
        if sys.platform == "win32":
            # Для Windows
            startup_folder = os.path.join(
                os.getenv("APPDATA"),
                "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
            )
            startup_script = os.path.join(startup_folder, self.script_name)

            if not os.path.exists(startup_script):
                try:
                    shutil.copy2(self.script_path, startup_script)
                    self.log(f"Добавлено в автозагрузку Windows: {startup_script}")
                except Exception as e:
                    self.log(f"Ошибка добавления в автозагрузку Windows: {e}")

        elif sys.platform == "linux" or sys.platform == "darwin":
            # Для Linux/Mac (нужны права sudo)
            cron_entry = f"@reboot python3 {os.path.join(target_folder, self.script_name)}"
            try:
                with open("/etc/crontab", "a") as f:
                    f.write(f"\n{cron_entry}\n")
                self.log("Добавлено в крон задачи")
            except Exception as e:
                self.log(f"Ошибка добавления в крон: {e}")

    def run(self, add_startup: bool = False) -> None:
        self.log(f"Запуск скрипта из {self.current_dir}")

        next_folder = self.get_next_folder()
        if not next_folder:
            self.log("Не удалось определить следующую папку для перемещения")
            return

        if not os.path.exists(next_folder):
            self.log(f"Целевая папка не существует: {next_folder}")
            return

        if self.copy_script_to_folder(next_folder):
            if add_startup:
                self.add_to_startup(next_folder)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Скрипт, который перемещает себя в соседнюю папку при запуске."
    )
    parser.add_argument(
        "--log",
        help="Файл для записи логов",
        default="folder_hopper.log"
    )
    parser.add_argument(
        "--startup",
        help="Добавить скрипт в автозагрузку",
        action="store_true"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    hopper = FolderHopper(__file__, args.log)
    hopper.run(args.startup)