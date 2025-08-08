import tkinter as tk
from tkinter import messagebox, ttk
import os
import re
import requests
import textract
from bs4 import BeautifulSoup
from docx import Document
from datetime import datetime

HISTORY_FILE = "history.txt"

def download_application_file(ts_id):
    url = f"https://connection.oe.if.ua/ts/{ts_id}/files/active"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, "Не вдалося завантажити сторінку"

    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('a', href=True)

    for link in links:
        text = link.text.strip().lower()
        if "заявка на проектування" in text and (".docx" in link['href'] or ".doc" in link['href']):
            file_url = "https://connection.oe.if.ua" + link['href']
            file_name = file_url.split("/")[-1]

            r = requests.get(file_url)
            with open(file_name, 'wb') as f:
                f.write(r.content)
            return file_name, None

    return None, "Файл не знайдено."

def extract_text_from_file(file_path):
    if file_path.endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join([p.text for p in doc.paragraphs])
    elif file_path.endswith(".doc"):
        text = textract.process(file_path).decode("utf-8")
    else:
        return None
    return text

def extract_info(text):
    info = {
        "ПІБ замовника": re.search(r"(Замовник|ПІБ)[^\n:]*[:\s]+([^\n]+)", text, re.IGNORECASE),
        "Адреса об'єкта": re.search(r"Адреса (об'єкта|підключення)[^\n:]*[:\s]+([^\n]+)", text, re.IGNORECASE),
        "Очікуване навантаження": re.search(r"(Навантаження|Потужність)[^\n:]*[:\s]+([^\n]+)", text, re.IGNORECASE),
        "Тип підключення": re.search(r"Тип підключення[^\n:]*[:\s]+([^\n]+)", text, re.IGNORECASE),
    }

    result = {}
    for key, match in info.items():
        result[key] = match.group(2).strip() if match else "не знайдено"
    return result

def save_to_history(ts_id, result):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ID: {ts_id}\n")
        for key, value in result.items():
            f.write(f"{key}: {value}\n")
        f.write("-" * 40 + "\n")

def show_history():
    if not os.path.exists(HISTORY_FILE):
        messagebox.showinfo("Історія", "Історія ще порожня.")
        return

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    history_window = tk.Toplevel(root)
    history_window.title("Історія запитів")
    history_window.geometry("600x400")

    history_text = tk.Text(history_window, wrap=tk.WORD)
    history_text.insert(tk.END, content)
    history_text.pack(fill=tk.BOTH, expand=True)

def handle_search():
    ts_id = entry.get()
    if not ts_id.isdigit():
        messagebox.showerror("Помилка", "Введіть числовий ID техумов!")
        return

    text_area.delete(1.0, tk.END)

    file_path, error = download_application_file(ts_id)
    if error:
        messagebox.showerror("Помилка", error)
        return

    try:
        text = extract_text_from_file(file_path)
        result = extract_info(text)
        os.remove(file_path)

        for key, value in result.items():
            text_area.insert(tk.END, f"{key}: {value}\n")

        save_to_history(ts_id, result)

    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося обробити файл: {e}")

# GUI
root = tk.Tk()
root.title("Заявка на проектування – офлайн версія")
root.geometry("520x430")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Введіть ID техумов:")
label.pack(pady=(0, 10))

entry = ttk.Entry(frame, font=("Arial", 12))
entry.pack(fill=tk.X, padx=10)

btn = ttk.Button(frame, text="Завантажити і проаналізувати", command=handle_search)
btn.pack(pady=10)

history_btn = ttk.Button(frame, text="📖 Відкрити історію", command=show_history)
history_btn.pack(pady=(0, 10))

text_area = tk.Text(frame, wrap=tk.WORD, height=15, font=("Arial", 10))
text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

root.mainloop()
