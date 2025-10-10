#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import ctypes
import tempfile
from pathlib import Path


def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Перезапуск с правами администратора"""
    if sys.argv[0].endswith('.exe'):
        # Скомпилированный exe
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.argv[0], " ".join(sys.argv[1:]), None, 1)
    else:
        # Python скрипт
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join([sys.argv[0]] + sys.argv[1:]), None,
                                            1)
    sys.exit()


def cleanup_directories():
    """Очистка старых каталогов"""
    print("Очистка старых каталогов...")

    directories = [
        os.path.join(os.environ['SystemDrive'], 'LOTR'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'BFME All In One Launcher'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'BFME Competetive Arena'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'BFME Workshop'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'My Battle for Middle-earth Files'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'My Battle for Middle-earth II Files'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'My Rise of the Witch-king Files'),
        os.path.join(os.environ['LOCALAPPDATA'], 'Bfme_Foundation_Team')
    ]

    for directory in directories:
        if os.path.exists(directory):
            try:
                if os.path.islink(directory):
                    os.unlink(directory)
                else:
                    shutil.rmtree(directory)
                print(f"[OK] Удалено: {directory}")
            except Exception as e:
                print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось удалить {directory}: {e}")


def check_system_file():
    """Проверка системного файла"""
    system_file = os.path.join(os.environ['WINDIR'], 'system32', 'APMon32.dll')
    return os.path.exists(system_file)


def import_reg_files():
    """Импорт REG-файлов"""
    print("Импорт регистрационных файлов...")

    current_dir = Path(__file__).parent
    reg_path = current_dir / "_FIX_" / "Regfiles" / "REG.reg"

    if reg_path.exists():
        try:
            subprocess.run(['regedit.exe', '/s', str(reg_path)], check=True, capture_output=True)
            print("[OK] REG-файл импортирован")
        except subprocess.CalledProcessError as e:
            print(f"[ОШИБКА] Не удалось импортировать REG-файл: {e}")
    else:
        print("[ПРЕДУПРЕЖДЕНИЕ] REG-файл не найден")


def create_symlinks():
    """Создание симлинков"""
    print("Создание симлинков...")

    current_dir = Path(__file__).parent

    symlinks = [
        {
            'target': Path(os.environ['SystemDrive']) / 'LOTR',
            'source': current_dir / 'LOTR'
        },
        {
            'target': Path(os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'BFME All In One Launcher',
            'source': current_dir / '_FIX_' / 'Roaming' / 'BFME All In One Launcher'
        },
        {
            'target': Path(os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'BFME Competetive Arena',
            'source': current_dir / '_FIX_' / 'Roaming' / 'BFME Competetive Arena'
        },
        {
            'target': Path(os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'BFME Workshop',
            'source': current_dir / '_FIX_' / 'Roaming' / 'BFME Workshop'
        },
        {
            'target': Path(os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'My Battle for Middle-earth Files',
            'source': current_dir / '_FIX_' / 'Roaming' / 'My Battle for Middle-earth Files'
        },
        {
            'target': Path(os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'My Battle for Middle-earth II Files',
            'source': current_dir / '_FIX_' / 'Roaming' / 'My Battle for Middle-earth II Files'
        },
        {
            'target': Path(os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'My Rise of the Witch-king Files',
            'source': current_dir / '_FIX_' / 'Roaming' / 'My Rise of the Witch-king Files'
        },
        {
            'target': Path(os.environ['LOCALAPPDATA']) / 'Bfme_Foundation_Team',
            'source': current_dir / '_FIX_' / 'Local' / 'Bfme_Foundation_Team'
        }
    ]

    for sl in symlinks:
        try:
            # Удаляем существующий симлинк/директорию
            if sl['target'].exists():
                if sl['target'].is_symlink():
                    sl['target'].unlink()
                else:
                    shutil.rmtree(sl['target'])

            # Создаем директорию для целевого пути если нужно
            sl['target'].parent.mkdir(parents=True, exist_ok=True)

            # Создаем симлинк
            if sl['source'].exists():
                sl['target'].symlink_to(sl['source'], target_is_directory=True)
                print(f"[OK] Создан симлинк: {sl['target'].name}")
            else:
                print(f"[ПРЕДУПРЕЖДЕНИЕ] Исходная директория не существует: {sl['source']}")

        except Exception as e:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось создать симлинк {sl['target'].name}: {e}")


def launch_launcher():
    """Запуск лаунчера"""
    print("Запуск лаунчера...")

    launcher_path = Path(
        os.environ['USERPROFILE']) / 'AppData' / 'Roaming' / 'BFME All In One Launcher' / 'AllInOneLauncher.exe'

    if launcher_path.exists():
        try:
            subprocess.Popen([str(launcher_path)], shell=True)
            print("[OK] Лаунчер запущен")
        except Exception as e:
            print(f"[ОШИБКА] Не удалось запустить лаунчер: {e}")
    else:
        print("[ОШИБКА] Лаунчер не найден")


def main():
    """Основная функция"""
    # Установка заголовка окна
    os.system('title BFME Setup Script')

    # Проверка прав администратора
    if not is_admin():
        print("Скрипт не запущен с правами администратора. Перезапуск...")
        run_as_admin()
        return

    try:
        # Очистка старых каталогов
        cleanup_directories()

        # Проверка системного файла
        if not check_system_file():
            print("ОШИБКА: Файл APMon32.dll не найден в system32")
            print("Убедитесь, что файл скопирован в системную директорию")
            input("Нажмите Enter для выхода...")
            sys.exit(1)

        # Импорт REG-файлов
        import_reg_files()

        # Создание симлинков
        create_symlinks()

        # Запуск лаунчера
        launch_launcher()

        print("\nЗавершено!")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)


if __name__ == "__main__":
    main()