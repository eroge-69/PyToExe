import keyboard
import os

FILE_NAME = "counter.txt"

# Створюємо файл з 0, якщо його ще немає
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write("0")

def update_counter():
    # читаємо значення
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        count = int(f.read().strip() or 0)
    
    # збільшуємо
    count += 1

    # записуємо назад
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        f.write(str(count))
    
    print(f"Лічильник смертей: {count}")

print("Програма запущена. Натискай F6, щоб додати смерть. (Ctrl+C для виходу)")

# слухаємо натискання F6
keyboard.add_hotkey("F6", update_counter)

# нескінченний цикл (чекає натискань)
keyboard.wait()
