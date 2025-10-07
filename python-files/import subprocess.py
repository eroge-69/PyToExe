import subprocess
import sys
import ctypes
import os

# Список служб, которые нужно контролировать
services = ["Spooler", "SCardSvr"]


def check_and_restart(service: str):
    """Проверяет состояние службы и перезапускает её при необходимости."""
    print(f"🔍 Проверка службы: {service}...")
    result = subprocess.run(["sc", "query", service],
                            capture_output=True, text=True)

    if "STOPPED" in result.stdout:
        print(f"🚀 Служба {service} остановлена. Запуск...")
        subprocess.run(["net", "start", service], shell=True)
    elif "RUNNING" in result.stdout:
        print(f"♻️ Служба {service} уже запущена. Перезапуск...")
        subprocess.run(["net", "stop", service], shell=True)
        subprocess.run(["net", "start", service], shell=True)
    else:
        print(
            f"⚠️ Не удалось определить состояние службы {service}. Вывод:\n{result.stdout}")


def run_with_admin():
    """Перезапускает скрипт с правами администратора, если он не запущен так."""
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("🔐 Требуются права администратора. Перезапуск...")
            params = " ".join(sys.argv)
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1)
            sys.exit()
    except Exception as e:
        print(f"❌ Ошибка проверки прав администратора: {e}")
        sys.exit(1)


def main():
    print("=== 🚀 Проверка и перезапуск служб ===\n")
    for service in services:
        check_and_restart(service)
    print("\n✅ Все службы проверены и перезапущены при необходимости.")
    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    run_with_admin()
    main()
