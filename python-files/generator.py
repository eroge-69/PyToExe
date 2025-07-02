import requests
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

def generate_files():
    appid = appid_entry.get().strip()
    if not appid.isdigit():
        messagebox.showerror("Ошибка", "AppID должен содержать только цифры!")
        return
    
    status_label.config(text="Генерация файлов...", foreground="blue")
    progress_bar.start(10)
    appid_entry.config(state="disabled")
    generate_button.config(state="disabled")
    
    try:
        response = requests.post(
            "https://generator.ryuu.lol/generate",
            data={"appid": appid},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            timeout=15
        )
        
        if response.status_code != 200:
            raise Exception(f"Ошибка сервера: {response.status_code}")
        
        data = response.json()
        
        # Запрос пути сохранения
        path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if not path:
            return
            
        # Сохранение файлов
        with open(os.path.join(path, f"{appid}.lua"), "w", encoding="utf-8") as f:
            f.write(data["lua"])
        
        with open(os.path.join(path, f"appmanifest_{appid}.acf"), "w", encoding="utf-8") as f:
            f.write(data["manifest"])
        
        status_label.config(text="Файлы успешно созданы!", foreground="green")
        messagebox.showinfo("Успех", f"Файлы сохранены в:\n{path}")
        
    except Exception as e:
        status_label.config(text="Ошибка генерации", foreground="red")
        messagebox.showerror("Ошибка", f"Не удалось создать файлы:\n{str(e)}")
    finally:
        progress_bar.stop()
        appid_entry.config(state="normal")
        generate_button.config(state="normal")

def create_gui():
    global appid_entry, status_label, generate_button, progress_bar
    
    root = tk.Tk()
    root.title("SteamTools Generator")
    root.geometry("400x200")
    root.resizable(False, False)
    
    # Стилизация
    root.tk_setPalette(background="#f0f0f0")
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10, "bold"))
    style.configure("TEntry", font=("Segoe UI", 10))
    
    # Элементы интерфейса
    header = ttk.Label(
        root, 
        text="Генератор файлов для SteamTools",
        font=("Segoe UI", 12, "bold"),
        justify="center"
    )
    header.pack(pady=10)
    
    frame = ttk.Frame(root)
    frame.pack(padx=20, pady=10, fill="x")
    
    ttk.Label(frame, text="Steam AppID:").grid(row=0, column=0, sticky="w", pady=5)
    appid_entry = ttk.Entry(frame, width=20)
    appid_entry.grid(row=0, column=1, padx=5, sticky="ew")
    
    ttk.Label(frame, text="Пример: 730 (CS:GO), 570 (Dota 2)").grid(row=1, column=1, sticky="w", pady=2)
    
    progress_bar = ttk.Progressbar(
        root, 
        orient="horizontal", 
        mode="indeterminate", 
        length=300
    )
    progress_bar.pack(pady=10)
    
    generate_button = ttk.Button(
        root,
        text="Сгенерировать файлы",
        command=generate_files
    )
    generate_button.pack(pady=10)
    
    status_label = ttk.Label(
        root, 
        text="Введите AppID и нажмите кнопку",
        font=("Segoe UI", 9),
        justify="center"
    )
    status_label.pack(pady=5)
    
    footer = ttk.Label(
        root, 
        text="Для SteamTools | generator.ryuu.lol",
        font=("Segoe UI", 8),
        foreground="gray"
    )
    footer.pack(side="bottom", pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()