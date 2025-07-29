import ctypes
import time
from ctypes import wintypes

# Константы для SetThreadExecutionState
ES_CONTINUOUS = 0x80000000
ES_DISPLAY_REQUIRED = 0x00000002
ES_SYSTEM_REQUIRED = 0x00000001

# Подключаемся к функции SetThreadExecutionState из kernel32
kernel32 = ctypes.windll.kernel32
kernel32.SetThreadExecutionState.argtypes = [wintypes.DWORD]
kernel32.SetThreadExecutionState.restype = wintypes.DWORD

def prevent_sleep():
    """
    Предотвращает переход в спящий режим и блокировку экрана.
    """
    print("Автоматическая блокировка экрана и переход в спящий режим отключены.")
    print("Нажмите Ctrl+C для выхода.")

    try:
        while True:
            # Сообщаем системе, что система и дисплей должны оставаться активными
            kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            time.sleep(60)  # Повторяем каждую минуту (можно уменьшить интервал)
    except KeyboardInterrupt:
        print("\nВосстановление нормального поведения системы...")
        # Снимаем флаг, чтобы система могла снова засыпать
        kernel32.SetThreadExecutionState(ES_CONTINUOUS)

if __name__ == "__main__":
    prevent_sleep()