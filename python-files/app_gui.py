
import asyncio
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# --- Bot state keys
WAITING_FOR_FIO, WAITING_FOR_FILE = range(2)

class BotWorker:
    def __init__(self, log_fn):
        self._thread = None
        self._loop = None
        self._application = None
        self._stop_event = threading.Event()
        self._log = log_fn
        self._base_path = None
        self._token = None

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def start(self, token: str, base_path: str):
        if self.is_running():
            self._log("Бот уже запущен.")
            return

        if not token or not token.strip():
            raise ValueError("Токен бота пустой.")
        if not base_path or not os.path.isdir(base_path):
            raise ValueError("Путь сохранения недоступен.")

        self._token = token.strip()
        self._base_path = base_path
        self._stop_event.clear()

        self._thread = threading.Thread(target=self._run_thread, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.is_running():
            self._log("Бот не запущен.")
            return
        # Signal stop in the PTB loop
        if self._application and self._loop:
            fut = asyncio.run_coroutine_threadsafe(self._application.stop(), self._loop)
            try:
                fut.result(timeout=5)
            except Exception as e:
                self._log(f"Ошибка при остановке: {e}")
        self._stop_event.set()
        self._log("Ожидание завершения бота...")
        if self._thread:
            self._thread.join(timeout=10)
        self._thread = None
        self._application = None
        self._loop = None
        self._log("Бот остановлен.")

    # --- Telegram handlers use bound methods below ---
    async def start_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Здравствуйте! Пожалуйста, введите ваше ФИО:")
        context.user_data['state'] = WAITING_FOR_FIO

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get('state') == WAITING_FOR_FIO:
            context.user_data['fio'] = update.message.text.strip()
            keyboard = [
                [InlineKeyboardButton("Справка", callback_data='справка')],
                [InlineKeyboardButton("Кредит", callback_data='кредит')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"Спасибо, {context.user_data['fio']}! Выберите тип документа:",
                reply_markup=reply_markup
            )
            context.user_data['state'] = WAITING_FOR_FILE

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        context.user_data['document_type'] = query.data
        await query.message.reply_text("Пожалуйста, отправьте документ (нажмите прикрепить → документ, НЕ фото/видео)")

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get('state') == WAITING_FOR_FILE and update.message and update.message.document:
            fio = context.user_data.get('fio', 'Unknown')
            document_type = context.user_data.get('document_type', 'unknown')

            safe_fio = fio.replace(' ', '_')
            date_str = datetime.now().strftime("%d.%m.%Y")

            # Use base path from application.bot_data set at startup
            base_path = context.application.bot_data.get("base_path", os.getcwd())
            folder_path = os.path.join(base_path, safe_fio)
            os.makedirs(folder_path, exist_ok=True)

            file = await update.message.document.get_file()
            _, ext = os.path.splitext(update.message.document.file_name or "")
            new_file_name = f"{safe_fio}_{document_type}_{date_str}{ext or ''}"
            dst_path = os.path.join(folder_path, new_file_name)

            await file.download_to_drive(dst_path)
            await update.message.reply_text(f"Файл успешно сохранён: {dst_path}")
            context.user_data.clear()

    def _build_application(self):
        app = Application.builder().token(self._token).build()
        app.add_handler(CommandHandler("start", self.start_cmd))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.Document.ALL, self.handle_file))
        # Put base path into bot_data so handlers can use it
        app.bot_data["base_path"] = self._base_path
        return app

    def _run_thread(self):
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._application = self._build_application()
            self._log("Бот запускается...")
            self._loop.run_until_complete(self._application.initialize())
            self._loop.run_until_complete(self._application.start())
            self._log("Бот запущен. Откройте Telegram и отправьте команду /start вашему боту.")
            # run polling until stop() called
            self._loop.run_until_complete(self._application.updater.start_polling())
            # Wait for stop
            self._loop.run_until_complete(self._application.shutdown())
            self._loop.run_until_complete(self._application.stop())
            self._log("Бот завершил работу.")
        except Exception as e:
            self._log(f"Критическая ошибка бота: {e}")
        finally:
            try:
                if self._loop and self._loop.is_running():
                    self._loop.stop()
            except Exception:
                pass

class App:
    def __init__(self, root):
        self.root = root
        root.title("Telegram Bot Launcher")
        root.geometry("720x420")

        self.worker = BotWorker(self.log)

        # Token
        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Токен бота:").grid(row=0, column=0, sticky="w")
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(frm, textvariable=self.token_var, width=64, show="*")
        self.token_entry.grid(row=0, column=1, sticky="we", padx=(8,0))
        ttk.Button(frm, text="Показать", command=self.toggle_token).grid(row=0, column=2, padx=6)

        # Save path
        ttk.Label(frm, text="Папка для сохранения:").grid(row=1, column=0, sticky="w", pady=(10,0))
        self.path_var = tk.StringVar(value=os.path.join(os.getcwd(), "documents"))
        self.path_entry = ttk.Entry(frm, textvariable=self.path_var, width=64)
        self.path_entry.grid(row=1, column=1, sticky="we", padx=(8,0), pady=(10,0))
        ttk.Button(frm, text="Выбрать...", command=self.choose_dir).grid(row=1, column=2, padx=6, pady=(10,0))

        # Controls
        btns = ttk.Frame(frm)
        btns.grid(row=2, column=0, columnspan=3, pady=14, sticky="w")
        self.start_btn = ttk.Button(btns, text="Запустить бота", command=self.start_bot)
        self.start_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text="Остановить", command=self.stop_bot, state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        # Log
        ttk.Label(frm, text="Журнал:").grid(row=3, column=0, sticky="nw")
        self.log_txt = tk.Text(frm, height=12, wrap="word", state="disabled")
        self.log_txt.grid(row=3, column=1, columnspan=2, sticky="nsew", pady=(6,0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

        self.log("Готово. Укажите токен и папку, затем нажмите «Запустить бота».")

    def toggle_token(self):
        self.token_entry.config(show="" if self.token_entry.cget("show") == "*" else "*")

    def choose_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def start_bot(self):
        try:
            token = self.token_var.get().strip()
            path = self.path_var.get().strip()
            if not os.path.isdir(path):
                os.makedirs(path, exist_ok=True)
            self.worker.start(token, path)
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Ошибка запуска", str(e))
            self.log(f"Ошибка запуска: {e}")

    def stop_bot(self):
        try:
            self.worker.stop()
        finally:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def log(self, msg: str):
        self.log_txt.config(state="normal")
        self.log_txt.insert("end", msg + "\n")
        self.log_txt.see("end")
        self.log_txt.config(state="disabled")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
