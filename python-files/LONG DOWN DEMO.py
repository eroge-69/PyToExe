import tkinter as tk

# Глобальные переменные для счетчиков
clicker_count = 0
shooter_count = 0

def open_window(func):
    """Закрывает текущее окно и открывает новое одно."""
    root.destroy()  # Закрыть текущее окно
    func()  # Открыть новое окно

def main_menu():
    """Первое окно с кнопками PLAY и EXIT."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="𝐋🅾Ⓝ𝔾 D𝑶ω₦", font=("Helvetica", 100))
    label.pack(expand=True)

    play_button = tk.Button(root, text="PLAY", font=("Helvetica", 30), command=lambda: open_window(name_input))
    play_button.pack(pady=20)

    exit_button = tk.Button(root, text="EXIT", font=("Helvetica", 30), command=root.quit)
    exit_button.pack(pady=20)

    root.mainloop()

def name_input():
    """Окно для ввода имени."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="Hello friend, let's be friends, what's your name?", font=("Helvetica", 30))
    label.pack(pady=20)

    name_entry = tk.Entry(root, font=("Helvetica", 30))
    name_entry.pack(pady=20)

    ok_button = tk.Button(root, text="OK", font=("Helvetica", 30), command=lambda: open_window(nice_to_meet))
    ok_button.pack(pady=20)

    root.mainloop()

def nice_to_meet():
    """Окно с приветственным сообщением."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="Nice to meet you :), let's play.", font=("Helvetica", 30))
    label.pack(pady=20)

    lets_button = tk.Button(root, text="Let's", font=("Helvetica", 30), command=lambda: open_window(choose_game))
    lets_button.pack(pady=20)

    root.mainloop()

def choose_game():
    """Окно выбора игры."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="Choose a game", font=("Helvetica", 30))
    label.pack(pady=20)

    clicker_button = tk.Button(root, text="Clicker", font=("Helvetica", 30), command=lambda: open_window(clicker_game))
    clicker_button.pack(pady=20)

    shooter_button = tk.Button(root, text="Shoter", font=("Helvetica", 30), command=lambda: open_window(shooter_game))
    shooter_button.pack(pady=20)

    root.mainloop()

def clicker_game():
    """Окно Clicker игры."""
    global root, clicker_count
    clicker_count = 0

    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="Click me!", font=("Helvetica", 30))
    label.pack(pady=20)

    click_label = tk.Label(root, text="0", font=("Helvetica", 30))
    click_label.pack(pady=20)

    click_button = tk.Button(root, text="Click me!", font=("Helvetica", 30), command=lambda: count_clicks(click_label))
    click_button.pack(pady=20)

    root.mainloop()

def count_clicks(click_label):
    """Увеличивает счетчик Clicks при нажатии на кнопку."""
    global clicker_count
    clicker_count += 1
    click_label.config(text=str(clicker_count))  # Обновить текст счетчика
    if clicker_count >= 100:  # Если нажатий 100
        open_window(end_message_clicker)

def end_message_clicker():
    """Сообщение об окончании игры Clicker."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="We played well, let's play some more?", font=("Helvetica", 30))
    label.pack(pady=20)

    lets_button = tk.Button(root, text="Let's", font=("Helvetica", 30), command=lambda: open_window(help_message))
    lets_button.pack(pady=20)

    root.mainloop()

def help_message():
    """Окно помощи."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="C̐̉̍͌ͪȧ̻̙̂n̩̓̐̏ͨ ̰ͦ̌ͭy̙͈͚̙̲̐̈͗o͈̯̱̮̫̰ͮͪ̄̇̇u̱̮̺ͭ ̮͎͙̦̱̜̫͆ͨ̌̑ͪh̺̙̹͇̳̑͐ȅ͕̪̦ͤ̍͆͋̍l̥̣̙͇p̫̠͎̘͈̟ͥͫͅ ̠̥̮̥ͬ͐ͪ͊ͪm͛̓̊́̍e̹̪̦̠̼̖̜͑ͣ͆͊̊̆̐ ̞̗̯̟̺͇̪ͭ͛ͬ̌̄̂ẅ̖͚̣͔̳͈͈̉̅͊i̝͍̦͍̞̹t͙͍͚́̏ͤ͛h̹̘̣̠̬͎͚ͧ̔̈́ͪ ͈̌̽͒t̻̋̓h̽ͯis̤̺̻̯̺?͉", font=("Helvetica", 30))
    label.pack(pady=20)

    how_button = tk.Button(root, text="How?", font=("Helvetica", 30), command=lambda: open_window(end_demo))
    how_button.pack(pady=20)

    root.mainloop()

def end_demo():
    """Окно завершения демо версии."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="End of demo version", font=("Helvetica", 30))
    label.pack(pady=20)

    exit_button = tk.Button(root, text="EXIT", font=("Helvetica", 30), command=root.quit)
    exit_button.pack(pady=20)

    root.mainloop()

def shooter_game():
    """Окно Shooter игры."""
    global root, shooter_count
    shooter_count = 0

    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="Ducks are appearing! Click them!", font=("Helvetica", 30))
    label.pack(pady=20)

    duck_button = tk.Button(root, text="DUCK", font=("Helvetica", 30), command=lambda: count_ducks())
    duck_button.pack(pady=20)

    root.mainloop()

def count_ducks():
    """Увеличивает счетчик уток при нажатии на кнопку."""
    global shooter_count
    shooter_count += 1
    if shooter_count >= 10:  # Если нажатий 10
        open_window(end_message_shooter)
    
    print(f"Duck count: {shooter_count}")  # Для отладки

def end_message_shooter():
    """Сообщение об окончании игры Shooter."""
    global root
    root = tk.Tk()
    root.title("GAME")
    root.geometry("1280x720")

    label = tk.Label(root, text="We played well, let's play some more?", font=("Helvetica", 30))
    label.pack(pady=20)

    lets_button = tk.Button(root, text="Let's", font=("Helvetica", 30), command=lambda: open_window(help_message))
    lets_button.pack(pady=20)

    root.mainloop()

# Запускаем главное меню
main_menu()
