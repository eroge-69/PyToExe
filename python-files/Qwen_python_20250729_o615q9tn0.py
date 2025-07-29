import ctypes
import time
from ctypes import wintypes

# Константы
ES_CONTINUOUS = 0x80000000
ES_DISPLAY_REQUIRED = 0x00000002
ES_SYSTEM_REQUIRED = 0x00000001

# Подключаем API Windows
kernel32 = ctypes.windll.kernel32
kernel32.SetThreadExecutionState.argtypes = [wintypes.DWORD]
kernel32.SetThreadExecutionState.restype = wintypes.DWORD

def prevent_sleep():
    print("🔒 Защита от блокировки экрана запущена.")
    print("💡 Экран и система не будут засыпать.")
    print("🛑 Нажмите Ctrl+C для остановки.")
    try:
        while True:
            kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            time.sleep(30)  # Проверка каждые 30 секунд
    except KeyboardInterrupt:
        print("\n✅ Защита отключена. Система может снова засыпать.")
        kernel32.SetThreadExecutionState(ES_CONTINUOUS)

if __name__ == "__main__":
    prevent_sleep()