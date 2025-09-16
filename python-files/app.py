import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import threading
import time
from ttkbootstrap import Style

# ⚠️ ЗАМЕНИ НА СВОИ ДАННЫЕ ⚠️
OPENROUTER_API_KEY = "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"
YOUR_SITE_URL = "http://localhost"
YOUR_SITE_NAME = "My App"
MODEL = "deepseek/deepseek-r1:free"  # ← именно эта модель, как в твоём примере

class SimpleChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💬 DeepSeek Chat")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)

        self.style = Style(theme="darkly")

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        header = ttk.Label(main_frame, text="🧠 DeepSeek R1 Chat", font=("Segoe UI", 16, "bold"))
        header.pack(pady=(0, 15))

        # Чат-область
        chat_container = ttk.Frame(main_frame)
        chat_container.pack(fill=tk.BOTH, expand=True)

        self.chat_box = tk.Text(
            chat_container,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            state=tk.DISABLED,
            bg="#1e1e1e",
            fg="#ffffff",
            padx=15,
            pady=15,
            relief="flat"
        )
        self.chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(chat_container, command=self.chat_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_box.config(yscrollcommand=scrollbar.set)

        # Поле ввода
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(15, 0))

        self.user_input = ttk.Entry(input_frame, font=("Segoe UI", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.focus()

        send_btn = ttk.Button(input_frame, text="➤ Отправить", command=self.send_message, bootstyle="success")
        send_btn.pack(side=tk.RIGHT)

        clear_btn = ttk.Button(main_frame, text="🗑️ Очистить", command=self.clear_chat, bootstyle="secondary")
        clear_btn.pack(pady=(10, 0), anchor="e")

        self.add_message("system", "🚀 Готов к работе. Задайте вопрос — отвечу через DeepSeek R1 (free).")

    def add_message(self, role, content):
        self.chat_box.config(state=tk.NORMAL)

        prefix = ""
        if role == "user":
            prefix = "👤 Вы: "
            tag = "user"
            color = "#2D4B37"
        elif role == "assistant":
            prefix = "🤖 DeepSeek: "
            tag = "ai"
            color = "#333333"
        else:
            prefix = "⚙️ Система: "
            tag = "system"
            color = "#554E3D"

        full_msg = f"{prefix}{content}\n\n"
        self.chat_box.insert(tk.END, full_msg)

        start_idx = self.chat_box.index("end-1c linestart")
        end_idx = self.chat_box.index("end-1c lineend")
        self.chat_box.tag_add(tag, start_idx, f"{end_idx}+1line")
        self.chat_box.tag_configure(tag, background=color, relief="raised")

        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.user_input.delete(0, tk.END)
        self.add_message("user", user_text)

        # Отправляем запрос в фоновом потоке
        thread = threading.Thread(target=self.get_ai_response, args=(user_text,), daemon=True)
        thread.start()

    def get_ai_response(self, user_message):
        self.add_message("system", "⏳ Отправляю запрос к DeepSeek через OpenRouter...")

        try:
            # Формируем запрос ТОЧНО как в твоём примере
            url = "https://openrouter.ai/api/v1/chat/completions"  # ← убраны пробелы в конце!

            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            }

            data = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }

            # Логируем для отладки
            print("\n" + "="*60)
            print("[📤 ОТПРАВКА ЗАПРОСА]")
            print(f"URL: {url}")
            print(f"Model: {MODEL}")
            print(f"Message: {user_message[:100]}...")
            print("="*60)

            response = requests.post(
                url=url,
                headers=headers,
                data=json.dumps(data)
            )

            print(f"[📡 ОТВЕТ] Статус: {response.status_code}")
            print(f"Тело: {response.text[:500]}...")
            print("="*60 + "\n")

            if response.status_code != 200:
                error_msg = f"❌ Ошибка {response.status_code}"
                try:
                    err_detail = response.json().get("error", {}).get("message", "—")
                    error_msg += f": {err_detail}"
                except:
                    error_msg += f": {response.text[:200]}"
                self.add_message("system", error_msg)
                return

            # Парсим ответ
            result = response.json()
            ai_reply = result["choices"][0]["message"]["content"].strip()

            # Выводим ответ
            self.root.after(0, lambda: self.add_message("assistant", ai_reply))

        except Exception as e:
            error_msg = f"💥 Ошибка: {str(e)}"
            print(error_msg)
            self.add_message("system", error_msg)

    def clear_chat(self):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.delete(1.0, tk.END)
        self.chat_box.config(state=tk.DISABLED)
        self.add_message("system", "🧹 Чат очищен. Задайте новый вопрос!")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChatApp(root)
    root.mainloop()