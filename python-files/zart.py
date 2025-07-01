
import ctypes
import time

# Pierwsze okienko
ctypes.windll.user32.MessageBoxW(0, "ZOSTAŁAŚ ZHAKOWANA", "Uwaga!", 0)

# Mała przerwa, opcjonalnie
time.sleep(0.5)

# Drugie okienko
ctypes.windll.user32.MessageBoxW(0, "ŻARTOWAŁEM KOCHAM CIĘ ❤️", "Niespodzianka!", 0)
