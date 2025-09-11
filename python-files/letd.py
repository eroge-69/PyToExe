import os
import platform
import time
from colorama import Fore, Style, init

# تفعيل الألوان في ويندوز
init(autoreset=True)

# شعار ROKS باللون الأحمر
logo = f"""{Fore.RED}
L     EEEEE TTTTT DDDD
L     E       T   D   D
L     EEEE    T   D   D
L     E       T   D   D
LLLL  EEEEE   T   DDDD

{Style.RESET_ALL}"""

print(logo)

# إدخال IP من المستخدم
ip = input("Enter The IP: ")

# تحديد أمر ping حسب النظام
param = "-n" if platform.system().lower() == "windows" else "-c"

# ألوان للتغيير (Rainbow)
colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.WHITE]

while True:
    for color in colors:
        response = os.system(
            f"ping {param} 1 {ip} >nul 2>&1" if platform.system().lower() == "windows" else f"ping {param} 1 {ip} > /dev/null 2>&1")

        if response == 0:
            print(color + f"{ip} is online")
        else:
            print(color + f"{ip} is offline...")

        time.sleep(1)
