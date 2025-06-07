import tkinter as tk
from tkinter import ttk, messagebox
import pyfiglet
import tkinter.font as tkFont

# Получить список всех шрифтов из pyfiglet
all_fonts = pyfiglet.FigletFont.getFonts()


# ВАЖНО: Можно отфильтровать нужные или показать все
# Я беру полный список, так как пользователь просил очень много шрифтов.

class AsciiBannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ASCII Banner Generator")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")

        # Настроим шрифты для GUI (Arial Black если есть)
        try:
            self.gui_font = tkFont.Font(family="Arial Black", size=12)
        except:
            self.gui_font = tkFont.Font(family="Arial", size=12)

        self.create_widgets()

    def create_widgets(self):
        # Метка выбора шрифта
        label = tk.Label(self, text="Выберите шрифт ASCII:", font=self.gui_font, fg="white", bg="#1e1e1e")
        label.pack(pady=10)

        # Combobox для выбора шрифта
        self.font_var = tk.StringVar(value="standard")
        self.font_combo = ttk.Combobox(self, values=all_fonts, textvariable=self.font_var, width=30, font=self.gui_font)
        self.font_combo.pack()

        # Кнопка генерации
        gen_btn = tk.Button(self, text="Сгенерировать баннер", command=self.generate_banner, font=self.gui_font,
                            bg="#007acc", fg="white")
        gen_btn.pack(pady=10)

        # Текстовое поле для ASCII баннера с меньшим шрифтом
        self.text_font = tkFont.Font(family="Courier New", size=10)
        self.text_area = tk.Text(self, height=20, width=90, font=self.text_font, bg="#121212", fg="#00ff00",
                                 insertbackground="white")
        self.text_area.pack(padx=10, pady=10)

        # Кнопка копирования результата
        copy_btn = tk.Button(self, text="Скопировать в буфер обмена", command=self.copy_to_clipboard,
                             font=self.gui_font, bg="#28a745", fg="white")
        copy_btn.pack(pady=5)

    def generate_banner(self):
        font_name = self.font_var.get()
        text = "ASCII Banner"  # Можно сделать поле ввода для текста, сейчас фикс

        # В будущем можно добавить поле для ввода текста баннера, пока просто пример
        # Создадим диалог для ввода текста:
        text = self.ask_for_text()
        if not text:
            return

        try:
            banner = pyfiglet.figlet_format(text, font=font_name)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, banner)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать баннер:\n{e}")

    def copy_to_clipboard(self):
        banner_text = self.text_area.get("1.0", tk.END).strip()
        if banner_text:
            self.clipboard_clear()
            self.clipboard_append(banner_text)
            messagebox.showinfo("Скопировано", "Текст баннера скопирован в буфер обмена")
        else:
            messagebox.showwarning("Внимание", "Нет текста для копирования")

    def ask_for_text(self):
        # Простое окно для ввода текста баннера
        win = tk.Toplevel(self)
        win.title("Введите текст баннера")
        win.geometry("400x120")
        win.configure(bg="#1e1e1e")
        win.grab_set()

        label = tk.Label(win, text="Введите текст для ASCII баннера:", font=self.gui_font, fg="white", bg="#1e1e1e")
        label.pack(pady=5)

        entry = tk.Entry(win, font=self.gui_font, width=30)
        entry.pack(pady=5)

        result = {"text": None}

        def on_ok():
            val = entry.get().strip()
            if val:
                result["text"] = val
                win.destroy()
            else:
                messagebox.showwarning("Внимание", "Текст не может быть пустым")

        ok_btn = tk.Button(win, text="OK", command=on_ok, font=self.gui_font, bg="#007acc", fg="white")
        ok_btn.pack(pady=5)

        self.wait_window(win)
        return result["text"]


if __name__ == "__main__":
    app = AsciiBannerApp()
    app.mainloop()
