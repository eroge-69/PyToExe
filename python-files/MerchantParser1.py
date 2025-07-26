import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time, threading, re

stop_flag = False

def clean_number(raw):
    phone = re.sub(r'\D', '', raw)
    if phone.startswith('8'):
        phone = phone[1:]
    elif phone.startswith('7') and len(phone) == 11:
        phone = phone[1:]
    return phone[-10:] if len(phone) >= 10 else None

def start_thread():
    global stop_flag
    stop_flag = False
    threading.Thread(target=parser).start()

def stop():
    global stop_flag
    stop_flag = True
    log_status("[СТОП] Парсинг остановлен.")

def log_status(msg):
    status_box.config(state='normal')
    status_box.insert(tk.END, msg + '\n')
    status_box.see(tk.END)
    status_box.config(state='disabled')

def choose_file():
    path = filedialog.asksaveasfilename(defaultextension=".txt")
    if path:
        output_path.set(path)

def parser():
    try:
        url = start_url.get().strip()
        base_id_match = re.search(r'/merchant/(\d+)', url)
        if not base_id_match:
            log_status("[ОШИБКА] Неверный формат ссылки")
            return
        base_id = int(base_id_match.group(1))
        count = int(number_count.get())
        delay = float(delay_time.get())
        save_to = output_path.get()

        log_status("[СТАРТ] Запущен парсинг...")

        options = Options()
        # Без стелс-режима
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)

        saved = 0
        for i in range(count):
            if stop_flag:
                break
            current_id = base_id + i
            link = f"https://halykmarket.kz/merchant/{current_id}"
            driver.get(link)
            time.sleep(2)

            try:
                number_button = driver.find_element(By.CSS_SELECTOR, ".product-review-info-shop-block-texts-number")
                number_button.click()
                time.sleep(1)
                href = number_button.get_attribute("href")
                if href and href.startswith("tel:"):
                    raw = href.replace("tel:", "")
                    formatted = clean_number(raw)
                    if formatted:
                        with open(save_to, 'a', encoding='utf-8') as f:
                            f.write(formatted + '\n')
                        saved += 1
                        log_status(f"[{saved}] Сохранено: {formatted}")
                    else:
                        log_status(f"[ОШИБКА] Формат номера неправильный: {raw}")
                else:
                    log_status(f"[ОШИБКА] Номер не найден на ID {current_id}")
            except Exception as e:
                log_status(f"[ОШИБКА] Номер не найден на ID {current_id} — {str(e)}")
            
            time.sleep(delay)

        driver.quit()
        log_status("[ГОТОВО] Парсинг завершён.")
    except Exception as e:
        log_status(f"[ОШИБКА] {str(e)}")

# GUI
root = tk.Tk()
root.title("Merchant Parser")
root.configure(bg='black')

tk.Label(root, text="Ссылка на продавца:", fg='white', bg='black').grid(row=0, column=0, sticky="w")
start_url = tk.StringVar()
tk.Entry(root, textvariable=start_url, bg='black', fg='white', insertbackground='white').grid(row=0, column=1)

tk.Label(root, text="Сколько номеров сохранить:", fg='white', bg='black').grid(row=1, column=0, sticky="w")
number_count = tk.StringVar()
tk.Entry(root, textvariable=number_count, bg='black', fg='white', insertbackground='white').grid(row=1, column=1)

tk.Label(root, text="Задержка (сек):", fg='white', bg='black').grid(row=2, column=0, sticky="w")
delay_time = tk.StringVar()
delay_time.set("2")
tk.Entry(root, textvariable=delay_time, bg='black', fg='white', insertbackground='white').grid(row=2, column=1)

tk.Label(root, text="Куда сохранить файл:", fg='white', bg='black').grid(row=3, column=0, sticky="w")
output_path = tk.StringVar()
tk.Entry(root, textvariable=output_path, bg='black', fg='white', insertbackground='white').grid(row=3, column=1)
tk.Button(root, text="Выбрать", command=choose_file).grid(row=3, column=2)

tk.Button(root, text="Старт", command=start_thread, bg='green', fg='white').grid(row=4, column=0)
tk.Button(root, text="Стоп", command=stop, bg='red', fg='white').grid(row=4, column=1)

status_box = tk.Text(root, height=12, state='disabled', bg='black', fg='lime')
status_box.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
