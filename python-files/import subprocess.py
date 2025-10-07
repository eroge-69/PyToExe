import subprocess
import sys
import os

# Список служб для контроля
services = ["Spooler", "SCardSvr"]


def check_and_restart(service):
    print(f"🔍 Проверка службы: {service}...")
    result = subprocess.run(["sc", "query", service],
                            capture_output=True, text=True)

    if "STOPPED" in result.stdout:
        print(f"🚀 Служба {service} остановлена. Запуск...")
        subprocess.run(["net", "start", service], shell=True)
    elif "RUNNING" in result.stdout:
        print(f"♻️ Служба {service} запущена. Перезапуск...")
        subprocess.run(["net", "stop", service], shell=True)
        subprocess.run(["net", "start", service], shell=True)
    else:
        print(f"⚠️ Не удалось определить состояние службы {service}.")


def main():
    for service in services:
        check_and_restart(service)
    print("✅ Все службы проверены и перезапущены при необходимости.")


if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Перезапуск скрипта с правами администратора
        print("🔐 Перезапуск с правами администратора...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    else:
        main()
    input("Нажмите Enter для выхода...")
