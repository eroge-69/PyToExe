import tkinter as tk
from tkinter import messagebox
from time import strftime
import webbrowser
import os
import matplotlib.pyplot as plt
import webview
import sys

root = tk.Tk()
root.title("Roblox OS")
root.geometry("800x600")
root.config(bg="skyblue")

# === Логін-екран ===
def check_login():
    username = entry_username.get()
    password = entry_password.get()
    if username == "admin" and password == "1234":
        login_frame.destroy()
        show_desktop()
    else:
        messagebox.showerror("Помилка", "Невірний логін або пароль")

login_frame = tk.Frame(root, bg="lightgray")
login_frame.pack(expand=True, fill='both')

tk.Label(login_frame, text="Вхід в Roblox OS", font=("Arial", 24), bg="lightgray").pack(pady=20)
tk.Label(login_frame, text="Логін:", bg="lightgray").pack()
entry_username = tk.Entry(login_frame)
entry_username.pack(pady=5)

tk.Label(login_frame, text="Пароль:", bg="lightgray").pack()
entry_password = tk.Entry(login_frame, show="*")
entry_password.pack(pady=5)

tk.Button(login_frame, text="Увійти", command=check_login).pack(pady=20)

# === Робочий стіл ===
def show_desktop():
    def open_browser():
        webbrowser.open("https://www.google.com")

    def open_browser_pro():
        webview.create_window("Roblox Browser PRO", "https://www.google.com", width=800, height=600)
        webview.start()

    def open_notepad():
        notepad = tk.Toplevel(root)
        notepad.title("Roblox Notepad")
        notepad.geometry("400x300")
        text = tk.Text(notepad)
        text.pack(expand=True, fill='both')

    def open_virus():
        virus = tk.Toplevel(root)
        virus.title("Virus.exe")
        virus.geometry("300x100")
        tk.Label(virus, text="Виявлено Roblox вірус! \U0001F480", fg="red", font=("Arial", 14)).pack(pady=10)
        tk.Button(virus, text="Ок", command=virus.destroy).pack()

    def open_lemonade_game():
        game = tk.Toplevel(root)
        game.title("\U0001F34B Лимонад Бізнес")
        game.geometry("420x400")

        money = tk.DoubleVar(value=0)
        price = tk.DoubleVar(value=1.0)
        sold = tk.IntVar(value=0)
        profit_log = []

        save_file = "lemonade_save.txt"

        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    money.set(float(lines[0].strip()))
                    sold.set(int(lines[1].strip()))

        def sell():
            if price.get() > 3.0:
                messagebox.showinfo("Конкурент!", "Клієнти пішли до конкурента! \U0001F621")
                return
            cost = 0.3
            income = price.get() - cost
            money.set(round(money.get() + income, 2))
            sold.set(sold.get() + 1)
            profit_log.append(income)
            update_labels()
            save_data()

        def update_labels():
            lbl_money.config(text=f"\U0001F4B0 Гроші: ${money.get()}")
            lbl_sold.config(text=f"\U0001F964 Продано: {sold.get()} шт.")
            lbl_price.config(text=f"\U0001F4B5 Ціна: ${price.get()}")

        def increase_price():
            price.set(round(price.get() + 0.5, 2))
            update_labels()

        def decrease_price():
            if price.get() > 0.5:
                price.set(round(price.get() - 0.5, 2))
                update_labels()

        def save_data():
            with open(save_file, "w") as f:
                f.write(f"{money.get()}\n{sold.get()}")

        def show_profit_chart():
            if not profit_log:
                messagebox.showinfo("Графік", "Немає прибутків для показу \U0001F605")
                return
            plt.plot(profit_log, marker="o")
            plt.title("\U0001F4C8 Прибуток з продажів")
            plt.xlabel("Продажі")
            plt.ylabel("Прибуток ($)")
            plt.grid(True)
            plt.show()

        lbl_money = tk.Label(game, text="", font=("Arial", 14))
        lbl_money.pack(pady=5)
        lbl_sold = tk.Label(game, text="", font=("Arial", 12))
        lbl_sold.pack()
        lbl_price = tk.Label(game, text="", font=("Arial", 12))
        lbl_price.pack()
        update_labels()

        tk.Button(game, text="\U0001F964 Продати лимонад", font=("Arial", 14), bg="yellow", command=sell).pack(pady=10)
        tk.Button(game, text="⬆️ Ціну ↑", command=increase_price).pack()
        tk.Button(game, text="⬇️ Ціну ↓", command=decrease_price).pack()
        tk.Button(game, text="\U0001F4C8 Графік прибутку", command=show_profit_chart).pack(pady=10)
        tk.Button(game, text="Вийти", command=game.destroy).pack(side="bottom", pady=10)

    def shutdown():
        answer = messagebox.askyesno("Вимкнення", "Точно вимкнути Roblox OS?")
        if answer:
            root.destroy()

    def restart():
        answer = messagebox.askyesno("Перезапуск", "Перезапустити Roblox OS?")
        if answer:
            python = sys.executable
            os.execl(python, python, *sys.argv)

    # Іконки на робочому столі
    tk.Button(root, text="\U0001F310 Браузер", command=open_browser, width=15, height=2).place(x=50, y=50)
    tk.Button(root, text="🌐 Браузер PRO", command=open_browser_pro, width=15, height=2).place(x=200, y=50)
    tk.Button(root, text="\U0001F4DD Нотатки", command=open_notepad, width=15, height=2).place(x=50, y=120)
    tk.Button(root, text="\U0001F480 Вірус", command=open_virus, width=15, height=2).place(x=50, y=190)
    tk.Button(root, text="\U0001F34B Бізнес", command=open_lemonade_game, width=15, height=2).place(x=50, y=260)

    # Годинник
    clock = tk.Label(root, text="", font=("Arial", 12), bg="skyblue", anchor="e")
    clock.place(x=700, y=10)

    def update_clock():
        clock.config(text=strftime("%H:%M:%S"))
        root.after(1000, update_clock)
    update_clock()

    # Меню Пуск
    start_menu = None

    def toggle_start_menu():
        nonlocal start_menu
        if start_menu and start_menu.winfo_exists():
            start_menu.destroy()
            start_menu = None
        else:
            start_menu = tk.Toplevel(root)
            start_menu.overrideredirect(True)
            start_menu.geometry("150x280+10+430")
            start_menu.config(bg="lightgray")

            tk.Button(start_menu, text="🌐 Браузер PRO", command=lambda: [open_browser_pro(), toggle_start_menu()], width=20).pack(pady=2)
            tk.Button(start_menu, text="📝 Нотатки", command=lambda: [open_notepad(), toggle_start_menu()], width=20).pack(pady=2)
            tk.Button(start_menu, text="💀 Вірус", command=lambda: [open_virus(), toggle_start_menu()], width=20).pack(pady=2)
            tk.Button(start_menu, text="🍋 Бізнес", command=lambda: [open_lemonade_game(), toggle_start_menu()], width=20).pack(pady=2)
            tk.Button(start_menu, text="🔄 Перезапуск", command=lambda: [restart(), toggle_start_menu()], width=20).pack(pady=2)
            tk.Button(start_menu, text="🔻 Вимкнути", fg="red", command=lambda: [shutdown(), toggle_start_menu()], width=20).pack(pady=5)

            start_menu.bind("<FocusOut>", lambda e: toggle_start_menu())
            start_menu.focus_set()

    tk.Button(root, text="start menu", bg="lightgray", command=toggle_start_menu).place(x=10, y=550, width=80, height=30)

root.mainloop()
