import subprocess
import sys


def run_bot(script_name):
    """Запускает Python-скрипт в отдельном процессе"""
    process = subprocess.Popen([sys.executable, script_name])
    return process


if __name__ == "__main__":
    # Запускаем оба бота
    bot1_process = run_bot("main.py")
    bot2_process = run_bot("support.py")

    # Ожидаем завершения (если нужно)
    bot1_process.wait()
    bot2_process.wait()
