import tkinter as tk
from tkinter import filedialog, messagebox

def new_file():
    text_area.delete(1.0, tk.END)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, content)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                content = text_area.get(1.0, tk.END)
                file.write(content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

app = tk.Tk()
app.title("Мой Блокнот")
app.geometry("600x400")

text_area = tk.Text(app, wrap=tk.WORD)
text_area.pack(fill=tk.BOTH, expand=1)

menu_bar = tk.Menu(app)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Новый", command=new_file)
file_menu.add_command(label="Открыть", command=open_file)
file_menu.add_command(label="Сохранить", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=app.quit)
menu_bar.add_cascade(label="Файл", menu=file_menu)

app.config(menu=menu_bar)
app.mainloop()
