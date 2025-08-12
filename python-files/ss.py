import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

CHALLENGES = [
    {"name": "Глубинная слепота", "details": "Игрок должен пройти шахту, полную ловушек, без источников света."},
    {"name": "Кошмар пещер", "details": "Выжить 30 минут в полной темноте, пока на вас охотятся усиленные мобы."},
    {"name": "Адская охота", "details": "Уничтожить 10 враждебных мобов в пещерах, не получив урона."},
    {"name": "Пещерный марафон", "details": "Пробежать 500 блоков по пещерам, не поднимаясь на поверхность."},
    {"name": "Тёмный кладоискатель", "details": "Найти и добыть 5 алмазов в условиях полной темноты."},
    {"name": "Выжить под лавой", "details": "Выдержать 15 секунд в лаве, используя только зелья и еду."},
    {"name": "Ловец теней", "details": "Победить 3 эндерменов в пещерах, не используя щит."},
    {"name": "Костяная засада", "details": "Победить 10 скелетов в узком туннеле."},
    {"name": "Живой камень", "details": "Сразиться с големом в подземелье, не получив более 3 ударов."},
    {"name": "Беззвучная охота", "details": "Пробраться через логово варденов, не активировав ни одного скалк-сенсора."}
]

class ChallengeApp(tb.Window):
    def __init__(self):
        super().__init__(title="Cave Horror Project - Челленджи", themename="darkly")
        self.geometry("900x640")
        self.minsize(700, 480)

        self._last_size = (900, 640)

        # Фон
        bg_file = "background.png"
        if os.path.exists(bg_file):
            img = Image.open(bg_file).convert("RGBA")
            # Затемнение
            dark_layer = Image.new("RGBA", img.size, (0, 0, 0, 120))
            img = Image.alpha_composite(img, dark_layer)
            self._original_bg = img.copy()
            self._set_bg_image(900, 640)
            self.bind("<Configure>", self._resize_bg)
        else:
            self.configure(bg="#0b0b0b")
            print("[WARNING] background.png не найден — фон будет однотонным.")

        # Панель — используем тёмный непрозрачный цвет (tkinter не поддерживает hex alpha)
        panel_bg = "#111114"

        self.panel = tk.Frame(self, bg=panel_bg, bd=0)
        self.panel.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        # Заголовок
        title = tk.Label(self.panel, text="Челленджи Cave Horror Project", font=("Arial", 20, "bold"),
                         bg=panel_bg, fg="white")
        title.pack(pady=10)

        # Список челленджей
        self.listbox = tk.Listbox(self.panel, font=("Arial", 13),
                                  bg="#333333", fg="white",
                                  selectbackground="#555555", bd=0)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for ch in CHALLENGES:
            self.listbox.insert("end", ch["name"])

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Кнопки
        btn_frame = tk.Frame(self.panel, bg=panel_bg)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="Начать", bootstyle=SUCCESS, command=self.start_challenge).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Выход", bootstyle=DANGER, command=self.destroy).pack(side="left", padx=5)

    def _set_bg_image(self, w, h):
        img = self._original_bg.resize((w, h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        if not hasattr(self, "_bg_label"):
            self._bg_label = tk.Label(self, image=photo, bd=0)
            self._bg_label.image = photo
            self._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self._bg_label.configure(image=photo)
            self._bg_label.image = photo

    def _resize_bg(self, event):
        w, h = event.width, event.height
        if (w, h) != self._last_size and w > 1 and h > 1:
            self._last_size = (w, h)
            self._set_bg_image(w, h)

    def on_select(self, event):
        idx = self.listbox.curselection()
        if not idx:
            return
        ch = CHALLENGES[int(idx[0])]
        self.show_popup(ch["name"], ch["details"])

    def show_popup(self, title, details):
        popup = tb.Toplevel(self)
        popup.title(title)
        popup.resizable(False, False)

        w, h = 400, 250
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(popup, text=title, font=("Arial", 16, "bold"), bg="#222222", fg="white").pack(pady=10)
        text = tk.Text(popup, wrap="word", font=("Arial", 12), bg="#333333", fg="white", bd=0, height=6)
        text.insert("1.0", details)
        text.config(state="disabled")
        text.pack(padx=10, pady=10, fill="both", expand=True)

        tb.Button(popup, text="Закрыть", bootstyle=PRIMARY, command=popup.destroy).pack(pady=10)

    def start_challenge(self):
        idx = self.listbox.curselection()
        if not idx:
            messagebox.showwarning("Ошибка", "Выберите челлендж")
            return
        ch = CHALLENGES[int(idx[0])]
        messagebox.showinfo("Начало челленджа", f"Запускаем: {ch['name']}")

if __name__ == "__main__":
    app = ChallengeApp()
    app.mainloop()