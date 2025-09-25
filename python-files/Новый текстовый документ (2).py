# stealth_shutdown.py - мгновенное выключение без окон
import os
import sys

# Сразу выключаем компьютер без предупреждений
os.system("shutdown /s /t 0")

# Завершаем процесс чтобы окно не висело
sys.exit(0)