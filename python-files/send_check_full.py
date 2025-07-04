import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json

def send_check():
    send_request("/sale", {
        "items": [{
            "name": entry_name.get(),
            "price": int(entry_price.get()),
            "quantity": float(entry_qty.get()),
            "tax": 0
        }],
        "payments": [{
            "code": "cash",
            "amount": int(entry_price.get()) * float(entry_qty.get())
        }],
        "print": True
    })

def send_xreport():
    send_request("/xreport", None)

def send_zreport():
    send_request("/zreport", None)

def open_shift():
    send_request("/open_shift", None)

def close_shift():
    send_request("/close_shift", None)

def send_echo():
    send_request("/echo", None)

def send_custom():
    try:
        payload = json.loads(text_custom_json.get("1.0", tk.END))
    except Exception as e:
        messagebox.showerror("Ошибка JSON", f"Невалидный JSON:\n{e}")
        return
    send_request(entry_custom_endpoint.get(), payload)

def send_request(endpoint, payload):
    ip = entry_ip.get()
    url = f"http://{ip}:8080{endpoint}"
    try:
        if payload is None:
            response = requests.post(url, timeout=5)
        else:
            response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        messagebox.showinfo("Успех", f"✅ Ответ от кассы ({endpoint}):\n{response.text}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"❌ Не удалось выполнить запрос:\n{e}")

root = tk.Tk()
root.title("Тест кассы SmartOne")
root.geometry("600x600")

tk.Label(root, text="IP адрес кассы:").pack()
entry_ip = tk.Entry(root)
entry_ip.insert(0, "192.168.15.222")
entry_ip.pack()

tk.Label(root, text="Наименование товара:").pack()
entry_name = tk.Entry(root)
entry_name.insert(0, "Тестовый товар")
entry_name.pack()

tk.Label(root, text="Цена (в копейках):").pack()
entry_price = tk.Entry(root)
entry_price.insert(0, "10000")
entry_price.pack()

tk.Label(root, text="Количество:").pack()
entry_qty = tk.Entry(root)
entry_qty.insert(0, "1")
entry_qty.pack()

tk.Label(root, text="--- Команды ---").pack(pady=10)

frame_btns = tk.Frame(root)
frame_btns.pack()

tk.Button(frame_btns, text="🧾 Продажа (SALE)", command=send_check, width=18).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_btns, text="📄 X-отчёт", command=send_xreport, width=18).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_btns, text="📄 Z-отчёт", command=send_zreport, width=18).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_btns, text="🔓 Открыть смену", command=open_shift, width=18).grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame_btns, text="🔒 Закрыть смену", command=close_shift, width=18).grid(row=2, column=0, padx=5, pady=5)
tk.Button(frame_btns, text="🔁 /echo", command=send_echo, width=18).grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="--- Произвольный запрос ---").pack(pady=10)
entry_custom_endpoint = tk.Entry(root)
entry_custom_endpoint.insert(0, "/custom_endpoint")
entry_custom_endpoint.pack()

text_custom_json = tk.Text(root, height=6)
text_custom_json.insert(tk.END, '{\n  "key": "value"\n}')
text_custom_json.pack()

tk.Button(root, text="📤 Отправить произвольный JSON", command=send_custom).pack(pady=10)

root.mainloop()