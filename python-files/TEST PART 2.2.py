# fake_salinewix_demo.py — повністю безпечна демонстрація
import tkinter as tk
import random
import threading
import time
import winsound

NUM_BOXES = 100  # кількість хаотичних вікон

def create_box():
    box = tk.Toplevel(root)
    box.overrideredirect(True)  # без заголовка
    box.geometry(f"200x100+{random.randint(0, root.winfo_screenwidth()-200)}+{random.randint(0, root.winfo_screenheight()-100)}")
    box.configure(bg=random.choice(['red','green','blue','yellow','magenta','cyan']))
    label = tk.Label(box, text="!!!", font=("Segoe UI", 20, "bold"), fg="white", bg=box['bg'])
    label.pack(expand=True, fill='both')
    # звук beep
    threading.Thread(target=lambda: winsound.Beep(random.randint(500,1000),100)).start()
    # хаотичне рухання
    def move():
        for _ in range(50):
            x = random.randint(10, root.winfo_screenwidth()-200)
            y = random.randint(10, root.winfo_screenheight()-100)
            box.geometry(f"200x100+{x}+{y}")
            time.sleep(0.05)
        box.destroy()
    threading.Thread(target=move).start()

root = tk.Tk()
root.withdraw()  # ховаємо головне вікно

# запуск хаотичних вікон
for i in range(NUM_BOXES):
    root.after(i*100, create_box)

root.mainloop()


# === ФУНКЦІЯ ПОМИЛОК ===
def show_error():
    for _ in range(400):  # кількість "помилок"
        ctypes.windll.user32.MessageBoxW(None, "System Error!", "Error", 0x10)
        time.sleep(0.05)  # швидкість появи

# === ФУНКЦІЯ ДИСКОТЕКИ ===
def disco():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="black")

    def flash_colors():
        colors = ["red", "blue", "green", "yellow", "purple", "cyan", "white", "orange", "red", "blue", "green", "yellow", "purple", "cyan", "white", "orange","red", "blue", "green", "yellow", "purple", "cyan", "white", "orange"]
        while True:
            root.configure(bg=random.choice(colors))
            root.update()
            time.sleep(0.1)

    threading.Thread(target=flash_colors, daemon=True).start()
    root.mainloop()

# === ЗАПУСК ===
def main():
    show_error()  # 400 помилок
    disco()       # потім дискотека

main()

