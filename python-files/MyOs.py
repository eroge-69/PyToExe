import tkinter as tk
import webbrowser
from datetime import datetime

class BIOSStyleOS(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Моя BIOS-стиль ОС")
        self.geometry("800x600")
        self.configure(bg='black')
        self.resizable(False, False)

        self.bg_color = 'black'
        self.text_color = 'white'
        self.is_fullscreen = False

        self.create_main_interface()
        self.update_time()

    def create_main_interface(self):
        self.canvas = tk.Canvas(self, width=800, height=600, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.menu_frame = tk.Frame(self, bg=self.bg_color)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor='center')

        btn_style = {'font': ('Courier', 12), 'fg': self.text_color, 'bg': self.bg_color,
                     'activebackground': self.bg_color, 'activeforeground': self.text_color,
                     'bd': 0, 'highlightthickness': 0}

        self.btn_calc = tk.Button(self.menu_frame, text='Калькулятор', command=self.open_calculator, **btn_style)
        self.btn_paint = tk.Button(self.menu_frame, text='Пэинт', command=self.open_paint, **btn_style)
        self.btn_notepad = tk.Button(self.menu_frame, text='Блокнот', command=self.open_notepad, **btn_style)
        self.btn_browser = tk.Button(self.menu_frame, text='Браузер', command=self.open_browser_window, **btn_style)
        self.btn_settings = tk.Button(self.menu_frame, text='Настройки', command=self.open_settings, **btn_style)
        self.btn_fullscreen = tk.Button(self.menu_frame, text='Полноэкранный режим', command=self.toggle_fullscreen, **btn_style)
        self.btn_wallet = tk.Button(self.menu_frame, text='Кошелек', command=self.open_wallet, **btn_style)

        self.btn_calc.grid(row=0, column=0, padx=10, pady=10)
        self.btn_paint.grid(row=0, column=1, padx=10, pady=10)
        self.btn_notepad.grid(row=1, column=0, padx=10, pady=10)
        self.btn_browser.grid(row=1, column=1, padx=10, pady=10)
        self.btn_settings.grid(row=2, column=0, padx=10, pady=10)
        self.btn_fullscreen.grid(row=2, column=1, padx=10, pady=10)
        self.btn_wallet.grid(row=3, column=0, padx=10, pady=10)

        self.time_label = tk.Label(self, font=('Courier', 12), fg=self.text_color, bg=self.bg_color)
        self.time_label.place(relx=0.95, rely=0.02, anchor='ne')

    def update_time(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.after(1000, self.update_time)

    def open_calculator(self):
        calc_window = tk.Toplevel(self)
        calc_window.title("Калькулятор")
        calc_window.geometry("300x400")
        calc_window.configure(bg=self.bg_color)

        expression = ''

        def press(num):
            nonlocal expression
            expression += str(num)
            entry_var.set(expression)

        def clear():
            nonlocal expression
            expression = ''
            entry_var.set('')

        def equal():
            try:
                result = eval(expression)
                entry_var.set(str(result))
            except:
                entry_var.set('Ошибка')

        entry_var = tk.StringVar()
        entry = tk.Entry(calc_window, textvariable=entry_var, font=('Courier', 14), bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color, bd=2, relief='ridge')
        entry.pack(pady=10, fill='x', padx=10)

        btns = [
            ('7', lambda: press(7)), ('8', lambda: press(8)), ('9', lambda: press(9)), ('/', lambda: press('/')),
            ('4', lambda: press(4)), ('5', lambda: press(5)), ('6', lambda: press(6)), ('*', lambda: press('*')),
            ('1', lambda: press(1)), ('2', lambda: press(2)), ('3', lambda: press(3)), ('-', lambda: press('-')),
            ('0', lambda: press(0)), ('.', lambda: press('.')), ('=', lambda: equal()), ('+', lambda: press('+')),
            ('C', clear)
        ]

        btn_frame = tk.Frame(calc_window, bg=self.bg_color)
        btn_frame.pack()

        for i, (text, cmd) in enumerate(btns):
            btn = tk.Button(btn_frame, text=text, command=cmd, width=5, height=2, font=('Courier', 12),
                            bg=self.bg_color, fg=self.text_color, activebackground=self.bg_color, activeforeground=self.text_color, bd=0)
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)

    def open_paint(self):
        paint_window = tk.Toplevel(self)
        paint_window.title("Пэинт")
        paint_window.geometry("600x400")
        paint_window.configure(bg=self.bg_color)

        canvas = tk.Canvas(paint_window, bg=self.bg_color)
        canvas.pack(fill='both', expand=True)

        def paint(event):
            x, y = event.x, event.y
            r = 5
            canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.text_color, outline=self.text_color)

        canvas.bind('<B1-Motion>', paint)

    def open_notepad(self):
        notepad = tk.Toplevel(self)
        notepad.title("Блокнот")
        notepad.geometry("600x400")
        notepad.configure(bg=self.bg_color)

        text_area = tk.Text(notepad, bg=self.bg_color, fg=self.text_color, insertbackground=self.text_color, font=('Courier', 12))
        text_area.pack(fill='both', expand=True)

    def open_browser_window(self):
        browser_win = tk.Toplevel(self)
        browser_win.title("Браузер")
        browser_win.geometry("800x600")
        browser_win.configure(bg=self.bg_color)

        url_var = tk.StringVar(value='https://www.google.com')

        def go_to_url():
            url = url_var.get()
            webbrowser.open(url)

        entry = tk.Entry(browser_win, textvariable=url_var, font=('Courier', 12))
        entry.pack(pady=5, fill='x', padx=5)

        go_button = tk.Button(browser_win, text='Перейти', command=go_to_url)
        go_button.pack(pady=5)

        # Можно расширить - например, добавлять веб-страницу в WebView, но для простоты используем webbrowser
        info_label = tk.Label(browser_win, text='Введите URL и нажмите "Перейти"', bg=self.bg_color, fg=self.text_color)
        info_label.pack(pady=10)

    def open_wallet(self):
        wallet_window = tk.Toplevel(self)
        wallet_window.title("Кошелек")
        wallet_window.geometry("400x300")
        wallet_window.configure(bg=self.bg_color)

        balance_label = tk.Label(wallet_window, text='Баланс: 1000 USDT', font=('Courier', 14), bg=self.bg_color, fg=self.text_color)
        balance_label.pack(pady=20)

        def refresh_balance():
            pass  # Тут можно реализовать обновление баланса

        refresh_btn = tk.Button(wallet_window, text='Обновить баланс', command=refresh_balance, bg=self.bg_color, fg=self.text_color, activebackground=self.bg_color, activeforeground=self.text_color)
        refresh_btn.pack()

    def open_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Настройки")
        settings_window.geometry("300x200")
        settings_window.configure(bg=self.bg_color)

        def set_bg_color():
            color = bg_entry.get()
            self.bg_color = color
            self.update_ui_colors()

        def set_text_color():
            color = text_entry.get()
            self.text_color = color
            self.update_ui_colors()

        tk.Label(settings_window, text='Цвет фона:', bg=self.bg_color, fg=self.text_color, font=('Courier', 10)).pack(pady=5)
        bg_entry = tk.Entry(settings_window)
        bg_entry.insert(0, self.bg_color)
        bg_entry.pack(pady=5)

        tk.Label(settings_window, text='Цвет текста:', bg=self.bg_color, fg=self.text_color, font=('Courier', 10)).pack(pady=5)
        text_entry = tk.Entry(settings_window)
        text_entry.insert(0, self.text_color)
        text_entry.pack(pady=5)

        apply_btn = tk.Button(settings_window, text='Применить', command=lambda: [set_bg_color(), set_text_color()], bg=self.bg_color, fg=self.text_color)
        apply_btn.pack(pady=10)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def update_ui_colors(self):
        self.configure(bg=self.bg_color)
        self.canvas.configure(bg=self.bg_color)
        self.menu_frame.configure(bg=self.bg_color)
        self.time_label.configure(bg=self.bg_color, fg=self.text_color)
        for btn in [self.btn_calc, self.btn_paint, self.btn_notepad, self.btn_browser, self.btn_settings, self.btn_fullscreen, self.btn_wallet]:
            btn.configure(bg=self.bg_color, fg=self.text_color, activebackground=self.bg_color, activeforeground=self.text_color)

        self.time_label.config(bg=self.bg_color, fg=self.text_color)

if __name__ == "__main__":
    app = BIOSStyleOS()
    app.mainloop()
